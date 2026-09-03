"""Durable coordination model for the v0.11.0 review-exchange core.

Step 2 adds a strict two-role LLM-nature snapshot while retaining legacy
coordination parsing for records that predate identity evidence.
"""

# ruff: noqa: EM101, TRY003

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, cast

from tools.review_exchange_models import (
    Actor,
    ConfirmationOutcome,
    CoordinationStatus,
    FamilyPolicy,
    IncompleteTransitionKind,
    ReviewContext,
    ReviewExchangeError,
    enum_value,
    mapping_value,
    non_negative_integer,
    optional_boolean,
    optional_string,
    positive_integer,
    strict_fields,
    validate_local_timestamp,
)
from tools.review_role_nature import RoleNatureSnapshot

if TYPE_CHECKING:
    from collections.abc import Mapping
    from typing import Any


def _validate_coordination_status(record: CoordinationRecord) -> None:
    """Validate lease and expected-actor rules for the durable status."""
    if record.status is CoordinationStatus.ACTIVE and record.lease_renewed_at is None:
        raise ReviewExchangeError("active coordination requires a lease timestamp")
    if (
        record.status is CoordinationStatus.AWAITING_HUMAN_CONFIRMATION
        and record.expected_next_actor is not Actor.HUMAN
    ):
        raise ReviewExchangeError("confirmation status requires human as next actor")
    if record.status is not CoordinationStatus.ESCALATED:
        return
    if not record.escalation_reason:
        raise ReviewExchangeError("escalated coordination requires a reason")
    if record.lease_renewed_at is not None:
        raise ReviewExchangeError("escalated coordination cannot carry an active lease")


def _validate_incomplete_transition(record: CoordinationRecord) -> None:
    """Validate the all-or-none transcript repair marker fields."""
    fields = (
        record.incomplete_transition,
        record.transcript_entry_id,
        record.transcript_offset,
    )
    if not any(value is not None for value in fields):
        return
    if not all(value is not None for value in fields):
        raise ReviewExchangeError(
            "incomplete transition fields must be recorded together",
        )
    offset = cast("int", record.transcript_offset)
    non_negative_integer(offset, "transcript offset")


def _validate_confirmation(record: CoordinationRecord) -> None:
    """Validate the all-or-none human confirmation fields."""
    fields = (
        record.confirmation_label,
        record.confirmed_outcome,
        record.confirmation_timestamp,
    )
    if not any(value is not None for value in fields):
        return
    if not all(value is not None for value in fields):
        raise ReviewExchangeError("confirmation fields must be recorded together")
    timestamp = cast("str", record.confirmation_timestamp)
    validate_local_timestamp(timestamp)


