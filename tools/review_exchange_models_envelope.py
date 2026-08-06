"""Review-content envelope handling for the v0.11.0 exchange core.

Step 1 split: keeps strict request and answer metadata, first-fenced JSON
parsing, and human summary identity checks separate from durable state models.
"""

# ruff: noqa: EM101, EM102, TRY003

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

from tools.review_exchange_models import (
    ExchangeIdentity,
    ReviewContext,
    ReviewDisposition,
    ReviewExchangeError,
    ReviewFamily,
    ReviewRole,
    enum_value,
    mapping_value,
    optional_path_value,
    optional_string,
    path_value,
    positive_integer,
    strict_fields,
    validate_local_timestamp,
)

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path
    from typing import Any


@dataclass(frozen=True)
class Envelope:
    """Strict machine-readable metadata for request and answer Markdown."""

    identity: ExchangeIdentity
    umbrella_path: Path | None
    document_path: Path
    implementation_step: str | None
    role: ReviewRole
    round_number: int
    created_at: str
    disposition: ReviewDisposition | None = None

    def __post_init__(self) -> None:
        """Validate role, round, timestamp, and family context fields."""
        object.__setattr__(self, "document_path", self.document_path.resolve())
        if self.umbrella_path is not None:
            object.__setattr__(self, "umbrella_path", self.umbrella_path.resolve())
        positive_integer(self.round_number, "envelope round")
        validate_local_timestamp(self.created_at)
        if self.role is ReviewRole.REVIEWER and self.disposition is None:
            raise ReviewExchangeError("reviewer envelope requires a disposition")
        if self.role is not ReviewRole.REVIEWER and self.disposition is not None:
            raise ReviewExchangeError(
                f"{self.role.value} envelope cannot declare a disposition",
            )
        if self.identity.family is ReviewFamily.CODE:
            if not self.implementation_step:
                raise ReviewExchangeError("code envelope requires an implementation step")
        elif self.implementation_step is not None:
            raise ReviewExchangeError(
                "implementation step is only valid for code review",
            )

    def to_dict(self) -> dict[str, Any]:
        """Return strict JSON-compatible envelope data."""
        return {
            "identity": self.identity.to_dict(),
            "umbrella_path": (
                self.umbrella_path.as_posix() if self.umbrella_path is not None else None
            ),
            "document_path": self.document_path.as_posix(),
            "implementation_step": self.implementation_step,
            "role": self.role.value,
            "round_number": self.round_number,
            "created_at": self.created_at,
            "disposition": self.disposition.value if self.disposition is not None else None,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Envelope:
        """Construct an envelope from strict JSON-compatible data."""
        expected = {
            "identity", "umbrella_path", "document_path", "implementation_step",
            "role", "round_number", "created_at", "disposition",
        }
        strict_fields(data, expected, "envelope")
        identity_data = mapping_value(data["identity"], "envelope identity")
        disposition_value = data["disposition"]
        disposition = (
            None
            if disposition_value is None
            else enum_value(
                ReviewDisposition,
                disposition_value,
                "review disposition",
            )
        )
        created_at = data["created_at"]
        if not isinstance(created_at, str):
            raise ReviewExchangeError("invalid envelope creation timestamp")
        return cls(
            identity=ExchangeIdentity.from_dict(identity_data),
            umbrella_path=optional_path_value(data["umbrella_path"], "umbrella path"),
            document_path=path_value(data["document_path"], "document path"),
            implementation_step=optional_string(
                data["implementation_step"],
                "implementation step",
            ),
            role=enum_value(ReviewRole, data["role"], "review role"),
            round_number=positive_integer(data["round_number"], "envelope round"),
            created_at=created_at,
            disposition=disposition,
        )


def render_envelope_markdown(envelope: Envelope, content: str) -> str:
    """Render one first-fenced JSON envelope followed by authored Markdown."""
    metadata = json.dumps(envelope.to_dict(), indent=2, sort_keys=True)
    return f"```json\n{metadata}\n```\n{content}"


def parse_envelope_markdown(markdown: str) -> tuple[Envelope, str]:
    """Parse exactly the first fenced block and return later Markdown unchanged."""
    opener = re.search(r"(?m)^```([^\r\n]*)\r?\n", markdown)
    if opener is None:
        raise ReviewExchangeError("review content has no fenced metadata block")
    if opener.group(1).strip() != "json":
        raise ReviewExchangeError("first fenced block must be JSON metadata")
    closer = re.search(r"(?m)^```[ \t]*\r?$", markdown[opener.end() :])
    if closer is None:
        raise ReviewExchangeError("JSON metadata fence is not closed")
    payload_start = opener.end()
    payload_end = payload_start + closer.start()
    content_start = payload_start + closer.end()
    if content_start < len(markdown) and markdown[content_start] == "\n":
        content_start += 1
    try:
        data = json.loads(markdown[payload_start:payload_end])
    except json.JSONDecodeError as error:
        raise ReviewExchangeError(f"invalid envelope JSON: {error.msg}") from error
    envelope_data = mapping_value(data, "envelope JSON")
    return Envelope.from_dict(envelope_data), markdown[content_start:]


def _summary_value(summary: str, label: str) -> str:
    """Read exactly one human-readable identity field from a summary."""
    prefix = f"{label}: "
    values = [line[len(prefix) :] for line in summary.splitlines() if line.startswith(prefix)]
    if len(values) != 1:
        raise ReviewExchangeError(f"summary identity mismatch: expected one {label} field")
    return values[0]


def validate_summary_identity(
    summary: str,
    context: ReviewContext,
    round_number: int,
) -> None:
    """Fail when human-readable request identity differs from machine context."""
    positive_integer(round_number, "review round")
    umbrella = (
        context.umbrella_path.as_posix()
        if context.umbrella_path is not None
        else "none"
    )
    expected = {"Umbrella draft": umbrella, "Review round": str(round_number)}
    if context.identity.family is ReviewFamily.SPECIFICATION:
        expected["Reviewed specification"] = context.document_path.as_posix()
    else:
        expected["Implementation plan"] = context.document_path.as_posix()
        step = cast("str", context.implementation_step)
        expected["Implementation step"] = step
    mismatches = [
        label
        for label, value in expected.items()
        if _summary_value(summary, label) != value
    ]
    if mismatches:
        raise ReviewExchangeError(
            "summary identity mismatch: " + ", ".join(mismatches),
        )


# eof
