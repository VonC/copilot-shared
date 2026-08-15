"""Capture immutable Git evidence shared by code-review actors."""

# ruff: noqa: EM101, EM102, TRY003

from __future__ import annotations

import re
import subprocess
from pathlib import Path

from tools.git_command import GitCommandOptions, run_cross_platform_git_command
from tools.review_exchange_models import ReviewExchangeError

_TREE_OBJECT_RE = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")


def capture_index_tree(repository: str | Path) -> str:
    """Return the Git tree object for the repository index, never its worktree."""
    root = Path(repository).expanduser().resolve()
    if not root.is_dir():
        raise ReviewExchangeError("cannot capture Git index tree: repository is not a directory")
    try:
        result = run_cross_platform_git_command(
            ("write-tree",),
            cwd=root,
            options=GitCommandOptions(capture_output=True, encoding="utf-8"),
        )
    except (OSError, subprocess.CalledProcessError) as error:
        raise ReviewExchangeError(f"cannot capture Git index tree: {error}") from error
    tree_object = result.stdout.strip()
    if _TREE_OBJECT_RE.fullmatch(tree_object) is None:
        raise ReviewExchangeError("Git returned a malformed tree object for the index")
    return tree_object


# eof
