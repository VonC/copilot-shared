"""Tests for the exact shared staged-path inventory boundary.

Step 1 proves that checking and committing can consume one ordered Git index
inventory without path filtering, filesystem probes, or rename interpretation.
"""

from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

from tools import commit_plan_support
from tools.git_command import GitCommandOptions

if TYPE_CHECKING:
    from pathlib import Path

    import pytest


def _return_stdout(
    monkeypatch: pytest.MonkeyPatch,
    stdout: str,
) -> None:
    """Replace the Git seam with one completed command carrying stdout."""

    def completed(
        arguments: tuple[str, ...],
        *,
        cwd: Path,
        options: GitCommandOptions,
    ) -> subprocess.CompletedProcess[str]:
        del cwd, options
        return subprocess.CompletedProcess(
            ["git", *arguments],
            0,
            stdout,
            "",
        )

    monkeypatch.setattr(
        commit_plan_support,
        "run_cross_platform_git_command",
        completed,
    )


def test_staged_paths_runs_the_exact_index_inventory_once(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The public boundary owns one exact cross-platform Git invocation."""
    calls: list[tuple[tuple[str, ...], Path, GitCommandOptions]] = []

    def completed(
        arguments: tuple[str, ...],
        *,
        cwd: Path,
        options: GitCommandOptions,
    ) -> subprocess.CompletedProcess[str]:
        calls.append((arguments, cwd, options))
        return subprocess.CompletedProcess(
            ["git", *arguments],
            0,
            "staged.txt\0",
            "",
        )

    monkeypatch.setattr(
        commit_plan_support,
        "run_cross_platform_git_command",
        completed,
    )

    assert commit_plan_support.staged_paths(tmp_path) == ("staged.txt",)
    assert calls == [
        (
            ("diff", "--cached", "--name-only", "--no-renames", "-z"),
            tmp_path,
            GitCommandOptions(capture_output=True, encoding="utf-8"),
        ),
    ]


def test_staged_paths_preserves_order_and_path_whitespace(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """NUL decoding keeps Git order and every non-delimiter character."""
    _return_stdout(
        monkeypatch,
        " leading.txt\0trailing.txt \0line\nbreak.txt\0",
    )

    assert commit_plan_support.staged_paths(tmp_path) == (
        " leading.txt",
        "trailing.txt ",
        "line\nbreak.txt",
    )


def test_staged_paths_keeps_a_deleted_path_in_membership(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Inventory decoding does not probe or discard a deleted worktree path."""
    _return_stdout(monkeypatch, "removed/file.txt\0")

    assert commit_plan_support.staged_paths(tmp_path) == ("removed/file.txt",)


def test_staged_paths_keeps_both_no_rename_sides(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The source and destination emitted by --no-renames remain separate."""
    _return_stdout(monkeypatch, "before.txt\0after.txt\0")

    assert commit_plan_support.staged_paths(tmp_path) == (
        "before.txt",
        "after.txt",
    )


def test_staged_paths_discards_only_empty_nul_segments(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """An empty index and repeated delimiters cannot create phantom paths."""
    _return_stdout(monkeypatch, "\0\0")

    assert commit_plan_support.staged_paths(tmp_path) == ()


# eof
