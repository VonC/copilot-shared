"""Exact path derivation and activation checks for review exchanges.

Step 1 derives the fixed artifact set from validated context, parses artifact
names back to their complete identity, and verifies all transient probes with
one effective Git-ignore call before protocol mutation.
"""

# ruff: noqa: EM101, EM102, S105, TRY003

from __future__ import annotations

import re
import subprocess
from typing import TYPE_CHECKING, Final

from tools.review_exchange_models import (
    ArchiveKind,
    ArtifactPaths,
    ExchangeIdentity,
    ReviewContext,
    ReviewExchangeError,
    ReviewFamily,
)

if TYPE_CHECKING:
    from pathlib import Path

_COMPACT_TIMESTAMP_RE: Final[re.Pattern[str]] = re.compile(
    r"^\d{8}-\d{6}$",
)
_VERSION_PART: Final[str] = r"(?P<version>v\d+\.\d+\.\d+)"
_SLUG_PART: Final[str] = r"(?P<slug>[a-z0-9][a-z0-9_-]*)"
_TYPE_PART: Final[str] = (
    r"(?P<type_token>feature-request|issue|design-specification|plan|code)"
)
_REQUEST_ANSWER_RE: Final[re.Pattern[str]] = re.compile(
    rf"^a\.review-(?:requested|answer)\.{_TYPE_PART}\."
    rf"{_VERSION_PART}\.{_SLUG_PART}\.md$",
)
_COORDINATION_RE: Final[re.Pattern[str]] = re.compile(
    rf"^a\.review-(?:active|consumed)\."
    rf"(?P<family>specification|code)\.{_TYPE_PART}\."
    rf"{_VERSION_PART}\.{_SLUG_PART}\.md$",
)
_LOCK_RE: Final[re.Pattern[str]] = re.compile(
    rf"^a\.review-lock\.(?P<family>specification|code)\."
    rf"{_TYPE_PART}\.{_VERSION_PART}\.{_SLUG_PART}\.lock$",
)
_ARCHIVE_RE: Final[re.Pattern[str]] = re.compile(
    rf"^a\.review-archive\.(?P<family>specification|code)\."
    rf"{_TYPE_PART}\.{_VERSION_PART}\.{_SLUG_PART}\."
    r"\d{8}-\d{6}\.(?:request|answer|consumed|coordination)\.md$",
)
_TRANSCRIPT_RE: Final[re.Pattern[str]] = re.compile(
    rf"^review\.{_TYPE_PART}\.{_VERSION_PART}\.{_SLUG_PART}\.md$",
)
_IGNORE_PROBE_TIMESTAMP: Final[str] = "20000101-000000"


def _identity_suffix(identity: ExchangeIdentity) -> str:
    """Return the common type, version, and slug filename suffix."""
    return f"{identity.type_token}.{identity.version}.{identity.slug}"


def derive_artifact_paths(
    project_root: Path,
    context: ReviewContext,
) -> ArtifactPaths:
    """Derive every fixed path once from exact validated exchange context."""
    root = project_root.resolve()
    try:
        context.document_path.relative_to(root)
    except ValueError as error:
        raise ReviewExchangeError(
            f"reviewed document is outside project root: {context.document_path}",
        ) from error
    identity = context.identity
    suffix = _identity_suffix(identity)
    family_suffix = f"{identity.family.value}.{suffix}"
    transcript = context.document_path.parent / f"review.{suffix}.md"
    return ArtifactPaths(
        identity=identity,
        project_root=root,
        transcript=transcript,
        request=root / f"a.review-requested.{suffix}.md",
        answer=root / f"a.review-answer.{suffix}.md",
        coordination=root / f"a.review-active.{family_suffix}.md",
        tombstone=root / f"a.review-consumed.{family_suffix}.md",
        transition_lock=root / f"a.review-lock.{family_suffix}.lock",
    )


