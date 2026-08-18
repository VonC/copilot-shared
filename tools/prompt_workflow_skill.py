"""Skill-mode command rendering and disk-derived routing for ``pw skill``.

Commands use the detected Claude or Codex prefix and point at the next document
workflow action. Post-write routing reviews the new artifact explicitly,
post-commit routing advances implementation steps, and post-merge routing walks
an umbrella collection in its declared order before allowing release work.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from tools import prompt_workflow_code_review as code_review
from tools import prompt_workflow_collection as collection
from tools import prompt_workflow_docs as docs
from tools import prompt_workflow_git as git
from tools import prompt_workflow_handoff as handoff
from tools import prompt_workflow_memory as memory
from tools import prompt_workflow_plan as plan
from tools import prompt_workflow_post_commit as post_commit
from tools import prompt_workflow_render as rendering
from tools import prompt_workflow_review as review
from tools import prompt_workflow_steps as steps
from tools.review_exchange_models import ArtifactState

if TYPE_CHECKING:
    from collections.abc import Mapping

    from tools.prompt_workflow_models import Topic, WorkflowState

# Markdown suffix dropped from an instruction file name to form the skill name.
MD_SUFFIX = ".md"
# Public compatibility exports now implemented by the cohesive rendering module.
HOST_CLAUDE = rendering.HOST_CLAUDE
HOST_CODEX = rendering.HOST_CODEX
DEFAULT_HOST = rendering.DEFAULT_HOST
detect_host = rendering.detect_host
host_prefix = rendering.host_prefix
render_command = rendering.render_command
render_step_command = rendering.render_step_command


# The instruction named before the workflow proper, when only a new draft exists.
PROCESS_DRAFT = "process-draft.md"
# The instruction each resolved workflow step names (step 1 on the slug branch writes).
STEP_INSTRUCTION = {
    1: "write-requirement.md",
    2: "review-ask-questions.md",
    3: "consolidate-then-review-ask-questions.md",
    4: "write-design.md",
    5: "review-ask-questions.md",
    6: "consolidate-then-review-ask-questions.md",
    7: "write-plans.md",
    8: "review-ask-questions.md",
    9: "consolidate-then-review-ask-questions.md",
    10: "implement-step.md",
}
# The artifact role each step reads or produces.
STEP_ROLE = {
    1: "requirement",
    2: "requirement",
    3: "requirement",
    4: "design",
    5: "design",
    6: "design",
    7: "plan",
    8: "plan",
    9: "plan",
    10: "plan",
}
# A review step whose current document, once it carries a decisions table, advances
# past the review to the next write or implement step (the Q02 post-process).
ADVANCE_PAST_REVIEW = {2: 4, 5: 7, 8: 10}
# The document type a write step produces for each artifact role.
PRODUCED_TYPE = {"requirement": "feature-request", "design": "design", "plan": "plan"}
# Workflow step number that hands execution to the plan implementation cycle.
IMPLEMENT_STEP = 10
SPEC_REVIEW_REQUESTOR = "spec-review-requestor"
SPEC_REVIEWER = "spec-reviewer"
CODE_REVIEW_REQUESTOR = "code-review-requestor"
CODE_REVIEWER = "code-reviewer"
FORCED_REVIEW_ROLES = frozenset(
    {
        SPEC_REVIEW_REQUESTOR,
        SPEC_REVIEWER,
        CODE_REVIEW_REQUESTOR,
        CODE_REVIEWER,
    },
)


def next_command(
    root: Path,
    topic: Topic,
    branch: str,
    env: Mapping[str, str],
    override: str | None = None,
) -> str:
    """Return the bare next-step command derived from the documents on disk.

    The next step is read from the tree only (never ``a.prompt_memory``): the
    state comes from ``compute_state`` with no memory step, ``next_step_numbers``
    picks the base step, and a current document carrying a decisions table
    advances past its review step (Q02). The resolved step maps to an instruction
    and a target document, which ``render_command`` turns into one host-prefixed
    line.

    Args:
        root: The project root the documents live under.
        topic: The resolved topic (version, slug, draft path).
        branch: The current branch name, used to tell a new draft (process-draft)
            from a draft already on its slug branch (write-requirement).
        env: The process environment, read for the host prefix.
        override: An optional host token forcing the prefix (see ``host_prefix``).

    Returns:
        One bare ``<prefix><name> on <document>`` command line.
    """
    state = steps.compute_state(root, topic, None)
    record = memory.read_memory(root)
    code_route = code_review.resolve_code_review_route(root, topic, state, record)
    if code_route is not None and code_route.state is not ArtifactState.IDLE:
        return code_review.command_for_route(root, code_route, host_prefix(env, override), render_step_command)
    review_route = review.live_specification_route(root, topic, state)
    if review_route is not None:
        role = (
            SPEC_REVIEWER
            if review_route.state is ArtifactState.REQUEST_PENDING
            else SPEC_REVIEW_REQUESTOR
        )
        return render_command(
            host_prefix(env, override),
            f"{role}{MD_SUFFIX}",
            _relpath(root, review_route.context.document_path),
        )
    step = _resolve_step(state)
    instruction, document = _instruction_and_document(step, root, topic, branch, state)
    prefix = host_prefix(env, override)
    command = render_command(prefix, instruction, document)
    if step == IMPLEMENT_STEP:
        return _implementation_command(root, state, prefix, command) or command
    return command


def _resolve_step(state: WorkflowState) -> int:
    """Return the base step, advanced past its review when the current doc is settled.

    Args:
        state: The workflow state read from disk.

    Returns:
        The first ``next_step_numbers`` step, advanced past its review step when
        the document that review step reads carries a consolidated decisions
        table (Q02): a decisions heading plus a ``| Qxx`` row or the
        no-open-questions settled row, so a seeded decisions section never
        skips the review. A step with no review document (everything but 2, 5,
        and 8) is returned as is.
    """
    step = steps.next_step_numbers(state)[0]
    review_doc = {2: state.requirement, 5: state.design, 8: state.plan}.get(step)
    if review_doc is not None and docs.has_consolidated_decisions(review_doc):
        return ADVANCE_PAST_REVIEW[step]
    return step


def _instruction_and_document(
    step: int,
    root: Path,
    topic: Topic,
    branch: str,
    state: WorkflowState,
) -> tuple[str, str]:
    """Return the instruction and the target document for a resolved step.

    Step 1 is special: off the slug branch a new draft is still to be processed;
    on the slug branch the requirement is written. Every other step names the
    document of its artifact role through ``_document``.

    Args:
        step: The resolved step number.
        root: The project root, used to make document paths relative.
        topic: The resolved topic.
        branch: The current branch name (the step-1 process-draft case).
        state: The workflow state, holding the existing document paths.

    Returns:
        An ``(instruction, document)`` pair for ``render_command``.
    """
    if step == 1 and branch != topic.slug:
        return PROCESS_DRAFT, _relpath(root, topic.draft_path)
    return STEP_INSTRUCTION[step], _document(root, topic, STEP_ROLE[step], state)


def _implementation_command(
    root: Path,
    state: WorkflowState,
    prefix: str,
    base_command: str,
) -> str | None:
    """Return the validation-plan command for an implementation-cycle route.

    Args:
        root: The project root, used for commit-history checks.
        state: The workflow state holding the validation plan path.
        prefix: The host command prefix for terminal release commands.
        base_command: The rendered implement-step command without a plan step.

    Returns:
        The command with a plan step, the terminal release command, or None when
        no validation plan can provide one.
    """
    if state.validation_plan is None:
        return None
    plan_steps = plan.parse_validation_steps(state.validation_plan.read_text(encoding="utf-8"))
    if not plan_steps:
        return None
    branch_start = git.fork_point(root)

    def _has_commit(number: str) -> bool:
        return git.has_step_commit(root, number, branch_start)

    step, _verified, terminal = plan.derive_x(plan_steps, _has_commit)
    if terminal:
        return f"{prefix}prepare-release"
    return f"{base_command} step {step}"


def _document(root: Path, topic: Topic, role: str, state: WorkflowState) -> str:
    """Return the document for a role: the existing one, or the one to produce.

    Args:
        root: The project root, used to make an existing path relative.
        topic: The resolved topic, used to name a document still to be produced.
        role: The artifact role (``requirement``, ``design``, or ``plan``).
        state: The workflow state holding the existing document paths.

    Returns:
        The relative path of the existing document for the role when present,
        otherwise the relative path of the document a write step produces.
    """
    existing = {
        "requirement": state.requirement,
        "design": state.design,
        "plan": state.plan,
    }[role]
    if existing is not None:
        return _relpath(root, existing)
    effort_dir = _relpath(root, topic.draft_path.parent)
    filename = f"{PRODUCED_TYPE[role]}.{topic.version}.{topic.slug}.md"
    return (Path(effort_dir) / filename).as_posix()


def _relpath(root: Path, path: Path) -> str:
    """Return ``path`` as a posix string relative to the project root."""
    return Path(os.path.relpath(Path(path).resolve(), root)).as_posix()


# Exit code when the skill mode has no command to emit (a forced skill that is not
# yet applicable, or no resolvable topic): stdout stays empty so the caller never
# reads the signal as a command (Q03).
EXIT_NOT_APPLICABLE = 3
# The document role a forced skill targets; the skill is emitted only when that
# document exists (Q04). Review and consolidate are not forceable here, since they
# read whichever document is current rather than a single owned one.
FORCED_ROLE = {
    "process-draft": "draft",
    "write-requirement": "requirement",
    "write-design": "design",
    "write-plans": "plan",
    "implement-step": "plan",
}

# Artifact roles accepted by the explicit post-write review handoff.
AFTER_WRITE_ROLES = ("requirement", "design", "plan")


def run_skill(  # noqa: PLR0913
    root: Path,
    skill_name: str | None,
    host_override: str | None,
    after_commit: str | None = None,
    after_write: str | None = None,
    after_merge: str | None = None,
) -> int:
    """Print the bare next-step command for the current topic, or a forced skill.

    With ``after_commit`` set, prints the post-commit next action for that
    just-committed plan step instead (Step 7). With ``after_write`` set, reviews
    that just-written artifact regardless of settled-looking content. Otherwise
    resolves the topic without a menu (the single draft, or the branch-locked
    one), then prints the disk-derived next command, or - with a skill name -
    that skill's command when its document exists. When nothing applies (no
    resolvable topic, a forced skill whose document is absent, no written
    artifact, or no next step after the commit) it writes a
    one-line note to stderr, leaves stdout empty, and returns
    ``EXIT_NOT_APPLICABLE`` so the caller never reads the signal as a command (Q03).

    Args:
        root: The project root.
        skill_name: A forced skill name, or None for the derived next step.
        host_override: A host token forcing the prefix, or None to detect it.
        after_commit: A just-committed plan step to derive the post-commit action
            for, or None for the normal next-step or forced-skill behavior.
        after_write: The artifact role just written, or None for disk-derived
            routing.
        after_merge: The repository-relative umbrella draft just merged into
            its destination, or None outside the collection checkpoint.

    Returns:
        0 when a command is printed, ``EXIT_NOT_APPLICABLE`` otherwise.
    """
    if after_merge is not None:
        return _emit(
            post_merge_command(root, after_merge, os.environ, host_override),
            f"pw skill: no collection backlog resolved from {after_merge}.\n",
        )
    if after_commit is not None:
        return _emit(
            post_commit_command(root, after_commit, os.environ, host_override),
            f"pw skill: no next step after committing {after_commit}.\n",
        )
    branch = git.current_branch(root)
    topic = handoff.resolve_current_topic(
        root,
        branch,
        memory.read_memory(root),
    )
    if topic is None:
        return _emit(None, "pw skill: no topic resolved on this branch.\n")
    if after_write is not None:
        return _emit(
            post_write_command(root, topic, after_write, os.environ, host_override),
            f"pw skill: no {after_write} document to review.\n",
        )
    if skill_name is not None:
        return _emit(
            forced_command(root, topic, skill_name, os.environ, host_override),
            f"pw skill: {skill_name} is not applicable here.\n",
        )
    branch_slug = branch.rsplit("/", maxsplit=1)[-1]
    if (
        post_commit.slug_key(branch_slug) == post_commit.slug_key(topic.slug)
        and docs.collection_items(topic.draft_path)
    ):
        umbrella = _relpath(root, topic.draft_path)
        command = post_merge_command(root, umbrella, os.environ, host_override)
        error = f"pw skill: no collection backlog resolved from {umbrella}.\n"
    else:
        command = next_command(root, topic, branch, os.environ, host_override)
        error = ""
    return _emit(command, error)


def run_authorized_code_review_commit(root: Path) -> int:
    """Resume one durable code-review commit without displaying another gate."""
    branch = git.current_branch(root)
    record = memory.read_memory(root)
    topic = handoff.resolve_current_topic(root, branch, record)
    if topic is None:
        message = "authorized code-review commit has no resolved workflow topic"
        raise code_review.CodeReviewRoutingError(message)
    state = steps.compute_state(root, topic, None)
    return code_review.continue_authorized_commit(root, topic, state, record)


def post_merge_command(
    root: Path,
    umbrella_document: str,
    env: Mapping[str, str],
    override: str | None = None,
) -> str | None:
    """Return the next ordered collection action after a feature merge."""
    return collection.post_merge_command(
        root,
        umbrella_document,
        env,
        override,
        collection.CollectionCommands(
            prefix_for=host_prefix,
            process_draft_for=lambda prefix, path, slug: (
                f"{render_command(prefix, PROCESS_DRAFT, _relpath(root, path))} "
                f"based on {slug}"
            ),
            resume_for=lambda topic, branch: next_command(
                root,
                topic,
                branch,
                env,
                override,
            ),
        ),
    )


def _emit(command: str | None, not_applicable_note: str) -> int:
    """Print a command to stdout and return 0, or note its absence on stderr.

    Args:
        command: The command to print, or None when nothing applies.
        not_applicable_note: The stderr line written when command is None.

    Returns:
        0 when a command is printed; ``EXIT_NOT_APPLICABLE`` when it is None.
    """
    if command is None:
        sys.stderr.write(not_applicable_note)
        return EXIT_NOT_APPLICABLE
    sys.stdout.write(f"{command}\n")
    return 0


def forced_command(
    root: Path,
    topic: Topic,
    skill_name: str,
    env: Mapping[str, str],
    override: str | None = None,
) -> str | None:
    """Return a forced skill's command when its document exists, else None (Q04).

    Args:
        root: The project root, used to make the document path relative.
        topic: The resolved topic.
        skill_name: The forced skill name (a key of ``FORCED_ROLE``).
        env: The process environment, read for the host prefix.
        override: A host token forcing the prefix, or None to detect it.

    Returns:
        The host-prefixed command naming the skill's document when that document
        exists; None when the skill is unknown or its document is absent.
    """
    state = steps.compute_state(root, topic, None)
    if skill_name in FORCED_REVIEW_ROLES:
        return _forced_review_command(
            root,
            topic,
            state,
            skill_name,
            env,
            override,
        )
    role = FORCED_ROLE.get(skill_name)
    if role is None:
        return None
    doc = (
        topic.draft_path
        if role == "draft"
        else {
            "requirement": state.requirement,
            "design": state.design,
            "plan": state.plan,
        }[role]
    )
    if doc is None:
        return None
    instruction = f"{skill_name}{MD_SUFFIX}"
    return render_command(host_prefix(env, override), instruction, _relpath(root, doc))


def _forced_review_command(  # noqa: PLR0913
    root: Path,
    topic: Topic,
    state: WorkflowState,
    skill_name: str,
    env: Mapping[str, str],
    override: str | None,
) -> str | None:
    """Dispatch one explicit review role without burdening generic routing."""
    if skill_name == CODE_REVIEWER:
        return _forced_code_reviewer_command(root, topic, state, env, override)
    if skill_name == SPEC_REVIEWER:
        return _forced_spec_reviewer_command(root, topic, state, env, override)
    if skill_name == CODE_REVIEW_REQUESTOR:
        route = code_review.resolve_code_review_route(
            root,
            topic,
            state,
            memory.read_memory(root),
        )
        if route is None or route.actor is not code_review.CodeReviewActor.REQUESTOR:
            return None
        return code_review.command_for_route(
            root,
            route,
            host_prefix(env, override),
            render_step_command,
        )
    doc = review.forced_specification_document(root, topic, state)
    if doc is None:
        return None
    return render_command(
        host_prefix(env, override),
        f"{SPEC_REVIEW_REQUESTOR}{MD_SUFFIX}",
        _relpath(root, doc),
    )


def _forced_spec_reviewer_command(
    root: Path,
    topic: Topic,
    state: WorkflowState,
    env: Mapping[str, str],
    override: str | None,
) -> str | None:
    """Render only an exact pending reviewer route and diagnose cold reclaim."""
    route = review.live_specification_route(root, topic, state)
    if route is None:
        return None
    if route.state is ArtifactState.ABANDONED_REQUEST:
        message = (
            "forced spec-reviewer cannot enter an abandoned request cold; "
            f"run {SPEC_REVIEW_REQUESTOR} reclaim for {route.context.identity.key}"
        )
        raise review.SpecificationReviewRoutingError(message)
    if route.state is not ArtifactState.REQUEST_PENDING:
        return None
    return render_command(
        host_prefix(env, override),
        f"{SPEC_REVIEWER}{MD_SUFFIX}",
        _relpath(root, route.context.document_path),
    )


def _forced_code_reviewer_command(
    root: Path,
    topic: Topic,
    state: WorkflowState,
    env: Mapping[str, str],
    override: str | None,
) -> str | None:
    """Render only an exact pending code reviewer route and diagnose cold reclaim."""
    route = code_review.resolve_code_review_route(
        root,
        topic,
        state,
        memory.read_memory(root),
    )
    if route is None:
        return None
    if route.state is ArtifactState.ABANDONED_REQUEST:
        message = (
            "forced code-reviewer cannot enter an abandoned request cold; "
            f"run {CODE_REVIEW_REQUESTOR} reclaim for {route.context.identity.key}"
        )
        raise code_review.CodeReviewRoutingError(message)
    if route.actor is not code_review.CodeReviewActor.REVIEWER:
        return None
    return code_review.command_for_route(
        root,
        route,
        host_prefix(env, override),
        render_step_command,
    )


def post_write_command(
    root: Path,
    topic: Topic,
    written_role: str,
    env: Mapping[str, str],
    override: str | None = None,
) -> str | None:
    """Return the review command for the artifact that was just written.

    This explicit handoff intentionally ignores decisions-table markers. A
    writer knows which artifact it produced, while bare ``pw skill`` remains the
    state-based router used after review and consolidation.

    Args:
        root: The project root.
        topic: The resolved topic.
        written_role: One of ``AFTER_WRITE_ROLES``.
        env: The process environment, read for the host prefix.
        override: A host token forcing the prefix, or None to detect it.

    Returns:
        A review command for the written artifact, or None when it is absent.
    """
    state = steps.compute_state(root, topic, None)
    document = {
        "requirement": state.requirement,
        "design": state.design,
        "plan": state.plan,
    }[written_role]
    if document is None:
        return None
    return render_command(
        host_prefix(env, override),
        "review-ask-questions.md",
        _relpath(root, document),
    )


def post_commit_command(
    root: Path,
    committed_step: str,
    env: Mapping[str, str],
    override: str | None = None,
) -> str | None:
    """Return the command to chain after committing ``committed_step`` (Step 7).

    Told the plan step the commit completes, this names the step after it for
    ``implement-step``; once that step was the last, ``prepare-release``; and when
    no validation plan is resolved (a standalone commit, no effort) or the step is
    not in the plan, None.

    Args:
        root: The project root.
        committed_step: The plan step id the commit just completed.
        env: The process environment, read for the host prefix.
        override: A host token forcing the prefix, or None to detect it.

    Returns:
        The host-prefixed command for the next action, or None when there is no
        plan in play or the committed step is not one of its steps.
    """
    branch = git.current_branch(root)
    record = memory.read_memory(root)
    topic = handoff.resolve_current_topic(root, branch, record)
    if topic is None:
        topic = post_commit.resolve_post_commit_topic(root, record, branch)
    if topic is None:
        return None
    state = steps.compute_state(root, topic, None)
    if state.validation_plan is None:
        return None
    numbers = [
        plan_step.number
        for plan_step in plan.parse_validation_steps(
            state.validation_plan.read_text(encoding="utf-8"),
        )
    ]
    if committed_step not in numbers:
        return None
    prefix = host_prefix(env, override)
    index = numbers.index(committed_step)
    if index + 1 < len(numbers):
        plan_doc = _document(root, topic, "plan", state)
        return f"{prefix}implement-step on {plan_doc} step {numbers[index + 1]}"
    return f"{prefix}prepare-release"


# eof
