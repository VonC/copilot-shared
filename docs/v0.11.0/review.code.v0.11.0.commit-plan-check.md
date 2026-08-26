# Code review transcript for v0.11.0

- Exchange: code/code/v0.11.0/commit-plan-check
- Reviewed document: docs/v0.11.0/plan.v0.11.0.commit-plan-check.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor - Step 1

- Recorded: 2026-08-26T13:00:18+02:00
- Exchange: code/code/v0.11.0/commit-plan-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.commit-plan-check.md
- Implementation step: 1
- Outcome: request

### Review identity for step 1 commit-plan-check (round 1)

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: docs/v0.11.0/plan.v0.11.0.commit-plan-check.md
Implementation step: 1
Review round: 1

### Code review evidence for step 1 commit-plan-check (round 1)

request_index_tree: 25d13fc7fc2b8f46a86f86d22c89ee82b2598cc5
resolved_validation_set:

- ghog day (sources: project)
- ghog single tests/unit/tools/test_commit_plan_support/test_commit_plan_support_tdd.py tests/unit/tools/test_git_batch_commit_workflow_process.py (sources: plan)
- rg -n staged_paths tools/commit_plan_support.py tools/git_batch_commit_workflow.py tests/unit/tools/test_commit_plan_support tests/unit/tools/test_git_batch_commit_workflow_process.py (sources: plan)
- git diff --cached --check (sources: request)

### Requestor assessment for step 1 commit-plan-check (round 1)

Step 1 is fully implemented against the settled plan.

The implementation uses one public staged-path inventory function, preserves
the batch workflow's compatibility helper as a thin delegate, and leaves the
validator and commit execution unchanged. The support boundary performs one Git
call and one linear NUL decode with no per-path filesystem probes.

Focused tests cover the exact Git arguments, repository root, command options,
path order, whitespace, deletions, both rename sides, and empty inventory. The
final groundhog walk reported
`fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0`.

No DDD-Hexagonal boundary smell, performance issue, line-budget breach, unit
coverage gap, or impaired feature behavior was found.

### Implementation report for step 1 commit-plan-check (round 1)

The new `tools/commit_plan_support.py` module owns
`staged_paths(root)`. It invokes
`git diff --cached --name-only --no-renames -z` through the existing
cross-platform Git adapter and returns ordered nonempty NUL-delimited paths.

`tools/git_batch_commit_workflow.py` retains `_staged_paths(root)` as a private
compatibility seam and delegates directly to the new public function. Its
existing validation call still passes that tuple to `validate_commit_plan`
before any mutation.

The new focused test leaf proves the subprocess and decoding contract. The
existing workflow test now proves delegation and unchanged validator wiring.
All implementation and test files remain below their advisory budgets.

### Change summary for step 1 commit-plan-check (round 1)

The staged tree contains ten paths in four proposed commit groups:

1. Repair the persisted specification-review transcript's ordered-list spacing.
2. Stabilize verification-gate tests by naming a threshold, removing duplicated
   legacy assertions, and eliminating one redundant lifecycle classification.
3. Add the shared staged inventory function, batch delegate, and focused tests.
4. Record the required Step 1 validation evidence as the final commit.

The root `a.commit` contains these subjects in dependency order:

- `docs(commit-plan): fix review list formatting`
- `test(workflow): stabilize verification gates`
- `feat(commit-plan): share staged path inventory`
- `docs(commit-plan-check): record step 1 validation`

### Writer response for step 1 commit-plan-check (round 1)

Writer response: This is the initial implementation review round, so there is no earlier reviewer
feedback or disagreement to assess.

The writer requests review of the exact Step 1 scope, all staged paths, the
implementation-check result, and the proposed four-group `a.commit` plan.

### Reviewer focus for step 1 commit-plan-check (round 1)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-1-round-1 -->

## Round 1 by reviewer - Step 1

- Recorded: 2026-08-26T13:15:50+02:00
- Exchange: code/code/v0.11.0/commit-plan-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.commit-plan-check.md
- Implementation step: 1
- Outcome: answer

### Assessed index identity for step 1 commit-plan-check (exchange 1) (round 1)

Baseline index tree: 25d13fc7fc2b8f46a86f86d22c89ee82b2598cc5

Assessed index tree: 25d13fc7fc2b8f46a86f86d22c89ee82b2598cc5

### Implementation check for step 1 commit-plan-check (exchange 1) (round 1)

Result: Yes. Step 1 has been fully implemented. I reached that verdict independently rather than by accepting the requestor's assessment, and it matches theirs.

The shared boundary is real and singular. `tools/commit_plan_support.py` owns `staged_paths(root)`, which runs the exact tuple `("diff", "--cached", "--name-only", "--no-renames", "-z")` through the existing cross-platform Git adapter with `GitCommandOptions(capture_output=True, encoding="utf-8")` and returns the ordered nonempty NUL-decoded tuple. The decisive parity evidence is negative rather than positive: `--no-renames` and `-z` no longer appear anywhere in `tools/git_batch_commit_workflow.py`, so no second Git invocation survived the extraction.

The compatibility seam behaves as Q02 settled it. `git_batch_commit_workflow._staged_paths(root)` is now a one-line delegate to `commit_plan_support.staged_paths(root)` with no inventory policy of its own, and `_validate_commit_plan_for_root` still passes that tuple to the unchanged public validator before any mutation. Because the delegate resolves the module attribute at call time, both existing monkeypatch seams still work, and I confirmed both survive at `tests/unit/tools/test_git_batch_commit_workflow_process.py:248` and `:298`.

The import removal is safe. `run_cross_platform_git_command` and `GitCommandOptions` have no remaining use in the workflow module, so dropping that import leaves no dangling reference.

Test coverage matches the contract the plan required. The new focused leaf pins the exact argument tuple, the repository root passed as `cwd`, the capture and encoding options, order and whitespace preservation including a leading space, a trailing space and an embedded newline, deletion membership, both `--no-renames` rename sides kept separate, and empty-segment handling that cannot manufacture phantom paths. The rewritten workflow test proves the delegate forwards the exact root and returns the public result unchanged, and the argument assertions it gave up were not lost but relocated to the module that now owns them.

Every line budget holds, and the extraction paid for itself. `tools/commit_plan_support.py` is 38 lines against an 80-line advisory, `tools/git_batch_commit_workflow.py` fell from 484 to 481 against a 490 advisory, the new test leaf is 4 and 135 lines against 5 and 180, and the updated workflow test fell from 353 to 347 against 370. Nothing approaches the 550 risk band or the 650 ceiling.

Architecture is clean in the direction that matters. The neutral support module depends only on the Git command adapter, the committing workflow depends on the support boundary, and no reverse dependency exists. Parser, validator, renderer, and commit-execution responsibilities stayed out of the support module, which is what keeps the Step 2 checker able to consume it without importing commit execution.

Performance is one Git subprocess call and one linear split-and-filter pass. There is no per-path filesystem probe, no nested membership scan, no added sort, and no quadratic or log-linear work introduced.

No existing behavior is impaired. The validator receives the same ordered tuple by the same call path, rename and deletion semantics are unchanged because the Git arguments are byte-identical, and commit execution was not touched.

Validation plan effects: I made no change to the validation plan. The writer had already recorded the Step 1 rows, and I found them correct, so there was nothing for reviewer mode to write.

The recorded rows conform to the template contract. The first sentence under `### Analysis of Step 1 implementation state` is exactly `Yes. Step 1 has been fully implemented.` with no prefix and no restatement of the step title, followed by a blank line and then a prose summary. Because the verdict is Yes, no `### Missing work for Step 1` section is required and none is present.

The document-level status line is correctly left at `No, it is not implemented.` Steps 2, 3 and 4 still read `Not started`, so the flip to `Yes, it is implemented.` would have been wrong here. I re-read all four `### Analysis of Step N implementation state` sections to confirm that.

The per-section content is accurate against the code rather than merely plausible. The architecture, performance, unit coverage and feature integrity sections each end with the required explicit yes-or-no sentence, and each of those four verdicts matches what I found independently.

No umbrella row was completed, and reviewer mode correctly suppressed that section: Step 1 is not the final step, and the umbrella digest is unchanged.

### Pre-repair mandatory checks and coverage for step 1 commit-plan-check (exchange 1) (round 1)

Coverage and correctness reproduce. Gate stability does not.

A plain `ghog day` does not re-prove the recorded result. It short-circuits with `No Python file changed since the last green ghog day walk - nothing to do (use --force to walk anyway)` and reports `cov=skipped outliers=skipped excluded=skipped exit=0`. Accepting that as coverage evidence would have been accepting a cached verdict, so I forced a real walk instead.

I ran `ghog day --force` twice, and the two runs disagree:

- Run one: `ghog full done fail=0 warn=0 xfail=0 cov=100 outliers=1 excluded=0 exit=8`.
- Run two: `ghog full done fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0`, reporting `Objective reached`.

The correctness and coverage axes are stable and match the requestor's claim: `fail=0`, `warn=0`, `xfail=0`, and `cov=100` on both runs across 2,010 tests. `ghog single` on the two Step 1 test files is also green with nothing failing in focus and no focus-versus-suite interaction.

The duration axis is not stable, and the flapping call is the one this commit set out to stabilize. Both runs name `tests/unit/tools/test_review_exchange_lifecycle/test_review_exchange_lifecycle_answers_tdd.py::test_reviewer_wait_spans_answer_pending_until_the_replacement_request` as the slowest call in the suite. Run one measured it at `0.55s` against the `0.50s` floor, which produced the single outlier and step exit `8`. Run two measured the same call at `0.41s`, under the floor, which produced `outliers=0` and exit `0`.

That is the flapping case the tool explicitly refuses to accept as fixed by re-measurement: "a call only slightly above the floor will flap on the next jitter, so do not just re-measure - shorten each call listed above the floor until it lands well below the floor with margin to spare". The measured spread of `0.41s` to `0.55s` around a `0.50s` floor is exactly that condition.

This matters for attribution rather than blame. Group 2 of the staged set modifies this very test, and its commit body states the intent: the test "repeated a persisted-state read during its fake wait, leaving it vulnerable to duration-floor jitter". The change is a genuine improvement, since it removes one `core.classify()` persisted-state read per poll and halves the poll count by moving `poll_interval` from `1` to `2`. The clock is a fake with no real sleep, so the remaining cost is real protocol artifact IO from `publish_answer`, `consume_answer`, `continue_round`, and `_start_and_request`. The improvement was not enough to clear the floor with margin, so the stated goal of that group is not yet met.

The requestor's recorded line is therefore reproducible but not dependable. `outliers=0 excluded=0 exit=0` is a real result that I obtained on run two, and it is recorded in the validation plan as settled repository-gate evidence. It is one sample of a two-sided distribution that straddles the floor.

The pre-existing accepted exclusion is healthy and unrelated: `tests/unit/tools/markdown_check/test_launcher/test_launcher_tdd.py::test_root_launcher_runs_without_an_activated_project_environment` is recorded at `0.85s` and currently measures `0.72s` and `0.76s`, comfortably inside its accepted budget.

I also ran the repository Markdown gate. It reports no finding for the plan, the validation plan, or either review transcript, so MD024 and MD025 hold across the appended rounds.

### Resolved validation set and sources for step 1 commit-plan-check (exchange 1) (round 1)

The request resolved four commands. I ran the union of that set and the current plan-derived resolver set, so five distinct commands were executed.

- `ghog day` — source `project`. The repository gate.
- `ghog single tests/unit/tools/test_commit_plan_support/test_commit_plan_support_tdd.py tests/unit/tools/test_git_batch_commit_workflow_process.py` — source `plan`. Targeted Step 1 tests.
- `rg -n staged_paths tools/commit_plan_support.py tools/git_batch_commit_workflow.py tests/unit/tools/test_commit_plan_support tests/unit/tools/test_git_batch_commit_workflow_process.py` — source `request`, narrowed relative to the plan.
- `rg -n "staged_paths|--no-renames|-z|validate_commit_plan" tools/commit_plan_support.py tools/git_batch_commit_workflow.py tests/unit/tools/test_commit_plan_support tests/unit/tools/test_git_batch_commit_workflow_process.py` — source `plan`, the full pattern at `docs/v0.11.0/plan.v0.11.0.commit-plan-check.md:324`, added by the union.
- `git diff --cached --check` — source `request`.

Every command ran. None was unavailable, so there is no missing mandatory evidence on the availability axis.

