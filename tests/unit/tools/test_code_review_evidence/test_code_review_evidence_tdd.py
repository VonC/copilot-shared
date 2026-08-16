"""TDD contracts for executable code-review repository evidence."""

from __future__ import annotations

import subprocess
from dataclasses import replace
from pathlib import Path

import pytest

from tools import code_review_evidence as evidence
from tools.review_exchange_models import ReviewExchangeError

# ruff: noqa: FBT001, FBT002, S603, S607
# pyright: reportPrivateUsage=false


def _git(root: Path, *arguments: str) -> str:
    """Run one bounded Git command in a temporary repository."""
    result = subprocess.run(
        ["git", *arguments],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
        timeout=10,
    )
    return result.stdout.strip()


@pytest.fixture(scope="module")
def staged_repository(
    tmp_path_factory: pytest.TempPathFactory,
) -> tuple[str, str, str, str]:
    """Build real staged Git evidence outside the measured test call."""
    root = tmp_path_factory.mktemp("code-review-evidence")
    _git(root, "init", "-q")
    tracked = root / "tracked.txt"
    tracked.write_text("staged\n", encoding="utf-8")
    _git(root, "add", "tracked.txt")
    captured = evidence.capture_index_tree(root)
    expected = _git(root, "write-tree")
    tracked.write_text("unstaged\n", encoding="utf-8")
    after_unstaged = evidence.capture_index_tree(root)
    _git(root, "add", "tracked.txt")
    after_staged = evidence.capture_index_tree(root)
    return captured, expected, after_unstaged, after_staged


def test_capture_index_tree_uses_the_index_without_inspecting_worktree(
    staged_repository: tuple[str, str, str, str],
) -> None:
    """Unstaged bytes do not change the captured Git tree object."""
    captured, expected, after_unstaged, after_staged = staged_repository
    assert captured == expected
    assert after_unstaged == captured
    assert after_staged != captured


