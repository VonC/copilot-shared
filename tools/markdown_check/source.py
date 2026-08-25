"""Build one fence-aware source model shared by every Markdown rule."""

from __future__ import annotations

import re
from collections import defaultdict, deque
from pathlib import PurePosixPath
from typing import TYPE_CHECKING

from tools.markdown_check.models import (
    Frontmatter,
    Heading,
    InlineCode,
    ListBlock,
    MarkdownLink,
    MarkdownSource,
    RawHtml,
    SourceLine,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

_FENCE_RE = re.compile(r"^[ \t]*(?P<fence>`{3,}|~{3,})")
_HEADING_RE = re.compile(
    r"^[ \t]{0,3}(?P<marks>#{1,6})[ \t]+"
    r"(?P<title>.*?)(?:[ \t]+#+[ \t]*)?$",
)
_LIST_RE = re.compile(r"^[ \t]{0,3}(?:[-+*]|\d+[.)])[ \t]+")
_HTML_RE = re.compile(r"</?(?P<name>[A-Za-z][A-Za-z0-9-]*)\b")
_LINK_RE = re.compile(r"(?<!!)\[[^\]\n]*\]\((?P<target><[^>\n]+>|[^\s)\n]+)")
_DESCRIPTION_RE = re.compile(r"^[ \t]*description[ \t]*:[ \t]*(?P<value>.*)$")


def fenced_line_numbers(lines: Sequence[str]) -> frozenset[int]:
    """Return line numbers in root or list-indented fenced code blocks."""
    fenced: set[int] = set()
    fence_character: str | None = None
    fence_length = 0
    for line_number, line in enumerate(lines, start=1):
        marker_match = _FENCE_RE.match(line)
        if fence_character is not None:
            fenced.add(line_number)
        if marker_match is None:
            continue
        marker = marker_match.group("fence")
        if fence_character is None:
            fence_character = marker[0]
            fence_length = len(marker)
            fenced.add(line_number)
        elif marker[0] == fence_character and len(marker) >= fence_length:
            fence_character = None
            fence_length = 0
    return frozenset(fenced)


def _frontmatter(lines: Sequence[str]) -> Frontmatter | None:
    """Parse only a leading YAML frontmatter block and its description."""
    if not lines or lines[0].strip() != "---":
        return None
    description: str | None = None
    for index, line in enumerate(lines[1:], start=2):
        if line.strip() == "---":
            return Frontmatter(1, index, description)
        match = _DESCRIPTION_RE.match(line)
        if match is not None:
            value = match.group("value").strip().strip("\"'").strip()
            description = value or None
    return None


def _visible_text(
    lines: Sequence[str],
    fenced: frozenset[int],
    frontmatter: Frontmatter | None,
) -> tuple[str, list[int]]:
    """Return same-width non-fenced text and a one-based line map."""
    visible: list[str] = []
    line_map: list[int] = []
    for line_number, line in enumerate(lines, start=1):
        hidden = line_number in fenced or (
            frontmatter is not None
            and frontmatter.start_line <= line_number <= frontmatter.end_line
        )
        rendered = " " * len(line) if hidden else line
        visible.append(rendered)
        line_map.extend([line_number] * len(rendered))
        if line_number < len(lines):
            line_map.append(line_number)
    return "\n".join(visible), line_map


def _backtick_runs(text: str) -> list[tuple[int, int]]:
    """Collect every maximal backtick run in one pass."""
    runs: list[tuple[int, int]] = []
    index = 0
    while index < len(text):
        if text[index] != "`":
            index += 1
            continue
        end = index + 1
        while end < len(text) and text[end] == "`":
            end += 1
        runs.append((index, end - index))
        index = end
    return runs


def _code_value(raw_content: str) -> str:
    """Apply CommonMark line and matching-space normalization to code content."""
    normalized = raw_content.replace("\n", " ")
    if (
        normalized.startswith(" ")
        and normalized.endswith(" ")
        and normalized.strip(" ")
    ):
        return normalized[1:-1]
    return normalized


def _inline_code(
    text: str,
    line_map: Sequence[int],
) -> tuple[tuple[InlineCode, ...], tuple[tuple[int, int], ...]]:
    """Pair equal backtick runs without rescanning content between spans."""
    runs = _backtick_runs(text)
    by_length: dict[int, deque[int]] = defaultdict(deque)
    for run_index, (_, length) in enumerate(runs):
        by_length[length].append(run_index)
    spans: list[InlineCode] = []
    ranges: list[tuple[int, int]] = []
    run_index = 0
    while run_index < len(runs):
        start, length = runs[run_index]
        candidates = by_length[length]
        while candidates and candidates[0] < run_index:
            candidates.popleft()
        if candidates and candidates[0] == run_index:
            candidates.popleft()
        if not candidates:
            run_index += 1
            continue
        closing_index = candidates.popleft()
        closing_start, _ = runs[closing_index]
        raw_content = text[start + length : closing_start]
        spans.append(
            InlineCode(
                line=line_map[start],
                delimiter_length=length,
                raw_content=raw_content,
                value=_code_value(raw_content),
            ),
        )
        ranges.append((start, closing_start + length))
        run_index = closing_index + 1
    return tuple(spans), tuple(ranges)


def _mask_ranges(text: str, ranges: Sequence[tuple[int, int]]) -> tuple[str, ...]:
    """Hide inline code while retaining line widths for other token locations."""
    masked = list(text)
    for start, end in ranges:
        for index in range(start, end):
            if masked[index] != "\n":
                masked[index] = " "
    return tuple("".join(masked).split("\n"))


def _continues_list(line: str) -> bool:
    """Return whether a non-blank line continues the current list block."""
    return _LIST_RE.match(line) is not None or line[0].isspace()


def _next_nonblank(lines: Sequence[str], start: int) -> int | None:
    """Return the next non-blank zero-based line index."""
    for index in range(start, len(lines)):
        if lines[index].strip():
            return index
    return None


def _list_block_end(lines: Sequence[str], start: int) -> int:
    """Return the zero-based last content line in one list block."""
    end = start
    cursor = start + 1
    while cursor < len(lines):
        line = lines[cursor]
        if line and _continues_list(line):
            end = cursor
            cursor += 1
            continue
        if line.strip():
            break
        lookahead = _next_nonblank(lines, cursor + 1)
        if lookahead is None:
            break
        next_line = lines[lookahead]
        if not _continues_list(next_line):
            break
        end = lookahead
        cursor = lookahead + 1
    return end


def _hidden_line(
    line_number: int,
    fenced: frozenset[int],
    frontmatter: Frontmatter | None,
) -> bool:
    """Return whether a structural scanner must ignore one source line."""
    if line_number in fenced:
        return True
    return bool(
        frontmatter is not None
        and frontmatter.start_line <= line_number <= frontmatter.end_line,
    )


def _list_blocks(
    lines: Sequence[str],
    fenced: frozenset[int],
    frontmatter: Frontmatter | None,
) -> tuple[ListBlock, ...]:
    """Record list outer boundaries once for MD032 evaluation."""
    blocks: list[ListBlock] = []
    index = 0
    while index < len(lines):
        line_number = index + 1
        if _hidden_line(line_number, fenced, frontmatter) or _LIST_RE.match(lines[index]) is None:
            index += 1
            continue
        end = _list_block_end(lines, index)
        blocks.append(
            ListBlock(
                start_line=line_number,
                end_line=end + 1,
                blank_before=index == 0 or not lines[index - 1].strip(),
                blank_after=end == len(lines) - 1 or not lines[end + 1].strip(),
            ),
        )
        index = end + 1
    return tuple(blocks)


def _structural_tokens(
    lines: Sequence[str],
    masked_lines: Sequence[str],
    fenced: frozenset[int],
    frontmatter: Frontmatter | None,
) -> tuple[tuple[Heading, ...], tuple[RawHtml, ...], tuple[MarkdownLink, ...]]:
    """Collect headings, raw HTML, and links from visible source lines."""
    headings: list[Heading] = []
    raw_html: list[RawHtml] = []
    links: list[MarkdownLink] = []
    for line_number, (line, masked) in enumerate(zip(lines, masked_lines, strict=True), start=1):
        if _hidden_line(line_number, fenced, frontmatter):
            continue
        heading = _HEADING_RE.match(line)
        if heading is not None:
            headings.append(
                Heading(line_number, len(heading.group("marks")), heading.group("title").strip()),
            )
        raw_html.extend(
            RawHtml(line_number, match.group("name").lower())
            for match in _HTML_RE.finditer(masked)
        )
        links.extend(
            MarkdownLink(line_number, match.group("target").strip("<>"))
            for match in _LINK_RE.finditer(masked)
        )
    return tuple(headings), tuple(raw_html), tuple(links)


def _body_lines(lines: Sequence[str], frontmatter: Frontmatter | None) -> tuple[SourceLine, ...]:
    """Retain non-blank body lines for bounded adapter classification."""
    body_start = frontmatter.end_line if frontmatter is not None else 0
    return tuple(
        SourceLine(index + 1, line)
        for index, line in enumerate(lines)
        if index >= body_start and line.strip()
    )


def parse_markdown(path: str | PurePosixPath, markdown: str) -> MarkdownSource:
    """Decode already-provided Markdown text into one reusable source model."""
    lines = tuple(markdown.splitlines())
    frontmatter = _frontmatter(lines)
    fenced = fenced_line_numbers(lines)
    visible_text, line_map = _visible_text(lines, fenced, frontmatter)
    inline_code, code_ranges = _inline_code(visible_text, line_map)
    prose_lines = _mask_ranges(visible_text, code_ranges)
    headings, raw_html, links = _structural_tokens(
        lines,
        prose_lines,
        fenced,
        frontmatter,
    )
    return MarkdownSource(
        path=PurePosixPath(str(path).replace("\\", "/")),
        lines=lines,
        frontmatter=frontmatter,
        headings=headings,
        list_blocks=_list_blocks(lines, fenced, frontmatter),
        raw_html=raw_html,
        links=links,
        inline_code=inline_code,
        prose_lines=prose_lines,
        body_lines=_body_lines(lines, frontmatter),
        fenced_lines=fenced,
    )


__all__ = ["fenced_line_numbers", "parse_markdown"]


# eof