`git diff --cached --check` returned exit `0` with no whitespace or conflict-marker finding across the ten staged paths.

Both `rg` commands pass and together supply the parity evidence. The narrowed request form returns 25 matching lines. The full plan pattern additionally proves the negative that matters: `--no-renames` and `-z` now appear only in `tools/commit_plan_support.py` at lines 20 and 21 and in the focused test's argument assertion, and appear nowhere in `tools/git_batch_commit_workflow.py`, while `validate_commit_plan` is still reached through `_staged_paths(root)` at `tools/git_batch_commit_workflow.py:201`. One Git inventory implementation exists, and delegation is covered by tests.

`ghog single` on the two Step 1 test files reports `fail=0 warn=0 xfail=0 exit=0` with nothing still failing in focus and nothing passing in focus while failing in the full suite.

`ghog day` needed care and is reported in the pre-repair validation evidence rather than here, because a plain invocation does not re-prove the recorded result.

### Resolver drift and direction for step 1 commit-plan-check (exchange 1) (round 1)

One drift was found, and it narrows the request relative to the plan.

The plan's Step 1 completion criteria at `docs/v0.11.0/plan.v0.11.0.commit-plan-check.md:324` specify:

```text
rg -n "staged_paths|--no-renames|-z|validate_commit_plan" tools/commit_plan_support.py tools/git_batch_commit_workflow.py tests/unit/tools/test_commit_plan_support tests/unit/tools/test_git_batch_commit_workflow_process.py
```

The request's resolved validation set carries the narrowed form instead:

```text
rg -n staged_paths tools/commit_plan_support.py tools/git_batch_commit_workflow.py tests/unit/tools/test_commit_plan_support tests/unit/tools/test_git_batch_commit_workflow_process.py
```

Direction: the request command is a strict subset of the plan command. It drops the `--no-renames`, `-z`, and `validate_commit_plan` alternatives, which are exactly the terms that prove the Git inventory was not duplicated and that the validator still receives the shared result. The narrowed form alone could pass while a second Git invocation survived in the workflow module.

I ran the union rather than either alone. Both commands were executed and both pass. The full plan pattern supplies the evidence the narrowed form would have missed: `--no-renames` and `-z` now appear only in `tools/commit_plan_support.py` at lines 20 and 21 and in the focused test assertion, and no longer appear anywhere in `tools/git_batch_commit_workflow.py`. That is the decisive parity evidence for Step 1.

No drift was found in the other three commands. This drift is reported, not repaired; the resolved set belongs to the requestor.

### Repository state around validation for step 1 commit-plan-check (exchange 1) (round 1)

My assessment produced no repository side effect. I made no repair, so the only writes were ignored root `a.*` reviewer evidence files.

Index identity held throughout. The request-time `request_index_tree` is `25d13fc7fc2b8f46a86f86d22c89ee82b2598cc5`, and `capture-index-tree` returned the identical value both before assessment and after the validation runs, so no early rejection was triggered and no staged change occurred during review.

The umbrella is untouched. `umbrella-digest capture` and `umbrella-digest compare` on `docs/v0.11.0/draft.v0.11.0.review-mode.md` both return `020d1d67f9a3dca50a2651e6dd7b6717b3f1a7ef5521c5eaf4a27de6e2c3b79c` with `changed: false`, so no boundary violation exists.

The validation-state comparison is clean. Using the same ordered ten-path set before and after, `validation-state compare` returns `acceptable: true` with empty `tracked_paths`, `untracked_paths`, and `ignored_paths`. No tracked validation side effect appeared, so nothing had to be left unstaged and unreverted.

One expected and acceptable difference sits outside that set. Running the full gate refreshed ignored coverage and test-selection artifacts such as `.coverage`, `.testmondata`, `a.ghog.log`, and `a.ghog.outliers`. These are ignored validation artifacts, which the contract explicitly accepts, and none is tracked or staged.

The only untracked path in the working tree is `docs/v0.11.0/review.code.v0.11.0.commit-plan-check.md`, this exchange's own transcript, created by the protocol rather than by my assessment.

### Repair inventory for step 1 commit-plan-check (exchange 1) (round 1)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 1 commit-plan-check (exchange 1) (round 1)

`a.commit` is mechanically accurate. I verified it rather than reading it, by running the repository's own public validator over the exact index: `parse_clipboard_content(content, interactive=False)`, then `commit_plan_support.staged_paths(root)`, then `validate_commit_plan(blocks, staged_paths)`.

The result is ten staged paths, four ordered groups, `valid=True`, and zero diagnostics. Every staged path appears exactly once and no planned path is absent from the index.

Group membership matches the staged set exactly:

- Group 1 `docs(commit-plan): fix review list formatting` carries the one spec-review transcript path.
- Group 2 `test(workflow): stabilize verification gates` carries the three verification-gate test paths.
- Group 3 `feat(commit-plan): share staged path inventory` carries the two production paths and the three Step 1 test paths.
- Group 4 `docs(commit-plan-check): record step 1 validation` carries the validation plan.

Ordering is least to most dependent and is correct: the transcript repair and the gate maintenance are independent, the feature follows, and the validation record depends on the feature it documents. Every subject is a conventional commit with an accurate scope.

One observation that needs no change now. The untracked `docs/v0.11.0/review.code.v0.11.0.commit-plan-check.md` is this exchange's own transcript and is deliberately absent from `a.commit`, since the round is still open and the transcript keeps growing. It must be included when the commit is finally taken, which the `git add -A` grouping pass at the commit gate will pick up.

I did not amend `a.commit`. Membership, ordering, scope, and subjects are all already accurate, so an amendment would have been a substantive change to commit grouping with no defect to correct.

### Findings and boundaries for step 1 commit-plan-check (exchange 1) (round 1)

Unresolved findings:

- Paired review renderers inline caller-authored Markdown directly after a `Label:` prefix and a following space on the same line, so any authored block that begins with a list item, heading, fence, or blockquote is structurally broken in both the published artifact and the versioned transcript. Verified call sites: `tools/spec_review_answer.py:188` (`Requested changes:` plus a following space), `tools/spec_review_request.py:177` and `:189` (`Writer response:` plus a following space), `tools/code_review_request.py:211` and `:223` (`Writer response:` plus a following space), and `tools/code_review_answer.py:335` and `:336` (`Result:` and `Validation plan effects:`, each plus a following space). The correct idiom already exists in the same file at `tools/code_review_answer.py:288`, where `_inventory` emits `f"{label}:\n\n"` before its list.
- This defect produced the exact damage that group 1 of the staged set repairs by hand: the round-one requested-change list in `docs/v0.11.0/review.plan.v0.11.0.commit-plan-check.md` was flattened onto its `Requested changes:` label line. Because the cause is unfixed, every future round whose authored block starts with a list or heading reproduces it and requires another hand edit to a versioned protocol artifact.
- The caller-authored heading contract in `instructions/review-requestor.md` is also unimplemented. That instruction states that generated request sections are level 2 and generated transcript sections are level 3, so caller-authored headings are shifted to level 3 or level 4 and qualified with identity, slug, exchange, and a final `(round N)` suffix. No such shift or qualification occurs: reviewer-authored `##` headings appear verbatim at level 2 inside level-3 sections in `docs/v0.11.0/review.plan.v0.11.0.commit-plan-check.md` at lines 138, 155, 171, 187, 204, 222, 263, 320, 365, 386, 400, 408, 543, 566, 580 and 596. MD024 and MD025 currently pass only because every authored heading text happened to be unique; the outline is already wrong and a future collision would become a transcript defect rather than a caught one.

Boundary-crossing work:

- Repairing the label-inlining defect would touch `tools/spec_review_answer.py`, `tools/spec_review_request.py`, `tools/code_review_request.py`, and `tools/code_review_answer.py`. None is named by Step 1, so I left all four unchanged and report them here rather than editing them.
- `tools/code_review_request.py` is additionally a Step 3 file in this same plan, where the requestor publication gate is added. A renderer fix landed there now would collide with Step 3, so the sequencing belongs to the writer rather than to this step.
- Implementing the caller-authored heading shift and qualification contract would touch the same renderer modules plus the shared section helpers. It is review-mode tooling work outside Step 1 and is reported rather than attempted.
- Groups 1 and 2 of the staged set are outside Step 1's plan file list. I assessed them because they are staged and carried by this commit plan, but I made no change to them. Their presence is legitimate under the grouped-commit rule that stages the whole tree and groups every staged change by its own dependencies.

### Writer instructions for step 1 commit-plan-check (exchange 1) (round 1)

Step 1 itself needs no rework. The implementation, its tests, its budgets, and the `a.commit` grouping are all correct, and I am not asking for a single change to `tools/commit_plan_support.py`, `tools/git_batch_commit_workflow.py`, or either Step 1 test file. Please do not rework them.

The requested changes are these.

Give the flapping test real margin. `tests/unit/tools/test_review_exchange_lifecycle/test_review_exchange_lifecycle_answers_tdd.py::test_reviewer_wait_spans_answer_pending_until_the_replacement_request` measured `0.55s` and `0.41s` on two forced walks against a `0.50s` floor, so the gate returns exit `8` on some runs and exit `0` on others. That file is already staged in group 2, and group 2's own commit body names this jitter as the problem it set out to solve, so this is finishing the work that group already claims rather than new scope. Follow `instructions/fix_slow_test.md` and shorten the call until it lands well below the floor with margin, then confirm with `ghog single` on that file followed by a forced `ghog day`. The dominant cost is real protocol artifact IO across `publish_answer`, `consume_answer`, `continue_round`, and `_start_and_request`, not the fake clock, so the reduction has to come from doing less artifact work per poll rather than from tuning `poll_interval` again. If the call proves irreducible under that instruction, the sanctioned alternative is `ghog exclude <node id> <measured seconds>`; do not raise the floor on line 2 of `a.ghog.outliers`.

Correct the recorded gate evidence in the validation plan. `docs/v0.11.0/plan.v0.11.0.commit-plan-check.validation.md` records `fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0` as settled repository-gate evidence for Step 1. That line is one sample from a distribution that straddles the floor, and a plain `ghog day` cannot re-prove it because it short-circuits to `cov=skipped`. Once the test has margin, re-run `ghog day --force` and record the result together with the fact that `--force` is required to reproduce it. If you prefer to keep the current wording, it must at least stop presenting `outliers=0 exit=0` as stable.

Record the renderer defect instead of only repairing its output. Group 1 hand-edits `docs/v0.11.0/review.plan.v0.11.0.commit-plan-check.md`, a versioned protocol artifact, to repair damage the tooling caused and will cause again. The cause is that paired renderers inline caller-authored Markdown directly after a `Label:` prefix and a following space on the same line, at `tools/spec_review_answer.py:188`, `tools/spec_review_request.py:177` and `:189`, `tools/code_review_request.py:211` and `:223`, and `tools/code_review_answer.py:335` and `:336`. The correct idiom already exists in the same file at `tools/code_review_answer.py:288`, where `_inventory` emits `f"{label}:\n\n"` before its list. At minimum, amend group 1's commit body to name that root cause and those call sites so the workaround is greppable in history rather than reading as a one-off formatting nit. Do not fix the renderers inside this step: `tools/code_review_request.py` is a Step 3 file in this same plan and a change there now would collide with the Step 3 publication gate. Decide where that work belongs, given that umbrella rows 9 and 10 are still pending.

Reconcile the resolved validation set with the plan. The request carried `rg -n staged_paths ...`, while the plan's Step 1 completion criteria at `docs/v0.11.0/plan.v0.11.0.commit-plan-check.md:324` specify the wider `rg -n "staged_paths|--no-renames|-z|validate_commit_plan" ...`. The narrowed form drops exactly the terms that prove the Git command was not duplicated. I ran the union and both pass, so nothing is broken, but later rounds should carry the plan's pattern so the parity evidence is not silently weakened.

One optional observation, not a requested change. The caller-authored heading contract in `instructions/review-requestor.md` promises that renderers shift authored headings to level 3 or 4 and qualify them with identity and a `(round N)` suffix. No shift or qualification happens, so authored `##` headings sit at level 2 inside level-3 sections in both transcripts. MD024 and MD025 pass today only because every authored heading text happened to be unique. It belongs with the same tooling decision as the label defect.

### Decision rationale for step 1 commit-plan-check (exchange 1) (round 1)

I am publishing `changes-requested`, and I made no repair of any kind this round.

