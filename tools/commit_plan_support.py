"""Shared read-only repository support for commit-plan workflows.

Step 1 centralizes exact staged-path inventory so validation and future checking
use the same Git arguments, NUL decoding, ordering, and rename-side membership.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from tools.git_command import GitCommandOptions, run_cross_platform_git_command

if TYPE_CHECKING:
    from pathlib import Path

_STAGED_PATH_ARGUMENTS = (
    "diff",
    "--cached",
    "--name-only",
    "--no-renames",
    "-z",
)


def staged_paths(root: Path) -> tuple[str, ...]:
    """Return ordered staged paths, counting both sides of a rename."""
    result = run_cross_platform_git_command(
        _STAGED_PATH_ARGUMENTS,
        cwd=root,
        options=GitCommandOptions(capture_output=True, encoding="utf-8"),
    )
    return tuple(path for path in result.stdout.split("\0") if path)


__all__ = ["staged_paths"]


# eof
