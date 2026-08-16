# Code review transcript for v0.11.0

- Exchange: code/code/v0.11.0/code-reviewer
- Reviewed document: docs/v0.11.0/plan.v0.11.0.code-reviewer.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor - Step 1

- Recorded: 2026-08-15T17:12:29+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 1
- Outcome: request

### Review identity for step 1 code-reviewer round 1

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: docs/v0.11.0/plan.v0.11.0.code-reviewer.md
Implementation step: 1
Review round: 1

### Code review evidence for step 1 code-reviewer round 1

request_index_tree: b0d97d2b88159d23ac5627f854363ca531a08b38
resolved_validation_set:

- ghog day (sources: project)
- ghog single tests/unit/tools/test_code_review_evidence/test_code_review_evidence_tdd.py tests/unit/tools/test_code_review_validation tests/unit/tools/test_code_review_request tests/unit/tools/test_code_review_requestor_acceptance (sources: plan)
- rg -n 'capture_index_tree|Code review evidence|request_index_tree|resolved_validation_set' tools/code_review_evidence.py tools/code_review_request.py templates/code-review-request.template.md instructions/code-review-requestor.md (sources: plan)

### Requestor assessment for step 1 code-reviewer round 1

Step 1 is fully implemented against the numbered plan and its validation
checklist. The staged implementation adds one shared request-time Git index
tree capture and one immutable resolved validation set, then carries both
through the paired request content and transcript summary from the same typed
round input.

The implementation check found the slice complete. Architecture remains split
between capture, validation resolution, and request rendering; command and
path processing remain linear in their inputs; focused unit coverage is 100%;
and the existing shared envelope, safe ignored-file IO, and code-family
routing behavior remain intact.

Groundhog completed with all static checks passing, all 1,693 tests passing,
100% project coverage, and no duration outliers. Step 2 has not started.

### Implementation report for step 1 code-reviewer round 1

Implemented the Step 1 immutable request-evidence slice:

- added `capture_index_tree` in `tools/code_review_evidence.py` as the single
  requestor/reviewer implementation of Git index-tree capture;
- added immutable resolved-validation command and set types plus additive,
  source-preserving resolution in `tools/code_review_validation.py`;
- extended `tools/code_review_request.py` so the CLI captures the publication-
  time index tree, accepts repeatable plan and request validation commands,
  and renders a distinct `## Code review evidence` JSON block;
- updated the request template and canonical requestor instruction to document
  the evidence contract; and
- added focused unit, instruction, acceptance, IO, temporary-repository, and
  round-trip coverage for the new behavior and preserved contracts.

The required validation-plan row records completion, architecture,
performance, coverage, feature-integrity, and the successful Groundhog result.

### Change summary for step 1 code-reviewer round 1

Staged paths for Step 1:

- `docs/v0.11.0/plan.v0.11.0.code-reviewer.validation.md`
- `instructions/code-review-requestor.md`
- `templates/code-review-request.template.md`
- `tests/unit/tools/test_code_review_evidence/__init__.py`
- `tests/unit/tools/test_code_review_evidence/test_code_review_evidence_tdd.py`
- `tests/unit/tools/test_code_review_request/test_code_review_request_tdd.py`
- `tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_acceptance_tdd.py`
- `tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_io_acceptance_tdd.py`
- `tests/unit/tools/test_code_review_requestor_instruction/test_code_review_requestor_instruction_tdd.py`
- `tests/unit/tools/test_code_review_validation/__init__.py`
- `tests/unit/tools/test_code_review_validation/test_code_review_validation_tdd.py`
- `tools/code_review_evidence.py`
- `tools/code_review_request.py`
- `tools/code_review_validation.py`

`a.commit` accounts for every staged path in three groups:

1. `feat(code-review): add request evidence types`
2. `feat(code-review): publish immutable evidence`
3. `docs(code-reviewer): record step 1 validation`

There are no unrelated staged paths. The validation-plan update is review
metadata and is isolated in the required trailing documentation group.

### Writer response for step 1 code-reviewer round 1

Writer response: This is Round 1, so there is no earlier reviewer feedback or writer
disagreement. Review the exact Step 1 scope, staged implementation and tests,
validation evidence, and whether `a.commit` accurately groups every staged
path. Leave any bounded reviewer repairs staged and report each repaired path.
Do not assess or begin the deferred Step 2 work.

### Reviewer focus for step 1 code-reviewer round 1

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-round-1 -->

## Round 1 by reviewer - Step 1

- Recorded: 2026-08-15T17:21:41+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 1
- Outcome: answer

### Assessed staged state for step 1 code-reviewer round 1

Request-time index tree `b0d97d2b88159d23ac5627f854363ca531a08b38` matched the
live index tree exactly before assessment, so this round assessed the published
subject. After the reviewer repair the index tree is
`9aae9a44bf86a6a5b898a88cb191e0432fa2572c`. The staged set holds exactly the
fourteen paths the change summary lists, with no unrelated staged content. The
untracked versioned transcript was deliberately left unstaged.

### Implementation assessment for step 1 code-reviewer round 1

Step 1 is implemented against the numbered plan. `capture_index_tree` is the
single capture implementation, reads the index rather than the worktree, and
validates SHA-1 and SHA-256 object shapes. `tools/code_review_validation.py`
resolves project defaults plus plan and request additions additively, with
per-command source attribution, deterministic order, and no removal operation.
`CodeReviewRoundInput` requires both evidence fields and receives the tree from
the shared helper instead of computing it. One typed value feeds both the
canonical JSON under the distinct `## Code review evidence` heading and the
paired human summary, and the shared `## JSON` envelope is untouched, which this
round's own request artifact demonstrates. Line budgets hold: 453 against 470,
36 against 80, 94 against 220, and 490 against 525.

### Repairs made in step 1 code-reviewer round 1

Staged: `tests/unit/tools/test_code_review_validation/__init__.py`, removing a
trailing blank line that failed `git diff --cached --check` and disagreed with
both sibling package files. Substantive, because it changes a tracked file other
than `a.commit`.

Reverted: an attempted line-ending normalization of `tools/code_review_request.py`,
returned to the writer's exact staged bytes for the reason recorded below.

### Findings returned to the writer for step 1 code-reviewer round 1

Mixed line endings in `tools/code_review_request.py` inflate the staged diff by
33 phantom line changes: the blob is `i/mixed` while every sibling is `i/lf`,
and `git diff --cached --ignore-cr-at-eol` reduces 104 insertions and 33
deletions to 71 insertions with no deletions. Both repair directions cross the
bounded-repair boundary, since LF normalization rewrites all 453 lines and CRLF
normalization makes the repository whitespace check report all 71 added lines,
so the convention decision belongs to the writer. The root cause is the absent
`text=auto` rule that leaves this file a CRLF outlier in an LF tree.

The versioned transcript is in no `a.commit` group and will be left behind
unless it is staged and added to the documentation group before committing.

Minor and non-blocking: the resolved-set guard uses `__class__ is not` where
`isinstance` is the ordinary idiom.

### Validation evidence for step 1 code-reviewer round 1

The focused plan command reports `fail=0 warn=0 xfail=0 exit=0` after the
repair. The plan completion grep finds all four evidence identifiers across the
four owning surfaces, 25 matches. `git diff --cached --check` exits 0 after the
repair and exited 2 before it. `ghog day` was not re-run by this review, since
the only repair is one blank line in a package docstring file and this round
requests changes rather than recommending readiness; it must be re-run before
the readiness round.

### a.commit assessment for step 1 code-reviewer round 1

Accurate, no amendment needed. Three groups account for all fourteen staged
paths exactly once, subjects are conventional and correctly ordered from
foundations to consumer to documentation, and the repair landed inside an
existing group, so membership and grouping are unchanged. No commit was created.

### Final reviewer decision for step 1 code-reviewer round 1

Decision: changes-requested. A substantive staged change in this round forbids a
commit-readiness recommendation, and the line-ending finding needs a writer
decision. The recommendation is advisory and authorizes no commit.

<!-- review-entry-id: answer-round-1 -->

## Round 2 by requestor - Step 1

- Recorded: 2026-08-15T19:03:16+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 1
- Outcome: request

### Review identity for step 1 code-reviewer round 2

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: docs/v0.11.0/plan.v0.11.0.code-reviewer.md
Implementation step: 1
Review round: 2

### Code review evidence for step 1 code-reviewer round 2

