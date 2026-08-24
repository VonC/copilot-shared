"""Render caller-authored review headings inside one identified round."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from tools.markdown_check.source import fenced_line_numbers

if TYPE_CHECKING:
    from collections.abc import Iterator

_ATX_HEADING_RE = re.compile(
    r"^(?P<indent>[ \t]{0,3})(?P<marks>#{1,6})[ \t]+"
    r"(?P<title>.*?)(?P<closing>[ \t]+#+[ \t]*)?$",
)
_ROUND_CONTEXT_RE = re.compile(
    r"\s+for step .+?(?: \(exchange \d+\))? "
    r"(?:round \d+|\(round \d+\))(?: \(exchange \d+\))?$",
)


def _authored_headings(lines: list[str]) -> Iterator[tuple[int, re.Match[str]]]:
    """Yield ATX headings using the checker's shared fence boundaries."""
    fenced = fenced_line_numbers(lines)
    for index, line in enumerate(lines):
        if index + 1 in fenced:
            continue
        heading = _ATX_HEADING_RE.match(line)
        if heading is not None:
            yield index, heading


def _qualified_title(title: str, qualifier: str, round_number: int) -> str:
    """Return one idempotent step-and-round-qualified heading title."""
    base = title.rstrip()
    current_suffix = f" for {qualifier} (round {round_number})"
    if base.endswith(current_suffix):
        base = base[: -len(current_suffix)]
    else:
        base = _ROUND_CONTEXT_RE.sub("", base)
    base = re.sub(rf"\s+\(round {round_number}\)$", "", base)
    return f"{base} for {qualifier} (round {round_number})"


def qualify_round_headings(
    markdown: str,
    *,
    minimum_level: int,
    qualifier: str,
    round_number: int,
) -> str:
    """Nest and qualify every caller-authored heading in one review round."""
    lines = markdown.splitlines()
    headings = dict(_authored_headings(lines))
    shallowest = min(
        (len(match.group("marks")) for match in headings.values()),
        default=minimum_level,
    )
    shift = max(0, minimum_level - shallowest)
    for index, heading in headings.items():
        level = min(6, len(heading.group("marks")) + shift)
        lines[index] = (
            f"{heading.group('indent')}{'#' * level} "
            f"{_qualified_title(heading.group('title'), qualifier, round_number)}"
            f"{heading.group('closing') or ''}"
        )
    rendered = "\n".join(lines)
    if markdown.endswith("\n"):
        rendered += "\n"
    return rendered


__all__ = ["qualify_round_headings"]


# eof