def test_capture_index_tree_rejects_non_repository_and_malformed_git_output(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Repository and object-identity failures remain explicit."""
    with pytest.raises(ReviewExchangeError, match="repository is not a directory"):
        evidence.capture_index_tree(tmp_path / "missing")
    with pytest.raises(ReviewExchangeError, match="capture Git index tree"):
        evidence.capture_index_tree(tmp_path)

    completed = subprocess.CompletedProcess(["git", "write-tree"], 0, "not-a-tree\n", "")
    def fake_run(_arguments: object, **_kwargs: object) -> subprocess.CompletedProcess[str]:
        """Return malformed output through the typed Git seam."""
        return completed

    monkeypatch.setattr(evidence, "run_cross_platform_git_command", fake_run)
    with pytest.raises(ReviewExchangeError, match="malformed tree object"):
        evidence.capture_index_tree(tmp_path)


def test_recorded_blobs_attribute_reviewer_changes_and_protect_writer_deletions(
    tmp_path: Path,
) -> None:
    """Blob baselines distinguish edits, creations, and writer deletions."""
    _git(tmp_path, "init", "-q")
    tracked = tmp_path / "tracked.txt"
    tracked.write_text("writer baseline\n", encoding="utf-8")
    _git(tmp_path, "add", "tracked.txt")

    baseline = evidence.record_pre_repair_blob(tmp_path, "tracked.txt")
    tracked.write_text("reviewer repair\n", encoding="utf-8")
    repair = evidence.attribute_reviewer_patch(tmp_path, baseline)
    assert repair.attributable is True
    assert repair.path == "tracked.txt"
    assert "reviewer repair" in repair.patch

    created = evidence.record_pre_repair_blob(tmp_path, "created.txt")
    (tmp_path / "created.txt").write_text("reviewer created\n", encoding="utf-8")
    creation = evidence.attribute_reviewer_patch(tmp_path, created)
    assert creation.attributable is True
    assert creation.created is True

    tracked.unlink()
    deleted = evidence.record_pre_repair_blob(tmp_path, "tracked.txt")
    deletion = evidence.attribute_reviewer_patch(tmp_path, deleted)
    assert deleted.writer_deleted is True
    assert deletion.attributable is False
    assert "writer-deleted" in deletion.reason


def test_umbrella_digest_and_validation_state_classify_command_artifacts(
    tmp_path: Path,
) -> None:
    """Ignored output is accepted while tracked-file mutation is reported."""
    _git(tmp_path, "init", "-q")
    (tmp_path / ".gitignore").write_text(".cache/\n", encoding="utf-8")
    tracked = tmp_path / "tracked.txt"
    tracked.write_text("before\n", encoding="utf-8")
    _git(tmp_path, "add", ".gitignore", "tracked.txt")

    umbrella = evidence.capture_umbrella_digest(tracked)
    assert umbrella.applicable is True
    assert evidence.compare_umbrella_digest(umbrella, tracked).changed is False
    tracked.write_text("after\n", encoding="utf-8")
    assert evidence.compare_umbrella_digest(umbrella, tracked).changed is True
    assert evidence.capture_umbrella_digest(None).applicable is False

    tracked.write_text("before\n", encoding="utf-8")
    before = evidence.capture_validation_state(tmp_path)
    cache = tmp_path / ".cache"
    cache.mkdir()
    (cache / "coverage.json").write_text("{}\n", encoding="utf-8")
    after_ignored = evidence.capture_validation_state(tmp_path)
    ignored = evidence.compare_validation_state(before, after_ignored)
    assert ignored.acceptable is True
    assert ignored.ignored_paths == (".cache/coverage.json",)

    tracked.write_text("command changed tracked content\n", encoding="utf-8")
    after_tracked = evidence.capture_validation_state(tmp_path)
    tracked_change = evidence.compare_validation_state(after_ignored, after_tracked)
    assert tracked_change.acceptable is False
    assert tracked_change.tracked_paths == ("tracked.txt",)


def test_manifest_round_trip_uses_stable_identity_and_rejects_drift(
    tmp_path: Path,
) -> None:
    """Retained evidence round-trips at one identity-derived ignored path."""
    _git(tmp_path, "init", "-q")
    (tmp_path / ".gitignore").write_text("a.*\n", encoding="utf-8")
    tracked = tmp_path / "tracked.txt"
    tracked.write_text("baseline\n", encoding="utf-8")
    _git(tmp_path, "add", ".gitignore", "tracked.txt")
    tree = evidence.capture_index_tree(tmp_path)
    recorded = evidence.record_pre_repair_blob(tmp_path, "tracked.txt")
    state = evidence.capture_validation_state(tmp_path)
    retained = evidence.CodeReviewEvidence(
        family="code",
        type_token="code",  # noqa: S106 - protocol type token, not a credential
        version="v0.11.0",
        slug="code-reviewer",
        implementation_step="2",
        baseline_index_tree=tree,
        assessed_index_tree=tree,
        recorded_blobs=(recorded,),
        repair_paths=("tracked.txt",),
        validation_before=state,
        validation_after=state,
    )

    path = evidence.write_manifest(tmp_path, retained)
    assert path.name == "a.code-review-evidence.v0.11.0.code-reviewer.step-2.json"
    assert evidence.read_manifest(tmp_path, retained.identity) == retained
    drifted_identity = (*retained.identity[:-1], "3")
    evidence.manifest_path(tmp_path, drifted_identity).write_text(
        path.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    with pytest.raises(ReviewExchangeError, match="identity disagrees"):
        evidence.read_manifest(tmp_path, drifted_identity)
    assert evidence.retire_manifest(tmp_path, retained.identity) is True
    assert evidence.retire_manifest(tmp_path, retained.identity) is False


def _retained_payload(tree: str) -> dict[str, object]:
    """Return one minimal valid retained-evidence payload."""
    return {
        "schema_version": 1,
        "identity": {
            "family": "code",
            "type_token": "code",
            "version": "v0.11.0",
            "slug": "code-reviewer",
            "implementation_step": "2",
        },
        "baseline_index_tree": tree,
        "assessed_index_tree": tree,
        "recorded_blobs": [],
        "repair_paths": [],
        "validation_before": None,
        "validation_after": None,
    }


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ("not-an-object", "must be an object"),
        ({"path": "", "object_id": None}, "path is invalid"),
        ({"path": "x", "object_id": "bad"}, "object is invalid"),
        (
            {"path": "x", "object_id": None, "writer_deleted": "yes"},
            "deletion flag is invalid",
        ),
    ],
)
def test_recorded_blob_payload_rejects_malformed_values(
    payload: object,
    message: str,
) -> None:
    """Retained blob fields fail at their typed boundary."""
    with pytest.raises(ReviewExchangeError, match=message):
        evidence.RecordedBlob.from_payload(payload)


def test_evidence_operations_reject_unsafe_and_unattributable_paths(
    tmp_path: Path,
) -> None:
    """Exact-path operations reject escapes, directories, absence, and binary text."""
    _git(tmp_path, "init", "-q")
    with pytest.raises(ReviewExchangeError, match="repository-relative"):
        evidence.record_pre_repair_blob(tmp_path, tmp_path / "absolute.txt")
    with pytest.raises(ReviewExchangeError, match="name a file"):
        evidence.record_pre_repair_blob(tmp_path, ".")
    directory = tmp_path / "directory"
    directory.mkdir()
    with pytest.raises(ReviewExchangeError, match="must be a file"):
        evidence.record_pre_repair_blob(tmp_path, "directory")

    absent = evidence.RecordedBlob("absent.txt", None)
    missing = evidence.attribute_reviewer_patch(tmp_path, absent)
    assert missing.attributable is False
    assert "absent" in missing.reason

    binary = tmp_path / "binary.txt"
    binary.write_bytes(b"\xff")
    with pytest.raises(ReviewExchangeError, match="UTF-8"):
        evidence.attribute_reviewer_patch(
            tmp_path,
            evidence.RecordedBlob("binary.txt", None),
        )


def test_git_evidence_errors_and_malformed_hash_are_explicit(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Git launch and object-shape failures never become empty evidence."""
    _git(tmp_path, "init", "-q")
    tracked = tmp_path / "tracked.txt"
    tracked.write_text("content\n", encoding="utf-8")

    def fail_git(*_args: object, **_kwargs: object) -> object:
        message = "git unavailable"
        raise OSError(message)

    monkeypatch.setattr(evidence, "run_cross_platform_git_command", fail_git)
    with pytest.raises(ReviewExchangeError, match="Git evidence command failed"):
        evidence.record_pre_repair_blob(tmp_path, "tracked.txt")

    calls = 0

    def malformed_hash(
        _arguments: object,
        **_kwargs: object,
    ) -> subprocess.CompletedProcess[str]:
        nonlocal calls
        calls += 1
        output = "" if calls == 1 else "not-an-object\n"
        return subprocess.CompletedProcess(["git"], 0, output, "")

    monkeypatch.setattr(evidence, "run_cross_platform_git_command", malformed_hash)
    with pytest.raises(ReviewExchangeError, match="malformed pre-repair blob"):
        evidence.record_pre_repair_blob(tmp_path, "tracked.txt")


def test_umbrella_and_validation_payload_failures_are_typed(tmp_path: Path) -> None:
    """Digest and validation snapshots reject malformed and inconsistent inputs."""
    with pytest.raises(ReviewExchangeError, match="umbrella document"):
        evidence.capture_umbrella_digest(tmp_path / "missing.md")
    with pytest.raises(ReviewExchangeError, match="applicability changed"):
        evidence.compare_umbrella_digest(
            evidence.UmbrellaDigest(applicable=False),
            __file__,
        )
    assert evidence.UmbrellaDigest.from_payload(
        {"applicable": True, "digest": "abc"},
    ).digest == "abc"
    with pytest.raises(ReviewExchangeError, match="applicability"):
        evidence.UmbrellaDigest.from_payload({"applicable": "yes", "digest": None})
    with pytest.raises(ReviewExchangeError, match="value"):
        evidence.UmbrellaDigest.from_payload({"applicable": True, "digest": 3})

    with pytest.raises(ReviewExchangeError, match="file digest value"):
        evidence.FileDigest.from_payload({"path": "x", "digest": 3})
    with pytest.raises(ReviewExchangeError, match="index tree"):
        evidence.ValidationState.from_payload({"index_tree": "bad"})
    with pytest.raises(ReviewExchangeError, match="tracked_files"):
        evidence.ValidationState.from_payload(
            {
                "index_tree": "0" * 40,
                "tracked_files": "bad",
                "ignored_files": [],
                "untracked_files": [],
            },
        )

    empty = evidence.ValidationState("0" * 40, (), (), ())
    changed = replace(empty, index_tree="1" * 40)
    comparison = evidence.compare_validation_state(empty, changed)
    assert comparison.tracked_paths == ("<index>",)
    assert comparison.to_payload()["acceptable"] is False
    umbrella_comparison = evidence.UmbrellaComparison(
        applicable=True,
        changed=False,
        before="a",
        after="a",
    )
    assert umbrella_comparison.to_payload()["changed"] is False
    repair = evidence.RepairAttribution("x", "patch", attributable=True)
    assert repair.to_payload()["attributable"] is True


def test_manifest_payload_and_io_failures_are_explicit(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Manifest schema, identity, ignore, write, and retirement errors are reported."""
    _git(tmp_path, "init", "-q")
    tree = "0" * 40
    payload = _retained_payload(tree)
    invalid_payloads = (
        ({**payload, "schema_version": 2}, "schema"),
        ({**payload, "baseline_index_tree": "bad"}, "tree identity"),
        ({**payload, "recorded_blobs": "bad"}, "repair evidence"),
        ({**payload, "repair_paths": [3]}, "repair evidence"),
    )
    for malformed, message in invalid_payloads:
        with pytest.raises(ReviewExchangeError, match=message):
            evidence.CodeReviewEvidence.from_payload(malformed)

    retained = evidence.CodeReviewEvidence.from_payload(payload)
    with pytest.raises(ReviewExchangeError, match="unsafe token"):
        evidence.manifest_path(tmp_path, (*retained.identity[:-1], "../2"))
    with pytest.raises(ReviewExchangeError, match="must be ignored"):
        evidence.write_manifest(tmp_path, retained)

    (tmp_path / ".gitignore").write_text("a.*\n", encoding="utf-8")
    original_write = Path.write_text

    def fail_write(
        self: Path,
        data: str,
        encoding: str | None = None,
        errors: str | None = None,
        newline: str | None = None,
    ) -> int:
        if self.name.endswith(".tmp"):
            message = "write denied"
            raise OSError(message)
        return original_write(
            self,
            data,
            encoding=encoding,
            errors=errors,
            newline=newline,
        )

    monkeypatch.setattr(Path, "write_text", fail_write)
    with pytest.raises(ReviewExchangeError, match="cannot write"):
        evidence.write_manifest(tmp_path, retained)
    monkeypatch.setattr(Path, "write_text", original_write)

    path = evidence.write_manifest(tmp_path, retained)
    original_unlink = Path.unlink

    def fail_unlink(
        self: Path,
        missing_ok: bool = False,
    ) -> None:
        if self == path:
            message = "retire denied"
            raise OSError(message)
        original_unlink(self, missing_ok=missing_ok)

    monkeypatch.setattr(Path, "unlink", fail_unlink)
    with pytest.raises(ReviewExchangeError, match="cannot retire"):
        evidence.retire_manifest(tmp_path, retained.identity)


def test_capture_validation_state_rejects_missing_repository(tmp_path: Path) -> None:
    """Validation capture requires one existing exact repository directory."""
    with pytest.raises(ReviewExchangeError, match="repository is not a directory"):
        evidence.capture_validation_state(tmp_path / "missing")