request_index_tree: 79915cab1824e3845e8242eddbc55c34fb3aab1c
resolved_validation_set:

- ghog day (sources: project)
- ghog single tests/unit/tools/test_code_review_evidence/test_code_review_evidence_tdd.py tests/unit/tools/test_code_review_validation tests/unit/tools/test_code_review_request tests/unit/tools/test_code_review_requestor_acceptance (sources: plan)
- rg -n 'capture_index_tree|Code review evidence|request_index_tree|resolved_validation_set' tools/code_review_evidence.py tools/code_review_request.py templates/code-review-request.template.md instructions/code-review-requestor.md (sources: plan)

### Requestor assessment for step 1 code-reviewer round 2

Step 1 is fully implemented against the numbered plan and its validation
checklist. The staged implementation adds one shared request-time Git index
tree capture and one immutable resolved validation set, then carries both
through the paired request content and transcript summary from the same typed
round input.

The implementation check found the slice complete. Architecture remains split
between capture, validation resolution, and request rendering; command and
path processing remain linear in their inputs; focused unit coverage is 100%;
and the existing shared envelope, safe ignored-file IO, and code-family
routing behavior remain intact.

Round 1's trailing-blank repair is correct and remains staged. The mixed line
endings in `tools/code_review_request.py` are deliberately retained because
normalizing the whole outlier is repository-convention work outside this
feature slice. The versioned review transcript is now staged and accounted for
in the documentation commit group; the frozen payload's exact-type guard is
also deliberately retained.

The original implementation Groundhog run completed with all static checks
passing, all 1,693 tests passing, 100% project coverage, and no duration
outliers. Post-review walks kept tests and coverage green while exposing
duration-only gates. Profiling moved repeated Git setup outside measured calls,
split all 15 route states into exhaustive parametrized calls, and removed an
unnecessary dashboard export without removing assertions or faking production
reads. The three non-Step-1 maintenance paths are isolated in `a.commit`. The
final walk reached `state=done exit=0` with all 1,707 tests passing, 100%
coverage, zero outliers, and zero exclusion regressions. Step 2 has not started.

### Implementation report for step 1 code-reviewer round 2

Implemented the Step 1 immutable request-evidence slice:

- added `capture_index_tree` in `tools/code_review_evidence.py` as the single
  requestor/reviewer implementation of Git index-tree capture;
- added immutable resolved-validation command and set types plus additive,
  source-preserving resolution in `tools/code_review_validation.py`;
- extended `tools/code_review_request.py` so the CLI captures the publication-
  time index tree, accepts repeatable plan and request validation commands,
  and renders a distinct `## Code review evidence` JSON block;
- updated the request template and canonical requestor instruction to document
  the evidence contract; and
- added focused unit, instruction, acceptance, IO, temporary-repository, and
  round-trip coverage for the new behavior and preserved contracts.

The required validation-plan row records completion, architecture,
performance, coverage, feature-integrity, and the successful Groundhog result.

Round 1 removed one trailing blank line from the validation package marker.
The repair is accepted and remains staged. The versioned code-review transcript
is now staged in the documentation group, and no production behavior changed
after the original implementation check.

The required post-repair Groundhog walk passed code and coverage but identified
four duration outliers. Renderer-only acceptance journeys now use deterministic
valid tree evidence while real capture remains covered by its focused Git leaf;
all 15 specification route states run as separate exhaustive cases; and the
dashboard rebuild test seeds the already-covered first-run artifacts directly.
Every assertion remains. The three unrelated test files are isolated in a
leading test-maintenance commit.

The follow-up walk cleared all seven original duration warnings and exposed one
different IO-acceptance call at 1.15 seconds. Profiling showed its two Git setup
subprocesses inside the measured call; those now run in a fixture while the
same routing, staged-path, and forbidden-scan assertions remain measured.

The next walk reported no ordinary outlier, but one accepted sensitive-history
call exceeded its recorded baseline. Its absent, empty, and relative Git config
states are now prepared in a fixture; the measured call still performs real
Git reads and the same fail-closed monkeypatch. Focused verification passes.

### Change summary for step 1 code-reviewer round 2

Staged paths for Step 1:

- `docs/v0.11.0/plan.v0.11.0.code-reviewer.validation.md`
- `docs/v0.11.0/review.code.v0.11.0.code-reviewer.md`
- `instructions/code-review-requestor.md`
- `templates/code-review-request.template.md`
- `tests/unit/tools/git_history_dashboard/test_report_acceptance/test_report_acceptance_tdd.py`
- `tests/unit/tools/sensitive_history/test_history_scan.py`
- `tests/unit/tools/test_code_review_evidence/__init__.py`
- `tests/unit/tools/test_code_review_evidence/test_code_review_evidence_tdd.py`
- `tests/unit/tools/test_code_review_request/test_code_review_request_tdd.py`
- `tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_acceptance_tdd.py`
- `tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_io_acceptance_tdd.py`
- `tests/unit/tools/test_code_review_requestor_instruction/test_code_review_requestor_instruction_tdd.py`
- `tests/unit/tools/test_code_review_validation/__init__.py`
- `tests/unit/tools/test_code_review_validation/test_code_review_validation_tdd.py`
- `tests/unit/tools/test_prompt_workflow_review/test_prompt_workflow_review_spec_reviewer_pbt.py`
- `tools/code_review_evidence.py`
- `tools/code_review_request.py`
- `tools/code_review_validation.py`

`a.commit` accounts for every staged path in four groups:

1. `test: shorten duration-gated checks`
2. `feat(code-review): add request evidence types`
3. `feat(code-review): publish immutable evidence`
4. `docs(code-reviewer): record step 1 validation`

There are no unaccounted staged paths. The Round 1 repair removed the trailing
blank line from `tests/unit/tools/test_code_review_validation/__init__.py`,
which was already assigned to the evidence-foundation group. The required
Groundhog rerun found four duration outliers, then one different routing call
on the follow-up walk. The Step 1 acceptance fixes stay in the renderer group,
while three unrelated routing, dashboard, and sensitive-history repairs are
isolated in the leading test group. The validation plan and versioned review
transcript are isolated in the trailing documentation group.

### Writer response for step 1 code-reviewer round 2

Writer response: Round 1 requested changes. I accepted the staged removal of the trailing blank
line in `tests/unit/tools/test_code_review_validation/__init__.py` and assessed
it as correct; `git diff --cached --check` now passes.

I deliberately retain `tools/code_review_request.py` in its current mixed
line-ending state for this feature slice. Normalizing to LF would rewrite all
453 lines, while normalizing to CRLF would make every added line fail the
repository whitespace check. Either is repository-convention work outside
Step 1, so no normalization is folded into these feature commits.

I kept the exact-type guard because `ResolvedValidationSet` is a frozen payload
boundary, and the reviewer marked that suggestion optional. I staged the
versioned transcript and added it to the trailing documentation group in
`a.commit`. There is no disagreement with the Round 1 findings.

The mandatory post-repair Groundhog walk passed all tests and 100% coverage but
exited on four duration outliers. I profiled and shortened each named call
without removing assertions: two renderer-only journeys no longer launch an
already separately tested Git capture, all 15 route states are separate
exhaustive calls, and the dashboard rebuild case no longer runs a discarded
first export. Focused Groundhog verification passes. `a.commit` isolates the
non-Step-1 test paths in a leading maintenance group.

That follow-up walk cleared all original warnings and identified one different
IO-acceptance call at 1.15 seconds. Its profiled Git setup now runs in a fixture
outside the measured call, preserving the same assertions, and its focused
Groundhog run passes.

That walk cleared ordinary outliers but found one accepted sensitive-history
call beyond its recorded baseline. Profiling identified repository setup in the
measured call. Three preconfigured repositories now cover absent, empty, and
relative config states outside the call, while the measured assertions retain
real Git reads and the fail-closed error path. Focused Groundhog passes, and the
repair is isolated with the other duration-gate maintenance paths.

The final walk reached `state=done exit=0`: all 1,707 tests pass with 100%
coverage, zero outliers, and zero exclusion regressions.

Review the replacement staged subject for Step 1 only. Leave any bounded
reviewer repairs staged and report each repaired path. Do not assess or begin
the deferred Step 2 work.

### Reviewer focus for step 1 code-reviewer round 2

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-round-2 -->

## Round 2 by reviewer - Step 1

- Recorded: 2026-08-15T20:32:00+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 1
- Outcome: answer

