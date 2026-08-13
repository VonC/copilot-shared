"""Contract tests for Step 3 instruction integration.

The checks pin only required trigger, delegation, and continuation tokens plus
their order, leaving prose free to improve without weakening the workflow.
"""

from pathlib import Path

_ROOT = Path(__file__).resolve().parents[4]


def _content(name: str) -> str:
    """Read one canonical instruction as normalized text."""
    return (_ROOT / "instructions" / name).read_text(encoding="utf-8")


def test_implement_step_samples_review_mode_after_grouping_and_delegates() -> None:
    """The normal stop is replaced only after successful grouping."""
    content = _content("implement-step.md")
    grouping = content.index("group-commits-msg")
    marker = content.index("a.review-mode", grouping)
    requestor = content.index("code-review-requestor", marker)
    workflow = content.index("pw skill", marker)
    assert grouping < marker < requestor
    assert marker < workflow
    assert "exact plan" in content[marker:]
    assert "implementation step" in content[marker:]
    assert "run the printed command verbatim" in content[marker:]
    assert "versioned review transcript" in content[marker:]


def test_grouping_instruction_has_a_dedicated_authorized_entry() -> None:
    """Durable authorization bypasses the choice display, not batch validation."""
    content = _content("group-commits-msg.md")
    start = content.index("Authorized code-review continuation")
    block = content[start:]
    ordered = [
        "owning-action-pending",
        "owning_action_authorized: true",
        "pw",
        "--root-a-commit",
        "complete",
    ]
    positions = [block.index(token) for token in ordered]
    assert positions == sorted(positions)
    assert "do not present" in block
    assert "authorization remains pending" in block

