"""Contract tests for the specification reviewer instruction.

Step 3 adds one canonical reviewer orchestration layer over the shared exchange
and paired answer renderer. These tests pin its exact policy, reviewer-owned
operations, retained-context recovery, and authority stops as observable
Markdown contracts.
"""

from __future__ import annotations

from tools import prompt_workflow_steps as steps

_ROOT = steps.llm_shared_dir()
_INSTRUCTION = _ROOT / "instructions" / "spec-reviewer.md"


def _content() -> str:
    """Read the canonical specification reviewer instruction."""
    return _INSTRUCTION.read_text(encoding="utf-8")


def _assert_in_order(content: str, tokens: tuple[str, ...]) -> None:
    """Assert that each contract token follows the previous token."""
    cursor = -1
    for token in tokens:
        position = content.find(token, cursor + 1)
        assert position > cursor, token
        cursor = position


def test_instruction_registers_exact_policy_and_context() -> None:
    """Every reviewer operation uses one exact specification identity."""
    content = _content()

    for token in (
        "--family specification",
        "--convergence-signal consolidation-ready",
        '--another-round-label "Revise and review again"',
        '--continue-owning-workflow-label "Consolidate"',
        "--document <exact-reviewed-specification>",
        "--umbrella <exact-umbrella-draft>",
    ):
        assert token in content
    assert "instructions/review-requestor.md" in content
    assert "Do not search documentation folders" in content


def test_instruction_orders_reviewer_operations_and_exact_paths() -> None:
    """The role waits, assesses, renders, and publishes through shared tools."""
    content = _content()

    _assert_in_order(
        content,
        (
            "`status`",
            "`wait-request`",
            "paths.request",
            "bin/spec_review_answer.bat",
            "`publish-answer`",
        ),
    )
    assert "bin/review_exchange.bat" in content
    assert "one bounded `wait-request` per round" in content
    assert "full exact reviewed specification" in content
    assert "convergence recommendation is advisory" in content
    published = content.index("`publish-answer` reports `outcome: published`")
    post_answer_wait = content.index(
        "immediately run the next bounded `wait-request`",
        published,
    )
    assert post_answer_wait > published
    assert "continue at Step 3" in content
    assert "same reviewer session" in content


def test_instruction_limits_reclaim_to_the_active_reviewer_session() -> None:
    """Cold abandoned requests return to requestor-owned recovery."""
    content = _content()

    assert "expired during this reviewer session" in content
    assert "call `reclaim` once" in content
    assert "cold route" in content
    assert "spec-review-requestor" in content
    assert "Do not reclaim from that cold route" in content


def test_instruction_revalidates_and_retires_retained_context_safely() -> None:
    """A single-use manifest survives until successful republication."""
    content = _content()

    for token in (
        "SHA-256",
        "document_sha256",
        "identity",
        "original_round_number",
        "assessment_input_paths",
        "--expected-document-sha256",
        "--retained-manifest-file",
    ):
        assert token in content
    _assert_in_order(
        content,
        (
            "`publish-answer` reports `outcome: published`",
            "remove the single-use",
            "retained manifest",
        ),
    )
    assert "Rendering or failed publication leaves the manifest intact" in content
    assert "retirement on exit `0` alone" in content


def test_instruction_stops_outside_reviewer_authority() -> None:
    """Writer, human, transcript, and stopped-state actions remain forbidden."""
    content = _content()

    for operation in (
        "consume-answer",
        "continue",
        "confirm",
        "complete",
        "cancel",
        "resolve",
        "archive",
    ):
        assert f"`{operation}`" in content
    for state in (
        "disabled",
        "mismatched",
        "interrupted",
        "repair-required",
        "escalated",
    ):
        assert f"`{state}`" in content
    assert "Reviewer-forbidden operations" in content
    assert "Do not edit or consolidate the reviewed specification" in content
    assert "Do not read the versioned transcript" in content
    assert "stop for human recovery" in content
    assert "Stop for the human choice; do not start a post-answer wait" in content


# eof
