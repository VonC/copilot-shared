"""Tests for split git batch commit workflow processing branches.

Fix: Cover commit-block and multi-block workflow control flow from the split
`tools.git_batch_commit_workflow` module without keeping a large combined test
file.

Fix: Cover the non-interactive path. A Git failure in non-interactive mode must
stop the batch and return False without calling `input()`, and the add and
commit phases must receive the `interactive` flag.
"""

from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

import pytest

from tools import git_batch_commit_models as git_batch_models
from tools import git_batch_commit_workflow as git_batch_workflow

# pyright: reportPrivateUsage=false
# ruff: noqa: S603, S607, SLF001

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path


def _valid_block(path: str = "src/example.py") -> git_batch_models.CommitBlock:
    commit_message = "fix(scope): title\n\nWhy:\n\nreason before\n\nreason after\n\nWhat:\n\n- change"
    return git_batch_models.CommitBlock(
        git_adds=[f"git add -A {path}"],
        commit_message=commit_message,
        commit_title="fix(scope): title",
    )


def _noop_git_reset(_root: Path) -> None:
    return None


def _return_false_process_commit_block(
    _block_arg: git_batch_models.CommitBlock,
    _index: int,
    _total: int,
    _root: Path,
    *,
    interactive: object = True,
    trace_git_commit: object = None,
) -> bool:
    del interactive, trace_git_commit
    return False


def _return_true_process_commit_block(
    _block_arg: git_batch_models.CommitBlock,
    _index: int,
    _total: int,
    _root: Path,
    *,
    interactive: object = True,
    trace_git_commit: object = None,
) -> bool:
    del interactive, trace_git_commit
    return True


def _raise_git_operation_error_process_commit_block(
    _block_arg: git_batch_models.CommitBlock,
    _index: int,
    _total: int,
    _root: Path,
    *,
    interactive: object = True,
    trace_git_commit: object = None,
) -> bool:
    del interactive, trace_git_commit
    msg = "git failed mid-batch"
    raise git_batch_models.GitOperationError(msg)


def _return_git_add_outcome(
    outcome: git_batch_models._GitAddOutcome,
) -> Callable[..., git_batch_models._GitAddOutcome]:
    def fake_git_add_files(
        _git_adds: list[str],
        _root: Path,
        *,
        interactive: bool = True,
    ) -> git_batch_models._GitAddOutcome:
        del interactive
        return outcome

    return fake_git_add_files


def _fail_input(_prompt: str) -> str:
    msg = "input() must not be called in non-interactive mode"
    raise AssertionError(msg)


def _raise_unexpected_diff_check(_git_adds: list[str], _root: Path) -> bool:
    msg = "unexpected diff check"
    raise AssertionError(msg)


def _return_true_staged_changes(_git_adds: list[str], _root: Path) -> bool:
    return True


def _one_staged_path(_root: Path) -> tuple[str, ...]:
    return ("src/example.py",)


