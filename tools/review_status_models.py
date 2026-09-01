"""Immutable typed records for repository-wide review status evidence."""

# pyright: reportUnnecessaryIsInstance=false
# ruff: noqa: EM101, EM102, TRY003

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import StrEnum
from pathlib import PurePosixPath, PureWindowsPath
from types import MappingProxyType
from typing import TYPE_CHECKING

from tools.review_exchange_models import (
    Actor,
    ArtifactState,
    ExchangeIdentity,
    ReviewExchangeError,
    ReviewFamily,
    ReviewRole,
    validate_local_timestamp,
)

if TYPE_CHECKING:
    from collections.abc import Mapping


SCHEMA_VERSION = 1


class ReviewStatusModelError(ValueError):
    """Raised when normalized review-status evidence is internally inconsistent."""


class ReviewStatusOutcome(StrEnum):
    """Repository-level trust outcome and process-status source."""

    TRUSTWORTHY = "trustworthy"
    UNTRUSTWORTHY = "untrustworthy"
    OPERATIONAL_FAILURE = "operational-failure"


class LeaseFreshness(StrEnum):
    """Derived lease state at one fixed evaluation timestamp."""

    CURRENT = "current"
    EXPIRED = "expired"
    NOT_HELD = "not-held"
    MISSING = "missing"


class ArtifactApplicability(StrEnum):
    """Whether one canonical artifact is expected for the observed state."""

    EXPECTED = "expected"
    NOT_APPLICABLE = "not-applicable"


class NextAction(StrEnum):
    """Stable protocol intent independent of human display text."""

    WAIT_FOR_COUNTERPART = "wait-for-counterpart"
    REQUESTOR_WORK = "requestor-work"
    REVIEWER_WORK = "reviewer-work"
    HUMAN_CONFIRMATION = "human-confirmation"
    AUTHORIZED_OWNING_WORK = "authorized-owning-work"
    RECLAIM = "reclaim"
    REPAIR = "repair"
    RESOLVE_ESCALATION = "resolve-escalation"
    NO_SAFE_ACTION = "no-safe-action"


class ArtifactKind(StrEnum):
    """The six canonical review-exchange artifact kinds."""

    REQUEST = "request"
    ANSWER = "answer"
    TRANSCRIPT = "transcript"
    COORDINATION = "coordination"
    TOMBSTONE = "tombstone"
    TRANSITION_LOCK = "transition-lock"


class RoleSpecialization(StrEnum):
    """Family-specific form of a continuing requestor or reviewer role."""

    SPECIFICATION_REQUESTOR = "specification-requestor"
    SPECIFICATION_REVIEWER = "specification-reviewer"
    CODE_REQUESTOR = "code-requestor"
    CODE_REVIEWER = "code-reviewer"


def _nonempty(value: str, label: str) -> str:
    """Return stripped nonempty text or reject it with a stable diagnostic."""
    if not isinstance(value, str) or not value.strip():
        raise ReviewStatusModelError(f"{label} must be nonempty text")
    return value


def _positive(value: int, label: str) -> int:
    """Return a positive integer while rejecting booleans."""
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ReviewStatusModelError(f"{label} must be a positive integer")
    return value


def _relative_path(value: str, label: str) -> str:
    """Validate one canonical repository-relative POSIX path."""
    _nonempty(value, label)
    path = PurePosixPath(value)
    invalid = (
        "\\" in value
        or value == "."
        or path.is_absolute()
        or PureWindowsPath(value).is_absolute()
        or ".." in path.parts
        or path.as_posix() != value
    )
    if invalid:
        raise ReviewStatusModelError(f"{label} must be a canonical repository-relative path")
    return value


def _absolute_root(value: str) -> str:
    """Validate one absolute POSIX or Windows repository-root spelling."""
    _nonempty(value, "repository root")
    if "\\" in value or not (
        PurePosixPath(value).is_absolute() or PureWindowsPath(value).is_absolute()
    ):
        raise ReviewStatusModelError("repository root must be an absolute POSIX path")
    return value


def _timestamp(value: str, label: str) -> datetime:
    """Parse one timezone-aware exchange timestamp into a comparable value."""
    try:
        validated = validate_local_timestamp(value)
    except ReviewExchangeError as error:
        raise ReviewStatusModelError(f"invalid {label}: {error}") from error
    return datetime.fromisoformat(validated)


@dataclass(frozen=True)
class ArtifactStatus:
    """Canonical artifact path with separate applicability and presence facts."""

    path: str
    applicability: ArtifactApplicability
    present: bool

    def __post_init__(self) -> None:
        """Reject noncanonical paths and non-boolean observations."""
        _relative_path(self.path, "artifact path")
        if not isinstance(self.applicability, ArtifactApplicability):
            raise ReviewStatusModelError("invalid artifact applicability")
        if not isinstance(self.present, bool):
            raise ReviewStatusModelError("artifact presence must be boolean")

    def to_dict(self) -> dict[str, object]:
        """Return the explicit stable artifact schema."""
        return {
            "path": self.path,
            "applicability": self.applicability.value,
            "present": self.present,
        }


