"""Bounded status discovery with one invocation-scoped artifact configuration."""

# ruff: noqa: EM101, EM102, TRY003

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from tools.review_artifact_configuration import ReviewArtifactConfiguration
from tools.review_exchange_models import (
    Actor,
    ArtifactPaths,
    ArtifactState,
    ExchangeIdentity,
    ReviewConfiguration,
    ReviewExchangeError,
    ReviewRole,
)
from tools.review_exchange_models_coordination import CoordinationRecord
from tools.review_exchange_models_envelope import parse_json_markdown
from tools.review_exchange_observer import ExchangeObservation, ReviewExchangeObserver
from tools.review_exchange_paths import (
    derive_artifact_paths,
    load_review_configuration,
    parse_transient_identity,
)
from tools.review_exchange_store import ReviewExchangeStore
from tools.review_exchange_transcript_identity import current_request_occurrence
from tools.review_status_models import (
    SCHEMA_VERSION,
    ArtifactApplicability,
    ArtifactKind,
    ArtifactStatus,
    DamagedCandidateStatus,
    ExchangeStatus,
    LeaseFreshness,
    LeaseStatus,
    NextAction,
    ReviewStatusOutcome,
    ReviewStatusResult,
    RoleSpecialization,
    StatusEntry,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Mapping
    from pathlib import Path

    from tools.review_exchange_models import FamilyPolicy, ReviewContext


_ACTIVE_PREFIX = "a.review-active."

_UNTRUSTWORTHY_STATES = frozenset(
    {
        ArtifactState.TRANSCRIPT_REPAIR_PENDING,
        ArtifactState.ESCALATED,
        ArtifactState.ABANDONED_MID_ROUND,
        ArtifactState.INTERRUPTED_ANSWER_PUBLICATION,
        ArtifactState.INTERRUPTED_TRANSCRIPT_APPEND,
        ArtifactState.ABANDONED_REQUEST,
        ArtifactState.ABANDONED_ANSWER,
        ArtifactState.INCONSISTENT,
    },
)

_NO_LEASE_STATES = frozenset(
    {
        ArtifactState.CONVERGENCE_GATE,
        ArtifactState.OWNING_ACTION_PENDING,
        ArtifactState.ESCALATED,
    },
)

_ACTION_BY_STATE = {
    ArtifactState.ROUND_IN_PROGRESS: NextAction.WAIT_FOR_COUNTERPART,
    ArtifactState.REQUEST_PENDING: NextAction.REVIEWER_WORK,
    ArtifactState.ANSWER_PUBLICATION_IN_PROGRESS: NextAction.REPAIR,
    ArtifactState.TRANSCRIPT_REPAIR_PENDING: NextAction.REPAIR,
    ArtifactState.ANSWER_PENDING: NextAction.REQUESTOR_WORK,
    ArtifactState.CONVERGENCE_GATE: NextAction.HUMAN_CONFIRMATION,
    ArtifactState.OWNING_ACTION_PENDING: NextAction.AUTHORIZED_OWNING_WORK,
    ArtifactState.ESCALATED: NextAction.RESOLVE_ESCALATION,
    ArtifactState.ABANDONED_MID_ROUND: NextAction.RECLAIM,
    ArtifactState.INTERRUPTED_ANSWER_PUBLICATION: NextAction.REPAIR,
    ArtifactState.INTERRUPTED_TRANSCRIPT_APPEND: NextAction.REPAIR,
    ArtifactState.ABANDONED_REQUEST: NextAction.RECLAIM,
    ArtifactState.ABANDONED_ANSWER: NextAction.RECLAIM,
    ArtifactState.INCONSISTENT: NextAction.NO_SAFE_ACTION,
}

_ACTION_TEXT = {
    NextAction.WAIT_FOR_COUNTERPART: "Wait for the counterpart to finish the current round.",
    NextAction.REQUESTOR_WORK: "Continue as the review requestor.",
    NextAction.REVIEWER_WORK: "Continue as the reviewer.",
    NextAction.HUMAN_CONFIRMATION: "Confirm whether to converge or start another round.",
    NextAction.AUTHORIZED_OWNING_WORK: "Continue the authorized owning workflow.",
    NextAction.RECLAIM: "Reclaim the abandoned exchange before continuing.",
    NextAction.REPAIR: "Repair the interrupted review transition.",
    NextAction.RESOLVE_ESCALATION: "Resolve the escalation before continuing.",
    NextAction.NO_SAFE_ACTION: "Inspect and repair the inconsistent exchange evidence.",
}

_EXTRA_EXPECTED = {
    ArtifactState.REQUEST_PENDING: frozenset({ArtifactKind.REQUEST}),
    ArtifactState.ANSWER_PUBLICATION_IN_PROGRESS: frozenset({ArtifactKind.TOMBSTONE}),
    ArtifactState.TRANSCRIPT_REPAIR_PENDING: frozenset(
        {ArtifactKind.ANSWER, ArtifactKind.TOMBSTONE},
    ),
    ArtifactState.ANSWER_PENDING: frozenset({ArtifactKind.ANSWER}),
    ArtifactState.CONVERGENCE_GATE: frozenset({ArtifactKind.ANSWER}),
    ArtifactState.OWNING_ACTION_PENDING: frozenset({ArtifactKind.ANSWER}),
    ArtifactState.INTERRUPTED_ANSWER_PUBLICATION: frozenset(
        {ArtifactKind.TOMBSTONE},
    ),
    ArtifactState.INTERRUPTED_TRANSCRIPT_APPEND: frozenset(
        {ArtifactKind.TOMBSTONE},
    ),
    ArtifactState.ABANDONED_REQUEST: frozenset({ArtifactKind.REQUEST}),
    ArtifactState.ABANDONED_ANSWER: frozenset({ArtifactKind.ANSWER}),
}


@dataclass(frozen=True)
class _StatusDependencies:
    """Private read boundary used to prove bounded and mutation-free collection."""

    load_artifact_configuration: Callable[[Path], ReviewArtifactConfiguration]
    load_configuration: Callable[
        [Path, ReviewArtifactConfiguration], ReviewConfiguration,
    ]
    enumerate_candidates: Callable[[ReviewArtifactConfiguration], tuple[Path, ...]]
    read_bytes: Callable[[Path], bytes]
    path_exists: Callable[[Path], bool]
    derive_paths: Callable[[ReviewArtifactConfiguration, ReviewContext], ArtifactPaths]
    make_store: Callable[[ArtifactPaths], ReviewExchangeStore]
    observe: Callable[
        [
            ReviewExchangeStore,
            ReviewContext,
            FamilyPolicy,
            ReviewConfiguration,
            Callable[[], datetime],
        ],
        ExchangeObservation,
    ]
    occurrence: Callable[[ReviewExchangeStore, ReviewContext, int], int]


@dataclass(frozen=True)
class _StatusInvocation:
    """One immutable status read context sharing artifact configuration."""

    root: Path
    artifacts: ReviewArtifactConfiguration
    configuration: ReviewConfiguration
    evaluated_at: datetime


def _enumerate_candidates(
    configuration: ReviewArtifactConfiguration,
) -> tuple[Path, ...]:
    """Enumerate the reserved prefix once inside the configured artifact home."""
    home = configuration.home
    if not home.is_dir():
        return ()
    return tuple(path for path in home.iterdir() if path.name.startswith(_ACTIVE_PREFIX))


def _load_review_configuration(
    root: Path,
    artifacts: ReviewArtifactConfiguration,
) -> ReviewConfiguration:
    """Load review-mode settings against one invocation-bound artifact home."""
    return load_review_configuration(root, configuration=artifacts)


def _derive_paths(
    artifacts: ReviewArtifactConfiguration,
    context: ReviewContext,
) -> ArtifactPaths:
    """Derive candidate paths without reloading artifact-home configuration."""
    return derive_artifact_paths(
        artifacts.project_root,
        context,
        configuration=artifacts,
    )


def _observe(
    store: ReviewExchangeStore,
    context: ReviewContext,
    policy: FamilyPolicy,
    configuration: ReviewConfiguration,
    wall_clock: Callable[[], datetime],
) -> ExchangeObservation:
    """Construct the existing observer and classify one fixed-path snapshot."""
    return ReviewExchangeObserver(
        store,
        context,
        policy,
        configuration,
        wall_clock,
    ).classify()


_DEFAULT_DEPENDENCIES = _StatusDependencies(
    load_artifact_configuration=ReviewArtifactConfiguration.load,
    load_configuration=_load_review_configuration,
    enumerate_candidates=_enumerate_candidates,
    read_bytes=lambda path: path.read_bytes(),
    path_exists=lambda path: path.exists(),
    derive_paths=_derive_paths,
    make_store=ReviewExchangeStore,
    observe=_observe,
    occurrence=current_request_occurrence,
)


def collect_review_status(
    root: Path,
    wall_clock: Callable[[], datetime],
) -> ReviewStatusResult:
    """Collect one immutable repository status without locking or mutation."""
    return _collect_review_status(root, wall_clock, _DEFAULT_DEPENDENCIES)


def _collect_review_status(
    root: Path,
    wall_clock: Callable[[], datetime],
    dependencies: _StatusDependencies,
) -> ReviewStatusResult:
    """Collect through an injected read boundary used by focused tests."""
    repository_root = root.absolute()
    try:
        repository_root = root.resolve(strict=True)
        artifacts = dependencies.load_artifact_configuration(repository_root)
        configuration = dependencies.load_configuration(repository_root, artifacts)
        evaluated_at = wall_clock()
        candidates = dependencies.enumerate_candidates(artifacts)
    except (OSError, UnicodeError, ReviewExchangeError, ValueError):
        return _operational_result(repository_root)

    invocation = _StatusInvocation(
        repository_root,
        artifacts,
        configuration,
        evaluated_at,
    )
    entries = tuple(
        _collect_candidate(
            invocation,
            candidate,
            dependencies,
        )
        for candidate in candidates
    )
    retained = tuple(entry for entry in entries if entry is not None)
    return _result(repository_root, _sort_entries(retained))


def _collect_candidate(
    invocation: _StatusInvocation,
    candidate: Path,
    dependencies: _StatusDependencies,
) -> StatusEntry | None:
    """Validate and normalize one candidate without affecting its siblings."""
    root = invocation.root
    identity = None
    try:
        identity = parse_transient_identity(candidate)
        before = dependencies.read_bytes(candidate)
        payload, _ = parse_json_markdown(before.decode("utf-8"))
        record = CoordinationRecord.from_dict(payload)
        _require_equal(
            identity,
            record.context.identity,
            "filename identity differs from coordination record",
        )
        paths = dependencies.derive_paths(invocation.artifacts, record.context)
        _require_equal(
            paths.coordination.resolve(),
            candidate.resolve(),
            "coordination candidate is not its canonical path",
        )
        store = dependencies.make_store(paths)

        def fixed_clock() -> datetime:
            return invocation.evaluated_at

        observation = dependencies.observe(
            store,
            record.context,
            record.policy,
            invocation.configuration,
            fixed_clock,
        )
        after = dependencies.read_bytes(candidate)
        if before != after:
            return _damaged(root, candidate, "changed-during-read", identity)
        _require_equal(
            observation.record,
            record,
            "observer coordination differs from parsed record",
        )
        if observation.state is ArtifactState.IDLE:
            return None
        presence = _probe_artifacts(paths, dependencies.path_exists)
        occurrence = dependencies.occurrence(
            store,
            record.context,
            record.round_number,
        )
        return _project_exchange(
            root,
            record,
            paths,
            observation,
            occurrence,
            invocation.configuration.wait_timeout_seconds,
            invocation.evaluated_at,
            presence,
        )
    except (OSError, UnicodeError, ReviewExchangeError, ValueError, TypeError) as error:
        return _damaged(
            root,
            candidate,
            f"invalid coordination candidate: {error}",
            identity,
        )


def _project_exchange(  # noqa: PLR0913
    root: Path,
    record: CoordinationRecord,
    paths: ArtifactPaths,
    observation: ExchangeObservation,
    occurrence: int,
    timeout_seconds: int,
    evaluated_at: datetime,
    presence: Mapping[ArtifactKind, bool],
) -> ExchangeStatus:
    """Project validated protocol evidence into the stable status schema."""
    state = observation.state
    role = _role_for(state, record.owner, record.expected_next_actor, presence)
    applicable = _applicable_kinds(state)
    artifacts = {
        kind: ArtifactStatus(
            _relative(root, path),
            (
                ArtifactApplicability.EXPECTED
                if kind in applicable
                else ArtifactApplicability.NOT_APPLICABLE
            ),
            presence[kind],
        )
        for kind, path in _artifact_paths(paths).items()
    }
    action = _next_action_for(state)
    context = record.context
    return ExchangeStatus(
        identity=context.identity,
        reviewed_document=_relative(root, context.document_path),
        umbrella=(
            None if context.umbrella_path is None else _relative(root, context.umbrella_path)
        ),
        implementation_step=context.implementation_step,
        round_number=record.round_number,
        occurrence=occurrence,
        state=state,
        diagnostic=observation.diagnostic,
        continuing_role=role,
        specialization=RoleSpecialization(f"{context.identity.family.value}-{role.value}"),
        owner=record.owner,
        lease=_lease_for(state, record.lease_renewed_at, timeout_seconds, evaluated_at),
        artifacts=artifacts,
        next_action=action,
        next_action_text=_ACTION_TEXT[action],
    )


def _artifact_paths(paths: ArtifactPaths) -> dict[ArtifactKind, Path]:
    """Name all six canonical paths in stable schema order."""
    return {
        ArtifactKind.REQUEST: paths.request,
        ArtifactKind.ANSWER: paths.answer,
        ArtifactKind.TRANSCRIPT: paths.transcript,
        ArtifactKind.COORDINATION: paths.coordination,
        ArtifactKind.TOMBSTONE: paths.tombstone,
        ArtifactKind.TRANSITION_LOCK: paths.transition_lock,
    }


def _probe_artifacts(
    paths: ArtifactPaths,
    exists: Callable[[Path], bool],
) -> dict[ArtifactKind, bool]:
    """Probe each fixed artifact exactly once after observation stabilizes."""
    return {kind: exists(path) for kind, path in _artifact_paths(paths).items()}


def _role_for(
    state: ArtifactState,
    _owner: Actor,
    expected: Actor,
    presence: Mapping[ArtifactKind, bool],
) -> ReviewRole:
    """Derive the agent that can continue, including artifact-shaped escalation."""
    if state in (ArtifactState.CONVERGENCE_GATE, ArtifactState.OWNING_ACTION_PENDING):
        return ReviewRole.REQUESTOR
    if state is ArtifactState.ESCALATED:
        reviewer_shape = presence[ArtifactKind.REQUEST] or presence[ArtifactKind.TOMBSTONE]
        requestor_shape = presence[ArtifactKind.ANSWER]
        if reviewer_shape is requestor_shape:
            raise ReviewExchangeError(
                "escalated artifact shape does not identify one continuing role",
            )
        return ReviewRole.REVIEWER if reviewer_shape else ReviewRole.REQUESTOR
    if expected in (Actor.REQUESTOR, Actor.REVIEWER):
        return ReviewRole(expected.value)
    raise ReviewExchangeError("active exchange has no continuing agent role")


def _lease_for(
    state: ArtifactState,
    renewed_at: str | None,
    timeout_seconds: int,
    evaluated_at: datetime,
) -> LeaseStatus:
    """Derive lease freshness from one captured evaluation time."""
    evaluated = evaluated_at.isoformat(timespec="seconds")
    if state in _NO_LEASE_STATES:
        return LeaseStatus(None, None, evaluated, timeout_seconds, LeaseFreshness.NOT_HELD)
    if renewed_at is None:
        return LeaseStatus(None, None, evaluated, timeout_seconds, LeaseFreshness.MISSING)
    renewed = datetime.fromisoformat(renewed_at)
    expires = renewed + timedelta(seconds=timeout_seconds)
    freshness = (
        LeaseFreshness.CURRENT if evaluated_at < expires else LeaseFreshness.EXPIRED
    )
    return LeaseStatus(
        renewed_at,
        expires.isoformat(timespec="seconds"),
        evaluated,
        timeout_seconds,
        freshness,
    )


def _applicable_kinds(state: ArtifactState) -> frozenset[ArtifactKind]:
    """Return state-aware expected artifacts; locks are never status evidence."""
    common = {ArtifactKind.TRANSCRIPT, ArtifactKind.COORDINATION}
    return frozenset(common | set(_EXTRA_EXPECTED.get(state, ())))


def _next_action_for(state: ArtifactState) -> NextAction:
    """Map every active state to one stable next-action intent."""
    try:
        return _ACTION_BY_STATE[state]
    except KeyError as error:
        raise ReviewExchangeError(f"state has no active next action: {state.value}") from error


def _outcome_for_state(state: ArtifactState) -> ReviewStatusOutcome:
    """Map one retained state to its repository trust contribution."""
    if state is ArtifactState.IDLE:
        raise ReviewExchangeError("idle state is not retained")
    if state in _UNTRUSTWORTHY_STATES:
        return ReviewStatusOutcome.UNTRUSTWORTHY
    return ReviewStatusOutcome.TRUSTWORTHY


def _sort_entries(entries: Iterable[StatusEntry]) -> tuple[StatusEntry, ...]:
    """Return deterministic healthy-identity then damaged-candidate ordering."""
    def key(entry: StatusEntry) -> tuple[str, ...]:
        if isinstance(entry, ExchangeStatus):
            identity = entry.identity
            return (
                "0",
                identity.family.value,
                identity.type_token,
                identity.version,
                identity.slug,
            )
        return ("1", entry.candidate_path)

    return tuple(sorted(entries, key=key))


def _damaged(
    root: Path,
    candidate: Path,
    diagnostic: str,
    identity: ExchangeIdentity | None,
) -> DamagedCandidateStatus:
    """Retain only a validated identity while normalizing candidate damage."""
    return DamagedCandidateStatus(
        _relative(root, candidate),
        diagnostic,
        identity,
    )


def _relative(root: Path, path: Path) -> str:
    """Return a canonical repository-relative POSIX path."""
    try:
        return path.resolve().relative_to(root).as_posix()
    except ValueError as error:
        raise ReviewExchangeError(f"path is outside repository root: {path}") from error


def _result(root: Path, entries: tuple[StatusEntry, ...]) -> ReviewStatusResult:
    """Build the aggregate outcome from independently retained evidence."""
    if not entries:
        outcome = ReviewStatusOutcome.TRUSTWORTHY
    elif any(
        isinstance(entry, DamagedCandidateStatus)
        or _outcome_for_state(entry.state) is ReviewStatusOutcome.UNTRUSTWORTHY
        for entry in entries
    ):
        outcome = ReviewStatusOutcome.UNTRUSTWORTHY
    else:
        outcome = ReviewStatusOutcome.TRUSTWORTHY
    return ReviewStatusResult(
        SCHEMA_VERSION,
        root.as_posix(),
        outcome,
        entries,
        len(entries),
        outcome is not ReviewStatusOutcome.TRUSTWORTHY,
    )


def _operational_result(root: Path) -> ReviewStatusResult:
    """Return a fatal collection result without claiming partial evidence."""
    return ReviewStatusResult(
        schema_version=SCHEMA_VERSION,
        repository_root=root.as_posix(),
        outcome=ReviewStatusOutcome.OPERATIONAL_FAILURE,
        exchanges=(),
        active_count=0,
        has_errors=True,
    )


def _require_equal(actual: object, expected: object, diagnostic: str) -> None:
    """Raise one stable candidate-validation diagnostic when a fact disagrees."""
    if actual != expected:
        raise ReviewExchangeError(diagnostic)


__all__ = ["collect_review_status"]


# eof
