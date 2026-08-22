"""Render caller-authored review headings inside one identified round."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator

_ATX_HEADING_RE = re.compile(
    r"^(?P<indent>[ \t]{0,3})(?P<marks>#{1,6})[ \t]+"
    r"(?P<title>.*?)(?P<closing>[ \t]+#+[ \t]*)?$",
)
_FENCE_RE = re.compile(r"^[ \t]{0,3}(?P<fence>`{3,}|~{3,})")
_ROUND_CONTEXT_RE = re.compile(
    r"\s+for step .+?(?: \(exchange \d+\))? "
    r"(?:round \d+|\(round \d+\))(?: \(exchange \d+\))?$",
)


def _authored_headings(lines: list[str]) -> Iterator[tuple[int, re.Match[str]]]:
    """Yield ATX headings outside fenced code blocks."""
    fence_character: str | None = None
    fence_length = 0
    for index, line in enumerate(lines):
        fence = _FENCE_RE.match(line)
        if fence is not None:
            marker = fence.group("fence")
            if fence_character is None:
                fence_character = marker[0]
                fence_length = len(marker)
            elif marker[0] == fence_character and len(marker) >= fence_length:
                fence_character = None
                fence_length = 0
            continue
        if fence_character is not None:
            continue
        heading = _ATX_HEADING_RE.match(line)
        if heading is not None:
            yield index, heading


def _qualified_title(title: str, qualifier: str, round_number: int) -> str:
    """Return one idempotent step-and-round-qualified heading title."""
    base = _ROUND_CONTEXT_RE.sub("", title.rstrip())
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