def archive_path(
    paths: ArtifactPaths,
    compact_timestamp: str,
    kind: ArchiveKind,
) -> Path:
    """Derive one exact evidence archive path for a selected artifact kind."""
    if _COMPACT_TIMESTAMP_RE.fullmatch(compact_timestamp) is None:
        raise ReviewExchangeError(
            "archive name requires compact local timestamp YYYYMMDD-HHMMSS",
        )
    identity = paths.identity
    name = (
        f"a.review-archive.{identity.family.value}.{identity.type_token}."
        f"{identity.version}.{identity.slug}.{compact_timestamp}.{kind.value}.md"
    )
    return paths.project_root / name


def transient_paths_for_ignore(paths: ArtifactPaths) -> tuple[Path, ...]:
    """Return every transient kind represented by one exact ignored probe."""
    archives = tuple(
        archive_path(paths, _IGNORE_PROBE_TIMESTAMP, kind)
        for kind in ArchiveKind
    )
    return (
        paths.request,
        paths.answer,
        paths.coordination,
        paths.tombstone,
        paths.transition_lock,
        *archives,
    )


def _identity_from_match(match: re.Match[str]) -> ExchangeIdentity:
    """Build and validate an identity from a parsed artifact filename."""
    values = match.groupdict()
    type_token = values["type_token"]
    family_value = values.get("family")
    family = (
        ReviewFamily(family_value)
        if family_value is not None
        else (
            ReviewFamily.CODE
            if type_token == "code"
            else ReviewFamily.SPECIFICATION
        )
    )
    return ExchangeIdentity(
        family=family,
        type_token=type_token,
        version=values["version"],
        slug=values["slug"],
    )


def parse_transient_identity(path: Path) -> ExchangeIdentity:
    """Parse complete identity from any supported transient artifact name."""
    for pattern in (
        _REQUEST_ANSWER_RE,
        _COORDINATION_RE,
        _LOCK_RE,
        _ARCHIVE_RE,
    ):
        match = pattern.fullmatch(path.name)
        if match is not None:
            return _identity_from_match(match)
    raise ReviewExchangeError(f"unrecognized review transient path: {path.name}")


def parse_transcript_identity(path: Path) -> ExchangeIdentity:
    """Parse complete identity from a supported transcript filename."""
    match = _TRANSCRIPT_RE.fullmatch(path.name)
    if match is None:
        raise ReviewExchangeError(f"unrecognized review transcript path: {path.name}")
    return _identity_from_match(match)


def _run_git(
    command: list[str],
    *,
    cwd: Path,
    input_text: str | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run one bounded Git query without a command shell."""
    return subprocess.run(  # noqa: S603
        command,
        cwd=cwd,
        input=input_text,
        text=True,
        capture_output=True,
        check=False,
    )


def validate_activation(project_root: Path, paths: ArtifactPaths) -> None:
    """Fail outside Git or when any derived transient is not ignored."""
    root = project_root.resolve()
    if root != paths.project_root:
        raise ReviewExchangeError("activation project root differs from derived paths")
    _require_git_repository(root)
    relative = tuple(
        path.relative_to(root).as_posix()
        for path in transient_paths_for_ignore(paths)
    )
    _require_ignored_transients(root, relative)


def _require_git_repository(root: Path) -> None:
    """Fail when Git cannot verify the selected project root."""
    repository = _run_git(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=root,
    )
    if repository.returncode != 0 or repository.stdout.strip() != "true":
        raise ReviewExchangeError("review mode requires a Git repository")


def _require_ignored_transients(root: Path, relative: tuple[str, ...]) -> None:
    """Submit the exact transient set through one effective ignore query."""
    input_text = "".join(f"{path}\n" for path in relative)
    ignored = _run_git(
        ["git", "check-ignore", "--stdin"],
        cwd=root,
        input_text=input_text,
    )
    if ignored.returncode not in {0, 1}:
        diagnostic = ignored.stderr.strip() or "git check-ignore failed"
        raise ReviewExchangeError(f"cannot verify transient ignore coverage: {diagnostic}")
    matched = frozenset(line for line in ignored.stdout.splitlines() if line)
    missing = tuple(path for path in relative if path not in matched)
    if missing:
        raise ReviewExchangeError(
            "review transient paths are not effectively ignored: " + ", ".join(missing),
        )


# eof