### Assessed staged state for step 1 code-reviewer round 2

Request-time tree `79915cab1824e3845e8242eddbc55c34fb3aab1c` matched the live
index exactly, and this review left it unchanged because its only repair was
confined to the ignored `a.commit`. Eighteen staged paths, as listed. Compared
against the round 1 assessed tree `9aae9a44bf86a6a5b898a88cb191e0432fa2572c`,
the entire delta is seven files, and no production file changed, so the round 1
implementation assessment carries forward. The three unrelated staged paths are
reliably separable: they touch no Step 1 file and sit in their own leading
commit group. The transcript's `AM` state is correct, since the round 2 request
append was deliberately left unstaged.

### Implementation assessment for step 1 code-reviewer round 2

Every round 1 item is resolved. The whitespace repair is accepted and staged,
the transcript is staged into group 4, the optional exact-type guard is kept,
and the mixed line endings are deliberately retained with the reason recorded in
the group 3 commit body, which is exactly the deliberate decision the round 1
answer asked for.

All four duration repairs preserve their assertions and two strengthen them. The
dashboard rebuild still seeds a `STALE SENTINEL` and asserts it is gone, proving
the overwrite more directly than before. The route test moves from Hypothesis
sampling to exhaustive parametrization over the full enum. The sensitive-history
test replaces three sequential config mutations with three fixture-prepared
repositories, which is equivalent because the production function reads current
config only. The IO acceptance test moves setup into a fixture and leaves the
measured body untouched. Where two acceptance leaves now pass a constant tree,
real capture remains covered by its temporary-repository leaf, the call-site
wiring by a monkeypatch that fails if the CLI stops calling it, and the command
order by the instruction test.

### Repairs made in step 1 code-reviewer round 2

One, in `a.commit` only: group 4's body said `record 1,693 passing tests` while
the validation record it commits now states 1,707. Polishing-only and not
substantive, since it changes no code, test, acceptance behavior, or grouping,
so this round remains eligible to recommend readiness. No staged path was
modified and the index tree is identical before and after.

### Validation evidence for step 1 code-reviewer round 2

`ghog day` exits 0. Reported honestly, the walk was a no-op: it printed that no
Python file changed since the last green walk and skipped coverage and outlier
measurement, which is the gate's own change detection confirming the writer's
full walk covers this exact state. `git diff --cached --check` exits 0. The
focused plan command passed in round 1 against unchanged production code.
Validation wrote only ignored artifacts, and the index tree and every tracked
path are identical before and after, so no side effect blocks readiness.

### a.commit assessment for step 1 code-reviewer round 2

Accurate after the corrected count. Four groups account for all eighteen staged
paths exactly once, the three unrelated duration repairs are isolated in a
leading maintenance group so they never enter a Step 1 commit, ordering runs
maintenance to foundations to consumer to documentation, and the unscoped
`test:` type is correct for three files spanning unrelated areas.

### Non-blocking observation for step 1 code-reviewer round 2

`test_prompt_workflow_review_spec_reviewer_pbt.py` no longer contains any
property-based test while every other `_pbt.py` file still uses `@given`, so the
suffix now misleads. Nothing automated enforces it, and renaming would move a
path between commit groups and so require another round, which is why it was
reported rather than repaired. The transcript is staged at its pre-round-2
snapshot and should be re-staged immediately before the authorized commit.

### Final reviewer decision for step 1 code-reviewer round 2

Decision: convergence-recommended, commit-ready for Step 1. No substantive
staged change was made this round, every readiness-floor item passes, and the
single repair was confined to `a.commit`. The recommendation is advisory and
authorizes no commit.

<!-- review-entry-id: answer-round-2 -->

## Round 2 by human - Step 1

- Recorded: 2026-08-15T20:59:58+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 1
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-2 -->

## Round 1 by requestor - Step 2

- Recorded: 2026-08-16T14:21:19+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 2
- Outcome: request

### Review identity for step 2 code-reviewer round 1

Umbrella draft: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-reviewer.md
Implementation step: 2
Review round: 1

### Code review evidence for step 2 code-reviewer round 1

request_index_tree: b74aeba63c51f7c51d01af03680e253eed2f01e8
resolved_validation_set:

- ghog day (sources: project)
- rg -n 'interactive=False|umbrella_digest|validation_state|retire_manifest' tools/code_review_evidence.py tools/code_review_evidence_cli.py tools/git_batch_commit_validation.py tests/unit/tools/test_code_review_evidence tests/unit/tools/test_git_batch_commit_validation (sources: plan)
- bin/code_review_evidence.bat --help (sources: plan)

### Requestor assessment for step 2 code-reviewer round 1

Step 2 is fully implemented. The staged implementation closes every item from
the previous validation-plan check: validation capture receives only explicit
literal paths, all CLI file operands stay within the selected repository,
retained evidence rejects malformed or contradictory payloads, and retained
file identity is fixed to `code/code`.

The final `ghog day` ran all 1,742 tests in 1 minute 31.1 seconds with zero
failures, 100% coverage, zero duration outliers, and a slowest call of 0.46
seconds. Static checks passed. The changed production modules contain 510, 291,
and 202 physical lines, below the 650-line ceiling. Validation capture performs
O(n) work over caller-named paths without a repository-wide selection scan.
Existing public imports, request evidence, retained evidence lifecycle, and the
shared commit-plan validator remain intact.

### Implementation report for step 2 code-reviewer round 1

The evidence hub now delegates validation snapshots and comparisons to a
focused validation-state module while keeping compatibility exports. Capture
requires an ordered non-empty file set and passes literal Git pathspecs only for
that set. Comparisons reject mismatched scopes.

The CLI resolves umbrella, baseline JSON, validation-state JSON, and retained
evidence operands relative to the selected repository and rejects absolute,
root, parent-traversal, or directory operands. Retained payload parsing checks
SHA-256 shapes, applicability pairs, unique safe paths, cross-field membership,
and the fixed code-review identity before read, write, or retirement.

Focused tests cover unrelated-file exclusion, literal pathspecs, invalid
operands, malformed payload relationships, duplicate paths, mixed identities,
and defensive Git failures. The validation plan records Step 2 as complete.

### Change summary for step 2 code-reviewer round 1

The staged review subject contains these eight paths:

- `tools/code_review_evidence.py`
- `tools/code_review_evidence_validation_state.py`
- `tools/code_review_evidence_cli.py`
- `tools/__init__.py`
- `tests/unit/tools/test_code_review_evidence/test_code_review_evidence_tdd.py`
- `tests/unit/tools/test_code_review_evidence/test_code_review_evidence_cli_tdd.py`
- `docs/v0.11.0/plan.v0.11.0.code-reviewer.validation.md`
- `docs/v0.11.0/review.code.v0.11.0.code-reviewer.md`

The root `a.commit` assigns the six production and test paths to
`fix(code-reviewer): bound evidence paths`, followed by the two documentation
paths in `docs(code-reviewer): record step 2 validation`. Both Why sections are
two-paragraph narratives that cite the review-mode umbrella draft, code-reviewer
topic draft, feature request, design, implementation plan, and validation plan.

### Writer response for step 2 code-reviewer round 1

Writer response: Round 1 has no earlier reviewer feedback. The writer completed only the four
missing-work findings recorded by the preceding Step 2 implementation check,
kept unrelated work unchanged, and requests an independent assessment of the
staged implementation and `a.commit` grouping.

### Reviewer focus for step 2 code-reviewer round 1

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-round-1 -->

## Round 1 by human - Step 2 - escalation

- Recorded: 2026-08-16T14:51:28+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 2
- Outcome: escalation

exchange was abandoned while waiting for reviewer

<!-- review-entry-id: escalation-round-1 -->

## Round 1 by human - Step 2 - human-reclaim

- Recorded: 2026-08-16T17:05:51+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 2
- Outcome: human-reclaim

Human recovery decision: resume step 2 round 1 in place.

The 1,800-second reviewer wait expired while this exchange was being driven as a
manual back-and-forth, so the recorded escalation describes a stopped handoff
rather than a failed round. The round-1 request, its immutable evidence, and the
transcript are intact and remain authoritative.

The human authorized the forced reclaim added to the shared protocol for exactly
this case, rather than `resolve` or `archive`. Both of those would have retired
the live evidence and opened a renumbered round that needs a replacement
request, which no part of this manual handoff requires.

<!-- review-entry-id: human-reclaim-round-1 -->

