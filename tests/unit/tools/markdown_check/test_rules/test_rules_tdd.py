"""Tests for supported Markdown and repository-local rule behavior."""

# ruff: noqa: PLR2004

from collections.abc import Callable

import pytest

from tools.markdown_check.classifier import DocumentClassification, DocumentKind
from tools.markdown_check.models import Finding, MarkdownSource
from tools.markdown_check.rules import (
    check_ls001,
    check_ls002,
    check_ls003,
    check_md001,
    check_md024,
    check_md025,
    check_md032,
    check_md033,
    check_md038,
    evaluate_rules,
)
from tools.markdown_check.source import parse_markdown

Rule = Callable[[MarkdownSource], tuple[Finding, ...]]


def test_heading_list_html_and_code_rules_return_located_findings() -> None:
    """Every catalog evaluator reports its own stable identifier and source line."""
    source = parse_markdown(
        "docs/broken.md",
        """# Title
### Jump
# Other title
## Repeated
## Repeated
Prose.
- item
Following prose.
<div>raw</div>
` padded `
""",
    )
    classification = DocumentClassification(DocumentKind.STRUCTURED, "default")

    findings = evaluate_rules(source, classification, allowed_html=frozenset({"img"}))

    rules = {finding.rule for finding in findings}
    assert rules == {"MD001", "MD024", "MD025", "MD032", "MD033", "MD038", "LS003"}
    assert any(finding.rule == "MD001" and finding.line == 2 for finding in findings)
    assert any(finding.rule == "MD032" and finding.line == 7 for finding in findings)
    assert any(finding.rule == "MD033" and finding.line == 9 for finding in findings)


def test_structured_outline_rules_and_adapter_exemptions_are_separate() -> None:
    """Only LS001 and LS002 honor adapter classification."""
    source = parse_markdown("docs/outline.md", "## Only section\n")
    structured = DocumentClassification(DocumentKind.STRUCTURED, "default")
    adapter = DocumentClassification(DocumentKind.ADAPTER, "frontmatter")

    assert [finding.rule for finding in check_ls001(source, structured)] == ["LS001"]
    assert [finding.rule for finding in check_ls002(source, structured)] == ["LS002"]
    assert check_ls001(source, adapter) == ()
    assert check_ls002(source, adapter) == ()


def test_md001_allows_a_fragment_to_start_below_level_one() -> None:
    """MD001 compares consecutive headings and leaves first-heading policy to MD041."""
    source = parse_markdown("templates/fragment.md", "## Fragment\n### Child\n")

    assert check_md001(source) == ()


@pytest.mark.parametrize(
    ("markdown", "has_finding"),
    [
        ("` leading`", True),
        ("`trailing `", True),
        ("` padded `", True),
        ("`  genuine  `", False),
        ("`   `", False),
        ("`` `literal` ``", False),
        ("`plain`", False),
    ],
)
def test_md038_distinguishes_padding_from_genuine_code_space(
    markdown: str,
    *,
    has_finding: bool,
) -> None:
    """MD038 preserves parsed boundary spaces and required backtick padding."""
    source = parse_markdown("docs/code.md", markdown)

    assert bool(check_md038(source)) is has_finding


def test_individual_rules_cover_clean_and_configured_paths() -> None:
    """Clean sources and the configured img element produce no findings."""
    source = parse_markdown(
        "docs/clean.md",
        """# Title

## First section

Text with <img src="logo.png"> and `code`.

## Second section
""",
    )

    rules: tuple[Rule, ...] = (
        check_md001,
        check_md024,
        check_md025,
        check_md032,
        check_md038,
        check_ls003,
    )
    assert all(rule(source) == () for rule in rules)
    assert check_md033(source, allowed_elements=frozenset({"img"})) == ()


def test_md032_accepts_a_list_with_blank_boundaries() -> None:
    """A list separated from surrounding prose satisfies MD032."""
    source = parse_markdown("docs/list.md", "Lead.\n\n- item\n\nTail.\n")

    assert check_md032(source) == ()


# eof
