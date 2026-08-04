"""Crash-recoverable exact-path persistence for review exchanges.

Step 2 centralizes complete UTF-8 replacement, identity validation, short
operating-system locks, request tombstones, evidence archives, and transcript
append repair from a persisted byte offset. It never discovers exchange files
by scanning directories or keeps a transition lock across counterpart work.
"""

# ruff: noqa: EM101, EM102, TRY003

from __future__ import annotations

import json
import os
import re
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass, replace
from pathlib import Path
from string import Template
from typing import TYPE_CHECKING, Final

from tools.review_exchange_models import (
    ArchiveKind,
    ArtifactPaths,
    IncompleteTransitionKind,
    ReviewContext,
    ReviewExchangeError,
    ReviewFamily,
    ReviewRole,
    mapping_value,
    validate_local_timestamp,
)
from tools.review_exchange_models_coordination import CoordinationRecord
from tools.review_exchange_models_envelope import parse_envelope_markdown
from tools.review_exchange_paths import archive_path

if TYPE_CHECKING:
    from collections.abc import Generator
    from typing import BinaryIO

if os.name == "nt":
    import msvcrt  # pragma: no cover - platform-specific import
else:
    import fcntl  # pragma: no cover - platform-specific import

_TEMPLATE_ROOT: Final[Path] = Path(__file__).resolve().parents[1] / "templates"
_ENTRY_ID_RE: Final[re.Pattern[str]] = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
_TRANSCRIPT_OUTCOMES: Final[frozenset[str]] = frozenset(
    {
        "request",
        "answer",
        "escalation",
        "human-confirmation",
        "human-resolution",
    },
)
_COORDINATION_OPEN: Final[str] = "```json\n"
_COORDINATION_CLOSE: Final[str] = "\n```\n"
_ENTRY_FOOTER_PREFIX: Final[str] = "<!-- review-entry-id:"
_ATOMIC_REPLACE_ATTEMPTS: Final[int] = 3


@dataclass(frozen=True)
class TranscriptEntry:
    """Complete current-round transcript content with a stable repair identity."""

    entry_id: str
    role: ReviewRole
    outcome: str
    recorded_at: str
    authored_content: str

    def __post_init__(self) -> None:
        """Reject ambiguous footer data and unsupported transcript outcomes."""
        if _ENTRY_ID_RE.fullmatch(self.entry_id) is None:
            raise ReviewExchangeError("invalid transcript entry identifier")
        if self.outcome not in _TRANSCRIPT_OUTCOMES:
            raise ReviewExchangeError(
                f"unsupported transcript outcome: {self.outcome}",
            )
        validate_local_timestamp(self.recorded_at)
        if _ENTRY_FOOTER_PREFIX in self.authored_content:
            raise ReviewExchangeError(
                "authored content contains reserved entry footer",
            )