## Round 1 by reviewer - Step 2

- Recorded: 2026-08-16T17:07:03+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 2
- Outcome: answer

### Assessed staged state for step 2 code-reviewer round 1

The request-time index tree `b74aeba63c51f7c51d01af03680e253eed2f01e8` matched
the live index exactly before assessment, so this round assessed the published
subject. After the single reviewer repair the index tree is
`a91e81508a79ddfcf2102e2bba1276759ec7d9db`. The staged set still holds exactly
the eight paths the change summary lists, with no unrelated staged content.

This round was resumed through the human-authorized forced reclaim rather than a
fresh round: the 1,800-second wait expired while the exchange was being driven
manually, and round 1, its request, and its evidence were intact.

The working tree also carries unstaged protocol work that is not part of this
review subject and not in any `a.commit` group: `tools/review_exchange_models.py`,
`tools/review_exchange_state.py`, `tools/review_exchange_store.py`,
`tools/review_exchange_human.py`, `tools/review_exchange_cli.py`,
`instructions/review-requestor.md`, and three review-exchange test modules. It
adds the forced reclaim used above and belongs to the review-exchange-core item.

### Implementation assessment for step 2 code-reviewer round 1

Step 2 is implemented against the numbered plan. Validation capture takes an
ordered caller-named file set, rejects an empty set, directories, absolute
paths, and traversal, and passes `:(literal)` pathspecs so Git matches only
those names. A monkeypatched `Path.read_bytes` proves unrelated tracked files
are neither listed nor hashed. Comparison refuses two snapshots whose ordered
path scopes disagree, so a narrowed second capture cannot silently pass.

Every CLI file operand now resolves under the selected repository and rejects
absolute, escaping, and root operands; directory operands fail through their
owning helper. Retained payload parsing validates SHA-256 digest shapes,
umbrella applicability pairing, unique repository-relative recorded-blob and
repair paths, membership of every file digest in the declared path scope, and
the fixed `code/code` identity before any manifest read, write, or retirement.
`write_manifest` re-validates through `from_payload`, so a hand-built value
object cannot bypass those invariants.

The split obeys the plan's line budgets: 510, 291, and 202 physical lines for
the evidence hub, the new validation-state module, and the CLI, against the
650-line ceiling. Capture is O(n) over the caller's paths with three fixed Git
calls and no repository-wide selection scan.

### Repairs made in step 2 code-reviewer round 1

Staged: `tools/code_review_evidence.py`. The new `__all__` declared only the
five re-exported validation-state names, which silences the unused-import rule
but also removes the module's own fourteen public names from its declared
surface, including `capture_index_tree` that Step 1 established as the single
shared capture helper. Every other module in `tools/` that declares `__all__`
enumerates its complete public API. The repair extends the list to the full
surface in the repository's ASCII order.

Substantive, because it changes a tracked file other than `a.commit`. A
substantive repair in this round forbids a commit-ready recommendation here.

### Findings returned to the writer for step 2 code-reviewer round 1

The split forked seven private helpers instead of sharing them.
`_payload_path`, `_unique_paths`, `_repository_root`, `_relative_path`,
`_TREE_OBJECT_RE`, and `_SHA256_RE` are now byte-identical in
`tools/code_review_evidence.py` and
`tools/code_review_evidence_validation_state.py`, and `_git` differs only by its
`check` keyword. Two of these are the repository-containment checks this step
exists to enforce, so an independent edit to one copy silently weakens the
other. The evidence hub already imports from the validation-state module, so a
single home is available; choosing between importing them from that module and
extracting a third shared module is a structural decision that belongs to the
writer.

Two historical transcript rounds were edited by hand and staged. The staged diff
of `docs/v0.11.0/review.code.v0.11.0.code-reviewer.md` inserts a blank line after
`resolved_validation_set:` at lines 29 and 216, inside Step 1 rounds 1 and 2 that
`bin/review_exchange.bat` appended in earlier commits. The requestor instruction
forbids overwriting a protocol artifact by hand. The edit is also incomplete:
`_CodeReviewEvidence.summary()` in `tools/code_review_request.py:124` still emits
the list with no preceding blank line, so this round's own Step 2 append
reproduces the defect at line 502. The renderer is the correct place to fix it
and belongs to Step 1's surface, outside this step; the reviewer left both the
staged hand edit and the current append untouched.

The validation plan's feature-integrity paragraph is already false. It states
that the transcript still contains only Step 1 request, answer, and
human-confirmation rounds. The working tree now holds the Step 2 round-1
request, the escalation, and the forced-reclaim entry, and Group 2 stages that
same transcript with `git add -A`, so the commit would carry a claim its own
sibling file contradicts.

Bounded capture narrows a design guarantee that Step 3 must restore. The design
requires any tracked-file difference around validation to be a readiness-blocking
finding, and separately requires comparing only explicitly named step files.
Capture now honours the second by scoping to caller-named paths, and the
repository-wide index tree still catches anything staged, but an unstaged
worktree change to a tracked file outside the named set is now invisible. Step 3
writes the reviewer-mode instruction and must state the mandatory minimum path
set, at least the staged step paths plus the known validation artifact paths, or
the tracked-difference acceptance case cannot hold in general.

### Validation evidence for step 2 code-reviewer round 1

`ghog day` after the repair reports `fail=0 warn=0 xfail=0 cov=100 outliers=0
excluded=0 exit=0` over 1,747 tests, with the full phase at 1 minute 12.3
seconds and a slowest call of 0.39 seconds. The count exceeds the request's
1,742 because the unstaged protocol work adds five tests; the reviewer repair
adds none.

The plan completion grep finds all four identifiers across the three production
modules and both test packages, in implementations and tests rather than prose.
`bin/code_review_evidence.bat --help` exits 0 from the repository root with no
environment setup. `git diff --cached --check` exits 0, and all eight staged
paths are `i/lf w/lf`, so the Step 1 line-ending finding did not recur.

Physical line counts are 510, 291, 202, and 102 for the four Step 2 production
modules and 549 and 328 for the two evidence test modules, all below the
650-line ceiling.

### a.commit assessment for step 2 code-reviewer round 1

Accurate, no amendment needed. Running the step's own validator,
`validate_commit_plan(parse_clipboard_content(a.commit, interactive=False),
staged_paths)`, returns zero diagnostics against the exact staged set: two
ordered groups, conventional subjects, exact membership, and no duplicate or
missing path. The repair landed inside an existing Group 1 member, so grouping
and boundaries are unchanged. No commit was created.

If the writer acts on the transcript finding, Group 2 keeps the transcript,
because the round-1 request, the escalation, the forced reclaim, and this answer
all append to it. Only its `What` bullet about keeping Step 1 paragraphs
visually separate would need rewording.

### Non-blocking observations for step 2 code-reviewer round 1

The package docstring in `tools/__init__.py` now advertises "split code-review
evidence responsibilities". That is one feature's internal structure described at
package level, and the file is not in the plan's Step 2 file list.

`test_code_review_evidence_tdd.py` stands at 549 lines against the Step 2
addendum that asks for split fixture support as either evidence test module
approaches 550. The next addition crosses it.

`capture_validation_state` runs `capture_index_tree` before
`capture_validation_paths` validates the path set, so a rejected call still
writes tree objects. Harmless, and reordering the two calls removes it.

### Final reviewer decision for step 2 code-reviewer round 1

Decision: changes-requested. The staged repair is substantive, which forbids a
commit-readiness recommendation in this round, and the duplicated helpers, the
hand-edited transcript rounds, and the false feature-integrity paragraph each
need a writer decision. The implementation itself is otherwise sound and close
to ready. This answer is advisory and authorizes no commit.

<!-- review-entry-id: answer-round-1 -->

## Round 2 by requestor - Step 2

- Recorded: 2026-08-16T17:50:35+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 2
- Outcome: request

### Review identity for step 2 code-reviewer round 2

Umbrella draft: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-reviewer.md
Implementation step: 2
Review round: 2

### Code review evidence for step 2 code-reviewer round 2

request_index_tree: 374240ee3e770c1a6f7b5bca3eb2efdae7e1fc69
resolved_validation_set:

- ghog day (sources: project)
- rg -n 'interactive=False|umbrella_digest|validation_state|retire_manifest' tools/code_review_evidence.py tools/code_review_evidence_cli.py tools/git_batch_commit_validation.py tests/unit/tools/test_code_review_evidence tests/unit/tools/test_git_batch_commit_validation (sources: plan)
- bin/code_review_evidence.bat --help (sources: plan)
- git diff --cached --check (sources: request)

