#!/usr/bin/env python3
"""Non-interactive command adapter for the v0.11.0 review-exchange core.

Step 4 gives later requestor and reviewer workflows one stable JSON command
surface. The adapter resolves one exact document identity, validates ignored
caller-owned UTF-8 inputs before reading them once, delegates every lifecycle
mutation to ``ReviewExchangeCore``, and keeps progress off standard output.
"""

# ruff: noqa: BLE001, EM101, EM102, TRY003

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, NoReturn, Protocol, TextIO

from tools import find_project_root
from tools.review_exchange_core import ReviewExchangeCore
from tools.review_exchange_models import (
    ArtifactPaths,
    ArtifactState,
    ExchangeIdentity,
    FamilyPolicy,
    ReviewConfiguration,
    ReviewContext,
    ReviewExchangeError,
    ReviewFamily,
)
from tools.review_exchange_paths import derive_artifact_paths, validate_activation
from tools.review_exchange_store import ReviewExchangeStore
from tools.review_exchange_wait import WaitOutcome, WaitProgress

if TYPE_CHECKING:
    from tools.review_exchange_human import ConfirmationDecision, ResolutionResult
    from tools.review_exchange_models_coordination import CoordinationRecord
    from tools.review_exchange_observer import ExchangeObservation
    from tools.review_exchange_wait import WaitResult


_DOCUMENT_RE = re.compile(
    r"^(feature-request|issue|design|plan)\.(v\d+\.\d+\.\d+)\."
    r"([a-z0-9][a-z0-9_-]*)\.md$",
)
_STOP_STATES = frozenset(
    {
        ArtifactState.ANSWER_PUBLICATION_IN_PROGRESS,
        ArtifactState.TRANSCRIPT_REPAIR_PENDING,
        ArtifactState.CONVERGENCE_GATE,
        ArtifactState.OWNING_ACTION_PENDING,
        ArtifactState.ESCALATED,
        ArtifactState.ABANDONED_MID_ROUND,
        ArtifactState.INTERRUPTED_ANSWER_PUBLICATION,
        ArtifactState.INTERRUPTED_TRANSCRIPT_APPEND,
        ArtifactState.ABANDONED_REQUEST,
        ArtifactState.ABANDONED_ANSWER,
        ArtifactState.INCONSISTENT,
    },
)


class CorePort(Protocol):
    """Lifecycle operations used by the command adapter."""

    def classify(self) -> ExchangeObservation:
        """Return the current exact-path state."""
        ...

    def start(self) -> CoordinationRecord:
        """Start the first active round."""
        ...

    def publish_request(self, markdown: str, transcript_content: str) -> CoordinationRecord:
        """Publish one request."""
        ...

    def publish_answer(self, markdown: str, transcript_content: str) -> CoordinationRecord:
        """Publish one answer."""
        ...

    def wait_for_exact(
        self,
        expected: ArtifactState,
        *,
        timeout_seconds: int | None,
        poll_interval: float,
        progress_interval: float,
        progress_callback: Callable[[WaitProgress], None] | None,
    ) -> WaitResult:
        """Wait for one counterpart artifact."""
        ...

    def consume_answer(
        self,
        *,
        reviewed_work_changed: bool,
        disagreement: bool = False,
    ) -> CoordinationRecord:
        """Consume one intermediate answer."""
        ...

    def continue_round(self) -> CoordinationRecord:
        """Advance to the next automated round."""
        ...

    def escalate(self, reason: str) -> CoordinationRecord:
        """Stop automation with durable evidence."""
        ...

    def confirm(
        self,
        label: str,
        *,
        guidance: str | None = None,
    ) -> ConfirmationDecision:
        """Persist one human convergence choice."""
        ...

    def cancel(self, reason: str) -> CoordinationRecord:
        """Cancel a convergence gate."""
        ...

    def resolve_escalation(self, summary: str, *, archive: bool) -> ResolutionResult:
        """Resolve stopped evidence and create a fresh round."""
        ...

    def complete(self) -> bool:
        """Finish a human-authorized owning action."""
        ...


@dataclass(frozen=True)
class Runtime:
    """Exact project, protocol context, paths, configuration, and core port."""

    project_root: Path
    context: ReviewContext
    paths: ArtifactPaths
    configuration: ReviewConfiguration
    core: CorePort


def _empty_extra() -> Mapping[str, Any]:
    """Return one typed empty operation payload."""
    return {}


@dataclass(frozen=True)
class OperationResult:
    """One delegated operation outcome before common JSON rendering."""

    outcome: str
    observation: ExchangeObservation | None = None
    exit_code: int | None = None
    extra: Mapping[str, Any] = field(default_factory=_empty_extra)


