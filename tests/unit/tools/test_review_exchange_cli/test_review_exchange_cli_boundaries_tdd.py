"""Boundary coverage for the Step 4 review-exchange command adapter.

These tests cover construction, parser limits, Git ignore probing, unreadable
caller inputs, disabled status, defensive dispatch, and the script entry point.
The lifecycle behavior remains covered by the core and the primary CLI tests.
"""

from __future__ import annotations

import argparse
import io
import json
import runpy
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from tests.unit.tools.test_review_exchange_cli.test_review_exchange_cli_tdd import (
    _common,
    _runtime,
)
from tools import review_exchange_cli as cli
from tools.review_exchange_core import ReviewExchangeCore
from tools.review_exchange_models import ReviewExchangeError

_EXIT_FATAL = 2
_EXIT_STOP = 3
_POSITIVE_FLOAT = 0.5
_POSITIVE_INT = 2
_WAIT_TIMEOUT = 15


def test_positive_number_parsers_reject_zero() -> None:
    """Wait durations and intervals must be positive before dispatch."""
    assert cli._positive_int("2") == _POSITIVE_INT
    assert cli._positive_float("0.5") == _POSITIVE_FLOAT
    with pytest.raises(argparse.ArgumentTypeError, match="positive"):
        cli._positive_int("0")
    with pytest.raises(argparse.ArgumentTypeError, match="positive"):
        cli._positive_float("-1")


def test_code_context_rejects_a_non_plan_document(tmp_path: Path) -> None:
    """The code family cannot reinterpret a specification file as a plan."""
    document = tmp_path / "design.v0.11.0.topic.md"
    document.write_text("# design\n", encoding="utf-8")
    with pytest.raises(ReviewExchangeError, match="exact plan"):
        cli._context_from_document("code", document, None, "4")


def test_build_runtime_constructs_the_real_core(tmp_path: Path) -> None:
    """Exact parsed context builds one configured production facade."""
    injected, _ = _runtime(tmp_path)
    (tmp_path / "a.review-mode").write_text(
        "wait_timeout_seconds=15\n",
        encoding="utf-8",
    )
    args = cli._parser().parse_args(["status", *_common(injected)])

    runtime = cli._build_runtime(args, tmp_path)

    assert runtime.project_root == tmp_path
    assert runtime.configuration.wait_timeout_seconds == _WAIT_TIMEOUT
    assert isinstance(runtime.core, ReviewExchangeCore)


def test_effective_ignore_probe_uses_fixed_git_arguments(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The probe handles found, visible, missing-Git, and process errors."""
    path = tmp_path / "a.input.md"
    path.write_text("input", encoding="utf-8")
    commands: list[list[str]] = []

    def git_path(_name: str) -> str:
        return "C:/Git/bin/git.exe"

    def run_git(command: list[str], **_kwargs: Any) -> subprocess.CompletedProcess[str]:
        commands.append(command)
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(cli.shutil, "which", git_path)
    monkeypatch.setattr(cli.subprocess, "run", run_git)
    assert cli._is_effectively_ignored(tmp_path, path) is True
    assert commands[0][-2:] == ["--", "a.input.md"]

    def visible_git(
        command: list[str],
        **_kwargs: Any,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(command, 1, "", "")

    monkeypatch.setattr(cli.subprocess, "run", visible_git)
    assert cli._is_effectively_ignored(tmp_path, path) is False
    def no_git(_name: str) -> None:
        return None

    monkeypatch.setattr(cli.shutil, "which", no_git)
    with pytest.raises(ReviewExchangeError, match="git was not found"):
        cli._is_effectively_ignored(tmp_path, path)

    def broken_git(_command: list[str], **_kwargs: Any) -> subprocess.CompletedProcess[str]:
        raise OSError

    monkeypatch.setattr(cli.shutil, "which", git_path)
    monkeypatch.setattr(cli.subprocess, "run", broken_git)
    with pytest.raises(ReviewExchangeError, match="cannot validate ignored input"):
        cli._is_effectively_ignored(tmp_path, path)


def test_input_reader_reports_missing_and_invalid_utf8(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Caller input failures become typed diagnostics before core delegation."""
    def ignored(_root: Path, _path: Path) -> bool:
        return True

    monkeypatch.setattr(cli, "_is_effectively_ignored", ignored)
    with pytest.raises(ReviewExchangeError, match="does not exist"):
        cli._read_input_file(tmp_path, tmp_path / "a.missing.md", "summary")
    invalid = tmp_path / "a.invalid.md"
    invalid.write_bytes(b"\xff")
    with pytest.raises(ReviewExchangeError, match="UTF-8"):
        cli._read_input_file(tmp_path, invalid, "summary")


def test_dispatch_covers_disabled_status_and_unknown_operation(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Disabled status is expected while an unknown internal operation fails."""
    disabled, _ = _runtime(tmp_path, enabled=False)
    result = cli._dispatch(argparse.Namespace(operation="status"), disabled, io.StringIO())
    assert result.outcome == "disabled"
    assert result.exit_code == _EXIT_STOP

    active, _ = _runtime(tmp_path / "active")

    def valid_activation(_root: Path, _paths: object) -> None:
        return None

    monkeypatch.setattr(cli, "validate_activation", valid_activation)
    with pytest.raises(ReviewExchangeError, match="unsupported operation"):
        cli._dispatch(argparse.Namespace(operation="unknown"), active, io.StringIO())


def test_script_entry_point_returns_fatal_json(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Direct script execution exits through main and retains its JSON result."""
    monkeypatch.setattr(sys, "argv", ["review_exchange_cli.py", "status"])
    with pytest.raises(SystemExit) as raised:
        runpy.run_path(str(Path(cli.__file__)), run_name="__main__")
    assert raised.value.code == _EXIT_FATAL
    assert json.loads(capsys.readouterr().out)["outcome"] == "fatal-input"


# eof