### Requestor assessment for step 2 code-reviewer round 2

Step 2 remains fully implemented after accepting every round-one finding. The
reviewer's complete `code_review_evidence.__all__` repair is retained. Shared
digest, path-containment, and Git primitives now have one implementation;
request summaries render validation lists correctly at their source; the
protocol transcript is no longer staged; and Step 3's plan names the minimum
staged-plus-validation-artifact path set.

The final Groundhog cycle passed all 1,747 tests with zero failures, 100%
coverage, zero duration outliers, and a slowest call of 0.43 seconds. Static
checks passed. The evidence hub, common boundary, validation-state module, CLI,
request renderer, and affected tests all remain below the 650-line ceiling.
Validation capture remains O(n) over caller-named paths with no repository-wide
selection scan.

### Implementation report for step 2 code-reviewer round 2

Round 2 retains the substantive public-surface repair made by the reviewer and
adds one shared `code_review_evidence_common.py` boundary for tree and digest
patterns, retained payload paths, unique ordered paths, repository roots,
contained file resolution, and Git evidence execution. Both evidence modules
import that boundary, so their containment and error behavior cannot drift.

`_CodeReviewEvidence.summary()` now inserts the required blank line before its
validation command list, with a regression assertion on the generated output.
The historical transcript bytes, including the two duplicate human headings,
remain untouched and unstaged. The implementation plan now requires Step 3 to
capture every staged step path and known validation artifact path, and the
validation plan records the round-one answer and current green evidence.

### Change summary for step 2 code-reviewer round 2

The staged round-two subject contains these eleven paths:

- `tools/code_review_evidence.py`
- `tools/code_review_evidence_common.py`
- `tools/code_review_evidence_validation_state.py`
- `tools/code_review_evidence_cli.py`
- `tools/code_review_request.py`
- `tools/__init__.py`
- `tests/unit/tools/test_code_review_evidence/test_code_review_evidence_tdd.py`
- `tests/unit/tools/test_code_review_evidence/test_code_review_evidence_cli_tdd.py`
- `tests/unit/tools/test_code_review_request/test_code_review_request_tdd.py`
- `docs/v0.11.0/plan.v0.11.0.code-reviewer.md`
- `docs/v0.11.0/plan.v0.11.0.code-reviewer.validation.md`

The root `a.commit` assigns the nine production and test paths to
`fix(code-reviewer): bound evidence paths`, followed by the plan and validation
plan in `docs(code-reviewer): record step 2 validation`. The transcript and the
nine review-exchange-core paths remain unstaged and outside both groups.

### Human guidance and writer response for step 2 code-reviewer round 2

Human guidance: Human recovery decision: resume step 2 round 1 in place.

The 1,800-second reviewer wait expired while this exchange was being driven as a
manual back-and-forth, so the recorded escalation describes a stopped handoff
rather than a failed round. The round-1 request, its immutable evidence, and the
transcript are intact and remain authoritative.

The human authorized the forced reclaim added to the shared protocol for exactly
this case, rather than `resolve` or `archive`. Both of those would have retired
the live evidence and opened a renumbered round that needs a replacement
request, which no part of this manual handoff requires.

Writer response: All round-one feedback is accepted with no disagreement. The writer retained
the reviewer's complete `__all__` repair, replaced the seven duplicated helpers
with one shared module, fixed validation-list spacing in the request renderer
and added its regression assertion, removed the protocol transcript from the
staged subject without editing its bytes, corrected the feature-integrity
record, and pinned Step 3's minimum validation-state path set.

The root `a.commit` was amended because the staged membership changed: the
renderer source, its test, the shared helper module, and the implementation plan
were added, while the protocol transcript was removed. The unrelated forced
reclaim implementation remains unstaged and in no commit group.

### Reviewer focus for step 2 code-reviewer round 2

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-round-2 -->

## Round 2 by reviewer - Step 2

- Recorded: 2026-08-16T18:57:02+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 2
- Outcome: answer

### Assessed staged state for step 2 code-reviewer round 2

The request-time index tree `374240ee3e770c1a6f7b5bca3eb2efdae7e1fc69` matched
the live index exactly before assessment, so this round assessed the published
subject. After three reviewer repairs the index tree is
`dc8ef97b732099a3c33e18f4e88568a87e684265`. The staged set holds exactly the
eleven paths the change summary lists, with no unrelated staged content.

The unstaged forced-reclaim work in `tools/review_exchange_*.py`,
`instructions/review-requestor.md`, and three review-exchange test modules is
still outside this subject and outside both `a.commit` groups. The protocol
transcript is also unstaged; that is assessed as a finding below rather than as
unrelated work.

### Round 1 findings verified in step 2 code-reviewer round 2

All four round-one findings are resolved, and the writer recorded no
disagreement.

The seven forked helpers now have one home in
`tools/code_review_evidence_common.py`, a 105-line module with a complete
`__all__` that both evidence modules import. The two copies of the
repository-containment check are gone, so they can no longer drift.

`_CodeReviewEvidence.summary()` emits the blank line at its source, with a
regression assertion that pins the generated `resolved_validation_set:` block
rather than the bare label. This round's own transcript entry renders the list
correctly at line 789, which is the end-to-end proof.

The staged transcript hand edit is gone and the file's staged bytes again equal
`HEAD`; the historical rounds and the two duplicate human headings were left
untouched. The reviewer's complete `code_review_evidence.__all__` repair is
retained verbatim.

Step 3 of the implementation plan now requires every validation-state capture to
name at least each staged step path and each known validation-artifact path, in
the fix intent, the tests-first list, and the command contract. That closes the
scope gap the round-one answer raised.

### Repairs made in step 2 code-reviewer round 2

Staged: `tools/code_review_evidence_validation_state.py`. Moving the shared
regexes out of the module left one blank line between the `TYPE_CHECKING` block
and `@dataclass(frozen=True)` at line 41, where PEP 8 and every sibling module
use two. `pyproject.toml` selects `ALL` but leaves `preview` commented out at
line 158, so ruff's E301 through E306 never run and no gate can see this.

Staged: `docs/v0.11.0/plan.v0.11.0.code-reviewer.validation.md`. The
architecture check claimed 467 and 235 physical lines for the evidence hub and
the validation-state module; both are twelve lines higher, which is exactly the
cost of the isort-expanded import blocks, so the counts predate the final
reformat. The row now reads 479, 105, 248, and 202, measured after the repair
above.

Amended: root `a.commit`. Group 2's second Why paragraph still narrated the
review transcript, which this round removed from both groups, so the message
described a file the commit does not touch. It now describes the Step 3 capture
contract that the staged plan actually adds.

The `a.commit` amendment and the validation-plan row are review metadata. The
blank line is a change to a tracked production file outside the exempt
categories, so it is substantive and forbids a commit-ready recommendation in
this round.

### Findings returned to the writer for step 2 code-reviewer round 2

The transcript left both `a.commit` groups, and that overcorrects the round-one
finding. That finding was about two hand-edited hunks inside published Step 1
rounds, not about the file's membership; reverting those hunks fixed it, and the
staged bytes already equal `HEAD`. Dropping the path as well means the entire
Step 2 review record, five appended entries, never lands with the Step 2 commit,
which is the same gap the Step 1 round-one answer raised and the writer closed
then by staging the transcript in the documentation group. Restoring it changes
staged membership, so the decision is the writer's, not a reviewer repair.

`test_code_review_evidence_tdd.py` now measures exactly 550 lines. The Step 2
addendum asks for split fixture support as either evidence test module
approaches 550, so the plan's own threshold is reached rather than approaching.
Splitting a test module is a structural decision and stays with the writer.

### Validation evidence for step 2 code-reviewer round 2

Every command in the resolved set ran after the repairs. `ghog day` reports
`fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0` over 1,747 tests,
with the full phase at 1 minute 30.1 seconds and a slowest call of 0.43 seconds.
The plan completion grep returns 60 matches across the three production modules
and both test packages. `bin/code_review_evidence.bat --help` exits 0 from the
repository root with no environment setup. `git diff --cached --check` exits 0,
which is the addition this request contributed to the set.

No resolver drift: the request's four commands are the project default plus two
plan additions plus one request addition, and the current resolver produces the
same set.