class ReviewExchangeStore:
    """Persist one exchange safely through fixed, identity-checked paths.

    The store prepares complete files beside their targets before replacement,
    preserves consumed requests as tombstones, and repairs transcript appends
    only from the coordination record's byte offset. Atomic replacement also
    tolerates a bounded transient sharing denial before failing without losing
    the prepared file. Callers scope ``transition_lock`` around one
    state-changing transition and release it before waiting or authoring
    feedback.
    """

    def __init__(
        self,
        paths: ArtifactPaths,
        *,
        template_root: Path | None = None,
    ) -> None:
        """Bind persistence to one already-derived exact artifact set."""
        self.paths = paths
        self._template_root = (
            template_root.resolve() if template_root is not None else _TEMPLATE_ROOT
        )

    @contextmanager
    def transition_lock(self) -> Generator[None]:
        """Hold the identity-specific operating-system lock for one transition."""
        lock_path = self.paths.transition_lock
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        with lock_path.open("a+b") as stream:
            self._ensure_lock_byte(stream)
            self._lock_stream(stream)
            try:
                yield
            finally:
                self._unlock_stream(stream)

    def publish_atomic(self, path: Path, content: str) -> None:
        """Validate and atomically create or replace one exact artifact."""
        target = self._require_exact_path(path)
        self._validate_content(target, content)
        prepared = self._prepare_atomic(target, content.encode("utf-8"))
        try:
            self._commit_prepared(prepared, target)
        except OSError as error:
            raise ReviewExchangeError(f"atomic publication failed: {error}") from error
        finally:
            self._discard_prepared(prepared)

    def publish_request(self, content: str) -> None:
        """Remove a valid stale answer before publishing a complete request."""
        self._validate_envelope(content, ReviewRole.REQUESTOR)
        prepared = self._prepare_atomic(self.paths.request, content.encode("utf-8"))
        try:
            self.remove_exact(self.paths.answer)
            self._commit_prepared(prepared, self.paths.request)
        except OSError as error:
            raise ReviewExchangeError(f"request publication failed: {error}") from error
        finally:
            self._discard_prepared(prepared)

    def publish_answer(self, content: str) -> None:
        """Consume the exact request to a tombstone before exposing its answer."""
        self._validate_envelope(content, ReviewRole.REVIEWER)
        prepared = self._prepare_atomic(self.paths.answer, content.encode("utf-8"))
        try:
            self.consume_request_to_tombstone()
            self._commit_prepared(prepared, self.paths.answer)
        except OSError as error:
            raise ReviewExchangeError(f"answer publication failed: {error}") from error
        finally:
            self._discard_prepared(prepared)

    def consume_request_to_tombstone(self) -> None:
        """Atomically rename the validated request to its stable tombstone."""
        if not self.paths.request.is_file():
            raise ReviewExchangeError("matching review request does not exist")
        if self.paths.tombstone.exists():
            raise ReviewExchangeError("matching request tombstone already exists")
        self.read_artifact(self.paths.request)
        try:
            self.paths.request.replace(self.paths.tombstone)
        except OSError as error:
            raise ReviewExchangeError(f"request consumption failed: {error}") from error

    def read_artifact(self, path: Path) -> str:
        """Read and identity-check one exact request, answer, or tombstone."""
        target = self._require_exact_path(path)
        if target not in {
            self.paths.request,
            self.paths.answer,
            self.paths.tombstone,
        }:
            raise ReviewExchangeError("path is not a review-content artifact")
        try:
            content = target.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            raise ReviewExchangeError(f"cannot read review artifact: {error}") from error
        expected_role = (
            ReviewRole.REVIEWER
            if target == self.paths.answer
            else ReviewRole.REQUESTOR
        )
        self._validate_envelope(content, expected_role)
        return content

    def remove_exact(self, path: Path) -> bool:
        """Remove one matching transient after validating its identity."""
        target = self._require_exact_path(path)
        if not target.exists():
            return False
        if target in {self.paths.request, self.paths.answer, self.paths.tombstone}:
            self.read_artifact(target)
        elif target == self.paths.coordination:
            self.read_coordination(required=True)
        else:
            raise ReviewExchangeError("path is not an exact cleanup target")
        try:
            target.unlink()
        except OSError as error:
            raise ReviewExchangeError(f"exact cleanup failed: {error}") from error
        return True

    def initialize_transcript(self, context: ReviewContext) -> bool:
        """Initialize a missing family transcript and preserve an existing one."""
        self._validate_context(context)
        if self.paths.transcript.exists():
            if not self.paths.transcript.is_file():
                raise ReviewExchangeError("transcript path is not a file")
            return False
        template_name = (
            "review-code-transcript.template.md"
            if context.identity.family is ReviewFamily.CODE
            else "review-specification-transcript.template.md"
        )
        try:
            template = Template(
                (self._template_root / template_name).read_text(encoding="utf-8"),
            )
            content = template.substitute(
                version=context.identity.version,
                exchange_identity=context.identity.key,
                reviewed_document=context.document_path.as_posix(),
            )
        except (KeyError, OSError, UnicodeError) as error:
            raise ReviewExchangeError(f"cannot initialize transcript: {error}") from error
        prepared = self._prepare_atomic(self.paths.transcript, content.encode("utf-8"))
        try:
            if self.paths.transcript.exists():
                return False
            self._commit_prepared(prepared, self.paths.transcript)
        except OSError as error:
            raise ReviewExchangeError(f"transcript initialization failed: {error}") from error
        finally:
            self._discard_prepared(prepared)
        return True

    def write_coordination(self, record: CoordinationRecord) -> None:
        """Atomically persist a strict coordination record for this identity."""
        self._validate_context(record.context)
        payload = json.dumps(record.to_dict(), indent=2, sort_keys=True)
        self.publish_atomic(
            self.paths.coordination,
            f"{_COORDINATION_OPEN}{payload}{_COORDINATION_CLOSE}",
        )

    def read_coordination(
        self,
        *,
        required: bool = False,
    ) -> CoordinationRecord | None:
        """Read one exact coordination record without artifact discovery."""
        path = self.paths.coordination
        if not path.exists():
            if required:
                raise ReviewExchangeError("coordination record does not exist")
            return None
        try:
            content = path.read_text(encoding="utf-8")
            data = self._coordination_json(content)
            record = CoordinationRecord.from_dict(mapping_value(data, "coordination JSON"))
        except (OSError, UnicodeError) as error:
            raise ReviewExchangeError(f"cannot read coordination record: {error}") from error
        self._validate_context(record.context)
        return record

    def append_transcript_once(
        self,
        record: CoordinationRecord,
        *,
        transition: IncompleteTransitionKind,
        entry: TranscriptEntry,
    ) -> CoordinationRecord:
        """Append or repair one entry using only its persisted suffix offset."""
        self._validate_context(record.context)
        if not self.paths.transcript.is_file():
            raise ReviewExchangeError("transcript must be initialized before append")
        stored = self.read_coordination(required=True)
        if stored is None:
            raise ReviewExchangeError("coordination record does not exist")
        marked = self._ensure_transcript_marker(
            stored,
            record,
            transition,
            entry.entry_id,
        )
        offset = marked.transcript_offset
        if offset is None:
            raise ReviewExchangeError("transcript repair marker has no byte offset")
        rendered = self._render_transcript_entry(marked, entry).encode("utf-8")
        suffix = self._read_suffix(self.paths.transcript, offset)
        if suffix != rendered:
            self._truncate_transcript(offset)
            try:
                self._append_bytes(self.paths.transcript, rendered)
            except OSError as error:
                raise ReviewExchangeError(f"transcript append failed: {error}") from error
        cleared = replace(
            marked,
            incomplete_transition=None,
            transcript_entry_id=None,
            transcript_offset=None,
        )
        self.write_coordination(cleared)
        return cleared

    def archive_evidence(
        self,
        kind: ArchiveKind,
        compact_timestamp: str,
    ) -> Path:
        """Move one exact validated transient to its identity-scoped archive."""
        sources = {
            ArchiveKind.REQUEST: self.paths.request,
            ArchiveKind.ANSWER: self.paths.answer,
            ArchiveKind.CONSUMED: self.paths.tombstone,
            ArchiveKind.COORDINATION: self.paths.coordination,
        }
        source = sources[kind]
        if source == self.paths.coordination:
            self.read_coordination(required=True)
        else:
            self.read_artifact(source)
        destination = archive_path(self.paths, compact_timestamp, kind)
        if destination.exists():
            raise ReviewExchangeError(f"review archive already exists: {destination.name}")
        try:
            source.replace(destination)
        except OSError as error:
            raise ReviewExchangeError(f"evidence archive failed: {error}") from error
        return destination

    def _require_exact_path(self, path: Path) -> Path:
        """Reject any path outside this exchange's constant fixed set."""
        target = path.resolve()
        fixed = {candidate.resolve() for candidate in self.paths.fixed_paths}
        if target not in fixed:
            raise ReviewExchangeError("path is outside the exact artifact set")
        if target == self.paths.transition_lock.resolve():
            raise ReviewExchangeError("transition lock is not a content artifact")
        return target

    def _validate_content(self, target: Path, content: str) -> None:
        """Validate identity-bearing content according to its exact target."""
        if target == self.paths.transcript:
            raise ReviewExchangeError(
                "transcript is append-only: use transcript operations",
            )
        if target in {self.paths.request, self.paths.tombstone}:
            self._validate_envelope(content, ReviewRole.REQUESTOR)
        elif target == self.paths.answer:
            self._validate_envelope(content, ReviewRole.REVIEWER)
        elif target == self.paths.coordination:
            data = self._coordination_json(content)
            record = CoordinationRecord.from_dict(mapping_value(data, "coordination JSON"))
            self._validate_context(record.context)

    def _validate_envelope(self, content: str, expected_role: ReviewRole) -> None:
        """Verify artifact role and complete identity before any mutation."""
        envelope, _ = parse_envelope_markdown(content)
        if envelope.identity != self.paths.identity:
            raise ReviewExchangeError("artifact identity does not match exact path")
        if envelope.role is not expected_role:
            raise ReviewExchangeError(
                f"artifact role must be {expected_role.value}",
            )

    def _validate_context(self, context: ReviewContext) -> None:
        """Verify one context belongs to the store's exact path set."""
        if context.identity != self.paths.identity:
            raise ReviewExchangeError("coordination identity does not match exact paths")
        if context.document_path.parent != self.paths.transcript.parent:
            raise ReviewExchangeError("reviewed document differs from transcript parent")

    @staticmethod
    def _coordination_json(content: str) -> object:
        """Parse the coordination record's required first fenced JSON block."""
        if not content.startswith(_COORDINATION_OPEN):
            raise ReviewExchangeError("coordination record must start with fenced JSON")
        closing = content.find(_COORDINATION_CLOSE, len(_COORDINATION_OPEN))
        if closing < 0:
            raise ReviewExchangeError("coordination JSON fence is not closed")
        if content[closing + len(_COORDINATION_CLOSE) :].strip():
            raise ReviewExchangeError("coordination record has unexpected trailing content")
        payload = content[len(_COORDINATION_OPEN) : closing]
        try:
            return json.loads(payload)
        except json.JSONDecodeError as error:
            raise ReviewExchangeError(f"invalid coordination JSON: {error.msg}") from error

    def _ensure_transcript_marker(
        self,
        stored: CoordinationRecord,
        requested: CoordinationRecord,
        transition: IncompleteTransitionKind,
        entry_id: str,
    ) -> CoordinationRecord:
        """Persist or validate the marker that owns one append repair."""
        if stored.incomplete_transition is None:
            if stored != requested:
                raise ReviewExchangeError("stale coordination record for transcript append")
            offset = self.paths.transcript.stat().st_size
            marked = replace(
                stored,
                incomplete_transition=transition,
                transcript_entry_id=entry_id,
                transcript_offset=offset,
            )
            self.write_coordination(marked)
            return marked
        if (
            stored.incomplete_transition is not transition
            or stored.transcript_entry_id != entry_id
        ):
            raise ReviewExchangeError("another transcript repair is already pending")
        return stored

    @staticmethod
    def _render_transcript_entry(
        record: CoordinationRecord,
        entry: TranscriptEntry,
    ) -> str:
        """Render one complete role-and-round-labeled transcript entry."""
        context = record.context
        umbrella = (
            context.umbrella_path.as_posix()
            if context.umbrella_path is not None
            else "none"
        )
        lines = [
            "",
            f"## Round {record.round_number} by {entry.role.value}",
            "",
            f"- Recorded: {entry.recorded_at}",
            f"- Exchange: {context.identity.key}",
            f"- Umbrella: {umbrella}",
            f"- Reviewed document: {context.document_path.as_posix()}",
        ]
        if context.implementation_step is not None:
            lines.append(f"- Implementation step: {context.implementation_step}")
        lines.extend(
            [
                f"- Outcome: {entry.outcome}",
                "",
                entry.authored_content.rstrip("\n"),
                "",
            ],
        )
        lines.append(f"<!-- review-entry-id: {entry.entry_id} -->")
        return "\n".join(lines) + "\n"

    @staticmethod
    def _prepare_atomic(target: Path, content: bytes) -> Path:
        """Write and synchronize one same-directory temporary file."""
        target.parent.mkdir(parents=True, exist_ok=True)
        descriptor, name = tempfile.mkstemp(
            prefix=".review-exchange-",
            suffix=".tmp",
            dir=target.parent,
        )
        prepared = Path(name)
        try:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
        except OSError:
            prepared.unlink(missing_ok=True)
            raise
        return prepared

    @staticmethod
    def _commit_prepared(prepared: Path, target: Path) -> None:
        """Expose a prepared file with bounded transient-sharing retries."""
        for attempt in range(_ATOMIC_REPLACE_ATTEMPTS):
            try:
                prepared.replace(target)
            except PermissionError:
                if attempt + 1 == _ATOMIC_REPLACE_ATTEMPTS:
                    raise
            else:
                return

    @staticmethod
    def _discard_prepared(prepared: Path) -> None:
        """Remove an uncommitted temporary file after success or failure."""
        prepared.unlink(missing_ok=True)

    @staticmethod
    def _read_suffix(path: Path, offset: int) -> bytes:
        """Read only the current entry suffix from its persisted byte offset."""
        try:
            with path.open("rb") as stream:
                stream.seek(offset)
                return stream.read()
        except OSError as error:
            raise ReviewExchangeError(f"cannot read transcript suffix: {error}") from error

    def _truncate_transcript(self, offset: int) -> None:
        """Discard a torn current-entry suffix without loading prior history."""
        try:
            with self.paths.transcript.open("r+b") as stream:
                stream.truncate(offset)
                stream.flush()
                os.fsync(stream.fileno())
        except OSError as error:
            raise ReviewExchangeError(f"cannot truncate transcript suffix: {error}") from error

    @staticmethod
    def _append_bytes(path: Path, content: bytes) -> None:
        """Append and synchronize one already-rendered complete entry."""
        with path.open("ab") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())

    @staticmethod
    def _ensure_lock_byte(stream: BinaryIO) -> None:
        """Ensure Windows has one byte range available for locking."""
        stream.seek(0, os.SEEK_END)
        if stream.tell() == 0:
            stream.write(b"\0")
            stream.flush()
        stream.seek(0)

    @staticmethod
    def _lock_stream(stream: BinaryIO) -> None:
        """Acquire one blocking standard-library operating-system lock."""
        if os.name == "nt":
            msvcrt.locking(stream.fileno(), msvcrt.LK_LOCK, 1)
            return
        fcntl.flock(stream.fileno(), fcntl.LOCK_EX)

    @staticmethod
    def _unlock_stream(stream: BinaryIO) -> None:
        """Release the operating-system lock before closing its handle."""
        stream.seek(0)
        if os.name == "nt":
            msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            return
        fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


# eof
