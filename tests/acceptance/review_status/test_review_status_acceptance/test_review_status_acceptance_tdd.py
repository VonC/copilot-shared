"""End-to-end acceptance for review-status reporting and read-only behavior.

The tests compare the real Windows launcher with direct module execution from a
nested caller repository, then assert the durable state categories and process
statuses promised by the settled review-status design. The invalid-root case
calls the public CLI adapter in-process so it tests the same status and stream
contract without paying for an unrelated cold Python subprocess.
"""

# ruff: noqa: PLR2004

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

import pytest

from tools import review_artifact_configuration as artifact_configuration
from tools.review_status import collect_review_status
from tools.review_status_cli import main as review_status_main
from tools.review_status_models import DamagedCandidateStatus

if TYPE_CHECKING:
    from collections.abc import Mapping

    from tests.acceptance.review_status.conftest import CommandMatrix


def _exchanges_by_slug(payload: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    """Index trustworthy identity-bearing entries by their stable slug."""
    exchanges = cast("list[Mapping[str, Any]]", payload["exchanges"])
    return {
        cast("Mapping[str, str]", entry["identity"])["slug"]: entry
        for entry in exchanges
        if entry["kind"] == "exchange"
    }


def _without_evaluation_time(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    """Remove only the per-process clock instant from a structured result."""
    normalized = cast("dict[str, Any]", json.loads(json.dumps(payload)))
    entries = cast("list[dict[str, Any]]", normalized["exchanges"])
    for entry in entries:
        if entry["kind"] == "exchange":
            lease = cast("dict[str, Any]", entry["lease"])
            lease["evaluated_at"] = "<captured-wall-clock>"
    return normalized


def _assert_specification_request(request: Mapping[str, Any]) -> None:
    """Check request-pending identity, ownership, action, and current lease."""
    assert request["state"] == "request-pending"
    assert request["continuing_role"] == "reviewer"
    assert request["specialization"] == "specification-reviewer"
    assert request["owner"] == "requestor"
    assert request["umbrella"] == "docs/v0.11.0/draft.v0.11.0.review-mode.md"
    assert request["next_action"] == "reviewer-work"
    assert request["lease"]["freshness"] == "current"


def _assert_convergence_gate(convergence: Mapping[str, Any]) -> None:
    """Check the distinct requestor continuation and reviewer ownership."""
    assert convergence["state"] == "convergence-gate"
    assert convergence["continuing_role"] == "requestor"
    assert convergence["owner"] == "reviewer"
    assert convergence["next_action"] == "human-confirmation"
    assert convergence["lease"]["freshness"] == "not-held"


def _assert_authorized_owning_action(owning: Mapping[str, Any]) -> None:
    """Check durable authorization and visible missing-answer evidence."""
    assert owning["state"] == "owning-action-pending"
    assert owning["continuing_role"] == "requestor"
    assert owning["next_action"] == "authorized-owning-work"
    assert owning["artifacts"]["answer"] == {
        "path": ".reviews/a.review-answer.code.v0.11.0.authorized.md",
        "applicability": "expected",
        "present": False,
    }


def _assert_escalated_wait(escalated: Mapping[str, Any]) -> None:
    """Check overnight-style escalation with its retained request shape."""
    assert escalated["state"] == "escalated"
    assert escalated["continuing_role"] == "reviewer"
    assert escalated["next_action"] == "resolve-escalation"
    assert escalated["lease"]["freshness"] == "not-held"
    assert escalated["artifacts"]["request"]["present"] is True


def _assert_remaining_states(exchanges: Mapping[str, Mapping[str, Any]]) -> None:
    """Check standalone, expired, and inconsistent state projections."""
    standalone = exchanges["standalone"]
    expired = exchanges["expired"]
    inconsistent = exchanges["inconsistent"]
    assert standalone["umbrella"] is None
    assert standalone["implementation_step"] == "4"
    assert expired["state"] == "abandoned-request"
    assert expired["lease"]["freshness"] == "expired"
    assert expired["next_action"] == "reclaim"
    assert inconsistent["state"] == "inconsistent"
    assert inconsistent["next_action"] == "no-safe-action"


def _assert_common_exchange_fields(exchanges: Mapping[str, Mapping[str, Any]]) -> None:
    """Check the complete artifact map and shared round evidence."""
    expected_artifacts = {
        "request",
        "answer",
        "transcript",
        "coordination",
        "tombstone",
        "transition-lock",
    }
    for exchange in exchanges.values():
        assert set(exchange["artifacts"]) == expected_artifacts
        assert exchange["round"] == 1
        assert exchange["occurrence"] == 1
        assert exchange["diagnostic"]


def _assert_human_identity_lines(stdout: str) -> None:
    """Check role, specialization, and umbrella labels in human output."""
    assert "Role: reviewer" in stdout
    assert "Specialization: specification-reviewer" in stdout
    assert "Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md" in stdout
    assert "Umbrella: none" in stdout


def _assert_human_state_lines(stdout: str) -> None:
    """Check blocked-state and damaged-candidate labels in human output."""
    assert "State: owning-action-pending" in stdout
    assert "State: escalated" in stdout
    assert "Damaged candidate" in stdout


def test_no_coordination_records_are_trustworthy(
    command_matrix: CommandMatrix,
) -> None:
    """Both public entry points report an empty repository as trustworthy."""
    direct = command_matrix.empty_direct
    launcher = command_matrix.empty_launcher

    assert direct.returncode == launcher.returncode == 0
    assert direct.stderr == launcher.stderr == ""
    assert _without_evaluation_time(direct.payload) == _without_evaluation_time(
        launcher.payload,
    )
    assert direct.payload["outcome"] == "trustworthy"
    assert direct.payload["active_count"] == 0
    assert direct.payload["exchanges"] == []


def test_launcher_and_direct_entry_match_from_nested_caller(
    command_matrix: CommandMatrix,
) -> None:
    """Installed runtime location never replaces the caller repository root."""
    direct = command_matrix.direct
    launcher = command_matrix.launcher

    assert direct.returncode == launcher.returncode == 3
    assert direct.stderr == launcher.stderr == ""
    assert _without_evaluation_time(direct.payload) == _without_evaluation_time(
        launcher.payload,
    )
    assert direct.payload["repository_root"] == command_matrix.populated_root.as_posix()
    assert direct.payload["active_count"] > 1
    assert direct.payload["outcome"] == "untrustworthy"


def test_state_identity_and_action_matrix_is_complete(
    command_matrix: CommandMatrix,
) -> None:
    """Durable state, role, ownership, umbrella, and action stay distinct."""
    exchanges = _exchanges_by_slug(command_matrix.direct.payload)
    _assert_specification_request(exchanges["spec-request"])
    _assert_convergence_gate(exchanges["convergence"])
    _assert_authorized_owning_action(exchanges["authorized"])
    _assert_escalated_wait(exchanges["wait-timeout"])
    _assert_remaining_states(exchanges)
    _assert_common_exchange_fields(exchanges)


def test_damaged_candidates_do_not_hide_healthy_exchanges(
    command_matrix: CommandMatrix,
) -> None:
    """Registered legacy damage remains separate from healthy records."""
    entries = cast(
        "list[Mapping[str, Any]]",
        command_matrix.direct.payload["exchanges"],
    )
    damaged = [entry for entry in entries if entry["kind"] == "damaged-candidate"]

    assert _exchanges_by_slug(command_matrix.direct.payload)["spec-request"]
    assert len(damaged) == 1
    assert any(
        "missing context fields: umbrella_path" in entry["diagnostic"]
        for entry in damaged
    )
    assert command_matrix.direct.payload["has_errors"] is True


def test_human_output_exposes_role_umbrella_and_damage(
    command_matrix: CommandMatrix,
) -> None:
    """The human report carries the same identity and trust facts as JSON."""
    completed = command_matrix.human_launcher

    assert completed.returncode == 3
    assert completed.stderr == ""
    assert f"Repository: {command_matrix.populated_root.as_posix()}" in completed.stdout
    _assert_human_identity_lines(completed.stdout)
    _assert_human_state_lines(completed.stdout)


def test_repeated_status_calls_leave_protocol_and_git_state_unchanged(
    command_matrix: CommandMatrix,
) -> None:
    """Status changes no artifact, marker, lease, index, ref, or worktree fact."""
    assert command_matrix.before == command_matrix.after
    assert _without_evaluation_time(
        command_matrix.launcher.payload,
    ) == _without_evaluation_time(command_matrix.repeated_launcher.payload)
    assert command_matrix.before.git_status == ""


def test_changed_coordination_is_reported_without_mutating_the_candidate(
    changing_repository: tuple[Path, Path, bytes],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A changed second read becomes damage and never triggers protocol repair."""
    root, candidate, original_bytes = changing_repository
    original_read = Path.read_bytes
    reads = 0

    def changing_read(path: Path) -> bytes:
        nonlocal reads
        content = original_read(path)
        if path.resolve() != candidate.resolve():
            return content
        reads += 1
        return content if reads == 1 else content + b"\n"

    def untracked_directory(_root: Path, _relative: str) -> bool:
        return False

    original_configuration_load = (
        artifact_configuration.ReviewArtifactConfiguration.load
    )

    def load_untracked(
        _configuration_type: type[
            artifact_configuration.ReviewArtifactConfiguration
        ],
        project_root: Path,
    ) -> artifact_configuration.ReviewArtifactConfiguration:
        return original_configuration_load(
            project_root,
            tracked_directory=untracked_directory,
        )

    monkeypatch.setattr(
        artifact_configuration.ReviewArtifactConfiguration,
        "load",
        classmethod(load_untracked),
    )
    monkeypatch.setattr(Path, "read_bytes", changing_read)

    result = collect_review_status(root, lambda: datetime.now().astimezone())

    damaged = result.exchanges[0]
    assert isinstance(damaged, DamagedCandidateStatus)
    assert damaged.diagnostic == "changed-during-read"
    assert original_read(candidate) == original_bytes


def test_invalid_explicit_root_is_an_operational_failure(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """An invalid controlled root returns status two without a partial payload."""
    missing = tmp_path / "missing"
    process_status = review_status_main(
        ["--root", str(missing), "--format", "json"],
    )
    captured = capsys.readouterr()

    assert process_status == 2
    assert captured.out == ""
    assert captured.err.startswith("rvw_status: ")
    with pytest.raises(json.JSONDecodeError):
        json.loads(captured.err)