Line counts are 479, 105, 248, 202, and 461 for the evidence hub, common
boundary, validation-state module, CLI, and request renderer, and 550, 328, and
490 for the three staged test modules. All are below the 650-line ceiling.

### a.commit assessment for step 2 code-reviewer round 2

Accurate after the wording amendment above. Running the step's own validator,
`validate_commit_plan(parse_clipboard_content(a.commit, interactive=False),
staged_paths)`, returns zero diagnostics against the exact staged set both
before and after the repairs: two ordered groups, conventional subjects, exact
membership, and no duplicate or missing path. Both repairs landed inside
existing group members, so membership, grouping, and order are unchanged. No
commit was created.

### Non-blocking observations for step 2 code-reviewer round 2

The seven single-name `from tools.code_review_evidence_common import (X as _Y)`
statements are required, not accidental: `pyproject.toml` sets no
`combine-as-imports`, so isort's default splits aliased imports. A repository-wide
`[tool.ruff.lint.isort] combine-as-imports = true` would collapse them into one
statement and reclaim the twelve lines discussed above, but that setting is
outside this step.

`capture_index_tree` still calls `run_cross_platform_git_command` directly
instead of the new `run_git_evidence`, which keeps `subprocess` and
`GitCommandOptions` imported in the evidence hub for one call site. It is the
one primitive that did not move to the common boundary, and its distinct error
message is a defensible reason to leave it.

The duplicate `## Round 1 by human - Step 2` heading pair remains in the
transcript. It was rendered before the store began qualifying human headings by
outcome, and correcting it would mean editing published protocol bytes.

### Final reviewer decision for step 2 code-reviewer round 2

Decision: changes-requested. The blank-line repair is a change to a tracked
production file outside the exempt categories, and the transcript-membership
question needs a writer decision that a reviewer cannot make. Neither concerns
the implementation itself, which is complete, correct, and green on every
resolved validation command; round two accepted and closed every round-one
finding without regression. This answer is advisory and authorizes no commit.

<!-- review-entry-id: answer-round-2 -->

## Round 3 by requestor - Step 2

- Recorded: 2026-08-16T19:22:10+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 2
- Outcome: request

### Review identity for step 2 code-reviewer round 3

Umbrella draft: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-reviewer.md
Implementation step: 2
Review round: 3

### Code review evidence for step 2 code-reviewer round 3

request_index_tree: 3a95958c36bb108e951c4a672339809d740a9d52
resolved_validation_set:

- ghog day (sources: project)
- rg -n 'interactive=False|umbrella_digest|validation_state|retire_manifest' tools/code_review_evidence.py tools/code_review_evidence_cli.py tools/git_batch_commit_validation.py tests/unit/tools/test_code_review_evidence tests/unit/tools/test_git_batch_commit_validation (sources: plan)
- bin/code_review_evidence.bat --help (sources: plan)
- git diff --cached --check (sources: request)

### Requestor assessment for step 2 code-reviewer round 3

Step 2 is fully implemented after accepting all round-two repairs and returned
findings. The validation-state spacing and architecture counts are corrected,
`a.commit` describes its actual groups, the complete protocol transcript is
restored to the documentation group without changing historical bytes, and the
550-line evidence test is split into focused 221-line core and 363-line
defensive-boundary modules.

The final `ghog day` passed all 1,747 tests with zero failures, 100% coverage,
zero duration outliers, and a slowest call of 0.44 seconds. The full phase took
1 minute 17.3 seconds. Static checks passed, staged whitespace is clean, every
production and test module remains below the repository ceiling, and bounded
validation capture remains O(n) over explicit paths.

### Implementation report for step 2 code-reviewer round 3

The writer retained the reviewer's production blank-line repair, corrected
line counts of 479, 105, 248, and 202 in the validation plan, and retained the
reviewer's Group 2 narrative correction. The evidence test threshold is now
closed structurally: core capture and retained-lifecycle behavior stays in the
original module, while malformed payload, unsafe path, Git failure, and IO
boundary cases live in `test_code_review_evidence_boundaries_tdd.py`.

The writer restored `review.code.v0.11.0.code-reviewer.md` to Group 2. Its
staged content is protocol-generated, its historical Step 1 bytes and duplicate
human headings were not edited, and the exact-path group command can include
later Step 2 protocol entries. The validation plan records that decision and
the final green Groundhog evidence.

### Change summary for step 2 code-reviewer round 3

The staged round-three subject contains fourteen paths.

Group 1 contains eleven production and test paths:

- `tools/code_review_evidence.py`
- `tools/code_review_evidence_common.py`
- `tools/code_review_evidence_validation_state.py`
- `tools/code_review_evidence_cli.py`
- `tools/code_review_request.py`
- `tools/__init__.py`
- `tests/unit/tools/test_code_review_evidence/__init__.py`
- `tests/unit/tools/test_code_review_evidence/test_code_review_evidence_boundaries_tdd.py`
- `tests/unit/tools/test_code_review_evidence/test_code_review_evidence_tdd.py`
- `tests/unit/tools/test_code_review_evidence/test_code_review_evidence_cli_tdd.py`
- `tests/unit/tools/test_code_review_request/test_code_review_request_tdd.py`

Group 2 contains the implementation plan, validation plan, and protocol
transcript. The root `a.commit` uses `fix(code-reviewer): bound evidence paths`
followed by `docs(code-reviewer): record step 2 validation`. The nine
review-exchange-core paths remain unstaged and outside both groups.

### Human guidance and writer response for step 2 code-reviewer round 3

Human guidance: Human recovery decision: resume step 2 round 1 in place.

The 1,800-second reviewer wait expired while this exchange was being driven as a
manual back-and-forth, so the recorded escalation describes a stopped handoff
rather than a failed round. The round-1 request, its immutable evidence, and the
transcript are intact and remain authoritative.

The human authorized the forced reclaim added to the shared protocol for exactly
this case, rather than `resolve` or `archive`. Both of those would have retired
the live evidence and opened a renumbered round that needs a replacement
request, which no part of this manual handoff requires.

Writer response: All round-two feedback is accepted with no disagreement. The writer retained
the reviewer's three staged repairs, restored the protocol transcript to Group
2 as the complete Step 2 review record, and split the 550-line evidence test by
core behavior versus defensive boundaries. The test package docstring,
validation record, and `a.commit` membership and narrative were updated to
match those decisions.

Historical transcript bytes, including the duplicate human headings rendered
before the protocol fix, remain untouched. The unrelated forced-reclaim
implementation remains unstaged and in no `a.commit` group.

### Reviewer focus for step 2 code-reviewer round 3

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-round-3 -->

## Round 3 by reviewer - Step 2

- Recorded: 2026-08-16T20:09:00+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 2
- Outcome: answer

### Assessed staged state for step 2 code-reviewer round 3

The request-time index tree `3a95958c36bb108e951c4a672339809d740a9d52` matched
the live index exactly before assessment, so this round assessed the published
subject. After one reviewer repair the index tree is
`4531ab6b78e3d763d3b920f2456eefb6e3cfc4cb`. The staged set holds exactly the
fourteen paths the change summary lists, with no unrelated staged content.

The transcript is correctly `MM`: its staged bytes are a pure append over
`HEAD`, with no removed line anywhere in the staged diff, and the unstaged
portion is this round's protocol-generated request. The nine forced-reclaim
paths remain unstaged and outside both groups.

### Round 2 findings verified in step 2 code-reviewer round 3

Both returned findings are closed and all three round-two repairs are retained
without disagreement.

The transcript is back in Group 2 with its historical Step 1 bytes untouched, so
the complete Step 2 review record now lands with the step. The blank line before
`@dataclass` is retained, and the corrected architecture counts of 479, 105,
248, and 202 re-measure exactly against the current files. The Group 2 narrative
kept the reviewer's correction and extends it accurately now that the transcript
is a member again.

The 550-line evidence module is split into a 221-line core module and a
363-line boundary module, both under the plan's threshold. The split is a clean
move rather than a rewrite: the union of the two modules holds the same thirteen
test functions under the same names, and every distinctive boundary message,
including `code/code`, `unsafe token`, `paths disagree`, and
`Git evidence command failed`, still appears with its assertion. The package
docstring was updated to match.

### Repairs made in step 2 code-reviewer round 3