Five of the six readiness-floor results pass. Identity is exact: the request envelope, human-readable identity, plan, step, round, and exchange occurrence all agree, and the request-time index tree `25d13fc7fc2b8f46a86f86d22c89ee82b2598cc5` still matches the live index, so no early rejection applied. Implementation completeness is a genuine Yes that I derived independently. Staged attribution is clean, with every staged path belonging to a coherent group and no pre-existing unstaged work swept into the index. The `a.commit` grouping is mechanically valid against the exact index, with four groups, ten paths, and zero validator diagnostics. Coverage is `100` and the suite is green on every run I made.

The sixth result, mandatory validation, does not pass stably, and that is the blocking reason. `ghog day --force` returned exit `8` on one run and exit `0` on another, because the suite's slowest call flaps across the duration floor at `0.55s` and `0.41s` against `0.50s`. The repository's own gate therefore does not reliably report its objective as reached. The tool is explicit that re-measuring is not a fix for a call sitting that close to the floor, so I did not treat the green run as the answer. The flapping call is in a file this commit already stages, in the group whose commit body claims to have addressed that exact jitter, so the gap is between that group's stated intent and its measured effect rather than a defect I am importing from elsewhere.

Two verified findings remain unresolved, and the answer model itself refuses to pair them with a commit-ready recommendation. The renderer label-inlining defect is reproducible across seven call sites in four modules, it already damaged a versioned protocol artifact, and group 1 of this commit repairs that damage by hand without recording the cause, so the workaround will be needed again next round. The unimplemented caller-authored heading contract is the same class of defect and currently passes lint only by luck.

I deliberately did not repair any of it. The renderer fix lies outside Step 1 and would touch `tools/code_review_request.py`, which is a Step 3 file in this same plan, so repairing it here would both cross the step boundary and collide with later planned work. Amending group 1's commit body would have been a substantive change to commit grouping, which cannot validly finish the workflow in the same round, so I requested it rather than performing it. Because I made no substantive repair, nothing in this answer invalidates a commit-ready recommendation in the next round.

What I am asking for is proportionate. Step 1's implementation is correct and I explicitly asked that it not be reworked. The blocking item is finishing the stabilization that group 2 already started, in a file already staged, plus correcting one evidence line and recording one root cause. None of it requires reopening a settled requirement, design, or plan decision.

This recommendation is advisory and authorizes nothing. Only the human may choose `Commit` or `Rework and review again`, and a green checker or gate result would not by itself confer commit authority.

### Final reviewer decision for step 1 commit-plan-check (exchange 1) (round 1)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-1-round-1 -->

## Round 2 by requestor - Step 1

- Recorded: 2026-08-26T13:30:21+02:00
- Exchange: code/code/v0.11.0/commit-plan-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.commit-plan-check.md
- Implementation step: 1
- Outcome: request

### Review identity for step 1 commit-plan-check (round 2)

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: docs/v0.11.0/plan.v0.11.0.commit-plan-check.md
Implementation step: 1
Review round: 2

### Code review evidence for step 1 commit-plan-check (round 2)

request_index_tree: 5d8fde87ef62ef4ffd16d968b45a25a1519cd982
resolved_validation_set:

- ghog day (sources: project)
- ghog single tests/unit/tools/test_commit_plan_support/test_commit_plan_support_tdd.py tests/unit/tools/test_git_batch_commit_workflow_process.py (sources: plan)
- rg -n --regexp=staged_paths --regexp=--no-renames --regexp=-z --regexp=validate_commit_plan tools/commit_plan_support.py tools/git_batch_commit_workflow.py tests/unit/tools/test_commit_plan_support tests/unit/tools/test_git_batch_commit_workflow_process.py (sources: plan)
- ghog day --force (sources: request)
- git diff --cached --check (sources: request)

### Requestor assessment for step 1 commit-plan-check (round 2)

Step 1 remains fully implemented, and every required round-one correction is
now incorporated.

The lifecycle timing repair moves first-round artifact setup into a pytest
fixture while preserving the complete answer-consume-continue-request wait in
the measured call. Re-measurement reports 0.27s in setup and no slow call-phase
entry. The focused groundhog run is green.

A forced `ghog day --force` bypassed the cached no-op and reported
`fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0` across 2,010 tests.
The validation plan now names that forced evidence explicitly.

The commit plan retains accurate membership and order. Group 1 now records the
four deferred renderer call-site families that caused the transcript damage,
and group 2 describes the fixture-based timing repair.

### Implementation report for step 1 commit-plan-check (round 2)

The Step 1 production implementation is unchanged from round 1 because the
reviewer independently found it complete and requested no rework there.

The required timing repair changes only
`test_review_exchange_lifecycle_answers_tdd.py`. A fixture now performs harness
creation, round-one request publication, and answer publication during pytest
setup. The measured call still drives `wait_for_exact` through answer
consumption, continuation, round-two publication, and exact request discovery.

The validation record now states that the green coverage and duration evidence
came from `ghog day --force`. The root commit plan records the deferred renderer
root cause without changing group boundaries or subjects.

### Change summary for step 1 commit-plan-check (round 2)

The staged tree still contains the same ten paths and four groups. Round-one
repairs changed two already-staged paths and the ignored root commit plan:

- Move lifecycle artifact setup to a fixture for duration margin
- Record the forced green groundhog result in the Step 1 validation block
- Name the deferred label-inlining renderer call sites in group 1
- Update group 2 wording to match the fixture-based repair

The final subject remains
`docs(commit-plan-check): record step 1 validation` as required.

### Writer response for step 1 commit-plan-check (round 2)

Writer response: All required round-one feedback was accepted with no disagreement.

The flapping lifecycle call now performs its real protocol artifact setup in a
pytest fixture. The measured call retains every transition and assertion but no
longer reports as a slow call; the only reported duration is 0.27s in setup.
A focused run and a forced full groundhog walk are green, with 100% coverage and
no outlier.

The validation plan explicitly names `ghog day --force`, so the recorded result
cannot be mistaken for the cached no-op. Group 1's body now names
`tools/spec_review_answer.py`, `tools/spec_review_request.py`,
`tools/code_review_request.py`, and `tools/code_review_answer.py` as the deferred
label-inlining root cause. No renderer was changed in Step 1 because that work
belongs to later review-mode planning and would collide with Step 3.

The round-two validation set carries all four parity terms: `staged_paths`,
`--no-renames`, `-z`, and `validate_commit_plan`. The optional authored-heading
finding remains deferred with the related renderer work.

### Reviewer focus for step 1 commit-plan-check (round 2)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-1-round-2 -->

## Round 2 by reviewer - Step 1

- Recorded: 2026-08-26T13:40:20+02:00
- Exchange: code/code/v0.11.0/commit-plan-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.commit-plan-check.md
- Implementation step: 1
- Outcome: answer

### Assessed index identity for step 1 commit-plan-check (exchange 1) (round 2)

Baseline index tree: 5d8fde87ef62ef4ffd16d968b45a25a1519cd982

Assessed index tree: 5d8fde87ef62ef4ffd16d968b45a25a1519cd982

### Implementation check for step 1 commit-plan-check (exchange 1) (round 2)

Result: Yes. Step 1 has been fully implemented. That verdict is unchanged from round one, and I re-derived it rather than carrying it forward on trust.

The Step 1 production work is byte-identical to what I already accepted. `git diff --cached --stat` over the five Step 1 paths reports exactly the same shape as round one, and the line counts are unchanged at 38 for `tools/commit_plan_support.py`, 481 for `tools/git_batch_commit_workflow.py`, 135 for the new focused test, and 347 for the updated workflow test. The requestor honored my request not to rework correct code.

Parity still holds under the widened validation command. `--no-renames` and `-z` appear nowhere in `tools/git_batch_commit_workflow.py`, so no second Git invocation exists, and `validate_commit_plan` is still reached through the delegate. That is the negative evidence the round-one narrowed command would have missed, and the round-two set now proves it directly.

The round-one blocker is genuinely fixed rather than re-measured. The repair moves first-round harness creation, request publication, and answer publication into the `replacement_request_round` fixture, leaving the measured call to drive `wait_for_exact` through answer consumption, round continuation, round-two publication, and exact request discovery. This is the technique `instructions/fix_slow_test.md` prescribes at line 40 for per-call heavy construction, which states that moving it to a fixture "also takes it out of the call phase the rule measures".

The fixture is function-scoped rather than module- or session-scoped, and that is correct here rather than a shortcut. It depends on `tmp_path`, which is itself function-scoped, so a broader scope is not available. It also has exactly one consumer, so "paid once" and "paid per call" are the same cost, and the instruction's reason for preferring a broader scope does not apply.

Test coverage of the behavior is fully preserved. All six assertions are unchanged, and the call still enters the wait while the exchange sits in answer-pending, so the span the test name claims is still proven by construction rather than by the removed `classify()` guard, which was a callback condition rather than an assertion.

Architecture, performance, and feature integrity are unchanged from round one and remain clean. The support module still depends only on the Git command adapter, the inventory is still one subprocess call and one linear decode, and no existing behavior is impaired.

Validation plan effects: I made no change to the validation plan again this round. The requestor's rows were already correct, so reviewer mode had nothing to write.

The round-one correction I asked for is present. The repository gate evidence line now reads that the forced `ghog day --force` bypassed the cached green no-op and completed with `fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0`. That removes the ambiguity I flagged, since a plain `ghog day` reports `cov=skipped` and cannot substantiate the claim.

The template contract still holds. The first sentence under `### Analysis of Step 1 implementation state` is exactly `Yes. Step 1 has been fully implemented.`, followed by a blank line and a prose summary, with no prefix and no restatement of the step title. No `### Missing work for Step 1` section is required or present for a Yes verdict.

The document-level status line is still correctly `No, it is not implemented.` I re-read all four `### Analysis of Step N implementation state` sections and Steps 2, 3 and 4 still read `Not started`, so the flip to `Yes, it is implemented.` would be wrong.

No umbrella row was completed and reviewer mode correctly suppressed that section. The umbrella digest is unchanged at `020d1d67f9a3dca50a2651e6dd7b6717b3f1a7ef5521c5eaf4a27de6e2c3b79c`, confirmed by `umbrella-digest compare` reporting `changed: false`.

One optional wording nit, carrying no consequence: the evidence line reads "the final forced `ghog day --force`", where "forced" and `--force` duplicate each other. It could simply read "the final `ghog day --force`". This does not need another round.

### Pre-repair mandatory checks and coverage for step 1 commit-plan-check (exchange 1) (round 2)

The gate is now stably green with real margin, which is what round one could not establish.

I ran `ghog day --force` twice again, because a single green walk is exactly what misled the round-one evidence. Both runs agree:

- Run one: `ghog full done fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0`, reporting `Objective reached`.
- Run two: `ghog full done fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0`, reporting `Objective reached`.

The duration axis is no longer marginal. `tests/unit/tools/test_review_exchange_lifecycle/test_review_exchange_lifecycle_answers_tdd.py::test_reviewer_wait_spans_answer_pending_until_the_replacement_request` has dropped out of the reported slow list entirely. It is no longer the slowest call in the suite, where in round one it measured `0.55s` and `0.41s` against the `0.50s` floor.

The new slowest call is a different and pre-existing test, `tests/unit/tools/test_review_exchange_transcript_identity_tdd.py::test_answer_occurrence_follows_a_restarted_request_without_prior_answer`, at `0.33s` on both runs against the `0.50s` floor. That is 34 percent below the floor and identical across runs, which is the margin `instructions/fix_slow_test.md` asks for rather than a value that will flap on the next jitter.

`ghog single` on the repaired lifecycle test and both Step 1 test files is green, with nothing still failing in focus and nothing passing in focus while failing in the full suite.

`git diff --cached --check` returns exit `0` with no whitespace or conflict-marker finding across the ten staged paths.

Both `rg` parity checks pass, and the widened round-two command supplies the negative evidence directly.

The recorded evidence is now honest about how to reproduce it. The validation plan names `ghog day --force` and states that it bypassed the cached green no-op, so the recorded result can no longer be confused with the `cov=skipped` short-circuit that a plain `ghog day` produces.

The pre-existing accepted exclusion remains healthy and unrelated, with `test_root_launcher_runs_without_an_activated_project_environment` recorded at `0.85s` and currently measuring `0.75s`.

The repository Markdown gate reports no finding for the plan, the validation plan, or either review transcript, so MD024 and MD025 continue to hold across all appended rounds.

