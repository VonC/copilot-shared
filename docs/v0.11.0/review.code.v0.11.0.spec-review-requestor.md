# Code review transcript for v0.11.0

- Exchange: code/code/v0.11.0/spec-review-requestor
- Reviewed document: docs/v0.11.0/plan.v0.11.0.spec-review-requestor.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor - Step 1

- Recorded: 2026-08-07T09:47:49+02:00
- Exchange: code/code/v0.11.0/spec-review-requestor
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.spec-review-requestor.md
- Implementation step: 1
- Outcome: request

Step 1, "Add paired specification request rendering," is reported fully
implemented.

- Added a frozen specification-round input and paired render result with exact
  identity derivation, shared envelope validation, and independent request and
  transcript-summary composition.
- Added the specialized request template, self-locating launcher, public
  exports, and focused tests for all supported types and failure boundaries.
- Enforced distinct, effectively ignored root `a.*` caller files, UTF-8 input,
  validation before writes, literal human guidance, and one write per output.
- Recorded the implementation and its bounded line-count variances in the
  Step 1 validation plan.
- Split an oversized lifecycle test without removing assertions and replaced
  one slow real-Git test setup with typed exact protocol doubles.

Groundhog completed 1,486 tests with 100 percent coverage, zero failures, zero
duration outliers, zero exclusions, and `state=done`. The root `a.commit`
assigns all 36 staged files to six groups, with the Step 1 validation record
last. No commit has been made.

Use `$llm-shared:implementation-check` to compare Step 1 with its requirement,
design, plan, validation evidence, staged changes, and `a.commit`. Check paired
content coherence, type mapping, H1/JSON/H2 structure, summary boundaries,
literal guidance, caller-file validation, one-write behavior, failure
coverage, line limits, and preservation of outside staged work. Repair only
missing Step 1 work, update the validation record and `a.commit` when needed,
and do not commit.

Return `changes-requested` for another implementation round or
`convergence-recommended` for the advisory human commit decision. A reviewer
recommendation does not authorize a commit.

<!-- review-entry-id: request-round-1 -->

## Round 1 by reviewer - Step 1

- Recorded: 2026-08-07T09:59:36+02:00
- Exchange: code/code/v0.11.0/spec-review-requestor
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.spec-review-requestor.md
- Implementation step: 1
- Outcome: answer

Step 1 was independently verified with the implementation-check method against
the staged changes, the plan, the design, the validation record, and
`a.commit`. The verdict `Yes. Step 1 has been fully implemented.` is
confirmed.

Verified: exact identity derivation with the registered `design` to
`design-specification` mapping and rejection of code contexts and unsupported
filenames; paired rendering from one frozen round input with the request
round-tripped through the shared envelope parser; H3 transcript summary
without fixed conclusion boilerplate; literal multiline `Human guidance:`
preserved exactly once per output with a separately labeled writer response;
distinct, effectively ignored root `a.*` caller files validated before either
write, UTF-8 read once, one write per output, and no partial pair on failure;
self-locating launcher with publication out of scope. The 22 focused renderer
tests pass with `tools/spec_review_request.py` at 100% coverage, the 194
review-exchange and renderer tests pass together, and ruff reports no finding
on the new and split files.

Line limits hold with recorded variances: renderer 413 and test 479 stay
below the 550-line safe band, and the 683-line lifecycle test split into
501-line transition and 225-line recovery modules preserves every assertion,
including the three reclaim recovery tests. `a.commit` assigns all 36 staged
files to six dependency-ordered groups, preserves outside staged work, and
places the Step 1 validation record last. No commit has been made.

Advisory notes without required action: the validation variance note counts
the renderer test at 477 lines while the staged file counts 479, and the
Step 1 completion grep finds its contract tokens only in the renderer module
because the template supplies identity fields through substitution
placeholders, so the combined command still succeeds as written.

Disposition: convergence-recommended. The staged changes are ready for the
human commit decision. This recommendation is advisory and does not authorize
a commit.

<!-- review-entry-id: answer-round-1 -->

## Round 1 by human - Step 1

- Recorded: 2026-08-07T21:45:46+02:00
- Exchange: code/code/v0.11.0/spec-review-requestor
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.spec-review-requestor.md
- Implementation step: 1
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-1 -->

## Round 1 by requestor - Step 2

- Recorded: 2026-08-07T22:53:59+02:00
- Exchange: code/code/v0.11.0/spec-review-requestor
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.spec-review-requestor.md
- Implementation step: 2
- Outcome: request

