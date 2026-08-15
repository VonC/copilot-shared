#!/usr/bin/env python3
"""Render paired implementation code-review artifacts from one round input.

Step 1 gives the implementation request and its transcript summary one frozen
source of truth. Pure rendering reuses the shared exchange envelope, while the
command boundary validates exact ignored UTF-8 inputs before writing the pair.
"""

# ruff: noqa: EM101, EM102, TRY003

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from string import Template
from typing import TYPE_CHECKING, NoReturn

from tools._models import find_project_root
from tools.code_review_evidence import capture_index_tree
from tools.code_review_validation import (
    DEFAULT_PROJECT_VALIDATION_COMMANDS,
    ResolvedValidationSet,
    resolve_code_review_validation,
)
from tools.review_exchange_models import (
    ExchangeIdentity,
    ReviewContext,
    ReviewExchangeError,
    ReviewFamily,
    ReviewRole,
    format_local_timestamp,
    validate_local_timestamp,
)
from tools.review_exchange_models_envelope import (
    Envelope,
    parse_envelope_markdown,
    render_envelope_markdown,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

_PLAN_RE = re.compile(r"^plan\.(v\d+\.\d+\.\d+)\.([a-z0-9][a-z0-9_-]*)\.md$")
_TEMPLATE_PATH = Path(__file__).resolve().parents[1] / "templates" / (
    "code-review-request.template.md"
)
_JSON_SECTION = "## JSON"
_TREE_OBJECT_RE = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
_FATAL_EXIT = 2


@dataclass(frozen=True)
class CodeReviewRoundInput:
    """Validated code-review identity and separate authored round inputs."""

    context: ReviewContext
    round_number: int
    created_at: str
    assessment: str
    implementation_report: str
    change_summary: str
    writer_response: str
    request_index_tree: str
    resolved_validation_set: ResolvedValidationSet
    human_guidance: str | None = None

    def __post_init__(self) -> None:
        """Reject invalid identity, round, timestamp, or authored content."""
        if self.context.identity.family is not ReviewFamily.CODE:
            raise ReviewExchangeError("renderer requires a code review context")
        if self.round_number <= 0:
            raise ReviewExchangeError("round must be positive")
        validate_local_timestamp(self.created_at)
        authored = {
            "assessment": self.assessment,
            "implementation report": self.implementation_report,
            "change summary": self.change_summary,
            "writer response": self.writer_response,
        }
        for label, value in authored.items():
            if not value.strip():
                raise ReviewExchangeError(f"{label} must be non-empty")
        if _TREE_OBJECT_RE.fullmatch(self.request_index_tree) is None:
            raise ReviewExchangeError("request index tree must be a Git tree object")
        if self.resolved_validation_set.__class__ is not ResolvedValidationSet:
            raise ReviewExchangeError("resolved validation set must be typed")
        if self.human_guidance is not None and not self.human_guidance.strip():
            raise ReviewExchangeError("human guidance must be non-empty when supplied")


@dataclass(frozen=True)
class CodeReviewRequestRender:
    """Complete implementation request and paired substantive summary."""

    request_content: str
    transcript_summary: str

    def __post_init__(self) -> None:
        """Reject an incomplete paired rendering result."""
        if not self.request_content or not self.transcript_summary:
            raise ReviewExchangeError("paired request rendering must be non-empty")


@dataclass(frozen=True)
class _CodeReviewEvidence:
    """One typed source for canonical JSON and human-readable evidence."""

    request_index_tree: str
    resolved_validation_set: ResolvedValidationSet

    def to_payload(self) -> dict[str, object]:
        """Return the canonical authored JSON object."""
        return {
            "request_index_tree": self.request_index_tree,
            "resolved_validation_set": self.resolved_validation_set.to_payload(),
        }

    def summary(self) -> str:
        """Return the paired human-readable representation."""
        lines = [
            f"request_index_tree: {self.request_index_tree}",
            "resolved_validation_set:",
        ]
        for entry in self.resolved_validation_set.commands:
            sources = ", ".join(entry.sources)
            lines.append(f"- {entry.command} (sources: {sources})")
        return "\n".join(lines)


class _ArgumentParser(argparse.ArgumentParser):
    """Raise command errors so the adapter returns one stable exit code."""

    def error(self, message: str) -> NoReturn:
        """Convert argparse termination into a renderer validation error."""
        raise ReviewExchangeError(message)


def _positive_int(value: str) -> int:
    """Parse one positive command-line integer."""
    try:
        parsed = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("value must be positive") from error
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be positive")
    return parsed


def code_review_context(
    plan: str | Path,
    implementation_step: str,
    umbrella: str | Path | None = None,
) -> ReviewContext:
    """Derive one fixed code-family context from an exact plan and step."""
    plan_path = Path(plan).expanduser().resolve()
    match = _PLAN_RE.fullmatch(plan_path.name)
    if match is None:
        raise ReviewExchangeError("reviewed plan has an unsupported plan file name")
    if not implementation_step.strip():
        raise ReviewExchangeError("implementation step must be non-empty")
    version, slug = match.groups()
    identity = ExchangeIdentity(ReviewFamily.CODE, "code", version, slug)
    umbrella_path = None if umbrella is None else Path(umbrella).expanduser().resolve()
    return ReviewContext(identity, plan_path, umbrella_path, implementation_step.strip())


def _identity_label(source: CodeReviewRoundInput) -> str:
    """Return a filename-safe label for unique authored headings."""
    return f"step {source.context.implementation_step} {source.context.identity.slug}"


def _identity_fields(source: CodeReviewRoundInput) -> str:
    """Render the exact human-readable plan, step, round, and umbrella fields."""
    context = source.context
    umbrella = (
        context.umbrella_path.as_posix()
        if context.umbrella_path is not None
        else "none"
    )
    return "\n".join(
        (
            f"Umbrella draft: {umbrella}",
            f"Implementation plan: {context.document_path.as_posix()}",
            f"Implementation step: {context.implementation_step}",
            f"Review round: {source.round_number}",
        ),
    )


def _response_section(source: CodeReviewRoundInput, *, heading_level: int) -> str:
    """Render optional literal guidance separately from the writer response."""
    hashes = "#" * heading_level
    label = _identity_label(source)
    if source.human_guidance is None:
        return (
            f"{hashes} Writer response for {label} round {source.round_number}\n\n"
            f"Writer response: {source.writer_response.strip()}"
        )
    return (
        f"{hashes} Human guidance and writer response for {label} "
        f"round {source.round_number}\n\n"
        f"Human guidance: {source.human_guidance.rstrip()}\n\n"
        f"Writer response: {source.writer_response.strip()}"
    )


def _code_review_evidence(source: CodeReviewRoundInput) -> _CodeReviewEvidence:
    """Return the one typed payload used by request and transcript rendering."""
    return _CodeReviewEvidence(
        source.request_index_tree,
        source.resolved_validation_set,
    )


def _code_review_evidence_json(source: CodeReviewRoundInput) -> str:
    """Render canonical JSON for the authored evidence block."""
    return json.dumps(_code_review_evidence(source).to_payload(), indent=2, sort_keys=True)


def _code_review_evidence_summary(source: CodeReviewRoundInput) -> str:
    """Derive a human-readable paired summary from the same typed payload."""
    return _code_review_evidence(source).summary()


def _request_authored_content(source: CodeReviewRoundInput) -> str:
    """Render specialized H2 content from the canonical code template."""
    values = {
        "identity_label": _identity_label(source),
        "round_number": str(source.round_number),
        "identity_fields": _identity_fields(source),
        "code_review_evidence": _code_review_evidence_json(source),
        "assessment": source.assessment.strip(),
        "implementation_report": source.implementation_report.strip(),
        "change_summary": source.change_summary.strip(),
        "response_section": _response_section(source, heading_level=2),
    }
    try:
        template = Template(_TEMPLATE_PATH.read_text(encoding="utf-8"))
    except (OSError, UnicodeError) as error:
        raise ReviewExchangeError(f"cannot read request template: {error}") from error
    return template.substitute(values).rstrip() + "\n"


def _transcript_summary(source: CodeReviewRoundInput) -> str:
    """Render substantive requestor feedback without protocol boilerplate."""
    label = _identity_label(source)
    sections = (
        f"### Review identity for {label} round {source.round_number}\n\n"
        f"{_identity_fields(source)}",
        f"### Code review evidence for {label} round {source.round_number}\n\n"
        f"{_code_review_evidence_summary(source)}",
        f"### Requestor assessment for {label} round {source.round_number}\n\n"
        f"{source.assessment.strip()}",
        f"### Implementation report for {label} round {source.round_number}\n\n"
        f"{source.implementation_report.strip()}",
        f"### Change summary for {label} round {source.round_number}\n\n"
        f"{source.change_summary.strip()}",
        _response_section(source, heading_level=3),
        f"### Reviewer focus for {label} round {source.round_number}\n\n"
        "Check the exact plan step, staged implementation, test evidence, repaired "
        "path inventory, and a.commit accuracy.",
    )
    return "\n\n".join(sections) + "\n"


def render_code_review_request(source: CodeReviewRoundInput) -> CodeReviewRequestRender:
    """Render and validate the complete code request and summary together."""
    context = source.context
    envelope = Envelope(
        identity=context.identity,
        umbrella_path=context.umbrella_path,
        document_path=context.document_path,
        implementation_step=context.implementation_step,
        role=ReviewRole.REQUESTOR,
        round_number=source.round_number,
        created_at=source.created_at,
    )
    request_content = render_envelope_markdown(
        envelope,
        _request_authored_content(source),
    )
    parsed, _authored = parse_envelope_markdown(request_content)
    if parsed != envelope or _JSON_SECTION not in request_content:
        raise ReviewExchangeError("rendered request failed shared envelope validation")
    return CodeReviewRequestRender(request_content, _transcript_summary(source))


def _is_effectively_ignored(project_root: Path, path: Path) -> bool:
    """Ask Git whether one exact caller-owned root path is ignored."""
    git_executable = shutil.which("git")
    if git_executable is None:
        raise ReviewExchangeError("cannot validate ignored file: git was not found")
    try:
        result = subprocess.run(  # noqa: S603 - fixed Git executable and arguments
            [
                git_executable,
                "-C",
                str(project_root),
                "check-ignore",
                "-q",
                "--",
                str(path.relative_to(project_root)),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as error:
        raise ReviewExchangeError(f"cannot validate ignored file: {error}") from error
    return result.returncode == 0


def _root_file(
    project_root: Path,
    value: str | Path,
    label: str,
    *,
    input_file: bool,
) -> Path:
    """Validate one ignored caller-owned root input or output path."""
    path = Path(value).expanduser().resolve()
    if path.parent != project_root:
        raise ReviewExchangeError(f"{label} must be directly under project root")
    if not path.name.startswith("a."):
        raise ReviewExchangeError(f"{label} must use a project-root a.* name")
    if input_file and not path.is_file():
        raise ReviewExchangeError(f"{label} does not exist")
    if not input_file and path.exists() and not path.is_file():
        raise ReviewExchangeError(f"{label} must not be a directory")
    if not _is_effectively_ignored(project_root, path):
        raise ReviewExchangeError(f"{label} is not effectively ignored")
    return path


def _read_utf8(path: Path, label: str) -> str:
    """Read one validated caller-owned input exactly once as UTF-8."""
    try:
        with path.open(encoding="utf-8", newline="") as stream:
            return stream.read()
    except UnicodeError as error:
        raise ReviewExchangeError(f"{label} is not valid UTF-8") from error
    except OSError as error:
        raise ReviewExchangeError(f"cannot read {label}: {error}") from error


def _write_utf8(path: Path, content: str, label: str) -> None:
    """Write one validated caller-owned output in one UTF-8 operation."""
    try:
        with path.open("w", encoding="utf-8", newline="\n") as stream:
            stream.write(content)
    except OSError as error:
        raise ReviewExchangeError(f"cannot write {label}: {error}") from error


def _parser() -> _ArgumentParser:
    """Build the exact context, input, and paired-output CLI contract."""
    parser = _ArgumentParser(prog="code-review-request")
    parser.add_argument("--plan", required=True)
    parser.add_argument("--implementation-step", required=True)
    parser.add_argument("--umbrella")
    parser.add_argument("--round-number", required=True, type=_positive_int)
    parser.add_argument("--assessment-file", required=True)
    parser.add_argument("--implementation-report-file", required=True)
    parser.add_argument("--change-summary-file", required=True)
    parser.add_argument("--writer-response-file", required=True)
    parser.add_argument("--guidance-file")
    parser.add_argument("--plan-validation-command", action="append", default=[])
    parser.add_argument("--request-validation-command", action="append", default=[])
    parser.add_argument("--request-content-output", required=True)
    parser.add_argument("--transcript-summary-output", required=True)
    return parser


def _render_from_arguments(args: argparse.Namespace, project_root: Path) -> None:
    """Validate paths, read each input once, and write the paired result once."""
    root = project_root.resolve()
    context = code_review_context(args.plan, args.implementation_step, args.umbrella)
    input_specs = (
        ("assessment", args.assessment_file, "assessment file"),
        ("implementation_report", args.implementation_report_file, "implementation report file"),
        ("change_summary", args.change_summary_file, "change summary file"),
        ("writer_response", args.writer_response_file, "writer response file"),
    )
    inputs = {
        key: _root_file(root, value, label, input_file=True)
        for key, value, label in input_specs
    }
    guidance = None if args.guidance_file is None else _root_file(
        root, args.guidance_file, "guidance file", input_file=True,
    )
    request_output = _root_file(
        root, args.request_content_output, "request content output", input_file=False,
    )
    summary_output = _root_file(
        root, args.transcript_summary_output, "transcript summary output", input_file=False,
    )
    all_paths = (*inputs.values(), request_output, summary_output)
    if guidance is not None:
        all_paths = (*all_paths, guidance)
    if len(set(all_paths)) != len(all_paths):
        raise ReviewExchangeError("caller-owned input and output paths must be distinct")
    resolved_validation_set = resolve_code_review_validation(
        DEFAULT_PROJECT_VALIDATION_COMMANDS,
        args.plan_validation_command,
        args.request_validation_command,
    )
    request_index_tree = capture_index_tree(root)
    source = CodeReviewRoundInput(
        context=context,
        round_number=args.round_number,
        created_at=format_local_timestamp(),
        assessment=_read_utf8(inputs["assessment"], "assessment file"),
        implementation_report=_read_utf8(
            inputs["implementation_report"], "implementation report file",
        ),
        change_summary=_read_utf8(inputs["change_summary"], "change summary file"),
        writer_response=_read_utf8(inputs["writer_response"], "writer response file"),
        request_index_tree=request_index_tree,
        resolved_validation_set=resolved_validation_set,
        human_guidance=None if guidance is None else _read_utf8(guidance, "guidance file"),
    )
    rendered = render_code_review_request(source)
    _write_utf8(request_output, rendered.request_content, "request content output")
    _write_utf8(summary_output, rendered.transcript_summary, "transcript summary output")


def main(
    argv: Sequence[str] | None = None,
    *,
    project_root: Path | None = None,
) -> int:
    """Run paired code-review rendering with one stable fatal exit code."""
    try:
        args = _parser().parse_args(argv)
        root = find_project_root(Path.cwd()) if project_root is None else project_root
        _render_from_arguments(args, root)
    except (ReviewExchangeError, OSError) as error:
        sys.stderr.write(f"ERROR: {error}\n")
        return _FATAL_EXIT
    return 0


if __name__ == "__main__":  # pragma: no cover - thin launcher boundary
    raise SystemExit(main())


# eof
