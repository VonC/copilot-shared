"""Small physical-state boundary contracts for artifact migration."""

# ruff: noqa: SLF001

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tools.review_artifact_configuration import ReviewArtifactConfiguration
from tools.review_artifact_migration import MigrationMove, ReviewArtifactMigration
from tools.review_exchange_models import ReviewExchangeError

if TYPE_CHECKING:
    from pathlib import Path


def _service(root: Path) -> ReviewArtifactMigration:
    """Build migration with deterministic positive ignore verification."""
    configuration = ReviewArtifactConfiguration.load(root)
    return ReviewArtifactMigration(
        project_root=root,
        load_configuration=lambda: configuration,
        ignore_checker=lambda _home, _paths: True,
    )


def test_rollback_handles_duplicates_noops_and_ambiguous_paths(tmp_path: Path) -> None:
    """Rollback ignores duplicate/no-op entries and rejects ambiguous physical state."""
    service = _service(tmp_path)
    journal = tmp_path / "journal"
    journal.write_bytes(b"journal")
    source = tmp_path / "source"
    target = tmp_path / "target"
    duplicate = MigrationMove(source, target, "unused", duplicate=True)
    service._rollback((duplicate,), journal)
    assert not journal.exists()

    journal.write_bytes(b"journal")
    service._rollback((), journal)
    assert not journal.exists()

    source.write_bytes(b"source")
    target.write_bytes(b"target")
    ambiguous = MigrationMove(source, target, service._fingerprint(source))
    with pytest.raises(OSError, match="ambiguous"):
        service._rollback((ambiguous,), journal)


def test_existing_migration_lock_blocks_a_second_writer(tmp_path: Path) -> None:
    """Exclusive repository locking rejects concurrent migration writers."""
    (tmp_path / "a.review-requested.plan.v0.11.0.topic.md").write_bytes(b"request")
    lock = tmp_path / "review-artifact-migration.lock"
    lock.write_bytes(b"locked")

    with pytest.raises(ReviewExchangeError, match="already running"):
        _service(tmp_path).migrate()


# eof
