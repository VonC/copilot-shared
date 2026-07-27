---
name: prepare-release
description: 'Prepare a release from main, a long-lived integration branch such as develop, or a feature branch created from main, integration, or another feature. Plan topology and conflicts; prepare main in place, merge integration wholesale, or replay only confirmed feature commits before a --no-ff merge. Stop unsupported selections with an evidence-backed manual runbook. Audit existing wiki/ or docs/wiki/ Diataxis roots against every release commit, prepare release artifacts, make one chore(release) prepare commit, stop before brel, and never push.'
user-invocable: true
metadata:
  - "This skill prepares every release artifact and stops before brel; it never creates the tag and never pushes."
  - "Step 1-2: find the last tag (git describe --tags --abbrev=0) and detect a development effort (a commit since the tag touching docs/{feature,issue,design,plan}.*). With none, stop with 'release already done' (HEAD on a tag) or 'nothing to release yet'."
  - "Step 3: classify on-main, integration, or feature mode; in feature mode recover the actual fork from reflog and branch topology, show and confirm the exact feature-only range, and stop for a boundary when Git evidence is ambiguous."
  - "Apply gitworkflow topic graduation (one word, not GitFlow): a feature merged to develop can be merged independently to main; develop-to-main is only the explicit all-topics-ready bulk exception. Reject an empty main..integration range. For all-but-one, arbitrary-subset, or merge-containing ranges, stop before mutation and output actual OIDs, safe manual commands, verification, and the exact prepare-release re-entry branch."
  - "Before mutation, automatically locate and run prepare_release_plan.bat for deterministic topology and Git 2.50+ merge-tree conflict evidence; never ask the user to run it. Preview merges once and feature rebases commit by commit, stopping at the first predicted conflict."
  - "Step 4-5: make the current worktree clean and bring local main current; never rebase integration; for a feature not safely on latest main, create a promotion branch and rebase --onto main from the confirmed boundary, verify with range-diff, then run ghog day."
  - "Step 6-7: on main prepare in place; otherwise confirm the selected scope, switch to main with git switch --ignore-other-worktrees main, merge --no-ff the integration, feature, or promotion branch, and reword the merge with Why:/What:."
  - "Step 8: when wiki/ or docs/wiki/ exists, call review-and-update-project-docs for every existing root against the complete last_tag..HEAD release range; stop on uncovered topics, and commit reviewed wiki changes before release notes."
  - "Step 9-13: set version.txt to X.Y.Z-SNAPSHOT, call prepare_release_notes for the summary and changelog, pause for notes review, update pyproject.toml and uv when present, then make one chore(release): prepare for vX.Y.Z release commit."
  - "Step 14: report a summary and tell the user to review and run brel. It uses the flag file a.prepare-release.active (git-ignored, deleted at start, created before each sub-skill call, removed on exit) so the called skills return control to it."
---

[Instruction](../../../instructions/prepare-release.md)

Implementation is mutualized across the shared directories:

- [`../instructions/prepare-release.md`](../../../instructions/prepare-release.md)
  — the full workflow.

This skill calls the `group-commits-msg`, `update-merge-commit-msg`,
`review-and-update-project-docs`, and `prepare_release_notes` skills, and runs
the `ghog day` groundhog loop when it rebases the branch or merges a stale
base, using the flag file
`a.prepare-release.active` (git-ignored) so the called skills return control
to it instead of ending standalone. It readies every release artifact and
stops at the `chore(release): prepare for vX.Y.Z release` commit; the next
step is for the user to review and run `brel` to build and tag. The skill
never creates a tag and never pushes to a remote.