### Resolved validation set and sources for step 1 commit-plan-check (exchange 1) (round 2)

The request resolved five commands, and I ran all five. The current plan-derived
resolver set adds nothing this round, so the union equals the resolved set.

- `ghog day` — source `project`. The repository gate.
- `ghog day --force` — source `request`. Added this round so the recorded
  evidence is reproducible rather than a cached no-op.
- `ghog single tests/unit/tools/test_commit_plan_support/test_commit_plan_support_tdd.py tests/unit/tools/test_git_batch_commit_workflow_process.py` — source `plan`.
- `rg -n --regexp=staged_paths --regexp=--no-renames --regexp=-z --regexp=validate_commit_plan tools/commit_plan_support.py tools/git_batch_commit_workflow.py tests/unit/tools/test_commit_plan_support tests/unit/tools/test_git_batch_commit_workflow_process.py` — source `plan`, now carrying all four parity terms.
- `git diff --cached --check` — source `request`.

Every command ran and every command passed. Nothing was unavailable, so there is
no missing mandatory evidence.

I additionally ran `ghog single` on the repaired lifecycle test alongside the two
Step 1 test files, and ran `ghog day --force` twice rather than once, because a
single sample is what made the round-one evidence unreliable.

### Resolver drift and direction for step 1 commit-plan-check (exchange 1) (round 2)

The round-one drift is resolved, and no new drift was found.

The narrowed `rg -n staged_paths ...` command is gone. The round-two resolved set carries all four parity terms through explicit patterns:

```text
rg -n --regexp=staged_paths --regexp=--no-renames --regexp=-z --regexp=validate_commit_plan tools/commit_plan_support.py tools/git_batch_commit_workflow.py tests/unit/tools/test_commit_plan_support tests/unit/tools/test_git_batch_commit_workflow_process.py
```

That form is equivalent in coverage to the plan's alternation at `docs/v0.11.0/plan.v0.11.0.commit-plan-check.md:324` and is safer as a command line, because `--regexp=-z` cannot be mistaken for an `rg` option the way a bare `-z` alternative inside a quoted alternation can. I consider this an improvement on the plan's literal text rather than a deviation from it, and no further reconciliation is needed.

The set also gained `ghog day --force` from the `request` source. That directly addresses the round-one problem that a plain `ghog day` short-circuits to `cov=skipped` and cannot re-prove a recorded result. The resolved set now names the command that actually produces the evidence.

Comparing the round-two request set against the current plan-derived resolver set, the union adds nothing. Every plan command is present, so I ran the resolved set as given rather than a wider union this round.

### Repository state around validation for step 1 commit-plan-check (exchange 1) (round 2)

My assessment produced no repository side effect. I made no repair, so the only writes were ignored root `a.*` reviewer evidence files and ignored validation artifacts.

Index identity held throughout. The round-two request-time `request_index_tree` is `5d8fde87ef62ef4ffd16d968b45a25a1519cd982`, and `capture-index-tree` returned that identical value both before assessment and after two forced full gate walks. No early rejection applied and no staged change occurred during review.

The staged set is unchanged in membership. The same ten paths are staged as in round one; the round-one repairs modified content within two already-staged paths and the ignored root commit plan, without adding or removing any path.

The umbrella is untouched. `umbrella-digest compare` returns `020d1d67f9a3dca50a2651e6dd7b6717b3f1a7ef5521c5eaf4a27de6e2c3b79c` before and after with `changed: false`, so no boundary violation exists.

The validation-state comparison is clean. Using the same ordered ten-path set before and after, `validation-state compare` returns `acceptable: true` with empty `tracked_paths`, `untracked_paths`, and `ignored_paths`. No tracked validation side effect appeared, so nothing had to be left unstaged and unreverted.

Ignored validation artifacts were refreshed as expected by the forced walks, including `.coverage`, `.testmondata`, `a.ghog.log`, and `a.ghog.outliers`. The contract explicitly accepts differences confined to ignored validation artifacts, and none of these is tracked or staged.

The only untracked path in the working tree remains `docs/v0.11.0/review.code.v0.11.0.commit-plan-check.md`, this exchange's own transcript, created by the protocol rather than by my assessment.

### Repair inventory for step 1 commit-plan-check (exchange 1) (round 2)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 1 commit-plan-check (exchange 1) (round 2)

`a.commit` remains accurate, and I re-verified it mechanically rather than by reading it. Running the repository's own `parse_clipboard_content(content, interactive=False)`, then `commit_plan_support.staged_paths(root)`, then `validate_commit_plan(blocks, staged_paths)` against the live index returns ten staged paths, four ordered groups, `valid=True`, and zero diagnostics.

Membership, grouping, order, and subjects are unchanged from round one and still correct. Group 1 carries the spec-review transcript, group 2 the three verification-gate tests, group 3 the two production paths and three Step 1 test paths, and group 4 the validation plan. Ordering remains least to most dependent, and every subject is a conventional commit with an accurate scope. The final subject is still `docs(commit-plan-check): record step 1 validation`.

The round-one instruction about group 1 was satisfied. Its body now states that paired review renderers place caller-authored Markdown directly after a label, and it names `tools/spec_review_answer.py`, `tools/spec_review_request.py`, `tools/code_review_request.py`, and `tools/code_review_answer.py` as the deferred root cause, with an explicit note that Step 1 repairs only the existing transcript. The workaround is now greppable in history instead of reading as a one-off formatting nit, which is exactly what I asked for.

Group 2's body was updated to match what the code now does, describing the move of replacement-round artifact setup into a fixture rather than the earlier wording about a repeated persisted-state read alone. The commit message and the diff agree.

I did not amend `a.commit`. Membership, ordering, scope, and subjects are all accurate, so an amendment would have been a substantive change to commit grouping with no defect to correct, and it would have invalidated a commit-ready recommendation in this same round.

One carry-forward for the commit gate, unchanged from round one and needing no action now. The untracked `docs/v0.11.0/review.code.v0.11.0.commit-plan-check.md` is this exchange's own transcript and is deliberately absent from `a.commit` while the round is still open. The `git add -A` grouping pass at the commit gate will pick it up.

### Findings and boundaries for step 1 commit-plan-check (exchange 1) (round 2)

Unresolved findings: None.

Boundary-crossing work: None.

### Writer instructions for step 1 commit-plan-check (exchange 1) (round 2)

No change is required. Every round-one item is addressed and I am requesting nothing further.

Do not rework Step 1. The production implementation, its tests, the budgets, and the commit grouping are all correct, and the round-two repair to the lifecycle test is the right technique applied correctly.

One optional wording nit, which does not need another round and can be applied or ignored before the commit gate: the validation plan's evidence line reads "the final forced `ghog day --force`", where "forced" and `--force` duplicate each other. "the final `ghog day --force`" reads cleaner.

Two items are deferred by agreement rather than dropped, and should reach the pending review-mode requirements rather than being lost once this commit lands. The first is the label-inlining defect in `tools/spec_review_answer.py`, `tools/spec_review_request.py`, `tools/code_review_request.py`, and `tools/code_review_answer.py`, where the correct idiom already exists at `tools/code_review_answer.py:288`. Sequence it after Step 3, since Step 3 modifies `tools/code_review_request.py`. The second is the unimplemented caller-authored heading shift and qualification contract in `instructions/review-requestor.md`, which belongs with the same work.

At the commit gate, remember that the `git add -A` grouping pass will pick up `docs/v0.11.0/review.code.v0.11.0.commit-plan-check.md`, this exchange's transcript, which is deliberately absent from `a.commit` while the round is open.

If the human selects `Commit`, run the existing commit step. If the human selects `Rework and review again`, treat the wording nit as the full scope of that round unless the human supplies guidance that adds to it.

### Decision rationale for step 1 commit-plan-check (exchange 1) (round 2)

I am recommending `commit-ready`, and I made no repair of any kind in either round, so nothing in this exchange invalidates that recommendation.

All six readiness-floor results now pass. Identity is exact, with the request envelope, human-readable identity, plan, step, round, and exchange occurrence in agreement, and the request-time index tree `5d8fde87ef62ef4ffd16d968b45a25a1519cd982` matching the live index before and after two forced gate walks. Implementation completeness is a Yes I re-derived rather than carried forward. Mandatory validation and coverage now pass stably. Staged attribution is clean across the same ten paths. There is no unresolved finding against this step. The `a.commit` grouping is mechanically valid with zero validator diagnostics.

The round-one blocker is genuinely resolved rather than re-measured, which is the distinction I said I would hold to. Two forced walks now return `cov=100 outliers=0 excluded=0 exit=0` with `Objective reached`, where round one straddled the floor at `0.55s` and `0.41s`. The repaired call has left the slow list entirely, and the suite's slowest call is now a different, pre-existing test at `0.33s` against a `0.50s` floor, identical on both runs. That is margin, not a lucky sample. The technique used is the one `instructions/fix_slow_test.md` prescribes at line 40, and the function scope of the new fixture is forced by its `tmp_path` dependency rather than chosen, with a single consumer making the broader-scope advice moot.

The remaining renderer defect is deferred by explicit decision, and the human should see that clearly at this gate. Paired review renderers still inline caller-authored Markdown after a `Label:` prefix and a following space in `tools/spec_review_answer.py`, `tools/spec_review_request.py`, `tools/code_review_request.py`, and `tools/code_review_answer.py`, and the caller-authored heading shift promised by `instructions/review-requestor.md` is still unimplemented. Neither is caused by Step 1, neither touches Step 1 code, and repairing them here would cross the step boundary and collide with Step 3, which modifies `tools/code_review_request.py`. My round-one instruction was to record the cause rather than fix it, and group 1's commit body now names all four modules, so the workaround is documented in history instead of silently normalized. I classify this as tracked future work for the pending review-mode requirements, not as an unresolved finding against Step 1, and I would not block this commit on it.

I did not amend `a.commit` in either round. Its membership, ordering, scope, and subjects were accurate throughout, so an amendment would have been a substantive change to commit grouping with no defect to correct.

This recommendation is advisory and authorizes nothing. A green gate and a valid commit plan are mechanical evidence only; they do not confer commit authority. Only the human may choose `Commit` or `Rework and review again`.

### Final reviewer decision for step 1 commit-plan-check (exchange 1) (round 2)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-1-round-2 -->

## Round 2 by human - Step 1 - human-confirmation

- Recorded: 2026-08-26T15:57:15+02:00
- Exchange: code/code/v0.11.0/commit-plan-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.commit-plan-check.md
- Implementation step: 1
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-2 -->

## Round 1 by requestor - Step 2

- Recorded: 2026-08-26T18:23:05+02:00
- Exchange: code/code/v0.11.0/commit-plan-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.commit-plan-check.md
- Implementation step: 2
- Outcome: request

### Review identity for step 2 commit-plan-check (round 1)

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: docs/v0.11.0/plan.v0.11.0.commit-plan-check.md
Implementation step: 2
Review round: 1

### Code review evidence for step 2 commit-plan-check (round 1)

request_index_tree: 4d9b89f8a2e497e4d935b3b694511f849c53d55a
resolved_validation_set:

- ghog day (sources: project)
- rg -n CommitPlanCheck tools/commit_plan_check.py commit-plan-check.bat tests/unit/tools/test_commit_plan_check (sources: plan)
- commit-plan-check.bat --format json (sources: request)

### Requestor assessment for step 2 commit-plan-check (round 1)

Step 2 is fully implemented against its exact plan slice.

- Static checks pass for type safety, lint, complexity, file girth, Markdown,
  shell, and EOF rules.
- The final detached Groundhog day passes all 2,039 tests with 100% coverage,
  no warnings, expected failures, or duration outliers.
- The checker preserves parser, staged-inventory, and validator boundaries,
  introduces no DDD-Hexagonal dependency inversion, and contains no mutation
  path.
- Each nonempty check performs one plan read, one parser pass, one staged Git
  inventory, one validator call, and one projection without quadratic work.
- Existing batch commit execution and its root-plan dry-run rejection remain
  unchanged.

### Implementation report for step 2 commit-plan-check (round 1)

The implementation adds `CommitPlanCheckState` and the frozen
`CommitPlanCheckResult`, then composes the public parser, shared staged-path
inventory, and public validator in `check_commit_plan(root)`.

