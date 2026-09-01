"""Tests for deterministic human and JSON review-status rendering."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pytest

from tools.review_exchange_models import (
    Actor,
    ArtifactState,
    ExchangeIdentity,
    ReviewFamily,
    ReviewRole,
)
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
)
from tools.review_status_render import render_human, render_json

_ROOT = "C:/répositories/status"


def _artifacts() -> dict[ArtifactKind, ArtifactStatus]:
    """Return all artifact shapes, including missing and not-applicable evidence."""
    return {
        kind: ArtifactStatus(
            path=f"review evidence/{kind.value}.md",
            applicability=(
                ArtifactApplicability.NOT_APPLICABLE
                if kind in (ArtifactKind.TOMBSTONE, ArtifactKind.TRANSITION_LOCK)
                else ArtifactApplicability.EXPECTED
            ),
            present=kind not in (ArtifactKind.ANSWER, ArtifactKind.TRANSITION_LOCK),
        )
        for kind in ArtifactKind
    }


def _exchange(*, umbrella: str | None = "docs/v0.11.0/draft.v0.11.0.review-mode.md") -> ExchangeStatus:
    """Return one representative healthy code-review exchange."""
    return ExchangeStatus(
        identity=ExchangeIdentity(
            ReviewFamily.CODE,
            "code",
            "v0.11.0",
            "review-status-command",
        ),
        reviewed_document="docs/v0.11.0/plan.v0.11.0.review-status-command.md",
        umbrella=umbrella,
        implementation_step="3",
        round_number=2,
        occurrence=1,
        state=ArtifactState.REQUEST_PENDING,
        diagnostic="request awaits reviewer action",
        continuing_role=ReviewRole.REVIEWER,
        specialization=RoleSpecialization.CODE_REVIEWER,
        owner=Actor.REQUESTOR,
        lease=LeaseStatus(
            renewed_at="2026-08-30T09:00:00+02:00",
            expires_at="2026-08-30T10:00:00+02:00",
            evaluated_at="2026-08-30T09:30:00+02:00",
            timeout_seconds=3600,
            freshness=LeaseFreshness.CURRENT,
        ),
        artifacts=_artifacts(),
        next_action=NextAction.WAIT_FOR_COUNTERPART,
        next_action_text="Wait for the code reviewer answer.",
    )


def _result(
    *entries: ExchangeStatus | DamagedCandidateStatus,
    outcome: ReviewStatusOutcome = ReviewStatusOutcome.TRUSTWORTHY,
) -> ReviewStatusResult:
    """Wrap entries in one internally consistent repository result."""
    return ReviewStatusResult(
        schema_version=SCHEMA_VERSION,
        repository_root=_ROOT,
        outcome=outcome,
        exchanges=entries,
        active_count=len(entries),
        has_errors=outcome is not ReviewStatusOutcome.TRUSTWORTHY,
    )


def test_human_zero_report_is_complete_and_concise() -> None:
    """An empty trustworthy repository still states its complete outcome."""
    assert render_human(_result()) == (
        "Repository: C:/répositories/status\n"
        "Outcome: trustworthy\n"
        "Active exchanges: 0\n"
        "Errors: no"
    )


def test_human_exchange_block_labels_identity_responsibility_and_evidence() -> None:
    """Healthy blocks keep role, ownership, umbrella, and protocol facts distinct."""
    rendered = render_human(_result(_exchange()))

    assert rendered == "\n".join(  # noqa: FLY002 - readable pinned line protocol
        (
            "Repository: C:/répositories/status",
            "Outcome: trustworthy",
            "Active exchanges: 1",
            "Errors: no",
            "",
            "Exchange 1:",
            "  Family: code",
            "  Type: code",
            "  Version: v0.11.0",
            "  Slug: review-status-command",
            "  Reviewed document: docs/v0.11.0/plan.v0.11.0.review-status-command.md",
            "  Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md",
            "  Implementation step: 3",
            "  Round: 2",
            "  Occurrence: 1",
            "  State: request-pending",
            "  Role: reviewer",
            "  Specialization: code-reviewer",
            "  Owner: requestor",
            "  Lease: current",
            "  Lease renewed at: 2026-08-30T09:00:00+02:00",
            "  Lease expires at: 2026-08-30T10:00:00+02:00",
            "  Lease evaluated at: 2026-08-30T09:30:00+02:00",
            "  Lease timeout seconds: 3600",
            "  Artifact request: expected, present; review evidence/request.md",
            "  Artifact answer: expected, missing; review evidence/answer.md",
            "  Artifact transcript: expected, present; review evidence/transcript.md",
            "  Artifact coordination: expected, present; review evidence/coordination.md",
            "  Artifact tombstone: not-applicable, present; review evidence/tombstone.md",
            "  Artifact transition-lock: not-applicable, absent; review evidence/transition-lock.md",
            "  Next action: wait-for-counterpart",
            "  Next action detail: Wait for the code reviewer answer.",
            "  Diagnostic: request awaits reviewer action",
        ),
    )


def test_human_standalone_and_damaged_blocks_preserve_explicit_absence_and_diagnostics() -> None:
    """Standalone and damaged entries never invent missing identity."""
    damaged = DamagedCandidateStatus(
        candidate_path="a.review-active.broken.md",
        diagnostic="invalid coordination candidate: malformed JSON",
    )
    rendered = render_human(
        _result(
            _exchange(umbrella=None),
            damaged,
            outcome=ReviewStatusOutcome.UNTRUSTWORTHY,
        ),
    )

    assert "  Umbrella: none" in rendered
    assert "Damaged candidate 2:" in rendered
    assert "  Candidate: a.review-active.broken.md" in rendered
    assert "  Identity: unknown" in rendered
    assert "  Diagnostic: invalid coordination candidate: malformed JSON" in rendered


def test_json_is_complete_compact_unicode_safe_and_schema_versioned() -> None:
    """JSON is exactly the typed model projection with deterministic compact syntax."""
    result = _result(_exchange(umbrella=None))

    rendered = render_json(result)

    assert rendered == json.dumps(
        result.to_dict(),
        ensure_ascii=False,
        separators=(",", ":"),
    )
    assert "\n" not in rendered
    payload = json.loads(rendered)
    assert payload["schema_version"] == SCHEMA_VERSION
    assert payload["repository_root"] == _ROOT
    assert payload["exchanges"][0]["kind"] == "exchange"
    assert payload["exchanges"][0]["umbrella"] is None


def test_json_preserves_tagged_mixed_entry_order() -> None:
    """Machine output retains the service's one ordered tagged union."""
    damaged = DamagedCandidateStatus(
        candidate_path="a.review-active.broken.md",
        diagnostic="damaged",
    )
    payload = json.loads(
        render_json(
            _result(
                _exchange(),
                damaged,
                outcome=ReviewStatusOutcome.UNTRUSTWORTHY,
            ),
        ),
    )

    assert [entry["kind"] for entry in payload["exchanges"]] == [
        "exchange",
        "damaged-candidate",
    ]


def test_renderers_do_not_touch_filesystem_or_subprocess(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Both output forms are pure projections after status collection."""
    def forbidden(*_args: object, **_kwargs: object) -> None:
        message = "renderer crossed an IO boundary"
        raise AssertionError(message)

    monkeypatch.setattr(Path, "read_text", forbidden)
    monkeypatch.setattr(Path, "exists", forbidden)
    monkeypatch.setattr("subprocess.run", forbidden)
    result = _result(_exchange())

    assert render_human(result).startswith("Repository:")
    assert render_json(result).startswith('{"schema_version":1')
