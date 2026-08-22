"""Tests for nesting and qualifying caller-authored review headings."""

from tools.review_markdown_headings import qualify_round_headings


def test_headings_shift_as_one_outline_and_keep_code_fences_literal() -> None:
    """The shallowest heading moves below its parent without flattening children."""
    markdown = """Lead.

## Evidence

### Detail ###

```markdown
## Literal sample
~~~
```

###### Deep detail
"""

    rendered = qualify_round_headings(
        markdown,
        minimum_level=4,
        qualifier="step 2 relocation-force-rpath",
        round_number=3,
    )

    assert "#### Evidence for step 2 relocation-force-rpath (round 3)" in rendered
    assert "##### Detail for step 2 relocation-force-rpath (round 3) ###" in rendered
    assert "###### Deep detail for step 2 relocation-force-rpath (round 3)" in rendered
    assert "```markdown\n## Literal sample\n~~~\n```" in rendered
    assert rendered.endswith("\n")


def test_existing_round_context_is_replaced_and_rendering_is_idempotent() -> None:
    """A caller's older suffix is replaced by the canonical step-round suffix."""
    markdown = "## Test evidence for step 2 relocation-force-rpath round 3"

    rendered = qualify_round_headings(
        markdown,
        minimum_level=3,
        qualifier="step 2 relocation-force-rpath",
        round_number=3,
    )

    assert rendered == "### Test evidence for step 2 relocation-force-rpath (round 3)"
    assert (
        qualify_round_headings(
            rendered,
            minimum_level=3,
            qualifier="step 2 relocation-force-rpath",
            round_number=3,
        )
        == rendered
    )


def test_legacy_reviewer_exchange_suffix_is_replaced_once() -> None:
    """The old round-before-exchange suffix does not survive migration."""
    markdown = (
        "### Findings for step 2 relocation-force-rpath round 3 (exchange 1)"
    )

    rendered = qualify_round_headings(
        markdown,
        minimum_level=3,
        qualifier="step 2 relocation-force-rpath (exchange 1)",
        round_number=3,
    )

    assert rendered == (
        "### Findings for step 2 relocation-force-rpath (exchange 1) (round 3)"
    )


def test_specification_qualifier_is_idempotent() -> None:
    """A specification heading keeps one identity suffix across re-rendering."""
    rendered = "### Evidence for feature-request review-status-command (round 2)"

    assert (
        qualify_round_headings(
            rendered,
            minimum_level=3,
            qualifier="feature-request review-status-command",
            round_number=2,
        )
        == rendered
    )


def test_plain_markdown_and_tilde_fences_are_unchanged() -> None:
    """Content without authored headings returns byte-for-byte equivalent text."""
    markdown = "Lead.\n\n~~~text\n## Literal sample\n```\n~~~"

    assert (
        qualify_round_headings(
            markdown,
            minimum_level=4,
            qualifier="step 1 topic",
            round_number=1,
        )
        == markdown
    )
