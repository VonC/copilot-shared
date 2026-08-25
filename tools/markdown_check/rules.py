"""Pure evaluators for the bounded repository Markdown rule catalog."""

from __future__ import annotations

import re
import unicodedata
from itertools import pairwise

from tools.markdown_check.classifier import DocumentClassification, DocumentKind
from tools.markdown_check.models import Finding, InlineCode, MarkdownSource

_LINK_LABEL_RE = re.compile(r"!?\[([^\]]*)\]\([^)]*\)")
_HTML_TAG_RE = re.compile(r"</?[A-Za-z][^>]*>")
_UNDERSCORE_STRONG_RE = re.compile(r"(?<![\\_])__(?=\S).+?(?<=\S)__(?!_)")
_WHITESPACE_RE = re.compile(r"\s+")
_SECTION_LEVEL = 2
_MIN_SECTION_COUNT = 2


def _finding(source: MarkdownSource, line: int, rule: str, reason: str) -> Finding:
    """Build one finding with the shared stable path representation."""
    return Finding(source.path.as_posix(), line, rule, reason)


def check_md001(source: MarkdownSource) -> tuple[Finding, ...]:
    """Report level skips between consecutive headings."""
    findings: list[Finding] = []
    for previous, heading in pairwise(source.headings):
        if heading.level > previous.level + 1:
            findings.append(
                _finding(
                    source,
                    heading.line,
                    "MD001",
                    f"heading level {heading.level} skips level {previous.level + 1}",
                ),
            )
    return tuple(findings)


def check_md024(source: MarkdownSource) -> tuple[Finding, ...]:
    """Report every exact heading title occurrence after the first."""
    seen: set[str] = set()
    findings: list[Finding] = []
    for heading in source.headings:
        if heading.title in seen:
            findings.append(
                _finding(source, heading.line, "MD024", "duplicate heading content"),
            )
        else:
            seen.add(heading.title)
    return tuple(findings)


def check_md025(source: MarkdownSource) -> tuple[Finding, ...]:
    """Report every level-one heading after the document's first title."""
    seen_title = False
    findings: list[Finding] = []
    for heading in source.headings:
        if heading.level != 1:
            continue
        if seen_title:
            findings.append(
                _finding(source, heading.line, "MD025", "multiple level-one headings"),
            )
        seen_title = True
    return tuple(findings)


def check_md032(source: MarkdownSource) -> tuple[Finding, ...]:
    """Report list blocks that touch adjacent non-blank content."""
    findings: list[Finding] = []
    for block in source.list_blocks:
        if block.blank_before and block.blank_after:
            continue
        boundaries: list[str] = []
        if not block.blank_before:
            boundaries.append("before")
        if not block.blank_after:
            boundaries.append("after")
        findings.append(
            _finding(
                source,
                block.start_line,
                "MD032",
                f"list block needs a blank line {' and '.join(boundaries)} it",
            ),
        )
    return tuple(findings)


def check_md033(
    source: MarkdownSource,
    *,
    allowed_elements: frozenset[str] = frozenset(),
) -> tuple[Finding, ...]:
    """Report raw HTML elements not present in the configured allowance."""
    allowed = frozenset(element.lower() for element in allowed_elements)
    return tuple(
        _finding(source, element.line, "MD033", f"raw HTML element <{element.name}>")
        for element in source.raw_html
        if element.name not in allowed
    )


def _allowed_md038_space(span: InlineCode) -> bool:
    """Recognize genuine code whitespace and required literal-backtick padding."""
    raw = span.raw_content.replace("\n", " ")
    leading = raw.startswith(" ")
    trailing = raw.endswith(" ")
    if not leading and not trailing:
        return True
    if not raw.strip(" "):
        return True
    if not leading or not trailing:
        return False
    if span.value.startswith(" ") or span.value.endswith(" "):
        return True
    core = raw[1:-1]
    return core.startswith("`") or core.endswith("`")


def check_md038(source: MarkdownSource) -> tuple[Finding, ...]:
    """Report unnecessary spaces immediately inside inline-code delimiters."""
    return tuple(
        _finding(
            source,
            span.line,
            "MD038",
            "unnecessary space inside inline-code delimiters",
        )
        for span in source.inline_code
        if not _allowed_md038_space(span)
    )


def check_md050(source: MarkdownSource) -> tuple[Finding, ...]:
    """Require asterisks rather than underscores for strong emphasis."""
    return tuple(
        _finding(
            source,
            line_number,
            "MD050",
            "strong style [Expected: asterisk; Actual: underscore]",
        )
        for line_number, line in enumerate(source.prose_lines, start=1)
        if _UNDERSCORE_STRONG_RE.search(line) is not None
    )


def check_ls001(
    source: MarkdownSource,
    classification: DocumentClassification,
) -> tuple[Finding, ...]:
    """Require one level-one title only for structured documents."""
    if classification.kind is DocumentKind.ADAPTER or any(
        heading.level == 1 for heading in source.headings
    ):
        return ()
    return (_finding(source, 1, "LS001", "structured document needs a title"),)


def check_ls002(
    source: MarkdownSource,
    classification: DocumentClassification,
) -> tuple[Finding, ...]:
    """Require multiple level-two sections only for structured documents."""
    if classification.kind is DocumentKind.ADAPTER:
        return ()
    section_count = sum(heading.level == _SECTION_LEVEL for heading in source.headings)
    if section_count >= _MIN_SECTION_COUNT:
        return ()
    return (
        _finding(source, 1, "LS002", "structured document needs multiple sections"),
    )


def _normalized_title(title: str) -> str:
    """Apply the repository's anchor-style heading normalization."""
    rendered = _LINK_LABEL_RE.sub(r"\1", title)
    rendered = _HTML_TAG_RE.sub("", rendered)
    rendered = rendered.replace("`", "").replace("*", "").replace("_", "").replace("~", "")
    kept = "".join(
        character
        for character in rendered.casefold()
        if character == "-"
        or character.isspace()
        or unicodedata.category(character)[0] in {"L", "N"}
    )
    return _WHITESPACE_RE.sub("-", kept.strip())


def check_ls003(source: MarkdownSource) -> tuple[Finding, ...]:
    """Report every anchor-normalized heading title occurrence after the first."""
    seen: set[str] = set()
    findings: list[Finding] = []
    for heading in source.headings:
        normalized = _normalized_title(heading.title)
        if normalized in seen:
            findings.append(
                _finding(
                    source,
                    heading.line,
                    "LS003",
                    "heading title is not globally unique",
                ),
            )
        else:
            seen.add(normalized)
    return tuple(findings)


def evaluate_rules(
    source: MarkdownSource,
    classification: DocumentClassification,
    *,
    allowed_html: frozenset[str] = frozenset(),
) -> tuple[Finding, ...]:
    """Evaluate every Step 1 rule against one already-parsed source."""
    return (
        *check_md001(source),
        *check_md024(source),
        *check_md025(source),
        *check_md032(source),
        *check_md033(source, allowed_elements=allowed_html),
        *check_md038(source),
        *check_md050(source),
        *check_ls001(source, classification),
        *check_ls002(source, classification),
        *check_ls003(source),
    )


__all__ = [
    "check_ls001",
    "check_ls002",
    "check_ls003",
    "check_md001",
    "check_md024",
    "check_md025",
    "check_md032",
    "check_md033",
    "check_md038",
    "check_md050",
    "evaluate_rules",
]


# eof
