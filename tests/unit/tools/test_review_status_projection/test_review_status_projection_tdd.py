"""Independent settled expectations for every active review state."""

# pyright: reportPrivateUsage=false
# ruff: noqa: D103, PLR2004

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path

from tools.review_exchange_models import (
    Actor,
    ArtifactState,
    CoordinationStatus,
    ExchangeIdentity,
    FamilyPolicy,
    ReviewContext,
    ReviewFamily,
    ReviewRole,
)
from tools.review_exchange_models_coordination import CoordinationRecord
from tools.review_exchange_observer import ExchangeObservation
from tools.review_exchange_paths import derive_artifact_paths
from tools.review_status import _outcome_for_state, _project_exchange
from tools.review_status_models import (
    ArtifactApplicability,
    ArtifactKind,
    LeaseFreshness,
    NextAction,
    ReviewStatusOutcome,
    RoleSpecialization,
)

_NOW = datetime(2026, 8, 30, 10, 0, tzinfo=UTC)
_RENEWED = "2026-08-30T09:59:30+00:00"
_EXPECTED_ACTION = {
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
_EXPECTED_EXTRA_ARTIFACTS = {
    ArtifactState.REQUEST_PENDING: {ArtifactKind.REQUEST},
    ArtifactState.ANSWER_PUBLICATION_IN_PROGRESS: {ArtifactKind.TOMBSTONE},
    ArtifactState.TRANSCRIPT_REPAIR_PENDING: {
        ArtifactKind.ANSWER,
        ArtifactKind.TOMBSTONE,
    },
    ArtifactState.ANSWER_PENDING: {ArtifactKind.ANSWER},
    ArtifactState.CONVERGENCE_GATE: {ArtifactKind.ANSWER},
    ArtifactState.OWNING_ACTION_PENDING: {ArtifactKind.ANSWER},
    ArtifactState.INTERRUPTED_ANSWER_PUBLICATION: {ArtifactKind.TOMBSTONE},
    ArtifactState.INTERRUPTED_TRANSCRIPT_APPEND: {ArtifactKind.TOMBSTONE},
    ArtifactState.ABANDONED_REQUEST: {ArtifactKind.REQUEST},
    ArtifactState.ABANDONED_ANSWER: {ArtifactKind.ANSWER},
}
_UNTRUSTWORTHY = {
    ArtifactState.TRANSCRIPT_REPAIR_PENDING,
    ArtifactState.ESCALATED,
    ArtifactState.ABANDONED_MID_ROUND,
    ArtifactState.INTERRUPTED_ANSWER_PUBLICATION,
    ArtifactState.INTERRUPTED_TRANSCRIPT_APPEND,
    ArtifactState.ABANDONED_REQUEST,
    ArtifactState.ABANDONED_ANSWER,
    ArtifactState.INCONSISTENT,
}


def _record(root: Path, state: ArtifactState) -> CoordinationRecord:
    document = root / "docs" / f"plan.v0.11.0.{state.value}.md"
    umbrella = root / "docs" / "draft.v0.11.0.collection.md"
    document.parent.mkdir(parents=True, exist_ok=True)
    document.write_text("# Plan\n", encoding="utf-8")
    umbrella.write_text("# Umbrella\n", encoding="utf-8")
    identity = ExchangeIdentity(ReviewFamily.CODE, "code", "v0.11.0", state.value)
    return CoordinationRecord(
        ReviewContext(identity, document, umbrella, "2"),
        FamilyPolicy("ready", "Again", "Commit"),
        CoordinationStatus.ACTIVE,
        Actor.REQUESTOR,
        Actor.REVIEWER,
        1,
        _RENEWED,
    )


@pytest.mark.parametrize(
    "state",
    [state for state in ArtifactState if state is not ArtifactState.IDLE],
)
def test_every_active_state_has_exact_projection(
    tmp_path: Path,
    state: ArtifactState,
) -> None:
    record = _record(tmp_path, state)
    presence = dict.fromkeys(ArtifactKind, False)
    presence[ArtifactKind.REQUEST] = state is ArtifactState.ESCALATED
    exchange = _project_exchange(
        tmp_path,
        record,
        derive_artifact_paths(tmp_path, record.context),
        ExchangeObservation(state, record, None, None, "observed"),
        1,
        60,
        _NOW,
        presence,
    )
    requestor_states = {
        ArtifactState.CONVERGENCE_GATE,
        ArtifactState.OWNING_ACTION_PENDING,
    }
    expected_role = (
        ReviewRole.REQUESTOR if state in requestor_states else ReviewRole.REVIEWER
    )
    expected_lease = (
        LeaseFreshness.NOT_HELD
        if state in requestor_states | {ArtifactState.ESCALATED}
        else LeaseFreshness.CURRENT
    )
    expected_artifacts = {
        ArtifactKind.TRANSCRIPT,
        ArtifactKind.COORDINATION,
        *_EXPECTED_EXTRA_ARTIFACTS.get(state, set()),
    }

    assert exchange.continuing_role is expected_role
    assert exchange.specialization is RoleSpecialization(f"code-{expected_role.value}")
    assert exchange.owner is Actor.REQUESTOR
    assert exchange.next_action is _EXPECTED_ACTION[state]
    assert exchange.lease.freshness is expected_lease
    assert {
        kind
        for kind, artifact in exchange.artifacts.items()
        if artifact.applicability is ArtifactApplicability.EXPECTED
    } == expected_artifacts
    assert _outcome_for_state(state) is (
        ReviewStatusOutcome.UNTRUSTWORTHY
        if state in _UNTRUSTWORTHY
        else ReviewStatusOutcome.TRUSTWORTHY
    )
