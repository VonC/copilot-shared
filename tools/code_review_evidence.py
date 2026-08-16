"""Capture and retain executable Git evidence shared by code-review actors.

Step 2 extends immutable index capture with exact pre-repair blobs, reviewer
patch attribution, umbrella and validation-state comparisons, and one stable
identity-derived retained manifest.
"""

# ruff: noqa: EM101, EM102, TRY003

from __future__ import annotations

import difflib
import hashlib
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from tools.git_command import GitCommandOptions, run_cross_platform_git_command
from tools.review_exchange_models import ReviewExchangeError

_TREE_OBJECT_RE = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
_OBJECT_RE = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
_TOKEN_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
_MANIFEST_SCHEMA = 1
_IDENTITY_NAMES = ("family", "type_token", "version", "slug", "implementation_step")


def _object_map(payload: object, label: str) -> dict[str, object]:
    if not isinstance(payload, dict):
        raise ReviewExchangeError(f"{label} must be an object")
    return cast("dict[str, object]", payload)


def _required_string(payload: dict[str, object], name: str, label: str) -> str:
    value = payload.get(name)
    if not isinstance(value, str) or not value:
        raise ReviewExchangeError(f"{label} is invalid")
    return value


def _tree_field(payload: dict[str, object], name: str) -> str:
    value = _required_string(payload, name, "retained evidence tree identity")
    if _TREE_OBJECT_RE.fullmatch(value) is None:
        raise ReviewExchangeError("retained evidence tree identity is invalid")
    return value


def _repository_root(repository: str | Path) -> Path:
    root = Path(repository).expanduser().resolve()
    if not root.is_dir():
        raise ReviewExchangeError("repository is not a directory")
    return root


