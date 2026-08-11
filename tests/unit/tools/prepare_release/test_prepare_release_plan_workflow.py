"""Branch-role and operation selection tests for the release planner.

Fix: cover remaining planning branches: the boundary-less orphan branch,
merges in explicit feature scope, direct-merge conflict preview, explicit
`--feature-parent` boundaries (a first-parent merge success and an underivable failure),
an explicit base that is not a proper ancestor, rebase and reset reflog evidence, and the
ambiguity path where deduplicated parent candidates elect a unique nearest
boundary with reflogs disabled.

Fix: real-Git scenarios prepare plans or captured errors in fixtures, leaving
measured calls to verify the model without repository or planner subprocesses.
"""

from __future__ import annotations

import shutil
from typing import TYPE_CHECKING

import pytest

from tools.prepare_release import prepare_release_plan_workflow as workflow
from tools.prepare_release.prepare_release_plan_models import (
    CommitSummary,
    ReleaseAction,
    ReleaseMode,
    ReleasePlanError,
)
from tools.prepare_release.prepare_release_plan_workflow import build_release_plan

from .prepare_release_plan_test_support import commit_file, git, initialize_repository

if TYPE_CHECKING:
    from pathlib import Path

    from tools.prepare_release.prepare_release_plan_models import ReleasePlan

_EXPECTED_CANDIDATES = 2


class _FeatureRepositoryStub:
    """In-memory topology for feature-target selection tests."""

    def __init__(
        self,
        root: Path,
        *,
        integration_exists: bool,
        integration_contains_feature: bool = False,
    ) -> None:
        self.root = root
        self.integration_exists = integration_exists
        self.integration_contains_feature = integration_contains_feature

    def verify_repository(self) -> None:
        """Accept the synthetic repository."""

    def assert_supported_version(self) -> str:
        """Return a supported version without launching Git."""
        return "2.50.0"

    def current_branch(self) -> str:
        """Return the feature branch used by these tests."""
        return "feature"

    def resolve(self, ref: str) -> str:
        """Resolve the small synthetic ref set."""
        return {
            "main": "main-tip",
            "develop": "develop-current",
            "feature": "feature-tip",
        }.get(ref, ref)

    def config_value(self, _key: str) -> None:
        """Return no configured integration branch."""

    def branch_exists(self, branch: str) -> bool:
        """Expose develop only in integration-target scenarios."""
        return branch == "develop" and self.integration_exists

    def remote_default_branch(self) -> None:
        """Return no remote default branch."""

    def is_ancestor(self, ancestor: str, descendant: str) -> bool:
        """Answer only the topology relationships the planner asks about."""
        pair = self.resolve(ancestor), self.resolve(descendant)
        ancestors = {
            ("develop-tip", "feature-tip"),
            ("develop-tip", "develop-current"),
        }
        if self.integration_contains_feature:
            ancestors.add(("develop-current", "feature-tip"))
        return pair in ancestors

    def commit_count(self, _revision_range: str) -> int:
        """Return the single selected feature commit."""
        return 1

    def contains_merge(self, _revision_range: str) -> bool:
        """The synthetic feature range is linear."""
        return False

    def commits(self, _revision_range: str) -> tuple[CommitSummary, ...]:
        """Return the selected feature commit."""
        return (CommitSummary(oid="feature-tip", subject="feat: selected work"),)


def _stub_feature_repository(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    *,
    integration_exists: bool,
    integration_contains_feature: bool = False,
) -> None:
    """Install one in-memory repository behind the public planner entry point."""
    repository = _FeatureRepositoryStub(
        tmp_path,
        integration_exists=integration_exists,
        integration_contains_feature=integration_contains_feature,
    )

    def repository_factory(_root: Path) -> _FeatureRepositoryStub:
        return repository

    monkeypatch.setattr(workflow, "GitRepository", repository_factory)