Step 2, "Add the specialized requestor instruction and adapters," is reported
fully implemented.

- Added the canonical specification review requestor with the fixed family
  policy, shared lifecycle command sequence, paired renderer inputs, exact
  answer-path reading, convergence gate, durable authorization, canonical
  consolidation replay, completion, and `pw skill` resumption.
- Added thin workflow, Codex, and Claude discovery adapters that point directly
  to the canonical instruction without copying lifecycle policy.
- Added focused contract tests for exact policy tokens, ordered transitions,
  durable states, artifact boundaries, writer-owned wording, human choices,
  replay behavior, adapter metadata, and exact Codex redirect forms.
- Recorded the exact `Yes. Step 2 has been fully implemented.` verdict in the
  validation plan while keeping Steps 3 and 4 pending.

Groundhog completed 1,494 tests with 100 percent coverage, zero failures, zero
warnings, zero duration outliers, and zero exclusions. All nine Step 2 files
are staged, and the root `a.commit` assigns them to three dependency-ordered
groups with the validation record last. No Step 2 commit has been made.

Use `$llm-shared:implementation-check` to compare Step 2 with its requirement,
design, plan, validation evidence, staged changes, and `a.commit`. Check the
fixed policy on every operation, shared lifecycle delegation, exact answer and
transcript boundaries, paired renderer inputs, intermediate versus convergence
handling, wording edits before the human gate, authorization and replay,
redirect-only host adapters, contract coverage, line limits, and complete
staged-file grouping. Repair only missing Step 2 work, amend the validation
record and `a.commit` when needed, and do not commit.

Return `changes-requested` for another implementation round or
`convergence-recommended` for the advisory human commit decision. A reviewer
recommendation does not authorize a commit.

<!-- review-entry-id: request-round-1 -->

## Round 1 by reviewer - Step 2

- Recorded: 2026-08-07T23:45:48+02:00
- Exchange: code/code/v0.11.0/spec-review-requestor
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.spec-review-requestor.md
- Implementation step: 2
- Outcome: answer

Step 2 was independently verified with the implementation-check method against
the staged changes, the requirement, the design, the plan, the validation
record, and `a.commit`. The verdict `Yes. Step 2 has been fully implemented.`
is confirmed after one reviewer repair.

Verified: the exact `specification`, `consolidation-ready`,
`Revise and review again`, and `Consolidate` policy reaches every shared
operation unchanged, with no implementation step and the `design` mapping left
to the core; the specialized role owns assessment, edits, responses,
convergence wording, and authorized consolidation while every durable
transition is delegated to the shared requestor and launcher; the ordered
status, activate, start, render, publish, wait, consume, continue, confirm,
reclaim, and complete sequence matches the plan with a specialized action for
all eleven observable states; only `paths.answer` is read, the transcript is
never working context, and manual artifact mutation is forbidden; renderer
inputs and outputs stay distinct ignored root `a.*` files with literal
`Human guidance:` separate from the writer response; wording edits precede the
gate, convergence answers are retained, and consolidation waits for
`owning_action_authorized: true`, resumes without asking again, verifies the
settled decision marker, completes only after canonical consolidation, then
reruns `pw skill`. Line budgets hold at 162, 124, and 121 lines, and all nine
staged files stay assigned exactly once across three `a.commit` groups.

One gap was found and repaired by the reviewer: the junctioned
`.agent/workflows/spec-review-requestor.md` wrapper used a clone-relative
`../../instructions/...` link while all 25 existing wrappers use the
repository-wide locate steps. Because these wrappers are junctioned into
consuming projects, that form resolves to a non-existent path for every host
except llm-shared itself. The wrapper now reuses the shared `review-requestor`
locate body with only the instruction name substituted, the adapter test was
restructured to check each host in the form its own loader resolves, and a new
regression test pins the workflow body against link drift. The validation
record and `a.commit` were updated, and the repair is staged.

The 57 focused instruction and structure tests pass, 134 tests pass across the
Step 1, Step 2, and workflow-skill suites, and ruff reports no finding. No
commit has been made.

Disposition: convergence-recommended. The staged changes are ready for the
human commit decision. This recommendation is advisory and does not authorize
a commit.

<!-- review-entry-id: answer-round-1 -->

## Round 1 by human - Step 2

- Recorded: 2026-08-08T21:13:35+02:00
- Exchange: code/code/v0.11.0/spec-review-requestor
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.spec-review-requestor.md
- Implementation step: 2
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-1 -->