def _git(
    root: Path,
    arguments: tuple[str, ...],
    *,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    try:
        return run_cross_platform_git_command(
            arguments,
            cwd=root,
            options=GitCommandOptions(
                check=check,
                capture_output=True,
                encoding="utf-8",
            ),
        )
    except (OSError, subprocess.CalledProcessError) as error:
        raise ReviewExchangeError(f"Git evidence command failed: {error}") from error


def _relative_path(root: Path, value: str | Path) -> tuple[str, Path]:
    supplied = Path(value)
    if supplied.is_absolute():
        raise ReviewExchangeError("evidence path must be repository-relative")
    candidate = (root / supplied).resolve()
    try:
        relative = candidate.relative_to(root)
    except ValueError as error:
        raise ReviewExchangeError("evidence path must be repository-relative") from error
    if not relative.parts:
        raise ReviewExchangeError("evidence path must name a file")
    return relative.as_posix(), candidate


def capture_index_tree(repository: str | Path) -> str:
    """Return the Git tree object for the repository index, never its worktree."""
    root = Path(repository).expanduser().resolve()
    if not root.is_dir():
        raise ReviewExchangeError("cannot capture Git index tree: repository is not a directory")
    try:
        result = run_cross_platform_git_command(
            ("write-tree",),
            cwd=root,
            options=GitCommandOptions(capture_output=True, encoding="utf-8"),
        )
    except (OSError, subprocess.CalledProcessError) as error:
        raise ReviewExchangeError(f"cannot capture Git index tree: {error}") from error
    tree_object = result.stdout.strip()
    if _TREE_OBJECT_RE.fullmatch(tree_object) is None:
        raise ReviewExchangeError("Git returned a malformed tree object for the index")
    return tree_object


@dataclass(frozen=True)
class RecordedBlob:
    """Pre-repair worktree content recorded in the Git object database."""

    path: str
    object_id: str | None
    writer_deleted: bool = False

    def to_payload(self) -> dict[str, object]:
        """Return the JSON-safe recorded-blob representation."""
        return {
            "path": self.path,
            "object_id": self.object_id,
            "writer_deleted": self.writer_deleted,
        }

    @classmethod
    def from_payload(cls, payload: object) -> RecordedBlob:
        """Build a recorded blob from validated JSON-safe data."""
        data = _object_map(payload, "recorded blob")
        path = _required_string(data, "path", "recorded blob path")
        object_id = data.get("object_id")
        writer_deleted = data.get("writer_deleted", False)
        if object_id is not None and (
            not isinstance(object_id, str) or _OBJECT_RE.fullmatch(object_id) is None
        ):
            raise ReviewExchangeError("recorded blob object is invalid")
        if not isinstance(writer_deleted, bool):
            raise ReviewExchangeError("recorded blob deletion flag is invalid")
        return cls(path, object_id, writer_deleted)


@dataclass(frozen=True)
class RepairAttribution:
    """Patch from one recorded baseline to the current reviewer-authored state."""

    path: str
    patch: str
    attributable: bool
    created: bool = False
    reason: str = "attributable"

    def to_payload(self) -> dict[str, object]:
        """Return the JSON-safe repair-attribution representation."""
        return {
            "path": self.path,
            "patch": self.patch,
            "attributable": self.attributable,
            "created": self.created,
            "reason": self.reason,
        }


def record_pre_repair_blob(repository: str | Path, path: str | Path) -> RecordedBlob:
    """Record current worktree bytes before a reviewer first repairs one path."""
    root = _repository_root(repository)
    relative, candidate = _relative_path(root, path)
    tracked = _git(root, ("ls-files", "--error-unmatch", "--", relative), check=False)
    if not candidate.exists():
        return RecordedBlob(relative, None, writer_deleted=tracked.returncode == 0)
    if not candidate.is_file():
        raise ReviewExchangeError("pre-repair evidence path must be a file")
    result = _git(root, ("hash-object", "-w", "--", relative))
    object_id = result.stdout.strip()
    if _OBJECT_RE.fullmatch(object_id) is None:
        raise ReviewExchangeError("Git returned a malformed pre-repair blob object")
    return RecordedBlob(relative, object_id)


def attribute_reviewer_patch(
    repository: str | Path,
    baseline: RecordedBlob,
) -> RepairAttribution:
    """Compute only the change after a recorded pre-repair worktree baseline."""
    root = _repository_root(repository)
    relative, candidate = _relative_path(root, baseline.path)
    if baseline.writer_deleted:
        return RepairAttribution(
            relative,
            "",
            attributable=False,
            reason="writer-deleted path",
        )
    if not candidate.is_file():
        return RepairAttribution(
            relative,
            "",
            attributable=False,
            reason="repair target is absent",
        )
    try:
        current = candidate.read_text(encoding="utf-8").splitlines(keepends=True)
        if baseline.object_id is None:
            before: list[str] = []
        else:
            before = _git(root, ("cat-file", "blob", baseline.object_id)).stdout.splitlines(
                keepends=True,
            )
    except UnicodeError as error:
        raise ReviewExchangeError("reviewer patch attribution requires UTF-8 text") from error
    patch = "".join(
        difflib.unified_diff(
            before,
            current,
            fromfile=f"a/{relative}",
            tofile=f"b/{relative}",
        ),
    )
    return RepairAttribution(
        relative,
        patch,
        attributable=True,
        created=baseline.object_id is None,
    )


@dataclass(frozen=True)
class UmbrellaDigest:
    """Optional SHA-256 identity of the protected umbrella document."""

    applicable: bool
    digest: str | None = None

    def to_payload(self) -> dict[str, object]:
        """Return the JSON-safe optional digest representation."""
        return {"applicable": self.applicable, "digest": self.digest}

    @classmethod
    def from_payload(cls, payload: object) -> UmbrellaDigest:
        """Build an optional digest from validated JSON-safe data."""
        data = _object_map(payload, "umbrella digest evidence")
        applicable = data.get("applicable")
        digest = data.get("digest")
        if not isinstance(applicable, bool):
            raise ReviewExchangeError("umbrella digest applicability is invalid")
        if digest is not None and not isinstance(digest, str):
            raise ReviewExchangeError("umbrella digest value is invalid")
        return cls(applicable=applicable, digest=digest)


@dataclass(frozen=True)
class UmbrellaComparison:
    """Comparison result for a protected umbrella document."""

    applicable: bool
    changed: bool
    before: str | None
    after: str | None

    def to_payload(self) -> dict[str, object]:
        """Return the JSON-safe umbrella comparison representation."""
        return {
            "applicable": self.applicable,
            "changed": self.changed,
            "before": self.before,
            "after": self.after,
        }


def capture_umbrella_digest(path: str | Path | None) -> UmbrellaDigest:
    """Capture a protected umbrella digest or an explicit not-applicable value."""
    if path is None:
        return UmbrellaDigest(applicable=False)
    target = Path(path).expanduser().resolve()
    if not target.is_file():
        raise ReviewExchangeError("umbrella document is not a file")
    return UmbrellaDigest(
        applicable=True,
        digest=hashlib.sha256(target.read_bytes()).hexdigest(),
    )


def compare_umbrella_digest(
    baseline: UmbrellaDigest,
    path: str | Path | None,
) -> UmbrellaComparison:
    """Compare the umbrella after either a passing or failing criteria run."""
    current = capture_umbrella_digest(path)
    if baseline.applicable != current.applicable:
        raise ReviewExchangeError("umbrella applicability changed during assessment")
    return UmbrellaComparison(
        baseline.applicable,
        baseline.digest != current.digest,
        baseline.digest,
        current.digest,
    )


@dataclass(frozen=True)
class FileDigest:
    """Content identity for one repository-relative path."""

    path: str
    digest: str | None

    def to_payload(self) -> dict[str, object]:
        """Return the JSON-safe file digest representation."""
        return {"path": self.path, "digest": self.digest}

    @classmethod
    def from_payload(cls, payload: object) -> FileDigest:
        """Build one file digest from validated JSON-safe data."""
        data = _object_map(payload, "file digest")
        path = _required_string(data, "path", "file digest path")
        digest = data.get("digest")
        if digest is not None and not isinstance(digest, str):
            raise ReviewExchangeError("file digest value is invalid")
        return cls(path, digest)


@dataclass(frozen=True)
class ValidationState:
    """Index and worktree content identities around mandatory validation."""

    index_tree: str
    tracked_files: tuple[FileDigest, ...]
    ignored_files: tuple[FileDigest, ...]
    untracked_files: tuple[FileDigest, ...]

    def to_payload(self) -> dict[str, object]:
        """Return the JSON-safe validation-state representation."""
        return {
            "index_tree": self.index_tree,
            "tracked_files": [item.to_payload() for item in self.tracked_files],
            "ignored_files": [item.to_payload() for item in self.ignored_files],
            "untracked_files": [item.to_payload() for item in self.untracked_files],
        }

    @classmethod
    def from_payload(cls, payload: object) -> ValidationState:
        """Build a validation state from validated JSON-safe data."""
        data = _object_map(payload, "validation state")
        tree = data.get("index_tree")
        if not isinstance(tree, str) or _TREE_OBJECT_RE.fullmatch(tree) is None:
            raise ReviewExchangeError("validation state index tree is invalid")
        values: list[tuple[FileDigest, ...]] = []
        for name in ("tracked_files", "ignored_files", "untracked_files"):
            items = data.get(name)
            if not isinstance(items, list):
                raise ReviewExchangeError(f"validation state {name} is invalid")
            typed_items = cast("list[object]", items)
            values.append(tuple(FileDigest.from_payload(item) for item in typed_items))
        return cls(tree, *values)


@dataclass(frozen=True)
class ValidationStateComparison:
    """Classified repository differences produced by validation commands."""

    tracked_paths: tuple[str, ...]
    ignored_paths: tuple[str, ...]
    untracked_paths: tuple[str, ...]

    @property
    def acceptable(self) -> bool:
        """Return whether differences are confined to ignored artifacts."""
        return not self.tracked_paths and not self.untracked_paths

    def to_payload(self) -> dict[str, object]:
        """Return the JSON-safe validation comparison representation."""
        return {
            "acceptable": self.acceptable,
            "tracked_paths": list(self.tracked_paths),
            "ignored_paths": list(self.ignored_paths),
            "untracked_paths": list(self.untracked_paths),
        }


def _digest_path(root: Path, relative: str) -> FileDigest:
    path = root / Path(relative)
    digest = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
    return FileDigest(relative, digest)


def _listed_paths(root: Path, arguments: tuple[str, ...]) -> tuple[str, ...]:
    output = _git(root, arguments).stdout
    return tuple(sorted(path for path in output.split("\0") if path))


def capture_validation_state(repository: str | Path) -> ValidationState:
    """Capture exact index, tracked, ignored, and other untracked state."""
    root = _repository_root(repository)
    tracked = _listed_paths(root, ("ls-files", "-z"))
    ignored = _listed_paths(
        root,
        ("ls-files", "--others", "--ignored", "--exclude-standard", "-z"),
    )
    untracked = _listed_paths(root, ("ls-files", "--others", "--exclude-standard", "-z"))
    return ValidationState(
        capture_index_tree(root),
        tuple(_digest_path(root, path) for path in tracked),
        tuple(_digest_path(root, path) for path in ignored),
        tuple(_digest_path(root, path) for path in untracked),
    )


def _changed_paths(before: tuple[FileDigest, ...], after: tuple[FileDigest, ...]) -> tuple[str, ...]:
    before_map = {item.path: item.digest for item in before}
    after_map = {item.path: item.digest for item in after}
    return tuple(
        sorted(path for path in before_map.keys() | after_map.keys() if before_map.get(path) != after_map.get(path)),
    )


def compare_validation_state(
    before: ValidationState,
    after: ValidationState,
) -> ValidationStateComparison:
    """Classify validation side effects without staging, reverting, or relabeling."""
    tracked = set(_changed_paths(before.tracked_files, after.tracked_files))
    if before.index_tree != after.index_tree:
        tracked.add("<index>")
    return ValidationStateComparison(
        tuple(sorted(tracked)),
        _changed_paths(before.ignored_files, after.ignored_files),
        _changed_paths(before.untracked_files, after.untracked_files),
    )


@dataclass(frozen=True)
class CodeReviewEvidence:
    """Stable retained assessment evidence for one exact exchange and step."""

    family: str
    type_token: str
    version: str
    slug: str
    implementation_step: str
    baseline_index_tree: str
    assessed_index_tree: str
    recorded_blobs: tuple[RecordedBlob, ...] = ()
    repair_paths: tuple[str, ...] = ()
    validation_before: ValidationState | None = None
    validation_after: ValidationState | None = None

    @property
    def identity(self) -> tuple[str, str, str, str, str]:
        """Return the exact exchange identity plus implementation step."""
        return (
            self.family,
            self.type_token,
            self.version,
            self.slug,
            self.implementation_step,
        )

    def to_payload(self) -> dict[str, object]:
        """Return the versioned JSON-safe retained evidence representation."""
        return {
            "schema_version": _MANIFEST_SCHEMA,
            "identity": dict(
                zip(
                    _IDENTITY_NAMES,
                    self.identity,
                    strict=True,
                ),
            ),
            "baseline_index_tree": self.baseline_index_tree,
            "assessed_index_tree": self.assessed_index_tree,
            "recorded_blobs": [item.to_payload() for item in self.recorded_blobs],
            "repair_paths": list(self.repair_paths),
            "validation_before": None if self.validation_before is None else self.validation_before.to_payload(),
            "validation_after": None if self.validation_after is None else self.validation_after.to_payload(),
        }

    @classmethod
    def from_payload(cls, payload: object) -> CodeReviewEvidence:
        """Build retained evidence from one strict versioned manifest payload."""
        data = _object_map(payload, "retained evidence manifest")
        if data.get("schema_version") != _MANIFEST_SCHEMA:
            raise ReviewExchangeError("retained evidence manifest schema is invalid")
        identity = _object_map(data.get("identity"), "retained evidence identity")
        values = tuple(
            _required_string(identity, name, "retained evidence identity")
            for name in _IDENTITY_NAMES
        )
        blobs = data.get("recorded_blobs", [])
        repairs = data.get("repair_paths", [])
        if not isinstance(blobs, list) or not isinstance(repairs, list):
            raise ReviewExchangeError("retained repair evidence is invalid")
        typed_blobs = cast("list[object]", blobs)
        typed_repairs = cast("list[object]", repairs)
        if not all(isinstance(item, str) for item in typed_repairs):
            raise ReviewExchangeError("retained repair evidence is invalid")
        family, type_token, version, slug, step = values
        before = data.get("validation_before")
        after = data.get("validation_after")
        return cls(
            family=family,
            type_token=type_token,
            version=version,
            slug=slug,
            implementation_step=step,
            baseline_index_tree=_tree_field(data, "baseline_index_tree"),
            assessed_index_tree=_tree_field(data, "assessed_index_tree"),
            recorded_blobs=tuple(RecordedBlob.from_payload(item) for item in typed_blobs),
            repair_paths=cast("tuple[str, ...]", tuple(typed_repairs)),
            validation_before=(
                None if before is None else ValidationState.from_payload(before)
            ),
            validation_after=(
                None if after is None else ValidationState.from_payload(after)
            ),
        )


def manifest_path(
    repository: str | Path,
    identity: tuple[str, str, str, str, str],
) -> Path:
    """Derive one stable ignored manifest path from exact identity and step."""
    root = _repository_root(repository)
    family, type_token, version, slug, step = identity
    del family, type_token
    if any(_TOKEN_RE.fullmatch(value) is None for value in (version, slug, step)):
        raise ReviewExchangeError("retained evidence identity contains an unsafe token")
    return root / f"a.code-review-evidence.{version}.{slug}.step-{step}.json"


def write_manifest(repository: str | Path, retained: CodeReviewEvidence) -> Path:
    """Atomically write retained evidence to its stable ignored path."""
    root = _repository_root(repository)
    path = manifest_path(root, retained.identity)
    relative = path.relative_to(root).as_posix()
    ignored = _git(root, ("check-ignore", "-q", "--", relative), check=False)
    if ignored.returncode != 0:
        raise ReviewExchangeError("retained evidence manifest path must be ignored")
    temporary = path.with_suffix(path.suffix + ".tmp")
    try:
        temporary.write_text(
            json.dumps(retained.to_payload(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        temporary.replace(path)
    except (OSError, UnicodeError) as error:
        raise ReviewExchangeError(f"cannot write retained evidence manifest: {error}") from error
    return path


def read_manifest(
    repository: str | Path,
    identity: tuple[str, str, str, str, str],
) -> CodeReviewEvidence:
    """Read and validate the stable retained evidence for one identity."""
    path = manifest_path(repository, identity)
    try:
        retained = CodeReviewEvidence.from_payload(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ReviewExchangeError(f"cannot read retained evidence manifest: {error}") from error
    if retained.identity != identity:
        raise ReviewExchangeError("retained evidence manifest identity disagrees with request")
    return retained


def retire_manifest(
    repository: str | Path,
    identity: tuple[str, str, str, str, str],
) -> bool:
    """Retire retained evidence only after the caller observes publication."""
    path = manifest_path(repository, identity)
    try:
        path.unlink()
    except FileNotFoundError:
        return False
    except OSError as error:
        raise ReviewExchangeError(f"cannot retire retained evidence manifest: {error}") from error
    return True


# eof
