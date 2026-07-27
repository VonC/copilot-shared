---
name: prepare-release
description: 'Prepare a release from main, a long-lived integration branch such as develop, or a feature branch created from main, integration, or another feature. Apply gitworkflow topic graduation and preview conflicts; for unsupported selections, stop with an evidence-backed manual runbook. Audit existing wiki/ or docs/wiki/ Diataxis roots against every commit in the release range, prepare release artifacts, make one chore(release) prepare commit, stop before brel, and never push. Use when the user asks to prepare or cut a release.'
user-invocable: true
argument-hint: 'Explain the release context from main, develop/integration, or any feature branch. The skill automatically runs the planner; ambiguous feature ancestry pauses for a parent branch or boundary commit.'
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
