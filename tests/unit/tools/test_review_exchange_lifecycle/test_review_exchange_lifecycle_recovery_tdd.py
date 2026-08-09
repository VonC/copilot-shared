"""Timeout, reclaim, escalation, and recovery coverage for the exchange core.

The split keeps recovery responsibilities focused while reusing the exact
deterministic lifecycle harness from the publication-transition sibling.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tools.review_exchange_core import WaitOutcome
from tools.review_exchange_models import (
    Actor,
    ArchiveKind,
    ArtifactState,
    CoordinationStatus,
    FamilyPolicy,
    IncompleteTransitionKind,
    ReviewDisposition,
    ReviewExchangeError,
)
from tools.review_exchange_models_coordination import CoordinationRecord

from . import test_review_exchange_lifecycle_tdd as lifecycle

if TYPE_CHECKING:
    from pathlib import Path


def test_wait_timeout_escalates_once_and_preserves_state(tmp_path: Path) -> None:
    """A monotonic deadline records one timeout escalation without a heartbeat."""
    core, store, _, _ = lifecycle._harness(tmp_path)
    core.start()

    result = core.wait_for_exact(
        ArtifactState.REQUEST_PENDING,
        timeout_seconds=2,
        poll_interval=1,
        progress_interval=1,
    )
    again = core.escalate("wait timed out while request was absent")

    assert result.outcome is WaitOutcome.TIMED_OUT
    assert result.observation.state is ArtifactState.ESCALATED
    assert again.status is CoordinationStatus.ESCALATED
    transcript = store.paths.transcript.read_text(encoding="utf-8")
    assert transcript.count("Outcome: escalation") == 1


def test_wait_detects_abandonment_and_attributes_expected_actor(tmp_path: Path) -> None:
    """An expired active lease escalates with the expected actor in evidence."""
    core, store, context, _ = lifecycle._harness(tmp_path)
    expired = CoordinationRecord(
        context,
        FamilyPolicy("commit-ready", "Another round", "Commit"),
        CoordinationStatus.ACTIVE,
        Actor.REQUESTOR,
        Actor.REVIEWER,
        1,
        "2026-08-04T12:00:00+00:00",
    )
    store.initialize_transcript(context)
    store.write_coordination(expired)

    result = core.wait_for_exact(
        ArtifactState.REQUEST_PENDING,
        timeout_seconds=5,
        poll_interval=1,
    )

    assert result.outcome is WaitOutcome.ABANDONED
    assert result.observation.record is not None
    assert result.observation.record.escalation_reason is not None
    assert "reviewer" in result.observation.record.escalation_reason


def test_reclaim_renews_abandoned_request_and_answer_in_place(tmp_path: Path) -> None:
    """A returning expected actor restores pending rounds by lease renewal."""
    core, store, context, clock = lifecycle._harness(tmp_path)
    lifecycle._start_and_request(core, context, clock)
    request_content = store.paths.request.read_text(encoding="utf-8")
    transcript_before = store.paths.transcript.read_text(encoding="utf-8")
    clock.sleep(61)
    assert core.classify().state is ArtifactState.ABANDONED_REQUEST

    reclaimed = core.reclaim()

    assert reclaimed.lease_renewed_at == lifecycle._timestamp(clock)
    assert reclaimed.status is CoordinationStatus.ACTIVE
    assert reclaimed.expected_next_actor is Actor.REVIEWER
    assert core.classify().state is ArtifactState.REQUEST_PENDING
    assert store.paths.request.read_text(encoding="utf-8") == request_content
    assert store.paths.transcript.read_text(encoding="utf-8") == transcript_before

    core.publish_answer(
        lifecycle._answer(context, clock, 1),
        "Reviewer report after reclaim.",
    )
    clock.sleep(61)
    assert core.classify().state is ArtifactState.ABANDONED_ANSWER
    core.reclaim()
    assert core.classify().state is ArtifactState.ANSWER_PENDING


def test_reclaim_restores_mid_round_and_stays_idempotent_on_live_rounds(
    tmp_path: Path,
) -> None:
    """Mid-round work can resume and live rounds tolerate a repeated reclaim."""
    core, store, context, clock = lifecycle._harness(tmp_path)
    lifecycle._start_and_request(core, context, clock)
    core.publish_answer(lifecycle._answer(context, clock, 1), "Reviewer report.")
    core.consume_answer(reviewed_work_changed=True)
    clock.sleep(61)
    assert core.classify().state is ArtifactState.ABANDONED_MID_ROUND

    first = core.reclaim()
    second = core.reclaim()

    assert core.classify().state is ArtifactState.ROUND_IN_PROGRESS
    assert first.round_number == 1
    assert second.round_number == 1
    transcript = store.paths.transcript.read_text(encoding="utf-8")
    assert transcript.count("Outcome: escalation") == 0


def test_reclaim_rejects_missing_coordination_gate_and_escalated_states(
    tmp_path: Path,
) -> None:
    """Reclaim never bypasses idle, convergence-gate, or escalated stops."""
    idle_core, _, _, _ = lifecycle._harness(tmp_path / "idle")
    with pytest.raises(ReviewExchangeError, match="durable coordination"):
        idle_core.reclaim()

    gate_core, _, gate_context, gate_clock = lifecycle._harness(tmp_path / "gate")
    lifecycle._reach_gate(gate_core, gate_context, gate_clock)
    gate_clock.sleep(61)
    with pytest.raises(ReviewExchangeError, match="reclaim requires"):
        gate_core.reclaim()

    core, _, context, clock = lifecycle._harness(tmp_path / "escalated")
    lifecycle._start_and_request(core, context, clock)
    clock.sleep(61)
    core.escalate("abandonment recorded before any reclaim")
    with pytest.raises(ReviewExchangeError, match="reclaim requires"):
        core.reclaim()


def test_invalid_transition_and_confirmation_labels_fail_without_mutation(
    tmp_path: Path,
) -> None:
    """Wrong actors, states, and labels cannot advance the exchange."""
    core, store, context, clock = lifecycle._harness(tmp_path)
    core.start()
    with pytest.raises(ReviewExchangeError, match="request pending"):
        core.publish_answer(lifecycle._answer(context, clock, 1), "Too early.")
    with pytest.raises(ReviewExchangeError, match="answer pending"):
        core.consume_answer(reviewed_work_changed=True)
    with pytest.raises(ReviewExchangeError, match="completed answer assessment"):
        core.continue_round()

    core.publish_request(lifecycle._request(context, clock, 1), "Valid request.")
    core.publish_answer(
        lifecycle._answer(
            context,
            clock,
            1,
            ReviewDisposition.CONVERGENCE_RECOMMENDED,
        ),
        "Converged.",
    )
    with pytest.raises(ReviewExchangeError, match="unregistered confirmation label"):
        core.confirm("Reviewer says yes")
    assert store.paths.answer.is_file()


def test_escalation_append_failure_repairs_once(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An interrupted escalation append remains marker-owned and idempotent."""
    core, store, _, _ = lifecycle._harness(tmp_path)
    core.start()
    original_append = store._append_bytes
    failed = False

    def fail_once(path: Path, content: bytes) -> None:
        nonlocal failed
        if not failed:
            failed = True
            message = "injected escalation append failure"
            raise OSError(message)
        original_append(path, content)

    monkeypatch.setattr(store, "_append_bytes", fail_once)
    with pytest.raises(ReviewExchangeError, match="transcript append failed"):
        core.escalate("Manual review required")

    marked = store.read_coordination(required=True)
    assert marked is not None
    assert marked.incomplete_transition is IncompleteTransitionKind.ESCALATION
    record = core.escalate("Manual review required")

    assert record.status is CoordinationStatus.ESCALATED
    assert record.incomplete_transition is None
    transcript = store.paths.transcript.read_text(encoding="utf-8")
    assert transcript.count("Outcome: escalation") == 1


def test_resolution_archives_only_supported_exact_evidence(tmp_path: Path) -> None:
    """Resolution returns identity-scoped archives for each live evidence kind."""
    core, _, context, clock = lifecycle._harness(tmp_path)
    lifecycle._start_and_request(core, context, clock)
    core.escalate("Archive the stopped request")

    resolution = core.resolve_escalation("Restart cleanly.", archive=True)

    names = {path.name for path in resolution.archived_paths}
    assert len(names) == lifecycle._EXPECTED_ARCHIVE_COUNT
    assert any(f".{ArchiveKind.REQUEST.value}.md" in name for name in names)
    assert any(f".{ArchiveKind.COORDINATION.value}.md" in name for name in names)


# eof
