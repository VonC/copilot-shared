"""Acceptance contracts for the checked repository and shared gate wiring."""

# ruff: noqa: S603

from __future__ import annotations

import json
import subprocess

import pytest

from tools import prompt_workflow_steps as steps


@pytest.fixture
def repository_launcher_result() -> subprocess.CompletedProcess[str]:
    """Run the real public launcher outside the measured assertion call."""
    root = steps.llm_shared_dir()
    return subprocess.run(
        [str(root / "markdown-check.bat")],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )


def test_shared_gate_records_one_markdown_launcher_failure_path() -> None:
    """check.bat owns one launcher call and one named aggregate failure."""
    source = (steps.llm_shared_dir() / "check.bat").read_text(encoding="utf-8")

    assert source.count('call "%PRJ_DIR%\\markdown-check.bat"') == 1
    assert source.count("call :record_failure markdown %markdown_status%") == 1
    assert 'set "markdown_status=%ERRORLEVEL%"' in source
    assert 'set "markdown_status="' in source


def test_checked_repository_passes_public_launcher(
    repository_launcher_result: subprocess.CompletedProcess[str],
) -> None:
    """The authoritative baseline and repaired repository produce a clean run."""
    assert repository_launcher_result.returncode == 0
    assert repository_launcher_result.stdout == ""
    assert repository_launcher_result.stderr == ""


def test_zero_debt_markdown_rules_have_no_baseline_entries() -> None:
    """Only confirmed MD033 debt may appear among Markdown rule allowances."""
    root = steps.llm_shared_dir()
    payload = json.loads(
        (root / ".markdownlint-baseline.json").read_text(encoding="utf-8"),
    )
    markdown_rules = {
        allowance["rule"]
        for allowance in payload["allowances"]
        if str(allowance["rule"]).startswith("MD")
    }

    assert markdown_rules == {"MD033"}


# eof
