"""Bounded routing and authorized continuation for implementation code review.

The adapter derives one exact plan-step context from the current workflow,
checks only that identity's fixed exchange paths, and delegates the existing
batch-commit action after durable human authorization. It never discovers
documents or protocol artifacts by directory traversal.
"""

# ruff: noqa: EM101, EM102, TRY003

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from typing import TYPE_CHECKING, Final, cast

from tools import prompt_workflow_plan as plan
from tools import prompt_workflow_steps as steps
from tools.code_review_request import code_review_context
from tools.prompt_workflow_models import PromptWorkflowError
from tools.review_exchange_core import ReviewExchangeCore
from tools.review_exchange_models import (
    ArtifactState,
    ConfirmationOutcome,
    FamilyPolicy,
    ReviewConfiguration,
    ReviewContext,
)
from tools.review_exchange_paths import derive_artifact_paths
from tools.review_exchange_store import ReviewExchangeStore

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from tools.prompt_workflow_models import MemoryRecord, Topic, WorkflowState

CODE_REVIEW_POLICY: Final[FamilyPolicy] = FamilyPolicy(
    "commit-ready",
    "Rework and review again",
    "Commit",
)
CODE_REVIEW_REQUESTOR: Final[str] = "code-review-requestor.md"


class CodeReviewRoutingError(PromptWorkflowError):
    """Raised when one exact code-review route is absent or inconsistent."""


@dataclass(frozen=True)
class CodeReviewRoute:
    """One exact implementation context and its observed exchange state."""

    context: ReviewContext
    state: ArtifactState


def _umbrella_path(root: Path, topic: Topic) -> Path | None:
    """Resolve the child draft's sole explicit umbrella path, when present."""
    prefix = "- Umbrella: "
    matches = [
        line.removeprefix(prefix).strip()
        for line in topic.draft_path.read_text(encoding="utf-8").splitlines()
        if line.startswith(prefix)
    ]
    if not matches:
        return None
    if len(matches) != 1 or not matches[0]:
        raise CodeReviewRoutingError("draft has an ambiguous umbrella marker")
    umbrella = (root / matches[0]).resolve()
    try:
        umbrella.relative_to(root.resolve())
    except ValueError as error:
        raise CodeReviewRoutingError("umbrella is outside the project root") from error
    if not umbrella.is_file():
        raise CodeReviewRoutingError(f"umbrella does not exist: {matches[0]}")
    return umbrella


def _plan_steps(state: WorkflowState) -> tuple[str, ...]:
    """Return the exact declared validation-plan step identifiers."""
    if state.validation_plan is None:
        raise CodeReviewRoutingError("code review requires a validation plan")
    return tuple(
        item.number
        for item in plan.parse_validation_steps(
            state.validation_plan.read_text(encoding="utf-8"),
        )
    )


def _context(
    root: Path,
    topic: Topic,
    state: WorkflowState,
    record: MemoryRecord | None,
) -> ReviewContext:
    """Build and validate the current plan-step context without searching."""
    if state.plan is None:
        raise CodeReviewRoutingError("code review requires an exact plan document")
    if record is None or record.plan_step is None:
        raise CodeReviewRoutingError("code review requires an implementation step")
    if record.version != topic.version or record.topic != topic.slug:
        raise CodeReviewRoutingError("workflow topic differs from the resolved plan")
    if record.plan_step not in _plan_steps(state):
        raise CodeReviewRoutingError(f"unknown plan step: {record.plan_step}")
    context = code_review_context(
        state.plan,
        record.plan_step,
        _umbrella_path(root, topic),
    )
    identity = context.identity
    if identity.version != topic.version or identity.slug != topic.slug:
        raise CodeReviewRoutingError("plan identity differs from the workflow topic")
    return context


