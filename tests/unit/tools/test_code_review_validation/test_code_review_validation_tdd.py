"""TDD contracts for immutable mandatory validation resolution."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from typing import cast

import pytest

from tools.code_review_validation import (
    ResolvedValidationCommand,
    ResolvedValidationSet,
    ValidationSource,
    resolve_code_review_validation,
)
from tools.review_exchange_models import ReviewExchangeError


def test_resolver_preserves_defaults_adds_checks_and_merges_sources() -> None:
    """First appearance orders commands and every contributing source is retained."""
    resolved = resolve_code_review_validation(
        ("ghog day", "project lint"),
        ("focused tests", "project lint"),
        ("request audit", "focused tests"),
    )

    assert resolved.command_lines == (
        "ghog day",
        "project lint",
        "focused tests",
        "request audit",
    )
    assert [entry.sources for entry in resolved.commands] == [
        ("project",),
        ("project", "plan"),
        ("plan", "request"),
        ("request",),
    ]
    with pytest.raises(FrozenInstanceError):
        setattr(resolved, "commands", ())


def test_resolver_is_deterministic_and_exposes_drift_inputs() -> None:
    """Equal inputs are stable while later additions produce a comparable value."""
    before = resolve_code_review_validation(("ghog day",), ("focused tests",))
    repeated = resolve_code_review_validation(("ghog day",), ("focused tests",))
    after = resolve_code_review_validation(
        ("ghog day",),
        ("focused tests",),
        ("security audit",),
    )

    assert before == repeated
    assert before != after
    assert after.command_lines == (*before.command_lines, "security audit")


@pytest.mark.parametrize(
    ("project", "plan", "request_commands", "message"),
    [
        ((), (), (), "project validation defaults must be non-empty"),
        ((" ",), (), (), "validation command must be non-empty"),
        (("ghog day",), ("",), (), "validation command must be non-empty"),
        (("ghog day",), (), ("\n",), "validation command must be non-empty"),
    ],
)
def test_resolver_rejects_missing_defaults_and_empty_additions(
    project: tuple[str, ...],
    plan: tuple[str, ...],
    request_commands: tuple[str, ...],
    message: str,
) -> None:
    """The additive API cannot erase defaults or publish empty commands."""
    with pytest.raises(ReviewExchangeError, match=message):
        resolve_code_review_validation(project, plan, request_commands)


def test_typed_validation_values_reject_invalid_direct_construction() -> None:
    """Callers cannot bypass resolver invariants through public constructors."""
    with pytest.raises(ReviewExchangeError, match="validation command must be non-empty"):
        ResolvedValidationCommand(" ", ("project",))
    with pytest.raises(ReviewExchangeError, match="sources must be non-empty and unique"):
        ResolvedValidationCommand("ghog day", ())
    with pytest.raises(ReviewExchangeError, match="source is unsupported"):
        ResolvedValidationCommand("ghog day", (cast("ValidationSource", "writer"),))
    with pytest.raises(ReviewExchangeError, match="set must be non-empty"):
        ResolvedValidationSet(())

    command = ResolvedValidationCommand("ghog day", ("project",))
    with pytest.raises(ReviewExchangeError, match="commands must be unique"):
        ResolvedValidationSet((command, command))
