"""Step 1 acceptance for independent review-mode documentation.

The tests pin entry-point discovery, the visual and terminology boundary from
self-review, canonical authority links, bounded local-link checks, and the
incremental AC01-through-AC12 coverage record.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from .conftest import assert_local_links, assert_named_paths, read_declared

if TYPE_CHECKING:
    from pathlib import Path

_EXPLANATION = "wiki/explanation/independent-review-mode-and-human-authority.md"
_SELF_REVIEW_EXPLANATION = "wiki/explanation/why-the-llm-reviews-its-own-work.md"
_SELF_REVIEW_HOW_TO = "wiki/how-to/answer-a-review-round.md"
_COVERAGE = "docs/v0.11.0/coverage.v0.11.0.review-mode-docs.md"
_STEP_1_PAGES = (
    "README.md",
    "wiki/README.md",
    _EXPLANATION,
    _SELF_REVIEW_EXPLANATION,
    _SELF_REVIEW_HOW_TO,
    _COVERAGE,
)
_CANONICAL_INSTRUCTIONS = (
    "instructions/review-requestor.md",
    "instructions/spec-reviewer.md",
    "instructions/code-reviewer.md",
)
_INVENTORY_CANDIDATES = (
    "wiki/reference/skills-catalog.md",
    "wiki/reference/artifact-files.md",
    "wiki/reference/aliases-and-launchers.md",
    "wiki/reference/templates.md",
    "wiki/reference/automation-and-direct-invocation.md",
    "wiki/reference/repository-layout.md",
)
_MINIMUM_PENDING_ROWS = 10
_BACKTICK = "`"


def _heading_position(markdown: str, label: str) -> int:
    """Return the position of one second-level heading containing a label."""
    match = re.search(rf"^## .*{label}.*$", markdown, re.MULTILINE)
    assert match is not None
    return match.start()


def test_step_1_entry_points_distinguish_review_modes_and_keep_diataxis_order(
    docs_root: Path,
) -> None:
    """Step 1 discovery: both entry points route to the new explanation."""
    root_readme = read_declared(docs_root, "README.md")
    wiki_readme = read_declared(docs_root, "wiki/README.md")

    assert "independent review mode" in root_readme
    assert _EXPLANATION in root_readme
    assert "self-review loop" in root_readme
    assert "independent review mode" in wiki_readme
    assert "explanation/independent-review-mode-and-human-authority.md" in wiki_readme
    headings = tuple(
        _heading_position(wiki_readme, label)
        for label in ("Explanation", "Tutorials", "How-to guides", "Reference")
    )
    assert headings == tuple(sorted(headings))


def test_step_1_visual_identity_and_reciprocal_comparison_stay_distinct(
    docs_root: Path,
) -> None:
    """Step 1 identity: generic independent logo, retained self-review logo."""
    explanation = read_declared(docs_root, _EXPLANATION)
    self_review_explanation = read_declared(docs_root, _SELF_REVIEW_EXPLANATION)
    self_review_how_to = read_declared(docs_root, _SELF_REVIEW_HOW_TO)

    assert "../assets/logo-llm-shared-transparent.png" in explanation
    assert "logo-llm-shared-review-transparent.png" in self_review_explanation
    assert "logo-llm-shared-review-transparent.png" in self_review_how_to
    comparison_link = "independent-review-mode-and-human-authority.md"
    assert comparison_link in self_review_explanation
    assert f"../explanation/{comparison_link}" in self_review_how_to


def test_step_1_explanation_names_authorities_and_canonical_policy(
    docs_root: Path,
) -> None:
    """Step 1 authority: advisory results and durable evidence are explicit."""
    explanation = read_declared(docs_root, _EXPLANATION)

    for role in ("requestor", "reviewer", "human"):
        assert role in explanation
    assert "does not authorize consolidation or commit" in explanation
    assert "not working context" in explanation
    for instruction in _CANONICAL_INSTRUCTIONS:
        assert f"../../{instruction}" in explanation


def test_step_1_declared_links_and_named_paths_resolve(docs_root: Path) -> None:
    """Step 1 links: bounded declared pages resolve local targets and fragments."""
    assert_local_links(docs_root, _STEP_1_PAGES)
    assert_named_paths(
        docs_root,
        (
            *_STEP_1_PAGES,
            *_CANONICAL_INSTRUCTIONS,
            "wiki/assets/logo-llm-shared-transparent.png",
            "wiki/assets/logo-llm-shared-review-transparent.png",
        ),
    )


def test_step_1_coverage_starts_complete_enumerations_with_pending_rows(
    docs_root: Path,
) -> None:
    """Step 1 coverage: all criteria and inventory candidates start versioned."""
    coverage = read_declared(docs_root, _COVERAGE)

    for number in range(1, 13):
        assert coverage.count(f"| AC{number:02d} |") == 1
    for candidate in _INVENTORY_CANDIDATES:
        assert coverage.count(f"{_BACKTICK}{candidate}{_BACKTICK}") == 1
    assert "| AC02 | Page evidence |" in coverage
    assert "| AC10 | Validation evidence | Pending |" in coverage
    assert coverage.count("| Pending |") >= _MINIMUM_PENDING_ROWS