@dataclass(frozen=True)
class LeaseStatus:
    """Raw and derived lease evidence fixed at one evaluation timestamp."""

    renewed_at: str | None
    expires_at: str | None
    evaluated_at: str
    timeout_seconds: int
    freshness: LeaseFreshness

    def __post_init__(self) -> None:
        """Reject lease categories that disagree with their fixed timestamps."""
        timeout = _positive(self.timeout_seconds, "lease timeout")
        evaluated = _timestamp(self.evaluated_at, "lease evaluation timestamp")
        if not isinstance(self.freshness, LeaseFreshness):
            raise ReviewStatusModelError("invalid lease freshness")
        if self.freshness in (LeaseFreshness.NOT_HELD, LeaseFreshness.MISSING):
            if self.renewed_at is not None or self.expires_at is not None:
                raise ReviewStatusModelError("lease-free state must not carry lease timestamps")
            return
        if self.renewed_at is None or self.expires_at is None:
            raise ReviewStatusModelError("current or expired lease requires both timestamps")
        renewed = _timestamp(self.renewed_at, "lease renewal timestamp")
        expires = _timestamp(self.expires_at, "lease expiry timestamp")
        if expires != renewed + timedelta(seconds=timeout):
            raise ReviewStatusModelError("lease expiry must equal renewal plus timeout")
        is_current = evaluated < expires
        if is_current is not (self.freshness is LeaseFreshness.CURRENT):
            raise ReviewStatusModelError("lease freshness disagrees with evaluation timestamp")

    def to_dict(self) -> dict[str, object]:
        """Return the explicit stable lease schema."""
        return {
            "renewed_at": self.renewed_at,
            "expires_at": self.expires_at,
            "evaluated_at": self.evaluated_at,
            "timeout_seconds": self.timeout_seconds,
            "freshness": self.freshness.value,
        }


@dataclass(frozen=True)
class ExchangeStatus:
    """Complete trustworthy identity plus normalized active-exchange evidence."""

    identity: ExchangeIdentity
    reviewed_document: str
    umbrella: str | None
    implementation_step: str | None
    round_number: int
    occurrence: int
    state: ArtifactState
    diagnostic: str
    continuing_role: ReviewRole
    specialization: RoleSpecialization
    owner: Actor
    lease: LeaseStatus
    artifacts: Mapping[ArtifactKind, ArtifactStatus]
    next_action: NextAction
    next_action_text: str

    def __post_init__(self) -> None:
        """Validate complete healthy evidence and freeze the six-key artifact map."""
        _validate_exchange_identity(self)
        _validate_exchange_protocol(self)
        _validate_exchange_artifacts(self)
        object.__setattr__(self, "artifacts", MappingProxyType(dict(self.artifacts)))
        if not isinstance(self.next_action, NextAction):
            raise ReviewStatusModelError("invalid next action")
        _nonempty(self.next_action_text, "next-action text")

    def to_dict(self) -> dict[str, object]:
        """Return the explicit stable healthy-entry schema."""
        return {
            "kind": "exchange",
            "identity": self.identity.to_dict(),
            "reviewed_document": self.reviewed_document,
            "umbrella": self.umbrella,
            "implementation_step": self.implementation_step,
            "round": self.round_number,
            "occurrence": self.occurrence,
            "state": self.state.value,
            "diagnostic": self.diagnostic,
            "continuing_role": self.continuing_role.value,
            "specialization": self.specialization.value,
            "owner": self.owner.value,
            "lease": self.lease.to_dict(),
            "artifacts": {
                kind.value: self.artifacts[kind].to_dict() for kind in ArtifactKind
            },
            "next_action": self.next_action.value,
            "next_action_text": self.next_action_text,
        }


def _validate_exchange_identity(exchange: ExchangeStatus) -> None:
    """Validate identity and repository-relative document paths."""
    if not isinstance(exchange.identity, ExchangeIdentity):
        raise ReviewStatusModelError("exchange identity must be validated")
    _relative_path(exchange.reviewed_document, "reviewed document")
    if exchange.umbrella is not None:
        _relative_path(exchange.umbrella, "umbrella")


def _validate_exchange_protocol(exchange: ExchangeStatus) -> None:
    """Validate protocol facts that depend on the exchange identity."""
    _positive(exchange.round_number, "round")
    _positive(exchange.occurrence, "occurrence")
    if not isinstance(exchange.state, ArtifactState) or exchange.state is ArtifactState.IDLE:
        raise ReviewStatusModelError("healthy exchange state must be active")
    _nonempty(exchange.diagnostic, "exchange diagnostic")
    if exchange.continuing_role not in (ReviewRole.REQUESTOR, ReviewRole.REVIEWER):
        raise ReviewStatusModelError("continuing role must name an agent")
    expected_specialization = RoleSpecialization(
        f"{exchange.identity.family.value}-{exchange.continuing_role.value}",
    )
    if exchange.specialization is not expected_specialization:
        raise ReviewStatusModelError("role specialization disagrees with identity and role")
    if exchange.owner not in (Actor.REQUESTOR, Actor.REVIEWER):
        raise ReviewStatusModelError("exchange owner must name an agent")
    if exchange.identity.family is ReviewFamily.CODE:
        _nonempty(exchange.implementation_step or "", "implementation step")
    elif exchange.implementation_step is not None:
        raise ReviewStatusModelError("specification exchange cannot carry a step")


