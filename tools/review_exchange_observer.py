"""Read-only exact-path observation adapter for review exchanges.

Step 3 keeps filesystem reads and lease-time evaluation outside the pure state
table. The adapter validates all live evidence for one bound context and
policy, then delegates the resulting fixed-path snapshot for classification.
"""


from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from tools.review_exchange_models import (
    ArtifactState,
    FamilyPolicy,
    ReviewConfiguration,
    ReviewContext,
    ReviewExchangeError,
)
from tools.review_exchange_models_envelope import Envelope, parse_envelope_markdown
from tools.review_exchange_state import ArtifactSnapshot, classify_snapshot

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from tools.review_exchange_models_coordination import CoordinationRecord
    from tools.review_exchange_store import ReviewExchangeStore


@dataclass(frozen=True)
class ExchangeObservation:
    """Complete observable state and parsed current-round evidence."""

    state: ArtifactState
    record: CoordinationRecord | None
    request_envelope: Envelope | None
    answer_envelope: Envelope | None
    diagnostic: str


class ReviewExchangeObserver:
    """Observe one identity without mutating artifacts or renewing its lease."""

    def __init__(
        self,
        store: ReviewExchangeStore,
        context: ReviewContext,
        policy: FamilyPolicy,
        configuration: ReviewConfiguration,
        wall_clock: Callable[[], datetime],
    ) -> None:
        """Bind exact paths, immutable context, policy, and injected wall time."""
        self._store = store
        self._context = context
        self._policy = policy
        self._configuration = configuration
        self._wall_clock = wall_clock

    def classify(self) -> ExchangeObservation:
        """Validate one snapshot and map it through the pure state table."""
        snapshot = self._snapshot()
        decision = classify_snapshot(snapshot, self._lease_is_current)
        return ExchangeObservation(
            decision.state,
            snapshot.record,
            snapshot.request_envelope,
            snapshot.answer_envelope,
            decision.diagnostic,
        )

    def _snapshot(self) -> ArtifactSnapshot:
        """Read only this identity's fixed paths and validate all live evidence."""
        errors: list[str] = []
        request = self._read_envelope(self._store.paths.request, errors)
        answer = self._read_envelope(self._store.paths.answer, errors)
        tombstone = self._read_envelope(self._store.paths.tombstone, errors)
        record: CoordinationRecord | None = None
        if self._store.paths.coordination.exists():
            try:
                record = self._store.read_coordination(required=True)
            except ReviewExchangeError as error:
                errors.append(str(error))
        if record is not None:
            if record.context != self._context:
                errors.append("coordination context differs from core context")
            if record.policy != self._policy:
                errors.append("coordination family policy differs from registered policy")
            for label, envelope in (
                ("request", request),
                ("answer", answer),
                ("tombstone", tombstone),
            ):
                if envelope is not None and envelope.round_number != record.round_number:
                    errors.append(f"{label} round differs from coordination round")
        return ArtifactSnapshot(
            self._store.paths.request.exists(),
            self._store.paths.answer.exists(),
            self._store.paths.tombstone.exists(),
            request,
            answer,
            tombstone,
            record,
            tuple(errors),
        )

    def _read_envelope(self, path: Path, errors: list[str]) -> Envelope | None:
        """Read and context-check one present exact artifact without mutation."""
        if not path.exists():
            return None
        try:
            content = self._store.read_artifact(path)
            envelope, _ = parse_envelope_markdown(content)
        except ReviewExchangeError as error:
            errors.append(str(error))
            return None
        if (
            envelope.document_path != self._context.document_path
            or envelope.umbrella_path != self._context.umbrella_path
            or envelope.implementation_step != self._context.implementation_step
        ):
            errors.append("artifact context differs from core context")
            return None
        return envelope

    def _lease_is_current(self, record: CoordinationRecord) -> bool:
        """Evaluate one persisted renewal timestamp against current local time."""
        if record.lease_renewed_at is None:
            return False
        renewed = datetime.fromisoformat(record.lease_renewed_at)
        expires = renewed + timedelta(
            seconds=self._configuration.wait_timeout_seconds,
        )
        return self._wall_clock() < expires


# eof
