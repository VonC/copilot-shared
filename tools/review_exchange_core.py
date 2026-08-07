"""Application lifecycle service for durable review exchanges.

Step 3 coordinates the Step 1 protocol models and Step 2 exact-path store. It
classifies every observable state, makes transcript-appending mutations
marker-first and repairable, bounds waits with injected monotonic time, and
persists escalation or human authorization without granting reviewers an
owning action.
"""

# ruff: noqa: EM101, EM102, PLR0913, TRY003

from __future__ import annotations

import time
from dataclasses import replace
from datetime import datetime
from typing import TYPE_CHECKING, Final

from tools.review_exchange_human import (
    ConfirmationDecision,
    ResolutionResult,
    ReviewExchangeHumanMixin,
)
from tools.review_exchange_models import (
    Actor,
    ArtifactState,
    CoordinationStatus,
    FamilyPolicy,
    IncompleteTransitionKind,
    ReviewConfiguration,
    ReviewContext,
    ReviewDisposition,
    ReviewExchangeError,
    ReviewRole,
)
from tools.review_exchange_models_coordination import CoordinationRecord
from tools.review_exchange_models_envelope import (
    Envelope,
    parse_envelope_markdown,
    validate_summary_identity,
)
from tools.review_exchange_observer import ExchangeObservation, ReviewExchangeObserver
from tools.review_exchange_store import ReviewExchangeStore, TranscriptEntry
from tools.review_exchange_wait import (
    WaitOutcome,
    WaitProgress,
    WaitResult,
    wait_for_exact,
)

if TYPE_CHECKING:
    from collections.abc import Callable

__all__ = [
    "ConfirmationDecision",
    "ResolutionResult",
    "ReviewExchangeCore",
    "WaitOutcome",
    "WaitProgress",
    "WaitResult",
]

_NO_PROGRESS_LIMIT: Final[int] = 2
_RECLAIMABLE_STATES: Final[frozenset[ArtifactState]] = frozenset(
    {
        ArtifactState.ABANDONED_REQUEST,
        ArtifactState.ABANDONED_ANSWER,
        ArtifactState.ABANDONED_MID_ROUND,
        ArtifactState.REQUEST_PENDING,
        ArtifactState.ANSWER_PENDING,
        ArtifactState.ROUND_IN_PROGRESS,
    },
)