Staged: `docs/v0.11.0/plan.v0.11.0.code-reviewer.validation.md`. The feature
integrity paragraph claimed the transcript carries "both reclaim entries". It
carries one. The round-two lease reclaim appended nothing, which is the
documented contract for an ordinary reclaim: it renews the lease without
touching request, answer, or transcript bytes. The transcript holds exactly one
`human-reclaim-round-1` entry, and the paragraph now says so.

That is a reviewed-step validation record and therefore review metadata, not a
substantive change. It is the only repair in this round.

### Findings returned to the writer for step 2 code-reviewer round 3

The evidence tests do not execute Git, and the literal-pathspec guarantee is
unverified. `tests/unit/tools/test_code_review_evidence/conftest.py`, tracked
since `b592199` and unchanged by this step, installs an autouse fixture that
replaces `subprocess.run` with an in-memory Git for the whole package. Its
`_run_ls_files` handler branches on `command[1]` alone and never reads the
arguments after `--`, so the `:(literal)` pathspecs built at
`tools/code_review_evidence_validation_state.py:154` are discarded before they
reach any matcher.

The consequence is that the step's headline guarantee cannot fail. Deleting
`:(literal)` from that line and running `ghog single
tests/unit/tools/test_code_review_evidence` reports `fail=0 exit=0`; the
reviewer ran exactly that and restored the file from the index afterwards. The
`literal[1].txt` fixture exists precisely to catch glob interpretation and
cannot detect it. The captured result is bounded only because
`_selected_digests` filters in Python afterwards, so Git's own filtering is
untested for the tracked, ignored, and untracked classifications alike.

This contradicts the step's own contract. The plan's Step 2 tests-first list
requires temporary Git repositories, and design Q06 requires testing public
entry points over real temporary Git repositories. Only the module-scoped
`staged_repository` fixture in the core module is instantiated before the
function-scoped autouse patch, so it alone sees real Git.

The reviewer did not repair this. Both routes out, teaching the fake to honour
pathspecs or exempting one case from the autouse fake so it runs real Git, are
test-architecture decisions that trade directly against the runtime reduction
`b592199` deliberately bought. That trade belongs to the writer.

### Validation evidence for step 2 code-reviewer round 3

Every command in the resolved set ran after the repair. `ghog day --force`
reports `fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0` over 1,747
tests, with the full phase at 1 minute 30.3 seconds and a slowest call of 0.44
seconds. The force flag was needed because an unforced `ghog day` short-circuits
with "No Python file changed since the last green walk", which is evidence of an
unchanged tree rather than of a passing suite. The plan completion grep returns
60 matches. `bin/code_review_evidence.bat --help` exits 0 from the repository
root. `git diff --cached --check` exits 0.

No resolver drift: the four commands are the project default plus two plan
additions plus one request addition, and the current resolver produces the same
set.

Note that the 100% coverage figure counts lines executed against the fake Git
described above, so it does not by itself establish the real-Git behavior of
`_listed_path_set`.

Line counts are 479, 105, 248, 202, and 461 for the evidence hub, common
boundary, validation-state module, CLI, and request renderer, and 221, 363, 328,
and 490 for the four staged test modules. All are below the 650-line ceiling and
the two evidence test modules are below the plan's 550-line split threshold.

### a.commit assessment for step 2 code-reviewer round 3

Accurate, no amendment needed. Running the step's own validator,
`validate_commit_plan(parse_clipboard_content(a.commit, interactive=False),
staged_paths)`, returns zero diagnostics against the exact staged set: two
ordered groups, conventional subjects, exact membership over all fourteen paths,
and no duplicate or missing path. Both group narratives now match their
membership, including the restored transcript. The repair landed inside an
existing Group 2 member. No commit was created.

### Non-blocking observations for step 2 code-reviewer round 3

The split gives the package a third byte-identical `_git` helper. The Step 2
addendum asked for split fixture support, and Step 6 already plans a
`fixtures.py` for shared repository construction, which is its natural home.

The duplicate `## Round 1 by human - Step 2` heading pair now lands in the
commit through Group 2. It was rendered before the store began qualifying human
headings by outcome, it cannot recur, and correcting it would mean rewriting
published protocol bytes.

The seven single-name aliased imports per module remain isort's default output
because `pyproject.toml` sets no `combine-as-imports`, and `capture_index_tree`
still calls `run_cross_platform_git_command` directly rather than the new
`run_git_evidence`. Both were raised in round two and neither is a defect.

### Final reviewer decision for step 2 code-reviewer round 3

Decision: changes-requested. Everything returned in round two is closed cleanly
and the implementation is otherwise complete and green, but the step's central
bounded-capture guarantee is proven only by a Python-side filter: the test that
exists to verify it passes with the mechanism removed. That gap needs a writer
decision on test architecture, which a reviewer cannot make inside this step.
This answer is advisory and authorizes no commit.

<!-- review-entry-id: answer-round-3 -->

## Round 4 by requestor - Step 2

- Recorded: 2026-08-16T21:16:25+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 2
- Outcome: request

### Review identity for step 2 code-reviewer round 4

Umbrella draft: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-reviewer.md
Implementation step: 2
Review round: 4

### Code review evidence for step 2 code-reviewer round 4

request_index_tree: 09d7b30aae95368231feeda6637d514355bf545e
resolved_validation_set:

- ghog day (sources: project)
- rg -n 'interactive=False|umbrella_digest|validation_state|retire_manifest' tools/code_review_evidence.py tools/code_review_evidence_cli.py tools/git_batch_commit_validation.py tests/unit/tools/test_code_review_evidence tests/unit/tools/test_git_batch_commit_validation (sources: plan)
- bin/code_review_evidence.bat --help (sources: plan)
- git diff --cached --check (sources: request)

### Requestor assessment for step 2 code-reviewer round 4

Step 2 is fully implemented after accepting the round-three blocking finding.
The evidence package keeps its fast in-memory Git fixture by default, while one
explicit boundary contract opts out and uses a temporary real repository. That
contract records the arguments and output of all three production `git
ls-files` calls and proves that tracked, ignored, and untracked bracketed names
are selected literally while their glob-shaped decoys are excluded.

The final `ghog day` passed all 1,748 tests in 1 minute 23.8 seconds with zero
failures, 100% coverage, zero duration outliers, and no exclusions. The slowest
call was 0.42 seconds against the 0.50-second ceiling. Static checks passed,
`git diff --cached --check` is clean, the evidence test modules remain at 221
and 456 lines, and the staged subject contains exactly the fifteen paths named
by `a.commit`.

### Implementation report for step 2 code-reviewer round 4

The writer added an explicit `real_git_commands` opt-out to the evidence
package's autouse subprocess fixture. A module-scoped temporary repository now
contains literal-versus-glob pairs for tracked, ignored, and untracked files;
the production capture runs against real Git and returns the recorded command
arguments, Git output, and validation state to the assertion phase. The test
therefore proves Git's filtering rather than duplicating it in the in-memory
fake, while moving only costly repository and subprocess setup outside the
measured call phase.

The reviewer's round-three validation-plan repair is retained. The validation
record now includes the real-Git contract, the exact 1,748-test Groundhog
result, the 0.42-second slowest call, current test-module counts, and the
round-three protocol append. All earlier production, documentation, transcript,
and `a.commit` repairs remain intact.

Groundhog also identified two unrelated forced-reclaim tests just above the
project-wide ceiling. Their expensive journey preconditions moved into fixtures
without dropping assertions; that review-exchange-core test file remains
unstaged and outside this Step 2 review subject.

### Change summary for step 2 code-reviewer round 4

The staged round-four subject contains fifteen paths.

Group 1 contains twelve production and test paths:

- `tools/code_review_evidence.py`
- `tools/code_review_evidence_common.py`
- `tools/code_review_evidence_validation_state.py`
- `tools/code_review_evidence_cli.py`
- `tools/code_review_request.py`
- `tools/__init__.py`
- `tests/unit/tools/test_code_review_evidence/__init__.py`
- `tests/unit/tools/test_code_review_evidence/conftest.py`
- `tests/unit/tools/test_code_review_evidence/test_code_review_evidence_boundaries_tdd.py`
- `tests/unit/tools/test_code_review_evidence/test_code_review_evidence_tdd.py`
- `tests/unit/tools/test_code_review_evidence/test_code_review_evidence_cli_tdd.py`
- `tests/unit/tools/test_code_review_request/test_code_review_request_tdd.py`

