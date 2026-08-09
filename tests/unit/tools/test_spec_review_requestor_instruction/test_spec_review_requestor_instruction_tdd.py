"""Contract tests for the specification review requestor instruction.

Step 2 adds a specification-owned orchestration layer without copying the
role-neutral exchange state machine. These tests pin its fixed policy, shared
command delegation, round behavior, human gate, and replay-safe consolidation
handoff as observable Markdown contracts.
"""

from __future__ import annotations

from tools import prompt_workflow_steps as steps

_ROOT = steps.llm_shared_dir()
_INSTRUCTION = _ROOT / "instructions" / "spec-review-requestor.md"


def _content() -> str:
    """Read the canonical specialized instruction."""
    return _INSTRUCTION.read_text(encoding="utf-8")


def _assert_in_order(content: str, tokens: tuple[str, ...]) -> None:
    """Assert that each contract token follows the previous token."""
    cursor = -1
    for token in tokens:
        position = content.find(token, cursor + 1)
        assert position > cursor, token
        cursor = position


def test_instruction_registers_the_exact_specification_policy() -> None:
    """Every command uses the fixed family signal and human labels."""
    content = _content()

    for token in (
        "--family specification",
        "--convergence-signal consolidation-ready",
        '--another-round-label "Revise and review again"',
        '--continue-owning-workflow-label "Consolidate"',
    ):
        assert token in content
    assert "Pass this unchanged policy to every shared exchange operation" in content


def test_instruction_delegates_the_shared_requestor_sequence() -> None:
    """The specialized role joins renderer content to shared coordination."""
    content = _content()

    assert "instructions/review-requestor.md" in content
    assert "bin/review_exchange.bat" in content
    assert "bin/spec_review_request.bat" in content
    _assert_in_order(
        content,
        (
            "`status`",
            "`activate`",
            "`start`",
            "`publish-request`",
            "`wait-answer`",
            "`consume-answer`",
            "`continue`",
            "`confirm`",
        ),
    )
    assert "`reclaim`" in content
    assert "`complete`" in content


def test_instruction_handles_resumption_without_manual_artifact_edits() -> None:
    """Every durable state has a specialized action or a fail-closed stop."""
    content = _content()

    for state in (
        "disabled",
        "idle",
        "round-in-progress",
        "request-pending",
        "answer-pending",
        "abandoned-request",
        "abandoned-answer",
        "abandoned-mid-round",
        "convergence-gate",
        "owning-action-pending",
        "escalated",
    ):
        assert f"`{state}`" in content
    assert "Never create, overwrite, rename, or delete a protocol artifact by hand" in content
    assert "read only the exact `paths.answer` file" in content
    assert "Never read the versioned transcript as working context" in content


def test_instruction_owns_edits_rounds_and_human_choices() -> None:
    """Wording edits precede the gate and substantive edits repeat automatically."""
    content = _content()

    assert "Apply covered wording edits before presenting the human gate" in content
    assert "reviewed-work-changed" in content
    assert "disagreement" in content
    assert "Human guidance:" in content
    assert "Revise and review again" in content
    assert "Consolidate" in content
    assert "Do not call `consume-answer` for a convergence recommendation" in content
    assert "The reviewer recommendation never authorizes consolidation" in content


def test_instruction_completes_only_after_canonical_consolidation() -> None:
    """Durable authorization survives the consolidation handoff and session exit."""
    content = _content()

    _assert_in_order(
        content,
        (
            "owning_action_authorized",
            "consolidate-then-review-ask-questions",
            "settled decision marker",
            "`complete`",
            "rerun `pw skill`",
        ),
    )
    assert "`owning-action-pending`" in content
    assert "do not ask the human again" in content


# eof