def test_process_commit_block_skips_when_add_phase_requests_skip(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """A skip result from the add phase should skip the commit without diff checks."""
    block = _valid_block()
    monkeypatch.setattr(
        git_batch_workflow,
        "git_add_files",
        _return_git_add_outcome(
            git_batch_models._GitAddOutcome(
                should_continue=True,
                should_skip_commit=True,
            ),
        ),
    )
    monkeypatch.setattr(
        git_batch_workflow,
        "_block_has_staged_changes",
        _raise_unexpected_diff_check,
    )
    caplog.set_level("WARNING")

    assert git_batch_workflow._process_commit_block(block, 1, 1, tmp_path) is True
    assert "Skipping commit 1." in caplog.text


def test_process_commit_block_commits_when_staged_changes_exist(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A commit block with staged changes should call `git_commit` and continue."""
    block = _valid_block()
    captured: dict[str, object] = {}

    monkeypatch.setattr(
        git_batch_workflow,
        "git_add_files",
        _return_git_add_outcome(
            git_batch_models._GitAddOutcome(
                should_continue=True,
                should_skip_commit=False,
            ),
        ),
    )
    monkeypatch.setattr(
        git_batch_workflow,
        "_block_has_staged_changes",
        _return_true_staged_changes,
    )

    def fake_git_commit(
        commit_message: str,
        commit_title: str,
        root: Path,
        *,
        interactive: bool = True,
        trace_git_commit: bool = False,
    ) -> None:
        captured["commit_message"] = commit_message
        captured["commit_title"] = commit_title
        captured["root"] = root
        captured["interactive"] = interactive
        captured["trace_git_commit"] = trace_git_commit

    monkeypatch.setattr(git_batch_workflow, "git_commit", fake_git_commit)

    assert git_batch_workflow._process_commit_block(
        block,
        1,
        1,
        tmp_path,
        interactive=False,
        trace_git_commit=True,
    ) is True
    assert captured == {
        "commit_message": block.commit_message,
        "commit_title": block.commit_title,
        "root": tmp_path,
        "interactive": False,
        "trace_git_commit": True,
    }


def test_process_all_commits_stops_when_commit_block_requests_stop(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Commit processing should return False when a block asks the batch to stop."""
    block = _valid_block()
    monkeypatch.setattr(git_batch_workflow, "git_reset", _noop_git_reset)
    monkeypatch.setattr(
        git_batch_workflow,
        "_process_commit_block",
        _return_false_process_commit_block,
    )

    assert git_batch_workflow._process_all_commits([block], tmp_path) is False


def test_process_all_commits_logs_success_when_all_blocks_complete(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Successful commit processing should log the final success banner."""
    block = _valid_block()
    monkeypatch.setattr(git_batch_workflow, "git_reset", _noop_git_reset)
    monkeypatch.setattr(
        git_batch_workflow,
        "_process_commit_block",
        _return_true_process_commit_block,
    )
    caplog.set_level("INFO")

    assert git_batch_workflow._process_all_commits([block], tmp_path) is True
    assert "All commits processed successfully" in caplog.text


def test_batch_validation_uses_the_public_commit_plan_validator(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The commit path delegates staged membership and subjects to one API."""
    block = _valid_block()
    captured: dict[str, object] = {}

    monkeypatch.setattr(
        git_batch_workflow,
        "_staged_paths",
        _one_staged_path,
    )

    def fake_validate(
        blocks: list[git_batch_models.CommitBlock],
        staged_paths: tuple[str, ...],
    ) -> git_batch_models.CommitPlanValidation:
        captured["blocks"] = blocks
        captured["staged_paths"] = staged_paths
        return git_batch_models.CommitPlanValidation(groups=(), diagnostics=())

    monkeypatch.setattr(git_batch_workflow, "validate_commit_plan", fake_validate)
    git_batch_workflow._validate_commit_plan_for_root([block], tmp_path)
    assert captured == {
        "blocks": [block],
        "staged_paths": ("src/example.py",),
    }


def test_staged_paths_reads_exact_index_membership(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The batch boundary passes exact staged paths to the pure validator."""
    captured: dict[str, object] = {}

    def staged_result(
        arguments: tuple[str, ...],
        *,
        cwd: Path,
        options: object,
    ) -> subprocess.CompletedProcess[str]:
        captured.update(arguments=arguments, cwd=cwd, options=options)
        return subprocess.CompletedProcess(["git", *arguments], 0, "staged.txt\0", "")

    monkeypatch.setattr(
        git_batch_workflow,
        "run_cross_platform_git_command",
        staged_result,
    )
    assert git_batch_workflow._staged_paths(tmp_path) == ("staged.txt",)
    assert captured["arguments"] == (
        "diff",
        "--cached",
        "--name-only",
        "--no-renames",
        "-z",
    )
    assert captured["cwd"] == tmp_path


def test_batch_validation_reports_public_validator_diagnostics(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Typed diagnostics stop the batch before its commit phase."""
    block = _valid_block()
    monkeypatch.setattr(git_batch_workflow, "_staged_paths", _one_staged_path)
    invalid = git_batch_models.CommitPlanValidation(
        groups=(),
        diagnostics=("planned path is not staged: other.py",),
    )

    def return_invalid(
        _blocks: list[git_batch_models.CommitBlock],
        _paths: tuple[str, ...],
    ) -> git_batch_models.CommitPlanValidation:
        return invalid

    monkeypatch.setattr(
        git_batch_workflow,
        "validate_commit_plan",
        return_invalid,
    )
    with pytest.raises(git_batch_models.GitBatchCommitError, match=r"other\.py"):
        git_batch_workflow._validate_commit_plan_for_root([block], tmp_path)


def test_process_all_commits_stops_on_git_error_without_prompting_when_non_interactive(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """A Git failure in non-interactive mode should stop without calling input()."""
    block = _valid_block()
    monkeypatch.setattr(git_batch_workflow, "git_reset", _noop_git_reset)
    monkeypatch.setattr(
        git_batch_workflow,
        "_process_commit_block",
        _raise_git_operation_error_process_commit_block,
    )
    # Any input() call would hang an agent run, so make it fail the test instead.
    monkeypatch.setattr("builtins.input", _fail_input)
    caplog.set_level("INFO")

    assert (
        git_batch_workflow._process_all_commits(
            [block],
            tmp_path,
            interactive=False,
        )
        is False
    )
    assert "Stopping after Git operation failure (non-interactive)." in caplog.text


# eof
