"""Acceptance evidence for both read-only commit-plan checker entry points.

Step 4 exercises real repositories, exact state snapshots, rename inventory,
caller-owned redirection, operational failures, and request publication gates.
Slow Git setup runs in fixtures so measured assertion calls remain bounded.
"""

# ruff: noqa: S603, S607, SLF001

from __future__ import annotations

import json
import os
import subprocess
import sys
from argparse import Namespace
from dataclasses import dataclass, replace
from pathlib import Path
from typing import cast

import pytest

from tools import code_review_request as requestor
from tools import commit_plan_check
from tools.review_exchange_models import ReviewExchangeError

_NON_READY_STATUS = 3
_OPERATIONAL_STATUS = 2
_TREE_A = "a" * 40
_TREE_B = "b" * 40


@dataclass(frozen=True)
class _RepositoryState:
    """Observable repository state protected by the checker contract."""

    head: str
    index_tree: str
    staged_paths: tuple[str, ...]
    worktree_diff: bytes
    plan_bytes: bytes | None
    ignored_root: tuple[str, ...]


def _git(root: Path, *arguments: str) -> subprocess.CompletedProcess[bytes]:
    """Run one required Git setup or snapshot command."""
    return subprocess.run(
        ["git", "-C", str(root), *arguments],
        check=True,
        capture_output=True,
    )


def _commit(root: Path, message: str) -> None:
    """Create one deterministic local fixture commit."""
    subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "-c",
            "user.name=Commit Plan Acceptance",
            "-c",
            "user.email=acceptance@example.invalid",
            "commit",
            "-q",
            "-m",
            message,
        ],
        check=True,
        capture_output=True,
    )


def _initialize_repository(root: Path) -> None:
    """Create a repository with one stable HEAD and ignored root evidence."""
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    (root / ".gitignore").write_text("a.*\n", encoding="utf-8")
    (root / "baseline.txt").write_text("baseline\n", encoding="utf-8")
    _git(root, "add", "--", ".gitignore", "baseline.txt")
    _commit(root, "test: create baseline")


def _valid_plan(*paths: str) -> str:
    """Build one parser-valid group for the supplied exact membership."""
    commands = "\n".join(f"git add -- {path}" for path in paths)
    return f"""{commands}

feat(check): validate staged paths

Why:

The staged paths need one exact read-only plan.

The checker can now report mechanical readiness.

What:

- validate every staged path
"""


def _stage_sample(root: Path) -> None:
    """Create and stage the common sample path."""
    (root / "sample.txt").write_text("sample\n", encoding="utf-8")
    _git(root, "add", "--", "sample.txt")


def _module_environment() -> dict[str, str]:
    """Expose the project module while keeping the fixture as caller root."""
    environment = os.environ.copy()
    project_root = str(Path(commit_plan_check.__file__).resolve().parent.parent)
    previous = environment.get("PYTHONPATH")
    environment["PYTHONPATH"] = (
        f"{project_root}{os.pathsep}{previous}" if previous else project_root
    )
    return environment


def _adapter_arguments(root: Path, adapter: str, output_format: str) -> list[str]:
    """Return one module or root-launcher command over the same service."""
    common = ["--root", str(root), "--format", output_format]
    if adapter == "module":
        return [sys.executable, "-m", "tools.commit_plan_check", *common]
    project_root = Path(commit_plan_check.__file__).resolve().parent.parent
    return [str(project_root / "commit-plan-check.bat"), *common]


def _run_adapter(
    root: Path,
    adapter: str,
    output_format: str,
) -> subprocess.CompletedProcess[str]:
    """Run one public adapter with bounded process completion."""
    return subprocess.run(
        _adapter_arguments(root, adapter, output_format),
        cwd=root,
        env=_module_environment(),
        check=False,
        capture_output=True,
        text=True,
        timeout=20,
    )


def _snapshot(root: Path) -> _RepositoryState:
    """Capture every repository surface named by the no-mutation contract."""
    plan = root / "a.commit"
    ignored = _git(
        root,
        "ls-files",
        "--others",
        "--ignored",
        "--exclude-standard",
        "-z",
        "--",
        "a.*",
    ).stdout
    return _RepositoryState(
        head=_git(root, "rev-parse", "HEAD").stdout.decode().strip(),
        index_tree=_git(root, "write-tree").stdout.decode().strip(),
        staged_paths=tuple(
            part.decode()
            for part in _git(
                root,
                "diff",
                "--cached",
                "--name-only",
                "--no-renames",
                "-z",
            ).stdout.split(b"\0")
            if part
        ),
        worktree_diff=_git(root, "diff", "--binary").stdout,
        plan_bytes=plan.read_bytes() if plan.exists() else None,
        ignored_root=tuple(part.decode() for part in ignored.split(b"\0") if part),
    )


