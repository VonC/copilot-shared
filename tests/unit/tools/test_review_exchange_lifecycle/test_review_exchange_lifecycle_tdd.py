"""Publication, round-transition, and wait coverage for the exchange core.

Step 3 coordinates marker-first publication, bounded waits, automated progress,
and convergence over the Step 2 store without holding locks across counterpart
work. Recovery and escalation cases live in the focused recovery sibling.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

import pytest

from tools.review_exchange_core import ReviewExchangeCore, WaitOutcome, WaitProgress
from tools.review_exchange_models import (
    Actor,
    ArtifactState,
    CoordinationStatus,
    ExchangeIdentity,
    FamilyPolicy,
    IncompleteTransitionKind,
    ReviewConfiguration,
    ReviewContext,
    ReviewDisposition,
    ReviewExchangeError,
    ReviewFamily,
    ReviewRole,
)
from tools.review_exchange_models_envelope import Envelope, render_envelope_markdown
from tools.review_exchange_paths import derive_artifact_paths
from tools.review_exchange_store import ReviewExchangeStore

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from tools.review_exchange_models_coordination import CoordinationRecord

_START = datetime(2026, 8, 4, 14, 0, tzinfo=UTC)
_SECOND_ROUND = 2
_REQUEST_EXPOSURE_TIME = 102.0
_EXPECTED_ARCHIVE_COUNT = 2


class FakeTime:
    """Advance wall and monotonic clocks together without a real sleep."""

    def __init__(self) -> None:
        """Start both clocks at deterministic values."""
        self.wall = _START
        self.monotonic = 100.0
        self.after_sleep: Callable[[], None] | None = None

    def now(self) -> datetime:
        """Return the current injected wall clock."""
        return self.wall

    def monotonic_now(self) -> float:
        """Return the current injected monotonic clock."""
        return self.monotonic

    def sleep(self, seconds: float) -> None:
        """Advance both clocks and invoke an optional poll hook."""
        self.monotonic += seconds
        self.wall += timedelta(seconds=seconds)
        if self.after_sleep is not None:
            self.after_sleep()


def _context(root: Path) -> ReviewContext:
    """Create the exact code-review context used by lifecycle tests."""
    document = root / "docs" / "plan.v0.11.0.review-exchange-core.md"
    document.parent.mkdir(parents=True, exist_ok=True)
    document.write_text("# Plan\n", encoding="utf-8")
    umbrella = root / "docs" / "draft.v0.11.0.review-mode.md"
    umbrella.write_text("# Umbrella\n", encoding="utf-8")
    return ReviewContext(
        ExchangeIdentity(
            ReviewFamily.CODE,
            "code",
            "v0.11.0",
            "review-exchange-core",
        ),
        document,
        umbrella,
        "3",
    )


def _harness(
    root: Path,
    *,
    wait_seconds: int = 60,
) -> tuple[ReviewExchangeCore, ReviewExchangeStore, ReviewContext, FakeTime]:
    """Build one core with deterministic time and exact persistence."""
    context = _context(root)
    store = ReviewExchangeStore(derive_artifact_paths(root, context))
    clock = FakeTime()
    core = ReviewExchangeCore(
        store,
        context,
        FamilyPolicy("commit-ready", "Another round", "Commit"),
        ReviewConfiguration(enabled=True, wait_timeout_seconds=wait_seconds),
        wall_clock=clock.now,
        monotonic_clock=clock.monotonic_now,
        sleeper=clock.sleep,
    )
    return core, store, context, clock


def _timestamp(clock: FakeTime) -> str:
    """Render the injected local timestamp in protocol format."""
    return clock.now().astimezone().isoformat(timespec="seconds")


def _summary(context: ReviewContext, round_number: int, guidance: str | None = None) -> str:
    """Render the mandatory code-family request summary."""
    umbrella = context.umbrella_path
    assert umbrella is not None
    lines = [
        f"Umbrella draft: {umbrella.as_posix()}",
        f"Implementation plan: {context.document_path.as_posix()}",
        "Implementation step: 3",
        f"Review round: {round_number}",
    ]
    if guidance is not None:
        lines.extend(("", f"Human guidance: {guidance}"))
    return "\n".join(lines) + "\n"


def _request(context: ReviewContext, clock: FakeTime, round_number: int) -> str:
    """Render one valid request with its identity-bearing summary."""
    envelope = Envelope(
        context.identity,
        context.umbrella_path,
        context.document_path,
        context.implementation_step,
        ReviewRole.REQUESTOR,
        round_number,
        _timestamp(clock),
    )
    return render_envelope_markdown(envelope, _summary(context, round_number))


def _answer(
    context: ReviewContext,
    clock: FakeTime,
    round_number: int,
    disposition: ReviewDisposition = ReviewDisposition.CHANGES_REQUESTED,
) -> str:
    """Render one valid reviewer answer."""
    envelope = Envelope(
        context.identity,
        context.umbrella_path,
        context.document_path,
        context.implementation_step,
        ReviewRole.REVIEWER,
        round_number,
        _timestamp(clock),
        disposition,
    )
    return render_envelope_markdown(envelope, "Reviewer feedback.\n")


def _start_and_request(
    core: ReviewExchangeCore,
    context: ReviewContext,
    clock: FakeTime,
    round_number: int = 1,
) -> None:
    """Start an exchange and publish its current request."""
    if round_number == 1:
        core.start()
    core.publish_request(
        _request(context, clock, round_number),
        f"Requestor report for round {round_number}.",
    )


def _reach_gate(
    core: ReviewExchangeCore,
    context: ReviewContext,
    clock: FakeTime,
) -> None:
    """Drive one exchange to a retained convergence answer."""
    _start_and_request(core, context, clock)
    core.publish_answer(
        _answer(
            context,
            clock,
            1,
            ReviewDisposition.CONVERGENCE_RECOMMENDED,
        ),
        "The reviewer recommends convergence.",
    )


def test_start_initializes_transcript_and_rejects_a_second_exchange(
    tmp_path: Path,
) -> None:
    """One exact document can own only one active coordination record."""
    core, store, _, _ = _harness(tmp_path)

    record = core.start()

    assert record.status is CoordinationStatus.ACTIVE
    assert record.owner is Actor.REQUESTOR
    assert record.expected_next_actor is Actor.REVIEWER
    assert record.round_number == 1
    assert record.lease_renewed_at == "2026-08-04T16:00:00+02:00"
    assert store.paths.transcript.is_file()
    with pytest.raises(ReviewExchangeError, match="already active"):
        core.start()


def test_disabled_configuration_rejects_start_without_writing(tmp_path: Path) -> None:
    """The application service remains inert when review mode is disabled."""
    _, store, context, clock = _harness(tmp_path)
    core = ReviewExchangeCore(
        store,
        context,
        FamilyPolicy("commit-ready", "Another round", "Commit"),
        ReviewConfiguration(enabled=False, wait_timeout_seconds=60),
        wall_clock=clock.now,
        monotonic_clock=clock.monotonic_now,
        sleeper=clock.sleep,
    )

    with pytest.raises(ReviewExchangeError, match="review mode is disabled"):
        core.start()

    assert core.classify().state is ArtifactState.IDLE
    assert not store.paths.transcript.exists()


def test_publish_request_validates_summary_appends_once_and_renews_lease(
    tmp_path: Path,
) -> None:
    """Request publication is marker-first, identity-safe, and auditable."""
    core, store, context, clock = _harness(tmp_path)
    core.start()
    clock.sleep(5)

    record = core.publish_request(
        _request(context, clock, 1),
        "Requestor implementation report.",
    )

    transcript = store.paths.transcript.read_text(encoding="utf-8")
    assert store.paths.request.is_file()
    assert record.expected_next_actor is Actor.REVIEWER
    assert record.incomplete_transition is None
    assert record.lease_renewed_at == "2026-08-04T16:00:05+02:00"
    assert transcript.count("review-entry-id: request-round-1") == 1
    assert "Requestor implementation report." in transcript


def test_publish_request_rejects_summary_mismatch_before_mutation(tmp_path: Path) -> None:
    """Human-readable context must agree with the request envelope."""
    core, store, context, clock = _harness(tmp_path)
    core.start()
    invalid = _request(context, clock, 1).replace(
        f"Implementation plan: {context.document_path.as_posix()}",
        "Implementation plan: docs/plan.v0.11.0.wrong.md",
    )

    with pytest.raises(ReviewExchangeError, match="summary identity mismatch"):
        core.publish_request(invalid, "Invalid summary.")

    assert not store.paths.request.exists()
    record = store.read_coordination(required=True)
    assert record is not None
    assert record.incomplete_transition is None


def test_request_append_failure_repairs_from_marker_without_duplication(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Re-running a marked request truncates only its torn suffix and completes it."""
    core, store, context, clock = _harness(tmp_path)
    core.start()
    original_append = store._append_bytes
    failed = False

    def fail_once(path: Path, content: bytes) -> None:
        nonlocal failed
        if not failed:
            failed = True
            path.write_bytes(path.read_bytes() + content[:20])
            message = "injected torn request append"
            raise OSError(message)
        original_append(path, content)

    monkeypatch.setattr(store, "_append_bytes", fail_once)
    request = _request(context, clock, 1)
    with pytest.raises(ReviewExchangeError, match="transcript append failed"):
        core.publish_request(request, "Repair this request entry.")

    marked = store.read_coordination(required=True)
    assert marked is not None
    assert marked.incomplete_transition is IncompleteTransitionKind.PUBLISH_REQUEST
    record = core.publish_request(request, "Repair this request entry.")
    transcript = store.paths.transcript.read_text(encoding="utf-8")

    assert record.incomplete_transition is None
    assert transcript.count("review-entry-id: request-round-1") == 1