def _validate_exchange_artifacts(exchange: ExchangeStatus) -> None:
    """Validate the complete typed artifact mapping."""
    expected_kinds = set(ArtifactKind)
    if set(exchange.artifacts) != expected_kinds or any(
        not isinstance(value, ArtifactStatus) for value in exchange.artifacts.values()
    ):
        raise ReviewStatusModelError("artifact map must contain all six typed kinds")


@dataclass(frozen=True)
class DamagedCandidateStatus:
    """Untrusted candidate path with only safely parsed optional identity."""

    candidate_path: str
    diagnostic: str
    candidate_identity: ExchangeIdentity | None = None

    def __post_init__(self) -> None:
        """Reject escaped paths, missing diagnostics, and guessed identity text."""
        _relative_path(self.candidate_path, "candidate path")
        _nonempty(self.diagnostic, "candidate diagnostic")
        if self.candidate_identity is not None and not isinstance(
            self.candidate_identity,
            ExchangeIdentity,
        ):
            raise ReviewStatusModelError("candidate identity must be validated or absent")

    def to_dict(self) -> dict[str, object]:
        """Return the explicitly tagged damaged-candidate schema."""
        return {
            "kind": "damaged-candidate",
            "candidate_path": self.candidate_path,
            "identity": (
                None if self.candidate_identity is None else self.candidate_identity.to_dict()
            ),
            "diagnostic": self.diagnostic,
        }


StatusEntry = ExchangeStatus | DamagedCandidateStatus


@dataclass(frozen=True)
class ReviewStatusResult:
    """One immutable repository result shared by all status renderers."""

    schema_version: int
    repository_root: str
    outcome: ReviewStatusOutcome
    exchanges: tuple[StatusEntry, ...]
    active_count: int
    has_errors: bool

    def __post_init__(self) -> None:
        """Reject aggregate counts, flags, and outcomes that contradict entries."""
        if self.schema_version != SCHEMA_VERSION:
            raise ReviewStatusModelError(f"schema version must be {SCHEMA_VERSION}")
        _absolute_root(self.repository_root)
        _validate_result_entries(self)
        _validate_result_outcome(self)

    @property
    def process_status(self) -> int:
        """Return the stable shell status derived only from the overall outcome."""
        return {
            ReviewStatusOutcome.TRUSTWORTHY: 0,
            ReviewStatusOutcome.UNTRUSTWORTHY: 3,
            ReviewStatusOutcome.OPERATIONAL_FAILURE: 2,
        }[self.outcome]

    def to_dict(self) -> dict[str, object]:
        """Return the explicit versioned repository-result schema."""
        return {
            "schema_version": self.schema_version,
            "repository_root": self.repository_root,
            "outcome": self.outcome.value,
            "active_count": self.active_count,
            "has_errors": self.has_errors,
            "exchanges": [entry.to_dict() for entry in self.exchanges],
        }


def _validate_result_entries(result: ReviewStatusResult) -> None:
    """Validate result entry types, count, and error flag."""
    if not isinstance(result.outcome, ReviewStatusOutcome):
        raise ReviewStatusModelError("invalid review-status outcome")
    if not isinstance(result.exchanges, tuple) or any(
        not isinstance(entry, (ExchangeStatus, DamagedCandidateStatus))
        for entry in result.exchanges
    ):
        raise ReviewStatusModelError("exchanges must be a tuple of typed entries")
    if result.active_count != len(result.exchanges):
        raise ReviewStatusModelError("active count must equal the entry count")
    if not isinstance(result.has_errors, bool):
        raise ReviewStatusModelError("error flag must be boolean")


def _validate_result_outcome(result: ReviewStatusResult) -> None:
    """Validate relationships between overall trust and retained entries."""
    if result.has_errors is not (
        result.outcome is not ReviewStatusOutcome.TRUSTWORTHY
    ):
        raise ReviewStatusModelError("error flag disagrees with overall outcome")
    if result.outcome is ReviewStatusOutcome.TRUSTWORTHY and any(
        isinstance(entry, DamagedCandidateStatus) for entry in result.exchanges
    ):
        raise ReviewStatusModelError("trustworthy outcome cannot contain damaged entries")
    if result.outcome is ReviewStatusOutcome.UNTRUSTWORTHY and not result.exchanges:
        raise ReviewStatusModelError("untrustworthy outcome requires retained evidence")
    if result.outcome is ReviewStatusOutcome.OPERATIONAL_FAILURE and result.exchanges:
        raise ReviewStatusModelError("operational failure cannot claim observed entries")


# eof
