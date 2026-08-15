"""TDD contracts for immutable code-review index evidence."""

from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

import pytest

from tools import code_review_evidence as evidence
from tools.review_exchange_models import ReviewExchangeError

if TYPE_CHECKING:
    from pathlib import Path

# ruff: noqa: S603, S607


def _git(root: Path, *arguments: str) -> str:
    """Run one bounded Git command in a temporary repository."""
    result = subprocess.run(
        ["git", *arguments],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
        timeout=10,
    )
    return result.stdout.strip()


@pytest.fixture(scope="module")
def staged_repository(
    tmp_path_factory: pytest.TempPathFactory,
) -> tuple[str, str, str, str]:
    """Build real staged Git evidence outside the measured test call."""
    root = tmp_path_factory.mktemp("code-review-evidence")
    _git(root, "init", "-q")
    tracked = root / "tracked.txt"
    tracked.write_text("staged\n", encoding="utf-8")
    _git(root, "add", "tracked.txt")
    captured = evidence.capture_index_tree(root)
    expected = _git(root, "write-tree")
    tracked.write_text("unstaged\n", encoding="utf-8")
    after_unstaged = evidence.capture_index_tree(root)
    _git(root, "add", "tracked.txt")
    after_staged = evidence.capture_index_tree(root)
    return captured, expected, after_unstaged, after_staged


def test_capture_index_tree_uses_the_index_without_inspecting_worktree(
    staged_repository: tuple[str, str, str, str],
) -> None:
    """Unstaged bytes do not change the captured Git tree object."""
    captured, expected, after_unstaged, after_staged = staged_repository
    assert captured == expected
    assert after_unstaged == captured
    assert after_staged != captured


def test_capture_index_tree_rejects_non_repository_and_malformed_git_output(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Repository and object-identity failures remain explicit."""
    with pytest.raises(ReviewExchangeError, match="repository is not a directory"):
        evidence.capture_index_tree(tmp_path / "missing")
    with pytest.raises(ReviewExchangeError, match="capture Git index tree"):
        evidence.capture_index_tree(tmp_path)

    completed = subprocess.CompletedProcess(["git", "write-tree"], 0, "not-a-tree\n", "")
    def fake_run(_arguments: object, **_kwargs: object) -> subprocess.CompletedProcess[str]:
        """Return malformed output through the typed Git seam."""
        return completed

    monkeypatch.setattr(evidence, "run_cross_platform_git_command", fake_run)
    with pytest.raises(ReviewExchangeError, match="malformed tree object"):
        evidence.capture_index_tree(tmp_path)