Human and compact JSON renderers project the same immutable result. The CLI
supports discovered or explicit roots and maps ready, expected non-ready, and
operational outcomes to statuses 0, 3, and 2 with the required stream split.
The root launcher delegates to `python -m tools.commit_plan_check` and preserves
the CLI status.

The focused unit suite covers all six states, exact collaborator use, output
schema and ordering, CLI boundaries, module execution, discovery, operational
failures, and launcher delegation.

### Change summary for step 2 commit-plan-check (round 1)

The staged implementation contains exactly these paths:

- `commit-plan-check.bat`
- `tools/commit_plan_check.py`
- `tests/unit/tools/test_commit_plan_check/__init__.py`
- `tests/unit/tools/test_commit_plan_check/test_commit_plan_check_tdd.py`
- `docs/v0.11.0/plan.v0.11.0.commit-plan-check.validation.md`

The validated root `a.commit` contains two ordered groups:

1. `feat(commit-plan-check): expose read-only plan checker` contains the
   production checker, root launcher, and focused tests.
2. `docs(commit-plan-check): record step 2 validation` contains the required
   validation-plan evidence and is the final commit.

`commit-plan-check.bat --format json` reports `state=valid`, `ready=true`, all
five staged paths, both ordered groups, and no diagnostics.

### Writer response for step 2 commit-plan-check (round 1)

Writer response: None for round 1.

There is no earlier reviewer feedback, accepted repair, or disagreement to
report.

### Reviewer focus for step 2 commit-plan-check (round 1)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-2-round-1 -->

## Round 1 by reviewer - Step 2

- Recorded: 2026-08-26T18:53:53+02:00
- Exchange: code/code/v0.11.0/commit-plan-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.commit-plan-check.md
- Implementation step: 2
- Outcome: answer

### Assessed index identity for step 2 commit-plan-check (exchange 1) (round 1)

Baseline index tree: 4d9b89f8a2e497e4d935b3b694511f849c53d55a

Assessed index tree: 4d9b89f8a2e497e4d935b3b694511f849c53d55a

### Implementation check for step 2 commit-plan-check (exchange 1) (round 1)

Result: No. Step 2 has NOT been fully implemented. The service, renderers, and module CLI are correct and well tested, but the shipped root launcher does not satisfy the entry-point parity and root-discovery contract that Step 2 owns, so one of the step's two adapters is wrong.

Almost everything else is right, and I verified it against the code rather than the report.

The settled Q06 parsing boundary is honored exactly. `check_commit_plan(root)` resolves `<root>/a.commit`, returns `missing-plan` when it is absent, reads the file exactly once through `_read_plan`, returns `empty-plan` on empty or whitespace content, then parses with the public `parse_clipboard_content(content, interactive=False)`. The committing workflow's private `_read_and_parse_content` is not imported, so the read-only checker carries no dependency on commit execution and no clipboard fallback.

The failure taxonomy is complete and correctly ordered. Missing, empty, malformed, invalid, empty-staged, and operational outcomes are each reachable and distinct, and `CommitMessageError` is caught separately from the broad operational guard so a malformed plan reports `invalid-plan` at status three rather than an operational failure at status two.

The writer closed a gap the plan did not name. Nonempty content that parses to zero blocks returns `empty-plan` before the inventory call, covered by `test_nonempty_content_without_blocks_is_an_empty_plan`. That ordering matters: `validate_commit_plan([], [])` produces no diagnostics, so reaching the validator with zero blocks and an empty index would have reported a ready plan. The early return forecloses that, and I confirmed the behavior live rather than by reading.

The structured contract matches the design exactly. `structured_payload` emits `schema_version` 1 with `state`, `ready`, `staged_paths`, `groups` carrying `position`, `subject`, and `paths`, and `diagnostics`, with deterministic ordering. `_result_from_validation` checks the empty inventory before validity, so a nonempty plan against an empty index reports `empty-staged-set` as the design's acceptance table requires.

The module CLI status and stream mapping is correct. Operational failures write one stable diagnostic to stderr and return `2`, while ready and expected non-ready results write the complete rendered evidence to stdout and return `0` or `3`, so automation can parse evidence before observing status three.

Architecture, performance, and feature integrity are clean. The checker depends only on the neutral inventory boundary, the public parser, the public validator, and shared root discovery, with no reverse dependency. There is no reset, add, remove, commit, or file write anywhere in the production path, and the only repository access is one plan read and one read-only index query. Each nonempty call performs one read, one parse, one inventory, one validation, and one projection, with no per-path probe and no added sort.

The defect is confined to `commit-plan-check.bat`. Its `pushd` to the launcher directory replaces the caller's working directory, so the launcher and the module report different repositories from the same starting point. That is a Step 2 deliverable failing a Step 2 contract, which is why this check is a No rather than a Yes with an observation. The details, the demonstration, and a verified fix are in the findings.

Validation plan effects: I made no change to the validation plan. Reviewer mode may write only the reviewed step's rows, and I am reporting a No verdict that the writer must reconcile with their own recorded Yes, so editing their rows underneath them would obscure the disagreement rather than resolve it.

The recorded rows state `Yes. Step 2 has been fully implemented.` My independent assessment is `No. Step 2 has NOT been fully implemented.`, because the shipped root launcher does not satisfy the entry-point parity and root-discovery contract that Step 2 owns. When the launcher is fixed, the writer's verdict becomes correct and the rows will need only the evidence corrections below.

Two recorded claims currently overstate what is proven. The focused-verification bullet lists "launcher delegation" among covered behavior, but the only launcher test reads the batch file as text and asserts four substrings, all of which pass against the defective launcher. The file-girth bullet states that the files "remain below their split triggers and the 650-line repository ceiling", which is true, but omits that `tests/unit/tools/test_commit_plan_check/test_commit_plan_check_tdd.py` is 497 lines against the 420-line advisory estimate at `docs/v0.11.0/plan.v0.11.0.commit-plan-check.md:468`. The plan's shared execution checklist item 8 requires that variance to be recorded as evidence.

Under the writer-owned contract, a No verdict also requires a `### Missing work for Step 2` section listing each missing element concretely. That section does not exist, which is consistent with the writer having reached a Yes. The concrete work list is supplied in my writer instructions so it can be transferred directly if the verdict is revised.

The rest of the rows are accurate and should be kept. The typed service, shared orchestration, equivalent evidence, architecture, performance, and coverage sections all match what I found in the code, and the gate evidence line correctly reports the detached full walk.

The document-level status line is correctly `No, it is not implemented.` Steps 3 and 4 still read `Not started`, so no flip was due regardless of this step's verdict.

No umbrella row was completed and reviewer mode correctly suppressed that section. The umbrella digest is unchanged at `020d1d67f9a3dca50a2651e6dd7b6717b3f1a7ef5521c5eaf4a27de6e2c3b79c`, confirmed by `umbrella-digest compare` reporting `changed: false`.

### Pre-repair mandatory checks and coverage for step 2 commit-plan-check (exchange 1) (round 1)

The repository gate is green with real margin, and I forced the walk rather than trusting a cached verdict.

`ghog day --force` reported `ghog full done fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0` with `Objective reached` across 2,039 tests. Correctness, warnings, expected failures, coverage, and duration all pass.

The duration axis is comfortable rather than marginal. The suite's slowest call is `tests/unit/tools/test_commit_plan_check/test_commit_plan_check_tdd.py::test_module_main_and_root_launcher_delegate_to_the_same_cli` at `0.29s` against the `0.50s` floor, which is 42 percent below it. That call is the new subprocess-based test added by this step, and it is well inside budget. The Step 1 lifecycle call that flapped in the previous exchange no longer appears in the slow list at all, so the fixture repair has held across a further round of changes.

`ghog single` on the focused Step 2 test file is green, with nothing still failing in focus and nothing passing in focus while failing in the full suite.

Both `rg` checks pass. The narrowed request form matches, and the wider plan pattern returns 73 lines with all six otherwise-dropped terms present in the production module, evidencing the composed service, `interactive=False` parsing, the format flag, the versioned schema, and the status contract.

`commit-plan-check.bat --format json` returned `state=valid`, `ready=true`, five staged paths, two ordered groups, and zero diagnostics, at status `0`. That result is accurate for this repository, and I used the shipped checker itself as my commit-plan evidence.

The single validation caveat is the one this round is blocking on. That launcher result is correct only because validation ran with the working directory at the llm-shared root. From any other working directory the same command describes llm-shared rather than the caller, which I demonstrated live. So the gate evidence proves the service and the module CLI, and does not yet prove the launcher.

I also ran the repository Markdown gate, which reports no finding for the plan, the validation plan, or either review transcript, so MD024 and MD025 continue to hold.

I performed no repair, so there is no pre-repair versus post-repair difference to report beyond this baseline.

### Resolved validation set and sources for step 2 commit-plan-check (exchange 1) (round 1)

The request resolved three commands. The current plan-derived resolver set adds
two more, so I ran five in total as the union.

- `ghog day` — source `project`. Run as `ghog day --force`, because a plain
  invocation short-circuits to `cov=skipped` when no Python file changed since
  the last green walk and cannot re-prove a recorded result.
- `rg -n CommitPlanCheck tools/commit_plan_check.py commit-plan-check.bat tests/unit/tools/test_commit_plan_check` — source `request`, narrowed relative to the plan.
- `commit-plan-check.bat --format json` — source `request`.
- `rg -n "CommitPlanCheck|check_commit_plan|interactive=False|--format|schema_version|return 3|return 2" tools/commit_plan_check.py commit-plan-check.bat tests/unit/tools/test_commit_plan_check` — source `plan`, at `docs/v0.11.0/plan.v0.11.0.commit-plan-check.md:449`, added by the union.
- `ghog single tests/unit/tools/test_commit_plan_check/test_commit_plan_check_tdd.py` — source `plan`, at `docs/v0.11.0/plan.v0.11.0.commit-plan-check.md:481`, added by the union.

Every command ran and every command passed. Nothing was unavailable, so there
is no missing mandatory evidence on the availability axis.

One passing command carries a caveat that matters. `commit-plan-check.bat
--format json` returned `state=valid`, `ready=true`, five staged paths, two
ordered groups, and no diagnostics, which is correct. It is correct only
because the working directory during validation was the llm-shared root. The
same command from any other working directory reports llm-shared rather than
the caller, so its standing as evidence depends on the launcher fix requested
in this round.

### Resolver drift and direction for step 2 commit-plan-check (exchange 1) (round 1)

Two drifts were found, both narrowing the request relative to the plan, and both are the same pattern I reported and saw corrected during Step 1.

The `rg` command is narrowed. The request carries:

```text
rg -n CommitPlanCheck tools/commit_plan_check.py commit-plan-check.bat tests/unit/tools/test_commit_plan_check
```

The plan's Step 2 completion criteria at `docs/v0.11.0/plan.v0.11.0.commit-plan-check.md:449` specify:

```text
rg -n "CommitPlanCheck|check_commit_plan|interactive=False|--format|schema_version|return 3|return 2" tools/commit_plan_check.py commit-plan-check.bat tests/unit/tools/test_commit_plan_check
```

Direction: the request is a strict subset. It keeps only the type-name term and drops `check_commit_plan`, `interactive=False`, `--format`, `schema_version`, `return 3`, and `return 2`. Those dropped terms are precisely the evidence that the service is composed as settled, that Q06's `interactive=False` parsing is used, that the format flag exists, that the structured schema is versioned, and that the status contract is implemented. The narrowed form would pass on a module that had the right class names and none of that behavior.

The `ghog single` command is missing. The plan's Step 2 timing-run readiness at `docs/v0.11.0/plan.v0.11.0.commit-plan-check.md:481` specifies `ghog single tests/unit/tools/test_commit_plan_check/test_commit_plan_check_tdd.py`, and the resolved set does not contain it.

I ran the union rather than the resolved set alone. The full plan pattern returns 73 matching lines, with all six dropped terms present in the production module, so the composition and status contract are evidenced. `ghog single` on the focused test file is green with nothing failing in focus and no focus-versus-suite interaction.

This is the second consecutive first round in which the resolved set arrives narrower than the plan. It was corrected for Step 1 in round two, and the same correction is due here. The reliable fix is to derive the plan-sourced commands from the plan text rather than re-authoring them per request.

### Repository state around validation for step 2 commit-plan-check (exchange 1) (round 1)

My assessment produced no repository side effect. I made no repair, so the only writes were ignored root `a.*` reviewer evidence files and ignored validation artifacts.