def _human_fragments(payload: object) -> tuple[str, ...]:
    """Project structured evidence into the fragments rendered for humans."""
    structured = cast("dict[str, object]", payload)
    groups = cast("list[dict[str, object]]", structured["groups"])
    fragments = [
        f"state: {structured['state']}",
        f"ready: {str(structured['ready']).lower()}",
    ]
    for group in groups:
        fragments.append(cast("str", group["subject"]))
        fragments.extend(cast("list[str]", group["paths"]))
    fragments.extend(cast("list[str]", structured["diagnostics"]))
    return tuple(fragments)


@pytest.fixture(
    params=(
        ("valid", "valid", 0, True),
        ("missing-plan", "missing-plan", _NON_READY_STATUS, True),
        ("empty-plan", "empty-plan", _NON_READY_STATUS, True),
        ("empty-staged-set", "empty-staged-set", _NON_READY_STATUS, False),
        ("mismatch", "invalid-plan", _NON_READY_STATUS, True),
    ),
    ids=lambda value: value[0],
)
def evidence_case(
    tmp_path: Path,
    request: pytest.FixtureRequest,
) -> tuple[str, int, tuple[subprocess.CompletedProcess[str], ...], _RepositoryState, _RepositoryState]:
    """Run both formats and adapters outside the measured assertion phase."""
    scenario, expected_state, expected_status, stage_sample = request.param
    _initialize_repository(tmp_path)
    if stage_sample:
        _stage_sample(tmp_path)
    if scenario in {"valid", "empty-staged-set"}:
        (tmp_path / "a.commit").write_text(_valid_plan("sample.txt"), encoding="utf-8")
    elif scenario == "empty-plan":
        (tmp_path / "a.commit").write_bytes(b"")
    elif scenario == "mismatch":
        (tmp_path / "a.commit").write_text(_valid_plan("other.txt"), encoding="utf-8")
    before = _snapshot(tmp_path)
    results = tuple(
        _run_adapter(tmp_path, adapter, output_format)
        for output_format in ("human", "json")
        for adapter in ("module", "launcher")
    )
    return expected_state, expected_status, results, before, _snapshot(tmp_path)


def test_entry_points_share_status_evidence_and_repository_immutability(
    evidence_case: tuple[
        str,
        int,
        tuple[subprocess.CompletedProcess[str], ...],
        _RepositoryState,
        _RepositoryState,
    ],
) -> None:
    """All readiness states have adapter parity and exact before/after state."""
    expected_state, expected_status, results, before, after = evidence_case
    module_human, launcher_human, module_json, launcher_json = results

    assert before == after
    assert {result.returncode for result in results} == {expected_status}
    assert all(result.stderr == "" for result in results)
    assert module_human.stdout == launcher_human.stdout
    assert module_json.stdout == launcher_json.stdout
    payload = json.loads(module_json.stdout)
    assert payload["state"] == expected_state
    assert all(fragment in module_human.stdout for fragment in _human_fragments(payload))


@pytest.fixture
def rename_results(
    tmp_path: Path,
) -> tuple[subprocess.CompletedProcess[str], subprocess.CompletedProcess[str]]:
    """Run both adapters against a real staged rename during setup."""
    _initialize_repository(tmp_path)
    (tmp_path / "old.txt").write_text("renamed\n", encoding="utf-8")
    _git(tmp_path, "add", "--", "old.txt")
    _commit(tmp_path, "test: add rename source")
    _git(tmp_path, "mv", "old.txt", "new.txt")
    (tmp_path / "a.commit").write_text(
        _valid_plan("old.txt", "new.txt"),
        encoding="utf-8",
    )
    return (
        _run_adapter(tmp_path, "module", "json"),
        _run_adapter(tmp_path, "launcher", "json"),
    )


def test_rename_inventory_contains_source_and_destination(
    rename_results: tuple[
        subprocess.CompletedProcess[str],
        subprocess.CompletedProcess[str],
    ],
) -> None:
    """No-renames inventory treats both sides as exact plan membership."""
    module, launcher = rename_results
    assert module.returncode == launcher.returncode == 0
    assert module.stdout == launcher.stdout
    assert set(json.loads(module.stdout)["staged_paths"]) == {"old.txt", "new.txt"}


@pytest.fixture
def operational_results(
    tmp_path: Path,
) -> tuple[subprocess.CompletedProcess[str], subprocess.CompletedProcess[str]]:
    """Run both adapters with a root whose Git inventory cannot be read."""
    (tmp_path / ".git").mkdir()
    (tmp_path / "a.commit").write_text(_valid_plan("sample.txt"), encoding="utf-8")
    return (
        _run_adapter(tmp_path, "module", "json"),
        _run_adapter(tmp_path, "launcher", "json"),
    )


