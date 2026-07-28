"""Structural checks for the packaged Codex plugin."""

from __future__ import annotations

import pytest

from tools import prompt_workflow_steps as steps

PluginSnapshot = tuple[
    set[str],
    set[str],
    tuple[tuple[str, str, bytes, bytes], ...],
]


@pytest.fixture(scope="session")
def codex_plugin_snapshot() -> PluginSnapshot:
    """Read the Codex package once, outside the measured test-call phase."""
    root = steps.llm_shared_dir()
    instructions = root / "instructions"
    plugin = root / ".agents" / "llm-shared"
    instruction_names = {path.name for path in instructions.glob("*.md")}
    expected_skill_names = {
        name.removesuffix(".md").replace("_", "-") for name in instruction_names
    }
    packaged_skill_names = {
        path.name for path in (plugin / "skills").iterdir() if path.is_dir()
    }
    rows = tuple(
        (
            name,
            (
                plugin
                / "skills"
                / name.removesuffix(".md").replace("_", "-")
                / "SKILL.md"
            ).read_text(encoding="utf-8"),
            (plugin / "instructions" / name).read_bytes(),
            (instructions / name).read_bytes(),
        )
        for name in instruction_names
    )
    return expected_skill_names, packaged_skill_names, rows


def test_codex_plugin_packages_every_instruction(
    codex_plugin_snapshot: PluginSnapshot,
) -> None:
    """Every shared instruction has a matching, self-contained Codex skill."""
    expected_skill_names, packaged_skill_names, rows = codex_plugin_snapshot
    assert packaged_skill_names == expected_skill_names
    for instruction_name, skill, packaged, source in rows:
        assert f"[Instruction](../../instructions/{instruction_name})" in skill
        assert packaged == source