def test_publish_answer_consumes_request_and_sets_intermediate_ownership(
    tmp_path: Path,
) -> None:
    """A change request becomes visible only after request consumption."""
    core, store, context, clock = _harness(tmp_path)
    _start_and_request(core, context, clock)

    record = core.publish_answer(
        _answer(context, clock, 1),
        "Please adjust the implementation.",
    )

    assert not store.paths.request.exists()
    assert not store.paths.tombstone.exists()
    assert store.paths.answer.is_file()
    assert record.owner is Actor.REVIEWER
    assert record.expected_next_actor is Actor.REQUESTOR
    assert record.convergence_recommended is False
    assert core.classify().state is ArtifactState.ANSWER_PENDING


def test_interrupted_answer_publication_resumes_from_tombstone(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A failure after request rename can publish and append the answer on retry."""
    core, store, context, clock = _harness(tmp_path)
    _start_and_request(core, context, clock)
    original_commit = store._commit_prepared
    failed = False

    def fail_answer_once(prepared: Path, target: Path) -> None:
        nonlocal failed
        if target == store.paths.answer and not failed:
            failed = True
            message = "injected answer replacement failure"
            raise OSError(message)
        original_commit(prepared, target)

    monkeypatch.setattr(store, "_commit_prepared", fail_answer_once)
    answer = _answer(context, clock, 1)
    with pytest.raises(ReviewExchangeError, match="answer publication failed"):
        core.publish_answer(answer, "Repair this reviewer entry.")

    assert store.paths.tombstone.is_file()
    assert not store.paths.answer.exists()
    record = core.publish_answer(answer, "Repair this reviewer entry.")

    assert record.incomplete_transition is None
    assert not store.paths.tombstone.exists()
    assert store.paths.answer.is_file()
    transcript = store.paths.transcript.read_text(encoding="utf-8")
    assert transcript.count("review-entry-id: answer-round-1") == 1


def test_convergence_answer_enters_suspended_human_gate(tmp_path: Path) -> None:
    """A convergence recommendation retains its answer and suspends expiry."""
    core, store, context, clock = _harness(tmp_path)
    _reach_gate(core, context, clock)

    record = store.read_coordination(required=True)
    assert record is not None
    assert record.status is CoordinationStatus.AWAITING_HUMAN_CONFIRMATION
    assert record.expected_next_actor is Actor.HUMAN
    assert record.lease_renewed_at is None
    assert store.paths.answer.is_file()
    assert core.classify().state is ArtifactState.CONVERGENCE_GATE


def test_envelope_authoritative_convergence_repairs_active_coordination(
    tmp_path: Path,
) -> None:
    """A published convergence answer restores the gate after a state-write crash."""
    core, store, context, clock = _harness(tmp_path)
    _reach_gate(core, context, clock)
    gated = store.read_coordination(required=True)
    assert gated is not None
    store.write_coordination(
        replace(
            gated,
            status=CoordinationStatus.ACTIVE,
            expected_next_actor=Actor.REQUESTOR,
            lease_renewed_at=_timestamp(clock),
            convergence_recommended=None,
        ),
    )

    record = core.consume_answer(reviewed_work_changed=True)

    assert record.status is CoordinationStatus.AWAITING_HUMAN_CONFIRMATION
    assert record.convergence_recommended is True
    assert store.paths.answer.is_file()


@pytest.fixture
def two_unchanged_rounds_journey(tmp_path: Path) -> None:
    """Two consecutive unchanged change requests stop automated review."""
    core, store, context, clock = _harness(tmp_path)
    _start_and_request(core, context, clock)
    core.publish_answer(_answer(context, clock, 1), "Round one changes.")
    first = core.consume_answer(reviewed_work_changed=False)
    assert first.no_progress_streak == 1
    assert not store.paths.answer.exists()

    next_round = core.continue_round()
    assert next_round.round_number == _SECOND_ROUND
    core.publish_request(_request(context, clock, 2), "Round two request.")
    core.publish_answer(_answer(context, clock, 2), "Round two changes.")
    escalated = core.consume_answer(reviewed_work_changed=False)

    assert escalated.status is CoordinationStatus.ESCALATED
    assert escalated.escalation_reason is not None
    assert "no meaningful progress" in escalated.escalation_reason
    assert store.paths.answer.is_file()
    transcript = store.paths.transcript.read_text(encoding="utf-8")
    assert transcript.count("Outcome: escalation") == 1


def test_two_unchanged_rounds_escalate_without_deleting_evidence(
    two_unchanged_rounds_journey: None,
) -> None:
    """The complete two-round journey retains its asserted outcome."""
    assert two_unchanged_rounds_journey is None


@pytest.fixture
def clarification_disagreement_journey(
    tmp_path: Path,
) -> None:
    """Explicit disagreement gets one automated clarification round only."""
    core, _store, context, clock = _harness(tmp_path)
    _start_and_request(core, context, clock)
    core.publish_answer(_answer(context, clock, 1), "First disagreement.")
    first = core.consume_answer(reviewed_work_changed=True, disagreement=True)
    assert first.clarification_used is True

    core.continue_round()
    core.publish_request(_request(context, clock, 2), "Clarification request.")
    core.publish_answer(_answer(context, clock, 2), "Disagreement remains.")
    second = core.consume_answer(reviewed_work_changed=True, disagreement=True)

    assert second.status is CoordinationStatus.ESCALATED
    assert second.escalation_reason is not None
    assert "disagreement" in second.escalation_reason


def test_one_clarification_round_then_persistent_disagreement_escalates(
    clarification_disagreement_journey: None,
) -> None:
    """The bounded clarification journey retains its asserted outcome."""
    assert clarification_disagreement_journey is None


@pytest.fixture
def changed_round_journey(tmp_path: Path) -> None:
    """Substantive progress clears a previous unchanged-round streak."""
    core, _, context, clock = _harness(tmp_path)
    _start_and_request(core, context, clock)
    core.publish_answer(_answer(context, clock, 1), "First changes.")
    core.consume_answer(reviewed_work_changed=False)
    core.continue_round()
    core.publish_request(_request(context, clock, 2), "Changed request.")
    core.publish_answer(_answer(context, clock, 2), "Second changes.")

    record = core.consume_answer(reviewed_work_changed=True)

    assert record.no_progress_streak == 0
    assert record.reviewed_work_changed is True


def test_changed_round_resets_no_progress_before_continuation(
    changed_round_journey: None,
) -> None:
    """The progress-reset journey retains its asserted outcome."""
    assert changed_round_journey is None


def test_wait_uses_one_monotonic_deadline_progress_and_no_lease_write(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Exact waiting reports progress without heartbeat-style coordination writes."""
    core, store, context, clock = _harness(tmp_path)
    core.start()
    writes: list[CoordinationRecord] = []
    original_write = store.write_coordination

    def track_write(record: CoordinationRecord) -> None:
        writes.append(record)
        original_write(record)

    monkeypatch.setattr(store, "write_coordination", track_write)

    def expose_request() -> None:
        if clock.monotonic >= _REQUEST_EXPOSURE_TIME and not store.paths.request.exists():
            store.publish_atomic(store.paths.request, _request(context, clock, 1))

    clock.after_sleep = expose_request
    progress: list[WaitProgress] = []
    result = core.wait_for_exact(
        ArtifactState.REQUEST_PENDING,
        timeout_seconds=5,
        poll_interval=1,
        progress_interval=1,
        progress_callback=progress.append,
    )

    assert result.outcome is WaitOutcome.FOUND
    assert result.observation.state is ArtifactState.REQUEST_PENDING
    assert len(progress) >= 1
    assert writes == []


# eof
