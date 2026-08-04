"""Tests for composable installation of sensitive Git hooks.

Fix: the ``subprocess.run`` stand-in is fully typed (``object`` parameters
and a ``NoReturn`` return), so the strict pyright gate no longer flags
unknown parameter or argument types on the monkeypatched double.
Collision propagation injects Git path discovery because repository plumbing
is covered separately and is not part of that behavior.
The real hook-commit and CLI scenarios prepare their subprocess results in
fixtures so assertion timing is not coupled to Git process startup.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import NoReturn

import pytest

import tools.sensitive_history.install_hooks as hook_installer
from tools.sensitive_history.install_hooks import (
    DISPATCHER_MARKER,
    HookInstallError,
    _adopt_existing_hook,
    _configure_shared_rules,
    _dispatcher,
    _entry,
    _git_path,
    _shell_quote,
    _write_executable,
    install_hooks,
    main,
)


def _repo(path: Path) -> Path:
    path.mkdir()
    subprocess.run(  # noqa: S603
        ["git", "init", "-b", "main"],  # noqa: S607
        cwd=path,
        check=True,
        capture_output=True,
    )
    return path


def test_install_is_idempotent_and_preserves_an_existing_hook(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A dispatcher adopts existing work and gains one managed sensitive entry."""
    repo = tmp_path / "repo"
    repo.mkdir()
    hooks = repo / "hooks"
    hooks.mkdir()

    def fake_git_path(candidate: Path, name: str) -> Path:
        assert candidate == repo.resolve()
        assert name == "hooks"
        return hooks

    monkeypatch.setattr(hook_installer, "_git_path", fake_git_path)
    existing = hooks / "pre-commit"
    existing.write_text("#!/bin/sh\necho existing\n", encoding="utf-8")

    changes = install_hooks(repo, tmp_path / "llm-shared")

    assert "preserved existing pre-commit" in changes
    assert DISPATCHER_MARKER in existing.read_text(encoding="utf-8")
    assert (hooks / "pre-commit.d" / "50-existing").read_text(encoding="utf-8").endswith(
        "echo existing\n",
    )
    entry = (hooks / "pre-commit.d" / "90-sensitive").read_text(encoding="utf-8")
    assert "sensitive_pre_commit.py" in entry
    assert install_hooks(repo, tmp_path / "llm-shared") == ()


def test_shared_rules_config_is_absolute_and_idempotent(tmp_path: Path) -> None:
    """Hook repositories retain an explicit machine-local common rules path."""
    repo = _repo(tmp_path / "repo")
    shared = tmp_path / "common.rules"
    shared.write_text("literal:CommonTerm==>redacted\n", encoding="utf-8")

    assert _configure_shared_rules(repo, shared)
    configured = subprocess.run(  # noqa: S603
        ["git", "config", "--path", "--get", "sensitive.sharedRulesFile"],  # noqa: S607
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    ).stdout.strip()
    assert Path(configured).resolve() == shared.resolve()
    assert not _configure_shared_rules(repo, shared)
    with pytest.raises(HookInstallError, match="not found"):
        _configure_shared_rules(repo, tmp_path / "missing.rules")


