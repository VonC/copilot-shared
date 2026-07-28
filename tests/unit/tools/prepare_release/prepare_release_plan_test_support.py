"""Real-repository fixtures for prepare-release planner tests."""

from __future__ import annotations

import os
import subprocess
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

_TEST_GIT_CONFIG = {
    "GIT_CONFIG_COUNT": "2",
    "GIT_CONFIG_KEY_0": "user.name",
    "GIT_CONFIG_VALUE_0": "Release Planner Tests",
    "GIT_CONFIG_KEY_1": "user.email",
    "GIT_CONFIG_VALUE_1": "release-planner@example.invalid",
}


def git(repo: Path, *args: str) -> str:
    """Run Git in a temporary test repository and return stripped stdout."""
    env = os.environ.copy()
    env.update(_TEST_GIT_CONFIG)
    result = subprocess.run(  # noqa: S603
        ["git", *args],  # noqa: S607
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
    )
    return result.stdout.strip()


def initialize_repository(repo: Path) -> str:
    """Initialize a main branch with one tagged base commit."""
    repo.mkdir()
    git(repo, "init", "-b", "main")
    (repo / "shared.txt").write_text("base\n", encoding="utf-8")
    git(repo, "add", "shared.txt")
    git(repo, "commit", "-m", "feat: base")
    git(repo, "tag", "v1.0.0")
    return git(repo, "rev-parse", "HEAD")


def commit_file(repo: Path, path: str, content: str, message: str) -> str:
    """Write and commit one file, returning the new commit OID."""
    (repo / path).write_text(content, encoding="utf-8")
    git(repo, "add", path)
    git(repo, "commit", "-m", message)
    return git(repo, "rev-parse", "HEAD")


# eof