@pytest.fixture
def integration_merge_plan(tmp_path: Path) -> ReleasePlan:
    """Prepare the real-Git integration merge plan outside assertion time."""
    repo = tmp_path / "repo"
    initialize_repository(repo)
    git(repo, "switch", "-c", "develop")
    commit_file(repo, "develop.txt", "develop\n", "feat: integrated work")
    git(repo, "switch", "main")
    return build_release_plan(repo, branch="develop", integration_branch="develop")


@pytest.fixture
def integration_conflict_plan(tmp_path: Path) -> ReleasePlan:
    """Prepare the real-Git integration conflict plan outside assertion time."""
    repo = tmp_path / "repo"
    initialize_repository(repo)
    git(repo, "switch", "-c", "develop")
    commit_file(repo, "shared.txt", "develop\n", "feat: develop change")
    git(repo, "switch", "main")
    commit_file(repo, "shared.txt", "main\n", "fix: main change")
    return build_release_plan(repo, branch="develop", integration_branch="develop")


@pytest.fixture
def explicit_parent_plan(tmp_path: Path) -> tuple[str, ReleasePlan]:
    """Prepare the first-parent boundary plan outside assertion time."""
    repo = tmp_path / "repo"
    base = initialize_repository(repo)
    git(repo, "switch", "-c", "feature")
    commit_file(repo, "feature.txt", "feature\n", "feat: feature change")
    git(repo, "switch", "-c", "develop", "main")
    git(repo, "merge", "--no-ff", "feature", "-m", "merge feature")
    plan = build_release_plan(
        repo,
        branch="feature",
        feature_parent="develop",
        preview_conflicts=False,
    )
    return base, plan


@pytest.fixture
def single_parent_plan(tmp_path: Path) -> tuple[str, ReleasePlan]:
    """Prepare the sole-parent boundary plan outside assertion time."""
    repo = tmp_path / "repo"
    base = initialize_repository(repo)
    git(repo, "switch", "-c", "feature")
    commit_file(repo, "feature.txt", "feature\n", "feat: feature change")
    git(repo, "switch", "main")
    commit_file(repo, "main.txt", "main\n", "fix: main work")
    shutil.rmtree(repo / ".git" / "logs")
    plan = build_release_plan(repo, branch="feature", preview_conflicts=False)
    return base, plan


@pytest.fixture
def ambiguous_parent_plan(tmp_path: Path) -> tuple[str, ReleasePlan]:
    """Prepare the deduplicated-parent plan outside assertion time."""
    repo = tmp_path / "repo"
    initialize_repository(repo)
    git(repo, "switch", "-c", "develop")
    fork_point = commit_file(repo, "parent.txt", "develop\n", "feat: parent work")
    git(repo, "switch", "-c", "feature")
    commit_file(repo, "feature.txt", "feature\n", "feat: feature change")
    # Advance develop and main past the fork and drop every reflog, so no
    # fork-point or branch-creation answer survives and the planner must
    # weigh plain merge-base candidates from every parent branch.
    git(repo, "switch", "develop")
    commit_file(repo, "parent.txt", "develop again\n", "feat: later parent work")
    git(repo, "switch", "main")
    commit_file(repo, "main.txt", "main\n", "fix: main work")
    git(repo, "branch", "other", "main")
    shutil.rmtree(repo / ".git" / "logs")
    plan = build_release_plan(repo, branch="feature", preview_conflicts=False)
    return fork_point, plan


@pytest.fixture
def rebased_feature_plan(tmp_path: Path) -> tuple[str, ReleasePlan]:
    """Prepare the reflog-backed rebase plan outside assertion time."""
    repo = tmp_path / "repo"
    initialize_repository(repo)
    git(repo, "switch", "-c", "feature")
    commit_file(repo, "feature.txt", "feature\n", "feat: feature change")
    git(repo, "switch", "main")
    main_tip = commit_file(repo, "main.txt", "main\n", "fix: main work")
    git(repo, "rebase", "main", "feature")
    plan = build_release_plan(repo, preview_conflicts=False)
    return main_tip, plan


