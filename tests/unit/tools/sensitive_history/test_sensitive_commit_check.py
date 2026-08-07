"""Tests for fast checks of only the commit currently being prepared.

Fix: the monkeypatched Git doubles are fully typed (``object`` parameters,
explicit returns, and named functions instead of untyped lambdas), so the
strict pyright gate no longer flags unknown parameter or argument types.
The empty-rules case injects repository/config discovery so it tests parsing
and hook outcomes without paying for an unrelated Git repository fixture.
The unborn-branch case supplies exact Git protocol records through typed
doubles, preserving empty-tree coverage without repeated Windows process
startup in the timed test call.
"""

from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING, NoReturn

import pytest

import tools.sensitive_history.sensitive_commit_check as check
from tools.sensitive_history import history_scan
from tools.sensitive_history.history_scan import (
    HistoryScanError,
    patterns_from_replacement_file,
)
from tools.sensitive_history.sensitive_commit_check import (
    BLOCKED,
    ERROR,
    _git,
    check_message,
    check_staged_blobs,
    main,
    repository_root,
    staged_blob_paths,
)

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

TERM = "ForbiddenValue"
_EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
_FIRST_OID = "1111111111111111111111111111111111111111"


class _UnbornRepository:
    """Return one staged blob without launching a real cat-file process."""

    def __init__(self, _root: Path) -> None:
        """Accept the repository root used by the production boundary."""

    def iter_blobs(self, blob_ids: tuple[str, ...]) -> Iterator[tuple[str, bytes]]:
        """Yield the exact staged object content requested by the scanner."""
        for oid in blob_ids:
            yield oid, f"{TERM}\n".encode()


