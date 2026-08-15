"""Resolve mandatory code-review validation commands and their sources."""

# ruff: noqa: EM101, TRY003

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from tools.review_exchange_models import ReviewExchangeError

if TYPE_CHECKING:
    from collections.abc import Sequence

ValidationSource = Literal["project", "plan", "request"]
DEFAULT_PROJECT_VALIDATION_COMMANDS = ("ghog day",)
_SOURCE_ORDER: tuple[ValidationSource, ...] = ("project", "plan", "request")


@dataclass(frozen=True)
class ResolvedValidationCommand:
    """One normalized command with every source that requires it."""

    command: str
    sources: tuple[ValidationSource, ...]

    def __post_init__(self) -> None:
        """Reject empty commands and invalid or duplicate source labels."""
        if not self.command.strip():
            raise ReviewExchangeError("validation command must be non-empty")
        if not self.sources or len(set(self.sources)) != len(self.sources):
            raise ReviewExchangeError("validation command sources must be non-empty and unique")
        if any(source not in _SOURCE_ORDER for source in self.sources):
            raise ReviewExchangeError("validation command source is unsupported")

    def to_payload(self) -> dict[str, object]:
        """Return the canonical request-payload representation."""
        return {"command": self.command, "sources": list(self.sources)}


@dataclass(frozen=True)
class ResolvedValidationSet:
    """Immutable, deterministically ordered mandatory validation commands."""

    commands: tuple[ResolvedValidationCommand, ...]

    def __post_init__(self) -> None:
        """Reject empty sets and duplicate command lines."""
        if not self.commands:
            raise ReviewExchangeError("resolved validation set must be non-empty")
        command_lines = tuple(entry.command for entry in self.commands)
        if len(set(command_lines)) != len(command_lines):
            raise ReviewExchangeError("resolved validation commands must be unique")

    @property
    def command_lines(self) -> tuple[str, ...]:
        """Return the command lines in deterministic execution order."""
        return tuple(entry.command for entry in self.commands)

    def to_payload(self) -> dict[str, object]:
        """Return the canonical request-payload representation."""
        return {"commands": [entry.to_payload() for entry in self.commands]}


def resolve_code_review_validation(
    project_defaults: Sequence[str],
    plan_additions: Sequence[str] = (),
    request_additions: Sequence[str] = (),
) -> ResolvedValidationSet:
    """Combine required defaults and additions without a removal operation."""
    if not project_defaults:
        raise ReviewExchangeError("project validation defaults must be non-empty")
    sources_by_command: dict[str, list[ValidationSource]] = {}
    for source, commands in zip(
        _SOURCE_ORDER,
        (project_defaults, plan_additions, request_additions),
        strict=True,
    ):
        for raw_command in commands:
            command = raw_command.strip()
            if not command:
                raise ReviewExchangeError("validation command must be non-empty")
            labels = sources_by_command.setdefault(command, [])
            if source not in labels:
                labels.append(source)
    return ResolvedValidationSet(
        tuple(
            ResolvedValidationCommand(command, tuple(sources))
            for command, sources in sources_by_command.items()
        ),
    )


# eof
