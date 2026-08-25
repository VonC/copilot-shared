"""Structural tests for the Step 4 canonical requestor instruction.

Step 4 keeps coordination guidance in one root instruction. Provider-specific
Markdown carries discovery metadata and a direct redirect only, so later
requestor integrations cannot fork the lifecycle rules.
"""

from __future__ import annotations

from tools import prompt_workflow_steps as steps

_MAX_WORKFLOW_LINES = 15


def _assert_contains_all(content: str, fragments: tuple[str, ...]) -> None:
    """Report every required fragment missing from one requestor instruction."""
    missing = tuple(fragment for fragment in fragments if fragment not in content)
    assert not missing, f"missing requestor fragments: {missing!r}"


def test_canonical_requestor_delegates_every_mutation_to_launcher() -> None:
    """The canonical body names the launcher and core without copying a table."""
    root = steps.llm_shared_dir()
    content = (root / "instructions/review-requestor.md").read_text(encoding="utf-8")
    normalized = " ".join(content.split())

    _assert_contains_all(
        content,
        (
            "review_exchange.bat",
            "ReviewExchangeCore",
            "--content-file",
            "--summary-file",
            "--guidance-file",
            "one final JSON object",
            "standard error",
            "reciprocal active waits",
            "No human prompt or new reviewer invocation",
        ),
    )
    assert "| Request | Answer |" not in content
    assert "reviewer is already in its post-answer `wait-request`" in normalized


def test_provider_files_redirect_directly_to_canonical_instruction() -> None:
    """Each provider adapter points at the root body and stays short."""
    root = steps.llm_shared_dir()
    workflow = (root / ".agent/workflows/review-requestor.md").read_text(
        encoding="utf-8",
    )
    packaged = (
        root / ".agents/llm-shared/instructions/review-requestor.md"
    ).read_text(encoding="utf-8")
    skill = (
        root / ".agents/llm-shared/skills/review-requestor/SKILL.md"
    ).read_text(encoding="utf-8")
    canonical = (root / "instructions/review-requestor.md").read_text(
        encoding="utf-8",
    )

    assert "instructions/review-requestor.md" in workflow
    assert "../../../instructions/review-requestor.md" in packaged
    assert "../../../../instructions/review-requestor.md" in skill
    assert canonical not in workflow
    assert canonical not in packaged
    assert canonical not in skill
    assert len(workflow.splitlines()) < _MAX_WORKFLOW_LINES
    assert len(packaged.splitlines()) == 1


# eof