class ReviewExchangeCore(ReviewExchangeHumanMixin):
    """Coordinate one identity through bounded, recoverable review rounds.

    The application service owns transition ordering and clocks while delegating
    all filesystem mechanics to ``ReviewExchangeStore`` and all pure shape
    decisions to ``review_exchange_state``. Locks cover only one transition;
    waits, reviewer work, and owning actions always occur outside them.
    """

    def __init__(
        self,
        store: ReviewExchangeStore,
        context: ReviewContext,
        policy: FamilyPolicy,
        configuration: ReviewConfiguration,
        *,
        wall_clock: Callable[[], datetime] | None = None,
        monotonic_clock: Callable[[], float] | None = None,
        sleeper: Callable[[float], None] | None = None,
    ) -> None:
        """Bind lifecycle behavior to one exact context and injectable time."""
        if store.paths.identity != context.identity:
            raise ReviewExchangeError("core context differs from store identity")
        if store.paths.transcript.parent != context.document_path.parent:
            raise ReviewExchangeError("core document differs from transcript parent")
        self.store = store
        self.context = context
        self.policy = policy
        self.configuration = configuration
        self._wall_clock = wall_clock or (lambda: datetime.now().astimezone())
        self._monotonic_clock = monotonic_clock or time.monotonic
        self._sleeper = sleeper or time.sleep
        self._observer = ReviewExchangeObserver(
            store,
            context,
            policy,
            configuration,
            self._current_wall_time,
        )

    def _current_wall_time(self) -> datetime:
        """Return injected wall time while preserving runtime clock replacement."""
        return self._wall_clock()

    def classify(self) -> ExchangeObservation:
        """Return one fail-closed state without mutating artifacts or leases."""
        return self._observer.classify()

    def start(self) -> CoordinationRecord:
        """Initialize a missing transcript and start exactly one active round."""
        if not self.configuration.enabled:
            raise ReviewExchangeError("review mode is disabled")
        with self.store.transition_lock():
            if self.classify().state is not ArtifactState.IDLE:
                raise ReviewExchangeError("review exchange is already active")
            self.store.initialize_transcript(self.context)
            record = CoordinationRecord(
                self.context,
                self.policy,
                CoordinationStatus.ACTIVE,
                Actor.REQUESTOR,
                Actor.REVIEWER,
                1,
                self._timestamp(),
            )
            self.store.write_coordination(record)
            return record

    def publish_request(
        self,
        markdown: str,
        transcript_content: str,
    ) -> CoordinationRecord:
        """Publish and append one validated current-round request idempotently."""
        with self.store.transition_lock():
            observation = self.classify()
            record = self._require_record(observation)
            repairing = record.incomplete_transition is (
                IncompleteTransitionKind.PUBLISH_REQUEST
            )
            if not repairing and observation.state is not ArtifactState.ROUND_IN_PROGRESS:
                raise ReviewExchangeError("request publication requires a round in progress")
            envelope, authored = self._validate_envelope(markdown, ReviewRole.REQUESTOR, record)
            validate_summary_identity(authored, self.context, record.round_number)
            if record.human_guidance is not None:
                expected_guidance = f"Human guidance: {record.human_guidance}"
                if expected_guidance not in authored:
                    raise ReviewExchangeError(
                        "replacement request summary omits confirmed human guidance",
                    )
            entry = TranscriptEntry(
                f"request-round-{record.round_number}",
                ReviewRole.REQUESTOR,
                "request",
                envelope.created_at,
                transcript_content,
            )
            marked = self._mark_transition(
                record,
                IncompleteTransitionKind.PUBLISH_REQUEST,
                entry.entry_id,
            )
            self.store.publish_request(markdown)
            marked = self.store.append_transcript_once(
                marked,
                transition=IncompleteTransitionKind.PUBLISH_REQUEST,
                entry=entry,
                clear_marker=False,
            )
            final = replace(
                marked,
                owner=Actor.REQUESTOR,
                expected_next_actor=Actor.REVIEWER,
                lease_renewed_at=self._timestamp(),
                incomplete_transition=None,
                transcript_entry_id=None,
                transcript_offset=None,
                human_guidance=None,
            )
            self.store.write_coordination(final)
            return final

    def publish_answer(
        self,
        markdown: str,
        transcript_content: str,
    ) -> CoordinationRecord:
        """Consume, publish, append, and route one reviewer answer safely."""
        with self.store.transition_lock():
            observation = self.classify()
            record = self._require_record(observation)
            repairing = record.incomplete_transition is (
                IncompleteTransitionKind.PUBLISH_ANSWER
            )
            if not repairing and observation.state is not ArtifactState.REQUEST_PENDING:
                raise ReviewExchangeError("answer publication requires a request pending")
            envelope, _ = self._validate_envelope(markdown, ReviewRole.REVIEWER, record)
            entry = TranscriptEntry(
                f"answer-round-{record.round_number}",
                ReviewRole.REVIEWER,
                "answer",
                envelope.created_at,
                transcript_content,
            )
            marked = self._mark_transition(
                record,
                IncompleteTransitionKind.PUBLISH_ANSWER,
                entry.entry_id,
            )
            self._publish_or_repair_answer(markdown)
            marked = self.store.append_transcript_once(
                marked,
                transition=IncompleteTransitionKind.PUBLISH_ANSWER,
                entry=entry,
                clear_marker=False,
            )
            self.store.remove_exact(self.store.paths.tombstone)
            convergence = envelope.disposition is ReviewDisposition.CONVERGENCE_RECOMMENDED
            final = replace(
                marked,
                status=(
                    CoordinationStatus.AWAITING_HUMAN_CONFIRMATION
                    if convergence
                    else CoordinationStatus.ACTIVE
                ),
                owner=Actor.REVIEWER,
                expected_next_actor=Actor.HUMAN if convergence else Actor.REQUESTOR,
                lease_renewed_at=None if convergence else self._timestamp(),
                convergence_recommended=convergence,
                incomplete_transition=None,
                transcript_entry_id=None,
                transcript_offset=None,
            )
            self.store.write_coordination(final)
            return final

    def consume_answer(
        self,
        *,
        reviewed_work_changed: bool,
        disagreement: bool = False,
    ) -> CoordinationRecord:
        """Record requestor assessment and consume only an intermediate answer."""
        with self.store.transition_lock():
            observation = self.classify()
            record = self._require_record(observation)
            if observation.state is ArtifactState.CONVERGENCE_GATE:
                return self._restore_convergence_gate(record, observation.answer_envelope)
            if observation.state is not ArtifactState.ANSWER_PENDING:
                raise ReviewExchangeError("answer consumption requires an answer pending")
            answer = observation.answer_envelope
            if answer is None or answer.disposition is not ReviewDisposition.CHANGES_REQUESTED:
                raise ReviewExchangeError("answer pending state lacks a change request")
            clarification_used = record.clarification_used
            if disagreement:
                if clarification_used:
                    return self._escalate_locked(
                        "review disagreement remained after the clarification round",
                        ReviewRole.REQUESTOR,
                    )
                clarification_used = True
            streak = 0 if reviewed_work_changed else record.no_progress_streak + 1
            if streak >= _NO_PROGRESS_LIMIT:
                return self._escalate_locked(
                    "two consecutive change-request rounds made no meaningful progress",
                    ReviewRole.REQUESTOR,
                )
            self.store.remove_exact(self.store.paths.answer)
            updated = replace(
                record,
                owner=Actor.REQUESTOR,
                expected_next_actor=Actor.REQUESTOR,
                lease_renewed_at=self._timestamp(),
                reviewed_work_changed=reviewed_work_changed,
                no_progress_streak=streak,
                clarification_used=clarification_used,
                convergence_recommended=False,
            )
            self.store.write_coordination(updated)
            return updated

    def reclaim(self) -> CoordinationRecord:
        """Renew one expired lease in place for an intact, unescalated round.

        Reclaiming restores the live counterpart state of an abandoned round
        without touching any artifact or transcript content. It is idempotent
        while the round stays live and never applies to an escalated,
        confirming, interrupted, or inconsistent exchange.
        """
        with self.store.transition_lock():
            observation = self.classify()
            record = self._require_record(observation)
            if observation.state not in _RECLAIMABLE_STATES:
                raise ReviewExchangeError(
                    "reclaim requires an intact abandoned or live round",
                )
            updated = replace(record, lease_renewed_at=self._timestamp())
            self.store.write_coordination(updated)
            return updated

    def continue_round(self) -> CoordinationRecord:
        """Advance one completed intermediate assessment to its next round."""
        with self.store.transition_lock():
            observation = self.classify()
            record = self._require_record(observation)
            if (
                observation.state is not ArtifactState.ROUND_IN_PROGRESS
                or record.reviewed_work_changed is None
            ):
                raise ReviewExchangeError(
                    "continuation requires a completed answer assessment",
                )
            updated = replace(
                record,
                owner=Actor.REQUESTOR,
                expected_next_actor=Actor.REVIEWER,
                round_number=record.round_number + 1,
                lease_renewed_at=self._timestamp(),
                reviewed_work_changed=None,
                convergence_recommended=None,
            )
            self.store.write_coordination(updated)
            return updated

    def wait_for_exact(
        self,
        expected: ArtifactState,
        *,
        timeout_seconds: int | None = None,
        poll_interval: float = 1.0,
        progress_interval: float = 30.0,
        progress_callback: Callable[[WaitProgress], None] | None = None,
    ) -> WaitResult:
        """Poll one derived counterpart state against one monotonic deadline."""
        limit = timeout_seconds or self.configuration.wait_timeout_seconds
        return wait_for_exact(
            expected,
            timeout_seconds=limit,
            poll_interval=poll_interval,
            progress_interval=progress_interval,
            progress_callback=progress_callback,
            monotonic_clock=self._monotonic_clock,
            sleeper=self._sleeper,
            observe=self.classify,
            escalate=self._observation_after_escalation,
        )

    def escalate(
        self,
        reason: str,
        role: ReviewRole = ReviewRole.HUMAN,
    ) -> CoordinationRecord:
        """Persist and append one idempotent evidence-preserving escalation."""
        with self.store.transition_lock():
            return self._escalate_locked(reason, role)

    def _validate_envelope(
        self,
        markdown: str,
        role: ReviewRole,
        record: CoordinationRecord,
    ) -> tuple[Envelope, str]:
        """Validate exact context, role, and current round before mutation."""
        envelope, authored = parse_envelope_markdown(markdown)
        if envelope.role is not role:
            raise ReviewExchangeError(f"artifact role must be {role.value}")
        if (
            envelope.identity != self.context.identity
            or envelope.document_path != self.context.document_path
            or envelope.umbrella_path != self.context.umbrella_path
            or envelope.implementation_step != self.context.implementation_step
        ):
            raise ReviewExchangeError("artifact envelope differs from review context")
        if envelope.round_number != record.round_number:
            raise ReviewExchangeError("artifact round differs from coordination round")
        return envelope, authored

    def _timestamp(self) -> str:
        """Return injected local wall time with a numeric UTC offset."""
        return self._wall_clock().astimezone().isoformat(timespec="seconds")

    def _require_record(self, observation: ExchangeObservation) -> CoordinationRecord:
        """Return current coordination or reject an unauthoritative shape."""
        if observation.record is None:
            raise ReviewExchangeError("operation requires durable coordination")
        return observation.record

    def _mark_transition(
        self,
        record: CoordinationRecord,
        transition: IncompleteTransitionKind,
        entry_id: str,
    ) -> CoordinationRecord:
        """Persist a pre-append byte offset before the transition's first mutation."""
        self.store.initialize_transcript(self.context)
        if record.incomplete_transition is not None:
            if (
                record.incomplete_transition is not transition
                or record.transcript_entry_id != entry_id
            ):
                raise ReviewExchangeError("another transcript repair is already pending")
            return record
        marked = replace(
            record,
            incomplete_transition=transition,
            transcript_entry_id=entry_id,
            transcript_offset=self.store.paths.transcript.stat().st_size,
        )
        self.store.write_coordination(marked)
        return marked

    def _publish_or_repair_answer(self, markdown: str) -> None:
        """Resume answer publication from request, tombstone, or visible answer."""
        request = self.store.paths.request
        answer = self.store.paths.answer
        tombstone = self.store.paths.tombstone
        if request.is_file() and not answer.exists() and not tombstone.exists():
            self.store.publish_answer(markdown)
            return
        if tombstone.is_file():
            if answer.is_file():
                if self.store.read_artifact(answer) != markdown:
                    raise ReviewExchangeError("visible answer differs from repair content")
                return
            self.store.publish_atomic(answer, markdown)
            return
        if answer.is_file() and not request.exists():
            if self.store.read_artifact(answer) != markdown:
                raise ReviewExchangeError("visible answer differs from repair content")
            return
        raise ReviewExchangeError("answer repair has no authoritative request evidence")

    def _restore_convergence_gate(
        self,
        record: CoordinationRecord,
        envelope: Envelope | None,
    ) -> CoordinationRecord:
        """Use the retained answer's disposition to repair missing gate state."""
        if envelope is None or envelope.disposition is not (
            ReviewDisposition.CONVERGENCE_RECOMMENDED
        ):
            raise ReviewExchangeError("convergence gate lacks an authoritative answer")
        if record.status is CoordinationStatus.AWAITING_HUMAN_CONFIRMATION:
            return record
        repaired = replace(
            record,
            status=CoordinationStatus.AWAITING_HUMAN_CONFIRMATION,
            owner=Actor.REVIEWER,
            expected_next_actor=Actor.HUMAN,
            lease_renewed_at=None,
            convergence_recommended=True,
        )
        self.store.write_coordination(repaired)
        return repaired

    def _escalate_locked(
        self,
        reason: str,
        role: ReviewRole,
    ) -> CoordinationRecord:
        """Perform one marker-first escalation while the caller holds the lock."""
        if not reason.strip():
            raise ReviewExchangeError("escalation reason must be non-empty")
        observation = self.classify()
        record = observation.record
        if (
            record is not None
            and record.status is CoordinationStatus.ESCALATED
            and record.incomplete_transition is None
        ):
            return record
        if record is None:
            self.store.initialize_transcript(self.context)
            record = CoordinationRecord(
                self.context,
                self.policy,
                CoordinationStatus.ACTIVE,
                Actor.REQUESTOR,
                Actor.HUMAN,
                self._orphan_round(observation),
                self._timestamp(),
            )
            self.store.write_coordination(record)
        entry_id = f"escalation-round-{record.round_number}"
        marked = self._mark_transition(
            record,
            IncompleteTransitionKind.ESCALATION,
            entry_id,
        )
        if marked.status is not CoordinationStatus.ESCALATED:
            marked = replace(
                marked,
                status=CoordinationStatus.ESCALATED,
                expected_next_actor=Actor.HUMAN,
                lease_renewed_at=None,
                escalation_reason=reason.strip(),
            )
            self.store.write_coordination(marked)
        elif marked.escalation_reason != reason.strip():
            raise ReviewExchangeError("pending escalation has a different reason")
        entry = TranscriptEntry(
            entry_id,
            role,
            "escalation",
            self._timestamp(),
            reason.strip(),
        )
        marked = self.store.append_transcript_once(
            marked,
            transition=IncompleteTransitionKind.ESCALATION,
            entry=entry,
            clear_marker=False,
        )
        final = self._clear_marker(marked)
        self.store.write_coordination(final)
        return final

    def _clear_marker(self, record: CoordinationRecord) -> CoordinationRecord:
        """Clear one fully completed transcript repair marker in memory."""
        return replace(
            record,
            incomplete_transition=None,
            transcript_entry_id=None,
            transcript_offset=None,
        )

    def _observation_after_escalation(self, reason: str) -> ExchangeObservation:
        """Record one escalation and return its resulting observable state."""
        self.escalate(reason)
        return self.classify()

    @staticmethod
    def _orphan_round(observation: ExchangeObservation) -> int:
        """Recover a conservative round number from valid orphan envelopes."""
        rounds = [
            envelope.round_number
            for envelope in (observation.request_envelope, observation.answer_envelope)
            if envelope is not None
        ]
        return max(rounds, default=1)


# eof