def _run_git(repo: Path, *args: str) -> str:
    result = subprocess.run(  # noqa: S603
        ["git", *args],  # noqa: S607
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout.strip()


def _write_rules(repo: Path) -> None:
    (repo / "a.sensitive.replacements.local.txt").write_text(
        f"literal:{TERM}==>redacted\n",
        encoding="utf-8",
    )


@pytest.fixture
def pending_repo(tmp_path: Path) -> Path:
    """Create a repository whose history already contains a protected term."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _run_git(repo, "init", "-b", "main")
    _run_git(repo, "config", "user.name", "Pending Commit Tests")
    _run_git(repo, "config", "user.email", "pending@example.invalid")
    (repo / ".gitignore").write_text("a.*\n", encoding="utf-8")
    _write_rules(repo)
    (repo / "legacy.txt").write_text(f"old {TERM}\n", encoding="utf-8")
    (repo / "safe.txt").write_text("safe\n", encoding="utf-8")
    _run_git(repo, "add", ".gitignore", "legacy.txt", "safe.txt")
    _run_git(repo, "commit", "-m", "initial history")
    return repo


def _patterns(repo: Path):  # noqa: ANN202
    return patterns_from_replacement_file(repo / "a.sensitive.replacements.local.txt")


def test_staged_check_ignores_history_unstaged_content_and_pure_renames(
    pending_repo: Path,
) -> None:
    """Only new blob object IDs in the index are candidates."""
    (pending_repo / "safe.txt").write_text(f"unstaged {TERM}\n", encoding="utf-8")
    _run_git(pending_repo, "mv", "legacy.txt", "renamed.txt")

    assert staged_blob_paths(pending_repo) == {}
    assert check_staged_blobs(pending_repo, _patterns(pending_repo)) == []


def test_staged_check_reports_text_binary_and_renamed_blob_updates(
    pending_repo: Path,
) -> None:
    """Changed staged text and binary blobs are read from the index in one batch."""
    (pending_repo / "text.txt").write_text(
        f"safe first line\ncontains {TERM}\n",
        encoding="utf-8",
    )
    (pending_repo / "binary.dat").write_bytes(f"prefix\0{TERM}\n".encode())
    _run_git(pending_repo, "mv", "legacy.txt", "renamed.txt")
    (pending_repo / "renamed.txt").write_text(f"updated {TERM}\n", encoding="utf-8")
    _run_git(pending_repo, "add", "text.txt", "binary.dat", "renamed.txt")

    paths = staged_blob_paths(pending_repo)
    assert sorted(path for values in paths.values() for path in values) == [
        "binary.dat",
        "renamed.txt",
        "text.txt",
    ]
    assert {finding.location for finding in check_staged_blobs(pending_repo, _patterns(pending_repo))} == {
        "binary.dat:1",
        "renamed.txt:1",
        "text.txt:2",
    }


def test_staged_check_handles_initial_commit_and_no_pending_changes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An unborn branch compares against Git's empty tree without real processes."""
    repo = tmp_path / "new"
    repo.mkdir()
    _write_rules(repo)
    diff_calls = 0
    calls: list[tuple[str, ...]] = []

    def unborn_git(
        _root: Path,
        *args: str,
        input_bytes: bytes | None = None,
    ) -> bytes:
        """Model an unborn HEAD, one staged addition, then an empty index."""
        nonlocal diff_calls
        calls.append(args)
        if args == ("rev-parse", "--verify", "HEAD"):
            message = "unborn HEAD"
            raise HistoryScanError(message)
        if args == ("hash-object", "-t", "tree", "--stdin"):
            assert input_bytes == b""
            return _EMPTY_TREE.encode()
        diff_calls += 1
        if diff_calls == 1:
            metadata = f":000000 100644 {'0' * 40} {_FIRST_OID} A"
            return metadata.encode() + b"\0first.txt\0"
        return b""

    monkeypatch.setattr(check, "_git", unborn_git)
    monkeypatch.setattr(check, "GitRepository", _UnbornRepository)

    assert check_staged_blobs(repo, _patterns(repo))[0].location == "first.txt:1"
    assert staged_blob_paths(repo) == {}
    assert ("hash-object", "-t", "tree", "--stdin") in calls
    assert all(_EMPTY_TREE in args for args in calls if args and args[0] == "diff")


def test_message_check_is_redacted_and_main_returns_hook_statuses(
    pending_repo: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The companion checks the supplied message without echoing its content."""
    message = pending_repo / ".git" / "COMMIT_EDITMSG"
    message.write_text(f"safe subject\nbody {TERM}\n", encoding="utf-8")

    findings = check_message(message, _patterns(pending_repo))
    assert findings[0].location == "commit message line 2"
    assert main(["--root", str(pending_repo), "message", str(message)]) == BLOCKED
    error = capsys.readouterr().err
    assert "commit message line 2" in error
    assert TERM not in error

    message.write_text("safe subject\n", encoding="utf-8")
    assert main(["--root", str(pending_repo), "message", str(message)]) == 0
    assert main(["--root", str(pending_repo), "staged"]) == 0


def test_empty_rule_files_warn_and_do_not_block_commits(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """An intentionally empty bootstrap configuration leaves commits usable."""
    repo = tmp_path / "repo"
    repo.mkdir()
    shared = tmp_path / "shared.rules"
    shared.write_text("", encoding="utf-8")
    (repo / "a.sensitive.replacements.local.txt").write_text(
        "",
        encoding="utf-8",
    )
    configured = [shared]

    def resolve_root(root: Path) -> Path:
        return root.resolve()

    def configured_file(root: Path) -> Path:
        assert root == repo.resolve()
        return configured[0]

    monkeypatch.setattr(check, "repository_root", resolve_root)
    monkeypatch.setattr(
        history_scan,
        "configured_shared_replacement_file",
        configured_file,
    )

    assert main(["--root", str(repo), "staged"]) == 0
    warning = capsys.readouterr().err
    assert "sensitive commit check skipped" in warning
    assert "no sensitive replacement rules configured" in warning

    missing = tmp_path / "missing.rules"
    configured[0] = missing
    assert main(["--root", str(repo), "staged"]) == ERROR
    assert "cannot read replacement file" in capsys.readouterr().err


def test_configuration_and_git_errors_fail_closed(
    pending_repo: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Missing inputs and malformed Git output never silently allow a commit."""
    missing = tmp_path / "missing-message"
    with pytest.raises(HistoryScanError, match="cannot read commit message"):
        check_message(missing, _patterns(pending_repo))

    def failed_git(*_args: object, **_kwargs: object) -> NoReturn:
        raise subprocess.CalledProcessError(
            1,
            ["git", "status"],
            stderr=b"simulated failure",
        )

    def missing_git(*_args: object, **_kwargs: object) -> NoReturn:
        raise FileNotFoundError

    monkeypatch.setattr(subprocess, "run", failed_git)
    with pytest.raises(HistoryScanError, match="failed: simulated failure"):
        _git(pending_repo, "status")

    monkeypatch.setattr(subprocess, "run", missing_git)
    with pytest.raises(HistoryScanError, match="git status failed"):
        _git(pending_repo, "status")

    assert main(["--root", str(tmp_path), "staged"]) == ERROR
    assert "could not run" in capsys.readouterr().err


def test_unexpected_raw_record_is_rejected(
    pending_repo: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A changed Git raw-diff contract blocks rather than missing content."""
    def fake_base_tree(_root: Path) -> str:
        return "base"

    def fake_git(*_args: object, **_kwargs: object) -> bytes:
        return b":bad\0path\0"

    monkeypatch.setattr(check, "_base_tree", fake_base_tree)
    monkeypatch.setattr(check, "_git", fake_git)
    with pytest.raises(HistoryScanError, match="unexpected git diff"):
        staged_blob_paths(pending_repo)


def test_repository_root_resolves_from_a_subdirectory(pending_repo: Path) -> None:
    """Hooks behave the same even when invoked below the worktree root."""
    child = pending_repo / "child"
    child.mkdir()
    assert repository_root(child) == pending_repo.resolve()
