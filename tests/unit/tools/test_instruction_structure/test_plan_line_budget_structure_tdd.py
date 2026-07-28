"""Structural checks for implementation-plan line-budget policy."""

from __future__ import annotations

from tools import prompt_workflow_steps as steps


def test_plan_writing_treats_sub_ceiling_estimates_as_advisory() -> None:
    """Plan estimates below 650 never create mandatory split work."""
    root = steps.llm_shared_dir()
    instruction = (root / "instructions" / "write-plans.md").read_text(
        encoding="utf-8",
    )
    template = (root / "templates" / "write-plans.template.md").read_text(
        encoding="utf-8",
    )

    assert "below 550 lines: safe to extend" in instruction
    assert "from 550 through 650 lines: at risk" in instruction
    assert "above 650 lines: over the repository limit" in instruction
    assert "do not invent a tighter mandatory target" in instruction
    assert "without marking the step incomplete" in instruction
    assert "remaining at or below 650" in template
    assert "record the variance without failing the step" in template