Group 2 contains the implementation plan, validation plan, and protocol
transcript. The root `a.commit` uses `fix(code-reviewer): bound evidence paths`
followed by `docs(code-reviewer): record step 2 validation`. The nine
review-exchange-core paths and `.vscode/settings.json` remain unstaged and
outside both groups.

### Human guidance and writer response for step 2 code-reviewer round 4

Human guidance: Human recovery decision: resume step 2 round 1 in place.

The 1,800-second reviewer wait expired while this exchange was being driven as a
manual back-and-forth, so the recorded escalation describes a stopped handoff
rather than a failed round. The round-1 request, its immutable evidence, and the
transcript are intact and remain authoritative.

The human authorized the forced reclaim added to the shared protocol for exactly
this case, rather than `resolve` or `archive`. Both of those would have retired
the live evidence and opened a renumbered round that needs a replacement
request, which no part of this manual handoff requires.

Writer response: All round-three feedback is accepted with no disagreement. The writer chose the
real-Git route requested by the plan and design: the package fake remains the
fast default, but one explicit contract bypasses it and observes Git's actual
literal-pathspec filtering for every validation-state path class. Every prior
assertion remains, and the new command and output assertions fail if
`:(literal)` is removed.

The reviewer-authored correction about ordinary reclaim behavior is retained.
Historical transcript bytes remain untouched, the round-three request and
answer are a pure append, and the unrelated forced-reclaim implementation and
test-speed correction remain unstaged and in no `a.commit` group.

### Reviewer focus for step 2 code-reviewer round 4

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-round-4 -->

## Round 4 by reviewer - Step 2

- Recorded: 2026-08-16T21:32:17+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 2
- Outcome: answer

### Assessed staged state for step 2 code-reviewer round 4

The request-time index tree `09d7b30aae95368231feeda6637d514355bf545e` matched
the live index exactly before assessment, so this round assessed the published
subject. After one polishing repair the index tree is
`6c80f7db17e8f6de9fab02dfb30019a45e841357`. The staged set holds exactly the
fifteen paths the change summary lists.

The transcript remains correctly `MM`: its staged bytes are a pure append over
`HEAD` with no removed line anywhere in the staged diff, and the unstaged
portion is this round's protocol-generated request. The nine
review-exchange-core paths and `.vscode/settings.json` stay unstaged and outside
both groups, as the change summary states.

### Round 3 finding verified in step 2 code-reviewer round 4

The blocking finding is closed, and the reviewer proved it the same way it was
raised rather than accepting the writer's report.

Removing `:(literal)` from `tools/code_review_evidence_validation_state.py:154`
and running `ghog single tests/unit/tools/test_code_review_evidence` now reports
`fail=1 exit=2` on
`test_validation_pathspecs_filter_real_git_literally`. In round three the same
mutation reported `fail=0 exit=0`. The file was restored from the index
afterwards and its content re-verified.

An independent probe outside this repository confirms the behavior the contract
depends on. Against a real repository holding `literal[1].txt` beside a
`literal1.txt` decoy, `git ls-files -- 'tracked/literal[1].txt'` returns both
names, while `git ls-files -- ':(literal)tracked/literal[1].txt'` returns only
the bracketed one. The same holds for the `--others` and
`--others --ignored` forms, so all three production calls are genuinely bounded.

The opt-out is well placed. A `real_git_commands` fixture whose presence in
`request.fixturenames` makes the autouse fake return early keeps the fast
in-memory Git as the package default while one contract observes real Git, which
is what the plan's tests-first list and design Q06 require. The module-scoped
repository and capture fixtures keep process setup outside the measured call, so
the suite kept zero outliers.

### Repairs made in step 2 code-reviewer round 4

Staged: `docs/v0.11.0/plan.v0.11.0.code-reviewer.validation.md`. Two paragraphs
carried ragged wrapping where this round's inserted sentences were not reflowed,
leaving `threshold. One explicit` and `nothing, because an ordinary` as short
lines mid-sentence against the document's consistent width. Both paragraphs are
rewrapped with no wording change.

Polishing-only: this is a reviewed-step validation record, it changes no code,
test, acceptance behavior, or commit grouping, and it therefore does not forbid
the recommendation below. It is the only repair in this round.

### Findings returned to the writer for step 2 code-reviewer round 4

None. No finding from any earlier round remains open, and this round introduced
none.

### Precision note on the proven guarantee for step 2 code-reviewer round 4

Worth recording so Step 3 does not over-claim what the contract establishes. Of
the new test's three assertion groups, the pathspec-argument assertion and the
raw `git ls-files` output assertion both fail under the mutation. The
`ValidationState` assertions do not, because a bare pathspec still matches the
bracketed file exactly and `_selected_digests` discards the extra decoy in
Python afterwards.

So the contract proves the correct thing: `:(literal)` bounds what Git itself
selects, which is where the cost and the surprise live. It does not claim that
`ValidationState` would be wrong without it. Step 3 should describe the
guarantee in those terms.

### Validation evidence for step 2 code-reviewer round 4

Every command in the resolved set ran after the repair. `ghog day --force`
reports `fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0` over 1,748
tests, with the full phase at 1 minute 34.0 seconds and a slowest call of 0.41
seconds. The request records 1 minute 23.8 seconds and 0.42 seconds from the
writer's run; wall-clock differs between machines and runs while every reported
outcome field agrees, and the outlier count is zero in both.

The plan completion grep returns 61 matches.
`bin/code_review_evidence.bat --help` exits 0 from the repository root.
`git diff --cached --check` exits 0. No resolver drift: the four commands are
the project default plus two plan additions plus one request addition, and the
current resolver produces the same set.

Line counts are 479, 105, 248, 202, and 461 for the evidence hub, common
boundary, validation-state module, CLI, and request renderer, and 221, 456, 328,
257, and 490 for the staged test modules and package fixture. All are below the
650-line ceiling, and both evidence test modules are below the plan's 550-line
split threshold. Every number the validation plan states re-measures exactly.

### a.commit assessment for step 2 code-reviewer round 4

Accurate, no amendment needed. Running the step's own validator,
`validate_commit_plan(parse_clipboard_content(a.commit, interactive=False),
staged_paths)`, returns zero diagnostics against the exact staged set: two
ordered groups, conventional subjects, exact membership over all fifteen paths,
and no duplicate or missing path. Both narratives match their membership, and
both `What` lists now name the real-Git contract and the 1,748-test result. The
repair landed inside an existing Group 2 member. No commit was created.

### Non-blocking observations for step 2 code-reviewer round 4

`assert real_git_commands is True` can never fail, since the fixture returns a
constant. It reads as a contract assertion but its real job is to request the
fixture so the autouse fake stands down. A short comment saying that would age
better than the assertion.

The duplicate `## Round 1 by human - Step 2` heading pair still lands through
Group 2. It was rendered before the store began qualifying human headings by
outcome, it cannot recur, and correcting it would mean rewriting published
protocol bytes.

The package now carries three byte-identical `_git` helpers, and Step 6 already
plans a `fixtures.py` that is their natural home. The isort import style and
`capture_index_tree` not routing through `run_git_evidence` remain as described
in earlier rounds. None of these is a defect.

### Final reviewer decision for step 2 code-reviewer round 4

Decision: commit-ready. Step 2 is fully implemented against its plan step; every
finding from rounds one through three is closed and independently verified, the
round-three blocking finding by mutation and by direct Git probe; `a.commit`
matches the staged set exactly; and all four resolved validation commands are
green with 100% coverage and zero outliers. The only repair in this round is
polishing-only, so it does not forbid this recommendation.

This recommendation is advisory. It authorizes no commit, and the human gate
remains the sole authority for the `Commit` choice.

<!-- review-entry-id: answer-round-4 -->

## Round 4 by human - Step 2 - human-confirmation

- Recorded: 2026-08-16T21:44:19+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 2
- Outcome: human-confirmation

Human choice: Rework and review again
Outcome: another-round
Guidance: Rework and review again.

No Markdown file may carry a linter warning under the repository
`.markdownlint.json`, and no document may repeat a heading title. MD024 and
MD025 are not negotiable and neither rule may be disabled to make a file pass.

The `bis` suffix hand-written onto the published `human-reclaim-round-1` heading
is not acceptable: it is a counter, it edits protocol bytes by hand, and no
renderer would emit it. Restore both round-one human headings to exactly what
the current store renders, which qualifies a human entry by its outcome, and fix
every remaining duplicate or warning at its source rather than in the rendered
output.

<!-- review-entry-id: human-confirmation-round-4 -->