def test_failed_git_inventory_has_stable_operational_diagnostic(
    operational_results: tuple[
        subprocess.CompletedProcess[str],
        subprocess.CompletedProcess[str],
    ],
) -> None:
    """An untrustworthy Git boundary maps to status two on both adapters."""
    module, launcher = operational_results
    assert module.returncode == launcher.returncode == _OPERATIONAL_STATUS
    assert module.stdout == launcher.stdout == ""
    assert module.stderr == launcher.stderr
    assert module.stderr.startswith("commit-plan-check: cannot inventory commit plan:")


@pytest.fixture
def redirected_evidence(
    tmp_path: Path,
) -> tuple[_RepositoryState, _RepositoryState, subprocess.CompletedProcess[str], Path]:
    """Redirect launcher stdout as a caller-owned ignored file during setup."""
    _initialize_repository(tmp_path)
    _stage_sample(tmp_path)
    (tmp_path / "a.commit").write_text(_valid_plan("sample.txt"), encoding="utf-8")
    evidence = tmp_path / "a.check-evidence.json"
    before = _snapshot(tmp_path)
    with evidence.open("w", encoding="utf-8", newline="\n") as stream:
        result = subprocess.run(
            _adapter_arguments(tmp_path, "launcher", "json"),
            cwd=tmp_path,
            env=_module_environment(),
            check=False,
            stdout=stream,
            stderr=subprocess.PIPE,
            text=True,
            timeout=20,
        )
    return before, _snapshot(tmp_path), result, evidence


def test_caller_owned_redirection_is_the_only_observable_change(
    redirected_evidence: tuple[
        _RepositoryState,
        _RepositoryState,
        subprocess.CompletedProcess[str],
        Path,
    ],
) -> None:
    """The checker owns no write when the caller redirects its stdout."""
    before, after, result, evidence = redirected_evidence
    assert result.returncode == 0
    assert result.stderr == ""
    assert before == replace(after, ignored_root=before.ignored_root)
    assert set(after.ignored_root) == {*before.ignored_root, evidence.name}
    assert json.loads(evidence.read_text(encoding="utf-8"))["ready"] is True


def _request_arguments(root: Path) -> Namespace:
    """Create ignored caller inputs and paired outputs for the request gate."""
    for name in ("assessment", "report", "changes", "response"):
        (root / f"a.{name}.md").write_text(f"{name}\n", encoding="utf-8")
    return Namespace(
        plan="docs/v0.11.0/plan.v0.11.0.commit-plan-check.md",
        implementation_step="4",
        umbrella=None,
        round_number=1,
        assessment_file=str(root / "a.assessment.md"),
        implementation_report_file=str(root / "a.report.md"),
        change_summary_file=str(root / "a.changes.md"),
        writer_response_file=str(root / "a.response.md"),
        guidance_file=None,
        plan_validation_command=[],
        request_validation_command=[],
        request_content_output=str(root / "a.request.md"),
        transcript_summary_output=str(root / "a.summary.md"),
    )


@pytest.fixture
def requestor_rejections(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[str, str, bool, bool]:
    """Exercise both real-Git request rejections outside the measured call."""
    _initialize_repository(tmp_path)
    _stage_sample(tmp_path)
    (tmp_path / "a.commit").write_text(_valid_plan("other.txt"), encoding="utf-8")
    arguments = _request_arguments(tmp_path)

    with pytest.raises(ReviewExchangeError, match="commit plan is not ready") as invalid:
        requestor._render_from_arguments(arguments, tmp_path)

    (tmp_path / "a.commit").write_text(_valid_plan("sample.txt"), encoding="utf-8")
    trees = iter((_TREE_A, _TREE_B))

    def capture_drifting_tree(_root: Path) -> str:
        return next(trees)

    monkeypatch.setattr(requestor, "capture_index_tree", capture_drifting_tree)
    with pytest.raises(ReviewExchangeError, match="index changed") as drift:
        requestor._render_from_arguments(arguments, tmp_path)

    return (
        str(invalid.value),
        str(drift.value),
        (tmp_path / "a.request.md").exists(),
        (tmp_path / "a.summary.md").exists(),
    )


def test_requestor_rejects_invalid_plan_and_index_drift_without_outputs(
    requestor_rejections: tuple[str, str, bool, bool],
) -> None:
    """Both request-publication rejection paths preserve paired outputs."""
    invalid, drift, request_exists, summary_exists = requestor_rejections

    assert "commit plan is not ready" in invalid
    assert "index changed" in drift
    assert not request_exists
    assert not summary_exists


# eof