Index identity held throughout. The request-time `request_index_tree` is `4d9b89f8a2e497e4d935b3b694511f849c53d55a`, and `capture-index-tree` returned that identical value both before assessment and after the forced gate walk, the focused run, and every probe. No early rejection applied and no staged change occurred during review.

The umbrella is untouched. `umbrella-digest compare` returns `020d1d67f9a3dca50a2651e6dd7b6717b3f1a7ef5521c5eaf4a27de6e2c3b79c` before and after with `changed: false`.

The validation-state comparison is clean. Using the same ordered five-path set before and after, `validation-state compare` returns `acceptable: true` with empty `tracked_paths`, `untracked_paths`, and `ignored_paths`.

My entry-point probes ran entirely outside the repository. To demonstrate the launcher divergence I created a scratch Git repository under the session scratchpad, outside this working tree, and ran both entry points against it with `PRJ_DIR` cleared. That repository is not inside the project, nothing was written into the project, and the checker itself performed no write in either invocation, which independently exercises the read-only contract.

Ignored validation artifacts were refreshed as expected by the forced walk, including `.coverage`, `.testmondata`, `a.ghog.log`, and `a.ghog.outliers`. The contract accepts differences confined to ignored validation artifacts, and none is tracked or staged.

One tracked path outside the staged set is modified and correctly so. `docs/v0.11.0/review.code.v0.11.0.commit-plan-check.md` carries the appended Step 2 request and is not staged while this round is open, exactly as in the Step 1 exchange. The `git add -A` grouping pass at the commit gate will pick it up.

### Repair inventory for step 2 commit-plan-check (exchange 1) (round 1)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 2 commit-plan-check (exchange 1) (round 1)

`a.commit` is accurate, and I verified it with the checker this step just shipped rather than by reading it. `commit-plan-check.bat --format json` from the repository root returns `state=valid`, `ready=true`, five staged paths, two ordered groups, and zero diagnostics at status `0`.

Group membership matches the staged set exactly:

- Group 1 `feat(commit-plan-check): expose read-only plan checker` carries `commit-plan-check.bat`, `tools/commit_plan_check.py`, and the two focused test paths.
- Group 2 `docs(commit-plan-check): record step 2 validation` carries the validation plan and is the final commit.

Ordering is least to most dependent and correct, since the validation record documents the implementation that precedes it. Both subjects are conventional commits with accurate scopes, and both bodies describe what the diffs actually do.

This plan uses a different authored shape from the Step 1 plan, with `git add -- <path>` lines and unfenced message bodies rather than `## Group N` headings, `git add -A <path>` lines, and fenced blocks. The public parser accepts both, and the shipped checker confirms this one parses into exactly two ordered groups with exact membership, so the difference is presentational rather than a defect. It is worth keeping in mind only because the two shapes now coexist in this effort's history.

I did not amend `a.commit`. Membership, ordering, scope, and subjects are all accurate, so an amendment would have been a substantive change to commit grouping with no defect to correct.

One consequence of the launcher finding reaches this assessment honestly. The command I used as commit-plan evidence produced a correct answer only because my working directory was the llm-shared root. That does not weaken the conclusion for this repository, since the module entry point and my own validator run agree with it, but it does mean the same command is not yet trustworthy as the shared readiness floor Step 4 intends it to be.

### Findings and boundaries for step 2 commit-plan-check (exchange 1) (round 1)

Unresolved findings:

- The root launcher discards the caller's working directory, so the two shipped entry points disagree about which repository they check. `commit-plan-check.bat` runs `pushd "%COMMIT_PLAN_CHECK_ROOT%"` before `python -m tools.commit_plan_check`, which makes `find_project_root(Path.cwd())` resolve to the llm-shared repository rather than the caller's. I demonstrated the divergence directly, from one working directory in a scratch repository with `PRJ_DIR` cleared so environment precedence could not mask it: the module entry point returned `{"state":"empty-plan","ready":false}` with status `3`, describing that repository correctly, while the launcher returned `{"state":"valid","ready":true}` with status `0`, describing llm-shared instead.
- This breaks three settled contracts. The plan's Step 2 expected outcome requires that "Both entry points emit identical ordered evidence without changing Git or repository files". The design's first acceptance row requires that a valid root plan makes "Both entry points report identical ordered groups and return `0`". Design Q07 settles root resolution as "Discover the root from the current directory by default and accept optional `--root <path>`", and the `pushd` removes that default.
- The consequence is a false green on a readiness gate, which is the most damaging way this feature can fail. Step 4 will place `commit-plan-check.bat` in the code reviewer's readiness floor and in `group-commits-msg` before commit grouping. llm-shared is a shared tooling repository consumed by other projects through `LLM_SHARED_DIR`, so a reviewer or grouping run whose working directory sits in a consuming project would receive `ready=true` and status `0` describing llm-shared's plan while the caller's own `a.commit` is missing, empty, or mismatched.
- A fix is available and I verified it works before recommending it. Replacing the `pushd` with a `PYTHONPATH` entry that points at the launcher directory keeps the caller's working directory intact: running the module with `PYTHONPATH` set to the llm-shared root and the working directory left in the scratch repository returned `{"state":"empty-plan","ready":false}` with status `3`, exactly matching the module entry point. The `--root` passthrough already works and returned the same correct result, so it remains a usable workaround but cannot substitute for a correct default.
- The launcher delegation test cannot detect this class of defect because it never executes the launcher. `test_module_main_and_root_launcher_delegate_to_the_same_cli` reads `commit-plan-check.bat` as text and asserts that it contains `-m tools.commit_plan_check`, `%ERRORLEVEL%`, `exit /b 2`, and `exit /b`. Every one of those assertions passes against the current defective launcher. Its module half runs only `--help` with `cwd=root`, so it exercises neither discovery nor parity. Step 2's own test list claims "root-launcher delegation" coverage and the validation plan repeats that claim, but what is proven is file content rather than behavior.
- The Step 2 test file exceeds its advisory line estimate without the variance being recorded. `tests/unit/tools/test_commit_plan_check/test_commit_plan_check_tdd.py` measures 497 physical lines against the plan's advisory estimate of 420 at `docs/v0.11.0/plan.v0.11.0.commit-plan-check.md:468`. That is not a failure, since the file stays below the 550 risk band and the 650 ceiling, but the plan's shared execution checklist item 8 requires that a file exceeding only an advisory estimate has "the variance recorded as evidence". The validation plan states that the files "remain below their split triggers and the 650-line repository ceiling" without acknowledging the overrun.

Boundary-crossing work:

- Fixing the launcher is inside Step 2 rather than across a boundary, since `commit-plan-check.bat` is named by the step and is already staged. I did not repair it anyway, and the reason is scope quality rather than ownership: the correct fix pairs a launcher change with a replacement test that executes both entry points against one temporary repository, and that test is the evidence the step is missing. Writing the fix without its test would hand back a change whose only proof is my prose, and writing both would be a substantive repair that cannot validly finish this round in any case.
- The mechanism also carries a small decision the writer should own. Preserving the caller's working directory can be done by prepending the launcher directory to `PYTHONPATH`, which I verified works, or by capturing `%CD%` before the `pushd` and injecting it as `--root` only when the caller did not pass one. I recommend the first as simpler and side-effect-free, but choosing between them is a design call at the adapter boundary rather than an unambiguous repair.
- The label-inlining renderer defect carried over from the Step 1 exchange is still present and still deferred by agreement. It affects `tools/spec_review_answer.py`, `tools/spec_review_request.py`, `tools/code_review_request.py`, and `tools/code_review_answer.py`, and the correct idiom already exists at `tools/code_review_answer.py:288`. It remains outside Step 2, and `tools/code_review_request.py` is a Step 3 file, so repairing it here would still collide with Step 3. It is recorded in the Step 1 commit history as agreed.
- The unimplemented caller-authored heading shift contract in `instructions/review-requestor.md` is likewise unchanged and deferred with the same tooling work.
- The repeated narrowing of plan-sourced validation commands between the plan text and the resolved set is a requestor-side concern rather than implementation work. I report it with its direction and ran the union; I did not alter the resolved set, which belongs to the requestor.

### Writer instructions for step 2 commit-plan-check (exchange 1) (round 1)

The service, renderers, module CLI, and test matrix are good work and need no rework. The requested changes are confined to the launcher, one test, and two recorded claims.

Fix the launcher so it stops discarding the caller's working directory. In `commit-plan-check.bat`, the `pushd "%COMMIT_PLAN_CHECK_ROOT%"` and matching `popd` exist so `python -m tools.commit_plan_check` can resolve the `tools` package, but they also destroy the cwd that Q07 makes the default root. Prepend the launcher directory to `PYTHONPATH` instead and drop the `pushd` and `popd` pair, keeping the `%ERRORLEVEL%` capture and `exit /b` passthrough exactly as they are. I verified this before recommending it: with the working directory left in a scratch repository and `PYTHONPATH` pointing at the llm-shared root, the module returned `{"state":"empty-plan","ready":false}` and status `3`, identical to the module entry point run the same way, where the current launcher returned `{"state":"valid","ready":true}` and status `0`.

Do not copy `markdown-check.bat` here. That launcher uses the same `pushd`, and for it the behavior is harmless because scanning llm-shared's own tree is its purpose. Step 2's checker is the opposite case: its subject is whichever repository the caller is standing in, so the pattern must diverge deliberately. It is worth a short comment in the launcher saying why, so a later reader does not "restore consistency" with the other root launcher.

Replace the text-matching launcher test with one that executes the launcher. `test_module_main_and_root_launcher_delegate_to_the_same_cli` currently reads `commit-plan-check.bat` and asserts it contains `-m tools.commit_plan_check`, `%ERRORLEVEL%`, `exit /b 2`, and `exit /b`. All four assertions pass against the defective launcher, so the test cannot fail for the reason it exists. Make it run both entry points from one temporary Git repository with its own `a.commit` and assert that the JSON payloads and the exit statuses are identical. Guard it for Windows if needed, since the launcher is a batch file. Step 4 already plans real-repository parity acceptance, so if you prefer to keep the unit test lightweight, say explicitly in the Step 2 evidence that launcher parity is proven in Step 4 rather than claiming it here.

Correct two claims that currently overstate what is proven. The Step 2 focused-verification bullet in the validation plan lists "launcher delegation" among covered behavior; until the test above exists, that reads as behavioral coverage which does not exist. Also record the line-budget variance: `tests/unit/tools/test_commit_plan_check/test_commit_plan_check_tdd.py` is 497 lines against the 420-line advisory estimate at `docs/v0.11.0/plan.v0.11.0.commit-plan-check.md:468`. The file is comfortably below the 550 risk band and the 650 ceiling, so nothing needs splitting, but the plan's shared execution checklist item 8 requires the variance to be recorded as evidence rather than passed over. The current wording only states that the files remain below their split triggers and the ceiling.

Re-run the evidence after the launcher change. `commit-plan-check.bat --format json` is in the resolved validation set and currently produces a correct result only because the working directory happens to be the llm-shared root, so its value as evidence depends on the fix.

Two things deliberately need no change. The `a.commit` plan is accurate as it stands, with two ordered groups, exact membership, and conventional subjects, and I confirmed it with the shipped checker itself. The zero-block early return you added ahead of the inventory call is not in the plan text but is correct and worth keeping, because reaching the validator with zero blocks and an empty index would otherwise report a ready plan.

### Decision rationale for step 2 commit-plan-check (exchange 1) (round 1)

I am publishing `changes-requested`, and I made no repair, so nothing here prevents a commit-ready recommendation in the next round.

This is a disagreement about one deliverable, not about the step's quality. The requestor assessed Step 2 as fully implemented, and most of it plainly is: the typed result, the six-state taxonomy, the Q06 parsing boundary, the versioned structured schema, the status and stream contract, the architecture direction, and a genuinely strong 21-case test matrix all hold up under independent checking. The writer also closed a gap the plan never named, returning `empty-plan` for nonempty content that parses to zero blocks, which forecloses a real hole where `validate_commit_plan([], [])` would otherwise have reported a ready plan.

The blocking reason is that one of Step 2's two shipped entry points is wrong. `commit-plan-check.bat` runs `pushd` to its own directory before invoking the module, which replaces the caller's working directory and defeats the root discovery that design Q07 settles as the default. I did not infer this from reading the batch file. I built a scratch repository outside the project, cleared `PRJ_DIR` so environment precedence could not mask the behavior, and ran both entry points from the same working directory: the module returned `empty-plan` at status `3`, describing that repository, while the launcher returned `valid` with `ready=true` at status `0`, describing llm-shared. That directly contradicts the plan's Step 2 outcome that both entry points emit identical evidence and the design's first acceptance row requiring both to report identical groups.

