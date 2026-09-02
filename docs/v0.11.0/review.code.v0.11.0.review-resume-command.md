# Code review transcript for v0.11.0

- Exchange: code/code/v0.11.0/review-resume-command
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-resume-command.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor - Step 0

- Recorded: 2026-09-01T20:51:27+02:00
- Exchange: code/code/v0.11.0/review-resume-command
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-resume-command.md
- Implementation step: 0
- Outcome: request

### Review identity for step 0 review-resume-command (round 1)

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: docs/v0.11.0/plan.v0.11.0.review-resume-command.md
Implementation step: 0
Review round: 1

### Code review evidence for step 0 review-resume-command (round 1)

request_index_tree: fc3792b2226b86aec05a004722a394cc7e6ba245
resolved_validation_set:

- ghog day (sources: project)
- ghog single tests/unit/tools/test_review_resume_perf/test_review_resume_perf_tdd.py (sources: plan)
- rg -n -e xfail -e timeout -e migration -e notification -e poll tests/unit/tools/test_review_resume_perf (sources: plan)
- commit-plan-check.bat --format json (sources: request)

commit_plan_result:

```text
state: valid
ready: true
group 1: chore(vscode): recognize prevalidated
group 1 path: .vscode/settings.json
group 2: docs(review): qualify repeated exchange headings
group 2 path: docs/v0.11.0/review.feature-request.v0.11.0.review-resume-command.md
group 2 path: docs/v0.11.0/review.plan.v0.11.0.code-reviewer.md
group 3: test(review-resume): add performance guardrails
group 3 path: tests/unit/tools/test_review_resume_perf/__init__.py
group 3 path: tests/unit/tools/test_review_resume_perf/test_review_resume_perf_tdd.py
group 3 path: tests/acceptance/review_status/test_review_status_acceptance/test_review_status_acceptance_tdd.py
group 4: docs(review-resume-command): record step 0 validation
group 4 path: docs/v0.11.0/plan.v0.11.0.review-resume-command.validation.md
staged path: .vscode/settings.json
staged path: docs/v0.11.0/plan.v0.11.0.review-resume-command.validation.md
staged path: docs/v0.11.0/review.feature-request.v0.11.0.review-resume-command.md
staged path: docs/v0.11.0/review.plan.v0.11.0.code-reviewer.md
staged path: tests/acceptance/review_status/test_review_status_acceptance/test_review_status_acceptance_tdd.py
staged path: tests/unit/tools/test_review_resume_perf/__init__.py
staged path: tests/unit/tools/test_review_resume_perf/test_review_resume_perf_tdd.py
```

### Requestor assessment for step 0 review-resume-command (round 1)

Step 0 is fully implemented. The staged unit package defines three strict
Step 1 migration xfails and three strict Step 5 global-wait xfails, each with a
one-second timeout, deterministic spies, call-count assertions, and elapsed
bounds. The contracts cover exactly three flat placement reads, linear
candidate parsing, zero status projection, bounded quiet waits, notification
hints followed by authoritative rescans, and polling fallback.

No production domain or adapter dependency changes in Step 0. The test seams
express future filesystem, status, notification, poll, and monotonic-clock ports
explicitly, with linear candidate work and constant work per wait interval.

The final Groundhog day walk completed with 2,219 tests, `fail=0`, `warn=0`,
`xfail=6`, `cov=100`, `outliers=0`, `excluded=0`, and `exit=0`. The validation
plan records the same result and leaves Steps 1 through 6 pending.

### Implementation report for step 0 review-resume-command (round 1)

- Added `tests/unit/tools/test_review_resume_perf/__init__.py` and a 247-line
  `test_review_resume_perf_tdd.py` contract suite.
- Added typed migration and wait spies with deterministic candidate counts and
  synthetic monotonic time.
- Marked the six contracts as strict xfails owned by Step 1 or Step 5 so an
  unexpected early pass fails until the owning step activates its gates.
- Replaced a cold subprocess in the invalid-root review-status acceptance case
  with the same public CLI adapter call while preserving every return-code and
  stream assertion. The flagged call fell from 5.38 seconds to below the
  0.01-second report threshold.
- Qualified repeated exchange headings in two historical transcripts so the
  repository Markdown gate can validate the staged tree.
- Recorded the complete implementation-check evidence for Step 0.

### Change summary for step 0 review-resume-command (round 1)

The staged index contains seven paths in four validated `a.commit` groups:

1. `.vscode/settings.json` records the pre-existing `prevalidated` vocabulary
   addition.
2. The review-resume feature-request transcript and code-reviewer plan
   transcript receive exchange-2 heading qualifiers.
3. The two new performance-contract files and the optimized review-status
   acceptance file implement and verify Step 0.
4. The review-resume validation plan records Step 0 as fully implemented; this
   is the required final commit.

`commit-plan-check.bat --format json` reports `state=valid`, `ready=true`, the
same seven staged paths, and those four groups in dependency order.

### Writer response for step 0 review-resume-command (round 1)

Writer response: This is round 1, so there is no earlier reviewer feedback to accept, reject, or
disagree with. The requestor asks the reviewer to inspect the exact staged index,
the Step 0 validation verdict, the strict-xfail ownership boundaries, the
acceptance-test optimization, and the four-group commit plan.

### Reviewer focus for step 0 review-resume-command (round 1)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-0-round-1 -->

## Round 1 by reviewer - Step 0

- Recorded: 2026-09-01T21:06:25+02:00
- Exchange: code/code/v0.11.0/review-resume-command
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-resume-command.md
- Implementation step: 0
- Outcome: answer

### Assessed index identity for step 0 review-resume-command (exchange 1) (round 1)

Baseline index tree: fc3792b2226b86aec05a004722a394cc7e6ba245

Assessed index tree: fc3792b2226b86aec05a004722a394cc7e6ba245

### Implementation check for step 0 review-resume-command (exchange 1) (round 1)

Result: Yes. Step 0 is fully implemented.

Both files the plan names for Step 0 exist and are staged:
`tests/unit/tools/test_review_resume_perf/__init__.py` at 2 lines and
`test_review_resume_perf_tdd.py` at 247 lines, inside the advisory budgets of 5
and 260.

All six gates the plan requires are present, one per required contract: three
flat placement reads, linear candidate parsing, no full status projection from
`migration_check`, bounded quiet waiting, notification wake into an
authoritative rescan, and polling fallback. Each carries a strict xfail and a
one-second `pytest.mark.timeout`, and each asserts spy call counts; the two
contracts with synthetic workloads also assert a 0.25-second elapsed bound.

The spy ports cover the six behaviors the plan lists: configuration reads,
directory enumeration, candidate parsing, status projection, notification
hints, and fallback polls. The call sequences are internally consistent across
the three wait contracts: one initial rescan plus one per interval, a poll only
when no notification arrived, and rescan counts of 4, 2, and 3 that follow from
the declared interval counts.

Gate ownership is closed by the plan rather than by convention. Step 1 must
remove the migration xfails and Step 5 the wait xfails, and both steps state it
in their fix intent, implementation, and completion criteria. The seams import
`tools.review_artifact_migration` and `tools.review_resume_wait`, both of which
appear in the plan's new-production-module list, so the gates will activate
against the modules the plan actually schedules.

The reviewer wrote no validation-plan row and made no repair, so this result
reflects the writer's staged work unchanged.

Validation plan effects: The reviewer wrote no validation-plan row this round. Reviewer assessment mode
permits writing only the reviewed step's rows, and no correction was needed:
the writer's own Step 0 record already matches the evidence this review
collected independently.

The staged validation plan records Step 0 as fully implemented, names both new
files, describes the three migration and three wait gates, and reports
`fail=0`, `warn=0`, `xfail=6`, `cov=100`, `outliers=0`, `excluded=0`, `exit=0`.
The forced walk this reviewer ran returned exactly those values, so the record
is accurate rather than merely plausible.

It also discloses the three staged changes that fall outside Step 0's declared
file list, the acceptance-test optimization and the two transcript heading
fixes, together with the reason each was required. That disclosure is what
makes the wider staged scope attributable.

The umbrella row was not completed and must not be: reviewer mode never marks
an umbrella effort complete, and Steps 1 through 6 remain pending.

### Pre-repair mandatory checks and coverage for step 0 review-resume-command (exchange 1) (round 1)

No pre-repair blob was recorded, because no repair was made and no file was
edited by the reviewer.

The baseline captured before assessment covers all seven staged paths through
`validation-state capture`, with the index tree
`fc3792b2226b86aec05a004722a394cc7e6ba245`, seven tracked digests, and no
ignored or untracked entries in scope. That baseline is retained in the live
evidence manifest and in the ignored root file
`a.code-review.validation-before.resume-step0.json`.

The umbrella digest was captured before the implementation-check result as
`bb71aaf68bb45d395e719881a86817a146eba8f164e06a09433fb375914ddc81`.

One tooling note that affected evidence capture rather than the staged work:
`validation-state capture` output written through PowerShell `Out-File
-Encoding utf8` carries a byte-order mark, which the evidence launcher refuses
with "cannot read evidence JSON: Unexpected UTF-8 BOM". The retained baseline
was rewritten without a BOM from the same launcher output before comparison, so
the compared bytes are the launcher's own.

### Resolved validation set and sources for step 0 review-resume-command (exchange 1) (round 1)

Every resolved mandatory command was run independently by the reviewer against
the received repository state. All four passed.

- `ghog day` (project): `fail=0 warn=0 xfail=6 cov=100 outliers=0 excluded=0
  exit=0`, walk duration 2m56s, phases check, affected, and full all green.
- `ghog single tests/unit/tools/test_review_resume_perf/test_review_resume_perf_tdd.py`
  (plan): `fail=0 warn=0 xfail=6 exit=0`, which is the plan's "passes with only
  the declared strict xfails" criterion, with the six xfails being exactly the
  six declared gates.
- `rg -n -e xfail -e timeout -e migration -e notification -e poll tests/unit/tools/test_review_resume_perf`
  (plan): exit 0, listing every gate together with its owning step through the
  xfail reasons naming Step 1 and Step 5.
- `commit-plan-check.bat --format json` (request): exit 0 with `state=valid`,
  `ready=true`, seven staged paths, four ordered groups, and no diagnostics.