def _core(root: Path, context: ReviewContext) -> ReviewExchangeCore:
    """Bind the shared observer to one code-review identity and policy."""
    return ReviewExchangeCore(
        ReviewExchangeStore(derive_artifact_paths(root, context)),
        context,
        CODE_REVIEW_POLICY,
        ReviewConfiguration.load(root),
    )


def resolve_code_review_route(
    root: Path,
    topic: Topic,
    state: WorkflowState,
    record: MemoryRecord | None,
) -> CodeReviewRoute | None:
    """Return the marker-enabled or already-live exact plan-step route.

    A cold route exists only while review mode is enabled. Once coordination is
    durable, its fixed paths win even if the marker is later removed. Any live
    evidence for the same code identity but another implementation step fails
    closed instead of being silently ignored.
    """
    if state.plan is None or record is None or record.plan_step is None:
        return None
    probe_context = code_review_context(
        state.plan,
        record.plan_step,
        _umbrella_path(root, topic),
    )
    paths = derive_artifact_paths(root, probe_context)
    store = ReviewExchangeStore(paths)
    persisted = store.read_coordination()
    if (
        persisted is not None
        and persisted.context.implementation_step
        != probe_context.implementation_step
    ):
        raise CodeReviewRoutingError(
            "live code exchange uses another implementation step",
        )
    configuration = ReviewConfiguration.load(root)
    live_paths = (
        paths.request,
        paths.answer,
        paths.coordination,
        paths.tombstone,
        paths.transition_lock,
    )
    has_exact_evidence = any(path.exists() for path in live_paths)
    if not configuration.enabled and not has_exact_evidence:
        return None
    context = _context(root, topic, state, record)
    observation = ReviewExchangeCore(
        store,
        context,
        CODE_REVIEW_POLICY,
        configuration,
    ).classify()
    if observation.state is ArtifactState.INCONSISTENT:
        raise CodeReviewRoutingError(f"inconsistent code exchange: {observation.diagnostic}")
    return CodeReviewRoute(context, observation.state)


def command_for_route(
    root: Path,
    route: CodeReviewRoute,
    prefix: str,
    render_step: Callable[[str, str, str, str], str],
) -> str:
    """Render the specialized requestor handoff for one immutable route."""
    document = route.context.document_path.relative_to(root.resolve()).as_posix()
    implementation_step = cast("str", route.context.implementation_step)
    return render_step(
        prefix,
        CODE_REVIEW_REQUESTOR,
        document,
        implementation_step,
    )


def run_batch_commit(
    arguments: tuple[str, ...],
    *,
    cwd: Path,
) -> subprocess.CompletedProcess[str]:
    """Invoke the existing strict batch-commit workflow at one external seam.

    The launcher ships with llm-shared, so it is located through
    ``llm_shared_dir`` rather than the project root; ``cwd`` stays the reviewed
    project because that is where `a.commit` and the staged work live.
    """
    command = steps.llm_shared_dir() / "bin" / "gcba.bat"
    return subprocess.run(  # noqa: S603
        [str(command), *arguments],
        cwd=cwd,
        check=False,
        text=True,
    )


def continue_authorized_commit(
    root: Path,
    topic: Topic,
    state: WorkflowState,
    record: MemoryRecord | None,
) -> int:
    """Run one existing batch commit only for durable owning authorization."""
    route = resolve_code_review_route(root, topic, state, record)
    if route is None or route.state is not ArtifactState.OWNING_ACTION_PENDING:
        raise CodeReviewRoutingError("code-review commit is not authorized")
    core = _core(root, route.context)
    coordination = core.store.read_coordination(required=True)
    if (
        coordination is None
        or coordination.confirmed_outcome
        is not ConfirmationOutcome.CONTINUE_OWNING_WORKFLOW
    ):
        raise CodeReviewRoutingError("code-review commit is not durably authorized")
    result = run_batch_commit(
        ("--root-a-commit", "--non-interactive"),
        cwd=root.resolve(),
    )
    if result.returncode == 0:
        core.complete()
    return result.returncode


# eof
