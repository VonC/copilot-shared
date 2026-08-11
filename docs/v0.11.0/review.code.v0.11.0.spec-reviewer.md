# Code review transcript for v0.11.0

- Exchange: code/code/v0.11.0/spec-reviewer
- Reviewed document: docs/v0.11.0/plan.v0.11.0.spec-reviewer.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor - Step 1

- Recorded: 2026-08-11T12:45:33+02:00
- Exchange: code/code/v0.11.0/spec-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.spec-reviewer.md
- Implementation step: 1
- Outcome: request

Step 1, "Route pending requests to the specification reviewer," is reported
fully implemented.

- Added frozen `LiveSpecificationRoute` snapshots so one fixed-context pass
  retains both the exact document and its observed exchange state.
- Routed ordinary `request-pending` work to `spec-reviewer`; cold abandoned and
  writer-owned live states remain assigned to `spec-review-requestor`.
- Added forced `spec-reviewer` selection for an exact pending request, no-route
  handling for absent or writer-owned work, and an identity-bearing requestor
  reclaim diagnostic for a cold abandoned request.
- Extracted post-commit topic discovery to
  `tools/prompt_workflow_post_commit.py` while retaining
  `post_commit_command` in the skill router. The planned fallback also moved
  host rendering to `tools/prompt_workflow_render.py` with compatibility
  exports.
- Added example and property tests for immutable routes, all artifact-state
  owners, one three-context classification pass, host prefixes, exact target
  paths, ambiguity, marker gating, and forced recovery behavior.
- Recorded the completed Step 1 implementation check. The final module counts
  are 201 lines for `prompt_workflow_review.py`, 551 for
  `prompt_workflow_skill.py`, 91 for `prompt_workflow_post_commit.py`, and 47
  for `prompt_workflow_render.py`.
- Moved two unrelated real-Git test preparations into fixtures after the
  duration gate identified their measured call phases. Their assertions and
  real subprocess paths remain intact.

Groundhog completed 1,546 tests with 100 percent coverage, zero failures, zero
duration outliers, zero exclusions, and `exit=0`. The root `a.commit` assigns
all 21 staged files to five groups, retains the pre-existing staged Humanizer
skill, and places the Step 1 validation record last. No commit has been made.

Use the implementation-check method to compare Step 1 with the requirement,
design, plan, validation evidence, staged changes, and `a.commit`. Check the
single-observation route, exact state ownership, forced cold-recovery behavior,
one-way module splits, generated state-to-owner property, line budgets, full
test evidence, preservation of outside staged work, and trailing validation
group. Repair only missing Step 1 work, update the validation record and
`a.commit` when needed, and do not commit.

Return `changes-requested` for another implementation round or
`convergence-recommended` for the advisory human commit decision. A reviewer
recommendation does not authorize a commit.

<!-- review-entry-id: request-round-1 -->

## Round 1 by reviewer - Step 1

- Recorded: 2026-08-11T13:20:45+02:00
- Exchange: code/code/v0.11.0/spec-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.spec-reviewer.md
- Implementation step: 1
- Outcome: answer

Step 1 was independently checked against the requirement, design, plan,
validation record, staged changes, and `a.commit`. The verdict
`Yes. Step 1 has been fully implemented.` is confirmed after two reviewer
repairs.

The module split matches the plan and its dependency direction holds:
`prompt_workflow_post_commit.py` imports only documentation discovery and
shared models, `prompt_workflow_render.py` imports nothing from the package,
and the skill router imports both one way, so no cycle exists.
`post_commit_command` correctly remains in the router, the specific trap the
plan was amended to prevent. All four reported counts are exact at 201, 551,
91, and 47, leaving the router 99 lines below the ceiling because the step took
both the post-commit extraction and the render fallback the plan named as
likely.

Routing matches the design's state table. `LiveSpecificationRoute` is frozen
with context and observed state, `live_specification_route` preserves that
snapshot, and `live_specification_document` survives as a thin wrapper.
Ordinary selection maps `request-pending` to `spec-reviewer` and every other
live state to `spec-review-requestor`, while forced reviewer routing renders
only for an exact pending request, returns nothing for writer-owned states, and
raises the identity-bearing reclaim diagnostic for a cold abandoned request, as
Q02 requires. The property test samples every `ArtifactState`, drives the real
`next_command` selector, asserts the frozen snapshot, separates reviewer,
requestor, and no-route outcomes, and pins `classifications == 3` so a second
classification cannot creep in.

`a.commit` lists all 21 staged files exactly once across five dependency-ordered
groups, preserves the outside Humanizer skill, and places validation last. The
92 focused tests pass, ruff is clean, and no commit was made.

Two gaps were repaired. `def next_command` still had one blank line where every
other top-level definition uses two; the sibling effort recorded that repair as
blocked while the module sat at exactly 650 lines and asked for this very
split first, and Step 1 then added `SPEC_REVIEWER` in that spot without
restoring it. At 551 lines the blocked repair is finally possible and is now
applied, leaving the file at 552 with every definition consistent. The router
also imported `ArtifactState` from the `review_exchange_state` classifier that
only re-exports it; it now names the owning `review_exchange_models` module,
matching `prompt_workflow_review.py` and this step's own property test. Both
repairs are staged, `a.commit` needed no change, and the validation record
names them.

Disposition: convergence-recommended. The staged changes are ready for the
advisory human commit decision. This recommendation does not authorize a
commit.

<!-- review-entry-id: answer-round-1 -->

## Round 1 by human - Step 1

- Recorded: 2026-08-11T13:46:28+02:00
- Exchange: code/code/v0.11.0/spec-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.spec-reviewer.md
- Implementation step: 1
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-1 -->
