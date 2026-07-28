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


def test_llmup_alias_refreshes_the_personal_codex_plugin() -> None:
    """The console shortcut keeps the documented plugin update loop together."""
    root = steps.llm_shared_dir()
    doskeys = (root / "senv.doskey").read_text(encoding="utf-8")
    launcher = (root / "bin" / "update_llm_shared_plugin.bat").read_text(
        encoding="utf-8",
    )
    wiki = root / "wiki"
    pages = (
        wiki / "how-to" / "pick-up-skill-edits-without-restarting.md",
        wiki / "how-to" / "register-skills-as-a-codex-plugin.md",
        wiki / "reference" / "aliases-and-launchers.md",
    )
    layout = (wiki / "reference" / "repository-layout.md").read_text(
        encoding="utf-8",
    )

    assert 'llmup="%LLM_SHARED_DIR%\\bin\\update_llm_shared_plugin.bat"' in doskeys
    assert "--isolated --no-project --with PyYAML" in launcher
    assert "validate_plugin.py" in launcher
    assert "update_plugin_cachebuster.py" in launcher
    assert "plugin add llm-shared@personal" in launcher
    assert 'findstr /I /C:"llm-shared@personal"' in launcher
    assert all("llmup" in path.read_text(encoding="utf-8") for path in pages)
    assert "update_llm_shared_plugin" in layout