def test_shared_rules_config_reports_git_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A Git config failure stops installation before hooks become misleading."""
    repo = _repo(tmp_path / "repo")
    shared = tmp_path / "common.rules"
    shared.write_text("literal:CommonTerm==>redacted\n", encoding="utf-8")

    def failed_git(*_args: object, **_kwargs: object) -> NoReturn:
        message = "git unavailable"
        raise OSError(message)

    monkeypatch.setattr(subprocess, "run", failed_git)
    with pytest.raises(HookInstallError, match="cannot configure"):
        _configure_shared_rules(repo, shared)


def test_dispatcher_and_entry_are_small_composable_shell_scripts(tmp_path: Path) -> None:
    """Generated files dispatch by hook name and quote installation paths."""
    quoted = _shell_quote(tmp_path / "it's shared")
    entry = _entry(tmp_path / "python.exe", tmp_path / "it's shared" / "hook.py")

    assert "pre-commit" not in _dispatcher()
    assert '"$hook" "$@" || exit $?' in _dispatcher()
    assert "'\"'\"'" in quoted
    assert "python.exe" in entry
    assert "hook.py" in entry


def test_write_executable_updates_only_changed_content(tmp_path: Path) -> None:
    """Repeated checks do not rewrite an already-correct hook."""
    path = tmp_path / "hook"
    assert _write_executable(path, "one\n")
    assert not _write_executable(path, "one\n")
    assert _write_executable(path, "two\n")
    assert path.read_text(encoding="utf-8") == "two\n"


def test_existing_hook_collision_fails_without_overwriting(tmp_path: Path) -> None:
    """An ambiguous preserved-hook target requires manual resolution."""
    hook = tmp_path / "pre-commit"
    chain = tmp_path / "pre-commit.d"
    chain.mkdir()
    hook.write_text("user hook", encoding="utf-8")
    (chain / "50-existing").write_text("older hook", encoding="utf-8")

    with pytest.raises(HookInstallError, match="already exists"):
        _adopt_existing_hook(hook, chain)
    hook.unlink()
    _adopt_existing_hook(hook, chain)


@pytest.fixture
def git_path_main_results(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> tuple[str, int, str, int, str, int, str]:
    """Run real CLI Git operations outside measured assertion time."""
    repo = _repo(tmp_path / "repo")
    shared = tmp_path / "shared"

    hooks_name = _git_path(repo, "hooks").name
    rules = tmp_path / "common.rules"
    rules.write_text("literal:CommonTerm==>redacted\n", encoding="utf-8")
    arguments = [
        str(repo),
        "--shared-root",
        str(shared),
        "--shared-rules",
        str(rules),
    ]
    first_status = main(arguments)
    first_output = capsys.readouterr().out
    second_status = main(arguments)
    second_output = capsys.readouterr().out
    absent_status = main([str(tmp_path / "absent")])
    absent_error = capsys.readouterr().err
    return (
        hooks_name,
        first_status,
        first_output,
        second_status,
        second_output,
        absent_status,
        absent_error,
    )


def test_git_path_and_main_report_success_and_failure(
    git_path_main_results: tuple[str, int, str, int, str, int, str],
) -> None:
    """The CLI reports installs, checks, and invalid repositories."""
    (
        hooks_name,
        first_status,
        first_output,
        second_status,
        second_output,
        absent_status,
        absent_error,
    ) = git_path_main_results

    assert hooks_name == "hooks"
    assert first_status == 0
    assert "installed" in first_output
    assert second_status == 0
    assert "already installed" in second_output
    assert absent_status == 1
    assert "ERROR" in absent_error


def test_install_reports_preserved_target_collision(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The public installer propagates safe-adoption failures."""
    repo = tmp_path / "repo"
    repo.mkdir()
    hooks = repo / "hooks"
    hooks.mkdir()

    def fake_git_path(candidate: Path, name: str) -> Path:
        assert candidate == repo.resolve()
        assert name == "hooks"
        return hooks

    monkeypatch.setattr(hook_installer, "_git_path", fake_git_path)
    (hooks / "pre-commit").write_text("new user hook", encoding="utf-8")
    chain = hooks / "pre-commit.d"
    chain.mkdir()
    (chain / "50-existing").write_text("old user hook", encoding="utf-8")

    with pytest.raises(HookInstallError, match="already exists"):
        install_hooks(repo, tmp_path / "shared")


@pytest.fixture
def installed_hook_results(
    tmp_path: Path,
) -> tuple[
    subprocess.CompletedProcess[str],
    subprocess.CompletedProcess[str],
    subprocess.CompletedProcess[str],
]:
    """Run the three real hook commits outside measured assertion time."""
    repo = _repo(tmp_path / "repo")
    subprocess.run(  # noqa: S603
        ["git", "config", "user.name", "Hook Tests"],  # noqa: S607
        cwd=repo,
        check=True,
    )
    subprocess.run(  # noqa: S603
        ["git", "config", "user.email", "hooks@example.invalid"],  # noqa: S607
        cwd=repo,
        check=True,
    )
    shared_rules = tmp_path / "a.sensitive.replacements.local.txt"
    shared_rules.write_text(
        "literal:BlockedHookTerm==>redacted\n",
        encoding="utf-8",
    )
    (repo / "a.sensitive.replacements.local.txt").write_text("", encoding="utf-8")
    install_hooks(repo, Path(__file__).parents[4], shared_rules)

    candidate = repo / "candidate.txt"
    candidate.write_text("contains BlockedHookTerm\n", encoding="utf-8")
    subprocess.run(  # noqa: S603
        ["git", "add", "candidate.txt"],  # noqa: S607
        cwd=repo,
        check=True,
    )
    blob_result = subprocess.run(  # noqa: S603
        ["git", "commit", "-m", "safe message"],  # noqa: S607
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    candidate.write_text("safe content\n", encoding="utf-8")
    subprocess.run(  # noqa: S603
        ["git", "add", "candidate.txt"],  # noqa: S607
        cwd=repo,
        check=True,
    )
    message_result = subprocess.run(  # noqa: S603
        ["git", "commit", "-m", "BlockedHookTerm message"],  # noqa: S607
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    clean_result = subprocess.run(  # noqa: S603
        ["git", "commit", "-m", "safe message"],  # noqa: S607
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return blob_result, message_result, clean_result


def test_installed_hooks_block_blob_and_message_then_allow_clean_commit(
    installed_hook_results: tuple[
        subprocess.CompletedProcess[str],
        subprocess.CompletedProcess[str],
        subprocess.CompletedProcess[str],
    ],
) -> None:
    """Real Git commits exercise both generated dispatchers and lean adapters."""
    blob_result, message_result, clean_result = installed_hook_results

    assert blob_result.returncode != 0
    assert "candidate.txt:1" in blob_result.stderr
    assert "BlockedHookTerm" not in blob_result.stderr
    assert message_result.returncode != 0
    assert "commit message line 1" in message_result.stderr
    assert "BlockedHookTerm" not in message_result.stderr
    assert clean_result.returncode == 0, clean_result.stderr
