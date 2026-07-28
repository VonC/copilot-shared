"""Collection-aware routing used after a feature branch is merged."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from tools import prompt_workflow_docs as docs
from tools import prompt_workflow_steps as steps
from tools.prompt_workflow_models import PromptWorkflowError, Topic

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping
    from pathlib import Path

    from tools.prompt_workflow_models import CollectionItem


@dataclass(frozen=True, kw_only=True)
class ItemRoute:
    """Whether collection routing should continue and an optional command."""

    should_continue: bool
    command: str | None = None


@dataclass(frozen=True)
class CollectionCommands:
    """Callbacks supplied by the public skill module."""

    prefix_for: Callable[[Mapping[str, str], str | None], str]
    process_draft_for: Callable[[str, Path, str], str]
    resume_for: Callable[[Topic, str], str]


@dataclass(frozen=True)
class CollectionContext:
    """Stable values shared while routing the rows of one umbrella."""

    root: Path
    umbrella: Path
    version: str
    prefix: str
    process_draft_for: Callable[[str, Path, str], str]


def post_merge_command(
    root: Path,
    umbrella_document: str,
    env: Mapping[str, str],
    override: str | None,
    commands: CollectionCommands,
) -> str | None:
    """Return the next collection action after one feature was merged."""
    path = _umbrella_path(root, umbrella_document)
    if path is None:
        return None
    parsed = docs.parse_draft_name(path.name)
    items = docs.collection_items(path)
    if parsed is None or not items:
        return None
    version, _umbrella_slug = parsed
    prefix = commands.prefix_for(env, override)
    context = CollectionContext(root, path, version, prefix, commands.process_draft_for)
    for item in items:
        route = _item_route(context, item)
        if route.should_continue:
            continue
        if route.command is not None:
            return route.command
        topic = Topic(version=version, slug=item.slug, draft_path=path)
        return commands.resume_for(topic, item.slug)
    return f"{prefix}prepare-release"


def _item_route(
    context: CollectionContext,
    item: CollectionItem,
) -> ItemRoute:
    """Validate one row and decide whether to skip, start, or resume it."""
    state = steps.compute_state(
        context.root,
        Topic(version=context.version, slug=item.slug, draft_path=context.umbrella),
        None,
    )
    if item.status == "completed":
        _validate_completed_item(context.root, item)
        return ItemRoute(should_continue=True)
    if item.requirement_path is not None or item.validation_plan_path is not None:
        message = (
            f"Pending umbrella item {item.slug!r} must use '-' for its "
            "requirement and validation plan."
        )
        raise PromptWorkflowError(message)
    if _validation_plan_complete(state.validation_plan):
        message = (
            f"Umbrella item {item.slug!r} is pending, but "
            f"{state.validation_plan} says it is implemented. Run "
            "implementation-check for the final plan step so it can update "
            "the umbrella row."
        )
        raise PromptWorkflowError(message)
    if state.requirement is None:
        command = context.process_draft_for(
            context.prefix,
            context.umbrella,
            item.slug,
        )
        return ItemRoute(should_continue=False, command=command)
    return ItemRoute(should_continue=False)


def _umbrella_path(root: Path, document: str) -> Path | None:
    """Resolve an umbrella path when it remains inside the project."""
    path = (root / document).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError:
        return None
    return path if path.is_file() else None


def _validate_completed_item(root: Path, item: CollectionItem) -> None:
    """Require canonical completed rows to point at complete evidence."""
    if item.requirement_path is None or item.validation_plan_path is None:
        message = (
            f"Completed umbrella item {item.slug!r} must name its requirement "
            "and validation plan."
        )
        raise PromptWorkflowError(message)
    requirement = _collection_document(root, item.requirement_path)
    validation = _collection_document(root, item.validation_plan_path)
    if not requirement.is_file():
        message = (
            f"Completed umbrella item {item.slug!r} names a missing requirement: "
            f"{item.requirement_path}."
        )
        raise PromptWorkflowError(message)
    if not _validation_plan_complete(validation):
        message = (
            f"Completed umbrella item {item.slug!r} does not have complete "
            f"validation evidence at {item.validation_plan_path}."
        )
        raise PromptWorkflowError(message)


def _collection_document(root: Path, document: str) -> Path:
    """Resolve one declared collection document without leaving the project."""
    path = (root / document).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError as err:
        message = f"Umbrella document path leaves the project root: {document}."
        raise PromptWorkflowError(message) from err
    return path


def _validation_plan_complete(path: Path | None) -> bool:
    """Return whether a validation plan carries the completed effort status."""
    if path is None:
        return False
    significant = (
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    )
    return next(significant, "") == "Yes, it is implemented."


# eof