@pytest.fixture
def main_plan(tmp_path: Path) -> ReleasePlan:
    """Prepare the real-Git on-main plan outside assertion time."""
    repo = tmp_path / "repo"
    initialize_repository(repo)
    commit_file(repo, "main.txt", "main\n", "feat: release work")
    return build_release_plan(repo, preview_conflicts=False)


def test_plan_on_main_prepares_in_place(main_plan: ReleasePlan) -> None:
    """Starting from main never proposes a rebase or branch merge."""
    plan = main_plan

    assert plan.mode is ReleaseMode.ON_MAIN
    assert plan.action is ReleaseAction.PREPARE_IN_PLACE
    assert plan.scope == "v1.0.0..main"
    assert plan.operations == ("prepare version and release notes in place",)


def test_plan_integration_merges_no_ff_when_it_contains_main(
    integration_merge_plan: ReleasePlan,
) -> None:
    """A current integration branch is promoted directly with --no-ff."""
    plan = integration_merge_plan

    assert plan.mode is ReleaseMode.INTEGRATION
    assert plan.action is ReleaseAction.MERGE_NO_FF
    assert plan.merge_preview is not None
    assert plan.merge_preview.clean is True
    assert plan.operations[0] == "git switch --ignore-other-worktrees main"
    assert plan.operations[-1] == "git merge --no-ff develop"


@pytest.fixture
def configured_integration_plan(tmp_path: Path) -> ReleasePlan:
    """Prepare the configured integration plan outside assertion time."""
    repo = tmp_path / "repo"
    initialize_repository(repo)
    git(repo, "switch", "-c", "next")
    commit_file(repo, "next.txt", "next\n", "feat: integrated work")
    git(repo, "config", "prepare-release.integrationBranch", "next")
    return build_release_plan(repo, preview_conflicts=False)


def test_plan_uses_configured_integration_role(
    configured_integration_plan: ReleasePlan,
) -> None:
    """Repository config can name a non-develop integration branch."""
    plan = configured_integration_plan

    assert plan.integration_branch == "next"
    assert plan.mode is ReleaseMode.INTEGRATION
    assert plan.action is ReleaseAction.MERGE_NO_FF


def test_plan_integration_previews_main_sync_conflict(
    integration_conflict_plan: ReleasePlan,
) -> None:
    """A stale integration branch previews the main-into-integration sync first."""
    plan = integration_conflict_plan

    assert plan.action is ReleaseAction.SYNC_INTEGRATION_THEN_MERGE
    assert plan.merge_preview is not None
    assert plan.merge_preview.clean is False
    assert plan.merge_preview.conflicted_files == ("shared.txt",)
    assert plan.operations[1] == "git merge --no-ff main"


@pytest.fixture
def nested_feature_plan(tmp_path: Path) -> tuple[str, str, ReleasePlan]:
    """Prepare the real-Git nested-feature plan outside assertion time."""
    repo = tmp_path / "repo"
    initialize_repository(repo)
    git(repo, "switch", "-c", "develop")
    develop_tip = commit_file(repo, "parent.txt", "develop\n", "feat: parent work")
    git(repo, "switch", "-c", "feature")
    feature_tip = commit_file(repo, "feature.txt", "feature\n", "feat: selected work")
    git(repo, "switch", "main")
    commit_file(repo, "main.txt", "main\n", "fix: main work")

    plan = build_release_plan(
        repo,
        branch="feature",
        integration_branch="develop",
        feature_base=develop_tip,
    )
    return develop_tip, feature_tip, plan


def test_plan_nested_feature_uses_exact_onto_replay(
    nested_feature_plan: tuple[str, str, ReleasePlan],
) -> None:
    """A feature forked from develop replays only commits after that fork."""
    develop_tip, feature_tip, plan = nested_feature_plan

    assert plan.mode is ReleaseMode.FEATURE
    assert plan.action is ReleaseAction.REBASE_ONTO_MAIN_THEN_MERGE
    assert plan.feature_base == develop_tip
    assert [commit.oid for commit in plan.commits] == [feature_tip]
    assert plan.rebase_preview is not None
    assert plan.rebase_preview.clean is True
    assert plan.operations[1].startswith(f"git rebase --onto main {develop_tip}")


