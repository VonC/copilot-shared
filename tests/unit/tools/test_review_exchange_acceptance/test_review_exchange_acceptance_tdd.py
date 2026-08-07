"""Integrated acceptance coverage for the public review-exchange boundaries.

Step 5 composes the command adapter, real Git ignore resolution, exact artifact
paths, multi-round lifecycle, convergence choices, archives, and deterministic
wait reporting in temporary consuming repositories. Subprocess-heavy journeys
run in fixtures so their assertions remain below the duration-call gate.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

from tools import review_exchange_cli as cli
from tools.review_exchange_core import ReviewExchangeCore
from tools.review_exchange_models import (
    ArtifactPaths,
    ExchangeIdentity,
    FamilyPolicy,
    ReviewConfiguration,
    ReviewContext,
    ReviewDisposition,
    ReviewFamily,
    ReviewRole,
)
from tools.review_exchange_models_envelope import Envelope, render_envelope_markdown
from tools.review_exchange_paths import derive_artifact_paths
from tools.review_exchange_store import ReviewExchangeStore

if TYPE_CHECKING:
    from argparse import Namespace
    from collections.abc import Sequence

# ruff: noqa: S603, S607

pytestmark = pytest.mark.skipif(
    shutil.which("git") is None,
    reason="git is required for review-exchange acceptance tests",
)

_PROJECT_ROOT = Path(__file__).resolve().parents[4]
_CLI = _PROJECT_ROOT / "tools" / "review_exchange_cli.py"
_CREATED_AT = "2026-08-05T09:00:00+02:00"
_SUBPROCESS_TIMEOUT = 20
_EXPECTED_STOP = 3
_SECOND_ROUND = 2
_WAIT_LIMIT = 4


@dataclass(frozen=True)
class CliResult:
    """One parsed CLI subprocess result."""

    code: int
    payload: dict[str, Any]


@dataclass(frozen=True)
class IsolationJourney:
    """Observable results for activation and concurrent identity acceptance."""

    disabled: CliResult
    unignored: CliResult
    specification_status: CliResult
    code_status: CliResult
    duplicate_start: CliResult
    specification: ReviewContext
    code: ReviewContext


@dataclass(frozen=True)
class CodeJourney:
    """Observable results for a complete multi-round implementation exchange."""

    gate: CliResult
    first_confirmation: CliResult
    replayed_confirmation: CliResult
    owning_status: CliResult
    completion: CliResult
    paths: Any
    transcript: str


@dataclass(frozen=True)
class ResolutionJourney:
    """Observable results for human guidance and archived fresh resumption."""

    override: CliResult
    publication: CliResult
    escalation: CliResult
    resolution: CliResult
    paths: Any
    transcript: str


def _git(repo: Path, *arguments: str) -> None:
    """Run one real Git command in a temporary consuming repository."""
    subprocess.run(
        ["git", *arguments],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
        timeout=_SUBPROCESS_TIMEOUT,
    )


def _init_repo(root: Path, *, ignored: bool = True, marker: bool = True) -> None:
    """Create one Git repository with explicit opt-in and ignore policy."""
    root.mkdir(parents=True, exist_ok=True)
    _git(root, "init", "-q")
    if ignored:
        (root / ".gitignore").write_text("a.*\n", encoding="utf-8")
    if marker:
        (root / "a.review-mode").write_text("", encoding="utf-8")


def _context(
    root: Path,
    family: ReviewFamily,
    slug: str,
    *,
    step: str | None = None,
) -> ReviewContext:
    """Create one exact document and its accepted review context."""
    docs = root / "docs" / "v0.11.0"
    docs.mkdir(parents=True, exist_ok=True)
    if family is ReviewFamily.CODE:
        document = docs / f"plan.v0.11.0.{slug}.md"
        identity = ExchangeIdentity(family, "code", "v0.11.0", slug)
    else:
        document = docs / f"feature-request.v0.11.0.{slug}.md"
        identity = ExchangeIdentity(family, "feature-request", "v0.11.0", slug)
    document.write_text(f"# {slug}\n", encoding="utf-8")
    return ReviewContext(identity, document.resolve(), None, step)


def _policy(context: ReviewContext) -> FamilyPolicy:
    """Return family labels registered by the later specialized adapters."""
    if context.identity.family is ReviewFamily.CODE:
        return FamilyPolicy("commit-ready", "Rework and review again", "Commit")
    return FamilyPolicy(
        "consolidation-ready",
        "Revise and review again",
        "Consolidate",
    )


def _common(context: ReviewContext) -> list[str]:
    """Render the exact common command arguments for one exchange context."""
    policy = _policy(context)
    arguments = [
        "--family",
        context.identity.family.value,
        "--document",
        str(context.document_path),
        "--convergence-signal",
        policy.convergence_signal,
        "--another-round-label",
        policy.another_round_label,
        "--continue-owning-workflow-label",
        policy.continue_owning_workflow_label,
    ]
    if context.implementation_step is not None:
        arguments.extend(["--implementation-step", context.implementation_step])
    return arguments


def _run_cli(
    root: Path,
    context: ReviewContext,
    operation: str,
    extra: Sequence[str] = (),
) -> CliResult:
    """Invoke the real command adapter in a separate Python process."""
    environment = {
        **os.environ,
        "PRJ_DIR": str(root),
        "PYTHONPATH": os.pathsep.join(
            filter(None, (str(_PROJECT_ROOT), os.environ.get("PYTHONPATH", ""))),
        ),
    }
    completed = subprocess.run(
        [sys.executable, str(_CLI), operation, *_common(context), *extra],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=environment,
        timeout=_SUBPROCESS_TIMEOUT,
    )
    stdout_lines = tuple(completed.stdout.splitlines())
    assert len(stdout_lines) == 1, completed
    return CliResult(
        completed.returncode,
        json.loads(stdout_lines[0]),
    )


def _summary(
    context: ReviewContext,
    round_number: int,
    *,
    guidance: str | None = None,
) -> str:
    """Render the mandatory identity summary accepted by the core."""
    lines = ["Umbrella draft: none"]
    if context.identity.family is ReviewFamily.CODE:
        lines.extend(
            (
                f"Implementation plan: {context.document_path.as_posix()}",
                f"Implementation step: {context.implementation_step}",
            ),
        )
    else:
        lines.append(f"Reviewed specification: {context.document_path.as_posix()}")
    lines.append(f"Review round: {round_number}")
    if guidance is not None:
        lines.extend(("", f"Human guidance: {guidance}"))
    return "\n".join(lines) + "\n"


def _artifact(
    context: ReviewContext,
    role: ReviewRole,
    round_number: int,
    *,
    disposition: ReviewDisposition | None = None,
    guidance: str | None = None,
) -> str:
    """Render one complete public request or answer artifact."""
    envelope = Envelope(
        context.identity,
        context.umbrella_path,
        context.document_path,
        context.implementation_step,
        role,
        round_number,
        _CREATED_AT,
        disposition,
    )
    authored = (
        _summary(context, round_number, guidance=guidance)
        if role is ReviewRole.REQUESTOR
        else "Reviewer feedback for the acceptance journey.\n"
    )
    return render_envelope_markdown(envelope, authored)


def _input(root: Path, name: str, content: str) -> Path:
    """Write one caller-owned ignored input file and return its exact path."""
    path = root / f"a.{name}.md"
    path.write_text(content, encoding="utf-8")
    return path


def _publish(
    context: ReviewContext,
    role: ReviewRole,
    round_number: int,
    *,
    disposition: ReviewDisposition | None = None,
    guidance: str | None = None,
) -> CliResult:
    """Publish one role artifact through the real subprocess boundary."""
    root = context.document_path.parents[2]
    content = _input(
        root,
        "acceptance-content",
        _artifact(
            context,
            role,
            round_number,
            disposition=disposition,
            guidance=guidance,
        ),
    )
    report = _input(
        root,
        "acceptance-report",
        f"{role.value} report for round {round_number}.",
    )
    operation = "publish-request" if role is ReviewRole.REQUESTOR else "publish-answer"
    return _run_cli(
        root,
        context,
        operation,
        ("--content-file", str(content), "--summary-file", str(report)),
    )


@pytest.fixture
def isolation_journey(tmp_path: Path) -> IsolationJourney:
    """Run activation failures and two independent exchanges through subprocesses."""
    disabled_root = tmp_path / "disabled"
    _init_repo(disabled_root, marker=False)
    disabled_context = _context(disabled_root, ReviewFamily.CODE, "disabled", step="5")
    disabled = _run_cli(disabled_root, disabled_context, "activate")

    unignored_root = tmp_path / "unignored"
    _init_repo(unignored_root, ignored=False)
    unignored_context = _context(unignored_root, ReviewFamily.CODE, "unignored", step="5")
    unignored = _run_cli(unignored_root, unignored_context, "activate")

    active_root = tmp_path / "active"
    _init_repo(active_root)
    specification = _context(active_root, ReviewFamily.SPECIFICATION, "specification")
    code = _context(active_root, ReviewFamily.CODE, "implementation", step="5")
    assert _run_cli(active_root, specification, "start").code == 0
    assert _run_cli(active_root, code, "start").code == 0
    duplicate_start = _run_cli(active_root, code, "start")
    assert _publish(specification, ReviewRole.REQUESTOR, 1).code == 0
    specification_status = _run_cli(active_root, specification, "status")
    code_status = _run_cli(active_root, code, "status")
    return IsolationJourney(
        disabled,
        unignored,
        specification_status,
        code_status,
        duplicate_start,
        specification,
        code,
    )


def test_opt_in_real_git_and_exact_identity_isolation(
    isolation_journey: IsolationJourney,
) -> None:
    """Activation is inert by default and isolates real Git-backed exchanges."""
    _assert_activation_failures(isolation_journey)
    _assert_identity_isolation(isolation_journey)


def _assert_activation_failures(journey: IsolationJourney) -> None:
    """Check disabled, unignored, and duplicate-start stops."""
    actual = (
        journey.disabled.code,
        journey.disabled.payload["outcome"],
        journey.unignored.code,
        journey.duplicate_start.code,
    )
    assert actual == (
        _EXPECTED_STOP,
        "disabled",
        _SECOND_ROUND,
        _SECOND_ROUND,
    )
    assert "not effectively ignored" in journey.unignored.payload["diagnostic"]


def _assert_identity_isolation(journey: IsolationJourney) -> None:
    """Check independent states and the intentional code.code identity path."""
    assert journey.specification_status.payload["state"] == "request-pending"
    assert journey.code_status.payload["state"] == "round-in-progress"
    code_paths = derive_artifact_paths(journey.code.document_path.parents[2], journey.code)
    assert ".code.code." in code_paths.coordination.name
    assert journey.specification.identity != journey.code.identity


@pytest.fixture
def code_journey(tmp_path: Path) -> CodeJourney:
    """Run two code rounds through convergence and replayed owning authorization."""
    root = tmp_path / "code-journey"
    _init_repo(root)
    context = _context(root, ReviewFamily.CODE, "multi-round", step="5")
    paths = derive_artifact_paths(root, context)
    assert _run_cli(root, context, "start").code == 0
    assert _publish(context, ReviewRole.REQUESTOR, 1).code == 0
    assert _publish(
        context,
        ReviewRole.REVIEWER,
        1,
        disposition=ReviewDisposition.CHANGES_REQUESTED,
    ).code == 0
    consumed = _run_cli(
        root,
        context,
        "consume-answer",
        ("--reviewed-work-changed", "true"),
    )
    assert consumed.code == 0
    assert _run_cli(root, context, "continue").payload["round"] == _SECOND_ROUND
    assert _publish(context, ReviewRole.REQUESTOR, _SECOND_ROUND).code == 0
    assert _publish(
        context,
        ReviewRole.REVIEWER,
        _SECOND_ROUND,
        disposition=ReviewDisposition.CONVERGENCE_RECOMMENDED,
    ).code == _EXPECTED_STOP
    gate = _run_cli(root, context, "status")
    first_confirmation = _run_cli(root, context, "confirm", ("--choice-label", "Commit"))
    replayed_confirmation = _run_cli(
        root,
        context,
        "confirm",
        ("--choice-label", "Commit"),
    )
    owning_status = _run_cli(root, context, "status")
    completion = _run_cli(root, context, "complete")
    transcript = paths.transcript.read_text(encoding="utf-8")
    return CodeJourney(
        gate,
        first_confirmation,
        replayed_confirmation,
        owning_status,
        completion,
        paths,
        transcript,
    )


def test_multiround_convergence_and_cross_session_authorization_replay(
    code_journey: CodeJourney,
) -> None:
    """Intermediate automation ends only after replayable human authorization."""
    _assert_owning_authorization(code_journey)
    _assert_code_transcript_order(code_journey)


def _assert_owning_authorization(journey: CodeJourney) -> None:
    """Check convergence, replay, and idempotent owning completion."""
    actual = (
        journey.gate.code,
        journey.gate.payload["state"],
        journey.first_confirmation.payload["owning_action_authorized"],
        journey.replayed_confirmation.payload["owning_action_authorized"],
        journey.owning_status.payload["state"],
        journey.completion.code,
        journey.completion.payload["state"],
    )
    assert actual == (
        _EXPECTED_STOP,
        "convergence-gate",
        True,
        True,
        "owning-action-pending",
        0,
        "idle",
    )
    assert not any((journey.paths.answer.exists(), journey.paths.coordination.exists()))


def _assert_code_transcript_order(journey: CodeJourney) -> None:
    """Check round order, stable confirmation identity, and offset timestamps."""
    ordered = [
        journey.transcript.index("request-round-1"),
        journey.transcript.index("answer-round-1"),
        journey.transcript.index("request-round-2"),
        journey.transcript.index("answer-round-2"),
        journey.transcript.index("human-confirmation-round-2"),
    ]
    assert ordered == sorted(ordered)
    assert journey.transcript.count("human-confirmation-round-2") == 1
    assert re.search(r"Recorded: .*[-+]\d\d:\d\d", journey.transcript)


@pytest.fixture
def resolution_journey(tmp_path: Path) -> ResolutionJourney:
    """Run a specification override, escalation, archive, and fresh resumption."""
    root = tmp_path / "resolution-journey"
    _init_repo(root)
    context = _context(root, ReviewFamily.SPECIFICATION, "human-resolution")
    paths = derive_artifact_paths(root, context)
    assert _run_cli(root, context, "start").code == 0
    assert _publish(context, ReviewRole.REQUESTOR, 1).code == 0
    assert _publish(
        context,
        ReviewRole.REVIEWER,
        1,
        disposition=ReviewDisposition.CONVERGENCE_RECOMMENDED,
    ).code == _EXPECTED_STOP
    guidance = "Recheck the exact transcript boundary."
    guidance_file = _input(root, "acceptance-guidance", guidance)
    override = _run_cli(
        root,
        context,
        "confirm",
        (
            "--choice-label",
            "Revise and review again",
            "--guidance-file",
            str(guidance_file),
        ),
    )
    publication = _publish(
        context,
        ReviewRole.REQUESTOR,
        _SECOND_ROUND,
        guidance=guidance,
    )
    reason = _input(root, "acceptance-escalation", "Human evidence choice required.")
    escalation = _run_cli(root, context, "escalate", ("--summary-file", str(reason)))
    resolution = _input(root, "acceptance-resolution", "Archive and restart cleanly.")
    resolved = _run_cli(root, context, "archive", ("--summary-file", str(resolution)))
    transcript = paths.transcript.read_text(encoding="utf-8")
    return ResolutionJourney(override, publication, escalation, resolved, paths, transcript)


def test_human_override_guidance_archive_and_fresh_round(
    resolution_journey: ResolutionJourney,
) -> None:
    """Another-round guidance and archived human resolution remain observable."""
    _assert_resolution_state(resolution_journey)
    _assert_resolution_transcript(resolution_journey)


def _assert_resolution_state(journey: ResolutionJourney) -> None:
    """Check the override, archive paths, and authoritative fresh round."""
    archived = journey.resolution.payload["archived_paths"]
    actual = (
        journey.override.payload["outcome"],
        journey.override.payload["round"],
        journey.publication.code,
        journey.escalation.payload["state"],
        journey.resolution.payload["round"],
        len(archived),
    )
    assert actual == (
        "another-round",
        _SECOND_ROUND,
        0,
        "escalated",
        _EXPECTED_STOP,
        _SECOND_ROUND,
    )
    assert all(Path(path).is_file() for path in archived)
    assert not journey.paths.request.exists()


def _assert_resolution_transcript(journey: ResolutionJourney) -> None:
    """Check one confirmation, one resolution, and retained human guidance."""
    assert journey.transcript.count("Outcome: human-confirmation") == 1
    assert journey.transcript.count("Outcome: human-resolution") == 1
    assert "Recheck the exact transcript boundary." in journey.transcript


class FakeTime:
    """Advance one monotonic deadline and wall clock without real sleeping."""

    def __init__(self) -> None:
        """Start deterministic clocks and record every sleep interval."""
        self.wall = datetime(2026, 8, 5, 8, 0, tzinfo=UTC)
        self.monotonic = 10.0
        self.sleeps: list[float] = []

    def now(self) -> datetime:
        """Return the injected wall time."""
        return self.wall

    def monotonic_now(self) -> float:
        """Return the injected monotonic value."""
        return self.monotonic

    def sleep(self, seconds: float) -> None:
        """Advance both clocks by one requested poll interval."""
        self.sleeps.append(seconds)
        self.monotonic += seconds
        self.wall += timedelta(seconds=seconds)


def test_long_wait_has_progress_stderr_and_one_monotonic_deadline(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A long logical wait reports progress without a real-time test dependency."""
    root = tmp_path / "wait"
    root.mkdir()
    context = _context(root, ReviewFamily.CODE, "wait", step="5")
    store = ReviewExchangeStore(derive_artifact_paths(root, context))
    clock = FakeTime()
    policy = _policy(context)
    configuration = ReviewConfiguration(
        enabled=True,
        wait_timeout_seconds=_WAIT_LIMIT,
    )
    core = ReviewExchangeCore(
        store,
        context,
        policy,
        configuration,
        wall_clock=clock.now,
        monotonic_clock=clock.monotonic_now,
        sleeper=clock.sleep,
    )
    core.start()
    runtime = cli.Runtime(root, context, store.paths, configuration, core)
    def fixed_root(_start: Path) -> Path:
        return root

    def fixed_runtime(_args: Namespace, _root: Path) -> cli.Runtime:
        return runtime

    def valid_activation(_root: Path, _paths: ArtifactPaths) -> None:
        return None

    monkeypatch.setattr(cli, "find_project_root", fixed_root)
    monkeypatch.setattr(cli, "_build_runtime", fixed_runtime)
    monkeypatch.setattr(cli, "validate_activation", valid_activation)

    code = cli.main(
        [
            "wait-answer",
            *_common(context),
            "--timeout-seconds",
            str(_WAIT_LIMIT),
            "--poll-interval",
            "1",
            "--progress-interval",
            "1",
        ],
    )

    captured = capsys.readouterr()
    stdout_lines = captured.out.splitlines()
    progress = [json.loads(line)["progress"] for line in captured.err.splitlines()]
    assert code == _EXPECTED_STOP, captured.out + captured.err
    assert len(stdout_lines) == 1
    assert json.loads(stdout_lines[0])["outcome"] == "timed-out"
    assert len(progress) >= _EXPECTED_STOP
    assert [item["elapsed_seconds"] for item in progress] == sorted(
        item["elapsed_seconds"] for item in progress
    )
    assert sum(clock.sleeps) == _WAIT_LIMIT


# eof