The consequence is what makes it blocking rather than a note. Step 4 will place this exact launcher in the code reviewer's readiness floor and in `group-commits-msg` ahead of commit grouping. llm-shared is consumed by other projects through `LLM_SHARED_DIR`, so a run whose working directory sits in a consuming project would return `ready=true` and status `0` for llm-shared's plan while the caller's own `a.commit` is missing, empty, or mismatched. A readiness gate that reports a false green is the worst available failure mode for this feature, and it would be inherited by Steps 3 and 4 rather than caught there.

The existing test cannot catch it, which is why the green gate is not reassurance here. `test_module_main_and_root_launcher_delegate_to_the_same_cli` reads the batch file as text and asserts four substrings that all appear in the defective launcher, and its module half runs only `--help` with the working directory already set to the root. The full walk is genuinely green at `cov=100 outliers=0 exit=0` across 2,039 tests with comfortable duration margin, and it still proves nothing about launcher parity.

I did not repair it, and I want the reason on the record. The launcher is in scope, so ownership was not the obstacle. The fix belongs with a test that executes both entry points against one temporary repository, and that test is precisely the missing evidence; shipping the change without it would leave my prose as its only proof. The mechanism is also a small adapter-boundary decision between a `PYTHONPATH` entry and injecting `--root` from a captured `%CD%`. I verified the `PYTHONPATH` approach produces output identical to the module from a foreign working directory, so the recommendation is grounded rather than speculative, but the choice is the writer's.

Two smaller items ride along. The resolved validation set again arrived narrower than the plan, dropping five terms from the `rg` pattern and omitting `ghog single` entirely; I ran the union and both additions pass. The Step 2 test file is 497 lines against a 420-line advisory, which needs no split but does need its variance recorded under the plan's own checklist item 8.

This assessment is advisory and authorizes nothing. Only the human may choose `Commit` or `Rework and review again`.

### Final reviewer decision for step 2 commit-plan-check (exchange 1) (round 1)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-2-round-1 -->

## Round 2 by requestor - Step 2

- Recorded: 2026-08-26T19:27:32+02:00
- Exchange: code/code/v0.11.0/commit-plan-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.commit-plan-check.md
- Implementation step: 2
- Outcome: request

### Review identity for step 2 commit-plan-check (round 2)

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: docs/v0.11.0/plan.v0.11.0.commit-plan-check.md
Implementation step: 2
Review round: 2

### Code review evidence for step 2 commit-plan-check (round 2)

request_index_tree: b99b838d31fa916c508eb3e3720f014fc5abf283
resolved_validation_set:

- ghog day (sources: project)
- rg -n --regexp CommitPlanCheck --regexp check_commit_plan --regexp interactive=False --regexp=--format --regexp schema_version --regexp return\s+3 --regexp return\s+2 tools/commit_plan_check.py commit-plan-check.bat tests/unit/tools/test_commit_plan_check (sources: plan)
- ghog single tests/unit/tools/test_commit_plan_check/test_commit_plan_check_tdd.py (sources: plan)
- commit-plan-check.bat --format json (sources: request)

### Requestor assessment for step 2 commit-plan-check (round 2)

Step 2 is fully implemented after the round-1 corrections.

- The batch launcher now preserves the caller's working directory and exposes
  llm-shared imports through `PYTHONPATH`, so default root discovery and
  `--root` remain module-equivalent.
- A real Windows parity test runs both entry points from the same temporary Git
  repository with `PRJ_DIR` cleared and asserts identical status and JSON.
- The final detached Groundhog day passes all 2,039 tests at 100% coverage,
  with no warnings, expected failures, or duration outliers.
- Static, architecture, performance, mutation, and feature-integrity evidence
  remains green.

### Implementation report for step 2 commit-plan-check (round 2)

Round 2 preserves the complete checker service and changes only the adapter
boundary and its evidence.

`commit-plan-check.bat` no longer changes directories. It prepends its own root
to `PYTHONPATH`, invokes the same module from the caller's cwd, captures the
module status, and returns it unchanged.

Executable adapter coverage moved into a dedicated test leaf. Its parity test
creates one real repository, runs the module and batch launcher from that
foreign cwd, and compares their statuses and structured results. Real process
setup is module-scoped so the measured assertion call remains below the suite
duration floor without dropping any assertion.

The validation plan now records executable parity and the focused service
test's 33-line advisory variance.

### Change summary for step 2 commit-plan-check (round 2)

The reviewed index contains exactly six staged paths:

- `commit-plan-check.bat`
- `tools/commit_plan_check.py`
- `tests/unit/tools/test_commit_plan_check/__init__.py`
- `tests/unit/tools/test_commit_plan_check/test_commit_plan_check_tdd.py`
- `tests/unit/tools/test_commit_plan_check/test_commit_plan_check_adapter_tdd.py`
- `docs/v0.11.0/plan.v0.11.0.commit-plan-check.validation.md`

The amended and validated root `a.commit` still contains two ordered groups.
The implementation group now includes the split adapter test; the final group
remains `docs(commit-plan-check): record step 2 validation`.

The live checker reports `state=valid`, `ready=true`, all six staged paths,
both ordered groups, and no diagnostics.

### Writer response for step 2 commit-plan-check (round 2)

Writer response: Accepted all round-1 findings with no disagreement.

- Replaced launcher `pushd` and `popd` with caller-cwd-preserving `PYTHONPATH`
  setup.
- Replaced text-only launcher assertions with executable module-to-batch parity
  from a foreign temporary repository.
- Split adapter coverage into a dedicated test leaf before approaching the
  550-line risk threshold.
- Recorded the 453-line service test's 33-line advisory variance and corrected
  the launcher-coverage claim.
- Re-ran both focused tests, the complete Groundhog day, and the amended
  commit-plan check successfully.

### Reviewer focus for step 2 commit-plan-check (round 2)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-2-round-2 -->

## Round 2 by reviewer - Step 2

- Recorded: 2026-08-26T19:35:54+02:00
- Exchange: code/code/v0.11.0/commit-plan-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.commit-plan-check.md
- Implementation step: 2
- Outcome: answer

### Assessed index identity for step 2 commit-plan-check (exchange 1) (round 2)

Baseline index tree: b99b838d31fa916c508eb3e3720f014fc5abf283

Assessed index tree: b99b838d31fa916c508eb3e3720f014fc5abf283

### Implementation check for step 2 commit-plan-check (exchange 1) (round 2)

Result: Yes. Step 2 has been fully implemented. This reverses my round-one No, and the reversal rests on my own re-execution of the failing scenario rather than on the change summary.

The launcher defect is genuinely fixed. `commit-plan-check.bat` no longer changes directory; it prepends its own root to `PYTHONPATH`, preserving an existing value when one is set, and invokes the same module from the caller's working directory while still capturing and returning the module status. The file carries a comment stating why it must differ from the other root launcher, which is what stops a later reader from "restoring consistency" with `markdown-check.bat`.

I re-ran the exact scenario that failed in round one. From a scratch repository outside this project, with `PRJ_DIR` cleared so environment precedence could not mask the result, both entry points now agree on every path I exercised. On a plan with no groups, both returned `{"state":"empty-plan","ready":false}` at status `3`. On an unparseable plan, both returned identical `invalid-plan` evidence at status `3`. On a valid plan with matching staged membership, both returned `{"state":"valid","ready":true}` with the same single group and staged path at status `0`. In round one the same ready comparison produced `empty-plan` at status `3` from the module and `valid` at status `0` from the launcher, so the design's first acceptance row is now satisfied where it previously failed.

I also confirmed the stream contract holds under a noisy path, which I had not tested before. When the parser rejects a plan it writes its own explanatory prose, and that prose goes to stderr: stdout carried nothing but the JSON object and parsed cleanly. Automation can therefore read structured evidence before observing status three, as the design requires.

The replacement test is real coverage rather than restated intent. `test_module_and_root_launcher_check_the_same_caller_repository` builds a real Git repository with a staged file and a matching plan, clears `PRJ_DIR`, exposes imports through `PYTHONPATH` without overriding root discovery, runs both adapters from that foreign working directory, and asserts equal return codes, equal empty stderr, and equal parsed JSON. It would have failed against the round-one launcher, because the two payloads would have described different repositories. That is the property the old text-matching test could not express.

The extraction into a second file in the same leaf follows the plan's own split guidance and the repository's convention, where leaves such as `tests/unit/tools/test_review_exchange_lifecycle/` already hold several test files. Module-scoped process setup keeps the subprocess cost outside the measured call without dropping an assertion, and `tmp_path_factory` supports that scope, so unlike the Step 1 case a broader scope was available and was used.

The service itself is unchanged and still correct. `tools/commit_plan_check.py` remains at 247 lines with the same Q06 parsing boundary, the same six-state taxonomy and ordering, the same versioned structured schema, and the same status and stream mapping I accepted in round one.

Every budget holds. The checker is 247 lines against a 360 advisory, the launcher 27 against 35, the package marker 2 against 5, the focused service test 453 against a 420 advisory, and the new adapter leaf 131 lines. Nothing reaches the 550 risk band or the 650 ceiling.

Architecture, performance, and feature integrity are unchanged and clean. The dependency direction still runs one way, the production path still contains no reset, add, remove, commit, or file write, and each nonempty call still performs one read, one parse, one inventory, one validation, and one projection.

Validation plan effects: I made no change to the validation plan. The requestor's rows are now correct, and my verdict agrees with theirs, so reviewer mode had nothing to write.

The round-one disagreement is resolved. Their rows record `Yes. Step 2 has been fully implemented.` and my independent assessment now reaches the same verdict, because the launcher defect that made it a No is fixed and verified. No `### Missing work for Step 2` section is required, and none is present.

Both overstated claims are corrected. The focused-verification bullet now describes "executable module-to-launcher parity from a foreign Git repository" rather than generic launcher delegation, which matches what the new adapter test actually proves. The file-girth bullet now records the variance explicitly, stating that the focused service test at 453 lines exceeds its 420-line advisory estimate by 33 lines and that the recorded variance remains below the split trigger and the ceiling. That satisfies the plan's shared execution checklist item 8, which requires the variance to be recorded rather than passed over.

The remaining rows are accurate against the code. The launcher line count is recorded as 27 and measures 27, the checker as 247 and measures 247, and the evidence-parity row correctly states that expected non-readiness emits complete evidence on stdout, which I verified independently including under parser rejection.

The document-level status line is correctly `No, it is not implemented.` Steps 3 and 4 still read `Not started`, so no flip was due.

No umbrella row was completed and reviewer mode correctly suppressed that section. The umbrella digest is unchanged at `020d1d67f9a3dca50a2651e6dd7b6717b3f1a7ef5521c5eaf4a27de6e2c3b79c`, confirmed by `umbrella-digest compare` reporting `changed: false`.

### Pre-repair mandatory checks and coverage for step 2 commit-plan-check (exchange 1) (round 2)

The repository gate is green with comfortable margin, and I forced the walk rather than accepting a cached verdict.

`ghog day --force` reported `ghog full done fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0` with `Objective reached` across 2,039 tests.

The duration axis is healthy. The slowest call is `tests/unit/tools/test_review_exchange_recovery_acceptance/test_review_exchange_recovery_acceptance_tdd.py::test_abandoned_request_is_reclaimed_by_a_fresh_session` at `0.28s` against the `0.50s` floor, which is 44 percent below it. The new adapter parity test does not appear in the slow list at all, so its module-scoped subprocess setup succeeded in keeping real process cost out of the measured call. The Step 1 lifecycle call that flapped two exchanges ago is likewise absent.

The suite count is unchanged at 2,039, which is consistent rather than suspicious. The text-only delegation test was replaced by the executable parity test and the module-guard test was moved to the new leaf, so the net change is zero.

`ghog single` on the focused service test is green.

Both `rg` forms pass and are equivalent, each returning 75 lines, and all six terms the round-one command dropped are present in the production module.

`commit-plan-check.bat --format json` returns `state=valid`, `ready=true`, six staged paths, two ordered groups, and zero diagnostics at status `0`.

