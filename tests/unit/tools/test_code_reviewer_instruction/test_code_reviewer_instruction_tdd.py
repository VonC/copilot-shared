"""Content contracts for the canonical implementation code reviewer."""

from __future__ import annotations

from tools import prompt_workflow_steps as steps

_INSTRUCTION = steps.llm_shared_dir() / "instructions" / "code-reviewer.md"
_MINIMUM_EVIDENCE_REFERENCES = 7


def _content() -> str:
    """Read the canonical policy once for one assertion phase."""
    return _INSTRUCTION.read_text(encoding="utf-8")


def _assert_contains_all(content: str, fragments: tuple[str, ...]) -> None:
    """Report every required fragment missing from one policy document."""
    missing = tuple(fragment for fragment in fragments if fragment not in content)
    assert not missing, f"missing policy fragments: {missing!r}"


def test_instruction_delegates_every_executable_boundary_to_launchers() -> None:
    """The instruction sequences launchers instead of cloning their behavior."""
    content = _content()
    evidence = "bin/code_review_evidence.bat"
    for responsibility in (
        "baseline",
        "pre-repair blobs",
        "attribute-reviewer-patch",
        "validation-state",
        "manifest write",
        "manifest read",
        "manifest retire",
    ):
        assert responsibility in content
    assert content.count(evidence) >= _MINIMUM_EVIDENCE_REFERENCES
    assert "bin/code_review_answer.bat" in content
    assert "bin/review_exchange.bat" in content
    for forbidden_clone in ("git write-tree", "git hash-object", "git diff", "os.remove"):
        assert forbidden_clone not in content


def test_instruction_pins_policy_identity_and_reciprocal_bounded_waits() -> None:
    """Reviewer entry and later rounds use exact bounded counterpart waits."""
    content = _content()
    _assert_contains_all(
        content,
        (
            "--family code",
            "--convergence-signal commit-ready",
            '--another-round-label "Rework and review again"',
            '--continue-owning-workflow-label "Commit"',
            "--implementation-step <exact-plan-step>",
            "one bounded `wait-request` per round",
            "immediately run the next bounded `wait-request`",
            "same reviewer session",
            "continue at Step 3",
            "Read only the returned `paths.request`",
            "whether the expired request is first seen cold",
            "Require the reclaimed state to be",
        ),
    )
    assert "Do not read the versioned transcript" in " ".join(content.split())


def test_instruction_covers_assessment_repairs_validation_and_early_rejection() -> None:
    """The caller preserves every designed assessment and mutation boundary."""
    content = _content()
    for required in (
        "request-time index tree",
        "early rejection",
        "implementation-check",
        "umbrella digest",
        "pre-existing unstaged",
        "reviewer-authored",
        "tracked validation side effect",
        "a.commit",
        "Human guidance:",
        "changes-requested",
        "commit-ready",
    ):
        assert required in content


def test_instruction_covers_manifest_recovery_and_both_publication_exits() -> None:
    """Retained evidence survives failures and retires on either published exit."""
    content = _content()
    assert "identity-and-step-derived" in content
    assert "exits `0`" in content
    assert "exit `3`" in content
    assert "outcome: published" in content
    assert "assessed index tree" in content
    assert "fresh assessment" in content
    assert "exchange_occurrence" in content


def test_instruction_forbids_writer_human_and_commit_authority() -> None:
    """The reviewer can wait again without crossing role authority."""
    content = _content()
    normalized = " ".join(content.split())
    for operation in (
        "consume-answer",
        "continue",
        "confirm",
        "complete",
        "escalate",
        "cancel",
        "resolve",
        "archive",
        "commit",
    ):
        assert f"`{operation}`" in content
    assert "never authorizes a commit" in content
    assert "Waiting does not transfer requestor authority" in normalized
    assert "Stop after a convergence publication" in normalized


# eof