def test_plan_feature_can_land_on_current_integration(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Feature completion targets integration before release preparation."""
    _stub_feature_repository(
        monkeypatch,
        tmp_path,
        integration_exists=True,
        integration_contains_feature=True,
    )

    plan = build_release_plan(
        tmp_path,
        branch="feature",
        integration_branch="develop",
        feature_base="develop-tip",
        feature_target="integration",
        preview_conflicts=False,
    )

    assert plan.action is ReleaseAction.MERGE_NO_FF
    assert plan.feature_target_branch == "develop"
    assert plan.operations == (
        "git switch --ignore-other-worktrees develop",
        "git merge --no-ff feature",
    )


def test_plan_stale_feature_replays_only_its_range_onto_integration(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """An advanced integration branch gets an isolated feature replay."""
    _stub_feature_repository(
        monkeypatch,
        tmp_path,
        integration_exists=True,
    )

    plan = build_release_plan(
        tmp_path,
        branch="feature",
        integration_branch="develop",
        feature_base="develop-tip",
        feature_target="integration",
        preview_conflicts=False,
    )

    assert plan.action is ReleaseAction.REBASE_ONTO_INTEGRATION_THEN_MERGE
    assert [commit.oid for commit in plan.commits] == ["feature-tip"]
    assert plan.operations[1].startswith("git rebase --onto develop develop-tip")
    assert plan.operations[-2:] == (
        "git switch --ignore-other-worktrees develop",
        "git merge --no-ff prepare-release/feature-onto-develop",
    )


def test_plan_integration_target_requires_a_resolved_branch(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The planner cannot silently substitute main for a requested integration."""
    _stub_feature_repository(monkeypatch, tmp_path, integration_exists=False)

    with pytest.raises(ReleasePlanError, match="requires a resolved integration"):
        build_release_plan(
            tmp_path,
            feature_target="integration",
            preview_conflicts=False,
        )


def test_plan_rejects_an_unknown_feature_target(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Direct API callers receive an actionable target validation error."""
    _stub_feature_repository(monkeypatch, tmp_path, integration_exists=False)

    with pytest.raises(ReleasePlanError, match="Unknown feature target"):
        build_release_plan(
            tmp_path,
            feature_target="qa",
            preview_conflicts=False,
        )


@pytest.fixture
def auto_detected_boundary_plan(tmp_path: Path) -> tuple[str, ReleasePlan]:
    """Prepare automatic branch-boundary detection outside assertion time."""
    repo = tmp_path / "repo"
    base = initialize_repository(repo)
    git(repo, "switch", "-c", "feature")
    commit_file(repo, "feature.txt", "feature\n", "feat: feature")
    return base, build_release_plan(repo, preview_conflicts=False)


def test_plan_auto_detects_branch_creation_boundary(
    auto_detected_boundary_plan: tuple[str, ReleasePlan],
) -> None:
    """The latest branch-positioning reflog entry can prove the feature fork."""
    base, plan = auto_detected_boundary_plan

    assert plan.mode is ReleaseMode.FEATURE
    assert plan.action is ReleaseAction.MERGE_NO_FF
    assert plan.feature_base == base
    assert plan.boundary_evidence is not None
    assert plan.boundary_evidence.startswith("reflog:")


@pytest.fixture
def already_released_plan(tmp_path: Path) -> tuple[str, ReleasePlan]:
    """Prepare an already-released feature plan outside assertion time."""
    repo = tmp_path / "repo"
    initialize_repository(repo)
    git(repo, "switch", "-c", "feature")
    feature_tip = commit_file(repo, "feature.txt", "feature\n", "feat: feature")
    git(repo, "switch", "main")
    git(repo, "merge", "--no-ff", "feature", "-m", "merge feature")
    git(repo, "tag", "v1.1.0")
    plan = build_release_plan(repo, branch="feature", preview_conflicts=False)
    return feature_tip, plan


def test_plan_stops_feature_already_contained_by_release_tag(
    already_released_plan: tuple[str, ReleasePlan],
) -> None:
    """An old feature tip produces no empty replay when main already released it."""
    feature_tip, plan = already_released_plan

    assert plan.branch_oid == feature_tip
    assert plan.action is ReleaseAction.ALREADY_RELEASED
    assert plan.containing_release_tags == ("v1.1.0",)


@pytest.fixture
def orphan_boundary_plan(tmp_path: Path) -> ReleasePlan:
    """Prepare an orphan-branch boundary plan outside assertion time."""
    repo = tmp_path / "repo"
    initialize_repository(repo)
    git(repo, "switch", "--orphan", "rescue")
    commit_file(repo, "orphan.txt", "orphan\n", "feat: unrelated history")
    return build_release_plan(repo, preview_conflicts=False)


def test_plan_orphan_branch_requires_a_boundary(orphan_boundary_plan: ReleasePlan) -> None:
    """A branch without provable topology stops instead of guessing a base."""
    plan = orphan_boundary_plan

    assert plan.mode is ReleaseMode.FEATURE
    assert plan.action is ReleaseAction.NEEDS_FEATURE_BOUNDARY
    assert plan.boundary_candidates == ()
    assert plan.commits == ()
    assert any("--feature-base" in note for note in plan.notes)


@pytest.fixture
def explicit_merge_scope_plan(tmp_path: Path) -> tuple[str, ReleasePlan]:
    """Prepare the explicit merge-scope plan outside assertion time."""
    repo = tmp_path / "repo"
    base = initialize_repository(repo)
    git(repo, "switch", "-c", "feature")
    commit_file(repo, "feature.txt", "feature\n", "feat: feature change")
    git(repo, "switch", "-c", "side")
    commit_file(repo, "side.txt", "side\n", "feat: side change")
    git(repo, "switch", "feature")
    git(repo, "merge", "--no-ff", "side", "-m", "merge side")
    plan = build_release_plan(
        repo,
        branch="feature",
        feature_base=base,
        preview_conflicts=False,
    )
    return base, plan


def test_plan_flags_merges_inside_an_explicit_feature_scope(
    explicit_merge_scope_plan: tuple[str, ReleasePlan],
) -> None:
    """A feature range containing a merge asks for explicit commit selection."""
    base, plan = explicit_merge_scope_plan

    assert plan.action is ReleaseAction.NEEDS_FEATURE_BOUNDARY
    assert plan.feature_base == base
    assert plan.commits != ()
    assert any("contains merges" in note for note in plan.notes)


@pytest.fixture
def direct_merge_plan(tmp_path: Path) -> tuple[str, ReleasePlan]:
    """Prepare a direct-merge preview plan outside assertion time."""
    repo = tmp_path / "repo"
    base = initialize_repository(repo)
    git(repo, "switch", "-c", "feature")
    commit_file(repo, "feature.txt", "feature\n", "feat: feature change")
    return base, build_release_plan(repo)


def test_plan_direct_merge_previews_conflicts(
    direct_merge_plan: tuple[str, ReleasePlan],
) -> None:
    """A feature still rooted at the main tip previews the merge itself."""
    base, plan = direct_merge_plan

    assert plan.action is ReleaseAction.MERGE_NO_FF
    assert plan.feature_base == base
    assert plan.merge_preview is not None
    assert plan.merge_preview.clean is True


def test_plan_explicit_parent_uses_the_first_parent_merge_boundary(
    explicit_parent_plan: tuple[str, ReleasePlan],
) -> None:
    """A parent branch that merged the feature proves the fork point."""
    base, plan = explicit_parent_plan

    assert plan.feature_base == base
    assert plan.boundary_evidence == "first-parent merge into develop"
    assert plan.action is ReleaseAction.MERGE_NO_FF


@pytest.fixture
def explicit_parent_boundary_error(tmp_path: Path) -> ReleasePlanError:
    """Capture an underivable parent-boundary error outside assertion time."""
    repo = tmp_path / "repo"
    initialize_repository(repo)
    git(repo, "switch", "-c", "feature")
    commit_file(repo, "feature.txt", "feature\n", "feat: feature change")
    git(repo, "branch", "twin", "feature")

    with pytest.raises(ReleasePlanError) as caught:
        build_release_plan(
            repo,
            branch="feature",
            feature_parent="twin",
            preview_conflicts=False,
        )
    return caught.value


def test_plan_explicit_parent_without_a_boundary_fails(
    explicit_parent_boundary_error: ReleasePlanError,
) -> None:
    """A parent giving no derivable fork point raises instead of guessing."""
    assert "Could not derive a boundary" in str(explicit_parent_boundary_error)


@pytest.fixture
def explicit_base_error(tmp_path: Path) -> ReleasePlanError:
    """Capture the improper explicit-base error outside assertion time."""
    repo = tmp_path / "repo"
    initialize_repository(repo)
    git(repo, "switch", "-c", "feature")
    commit_file(repo, "feature.txt", "feature\n", "feat: feature change")

    with pytest.raises(ReleasePlanError) as caught:
        build_release_plan(repo, branch="feature", feature_base="feature", preview_conflicts=False)
    return caught.value


def test_plan_explicit_base_must_be_a_proper_ancestor(explicit_base_error: ReleasePlanError) -> None:
    """The branch tip itself is rejected as its own feature base."""
    assert "not a proper ancestor of feature" in str(explicit_base_error)


def test_plan_rebased_feature_uses_the_reflog_onto_evidence(
    rebased_feature_plan: tuple[str, ReleasePlan],
) -> None:
    """A completed rebase leaves the exact new base in the branch reflog."""
    main_tip, plan = rebased_feature_plan

    assert plan.feature_base == main_tip
    assert plan.boundary_evidence is not None
    assert plan.boundary_evidence.startswith("reflog: rebase")
    assert plan.action is ReleaseAction.MERGE_NO_FF


@pytest.fixture
def reset_reflog_plan(tmp_path: Path) -> tuple[str, ReleasePlan]:
    """Prepare reset reflog evidence outside assertion time."""
    repo = tmp_path / "repo"
    base = initialize_repository(repo)
    git(repo, "switch", "-c", "feature")
    commit_file(repo, "feature.txt", "feature\n", "feat: discarded work")
    git(repo, "reset", "--hard", "main")
    commit_file(repo, "feature.txt", "again\n", "feat: kept work")
    return base, build_release_plan(repo, preview_conflicts=False)


def test_plan_reset_reflog_entry_wins_as_latest_evidence(
    reset_reflog_plan: tuple[str, ReleasePlan],
) -> None:
    """The newest branch-positioning entry supersedes the creation entry."""
    base, plan = reset_reflog_plan

    assert plan.feature_base == base
    assert plan.feature_parent_refs == ("main",)
    assert plan.boundary_evidence == "reflog: reset: moving to main"


def test_plan_single_parent_candidate_is_selected_without_ranking(
    single_parent_plan: tuple[str, ReleasePlan],
) -> None:
    """One surviving parent candidate is the boundary without a nearest vote."""
    base, plan = single_parent_plan

    assert plan.feature_base == base
    assert plan.boundary_evidence == "merge-base main feature"
    (candidate,) = plan.boundary_candidates
    assert candidate.parent_refs == ("main",)
    assert plan.action is ReleaseAction.REBASE_ONTO_MAIN_THEN_MERGE


def test_plan_ambiguous_parents_select_the_unique_nearest_boundary(
    ambiguous_parent_plan: tuple[str, ReleasePlan],
) -> None:
    """Without reflogs, deduplicated candidates elect the nearest fork point."""
    fork_point, plan = ambiguous_parent_plan

    assert plan.feature_base == fork_point
    assert plan.feature_parent_refs == ("develop",)
    assert len(plan.boundary_candidates) == _EXPECTED_CANDIDATES
    # The two same-base candidates from main and other merge into one entry.
    assert plan.boundary_candidates[1].parent_refs == ("main", "other")
    assert plan.action is ReleaseAction.REBASE_ONTO_MAIN_THEN_MERGE


# eof