class JsonArgumentParser(argparse.ArgumentParser):
    """Raise parse errors so main can emit the mandatory final JSON object."""

    def error(self, message: str) -> NoReturn:
        """Convert argparse diagnostics to typed fatal input."""
        raise ReviewExchangeError(message)


def _positive_int(value: str) -> int:
    """Parse one positive integer command value."""
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be positive")
    return parsed


def _positive_float(value: str) -> float:
    """Parse one positive floating-point command value."""
    parsed = float(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be positive")
    return parsed


def _parser() -> JsonArgumentParser:
    """Build the command parser with shared exact-context arguments."""
    common = JsonArgumentParser(add_help=False)
    common.add_argument("--family", choices=("specification", "code"), required=True)
    common.add_argument("--document", required=True)
    common.add_argument("--umbrella")
    common.add_argument("--implementation-step")
    common.add_argument("--convergence-signal", required=True)
    common.add_argument("--another-round-label", required=True)
    common.add_argument("--continue-owning-workflow-label", required=True)

    parser = JsonArgumentParser(prog="review-exchange")
    subparsers = parser.add_subparsers(dest="operation", required=True)
    for name in ("activate", "status", "start", "continue", "complete"):
        subparsers.add_parser(name, parents=[common])
    for name in ("publish-request", "publish-answer"):
        command = subparsers.add_parser(name, parents=[common])
        command.add_argument("--content-file", required=True)
        command.add_argument("--summary-file", required=True)
    for name in ("wait-request", "wait-answer"):
        command = subparsers.add_parser(name, parents=[common])
        command.add_argument("--timeout-seconds", type=_positive_int)
        command.add_argument("--poll-interval", type=_positive_float, default=1.0)
        command.add_argument("--progress-interval", type=_positive_float, default=30.0)
    consume = subparsers.add_parser("consume-answer", parents=[common])
    consume.add_argument(
        "--reviewed-work-changed",
        choices=("true", "false"),
        required=True,
    )
    consume.add_argument("--disagreement", action="store_true")
    for name in ("escalate", "cancel", "resolve", "archive"):
        command = subparsers.add_parser(name, parents=[common])
        command.add_argument("--summary-file", required=True)
    confirm = subparsers.add_parser("confirm", parents=[common])
    confirm.add_argument("--choice-label", required=True)
    confirm.add_argument("--guidance-file")
    return parser


def _context_from_document(
    family_value: str,
    document_value: str | Path,
    umbrella_value: str | Path | None,
    implementation_step: str | None,
) -> ReviewContext:
    """Infer validated identity tokens from one exact reviewed document name."""
    document = Path(document_value).expanduser().resolve()
    match = _DOCUMENT_RE.fullmatch(document.name)
    if match is None:
        raise ReviewExchangeError("reviewed document has an unsupported file name")
    prefix, version, slug = match.groups()
    family = ReviewFamily(family_value)
    if family is ReviewFamily.CODE:
        if prefix != "plan":
            raise ReviewExchangeError("code review requires an exact plan document")
        type_token = "code"  # noqa: S105 - protocol token, not a credential
    else:
        type_token = "design-specification" if prefix == "design" else prefix
    identity = ExchangeIdentity(family, type_token, version, slug)
    umbrella = (
        None
        if umbrella_value is None
        else Path(umbrella_value).expanduser().resolve()
    )
    return ReviewContext(identity, document, umbrella, implementation_step)


def _build_runtime(args: argparse.Namespace, project_root: Path) -> Runtime:
    """Construct the exact-path lifecycle facade for one invocation."""
    context = _context_from_document(
        args.family,
        args.document,
        args.umbrella,
        args.implementation_step,
    )
    policy = FamilyPolicy(
        args.convergence_signal,
        args.another_round_label,
        args.continue_owning_workflow_label,
    )
    configuration = ReviewConfiguration.load(project_root)
    paths = derive_artifact_paths(project_root, context)
    store = ReviewExchangeStore(paths)
    core = ReviewExchangeCore(store, context, policy, configuration)
    return Runtime(project_root, context, paths, configuration, core)


def _is_effectively_ignored(project_root: Path, path: Path) -> bool:
    """Ask Git whether one caller-owned root input is effectively ignored."""
    relative = path.relative_to(project_root)
    git_executable = shutil.which("git")
    if git_executable is None:
        raise ReviewExchangeError("cannot validate ignored input: git was not found")
    try:
        result = subprocess.run(  # noqa: S603 - fixed Git command and separated paths
            [
                git_executable,
                "-C",
                str(project_root),
                "check-ignore",
                "-q",
                "--",
                str(relative),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as error:
        raise ReviewExchangeError(f"cannot validate ignored input: {error}") from error
    return result.returncode == 0


def _read_input_file(project_root: Path, value: str | Path, label: str) -> str:
    """Validate and read one ignored root ``a.*`` UTF-8 input exactly once."""
    path = Path(value).expanduser().resolve()
    if path.parent != project_root.resolve():
        raise ReviewExchangeError(f"{label} file must be directly under project root")
    if not path.name.startswith("a."):
        raise ReviewExchangeError(f"{label} file must use a project-root a.* name")
    if not path.is_file():
        raise ReviewExchangeError(f"{label} file does not exist: {path}")
    if not _is_effectively_ignored(project_root, path):
        raise ReviewExchangeError(f"{label} file is not effectively ignored by Git")
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise ReviewExchangeError(f"cannot read {label} file as UTF-8: {error}") from error


def _progress_writer(stream: TextIO) -> Callable[[WaitProgress], None]:
    """Build a JSON-lines progress callback that writes only to stderr."""
    def report(progress: WaitProgress) -> None:
        payload = {
            "progress": {
                "elapsed_seconds": progress.elapsed_seconds,
                "remaining_seconds": progress.remaining_seconds,
                "state": progress.state.value,
            },
        }
        stream.write(f"{json.dumps(payload, sort_keys=True)}\n")
        stream.flush()

    return report


def _require_activation(runtime: Runtime) -> OperationResult | None:
    """Return a disabled stop or validate the fixed transient path set."""
    if not runtime.configuration.enabled:
        return OperationResult("disabled", exit_code=3)
    validate_activation(runtime.project_root, runtime.paths)
    return None


def _dispatch_simple(
    args: argparse.Namespace,
    runtime: Runtime,
    _stderr: TextIO,
) -> OperationResult:
    """Handle operations that need no caller-owned Markdown."""
    if args.operation == "activate":
        return OperationResult("activated")
    if args.operation == "status":
        return OperationResult("observed")
    if args.operation == "start":
        runtime.core.start()
        return OperationResult("started")
    if args.operation == "continue":
        runtime.core.continue_round()
        return OperationResult("continued")
    return OperationResult("completed", extra={"removed": runtime.core.complete()})


def _dispatch_publication(
    args: argparse.Namespace,
    runtime: Runtime,
    _stderr: TextIO,
) -> OperationResult:
    """Read and delegate one request or answer publication."""
    content = _read_input_file(runtime.project_root, args.content_file, "content")
    summary = _read_input_file(runtime.project_root, args.summary_file, "summary")
    if args.operation == "publish-request":
        runtime.core.publish_request(content, summary)
    else:
        runtime.core.publish_answer(content, summary)
    return OperationResult("published")


def _dispatch_wait(
    args: argparse.Namespace,
    runtime: Runtime,
    stderr: TextIO,
) -> OperationResult:
    """Run one bounded request or answer wait."""
    expected = (
        ArtifactState.REQUEST_PENDING
        if args.operation == "wait-request"
        else ArtifactState.ANSWER_PENDING
    )
    result = runtime.core.wait_for_exact(
        expected,
        timeout_seconds=args.timeout_seconds,
        poll_interval=args.poll_interval,
        progress_interval=args.progress_interval,
        progress_callback=_progress_writer(stderr),
    )
    code = 0 if result.outcome is WaitOutcome.FOUND else 3
    return OperationResult(result.outcome.value, result.observation, code)


def _dispatch_consume(
    args: argparse.Namespace,
    runtime: Runtime,
    _stderr: TextIO,
) -> OperationResult:
    """Delegate one intermediate-answer assessment."""
    runtime.core.consume_answer(
        reviewed_work_changed=args.reviewed_work_changed == "true",
        disagreement=args.disagreement,
    )
    return OperationResult("consumed")


def _dispatch_recovery(
    args: argparse.Namespace,
    runtime: Runtime,
    _stderr: TextIO,
) -> OperationResult:
    """Delegate escalation, cancellation, or clear-or-archive recovery."""
    summary = _read_input_file(runtime.project_root, args.summary_file, "summary")
    if args.operation == "escalate":
        runtime.core.escalate(summary)
        return OperationResult("escalated")
    if args.operation == "cancel":
        runtime.core.cancel(summary)
        return OperationResult("cancelled")
    resolution = runtime.core.resolve_escalation(
        summary,
        archive=args.operation == "archive",
    )
    return OperationResult(
        "archived" if args.operation == "archive" else "resolved",
        extra={"archived_paths": [path.as_posix() for path in resolution.archived_paths]},
    )


def _dispatch_confirm(
    args: argparse.Namespace,
    runtime: Runtime,
    _stderr: TextIO,
) -> OperationResult:
    """Read optional guidance and delegate a human confirmation."""
    guidance = (
        None
        if args.guidance_file is None
        else _read_input_file(runtime.project_root, args.guidance_file, "guidance")
    )
    decision = runtime.core.confirm(args.choice_label, guidance=guidance)
    return OperationResult(
        decision.outcome.value,
        extra={"owning_action_authorized": decision.owning_action_authorized},
    )


OperationHandler = Callable[[argparse.Namespace, Runtime, TextIO], OperationResult]
_SIMPLE_HANDLER: OperationHandler = _dispatch_simple
_HANDLERS: dict[str, OperationHandler] = {
    "activate": _SIMPLE_HANDLER,
    "status": _SIMPLE_HANDLER,
    "start": _SIMPLE_HANDLER,
    "continue": _SIMPLE_HANDLER,
    "complete": _SIMPLE_HANDLER,
    "publish-request": _dispatch_publication,
    "publish-answer": _dispatch_publication,
    "wait-request": _dispatch_wait,
    "wait-answer": _dispatch_wait,
    "consume-answer": _dispatch_consume,
    "escalate": _dispatch_recovery,
    "cancel": _dispatch_recovery,
    "resolve": _dispatch_recovery,
    "archive": _dispatch_recovery,
    "confirm": _dispatch_confirm,
}


def _dispatch(
    args: argparse.Namespace,
    runtime: Runtime,
    stderr: TextIO,
) -> OperationResult:
    """Validate activation and delegate through one operation handler."""
    if args.operation == "status" and not runtime.configuration.enabled:
        return OperationResult("disabled", exit_code=3)
    if args.operation != "status":
        activation = _require_activation(runtime)
        if activation is not None:
            return activation
    handler = _HANDLERS.get(args.operation)
    if handler is None:
        raise ReviewExchangeError(f"unsupported operation: {args.operation}")
    return handler(args, runtime, stderr)


def _paths_payload(paths: ArtifactPaths) -> dict[str, str]:
    """Render every applicable fixed path with stable keys."""
    return {
        "answer": paths.answer.as_posix(),
        "coordination": paths.coordination.as_posix(),
        "request": paths.request.as_posix(),
        "tombstone": paths.tombstone.as_posix(),
        "transcript": paths.transcript.as_posix(),
        "transition_lock": paths.transition_lock.as_posix(),
    }


def _success_payload(runtime: Runtime, operation: str, result: OperationResult) -> dict[str, Any]:
    """Build the mandatory final result from the delegated state."""
    if result.outcome == "disabled":
        state = "disabled"
        record = None
        diagnostic = "review mode is disabled"
    else:
        observation = result.observation or runtime.core.classify()
        state = observation.state.value
        record = observation.record
        diagnostic = observation.diagnostic
    payload: dict[str, Any] = {
        "diagnostic": diagnostic,
        "identity": runtime.context.identity.to_dict(),
        "operation": operation,
        "outcome": result.outcome,
        "paths": _paths_payload(runtime.paths),
        "round": record.round_number if record is not None else None,
        "state": state,
    }
    payload.update(result.extra)
    return payload


def _fatal_payload(operation: str, diagnostic: str) -> dict[str, Any]:
    """Build the stable schema for invalid input or unexpected failure."""
    return {
        "diagnostic": diagnostic,
        "identity": None,
        "operation": operation,
        "outcome": "fatal-input",
        "paths": {},
        "round": None,
        "state": "fatal",
    }


def _operation_name(argv: Sequence[str]) -> str:
    """Return the first token for parse-failure reporting."""
    return argv[0] if argv and not argv[0].startswith("-") else "unknown"


def main(argv: Sequence[str] | None = None) -> int:
    """Run one operation and emit exactly one final UTF-8 JSON object."""
    arguments = list(sys.argv[1:] if argv is None else argv)
    operation = _operation_name(arguments)
    try:
        args = _parser().parse_args(arguments)
        operation = args.operation
        project_root = find_project_root(Path.cwd()).resolve()
        runtime = _build_runtime(args, project_root)
        result = _dispatch(args, runtime, sys.stderr)
        payload = _success_payload(runtime, operation, result)
        if result.exit_code is not None:
            code = result.exit_code
        else:
            code = 3 if payload["state"] in {state.value for state in _STOP_STATES} else 0
    except ReviewExchangeError as error:
        payload = _fatal_payload(operation, str(error))
        code = 2
    except Exception as error:
        payload = _fatal_payload(operation, str(error))
        code = 2
    sys.stdout.write(f"{json.dumps(payload, ensure_ascii=False, sort_keys=True)}\n")
    return code


if __name__ == "__main__":
    raise SystemExit(main())


# eof
