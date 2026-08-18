"""Stable transcript identities and restarted-exchange occurrence lookup."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tools.review_exchange_models import ReviewRole

if TYPE_CHECKING:
    from tools.review_exchange_models import ReviewContext
    from tools.review_exchange_store import ReviewExchangeStore


def transcript_entry_base(
    context: ReviewContext,
    role: ReviewRole,
    round_number: int,
) -> str:
    """Return one stable role identity scoped by code-review step when present."""
    prefix = "request" if role is ReviewRole.REQUESTOR else "answer"
    if context.implementation_step is not None:
        return f"{prefix}-step-{context.implementation_step}-round-{round_number}"
    return f"{prefix}-round-{round_number}"


def current_request_occurrence(
    store: ReviewExchangeStore,
    context: ReviewContext,
    round_number: int,
    *,
    before_offset: int | None = None,
) -> int:
    """Return the current restarted-exchange number from request entries."""
    base = transcript_entry_base(context, ReviewRole.REQUESTOR, round_number)
    next_occurrence = store.entry_occurrence(
        base,
        discriminator="exchange",
        before_offset=before_offset,
    )
    return max(1, next_occurrence - 1)


__all__ = ["current_request_occurrence", "transcript_entry_base"]


# eof