One material point about the first command. The plain `ghog day` invocation
first returned `exit=0` while doing no work at all: "No Python file changed
since the last green ghog day walk - nothing to do", with `cov=skipped
outliers=skipped excluded=skipped`. That result cannot substantiate coverage,
outliers, or the xfail count, and under the reviewer contract a command that
did not run is missing evidence rather than a pass. The reported result above
comes from `ghog day --force`, which performed the full 2,219-test walk.

Any later reviewer round on this repository should force the walk for the same
reason. A cached no-op is indistinguishable from a real pass in its exit code
alone, and it is the requestor's own earlier walk that primes the cache.

### Resolver drift and direction for step 0 review-resume-command (exchange 1) (round 1)

No resolver drift. The request's embedded set and the current resolver set are
identical, so the union adds nothing and removes nothing.

The repository declares no `.review-validation` file, so the project source
resolves to the built-in default `ghog day`, which is exactly what the request
payload records with source `project`. The two `plan` additions and the single
`request` addition in the payload match the commands this reviewer ran, in the
same order and with the same source labels.

### Repository state around validation for step 0 review-resume-command (exchange 1) (round 1)

The received repository state is unchanged by this review.

- Index tree at request time, at assessment start, and after every validation
  command: `fc3792b2226b86aec05a004722a394cc7e6ba245`. The request-time tree in
  the evidence payload matches, so the identity gate passed and no early
  rejection applied.
- Umbrella digest before and after the implementation-check result:
  `bb71aaf68bb45d395e719881a86817a146eba8f164e06a09433fb375914ddc81`,
  `changed: false`. The umbrella was not touched and no umbrella row was
  completed.
- Validation-state comparison over the seven staged paths: `acceptable: true`
  with empty `tracked_paths`, `untracked_paths`, and `ignored_paths`. The full
  suite, the focused run, the grep check, and the commit-plan check produced no
  tracked side effect inside the compared scope.

The validation runs did write ignored artifacts outside that scope, the
Groundhog log and its status and outlier records, which the contract treats as
acceptable. Nothing was reverted and nothing was staged.

### Repair inventory for step 0 review-resume-command (exchange 1) (round 1)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 0 review-resume-command (exchange 1) (round 1)

`a.commit` is accurate and needs no amendment. The reviewer re-ran
`commit-plan-check.bat --format json` independently rather than relying on the
result embedded in the request, and both agree.

The independent run reports `state=valid`, `ready=true`, `schema_version=1`, no
diagnostics, and exit 0. Its seven staged paths match the index exactly, and its
four groups are in dependency order:

1. `chore(vscode): recognize prevalidated` for `.vscode/settings.json`.
2. `docs(review): qualify repeated exchange headings` for the two review
   transcripts.
3. `test(review-resume): add performance guardrails` for the two new contract
   files and the optimized review-status acceptance test.
4. `docs(review-resume-command): record step 0 validation` for the validation
   plan, correctly placed last as the record of the completed step.

Group membership is defensible on its own terms. The vocabulary entry is
unrelated to Step 0 and is grouped alone; the transcript fixes are grouped
together as documentation; the acceptance-test optimization sits with the
performance work it belongs to rather than with unrelated tests; and the
validation record is the final commit.

A status 0 here satisfies only the mechanical `a.commit` result of the readiness
floor. It does not by itself establish implementation completeness, validation
results, or repair attribution, and it authorizes no commit.

### Findings and boundaries for step 0 review-resume-command (exchange 1) (round 1)

Unresolved findings: None.

Boundary-crossing work: None.

### Writer instructions for step 0 review-resume-command (exchange 1) (round 1)

Nothing is required before the human commit choice. The readiness floor is
complete, the reviewer made no repair, and no finding is carried into a later
round.

Three non-blocking notes, none of which changes the staged work:

1. Step 0's declared "Files involved" lists only the two new contract files,
   while three further files were changed to make Step 0's own gate pass: the
   review-status acceptance test, whose 5.38-second subprocess was the outlier
   standing between the walk and `outliers=0`, and two transcripts whose
   duplicate headings blocked the Markdown gate. Staging them was correct under
   the repository rule that a commit run covers every staged change, and the
   validation record discloses all three. The gap is in the plan's file list
   rather than in the work, so it is worth a line in the plan when a later step
   touches that section, not a rework round now.
2. The acceptance-test optimization preserves all four original assertions,
   status 2, empty stdout, the `rvw_status:` stderr prefix, and the JSON decode
   failure, and the launcher-versus-direct comparison still covers exit 0 and
   exit 3 as real processes. What it no longer covers is the exit-2 path as a
   process, including the `-P` isolation the old subprocess proved. That is a
   deliberate and reasonable trade for 5.38 seconds, and it is worth recording
   in the step's validation notes so a later reader does not mistake it for an
   oversight.
3. A plain `ghog day` in this repository can return `exit=0` while doing no
   work, reporting "No Python file changed since the last green ghog day walk"
   with coverage and outliers skipped. The requestor's own walk primes that
   cache, so a reviewer who runs the bare command inherits the writer's result
   instead of producing independent evidence. Future rounds should force the
   walk. Consider recording that in the plan's ready-to-run commands, where the
   shared gate loop is currently written as plain `ghog day`.

The commit-ready recommendation is advisory. Only the human may choose `Commit`
or `Rework and review again`, and this answer authorizes nothing on its own.

### Decision rationale for step 0 review-resume-command (exchange 1) (round 1)

All six readiness-floor results pass on independently collected evidence, and
this round made no repair of any kind, so the recommendation is commit-ready.

- Exact identity: the request-time index tree matches the live tree
  `fc3792b2226b86aec05a004722a394cc7e6ba245`, the named step exists in the exact
  plan, and the envelope, human-readable identity, round, and occurrence agree.
- Complete implementation: both declared files exist within budget, all six
  required gates are present with strict xfails and timeouts, the spies cover
  the six required ports, and the later steps that must remove each gate are the
  ones the plan names.
- Mandatory validation and coverage: all four resolved commands ran and passed,
  with the project gate forced to a real 2,219-test walk reporting `cov=100`,
  `outliers=0`, and the six expected xfails. No resolver drift.
- Attributable staged scope: every one of the seven staged paths is accounted
  for, three of them outside Step 0's file list but each disclosed in the
  validation record with the reason it was required, and none swept in without
  explanation.
- Unresolved findings: none current and none carried, this being round 1.
- `a.commit`: the independent re-run reports valid, ready, four ordered groups,
  and no diagnostics, matching the staged set exactly.

The three notes in the writer instructions are advisory observations about the
plan's file list, a deliberate coverage trade, and a caching hazard in the
project gate. None of them describes a defect in the staged work, so none blocks
this recommendation.

This recommendation is advisory and authorizes no commit. The human chooses
`Commit` or `Rework and review again` at the convergence gate.

### Final reviewer decision for step 0 review-resume-command (exchange 1) (round 1)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-0-round-1 -->

## Round 1 by human - Step 0 - human-confirmation

- Recorded: 2026-09-01T21:13:25+02:00
- Exchange: code/code/v0.11.0/review-resume-command
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-resume-command.md
- Implementation step: 0
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-1 -->

## Round 1 by requestor - Step 1

- Recorded: 2026-09-02T00:59:48+02:00
- Exchange: code/code/v0.11.0/review-resume-command
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-resume-command.md
- Implementation step: 1
- Outcome: request

### Review identity for step 1 review-resume-command (round 1)

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: docs/v0.11.0/plan.v0.11.0.review-resume-command.md
Implementation step: 1
Review round: 1

### Code review evidence for step 1 review-resume-command (round 1)

request_index_tree: d2204da02d307e13dee5865d23dfcb0d31443ee0
resolved_validation_set:

- ghog day (sources: project)
- ghog single tests/unit/tools/test_review_resume_perf/test_review_resume_perf_tdd.py tests/unit/tools/test_review_artifact_home tests/unit/tools/test_review_exchange_paths tests/unit/tools/test_review_exchange_store/test_review_exchange_store_validation_tdd.py (sources: plan)

commit_plan_result:

```text
state: valid
ready: true
group 1: feat(review): add configurable artifact home
group 1 path: tools/code_review_evidence.py
group 1 path: tools/review_artifact_configuration.py
group 1 path: tools/review_artifact_migration.py
group 1 path: tools/review_artifact_registry.py
group 1 path: tools/review_exchange_models.py
group 1 path: tools/review_exchange_paths.py
group 1 path: tools/review_status.py
group 1 path: tests/acceptance/review_status/test_review_status_acceptance/test_review_status_acceptance_tdd.py
group 1 path: tests/unit/tools/git_test_double.py
group 1 path: tests/unit/tools/test_code_review_evidence/conftest.py
group 1 path: tests/unit/tools/test_code_review_evidence/test_code_review_evidence_boundaries_tdd.py
group 1 path: tests/unit/tools/test_code_review_evidence/test_code_review_evidence_cli_tdd.py
group 1 path: tests/unit/tools/test_code_reviewer_acceptance/conftest.py
group 1 path: tests/unit/tools/test_code_reviewer_acceptance/fixtures.py
group 1 path: tests/unit/tools/test_prompt_workflow_code_review/test_prompt_workflow_code_review_tdd.py
group 1 path: tests/unit/tools/test_review_artifact_home/__init__.py
group 1 path: tests/unit/tools/test_review_artifact_home/test_review_artifact_configuration_tdd.py
group 1 path: tests/unit/tools/test_review_artifact_home/test_review_artifact_migration_boundaries_tdd.py
group 1 path: tests/unit/tools/test_review_artifact_home/test_review_artifact_migration_tdd.py
group 1 path: tests/unit/tools/test_review_artifact_home/test_review_artifact_registry_pbt.py
group 1 path: tests/unit/tools/test_review_artifact_home/test_review_artifact_registry_tdd.py
group 1 path: tests/unit/tools/test_review_exchange_acceptance/conftest.py
group 1 path: tests/unit/tools/test_review_exchange_acceptance/test_review_exchange_acceptance_tdd.py
group 1 path: tests/unit/tools/test_review_exchange_lifecycle/test_review_exchange_boundaries_tdd.py
group 1 path: tests/unit/tools/test_review_exchange_lifecycle/test_review_exchange_lifecycle_recovery_tdd.py
group 1 path: tests/unit/tools/test_review_exchange_models/test_review_exchange_models_tdd.py
group 1 path: tests/unit/tools/test_review_exchange_paths/test_review_exchange_paths_tdd.py
group 1 path: tests/unit/tools/test_review_exchange_state/test_review_exchange_state_tdd.py
group 1 path: tests/unit/tools/test_review_exchange_store/test_review_exchange_store_validation_tdd.py
group 1 path: tests/unit/tools/test_review_resume_perf/test_review_resume_perf_tdd.py
group 1 path: tests/unit/tools/test_review_status/test_review_status_tdd.py
group 1 path: tests/unit/tools/test_spec_review_requestor_acceptance/conftest.py
group 1 path: tests/unit/tools/test_spec_review_requestor_acceptance/test_spec_review_requestor_io_acceptance_tdd.py
group 1 path: tests/unit/tools/test_spec_reviewer_acceptance/conftest.py
group 2: docs(review-resume-command): fix transcript lint
group 2 path: docs/v0.11.0/review.code.v0.11.0.review-resume-command.md
group 3: docs(review-resume-command): record step 1 validation
group 3 path: docs/v0.11.0/plan.v0.11.0.review-resume-command.validation.md
staged path: docs/v0.11.0/plan.v0.11.0.review-resume-command.validation.md
staged path: docs/v0.11.0/review.code.v0.11.0.review-resume-command.md
staged path: tests/acceptance/review_status/test_review_status_acceptance/test_review_status_acceptance_tdd.py
staged path: tests/unit/tools/git_test_double.py
staged path: tests/unit/tools/test_code_review_evidence/conftest.py
staged path: tests/unit/tools/test_code_review_evidence/test_code_review_evidence_boundaries_tdd.py
staged path: tests/unit/tools/test_code_review_evidence/test_code_review_evidence_cli_tdd.py
staged path: tests/unit/tools/test_code_reviewer_acceptance/conftest.py
staged path: tests/unit/tools/test_code_reviewer_acceptance/fixtures.py
staged path: tests/unit/tools/test_prompt_workflow_code_review/test_prompt_workflow_code_review_tdd.py
staged path: tests/unit/tools/test_review_artifact_home/__init__.py
staged path: tests/unit/tools/test_review_artifact_home/test_review_artifact_configuration_tdd.py
staged path: tests/unit/tools/test_review_artifact_home/test_review_artifact_migration_boundaries_tdd.py
staged path: tests/unit/tools/test_review_artifact_home/test_review_artifact_migration_tdd.py
staged path: tests/unit/tools/test_review_artifact_home/test_review_artifact_registry_pbt.py
staged path: tests/unit/tools/test_review_artifact_home/test_review_artifact_registry_tdd.py
staged path: tests/unit/tools/test_review_exchange_acceptance/conftest.py
staged path: tests/unit/tools/test_review_exchange_acceptance/test_review_exchange_acceptance_tdd.py
staged path: tests/unit/tools/test_review_exchange_lifecycle/test_review_exchange_boundaries_tdd.py
staged path: tests/unit/tools/test_review_exchange_lifecycle/test_review_exchange_lifecycle_recovery_tdd.py
staged path: tests/unit/tools/test_review_exchange_models/test_review_exchange_models_tdd.py
staged path: tests/unit/tools/test_review_exchange_paths/test_review_exchange_paths_tdd.py
staged path: tests/unit/tools/test_review_exchange_state/test_review_exchange_state_tdd.py
staged path: tests/unit/tools/test_review_exchange_store/test_review_exchange_store_validation_tdd.py
staged path: tests/unit/tools/test_review_resume_perf/test_review_resume_perf_tdd.py
staged path: tests/unit/tools/test_review_status/test_review_status_tdd.py
staged path: tests/unit/tools/test_spec_review_requestor_acceptance/conftest.py
staged path: tests/unit/tools/test_spec_review_requestor_acceptance/test_spec_review_requestor_io_acceptance_tdd.py
staged path: tests/unit/tools/test_spec_reviewer_acceptance/conftest.py
staged path: tools/code_review_evidence.py
staged path: tools/review_artifact_configuration.py
staged path: tools/review_artifact_migration.py
staged path: tools/review_artifact_registry.py
staged path: tools/review_exchange_models.py
staged path: tools/review_exchange_paths.py
staged path: tools/review_status.py
```

### Requestor assessment for step 1 review-resume-command (round 1)

Step 1 is fully implemented.

The implementation adds strict artifact-home configuration, a closed artifact
registry and locator, transactional migration with recovery, home-aware status
and retained-evidence paths, and one invocation-scoped status configuration.
The focused Step 1 suite passed. The final Groundhog walk passed all 2,283 tests
with 100 percent production coverage, three intentional later-step xfails, no
warnings, and no timing outliers.

The migration scan is linear across exactly three flat locations. Status loads
artifact configuration once per invocation and reuses it for review-mode
loading, candidate enumeration, and candidate path derivation. No DDD or
ports-and-adapters violation, feature regression, or remaining Step 1 work was
found by the implementation check.

### Implementation report for step 1 review-resume-command (round 1)

The implementation introduces `ReviewArtifactConfiguration` for strict
`.review-artifacts.ini` parsing, repository-bound path validation, tracked-home
rejection, and exact home-local ignore preparation. The default home is
`.reviews`; a declaration can select another repository-local directory.

`ReviewArtifactRegistry` defines the closed runtime artifact vocabulary and
role attribution. `ReviewArtifactLocator` derives exchange paths, archives,
retained code-review evidence, fixed markers, guidance, question state, and the
migration journal under the configured home while transcripts remain beside
their reviewed documents.

`ReviewArtifactMigration` inspects only the project root, default home, and
configured home. It validates regular files, fingerprints exact bytes, resolves
identical duplicates, blocks ambiguous collisions, writes one strict atomic
full-snapshot JSON journal, rolls back uncommitted moves, completes committed
cleanup, recovers crash windows, and holds an exclusive migration lock.

Exchange derivation, review-mode lookup, review status, and retained evidence
now use the home-aware boundary. `_StatusInvocation` carries one artifact
configuration through each complete status projection, preventing repeated
declaration and Git tracking reads across multiple candidates.

The test work adds dedicated configuration, registry, property, migration,
recovery, and boundary suites; adapts existing exchange, status, reviewer, and
evidence fixtures to configured homes; activates the Step 1 performance
contracts; and preserves strict path, schema, transcript, and launcher behavior.

### Change summary for step 1 review-resume-command (round 1)

The staged implementation contains these paths:

- `tools/code_review_evidence.py`
- `tools/review_artifact_configuration.py`
- `tools/review_artifact_migration.py`
- `tools/review_artifact_registry.py`
- `tools/review_exchange_models.py`
- `tools/review_exchange_paths.py`
- `tools/review_status.py`
- `tests/acceptance/review_status/test_review_status_acceptance/test_review_status_acceptance_tdd.py`
- `tests/unit/tools/git_test_double.py`
- `tests/unit/tools/test_code_review_evidence/conftest.py`
- `tests/unit/tools/test_code_review_evidence/test_code_review_evidence_boundaries_tdd.py`
- `tests/unit/tools/test_code_review_evidence/test_code_review_evidence_cli_tdd.py`
- `tests/unit/tools/test_code_reviewer_acceptance/conftest.py`
- `tests/unit/tools/test_code_reviewer_acceptance/fixtures.py`
- `tests/unit/tools/test_prompt_workflow_code_review/test_prompt_workflow_code_review_tdd.py`
- `tests/unit/tools/test_review_artifact_home/__init__.py`
- `tests/unit/tools/test_review_artifact_home/test_review_artifact_configuration_tdd.py`
- `tests/unit/tools/test_review_artifact_home/test_review_artifact_migration_boundaries_tdd.py`
- `tests/unit/tools/test_review_artifact_home/test_review_artifact_migration_tdd.py`
- `tests/unit/tools/test_review_artifact_home/test_review_artifact_registry_pbt.py`
- `tests/unit/tools/test_review_artifact_home/test_review_artifact_registry_tdd.py`
- `tests/unit/tools/test_review_exchange_acceptance/conftest.py`
- `tests/unit/tools/test_review_exchange_acceptance/test_review_exchange_acceptance_tdd.py`
- `tests/unit/tools/test_review_exchange_lifecycle/test_review_exchange_boundaries_tdd.py`
- `tests/unit/tools/test_review_exchange_lifecycle/test_review_exchange_lifecycle_recovery_tdd.py`
- `tests/unit/tools/test_review_exchange_models/test_review_exchange_models_tdd.py`
- `tests/unit/tools/test_review_exchange_paths/test_review_exchange_paths_tdd.py`
- `tests/unit/tools/test_review_exchange_state/test_review_exchange_state_tdd.py`
- `tests/unit/tools/test_review_exchange_store/test_review_exchange_store_validation_tdd.py`
- `tests/unit/tools/test_review_resume_perf/test_review_resume_perf_tdd.py`
- `tests/unit/tools/test_review_status/test_review_status_tdd.py`
- `tests/unit/tools/test_spec_review_requestor_acceptance/conftest.py`
- `tests/unit/tools/test_spec_review_requestor_acceptance/test_spec_review_requestor_io_acceptance_tdd.py`
- `tests/unit/tools/test_spec_reviewer_acceptance/conftest.py`
- `docs/v0.11.0/review.code.v0.11.0.review-resume-command.md`
- `docs/v0.11.0/plan.v0.11.0.review-resume-command.validation.md`

The mechanically validated root `a.commit` has three groups, in dependency
order:

1. `feat(review): add configurable artifact home`
2. `docs(review-resume-command): fix transcript lint`
3. `docs(review-resume-command): record step 1 validation`

The final group uses the exact validation subject required by the workflow.

### Writer response for step 1 review-resume-command (round 1)

Writer response: This is the first code-review round for Step 1, so there is no earlier reviewer
feedback to accept, reject, or qualify. The requestor identified and closed one
invocation-scoped configuration reuse gap during implementation-check before
publishing this request.

### Reviewer focus for step 1 review-resume-command (round 1)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-1-round-1 -->

## Round 1 by reviewer - Step 1

- Recorded: 2026-09-02T10:50:18+02:00
- Exchange: code/code/v0.11.0/review-resume-command
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-resume-command.md
- Implementation step: 1
- Outcome: answer

### Assessed index identity for step 1 review-resume-command (exchange 1) (round 1)

Baseline index tree: d2204da02d307e13dee5865d23dfcb0d31443ee0

Assessed index tree: 08cad87b08cf8d6aa1bce8168e148d759a57a818

### Implementation check for step 1 review-resume-command (exchange 1) (round 1)

Result: Step 1 is not fully implemented in the reviewed state, so the reviewed-step
status sentence now reads `No. Step 1 has NOT been fully implemented.`

The delivered design is sound. `ReviewArtifactConfiguration` parses
`.review-artifacts.ini` strictly, defaults to `.reviews`, rejects absolute,
drive-qualified, expanded, escaping, and tracked homes, and prepares exact
`*\n` ignore coverage with rollback. `ReviewArtifactRegistry` closes the runtime
name vocabulary and `ReviewArtifactLocator` derives every transient below the
configured home while transcripts stay beside their reviewed documents.
`ReviewArtifactMigration` inspects exactly three flat locations, fingerprints
each candidate once, blocks ambiguity before movement, journals one atomically
replaced full snapshot, and recovers both the uncommitted and committed phases
under an exclusive lock.

Three findings stop the step short of complete.

The home move broke the reviewer's own publication path, and it surfaces only
when a reviewer actually runs. This is the round's most consequential finding. `code_review_evidence.manifest_path` now returns
the manifest inside the configured home, but `code_review_answer_cli._root_path`
still requires every caller input, retained manifest included, to sit directly
under the project root, while `_assessment_source` separately requires that
input to equal the live manifest path. Those two constraints became mutually
unsatisfiable, so `bin/code_review_answer.bat` failed every assessment render
with `retained manifest file must be directly under project root` and exit 2,
and no code-review answer could be published at all. The requestor could not
observe this, because the request renderer takes no manifest. The existing CLI
tests missed it because they monkeypatch `manifest_path` to a root-level
`tmp_path` file, so the double hid the very move Step 1 performed. On the human's
explicit direction that every review artifact and caller file belongs in
`.reviews`, the reviewer added one shared rule, `caller_file_parents`, and
routed all five request, answer, and exchange launchers through it. The rule
accepts the configured artifact home and, for now, the project root, so the
roughly 69 existing launcher test modules keep passing; both canonical
instructions were updated to require the home, and dropping the root from that
set is named follow-up work.

The closed registry regressed retained code-review evidence. `_RETAINED_RE`
accepted only `step-[1-9]\d*`, while `code_review_evidence._manifest_path`
still validates the step with `_TOKEN_RE` and renders the name through the
registry. Every retained-evidence operation for step 0 therefore failed with
`invalid registered retained-manifest name` and exit 2, although step 0 of this
very plan was code reviewed and retained evidence under the previous root
derivation. The reviewer repaired the pattern to `step-(?:0|[1-9]\d*)` and
verified that `read-manifest --implementation-step 0` now resolves its path.

The plan's own Step 1 completion criterion `ghog day` reports `exit=0` did not
hold on arrival. The walk stopped in its check phase on `markdown-check` and
the full suite reported failures with coverage withheld, caused by 66 tracked
`.agents/llm-shared/**` files an external plugin sync had rewritten with
machine-specific absolute redirects. After those were restored and the reviewer
repairs applied, `ghog day` reports `exit=0` with `cov=100`, `fail=0`,
`warn=0`, `outliers=0`, and the three intentional Step 5 xfails.

The architecture is otherwise clean, with one smell recorded rather than
repaired: `ReviewConfiguration.load` in `tools/review_exchange_models.py`
needs a function-local import of `tools.review_artifact_configuration` and
`tools.review_artifact_registry`, because both import `review_exchange_models`
at module scope. That deferred import is a real cycle between the shared model
module and the placement modules.

Placement and status work stays linear. Migration discovery is `O(n)` across
three flat directories with dictionary collision detection and no status
projection, and `_StatusInvocation` loads artifact configuration once per
invocation and reuses it for review-mode lookup, candidate enumeration, and
every candidate derivation.

Validation plan effects: The reviewer wrote only Step 1 rows of
`docs/v0.11.0/plan.v0.11.0.review-resume-command.validation.md`:

- the `Analysis of Step 1 implementation state` status sentence changed from
  `Yes. Step 1 has been fully implemented.` to
  `No. Step 1 has NOT been fully implemented.` with its supporting summary;
- a new `Missing work for Step 1` section records the five concrete items the
  writer must close, placed directly after `What was implemented for Step 1`;
- `Architecture check for Step 1` now records the deferred-import cycle between
  `review_exchange_models` and the placement modules and closes with an explicit
  yes;
- `Unit test coverage check for Step 1` records the proven `cov=100` result and
  names the registry test gap the reviewer closed;
- `Feature integrity for Step 1` records the step-0 retained-evidence
  regression, the launcher placement regression that blocked every answer
  render, the home-only status enumeration window that Step 4 closes, and the
  green walk reached after the contaminated `.agents/` files were restored.

The document-level status line stays `No, it is not implemented.` and no
umbrella row was touched. The opening theme sentence still claims Step 1 is
fully implemented and still says "Steps 2 through 7"; both are outside the
reviewed-step rows, so they are returned as writer work instead of edited.

### Pre-repair mandatory checks and coverage for step 1 review-resume-command (exchange 1) (round 1)

Baseline evidence was captured before any assessment or repair.

- `capture-index-tree` returned `d2204da02d307e13dee5865d23dfcb0d31443ee0`,
  which equals the `request_index_tree` carried by the round-1 request, so the
  received state matched the requested state and no early rejection applied.
- `umbrella-digest capture docs/v0.11.0/draft.v0.11.0.review-mode.md` returned
  `bb71aaf68bb45d395e719881a86817a146eba8f164e06a09433fb375914ddc81` and was
  retained as the before value.
- `validation-state capture` recorded the ordered union of the 36 staged step
  paths, the exact validation plan, and the known ghog artifacts `coverage.xml`,
  `.coverage`, `a.ghog.log`, and `a.ghog.senv.log`: 36 tracked files plus the
  ignored `.coverage` and `a.ghog.log`.
- `read-manifest` reported no retained manifest for this identity and step, so
  the round ran as a fresh assessment rather than a resumed one, and
  `write-manifest` stored the baseline before any mutation.
- `record-pre-repair-blob` captured `tools/review_artifact_registry.py` at
  `5cebee991881ae0ab16cfc90387521c948278005`,
  `tests/unit/tools/test_review_artifact_home/test_review_artifact_registry_tdd.py`
  at `6cb0ce733f75588dc1a438d0d79d40ff656cb670`, and
  `docs/v0.11.0/plan.v0.11.0.review-resume-command.validation.md` at
  `7c4339cda82a92bb96ab27a9eaaf6150132bf9c3` before their first edit. The
  answer-CLI blocker was found later in the round, so
  `tools/code_review_answer_cli.py` at
  `8c00ab8b26b3675c5b146301258552af849ff243` and
  `tests/unit/tools/test_code_review_answer/test_code_review_answer_cli_tdd.py`
  at `a07bb046fb2baaf4d0f062fd313bc609d16bc981` were recorded the same way
  before their own first edit. The wider caller-placement repair was found
  later still; each of its paths was recorded from the exact index blob that
  preceded the reviewer edit, and all 17 repair paths were proved cleanly
  attributable through `attribute-reviewer-patch` before any of them was
  staged.

### Resolved validation set and sources for step 1 review-resume-command (exchange 1) (round 1)

The reviewer ran the union of the request validation set and the current
resolver set. Both resolve to the same two mandatory commands, and both now
pass.

- `ghog day`, source project. Final result: `exit=0`. The walk completed all
  three phases: check `exit=0`, `affected --no-cov` `exit=0`, and full
  `fail=0 warn=0 xfail=3 cov=100 outliers=0 excluded=0 exit=0`. The three
  remaining xfails are the Step 5 wait gates.
- `ghog single tests/unit/tools/test_review_resume_perf/test_review_resume_perf_tdd.py tests/unit/tools/test_review_artifact_home tests/unit/tools/test_review_exchange_paths tests/unit/tools/test_review_exchange_store/test_review_exchange_store_validation_tdd.py`,
  source plan. Result: `fail=0 warn=0 xfail=3 exit=0`.

Reaching that state took three earlier attempts, and the record matters because
it is the evidence behind this round's findings.

- The first `ghog day` stopped in its check phase with
  `Failed steps for project 'llm-shared': markdown(1)`, reporting
  `.agents/llm-shared/instructions/code-reviewer.md:1: LS001` and `LS002`. A
  second run reproduced it.
- `ghog full` then reported `fail=2 cov=withheld` over 2,284 calls, failing
  `tests/acceptance/markdown_check/test_shared_gate/test_shared_gate_tdd.py::test_checked_repository_passes_public_launcher`
  and
  `tests/unit/tools/test_instruction_structure/test_codex_plugin_structure_tdd.py::test_codex_plugin_redirects_every_instruction`.
- The contamination kept spreading during the session, from 3 files to 66. A
  later `ghog full` reported `fail=8`, adding four instruction-adapter contract
  tests. Reverting `.agents/` cleared all of them at once, and the walk did not
  reproduce the drift afterwards, so ghog was never its source.

The reviewer also ran focused commands after each repair:
`ghog single tests/unit/tools/test_code_review_answer/test_code_review_answer_cli_tdd.py tests/unit/tools/test_review_artifact_home`
and the wider launcher set covering the code and specification request and
answer suites, both `exit=0`.

### Resolver drift and direction for step 1 review-resume-command (exchange 1) (round 1)

No resolver drift. The request-time validation set and the set resolved during
this round both contain exactly `ghog day` from the project source and the
focused `ghog single` command from the plan source, in the same order and with
the same arguments. The union the reviewer ran is therefore identical to the
request set, and no command was added or dropped in either direction.

### Repository state around validation for step 1 review-resume-command (exchange 1) (round 1)

The received index tree `d2204da02d307e13dee5865d23dfcb0d31443ee0` matched the
request-time index tree exactly, so the assessment ran against the requested
state. After the reviewer patch the assessed index tree is
`08cad87b08cf8d6aa1bce8168e148d759a57a818`.

The umbrella digest is unchanged:
`bb71aaf68bb45d395e719881a86817a146eba8f164e06a09433fb375914ddc81` before and
after, `changed: false`. No boundary violation.

`validation-state compare` over the ordered path set captured before the
criteria reports `tools/review_artifact_configuration.py`,
`tools/review_artifact_registry.py`,
`tests/unit/tools/test_review_artifact_home/test_review_artifact_configuration_tdd.py`,
`tests/unit/tools/test_review_artifact_home/test_review_artifact_registry_tdd.py`,
`docs/v0.11.0/plan.v0.11.0.review-resume-command.validation.md`, and the index
itself as the tracked differences, plus the ignored `.coverage` and `a.ghog.log`
that the validation commands rewrite. There is no tracked validation side effect
inside the reviewed path set.

The caller-placement repair also reached five launchers and four further test
modules that the request's staged set did not contain, so they fall outside the
compared path set by construction. Every one is recorded through the retained
manifest, which now lists 17 repair paths, and each was proved cleanly
attributable before staging.

The worktree carried one further contamination the reviewer did not create. 66
tracked files under `.agents/llm-shared/**` had been rewritten from relative
links to machine-specific absolute redirects such as
`instructions/groundhog.md`, and
`plugin.json` with changed line endings. It grew from 3 files to 66 during the
session. The repository's own gate forbids exactly this: `markdown-check`
rejects the rewritten stubs, and two instruction-structure suites assert the
relative form. No mandatory validation command could pass while it stood, so
on the human's explicit direction the reviewer restored all 66 with
`git checkout -- .agents/`. A later full walk did not reproduce the drift, so
the source is an external plugin sync rather than any repository command. The
commit handoff stages the whole tree with `git add -A`, so the tree must be
re-checked immediately before the commit.

The transcript `docs/v0.11.0/review.code.v0.11.0.review-resume-command.md`
shows an unstaged change: the round-1 request entry the protocol itself
appended after the staged lint fix. That is normal protocol authorship, not
writer work.

### Repair inventory for step 1 review-resume-command (exchange 1) (round 1)

Repairs made:

- tools/review_artifact_registry.py - substantive: widen `_RETAINED_RE` from `step-[1-9]\d*` to `step-(?:0|[1-9]\d*)` so retained code-review evidence resolves for step 0 again
- tools/review_artifact_configuration.py - substantive: add `caller_file_parents` as the single rule naming where a caller-owned review file may sit
- tools/code_review_answer_cli.py - substantive: resolve every caller input and both outputs through `caller_file_parents`, so the home-local retained manifest is accepted
- tools/review_exchange_cli.py - substantive: resolve `--content-file`, `--summary-file`, and `--guidance-file` through `caller_file_parents`
- tools/code_review_request.py - substantive: resolve caller inputs and outputs through `caller_file_parents`
- tools/spec_review_answer_cli.py - substantive: resolve caller inputs and outputs through `caller_file_parents`
- tools/spec_review_request.py - substantive: resolve caller inputs and outputs through `caller_file_parents`
- tests/unit/tools/test_review_artifact_home/test_review_artifact_registry_tdd.py - substantive: add `test_registry_renders_every_numbered_step_retained_manifest` and register the step-0 manifest name
- tests/unit/tools/test_review_artifact_home/test_review_artifact_configuration_tdd.py - substantive: cover the accepted caller locations and the broken-declaration fallback
- tests/unit/tools/test_code_review_answer/test_code_review_answer_cli_tdd.py - substantive: add a home-local render test and an out-of-repository rejection test
- tests/unit/tools/test_code_review_request/test_code_review_request_tdd.py - substantive: follow the new placement diagnostic
- tests/unit/tools/test_spec_review_answer/test_spec_review_answer_cli_tdd.py - substantive: follow the new placement diagnostic
- tests/unit/tools/test_spec_review_request/test_spec_review_request_tdd.py - substantive: follow the new placement diagnostic
- tests/unit/tools/test_review_exchange_cli/test_review_exchange_cli_tdd.py - substantive: follow the new placement diagnostic
- instructions/review-requestor.md - substantive: require caller files in the configured artifact home and document the declaration, ignore coverage, and transcript exception
- instructions/spec-reviewer.md - substantive: require home-local caller inputs, renderer outputs, and retained manifest
- docs/v0.11.0/plan.v0.11.0.review-resume-command.validation.md - review metadata: rewrite only the Step 1 rows, including the No status sentence and the `Missing work for Step 1` section
- a.commit - review metadata: add groups 2 and 3 for the caller-placement change and the instruction updates, and renumber the two documentation groups

Paths staged:

- ﻿docs/v0.11.0/plan.v0.11.0.review-resume-command.validation.md
- docs/v0.11.0/review.code.v0.11.0.review-resume-command.md
- instructions/review-requestor.md
- instructions/spec-reviewer.md
- tests/acceptance/review_status/test_review_status_acceptance/test_review_status_acceptance_tdd.py
- tests/unit/tools/git_test_double.py
- tests/unit/tools/test_code_review_answer/test_code_review_answer_cli_tdd.py
- tests/unit/tools/test_code_review_evidence/conftest.py
- tests/unit/tools/test_code_review_evidence/test_code_review_evidence_boundaries_tdd.py
- tests/unit/tools/test_code_review_evidence/test_code_review_evidence_cli_tdd.py
- tests/unit/tools/test_code_review_request/test_code_review_request_tdd.py
- tests/unit/tools/test_code_reviewer_acceptance/conftest.py
- tests/unit/tools/test_code_reviewer_acceptance/fixtures.py
- tests/unit/tools/test_prompt_workflow_code_review/test_prompt_workflow_code_review_tdd.py
- `tests/unit/tools/test_review_artifact_home/__init__.py`
- tests/unit/tools/test_review_artifact_home/test_review_artifact_configuration_tdd.py
- tests/unit/tools/test_review_artifact_home/test_review_artifact_migration_boundaries_tdd.py
- tests/unit/tools/test_review_artifact_home/test_review_artifact_migration_tdd.py
- tests/unit/tools/test_review_artifact_home/test_review_artifact_registry_pbt.py
- tests/unit/tools/test_review_artifact_home/test_review_artifact_registry_tdd.py
- tests/unit/tools/test_review_exchange_acceptance/conftest.py
- tests/unit/tools/test_review_exchange_acceptance/test_review_exchange_acceptance_tdd.py
- tests/unit/tools/test_review_exchange_cli/test_review_exchange_cli_tdd.py
- tests/unit/tools/test_review_exchange_lifecycle/test_review_exchange_boundaries_tdd.py
- tests/unit/tools/test_review_exchange_lifecycle/test_review_exchange_lifecycle_recovery_tdd.py
- tests/unit/tools/test_review_exchange_models/test_review_exchange_models_tdd.py
- tests/unit/tools/test_review_exchange_paths/test_review_exchange_paths_tdd.py
- tests/unit/tools/test_review_exchange_state/test_review_exchange_state_tdd.py
- tests/unit/tools/test_review_exchange_store/test_review_exchange_store_validation_tdd.py
- tests/unit/tools/test_review_resume_perf/test_review_resume_perf_tdd.py
- tests/unit/tools/test_review_status/test_review_status_tdd.py
- tests/unit/tools/test_spec_review_answer/test_spec_review_answer_cli_tdd.py
- tests/unit/tools/test_spec_review_request/test_spec_review_request_tdd.py
- tests/unit/tools/test_spec_review_requestor_acceptance/conftest.py
- tests/unit/tools/test_spec_review_requestor_acceptance/test_spec_review_requestor_io_acceptance_tdd.py
- tests/unit/tools/test_spec_reviewer_acceptance/conftest.py
- tools/code_review_answer_cli.py
- tools/code_review_evidence.py
- tools/code_review_request.py
- tools/review_artifact_configuration.py
- tools/review_artifact_migration.py
- tools/review_artifact_registry.py
- tools/review_exchange_cli.py
- tools/review_exchange_models.py
- tools/review_exchange_paths.py
- tools/review_status.py
- tools/spec_review_answer_cli.py
- tools/spec_review_request.py

### Commit plan assessment for step 1 review-resume-command (exchange 1) (round 1)

The reviewer reran `python -m tools.commit_plan_check --format json`
independently against the received repository state, before assessing grouping,
and again after staging the reviewer patch. `bin/commit_plan_check.bat` does not
exist yet, so the shipped module was invoked directly; it is the same checker
the launcher will wrap when umbrella row 8 lands.

Both runs returned `state: valid`, `ready: true`, exit `0`, an empty
`diagnostics` list, 36 staged paths, and the same three groups in dependency
order:

1. `feat(review): add configurable artifact home`
2. `docs(review-resume-command): fix transcript lint`
3. `docs(review-resume-command): record step 1 validation`

The final run reports 48 staged paths across five groups, because the reviewer
patch added the caller-placement change and the instruction updates. The
reviewer amended `a.commit` to carry them as two new groups placed after the
artifact-home group they depend on: group 2 `feat(review): accept caller files
in the artifact home` and group 3 `docs(review): require the artifact home for
caller files`. `tools/code_review_answer_cli.py` and its test moved out of
group 1 into group 2 so no path is claimed twice, and the two existing
documentation groups were renumbered 4 and 5. The checker returned `valid`,
`ready`, and an empty `diagnostics` list on the amended plan. The mechanical result
satisfies only the `a.commit` part of the readiness floor; it proves nothing
about completeness, validation, or coverage, and it authorizes no commit.

### Findings and boundaries for step 1 review-resume-command (exchange 1) (round 1)

Unresolved findings:

- `bin/code_review_answer.bat` could render no assessment at all in the delivered state, because every launcher required caller-owned files directly under the project root while `manifest_path` now returns the retained manifest inside the configured home; the reviewer routed all five launchers through one shared rule, and the writer must confirm that shape.
- `caller_file_parents` still accepts the project root beside the artifact home, so the roughly 69 existing launcher test modules keep passing; both canonical instructions now describe the home as the only correct location, so dropping the root from that set is named follow-up work rather than a finished state.
- The answer-CLI tests monkeypatch `manifest_path` to a root-level `tmp_path` file, so the double hid the regression the home move created; the same doubling pattern should be audited wherever Step 1 moved a path.
- `ReviewArtifactRegistry` still rejects a non-numeric implementation-step identifier such as `4A`, which `code_review_evidence._TOKEN_RE` accepts and `implementation-check.md` names as a valid `pw handoff after-check` argument; the alphabet is a writer decision.
- `ReviewConfiguration.load` in `tools/review_exchange_models.py` needs a function-local import of the placement modules to break a real import cycle, and the validation plan asserted no architecture issue.
- The validation plan's opening theme sentence claims Step 1 is fully implemented and names a Step 7 this plan does not have; it lies outside the reviewed-step rows the reviewer may write.
- `tools/review_artifact_migration.py` is 635 lines against its 480-line advisory target, and `tests/unit/tools/test_review_artifact_home/test_review_artifact_migration_tdd.py` is 632 lines although the plan required splitting recovery examples before either migration test file reached 550 lines; both stay under the 650-line ceiling, so they are advisory variance to record rather than a stop.
- Reaching a green gate required reverting 66 tracked `.agents/llm-shared/**` files that an external plugin sync had rewritten with machine-specific absolute redirects; the walk did not reproduce that drift afterwards, but the commit handoff stages with `git add -A`, so the tree must be re-checked immediately before the commit.

Boundary-crossing work:

- The caller-placement repair reached five launchers and four test modules that no plan step names, which exceeds an ordinary bounded in-step repair; the reviewer made it only because the human explicitly directed that every review artifact and caller file move into `.reviews`, and because without it no answer could be published at all.
- Removing the project root from `caller_file_parents`, so the artifact home becomes the only accepted location, needs a migration of roughly 69 existing launcher test modules and is left to the writer.
- Review-status candidate enumeration is now confined to the configured home with no legacy root fallback, and no production caller invokes `ReviewArtifactMigration` yet, so a repository still holding root-level coordination files reports no active exchange until Step 4 wires migration into status; that window belongs to the plan's own staging and is recorded rather than changed.
- Choosing whether the retained-manifest step token must also accept non-numeric sub-step identifiers is a writer decision about step identity, so the reviewer restored only the previously supported numeric form.
- The 66 contaminated `.agents/llm-shared/**` files were reverted with `git checkout --` rather than left in place, because the gate could not go green while they stood; that is human-directed cleanup of machine-generated drift, not writer work the reviewer absorbed.

### Writer instructions for step 1 review-resume-command (exchange 1) (round 1)

Do this before requesting the next round.

1. Confirm or replace the caller-placement repair, and treat it as the
   priority. Step 1 moved the retained manifest into the configured home but
   left every launcher requiring caller-owned files directly under the project
   root, so `bin/code_review_answer.bat` refused every assessment render and no
   code-review answer could be published. The reviewer added
   `caller_file_parents` in `tools/review_artifact_configuration.py` and routed
   `code_review_answer_cli`, `review_exchange_cli`, `code_review_request`,
   `spec_review_answer_cli`, and `spec_review_request` through it. Decide
   whether that is the shape you want, then sweep the same question across
   every other Step 1 path move: audit each test that monkeypatches
   `manifest_path` or an equivalent locator seam, because the existing
   answer-CLI tests pointed their double at a root-level `tmp_path` file and so
   proved nothing about the move.
2. Decide when the project root leaves `caller_file_parents`. It currently
   accepts the artifact home and the root, which keeps roughly 69 existing
   launcher test modules passing, but both canonical instructions now describe
   the home as the only correct location. Removing the root is a one-line
   change plus that test migration; schedule it or record the tolerance in the
   plan.
3. Re-check the tree immediately before the commit gate. An external plugin
   sync rewrote 66 tracked `.agents/llm-shared/**` files with machine-specific
   absolute redirects such as
   `instructions/groundhog.md`, growing from
   3 files to 66 during the review. The reviewer restored them with
   `git checkout -- .agents/`, and the later full walk did not reproduce the
   drift, so ghog is not its source. Because the commit handoff stages the whole
   tree with `git add -A`, confirm `git status --porcelain -- .agents` is empty
   right before committing.
4. Re-run `ghog day` and keep it at `exit=0` with `cov=100`. It reaches that
   now; confirm that
   `tests/acceptance/markdown_check/test_shared_gate/test_shared_gate_tdd.py::test_checked_repository_passes_public_launcher`
   and
   `tests/unit/tools/test_instruction_structure/test_codex_plugin_structure_tdd.py::test_codex_plugin_redirects_every_instruction`
   both pass, and that only the three Step 5 wait xfails remain.
5. Decide the retained-manifest step alphabet. The reviewer restored step `0` in
   `_RETAINED_RE`. Either widen it further so a sub-step identifier such as `4A`
   parses, matching `code_review_evidence._TOKEN_RE` and the `pw handoff
   after-check <x>` argument that `implementation-check.md` documents, or record
   in the plan that code-review steps are numeric only and constrain
   `_TOKEN_RE` to match. Keep the registry and the evidence renderer on one
   alphabet either way, and cover the decision with a registry test.
6. Break the import cycle behind `ReviewConfiguration.load` in
   `tools/review_exchange_models.py`, or record it in the plan as an accepted
   deviation. Moving review-mode marker resolution into `ReviewArtifactLocator`
   removes both the deferred import and the model's knowledge of the artifact
   home without changing behavior.
7. Rewrite the validation plan's opening theme sentence. It still claims Step 1
   is fully implemented, which now contradicts the Step 1 status sentence, and
   it says "Steps 2 through 7 remain pending" although this plan has Steps 0
   through 6.
8. Record the two accepted line-budget variances in the Step 1 addendums so the
   next step does not inherit them silently:
   `tools/review_artifact_migration.py` at 635 lines against a 480-line
   advisory target, and
   `tests/unit/tools/test_review_artifact_home/test_review_artifact_migration_tdd.py`
   at 632 lines although the split guidance required splitting recovery
   examples before either migration test file reached 550 lines. Both remain
   under the 650-line ceiling, so a split is optional; the record is not.
9. Assess the whole reviewer patch before continuing. It is staged, spans 17
   paths, and is listed in full in the repairs inventory of this answer: the
   registry and configuration modules, the five launchers, seven test modules,
   the two canonical instructions, and the Step 1 validation rows, with
   `a.commit` amended to carry two new groups. Keep, adjust, or reject it
   explicitly in the next round's writer response.

`a.commit` is valid and ready as amended, across five groups and 48 staged
paths. It needs further change only if items 2, 5, or 6 add files outside those
groups.

### Decision rationale for step 1 review-resume-command (exchange 1) (round 1)

The disposition is `changes-requested`, and two independent reasons each force
it on their own.

This round made substantive repairs, and large ones. They change production
code, tests, two canonical instructions, and the commit grouping, so they
cannot validly finish the workflow in the same round however sound they are.
The writer must see and accept them before the exchange can converge.

The reviewer also exceeded an ordinary bounded in-step repair, and says so
plainly. Only `tools/review_artifact_registry.py` and the validation-plan rows
sit inside the reviewed step's own files. The caller-placement change reaches
five launchers and four further test modules that no plan step names. Two
things justified it: the human explicitly directed that every review artifact
and caller-owned file move into `.reviews`, which settles the product decision
a reviewer may not take alone; and without it no code-review answer could be
rendered at all, so the exchange had no way to proceed. The writer may keep,
adjust, or reject the whole patch.

The evidence itself is now complete rather than blocking. `ghog day` reports
`exit=0` with `cov=100`, so the readiness floor's validation and coverage
result is satisfied for the reviewed state; the floor is still recorded as
incomplete because that state depends on an unassessed reviewer patch.

The two regressions were genuine Step 1 defects, and both are the same mistake
seen twice: the home move was applied to the producers of a path but not to its
consumers. `ReviewArtifactRegistry` refused a retained manifest that
`code_review_evidence` still renders and that step 0 of this very plan used,
and every launcher refused the home-local manifest that Step 1 had just
created. Neither could be observed from the requestor side, because the request
renderer takes no manifest, and the answer-CLI tests pointed their
`manifest_path` double at a root-level file, so the double hid exactly the move
under test.

Reaching a green gate also required restoring 66 tracked `.agents/llm-shared/**`
files that an external plugin sync had rewritten with machine-specific absolute
redirects. That drift is not writer work and not Step 1's doing; it was
reverted on the human's direction because no mandatory validation command could
pass while it stood.

Everything else is recorded rather than changed: the architecture smell, the
theme sentence outside the reviewed-step rows, the two line-budget variances
that stay under the 650-line ceiling, the remaining non-numeric step alphabet,
the project-root fallback the instructions no longer sanction, and the
home-only status enumeration window that Step 4 closes by design.

The identity checks all passed. The received index tree equalled the
request-time tree, the umbrella digest is unchanged, `a.commit` is valid and
ready across five groups and 48 paths, and the recommendation authorizes no
commit.

### Final reviewer decision for step 1 review-resume-command (exchange 1) (round 1)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-1-round-1 -->

## Round 2 by requestor - Step 1

- Recorded: 2026-09-02T12:22:08+02:00
- Exchange: code/code/v0.11.0/review-resume-command
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-resume-command.md
- Implementation step: 1
- Outcome: request

### Review identity for step 1 review-resume-command (round 2)

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: docs/v0.11.0/plan.v0.11.0.review-resume-command.md
Implementation step: 1
Review round: 2

### Code review evidence for step 1 review-resume-command (round 2)

request_index_tree: f302c7b08b233c9a897fcd4756eecbd6172bb4b8
resolved_validation_set:

- ghog day (sources: project)
- ghog single tests/unit/tools/test_review_resume_perf/test_review_resume_perf_tdd.py tests/unit/tools/test_review_artifact_home tests/unit/tools/test_review_exchange_paths tests/unit/tools/test_review_exchange_store/test_review_exchange_store_validation_tdd.py (sources: plan)

commit_plan_result:

```text
state: valid
ready: true
group 1: feat(review): add configurable artifact home
group 1 path: tools/code_review_evidence.py
group 1 path: tools/prompt_workflow_code_review.py
group 1 path: tools/prompt_workflow_review.py
group 1 path: tools/review_artifact_configuration.py
group 1 path: tools/review_artifact_migration.py
group 1 path: tools/review_artifact_registry.py
group 1 path: tools/review_exchange_models.py
group 1 path: tools/review_exchange_paths.py
group 1 path: tools/review_status.py
group 1 path: tests/acceptance/review_status/test_review_status_acceptance/test_review_status_acceptance_tdd.py
group 1 path: tests/unit/tools/git_test_double.py
group 1 path: tests/unit/tools/test_code_review_evidence/conftest.py
group 1 path: tests/unit/tools/test_code_review_evidence/test_code_review_evidence_boundaries_tdd.py
group 1 path: tests/unit/tools/test_code_review_evidence/test_code_review_evidence_cli_tdd.py
group 1 path: tests/unit/tools/test_code_reviewer_acceptance/conftest.py
group 1 path: tests/unit/tools/test_code_reviewer_acceptance/fixtures.py
group 1 path: tests/unit/tools/test_prompt_workflow_code_review/test_prompt_workflow_code_review_tdd.py
group 1 path: tests/unit/tools/test_review_artifact_home/__init__.py
group 1 path: tests/unit/tools/test_review_artifact_home/test_review_artifact_configuration_tdd.py
group 1 path: tests/unit/tools/test_review_artifact_home/test_review_artifact_migration_boundaries_tdd.py
group 1 path: tests/unit/tools/test_review_artifact_home/test_review_artifact_migration_tdd.py
group 1 path: tests/unit/tools/test_review_artifact_home/test_review_artifact_registry_pbt.py
group 1 path: tests/unit/tools/test_review_artifact_home/test_review_artifact_registry_tdd.py
group 1 path: tests/unit/tools/test_review_exchange_acceptance/conftest.py
group 1 path: tests/unit/tools/test_review_exchange_acceptance/test_review_exchange_acceptance_tdd.py
group 1 path: tests/unit/tools/test_review_exchange_lifecycle/test_review_exchange_boundaries_tdd.py
group 1 path: tests/unit/tools/test_review_exchange_lifecycle/test_review_exchange_lifecycle_recovery_tdd.py
group 1 path: tests/unit/tools/test_review_exchange_models/test_review_exchange_models_tdd.py
group 1 path: tests/unit/tools/test_review_exchange_paths/test_review_exchange_paths_tdd.py
group 1 path: tests/unit/tools/test_review_exchange_state/test_review_exchange_state_tdd.py
group 1 path: tests/unit/tools/test_review_exchange_store/test_review_exchange_store_validation_tdd.py
group 1 path: tests/unit/tools/test_review_resume_perf/test_review_resume_perf_tdd.py
group 1 path: tests/unit/tools/test_review_status/test_review_status_tdd.py
group 1 path: tests/unit/tools/test_spec_review_requestor_acceptance/conftest.py
group 1 path: tests/unit/tools/test_spec_review_requestor_acceptance/test_spec_review_requestor_io_acceptance_tdd.py
group 1 path: tests/unit/tools/test_spec_reviewer_acceptance/conftest.py
group 2: feat(review): enforce caller files in the artifact home
group 2 path: tools/code_review_answer_cli.py
group 2 path: tools/code_review_request.py
group 2 path: tools/review_exchange_cli.py
group 2 path: tools/spec_review_answer_cli.py
group 2 path: tools/spec_review_request.py
group 2 path: tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/test_commit_plan_check_acceptance_tdd.py
group 2 path: tests/unit/tools/test_code_review_answer/test_code_review_answer_cli_tdd.py
group 2 path: tests/unit/tools/test_code_review_request/test_code_review_request_tdd.py
group 2 path: tests/unit/tools/test_code_review_request_commit_plan/test_code_review_request_commit_plan_tdd.py
group 2 path: tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_io_acceptance_tdd.py
group 2 path: tests/unit/tools/test_code_reviewer_acceptance/test_code_reviewer_recovery_tdd.py
group 2 path: tests/unit/tools/test_review_exchange_cli/test_review_exchange_cli_boundaries_tdd.py
group 2 path: tests/unit/tools/test_review_exchange_cli/test_review_exchange_cli_tdd.py
group 2 path: tests/unit/tools/test_spec_review_answer/test_spec_review_answer_cli_tdd.py
group 2 path: tests/unit/tools/test_spec_review_request/test_spec_review_request_tdd.py
group 2 path: tests/unit/tools/test_spec_review_requestor_acceptance/test_spec_review_requestor_acceptance_tdd.py
group 2 path: tests/unit/tools/test_spec_reviewer_acceptance/fixtures.py
group 2 path: tests/unit/tools/test_spec_reviewer_acceptance/test_spec_reviewer_recovery_tdd.py
group 3: docs(review): require the artifact home for caller files
group 3 path: instructions/review-requestor.md
group 3 path: instructions/spec-reviewer.md
group 4: docs(review-resume-command): record step 1 review
group 4 path: docs/v0.11.0/review.code.v0.11.0.review-resume-command.md
group 5: docs(review-resume-command): update step 1 validation
group 5 path: docs/v0.11.0/plan.v0.11.0.review-resume-command.validation.md
staged path: docs/v0.11.0/plan.v0.11.0.review-resume-command.validation.md
staged path: docs/v0.11.0/review.code.v0.11.0.review-resume-command.md
staged path: instructions/review-requestor.md
staged path: instructions/spec-reviewer.md
staged path: tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/test_commit_plan_check_acceptance_tdd.py
staged path: tests/acceptance/review_status/test_review_status_acceptance/test_review_status_acceptance_tdd.py
staged path: tests/unit/tools/git_test_double.py
staged path: tests/unit/tools/test_code_review_answer/test_code_review_answer_cli_tdd.py
staged path: tests/unit/tools/test_code_review_evidence/conftest.py
staged path: tests/unit/tools/test_code_review_evidence/test_code_review_evidence_boundaries_tdd.py
staged path: tests/unit/tools/test_code_review_evidence/test_code_review_evidence_cli_tdd.py
staged path: tests/unit/tools/test_code_review_request/test_code_review_request_tdd.py
staged path: tests/unit/tools/test_code_review_request_commit_plan/test_code_review_request_commit_plan_tdd.py
staged path: tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_io_acceptance_tdd.py
staged path: tests/unit/tools/test_code_reviewer_acceptance/conftest.py
staged path: tests/unit/tools/test_code_reviewer_acceptance/fixtures.py
staged path: tests/unit/tools/test_code_reviewer_acceptance/test_code_reviewer_recovery_tdd.py
staged path: tests/unit/tools/test_prompt_workflow_code_review/test_prompt_workflow_code_review_tdd.py
staged path: tests/unit/tools/test_review_artifact_home/__init__.py
staged path: tests/unit/tools/test_review_artifact_home/test_review_artifact_configuration_tdd.py
staged path: tests/unit/tools/test_review_artifact_home/test_review_artifact_migration_boundaries_tdd.py
staged path: tests/unit/tools/test_review_artifact_home/test_review_artifact_migration_tdd.py
staged path: tests/unit/tools/test_review_artifact_home/test_review_artifact_registry_pbt.py
staged path: tests/unit/tools/test_review_artifact_home/test_review_artifact_registry_tdd.py
staged path: tests/unit/tools/test_review_exchange_acceptance/conftest.py
staged path: tests/unit/tools/test_review_exchange_acceptance/test_review_exchange_acceptance_tdd.py
staged path: tests/unit/tools/test_review_exchange_cli/test_review_exchange_cli_boundaries_tdd.py
staged path: tests/unit/tools/test_review_exchange_cli/test_review_exchange_cli_tdd.py
staged path: tests/unit/tools/test_review_exchange_lifecycle/test_review_exchange_boundaries_tdd.py
staged path: tests/unit/tools/test_review_exchange_lifecycle/test_review_exchange_lifecycle_recovery_tdd.py
staged path: tests/unit/tools/test_review_exchange_models/test_review_exchange_models_tdd.py
staged path: tests/unit/tools/test_review_exchange_paths/test_review_exchange_paths_tdd.py
staged path: tests/unit/tools/test_review_exchange_state/test_review_exchange_state_tdd.py
staged path: tests/unit/tools/test_review_exchange_store/test_review_exchange_store_validation_tdd.py
staged path: tests/unit/tools/test_review_resume_perf/test_review_resume_perf_tdd.py
staged path: tests/unit/tools/test_review_status/test_review_status_tdd.py
staged path: tests/unit/tools/test_spec_review_answer/test_spec_review_answer_cli_tdd.py
staged path: tests/unit/tools/test_spec_review_request/test_spec_review_request_tdd.py
staged path: tests/unit/tools/test_spec_review_requestor_acceptance/conftest.py
staged path: tests/unit/tools/test_spec_review_requestor_acceptance/test_spec_review_requestor_acceptance_tdd.py
staged path: tests/unit/tools/test_spec_review_requestor_acceptance/test_spec_review_requestor_io_acceptance_tdd.py
staged path: tests/unit/tools/test_spec_reviewer_acceptance/conftest.py
staged path: tests/unit/tools/test_spec_reviewer_acceptance/fixtures.py
staged path: tests/unit/tools/test_spec_reviewer_acceptance/test_spec_reviewer_recovery_tdd.py
staged path: tools/code_review_answer_cli.py
staged path: tools/code_review_evidence.py
staged path: tools/code_review_request.py
staged path: tools/prompt_workflow_code_review.py
staged path: tools/prompt_workflow_review.py
staged path: tools/review_artifact_configuration.py
staged path: tools/review_artifact_migration.py
staged path: tools/review_artifact_registry.py
staged path: tools/review_exchange_cli.py
staged path: tools/review_exchange_models.py
staged path: tools/review_exchange_paths.py
staged path: tools/review_status.py
staged path: tools/spec_review_answer_cli.py
staged path: tools/spec_review_request.py
```

### Requestor assessment for step 1 review-resume-command (round 2)

Step 1 is implemented across the complete staged patch and is ready for another independent review. The round-1 repairs were retained, then tightened where the plan required a single configured artifact home rather than temporary repository-root compatibility. The complete staged tree, including the reviewer-authored repairs and the writer follow-up, has been assessed rather than only the newly edited files.

The staged patch now keeps runtime artifact discovery separate from transcript handling, validates caller-owned renderer files against the configured artifact home, accepts numeric and named implementation substeps such as `4A`, and avoids the review-model/placement import cycle. The validation-plan overview and accepted file-size variances now match the implemented state.

The commit plan contains five groups and validates exactly against all 58 staged paths. `.agents` is clean, and `git diff --cached --check` is clean after LF normalization.

### Implementation report for step 1 review-resume-command (round 2)

Implemented the Step 1 review-artifact-home foundation and migration behavior, including configuration parsing, registered artifact naming, bounded placement discovery, migration planning, CLI integration, and acceptance/unit coverage.

Integrated the artifact configuration into code/spec request and answer renderers, exchange/status paths, and prompt-workflow launchers. Caller-owned inputs and outputs must now be direct children of the configured artifact home; invalid configuration fails closed.

Separated repository-aware artifact placement from the exchange data model by adding a path-layer configuration loader. Extended retained-manifest identity parsing to numeric and named substeps, including `4A`.

Migrated review fixtures to `.reviews`, used byte-exact ignore fixtures where Windows newline translation would invalidate the contract, corrected validation documentation, and retained the reviewer’s protocol transcript and commit-plan amendments.

Validation completed successfully:

- `ghog affected --no-cov`: fail=0, warn=0, xfail=0, exit=0.
- Focused slow-test recheck after bounding Hypothesis to 40 examples: 0.08 seconds versus 0.54 seconds before; assertions and strategies preserved.
- `ghog single tests/unit/tools/test_review_artifact_home/test_review_artifact_registry_pbt.py`: fail=0, warn=0, xfail=0, exit=0.
- Final `ghog day`: fail=0, warn=0, xfail=3, cov=100, outliers=0, excluded=0, exit=0.
- `python -m tools.commit_plan_check --format json` in the project environment: state=valid, ready=true, diagnostics empty.
- `git diff --cached --check`: exit 0.

### Change summary for step 1 review-resume-command (round 2)

Round 2 retains the substantive round-1 reviewer repairs and adds the writer follow-up needed to align them with the approved Step 1 design.

The writer removed temporary repository-root caller-file compatibility, made invalid artifact-home declarations fail closed, broadened retained-manifest step parsing to named substeps, and broke the model/placement import cycle. Tests and fixtures now exercise the `.reviews` home-only rule, including exact ignore-file bytes. Documentation now reports the correct Step 0/Step 1 state and the two accepted line-budget variances.

The property test identified as a Groundhog duration outlier was profiled and bounded to 40 generated examples without changing its strategy space or assertions. The final full gate is green at 100 percent coverage with no outliers.

### Writer response for step 1 review-resume-command (round 2)

Writer response: Accepted the round-1 changes-requested disposition and all substantive reviewer repairs.

For caller-file placement, the final behavior is home-only: `caller_file_parents` returns only the configured artifact home and invalid declarations return no permitted parents. Repository-root compatibility was intentionally removed because the Step 1 contract establishes `.reviews` as the default home.

For retained-manifest identities, the registry now accepts the plan’s full implementation-step alphabet, including named substeps such as `4A`, while rejecting traversal-shaped values.

For architecture, `ReviewConfiguration.load` is again a data-model parser. Repository-aware artifact configuration and review-mode marker resolution now live in `review_exchange_paths.load_review_configuration`, removing the import cycle while sharing the validated configuration with callers.

For documentation, the validation overview now states that Step 0 is complete, Step 1 is implemented and under review, and Steps 2 through 6 remain pending. The accepted Step 1 line-count variances are recorded for the 635-line migration module and 632-line migration test module; all Step 1 files remain below the 650-line hard limit.

For whole-patch readiness, the complete staged set was LF-normalized, checked for whitespace, checked for `.agents` contamination, validated against the five-group commit plan, and rerun through the full Groundhog gate. No disagreement is raised.

### Reviewer focus for step 1 review-resume-command (round 2)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-1-round-2 -->

## Round 2 by reviewer - Step 1

- Recorded: 2026-09-02T12:38:50+02:00
- Exchange: code/code/v0.11.0/review-resume-command
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-resume-command.md
- Implementation step: 1
- Outcome: answer

### Assessed index identity for step 1 review-resume-command (exchange 1) (round 2)

Baseline index tree: f302c7b08b233c9a897fcd4756eecbd6172bb4b8

Assessed index tree: a6f454c7f1d2bc5655df242e63814219babfcee3

### Implementation check for step 1 review-resume-command (exchange 1) (round 2)

Result: Yes. Step 1 is fully implemented in the reviewed state, and every round-1
finding is closed.

The three round-1 code findings are resolved, and each was verified against the
code rather than the writer response.

`ReviewArtifactRegistry._STEP` is now `[A-Za-z0-9][A-Za-z0-9._-]*`, character
for character the same alphabet `code_review_evidence._TOKEN_RE` validates. The
registry and the only producer of retained-manifest names can no longer
disagree, which is the actual defect behind the step-0 rejection. Numeric steps
and named substeps such as `4A` both render and parse, and a leading dot is
still refused, so no traversal-shaped value is admitted.

`caller_file_parents` returns only the configured artifact home and fails
closed to an empty set when the declaration is invalid. All five request,
answer, and exchange launchers resolve caller paths through it, and the
prompt-workflow launchers route review-mode loading through the same boundary.
This answer was authored, rendered, and published entirely from `.reviews`,
which exercises the repaired path end to end rather than asserting it.

The import cycle is genuinely broken rather than hidden. `ReviewConfiguration`
is a data-model parser again, taking an optional resolved `review_mode_path`,
while `review_exchange_paths.load_review_configuration` owns the
repository-aware lookup through `ReviewArtifactLocator`. No deferred import
remains and the model no longer knows about the artifact home.

The three documentation findings are closed too. The theme sentence now reads
that Step 0 is complete and Steps 1 through 6 remain pending, which is both
accurate and consistent with the per-step sections. The two accepted
line-budget variances are recorded in the Step 1 rows.

Every Step 1 completion criterion holds. The focused command reports
`fail=0 warn=0 xfail=3 exit=0`. The runtime-path bypass search finds one hit,
inside the migration implementation's own default-home scan, which the criterion
exempts. `ghog day` reports `exit=0` across check, affected, and full, with the
full phase at `fail=0 warn=0 xfail=3 cov=100 outliers=0 excluded=0`. Every Step
1 file stays under the 650-line ceiling: migration 635, registry 301,
configuration 184, paths 229, models 562, status 557, and the migration test
module 632.

Architecture, performance, and coverage all hold. Placement, naming, migration,
and configuration stay out of the exchange store; migration discovery is `O(n)`
across three flat locations with dictionary collision detection and no status
projection; and status still loads one artifact configuration per invocation.

Validation plan effects: The reviewer wrote only Step 1 rows of
`docs/v0.11.0/plan.v0.11.0.review-resume-command.validation.md`:

- the status sentence changed from `No. Step 1 has NOT been fully implemented.`
  to `Yes. Step 1 has been fully implemented.` with a summary matching the
  verified state;
- the stale `Missing work for Step 1` section was removed, because all six of
  its items are closed and leaving it would read as pending work;
- `Architecture check for Step 1` records the resolved import cycle and now
  closes with an explicit no;
- `Unit test coverage check for Step 1` records the `_STEP` and `_TOKEN_RE`
  parity, the home-only caller coverage, and the bounded property test;
- `Feature integrity for Step 1` records all three impairments as resolved and
  lists the completion-criterion evidence.

The document-level status line stays `No, it is not implemented.`, which is
correct: Steps 2 through 6 are still pending, so the final-step flip does not
apply. No umbrella row was touched, and no other section of the document was
edited.

### Pre-repair mandatory checks and coverage for step 1 review-resume-command (exchange 1) (round 2)

Baseline evidence was captured before any assessment.

- `capture-index-tree` returned `f302c7b08b233c9a897fcd4756eecbd6172bb4b8`,
  equal to the `request_index_tree` in the round-2 request, so the received
  state matched the requested state and no early rejection applied.
- `read-manifest` reported no retained manifest for this identity and step,
  because round 1 retired it after publication. This round therefore ran as a
  fresh assessment with a new baseline rather than reusing cached findings.
- `umbrella-digest capture` returned
  `bb71aaf68bb45d395e719881a86817a146eba8f164e06a09433fb375914ddc81`.
- `validation-state capture` recorded the ordered union of the 58 staged step
  paths and the known ghog artifacts `coverage.xml`, `.coverage`, `a.ghog.log`,
  and `a.ghog.senv.log`: 58 tracked files plus the ignored `.coverage` and
  `a.ghog.log`.
- `write-manifest` stored that baseline before any mutation.
- `record-pre-repair-blob` captured
  `docs/v0.11.0/plan.v0.11.0.review-resume-command.validation.md` at
  `8c9c0f2d0dd37d14e2f3be449fecc31ad2fa559e` before its only edit.

### Resolved validation set and sources for step 1 review-resume-command (exchange 1) (round 2)

The reviewer ran the union of the request validation set and the current
resolver set. Both resolve to the same two mandatory commands, and the reviewer
ran each independently rather than accepting the requestor's reported results.

- `ghog single tests/unit/tools/test_review_resume_perf/test_review_resume_perf_tdd.py tests/unit/tools/test_review_artifact_home tests/unit/tools/test_review_exchange_paths tests/unit/tools/test_review_exchange_store/test_review_exchange_store_validation_tdd.py`,
  source plan. Result: `fail=0 warn=0 xfail=3 exit=0`.
- `ghog day`, source project. Result: `exit=0`. Check `exit=0`,
  `affected --no-cov` `exit=0`, and full
  `fail=0 warn=0 xfail=3 cov=100 outliers=0 excluded=0 exit=0`. The run was
  forced, because the walk had already recorded a green state and would
  otherwise have skipped.

The three remaining xfails are the Step 5 global-wait gates, which Step 5 owns.
No mandatory evidence was unavailable, and `.agents` stayed clean across the
walk, so the round-1 contamination did not recur.

### Resolver drift and direction for step 1 review-resume-command (exchange 1) (round 2)

No resolver drift. The request-time validation set and the set resolved during
this round both contain exactly `ghog day` from the project source and the
focused `ghog single` command from the plan source, in the same order and with
the same arguments. The union the reviewer ran is identical to the request set.

### Repository state around validation for step 1 review-resume-command (exchange 1) (round 2)

The received index tree `f302c7b08b233c9a897fcd4756eecbd6172bb4b8` matched the
request-time index tree exactly, so the assessment ran against the requested
state. After the reviewed-step validation rows the assessed index tree is
`a6f454c7f1d2bc5655df242e63814219babfcee3`.

The umbrella digest is unchanged:
`bb71aaf68bb45d395e719881a86817a146eba8f164e06a09433fb375914ddc81` before and
after, `changed: false`. No boundary violation.

`validation-state compare` over the ordered path set reports one tracked
difference, `docs/v0.11.0/plan.v0.11.0.review-resume-command.validation.md`,
plus the ignored `a.ghog.log` that the validation commands rewrite. There is no
tracked validation side effect, no untracked difference, and no change outside
the reviewed-step rows.

The worktree is otherwise clean. `git status --porcelain` shows only the staged
set and the transcript, whose unstaged content is the round-2 request entry the
protocol itself appended. The 66 contaminated `.agents/llm-shared/**` files
reverted during round 1 have not returned: `git status --porcelain -- .agents`
is empty both before and after the full walk.

### Repair inventory for step 1 review-resume-command (exchange 1) (round 2)

Repairs made:

- docs/v0.11.0/plan.v0.11.0.review-resume-command.validation.md - review metadata: flip the Step 1 status sentence to Yes, remove the stale `Missing work for Step 1` section, and update the architecture, coverage, and feature-integrity rows to the verified state

Paths staged:

- ﻿docs/v0.11.0/plan.v0.11.0.review-resume-command.validation.md
- docs/v0.11.0/review.code.v0.11.0.review-resume-command.md
- instructions/review-requestor.md
- instructions/spec-reviewer.md
- tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/test_commit_plan_check_acceptance_tdd.py
- tests/acceptance/review_status/test_review_status_acceptance/test_review_status_acceptance_tdd.py
- tests/unit/tools/git_test_double.py
- tests/unit/tools/test_code_review_answer/test_code_review_answer_cli_tdd.py
- tests/unit/tools/test_code_review_evidence/conftest.py
- tests/unit/tools/test_code_review_evidence/test_code_review_evidence_boundaries_tdd.py
- tests/unit/tools/test_code_review_evidence/test_code_review_evidence_cli_tdd.py
- tests/unit/tools/test_code_review_request/test_code_review_request_tdd.py
- tests/unit/tools/test_code_review_request_commit_plan/test_code_review_request_commit_plan_tdd.py
- tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_io_acceptance_tdd.py
- tests/unit/tools/test_code_reviewer_acceptance/conftest.py
- tests/unit/tools/test_code_reviewer_acceptance/fixtures.py
- tests/unit/tools/test_code_reviewer_acceptance/test_code_reviewer_recovery_tdd.py
- tests/unit/tools/test_prompt_workflow_code_review/test_prompt_workflow_code_review_tdd.py
- `tests/unit/tools/test_review_artifact_home/__init__.py`
- tests/unit/tools/test_review_artifact_home/test_review_artifact_configuration_tdd.py
- tests/unit/tools/test_review_artifact_home/test_review_artifact_migration_boundaries_tdd.py
- tests/unit/tools/test_review_artifact_home/test_review_artifact_migration_tdd.py
- tests/unit/tools/test_review_artifact_home/test_review_artifact_registry_pbt.py
- tests/unit/tools/test_review_artifact_home/test_review_artifact_registry_tdd.py
- tests/unit/tools/test_review_exchange_acceptance/conftest.py
- tests/unit/tools/test_review_exchange_acceptance/test_review_exchange_acceptance_tdd.py
- tests/unit/tools/test_review_exchange_cli/test_review_exchange_cli_boundaries_tdd.py
- tests/unit/tools/test_review_exchange_cli/test_review_exchange_cli_tdd.py
- tests/unit/tools/test_review_exchange_lifecycle/test_review_exchange_boundaries_tdd.py
- tests/unit/tools/test_review_exchange_lifecycle/test_review_exchange_lifecycle_recovery_tdd.py
- tests/unit/tools/test_review_exchange_models/test_review_exchange_models_tdd.py
- tests/unit/tools/test_review_exchange_paths/test_review_exchange_paths_tdd.py
- tests/unit/tools/test_review_exchange_state/test_review_exchange_state_tdd.py
- tests/unit/tools/test_review_exchange_store/test_review_exchange_store_validation_tdd.py
- tests/unit/tools/test_review_resume_perf/test_review_resume_perf_tdd.py
- tests/unit/tools/test_review_status/test_review_status_tdd.py
- tests/unit/tools/test_spec_review_answer/test_spec_review_answer_cli_tdd.py
- tests/unit/tools/test_spec_review_request/test_spec_review_request_tdd.py
- tests/unit/tools/test_spec_review_requestor_acceptance/conftest.py
- tests/unit/tools/test_spec_review_requestor_acceptance/test_spec_review_requestor_acceptance_tdd.py
- tests/unit/tools/test_spec_review_requestor_acceptance/test_spec_review_requestor_io_acceptance_tdd.py
- tests/unit/tools/test_spec_reviewer_acceptance/conftest.py
- tests/unit/tools/test_spec_reviewer_acceptance/fixtures.py
- tests/unit/tools/test_spec_reviewer_acceptance/test_spec_reviewer_recovery_tdd.py
- tools/code_review_answer_cli.py
- tools/code_review_evidence.py
- tools/code_review_request.py
- tools/prompt_workflow_code_review.py
- tools/prompt_workflow_review.py
- tools/review_artifact_configuration.py
- tools/review_artifact_migration.py
- tools/review_artifact_registry.py
- tools/review_exchange_cli.py
- tools/review_exchange_models.py
- tools/review_exchange_paths.py
- tools/review_status.py
- tools/spec_review_answer_cli.py
- tools/spec_review_request.py

### Commit plan assessment for step 1 review-resume-command (exchange 1) (round 2)

The reviewer reran `python -m tools.commit_plan_check --format json`
independently against the received repository state, before assessing grouping,
and again after writing the reviewed-step validation rows.
`bin/commit_plan_check.bat` still does not exist, so the shipped module was
invoked directly; it is the same checker the launcher will wrap when umbrella
row 8 lands, and its absence is a gap in the launcher surface rather than in
this step.

Both runs returned `state: valid`, `ready: true`, exit `0`, an empty
`diagnostics` list, and 58 staged paths across five groups in dependency order:

1. `feat(review): add configurable artifact home`
2. `feat(review): enforce caller files in the artifact home`
3. `docs(review): require the artifact home for caller files`
4. `docs(review-resume-command): record step 1 review`
5. `docs(review-resume-command): record step 1 validation`

The two groups the reviewer added in round 1 survive with the writer's
tightened subject and body, and group 1 no longer claims the answer-CLI paths
that belong to group 2. The reviewer's only edit this round lands in
`docs/v0.11.0/plan.v0.11.0.review-resume-command.validation.md`, already
group 5, so staged membership, ordering, scope, and the conventional subjects
still match the staged work and `a.commit` needed no amendment.

The mechanical result satisfies only the `a.commit` part of the readiness
floor. It proves nothing about completeness, validation, or coverage, and it
authorizes no commit.

### Findings and boundaries for step 1 review-resume-command (exchange 1) (round 2)

Unresolved findings: None.

Boundary-crossing work: None.

### Writer instructions for step 1 review-resume-command (exchange 1) (round 2)

No changes are requested. The recommendation is advisory and authorizes no
commit; the human owns that decision at the convergence gate.

Two things are worth carrying forward rather than acting on now.

Re-check `git status --porcelain -- .agents` immediately before committing. An
external plugin sync rewrote 66 tracked files with machine-specific absolute
redirects during round 1, and the commit handoff stages the whole tree with
`git add -A`. The drift has not recurred across two full walks, so this is a
confirmation step rather than a known problem.

`bin/commit_plan_check.bat` still does not exist, so both roles invoke
`python -m tools.commit_plan_check` directly even though
`instructions/code-reviewer.md` names the launcher. That is umbrella row 8 and
belongs to its own effort, not to Step 1.

### Decision rationale for step 1 review-resume-command (exchange 1) (round 2)

The disposition is `commit-ready`, and the readiness floor is complete on all
six results.

Identity is exact. The received index tree equalled the request-time tree, the
human-readable identity agrees with the envelope, the named step exists in the
plan, the round is positive and reviewer-owned, and the umbrella digest is
unchanged.

Implementation is complete. Every Step 1 completion criterion holds, and every
round-1 finding is closed in the code rather than in prose: `_STEP` and
`_TOKEN_RE` are now the same alphabet, `caller_file_parents` is home-only and
fails closed, and the model/placement import cycle is broken by moving
review-mode resolution into the path layer.

Validation and coverage are proven. The reviewer ran both mandatory commands
independently: the focused command at `exit=0`, and `ghog day` at `exit=0` with
the full phase at `cov=100`, `fail=0`, `warn=0`, `outliers=0`, and the three
Step 5 xfails that Step 5 owns.

Staged scope is attributable. The only reviewer edit is the reviewed-step
validation rows, proved cleanly attributable before staging, with no tracked
validation side effect and no change outside those rows.

No findings are unresolved. Every round-1 item is closed, and this round found
nothing new that blocks.

`a.commit` is accurate. The independent rerun returns valid, ready, and empty
diagnostics across five groups and 58 staged paths.

This round made no substantive repair. The single edit is validation-plan rows
for the reviewed step, which the contract classifies as review metadata, so
`commit-ready` is available in this round rather than requiring another one.

One judgment is recorded rather than treated as a blocker. The registry property
test is now bounded to 40 generated examples to clear a duration outlier. The
strategy space and assertions are unchanged, so the cost is search depth, not
coverage, and the round-trip property remains exercised on every run.

The recommendation is advisory. It does not authorize a commit, and the human
owns the convergence gate.

### Final reviewer decision for step 1 review-resume-command (exchange 1) (round 2)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-1-round-2 -->

## Round 2 by human - Step 1 - human-confirmation

- Recorded: 2026-09-02T15:45:19+02:00
- Exchange: code/code/v0.11.0/review-resume-command
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-resume-command.md
- Implementation step: 1
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-2 -->
