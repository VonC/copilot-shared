---
name: prepare-release
description: 'Finish a feature by landing its exact range on develop when present, otherwise main, reword the merge, and stop with the next umbrella requirement from pw skill. When the umbrella is exhausted, or when invoked from main or integration for a release, continue through topology checks, the Diataxis wiki audit, release artifacts, and one chore(release) prepare commit. Stop before brel and never push. Use when the user asks to finish a feature or prepare a release.'
user-invocable: true
argument-hint: 'Explain the context from main, develop/integration, or any feature branch. Feature mode lands the requirement first and checks its umbrella; ambiguous ancestry pauses for a parent branch or boundary commit.'
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