@dataclass(frozen=True)
class CoordinationRecord:
    """Durable cross-process ownership, recovery, and confirmation state."""

    context: ReviewContext
    policy: FamilyPolicy
    status: CoordinationStatus
    owner: Actor
    expected_next_actor: Actor
    round_number: int
    lease_renewed_at: str | None
    reviewed_work_changed: bool | None = None
    convergence_recommended: bool | None = None
    no_progress_streak: int = 0
    clarification_used: bool = False
    incomplete_transition: IncompleteTransitionKind | None = None
    transcript_entry_id: str | None = None
    transcript_offset: int | None = None
    escalation_reason: str | None = None
    confirmation_label: str | None = None
    confirmed_outcome: ConfirmationOutcome | None = None
    confirmation_timestamp: str | None = None
    human_guidance: str | None = None
    role_natures: RoleNatureSnapshot = field(default_factory=RoleNatureSnapshot)

    def __post_init__(self) -> None:
        """Validate status, repair-marker, and confirmation invariants."""
        positive_integer(self.round_number, "coordination round")
        non_negative_integer(self.no_progress_streak, "no-progress streak")
        if self.lease_renewed_at is not None:
            validate_local_timestamp(self.lease_renewed_at)
        _validate_coordination_status(self)
        _validate_incomplete_transition(self)
        _validate_confirmation(self)

    def to_dict(self) -> dict[str, Any]:
        """Return strict JSON-compatible coordination data."""
        return {
            "context": self.context.to_dict(),
            "policy": self.policy.to_dict(),
            "status": self.status.value,
            "owner": self.owner.value,
            "expected_next_actor": self.expected_next_actor.value,
            "round_number": self.round_number,
            "lease_renewed_at": self.lease_renewed_at,
            "reviewed_work_changed": self.reviewed_work_changed,
            "convergence_recommended": self.convergence_recommended,
            "no_progress_streak": self.no_progress_streak,
            "clarification_used": self.clarification_used,
            "incomplete_transition": (
                self.incomplete_transition.value
                if self.incomplete_transition is not None
                else None
            ),
            "transcript_entry_id": self.transcript_entry_id,
            "transcript_offset": self.transcript_offset,
            "escalation_reason": self.escalation_reason,
            "confirmation_label": self.confirmation_label,
            "confirmed_outcome": (
                self.confirmed_outcome.value if self.confirmed_outcome is not None else None
            ),
            "confirmation_timestamp": self.confirmation_timestamp,
            "human_guidance": self.human_guidance,
            "role_natures": self.role_natures.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> CoordinationRecord:
        """Construct coordination state from strict JSON-compatible data."""
        expected = {
            "context", "policy", "status", "owner", "expected_next_actor",
            "round_number", "lease_renewed_at", "reviewed_work_changed",
            "convergence_recommended", "no_progress_streak", "clarification_used",
            "incomplete_transition", "transcript_entry_id", "transcript_offset",
            "escalation_reason", "confirmation_label", "confirmed_outcome",
            "confirmation_timestamp", "human_guidance",
        }
        legacy = "role_natures" not in data
        if not legacy:
            expected.add("role_natures")
        strict_fields(data, expected, "coordination record")
        marker_value = data["incomplete_transition"]
        outcome_value = data["confirmed_outcome"]
        offset_value = data["transcript_offset"]
        offset = (
            None
            if offset_value is None
            else non_negative_integer(offset_value, "transcript offset")
        )
        clarification = data["clarification_used"]
        if not isinstance(clarification, bool):
            raise ReviewExchangeError("clarification-used flag must be boolean")
        return cls(
            context=ReviewContext.from_dict(
                mapping_value(data["context"], "coordination context"),
            ),
            policy=FamilyPolicy.from_dict(
                mapping_value(data["policy"], "coordination family policy"),
            ),
            status=enum_value(
                CoordinationStatus,
                data["status"],
                "coordination status",
            ),
            owner=enum_value(Actor, data["owner"], "owner"),
            expected_next_actor=enum_value(
                Actor,
                data["expected_next_actor"],
                "expected next actor",
            ),
            round_number=positive_integer(data["round_number"], "coordination round"),
            lease_renewed_at=optional_string(data["lease_renewed_at"], "lease timestamp"),
            reviewed_work_changed=optional_boolean(
                data["reviewed_work_changed"], "reviewed-work-changed",
            ),
            convergence_recommended=optional_boolean(
                data["convergence_recommended"], "convergence-recommended",
            ),
            no_progress_streak=non_negative_integer(
                data["no_progress_streak"], "no-progress streak",
            ),
            clarification_used=clarification,
            incomplete_transition=(
                None
                if marker_value is None
                else enum_value(
                    IncompleteTransitionKind,
                    marker_value,
                    "incomplete transition",
                )
            ),
            transcript_entry_id=optional_string(
                data["transcript_entry_id"], "transcript entry id",
            ),
            transcript_offset=offset,
            escalation_reason=optional_string(
                data["escalation_reason"], "escalation reason",
            ),
            confirmation_label=optional_string(
                data["confirmation_label"], "confirmation label",
            ),
            confirmed_outcome=(
                None
                if outcome_value is None
                else enum_value(
                    ConfirmationOutcome,
                    outcome_value,
                    "confirmation outcome",
                )
            ),
            confirmation_timestamp=optional_string(
                data["confirmation_timestamp"], "confirmation timestamp",
            ),
            human_guidance=optional_string(data["human_guidance"], "human guidance"),
            role_natures=RoleNatureSnapshot.from_optional_dict(
                None
                if legacy
                else mapping_value(
                    data["role_natures"],
                    "coordination role natures",
                ),
            ),
        )


# eof