The round-one caveat on that last command is now discharged. Its result no longer depends on the working directory, because I confirmed from a scratch repository outside the project, with `PRJ_DIR` cleared, that the launcher and the module produce identical JSON and identical status on the empty-plan, invalid-plan, and valid paths. I also confirmed that parser prose goes to stderr and stdout carries only parseable JSON.

The repository Markdown gate reports no finding for the plan, the validation plan, or either review transcript, so MD024 and MD025 continue to hold.

I performed no repair, so there is no pre-repair versus post-repair difference beyond this baseline.

### Resolved validation set and sources for step 2 commit-plan-check (exchange 1) (round 2)

The request resolved four commands and I ran all four. The current plan-derived
resolver set adds nothing this round, so the union equals the resolved set.

- `ghog day` — source `project`. Run as `ghog day --force`, because a plain
  invocation short-circuits to `cov=skipped` and cannot re-prove a result.
- `rg -n --regexp CommitPlanCheck --regexp check_commit_plan --regexp interactive=False --regexp=--format --regexp schema_version --regexp return\s+3 --regexp return\s+2 tools/commit_plan_check.py commit-plan-check.bat tests/unit/tools/test_commit_plan_check` — source `plan`, now carrying every parity term.
- `ghog single tests/unit/tools/test_commit_plan_check/test_commit_plan_check_tdd.py` — source `plan`, restored this round.
- `commit-plan-check.bat --format json` — source `request`.

Every command ran and every command passed.

The `rg` command is now equivalent to the plan's canonical alternation at
`docs/v0.11.0/plan.v0.11.0.commit-plan-check.md:449`. I ran both forms and each
returns exactly 75 matching lines, so the `--regexp` spelling with `return\s+3`
and `return\s+2` loses no coverage. All six previously dropped terms are present
in the production module.

`ghog single` on the focused service test is green, with nothing failing in
focus and no focus-versus-suite interaction.

`commit-plan-check.bat --format json` reports `state=valid`, `ready=true`, six
staged paths, two ordered groups, and no diagnostics at status `0`. Unlike round
one this result no longer depends on the working directory being the llm-shared
root, since I verified the same command agrees with the module entry point from
a foreign repository.

### Resolver drift and direction for step 2 commit-plan-check (exchange 1) (round 2)

No drift this round. Both round-one drifts are corrected.

The `rg` command now carries every parity term. The resolved form uses explicit
`--regexp` flags with `return\s+3` and `return\s+2` where the plan at
`docs/v0.11.0/plan.v0.11.0.commit-plan-check.md:449` uses a quoted alternation
with `return 3` and `return 2`. I ran both forms rather than assuming
equivalence, and each returns exactly 75 matching lines over the same three
paths, so the spelling difference costs no coverage. As in Step 1, the
`--regexp` form is the safer command line, because `--regexp=--format` cannot be
mistaken for an option the way a bare `--format` alternative inside a quoted
pattern can.

`ghog single tests/unit/tools/test_commit_plan_check/test_commit_plan_check_tdd.py`
is restored to the resolved set from the `plan` source, matching
`docs/v0.11.0/plan.v0.11.0.commit-plan-check.md:481`.

Comparing the round-two request set against the current plan-derived resolver
set, the union adds nothing, so I ran the resolved set as given.

One process note rather than a finding. This is the second effort in which the
first round arrived narrower than the plan and the second round corrected it.
Deriving the plan-sourced commands from the plan text, rather than re-authoring
them per request, would remove the class rather than the instance.

### Repository state around validation for step 2 commit-plan-check (exchange 1) (round 2)

My assessment produced no repository side effect. I made no repair, so the only writes were ignored root `a.*` reviewer evidence files and ignored validation artifacts.

Index identity held throughout. The request-time `request_index_tree` is `b99b838d31fa916c508eb3e3720f014fc5abf283`, and `capture-index-tree` returned that identical value both before assessment and after the forced gate walk, the focused run, the Markdown gate, and every entry-point probe. No early rejection applied and no staged change occurred during review.

The umbrella is untouched. `umbrella-digest compare` returns `020d1d67f9a3dca50a2651e6dd7b6717b3f1a7ef5521c5eaf4a27de6e2c3b79c` before and after with `changed: false`.

The validation-state comparison is clean. Using the same ordered six-path set before and after, `validation-state compare` returns `acceptable: true` with empty `tracked_paths`, `untracked_paths`, and `ignored_paths`.

My parity probes ran entirely outside the repository. I created a scratch Git repository under the session scratchpad, exercised the empty-plan, invalid-plan, and valid paths through both entry points with `PRJ_DIR` cleared, and removed it afterwards. Nothing was written into this project, and the checker performed no write in any invocation, which independently exercises the read-only contract from a second direction.

Ignored validation artifacts were refreshed as expected by the forced walk, including `.coverage`, `.testmondata`, `a.ghog.log`, and `a.ghog.outliers`. The contract accepts differences confined to ignored validation artifacts, and none is tracked or staged.

One tracked path outside the staged set is modified and correctly so. `docs/v0.11.0/review.code.v0.11.0.commit-plan-check.md` carries the appended Step 2 rounds and is not staged while this round is open.

### Repair inventory for step 2 commit-plan-check (exchange 1) (round 2)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 2 commit-plan-check (exchange 1) (round 2)

`a.commit` is accurate after its amendment, and I verified it with the checker this step ships rather than by reading it. `commit-plan-check.bat --format json` returns `state=valid`, `ready=true`, six staged paths, two ordered groups, and zero diagnostics at status `0`.

The amendment is correct and minimal. Group 1 `feat(commit-plan-check): expose read-only plan checker` now also carries `tests/unit/tools/test_commit_plan_check/test_commit_plan_check_adapter_tdd.py` alongside the launcher, the checker module, the package marker, and the focused service test. Group 2 `docs(commit-plan-check): record step 2 validation` still carries the validation plan alone and remains the final commit.

Membership matches the index exactly, with all six staged paths planned and no planned path absent. Ordering is least to most dependent, since the validation record documents the implementation that precedes it. Both subjects are conventional commits with accurate scopes, and both bodies describe what the diffs actually do.

Placing the new adapter test in the implementation group rather than a separate one is the right call. It is part of the same deliverable and would not stand alone as a coherent commit.

I did not amend `a.commit`. Membership, ordering, scope, and subjects are all accurate, so an amendment would have been a substantive change to commit grouping with no defect to correct, and it would have invalidated a commit-ready recommendation in this same round.

Unlike round one, my commit-plan evidence no longer carries a working-directory caveat. The command I used is now trustworthy from any directory, which I confirmed against a scratch repository, so the same command can serve as the shared readiness floor Step 4 intends.

One carry-forward for the commit gate, unchanged in shape from the Step 1 exchange and needing no action now. `docs/v0.11.0/review.code.v0.11.0.commit-plan-check.md` is tracked, carries this exchange's appended rounds, and is deliberately unstaged while the round is open. The `git add -A` grouping pass at the commit gate will pick it up.

### Findings and boundaries for step 2 commit-plan-check (exchange 1) (round 2)

Unresolved findings: None.

Boundary-crossing work: None.

### Writer instructions for step 2 commit-plan-check (exchange 1) (round 2)

No change is required. Every round-one item is addressed and I am requesting nothing further.

Do not rework Step 2. The launcher fix, the executable parity test, the test-leaf split, and both evidence corrections are all correct as they stand.

Two things are worth keeping deliberately, so a later cleanup does not undo them. The comment in `commit-plan-check.bat` explaining why it preserves the caller's directory should stay, because the original defect came from copying `markdown-check.bat`, and without that note the `pushd` is likely to be restored in the name of consistency. The module scope on the adapter fixture should also stay, since it is what keeps real subprocess cost out of the measured call and off the duration floor.

Two items remain deferred by agreement rather than dropped, and should reach the pending review-mode requirements rather than being lost. The first is the label-inlining defect in `tools/spec_review_answer.py`, `tools/spec_review_request.py`, `tools/code_review_request.py`, and `tools/code_review_answer.py`, where the correct idiom already exists at `tools/code_review_answer.py:288`; sequence it after Step 3, which modifies `tools/code_review_request.py`. The second is the unimplemented caller-authored heading shift and qualification contract in `instructions/review-requestor.md`.

One process note for Step 3, offered rather than requested. Both first rounds in this effort arrived with a plan-sourced validation command narrower than the plan text, and both were corrected in round two. Deriving those commands from the plan rather than re-authoring them per request would remove the pattern.

At the commit gate, remember that the `git add -A` grouping pass will pick up `docs/v0.11.0/review.code.v0.11.0.commit-plan-check.md`, which carries this exchange's rounds and is deliberately unstaged while the round is open.

If the human selects `Commit`, run the existing commit step. If the human selects `Rework and review again`, there is no outstanding scope from me; treat any human guidance as the full scope of that round.

### Decision rationale for step 2 commit-plan-check (exchange 1) (round 2)

I am recommending `commit-ready`, and I made no repair in either round, so nothing in this exchange invalidates the recommendation.

All six readiness-floor results pass. Identity is exact, with the envelope, human-readable identity, plan, step, round, and exchange occurrence in agreement and the request-time index tree `b99b838d31fa916c508eb3e3720f014fc5abf283` matching the live index before and after all validation. Implementation completeness is now a Yes, reversing my round-one No. Mandatory validation and coverage pass with margin. Staged attribution is clean across six paths. No unresolved finding remains against this step. The `a.commit` grouping is valid with zero diagnostics.

The reversal is earned by re-execution, not by the change summary. I rebuilt the failing scenario from round one: a scratch repository outside this project, `PRJ_DIR` cleared so environment precedence could not mask the result, both entry points invoked from that foreign working directory. Where round one produced `empty-plan` at status `3` from the module against `valid` with `ready=true` at status `0` from the launcher, the two now agree byte for byte on the empty-plan path, the invalid-plan path, and the valid path, statuses included. The design's first acceptance row, which round one failed, now holds.

The fix is also the right shape rather than merely effective. The launcher preserves the caller's working directory by extending `PYTHONPATH` instead of changing directory, preserves an existing `PYTHONPATH` when present, still captures and returns the module status, and carries a comment explaining why it must diverge from `markdown-check.bat`. That comment matters more than it looks, because the defect originated in copying that pattern.

The replacement test can now fail for the reason it exists. The old assertion read the batch file as text and passed against the defective launcher. The new one builds a real repository, runs both adapters from a foreign working directory, and compares statuses, stderr, and parsed JSON, so it would have caught the original divergence. Module-scoped setup keeps the real process cost outside the measured call, and the gate confirms it: the parity test does not appear in the slow list, and the suite's slowest call sits 44 percent below the floor.

Two smaller round-one items are also closed. The advisory variance is now recorded explicitly at 453 against 420 lines, satisfying the plan's checklist item 8, and the launcher-coverage claim now says what the test actually proves. The resolved validation set carries every parity term and the restored `ghog single`; I ran both `rg` spellings and confirmed they return identical counts rather than assuming equivalence.

I checked one thing this round that I had not tested before, because a fix can shift a stream contract. When the parser rejects a plan it writes explanatory prose, and that prose goes to stderr: stdout carried only the JSON object and parsed cleanly. Automation can read structured evidence before observing status three, as the design requires.

One item remains deferred by agreement and the human should see it at this gate. The label-inlining defect in `tools/spec_review_answer.py`, `tools/spec_review_request.py`, `tools/code_review_request.py`, and `tools/code_review_answer.py` is unchanged, with the correct idiom already present at `tools/code_review_answer.py:288`, and the unimplemented caller-authored heading contract in `instructions/review-requestor.md` travels with it. Neither is caused by Step 2, neither touches Step 2 code, and `tools/code_review_request.py` belongs to Step 3, so repairing either here would cross the boundary and collide with planned work. Both are recorded in the Step 1 commit history. I classify them as tracked future work for the pending review-mode requirements rather than unresolved findings against Step 2, and I would not block this commit on them.

This recommendation is advisory and authorizes nothing. A green gate, a valid commit plan, and verified entry-point parity are mechanical evidence only. Only the human may choose `Commit` or `Rework and review again`.

### Final reviewer decision for step 2 commit-plan-check (exchange 1) (round 2)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-2-round-2 -->

## Round 2 by human - Step 2 - human-confirmation

- Recorded: 2026-08-26T20:06:06+02:00
- Exchange: code/code/v0.11.0/commit-plan-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.commit-plan-check.md
- Implementation step: 2
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-2 -->
