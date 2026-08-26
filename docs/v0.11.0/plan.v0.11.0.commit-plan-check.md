# v0.11.0 commit-plan-check implementation plan -- read-only readiness evidence

Implement one typed, read-only commit-plan check and use it as the shared
mechanical readiness floor for commit grouping and code review.

- **Shared inventory parity**: checking and committing consume the same exact
  staged-path inventory.
- **One checker contract**: the batch launcher and Python module render one
  immutable result with stable statuses and diagnostics.
- **Review enforcement**: request publication fails closed, while reviewers
  independently rerun the same command before assessing readiness.

> Markdown lint note: never leave a space immediately inside an inline code
> span (MD038); when a snippet starts or ends with a space, write that space as
> the literal token `[space]`. End any line that would be only italic text with
> a period after the closing underscore (MD036).

## Plan goal for v0.11.0 commit-plan checking

Implement the complete contract from
`docs/v0.11.0/design.v0.11.0.commit-plan-check.md` and its related feature
request in four ordered implementation steps.

- **Step 1 goal**: extract one public staged-inventory boundary and preserve
  exact batch-workflow behavior.
- **Step 2 goal**: add the immutable checker service, human and JSON renderers,
  Python CLI, and focused root launcher.
- **Step 3 goal**: enforce checker success and stable index identity before
  code-review request artifacts can be rendered.
- **Step 4 goal**: wire the canonical reviewer and grouping instructions and
  prove launcher parity, failure taxonomy, and repository immutability with
  acceptance tests.

No Step 0 timeout gate is required. This feature has no model call, network
wait, event loop, or background timing target; its performance contract is
bounded exact-file and Git-index IO. Step 4 provides the larger acceptance
coverage needed to prove that contract without an artificial time-based
`xfail`.

---

## Scope anchors for the v0.11.0 commit-plan-check plan

This plan implements the design from
`docs/v0.11.0/design.v0.11.0.commit-plan-check.md` and the confirmed rules in
`docs/v0.11.0/feature-request.v0.11.0.commit-plan-check.md`, targeting these
outcomes:

1. One shared staged inventory preserves `--no-renames` and NUL-delimited path
   semantics for both checking and committing.
2. One immutable checker result carries readiness state, typed groups, exact
   staged paths, and deterministic diagnostics to both output formats.
3. Code-review request rendering cannot publish unchecked or index-drifting
   evidence, and reviewer/grouping instructions use the same command.

The following are explicitly **in scope**:

- `commit-plan-check.bat` and `python -m tools.commit_plan_check` over one
  service function.
- Distinct ready, non-ready, and operational outcomes using statuses `0`, `3`,
  and `2`.
- Human and JSON projections of the same typed result.
- Requestor-side enforcement, reviewer-side independent checking, and grouped
  commit workflow use.
- Unit and acceptance evidence for successful, invalid, missing, empty,
  rename, operational-failure, index-drift, and no-mutation cases.

The following remain deferred beyond this effort:

- Repairing or rewriting `a.commit` from checker diagnostics.
- Mutation or commit flags on the checker.
- Support for `--root-a-commit --dry-run` in the committing launcher.
- Active-review status and interrupted-review resumption.
- Reviewer-specific staged-path filtering or worktree readiness rules.

---

## Complexity bound clarification for v0.11.0 commit-plan checking

- **O(1) amortized per path or group insertion**: new orchestration stores and
  projects parsed groups, staged paths, and diagnostics without nested
  membership scans.
- **O(n) total outside the reused validator**: root-plan parsing, NUL-delimited
  inventory decoding, result projection, and rendering are linear in plan
  content plus staged membership.
- **Existing mismatch reporting remains bounded**: the public validator may
  sort path differences for deterministic diagnostics, producing its existing
  `O(n log n)` invalid-result path; the checker must not add another sort or a
  nested pass.

There is no request-response hot path. No new code path may introduce
quadratic work, per-path subprocesses, or repeated parsing of the same plan.

---

## File-based IO cost clarification for v0.11.0 commit-plan checking

- Root discovery performs only a bounded parent lookup.
- Each checker call reads exactly `<root>/a.commit` once and runs the single
  shared Git index inventory once.
- Parsing, validation, and human or JSON rendering reuse one in-memory result;
  neither renderer scans files or reloads metadata.
- The requestor gate captures the index tree before and after the checker, then
  writes paired artifacts only after a ready result and identical trees.
- The checker itself performs no staging, reset, repair, evidence-file, or
  commit write.

The loading phase is therefore a tiny exact-plan and index-read operation, not
a documentation-tree or repository-file scan.

---

## Confirmed technical facts for v0.11.0 plan viability

Physical line counts include blank lines and use the same per-line iteration
metric as the repository big-file scan.

**Files over the 650-line repository planning limit**:

- None of the existing Python files planned for modification is over 650
  lines.

**Files in the 550-through-650 risk band**:

- `tests/unit/tools/test_code_review_request/test_code_review_request_tdd.py`:
  **550 lines**. Limit changes to the shared source fixture and existing
  assertions; place checker-specific cases in a new focused test leaf.

**Files below 550 and safe to extend**:

- `tools/git_batch_commit_workflow.py`: **484 lines**; extracting inventory is
  expected to keep or reduce its size.
- `tests/unit/tools/test_git_batch_commit_workflow_process.py`: **353 lines**.
- `tools/code_review_request.py`: **497 lines**; keep checker orchestration and
  evidence wiring compact so the file remains below the 550 risk band when
  practical.
- `tests/unit/tools/test_code_reviewer_acceptance/fixtures.py`: **281 lines**.
- `tests/unit/tools/test_code_reviewer_acceptance/test_code_reviewer_acceptance_tdd.py`:
  **362 lines**.
- `tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_acceptance_tdd.py`:
  **479 lines**.
- `tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_io_acceptance_tdd.py`:
  **281 lines**.
- `tests/unit/tools/test_code_reviewer_instruction/test_code_reviewer_instruction_tdd.py`:
  **118 lines**.
- `tests/unit/tools/test_group_commit_message_prompt_tdd.py`: **173 lines**.

**What does not exist yet**:

- `tools/commit_plan_support.py`.
- `tools/commit_plan_check.py`.
- `commit-plan-check.bat`.
- Focused unit leaves for commit-plan support, checker behavior, and
  code-review request checker integration.
- The commit-plan-check acceptance package and acceptance test leaf.

**Other confirmed facts affecting implementation**:

- `tools/git_batch_commit_validation.py` is 102 lines and already exports the
  side-effect-free `validate_commit_plan(blocks, staged_paths)` authority.
- `tools/git_batch_commit_models.py` is 151 lines and already owns immutable
  `CommitPlanGroup` and `CommitPlanValidation` values.
- `tools/git_batch_commit_git.py` is 479 lines and owns the cross-platform Git
  command wrapper used by the current inventory helper.
- `tools/git_batch_commit_workflow.py::_staged_paths` currently runs
  `git diff --cached --name-only --no-renames -z` but is not public.
- `tools/git_batch_commit_parsing.py::parse_clipboard_content` is public,
  exported in that module's `__all__`, and accepts content plus
  `interactive=False`; it is the parsing seam that preserves direct
  missing-file, empty-file, and unreadable-file classification in the checker.
- `tools/git_batch_commit_workflow.py::_read_and_parse_content` also accepts
  `interactive=False`, but it belongs to the committing workflow, includes
  clipboard and logging behavior, and collapses missing, empty, and read
  failures into `GitBatchCommitError`; it is not the read-only checker seam.
- `tools/code_review_request.py` already captures the request index tree and
  renders typed JSON and human evidence before writing paired artifacts.
- `markdown-check.bat` demonstrates the repository-root launcher pattern for a
  platform-neutral Python module.

---

## Current test-tree validation snapshot for v0.11.0 commit-plan checking

Existing test areas that must remain green:

- `tests/unit/tools/test_git_batch_commit_workflow_process.py` covers the
  current exact staged inventory and validator delegation.
- `tests/unit/tools/test_git_batch_commit_validation/` covers group ordering,
  conventional subjects, path normalization, duplicates, and exact membership.
- `tests/unit/tools/test_code_review_request/` covers typed code-review evidence
  and paired request rendering; its 550-line test file is already at risk.
- `tests/unit/tools/test_code_review_requestor_acceptance/` covers requestor
  rendering and publication-oriented IO boundaries.
- `tests/unit/tools/test_code_reviewer_acceptance/` covers the reviewer-facing
  request evidence flow.
- Canonical instruction contract tests cover `instructions/code-reviewer.md`
  and `instructions/group-commits-msg.md`.

New test leaf directories to create:

- `tests/unit/tools/test_commit_plan_support/`.
- `tests/unit/tools/test_commit_plan_check/`.
- `tests/unit/tools/test_code_review_request_commit_plan/`.
- `tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/`.

Property-based tests are not required. The feature has a finite failure
taxonomy and exact subprocess, path-order, status, and rendering contracts;
parameterized examples and real-repository acceptance fixtures provide the
stronger evidence. Existing validator tests continue to own path-rule breadth.

---

## Shared execution command checklist for all v0.11.0 commit-plan-check steps

Apply this checklist to every numbered step using its exact file list.

1. Count physical lines before edits for every step file.
2. Add or update the step's tests before production or instruction behavior.
3. Run `ghog single` on the exact affected test files.
4. Run the step-specific `rg` checks for public names, Git arguments, status
   mapping, evidence fields, or instruction wiring.
5. Run `ghog day` repeatedly until it reports the objective with `exit=0`.
6. Count physical lines after edits and compare every Python file with its
   baseline, policy band, advisory estimate, and 650-line ceiling.
7. If a Python file exceeds 650 lines, stop and apply the step's responsibility
   split before committing.
8. If a file exceeds only an advisory estimate while remaining at or below
   650, record the variance as evidence without failing the step.

## Ready-to-run commands for all v0.11.0 commit-plan-check steps

- Physical line count: `(Get-Content -LiteralPath '<path>').Count`
- Targeted tests: `ghog single <step-test-files>`
- Grep checks: `rg -n '<step-pattern>' <step-paths>`
- Shared gate loop: `ghog day`, repeated fix-and-walk until it reports the
  objective with `exit=0`

---

## Numbered implementation steps for v0.11.0 commit-plan checking

### Step 1. Share exact staged-path inventory with the committing workflow

#### Step 1 analysis and intent for staged inventory parity

Issues to address:

- Exact inventory is trapped in the private workflow helper
  `_staged_paths(root)`.
- A second implementation would risk diverging on NUL parsing, rename sides,
  deletions, whitespace, or path ordering.

Fix intent:

- Extract the existing Git invocation and decoding into one neutral public
  support function.
- Keep a compatibility delegate in the batch workflow where current imports
  and tests require it, while making both flows consume the public function.

Expected outcome:

- Batch validation and read-only checking receive identical repository-relative
  staged paths from the same implementation.
- The batch workflow's validation and commit behavior remains unchanged.

Step framing:

- Design link: “Shared staged inventory for commit-plan parity.”
- Complexity impact: one Git call and one linear NUL-delimited decode; no
  per-path filesystem checks.
- Feature preservation: existing root-plan validation, rename semantics, and
  commit execution stay intact.
- Execution checklist reference: “Shared execution command checklist for all
  v0.11.0 commit-plan-check steps” and its ready-to-run commands.

#### Step 1 implementation for staged inventory parity

**Files involved**:

- `tools/commit_plan_support.py` (new, to be created).
- `tools/git_batch_commit_workflow.py` (existing, to be updated).
- `tests/unit/tools/test_commit_plan_support/__init__.py` (new, to be created).
- `tests/unit/tools/test_commit_plan_support/test_commit_plan_support_tdd.py`
  (new, to be created).
- `tests/unit/tools/test_git_batch_commit_workflow_process.py` (existing, to be
  updated).

**Tests first**:

- Add focused tests that assert the exact Git argument tuple, repository root,
  capture/encoding options, NUL decoding, whitespace preservation, deletion
  membership, and two-path rename behavior.
- Update the workflow test to prove its compatibility helper delegates to the
  shared inventory and the public validator still receives that result.
- No PBT is needed; exact command and byte-decoding examples cover the bounded
  contract.

**Classes and behavior**:

- `staged_paths(root)`: run the existing cross-platform Git command exactly
  once and return the ordered nonempty path tuple.
- `git_batch_commit_workflow._staged_paths(root)`: remain a thin compatibility
  delegate with no inventory policy of its own.
- `_validate_commit_plan_for_root`: continue passing the shared inventory to
  the unchanged public validator before any mutation.

**Completion criteria**:

- `ghog day` reports the objective with `exit=0`.
- `rg -n "staged_paths|--no-renames|-z|validate_commit_plan" tools/commit_plan_support.py tools/git_batch_commit_workflow.py tests/unit/tools/test_commit_plan_support tests/unit/tools/test_git_batch_commit_workflow_process.py`
  shows one Git inventory implementation and explicit delegation coverage.
- Existing batch commit tests prove no commit-path behavior changed.

#### Step 1 addendums for staged inventory parity

Line-budget checkpoint:

- `tools/commit_plan_support.py`: before 0; below-550 safe; repository ceiling
  650; expected at or below 80 lines (advisory).
- `tools/git_batch_commit_workflow.py`: before 484; below-550 safe; repository
  ceiling 650; expected at or below 490 lines (advisory, with extraction
  expected to offset delegation changes).
- `tests/unit/tools/test_commit_plan_support/__init__.py`: before 0; below-550
  safe; repository ceiling 650; expected at or below 5 lines (advisory).
- `tests/unit/tools/test_commit_plan_support/test_commit_plan_support_tdd.py`:
  before 0; below-550 safe; repository ceiling 650; expected at or below 180
  lines (advisory).
- `tests/unit/tools/test_git_batch_commit_workflow_process.py`: before 353;
  below-550 safe; repository ceiling 650; expected at or below 370 lines
  (advisory).

Split guidance:

- If the new support module approaches the risk band, keep only Git inventory
  and decoding there; do not move parser, validator, renderer, or commit logic
  into it.
- If the workflow file would exceed 650, extract another existing workflow
  responsibility rather than growing the staged-inventory delegate.

Full workflow timing run readiness:

- `ghog single tests/unit/tools/test_commit_plan_support/test_commit_plan_support_tdd.py tests/unit/tools/test_git_batch_commit_workflow_process.py`
- `ghog day`

Time-gated status for Step 1:

- No Step 0 perf gate is affected; exact one-call inventory behavior is covered
  by focused assertions.

---

### Step 2. Expose one typed read-only checker through both entry points

#### Step 2 analysis and intent for checker evidence

Issues to address:

- No public command orchestrates exact root-plan parsing, shared staged
  inventory, and the existing validator without entering commit execution.
- Human reviewers and automation lack stable equivalent projections and the
  required `0`/`3`/`2` status taxonomy.

Fix intent:

- Add one immutable checker-specific result around the unchanged public
  validator result and input-state taxonomy.
- Run the service once per invocation, then select the human or JSON renderer.
- Add the root batch launcher and module CLI over the same `main` and service.

Expected outcome:

- Missing plan, empty plan, empty staged set, validator failures, and
  operational failures remain distinguishable.
- Both entry points emit identical ordered evidence without changing Git or
  repository files.

Step framing:

- Design links: “Read-only checker model for commit plans” and “Output
  contracts for commit-plan evidence.”
- Complexity impact: one exact plan read, one inventory call, one parse, one
  validation, and one projection per invocation.
- Feature preservation: the public validator model and committing launcher's
  incompatible root-plan dry-run behavior remain unchanged.
- Execution checklist reference: the shared execution checklist and
  ready-to-run commands in this document.

#### Step 2 implementation for checker evidence

**Files involved**:

- `tools/commit_plan_check.py` (new, to be created).
- `commit-plan-check.bat` (new, to be created).
- `tests/unit/tools/test_commit_plan_check/__init__.py` (new, to be created).
- `tests/unit/tools/test_commit_plan_check/test_commit_plan_check_tdd.py` (new,
  to be created).

**Tests first**:

- Parameterize ready, missing-plan, empty-plan, empty-staged-set, invalid-plan,
  unreadable-plan, Git failure, invalid argument, and unexpected-error cases.
- Assert `interactive=False`, exact use of `staged_paths` and
  `validate_commit_plan`, preservation of ordered typed groups and all
  diagnostics, deterministic human and JSON projections, stdout/stderr
  separation, and statuses `0`, `3`, and `2`.
- Assert the exact structured key set from the design: `schema_version` equal
  to `1`, `state`, `ready`, `staged_paths`, `groups` with `position`, `subject`,
  and `paths`, and `diagnostics`; expected non-readiness must emit this complete
  object to stdout before returning status `3`.
- Exercise `--root`, upward root discovery, default human format,
  `--format human|json`, module-main behavior, and root-launcher delegation.
- No PBT is needed; the finite state matrix is fully parameterized.

**Classes and behavior**:

- `CommitPlanCheckState`: enumerate the stable ready, expected non-ready, and
  operational states confirmed by the design.
- `CommitPlanCheckResult`: immutable groups, diagnostics, staged paths, state,
  and derived readiness with a structured payload projection.
- `check_commit_plan(root)`: resolve `<root>/a.commit`; return `missing-plan`
  when it is absent; read it exactly once and return `empty-plan` when content
  is empty or whitespace; otherwise parse through public
  `parse_clipboard_content(content, interactive=False)`, inventory once, call
  the public validator once, and return typed evidence without writing.
- Human and JSON renderers: project the same result deterministically and keep
  expected non-readiness on stdout.
- `main(argv)`: validate arguments, resolve the root, map result or operational
  failure to the documented stream and status contract.
- `commit-plan-check.bat`: resolve the llm-shared Python environment, run
  `python -m tools.commit_plan_check`, and preserve its exit status.

**Completion criteria**:

- `ghog day` reports the objective with `exit=0`.
- `rg -n "CommitPlanCheck|check_commit_plan|interactive=False|--format|schema_version|return 3|return 2" tools/commit_plan_check.py commit-plan-check.bat tests/unit/tools/test_commit_plan_check`
  confirms the service, projections, and adapter mappings.
- Focused tests prove the service never calls reset, add, rm, commit, or a file
  writer.

#### Step 2 addendums for checker evidence

Line-budget checkpoint:

- `tools/commit_plan_check.py`: before 0; below-550 safe; repository ceiling
  650; expected at or below 360 lines (advisory). The exact plan read and
  missing/empty/unreadable discrimination may exceed this advisory estimate;
  record the variance as evidence rather than treating it as a defect while
  the measured file remains at or below 650.
- `commit-plan-check.bat`: before 0; non-Python launcher; Python ceiling not
  applicable; expected at or below 35 physical lines (advisory).
- `tests/unit/tools/test_commit_plan_check/__init__.py`: before 0; below-550
  safe; repository ceiling 650; expected at or below 5 lines (advisory).
- `tests/unit/tools/test_commit_plan_check/test_commit_plan_check_tdd.py`:
  before 0; below-550 safe; repository ceiling 650; expected at or below 420
  lines (advisory).

Split guidance:

- If `tools/commit_plan_check.py` would exceed 650, split CLI parsing and stream
  rendering into `tools/commit_plan_check_cli.py`, leaving states, result, and
  service orchestration in the original module.
- If the unit test approaches 550, extract launcher and adapter cases into a
  sibling conventional test leaf before adding more cases.

Full workflow timing run readiness:

- `ghog single tests/unit/tools/test_commit_plan_check/test_commit_plan_check_tdd.py`
- `ghog day`

Time-gated status for Step 2:

- No timeout `xfail` is introduced. Focused tests assert bounded call counts;
  Step 4 measures behavior in real temporary repositories.

---

### Step 3. Enforce commit-plan readiness before code-review request rendering

#### Step 3 analysis and intent for requestor publication enforcement

Issues to address:

- Request rendering captures index identity but does not run the authoritative
  commit-plan checker.
- The request evidence cannot prove that its groups and diagnostics describe
  the same index tree that the request publishes.

Fix intent:

- Capture the index tree, run the shared checker, capture the tree again, and
  reject non-ready results or tree drift before rendering or writes.
- Carry the complete structured checker result in the typed code-review
  evidence and derive the human summary from the same value.

Expected outcome:

- Canonical requestor rendering creates neither paired artifact when the plan
  is non-ready, the checker fails operationally, or the index changes.
- Ready request content binds checker evidence, validation commands, and one
  stable request index tree.

Step framing:

- Design link: “Enforced requestor publication gate.”
- Complexity impact: two index-tree captures around one checker invocation;
  rendering remains one in-memory projection.
- Feature preservation: shared exchange publication stays role-neutral, direct
  protocol bypass remains documented, and existing paired-write validation is
  retained.
- Execution checklist reference: the shared execution checklist and
  ready-to-run commands in this document.

#### Step 3 implementation for requestor publication enforcement

**Files involved**:

- `tools/code_review_request.py` (existing, to be updated).
- `tests/unit/tools/test_code_review_request/test_code_review_request_tdd.py`
  (existing, to be updated).
- `tests/unit/tools/test_code_review_request_commit_plan/__init__.py` (new, to
  be created).
- `tests/unit/tools/test_code_review_request_commit_plan/test_code_review_request_commit_plan_tdd.py`
  (new, to be created).
- `tests/unit/tools/test_code_reviewer_acceptance/fixtures.py` (existing, to be
  updated).
- `tests/unit/tools/test_code_reviewer_acceptance/test_code_reviewer_acceptance_tdd.py`
  (existing, to be updated).
- `tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_acceptance_tdd.py`
  (existing, to be updated).
- `tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_io_acceptance_tdd.py`
  (existing, to be updated).

**Tests first**:

- Extend shared request builders with one typed valid checker result and assert
  its full payload and human summary are paired.
- Supply the new required result through the shared fixture used by the six
  existing keyword-based `CodeReviewRoundInput(` construction sites, limiting
  the 550-line rendering test to one fixture-level compatibility change.
- Add focused tests for status-three non-readiness, operational failure,
  before/after index drift, exactly one checker call, complete evidence, and no
  output creation on every rejected path.
- Retain existing tests for distinct inputs and outputs, validation-set
  resolution, envelope identity, and successful paired writes.
- No PBT is needed; typed boundary and failure-order cases are finite.

**Classes and behavior**:

- `CodeReviewRoundInput`: require one typed commit-plan result alongside the
  stable request index tree and resolved validation set; `__post_init__` must
  reject a non-ready result so the public renderer cannot construct request
  content with invalid checker evidence.
- `_CodeReviewEvidence`: include the full structured checker payload and
  derive a quotable summary without reparsing JSON.
- `_render_from_arguments`: capture tree A, run `check_commit_plan`, require a
  ready result, capture tree B, require A equals B, build typed input, render,
  and only then write both outputs. This render path owns command order;
  `CodeReviewRoundInput.__post_init__` owns the separate representability
  invariant for direct public renderer use.
- Existing `render_code_review_request`: continue validating the envelope and
  paired content from a single typed source.

**Completion criteria**:

- `ghog day` reports the objective with `exit=0`.
- `rg -n "commit_plan|check_commit_plan|request_index_tree|capture_index_tree|ready" tools/code_review_request.py tests/unit/tools/test_code_review_request tests/unit/tools/test_code_review_request_commit_plan tests/unit/tools/test_code_reviewer_acceptance tests/unit/tools/test_code_review_requestor_acceptance`
  shows typed evidence, enforcement order, and rejection coverage.
- Every non-ready, operational, or drift case proves that neither output file
  exists or changes.

#### Step 3 addendums for requestor publication enforcement

Line-budget checkpoint:

- `tools/code_review_request.py`: before 497; below-550 safe; repository ceiling
  650; expected at or below 545 lines (advisory). If it enters the risk band,
  avoid further growth and keep checker policy in `tools/commit_plan_check.py`.
- `tests/unit/tools/test_code_review_request/test_code_review_request_tdd.py`:
  before 550; 550-through-650 risk; repository ceiling 650; expected at or
  below 560 lines (advisory). Add only shared fixture/evidence alignment here.
- `tests/unit/tools/test_code_review_request_commit_plan/__init__.py`: before 0;
  below-550 safe; repository ceiling 650; expected at or below 5 lines
  (advisory).
- `tests/unit/tools/test_code_review_request_commit_plan/test_code_review_request_commit_plan_tdd.py`:
  before 0; below-550 safe; repository ceiling 650; expected at or below 260
  lines (advisory).
- `tests/unit/tools/test_code_reviewer_acceptance/fixtures.py`: before 281;
  below-550 safe; repository ceiling 650; expected at or below 290 lines
  (advisory).
- `tests/unit/tools/test_code_reviewer_acceptance/test_code_reviewer_acceptance_tdd.py`:
  before 362; below-550 safe; repository ceiling 650; expected at or below 375
  lines (advisory).
- `tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_acceptance_tdd.py`:
  before 479; below-550 safe; repository ceiling 650; expected at or below 500
  lines (advisory).
- `tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_io_acceptance_tdd.py`:
  before 281; below-550 safe; repository ceiling 650; expected at or below 300
  lines (advisory).

Split guidance:

- Keep new checker-specific request tests in their dedicated leaf. Do not grow
  the existing 550-line rendering test beyond shared fixture compatibility and
  evidence-parity assertions.
- If `tools/code_review_request.py` exceeds 650, extract only commit-plan gate
  sequencing and typed evidence conversion to a focused requestor helper;
  leave envelope and paired rendering in the existing module.

Full workflow timing run readiness:

- `ghog single tests/unit/tools/test_code_review_request/test_code_review_request_tdd.py tests/unit/tools/test_code_review_request_commit_plan/test_code_review_request_commit_plan_tdd.py tests/unit/tools/test_code_reviewer_acceptance/test_code_reviewer_acceptance_tdd.py tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_acceptance_tdd.py tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_io_acceptance_tdd.py`
- `ghog day`

Time-gated status for Step 3:

- No timeout gate is affected. Call-order tests prove bounded index capture and
  checker use before any writes.

---

### Step 4. Roll out shared review guidance and acceptance evidence

#### Step 4 analysis and intent for repository-wide adoption

Issues to address:

- Reviewer instructions currently assess `a.commit` without naming the shipped
  read-only command.
- Grouped-commit guidance reaches the committing batch path without an earlier
  shared read-only readiness result.
- Unit isolation alone cannot prove launcher parity and full Git-state
  immutability in real repositories.

Fix intent:

- Require the code reviewer to rerun the checker and record its mechanical
  evidence without treating success as commit authority.
- Require grouped-commit preparation to run the checker after formatting and
  staging, repairing status-three diagnostics before presenting commit choices.
- Add real-repository acceptance tests for both entry points, all important
  readiness states, rename membership, requestor rejection, and before/after
  state equality.

Expected outcome:

- Requestors, reviewers, and grouped-commit execution share one readiness floor
  while preserving their distinct authority boundaries.
- Successful and failing checker calls demonstrably leave `HEAD`, index,
  worktree, `a.commit`, and ignored-root inventory unchanged.

Step framing:

- Design links: “Independent reviewer readiness check,” “Grouping workflow use
  of the checker,” and “Acceptance cases.”
- Complexity impact: acceptance fixtures use bounded temporary repositories;
  production guidance adds one explicit checker call, not a scan or poll loop.
- Feature preservation: a ready result never authorizes a commit, and the final
  batch workflow still validates again before mutation.
- Execution checklist reference: the shared execution checklist and
  ready-to-run commands in this document.

#### Step 4 implementation for repository-wide adoption

**Files involved**:

- `instructions/code-reviewer.md` (existing, to be updated).
- `instructions/group-commits-msg.md` (existing, to be updated).
- `tests/unit/tools/test_code_reviewer_instruction/test_code_reviewer_instruction_tdd.py`
  (existing, to be updated).
- `tests/unit/tools/test_group_commit_message_prompt_tdd.py` (existing, to be
  updated).
- `tests/acceptance/commit_plan_check/__init__.py` (new, to be created).
- `tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/__init__.py`
  (new, to be created).
- `tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/test_commit_plan_check_acceptance_tdd.py`
  (new, to be created).

**Tests first**:

- Extend instruction contract tests to require the focused launcher, its
  readiness-only meaning, status-three repair behavior, independent reviewer
  rerun, and the prohibition on deriving commit authority from status zero.
- Build temporary Git repositories that run the batch and module entry points
  against valid, missing-plan, empty-plan, empty-staged-set, mismatched, and
  renamed inputs and compare human/JSON evidence and statuses.
- Cover an unreadable plan or failed Git inventory as an operational failure
  with a stable stderr diagnostic and status `2` across both entry points.
- Redirect stdout into a caller-owned ignored root `a.*` evidence file and
  prove the checker remains read-only while the caller owns that write.
- Capture `HEAD`, index tree, staged paths, tracked worktree diff,
  `a.commit` bytes, and ignored root `a.*` inventory before and after valid and
  invalid calls.
- Exercise requestor rendering with invalid checker evidence and index drift to
  confirm no paired artifacts are written.
- No PBT is needed; these are cross-boundary acceptance scenarios with exact
  expected state snapshots.

**Classes and behavior**:

- `instructions/code-reviewer.md`: place `commit-plan-check.bat` in the six-part
  readiness floor, require an independent rerun, and distinguish mechanical
  success from assessment and commit authority.
- `instructions/group-commits-msg.md`: run the read-only checker after canonical
  formatting and staging, repair non-ready diagnostics, then retain the
  authorized committing batch path as the final defensive validation.
- Acceptance fixtures: create deterministic temporary repositories and compare
  complete before/after state snapshots around both adapters.

**Completion criteria**:

- `ghog day` reports the objective with `exit=0`.
- `rg -n "commit-plan-check|status|readiness|never authorizes|independent" instructions/code-reviewer.md instructions/group-commits-msg.md tests/unit/tools/test_code_reviewer_instruction tests/unit/tools/test_group_commit_message_prompt_tdd.py tests/acceptance/commit_plan_check`
  confirms the shared command and authority wording.
- Acceptance tests prove identical service evidence across entry points and
  exact repository-state preservation for successful and failing calls.
- The full feature request acceptance criteria are covered by unit or
  acceptance evidence without invoking commit execution.

#### Step 4 addendums for repository-wide adoption

Line-budget checkpoint:

- `instructions/code-reviewer.md`: before 209; non-Python Markdown; Python
  ceiling not applicable; expected at or below 225 physical lines (advisory).
- `instructions/group-commits-msg.md`: before 119; non-Python Markdown; Python
  ceiling not applicable; expected at or below 135 physical lines (advisory).
- `tests/unit/tools/test_code_reviewer_instruction/test_code_reviewer_instruction_tdd.py`:
  before 118; below-550 safe; repository ceiling 650; expected at or below 145
  lines (advisory).
- `tests/unit/tools/test_group_commit_message_prompt_tdd.py`: before 173;
  below-550 safe; repository ceiling 650; expected at or below 205 lines
  (advisory).
- `tests/acceptance/commit_plan_check/__init__.py`: before 0; below-550 safe;
  repository ceiling 650; expected at or below 5 lines (advisory).
- `tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/__init__.py`:
  before 0; below-550 safe; repository ceiling 650; expected at or below 5
  lines (advisory).
- `tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/test_commit_plan_check_acceptance_tdd.py`:
  before 0; below-550 safe; repository ceiling 650; expected at or below 380
  lines (advisory).

Split guidance:

- If the acceptance test approaches 550 lines, extract repository-state setup
  and snapshot helpers into `tests/acceptance/commit_plan_check/conftest.py`,
  leaving scenarios in the conventional test leaf. The parent-package
  placement is deliberate so later sibling acceptance leaves can share the
  helpers, even though current repository conftests are leaf-level.
- Keep instruction changes limited to command use and authority boundaries;
  do not copy checker implementation details into Markdown.

Full workflow timing run readiness:

- `ghog single tests/unit/tools/test_code_reviewer_instruction/test_code_reviewer_instruction_tdd.py tests/unit/tools/test_group_commit_message_prompt_tdd.py tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/test_commit_plan_check_acceptance_tdd.py`
- `ghog day`

Time-gated status for Step 4:

- No timeout `xfail` is removed. Acceptance evidence records bounded command
  completion through groundhog and proves IO call counts and state equality.

## Open questions for the v0.11.0 commit-plan-check implementation plan

### Q01: Initial checker module granularity

Question description: Step 2 projects `tools/commit_plan_check.py` at no more
than 360 lines and assigns it the immutable result, service orchestration,
renderers, argument parsing, and module entry point. Should implementation keep
that cohesive initial module or split service and CLI responsibilities before
the line budget requires it?

#### BBQ for Q01

The first service counter can hold ordering, preparation, and pickup while the
queue is short, or the kitchen and pickup counter can be separated before any
crowding exists. Separating early clarifies stations but adds handoffs; keeping
one counter is simpler while the workload stays bounded. In this picture: the
service counter is `tools/commit_plan_check.py`, the kitchen is checker
orchestration, the pickup counter is CLI and rendering, and crowding is the
550-line risk band.

#### Options for Q01

- Option 1A: Keep one `tools/commit_plan_check.py` module initially.
  - pro: Minimizes files and keeps the one-service, one-invocation flow easy to
    trace.
  - con: Service and adapter responsibilities share a module until a later
    line-budget split becomes necessary.
- Option 1B: Create `tools/commit_plan_check.py` and
  `tools/commit_plan_check_cli.py` in Step 2.
  - pro: Separates orchestration data from argument and stream handling from
    the start.
  - con: Adds a module and import boundary despite the current 360-line
    advisory estimate.
- Option 1C: Create a `tools/commit_plan_check/` package with model, service,
  renderer, and CLI modules.
  - pro: Gives every responsibility an explicit file boundary.
  - con: Multiplies files, package initializers, tests, and navigation for a
    focused command.

#### Recommended option for Q01 (with arguments for this choice)

Option 1A: Keep the initial checker in one module. The projected size is safely
below 550, the plan already defines a precise split at 650, and the compact
shape best supports the instruction to avoid unnecessary file IO and file
count.

#### Answer to Q01: option 1A (with reason why it must be accepted as the answer)

Option 1A: Accept the cohesive module because it implements the settled
service and adapter contract without premature structure. Record the advisory
estimate, and apply the named CLI split only if measured growth reaches the
repository limit.

### Q02: Batch inventory compatibility delegate

Question description: Step 1 extracts public `staged_paths(root)` but proposes
keeping `git_batch_commit_workflow._staged_paths(root)` as a thin delegate.
Should implementation preserve that private compatibility point or update all
current imports and tests to use the public function immediately?

#### BBQ for Q02

A building can keep the old doorway as a short corridor to the new common
entrance, close it and redirect every visitor at once, or leave two staffed
entrances. The corridor avoids disruption without duplicating security; two
staffed entrances risk different rules. In this picture: the common entrance
is `commit_plan_support.staged_paths`, the old doorway is workflow
`_staged_paths`, visitors are current callers and monkeypatches, and security
rules are exact Git inventory semantics.

#### Options for Q02

- Option 2A: Keep `_staged_paths` as a thin delegate to the public function.
  - pro: Preserves current monkeypatch and import seams while maintaining one
    inventory implementation.
  - con: Retains a private compatibility name that later cleanup may remove.
- Option 2B: Remove `_staged_paths` and update all callers and tests in Step 1.
  - pro: Leaves only the public boundary and no compatibility surface.
  - con: Expands Step 1 churn and couples workflow tests directly to the new
    support module.
- Option 2C: Keep both helpers with separate Git calls.
  - pro: Requires the fewest immediate workflow edits.
  - con: Violates the parity requirement and permits checker and committing
    inventory to diverge.

#### Recommended option for Q02 (with arguments for this choice)

Option 2A: Keep the thin delegate. The design explicitly permits a private
compatibility wrapper, current tests patch that seam, and delegation preserves
one policy authority while limiting unrelated changes.

#### Answer to Q02: option 2A (with reason why it must be accepted as the answer)

Option 2A: Accept the delegate because it gives current batch behavior a stable
transition path without duplicating inventory logic. Tests must prove the
delegate calls the public function and cannot reinterpret its result.

### Q03: Requestor gate placement within the existing renderer module

Question description: Step 3 adds before/after index capture, one checker call,
readiness rejection, drift rejection, and checker evidence to the 497-line
`tools/code_review_request.py`. Should those small orchestration changes remain
in the specialized renderer or be extracted into a new helper immediately?

#### BBQ for Q03

A boarding desk can check the ticket and compare the passenger list before
printing a pass, or send those checks to a separate desk. The first keeps the
publication decision visible where the pass is produced; the second reduces
desk duties but introduces another handoff. In this picture: the boarding desk
is `tools/code_review_request.py`, the ticket check is `check_commit_plan`, the
passenger-list comparison is index-tree stability, and the boarding pass is
the paired request output.

#### Options for Q03

- Option 3A: Keep compact gate sequencing in `tools/code_review_request.py`.
  - pro: Places the enforced pre-write order directly at the specialized
    renderer boundary selected by the design.
  - con: Moves the file closer to the 550-line risk band.
- Option 3B: Create a requestor-specific commit-plan gate helper in Step 3.
  - pro: Keeps the renderer file smaller and isolates gate sequencing.
  - con: Adds a module whose only caller is one short orchestration path.
- Option 3C: Run the checker only from the outer workflow before invoking the
  renderer.
  - pro: Avoids growth in the renderer module.
  - con: Weakens enforcement because direct renderer use can bypass the
    precondition and evidence binding.

#### Recommended option for Q03 (with arguments for this choice)

Option 3A: Keep the compact sequence in the specialized renderer. It is the
confirmed enforcement boundary, the 545-line advisory estimate remains below
the risk band, and checker policy itself stays in `tools/commit_plan_check.py`.

#### Answer to Q03: option 3A (with reason why it must be accepted as the answer)

Option 3A: Accept in-module sequencing because it makes the required order and
no-write rejection visible at the artifact boundary. Extract only if the
measured file exceeds 650 or the orchestration grows into a separate
responsibility.

### Q04: Growth control for the existing request rendering test

Question description: The existing
`test_code_review_request_tdd.py` is exactly 550 lines. Should Step 3 update it
only for shared typed-source compatibility and put all new checker-gate cases
in the planned focused leaf, or split the existing test before implementation?
All six existing `CodeReviewRoundInput(` construction sites use keyword
arguments, so the new required checker result can be supplied through their
shared fixture rather than added independently in each test.

#### BBQ for Q04

A full archive shelf can receive one revised index card while a new shelf holds
a new collection, or the archive can be reorganized before the new collection
arrives. The index-card change preserves navigation with little handling; a
full reorganization improves space but delays the new collection. In this
picture: the full shelf is the 550-line rendering test, the index card is its
shared source fixture, the new shelf is the checker-specific test leaf, and the
new collection is gate sequencing coverage.

#### Options for Q04

- Option 4A: Make only fixture and parity updates in the existing test and add
  all new cases to the focused leaf.
  - pro: Avoids material growth in the risk-band file and keeps new tests
    responsibility-focused.
  - con: Related renderer tests are spread across two leaves.
- Option 4B: Split the existing rendering test before adding checker coverage.
  - pro: Reduces the risk-band file and can improve long-term test navigation.
  - con: Adds a cleanup operation that is not required by the feature and
    broadens Step 3.
- Option 4C: Add all checker cases to the existing test file.
  - pro: Keeps every request renderer test in one location.
  - con: Grows an already at-risk file and is likely to force an unrelated
    split during the feature.

#### Recommended option for Q04 (with arguments for this choice)

Option 4A: Limit the existing file to the minimal typed-result fixture and
evidence-parity changes. The new leaf provides a clean home for enforcement
cases and honors the plan's risk-band guidance without mandatory cleanup.

#### Answer to Q04: option 4A (with reason why it must be accepted as the answer)

Option 4A: Accept the focused new leaf because it controls growth while
preserving existing rendering coverage. Supply the required checker result
through the shared fixture so the risk-band file absorbs one fixture change.
A later split is required only if the existing file exceeds 650, not merely
because it exceeds an advisory estimate.

### Q05: Acceptance fixture extraction timing

Question description: Step 4 estimates the new real-repository acceptance test
at no more than 380 lines and names a `conftest.py` extraction only if it
approaches 550. Should temporary-repository setup and state snapshots begin in
the scenario file or be extracted before the first acceptance case?

#### BBQ for Q05

A field team can keep its compact equipment kit beside the first set of tests,
move common tools to a shared depot immediately, or borrow tools from a
laboratory with different conditions. A local kit is easy to audit while
small; a depot helps when many teams use it. In this picture: the equipment kit
is acceptance setup and snapshot helpers, the field tests are real-repository
scenarios, the depot is acceptance `conftest.py`, and the laboratory is unit
test support.

#### Options for Q05

- Option 5A: Keep helpers in the acceptance scenario file initially and
  extract only near the 550-line risk band.
  - pro: Keeps the real-repository contract visible in one focused file and
    avoids a premature fixture surface.
  - con: The scenario file may become dense before extraction is triggered.
- Option 5B: Create acceptance `conftest.py` with repository and snapshot
  helpers immediately.
  - pro: Separates setup from scenarios and supports later acceptance leaves.
  - con: Adds a file and shared fixture API before there is a second consumer.
- Option 5C: Reuse unit-test Git fixtures directly.
  - pro: Avoids duplicating repository setup helpers.
  - con: Couples acceptance evidence to isolated unit support and can hide the
    real launcher boundary.

#### Recommended option for Q05 (with arguments for this choice)

Option 5A: Start with local helpers. The 380-line estimate is safely below the
risk band, one file makes the complete no-mutation proof easy to inspect, and
the plan already defines the exact extraction trigger and destination. The
parent-package `tests/acceptance/commit_plan_check/conftest.py` destination is
deliberate so later sibling acceptance leaves can share it, even though the
repository's current conftests are leaf-level.

#### Answer to Q05: option 5A (with reason why it must be accepted as the answer)

Option 5A: Accept local acceptance helpers until measured growth approaches
550. Extract them to the named acceptance `conftest.py` when reuse or line risk
becomes real, while keeping unit fixtures out of the acceptance boundary. Keep
that helper at the parent package to preserve its intended sibling-sharing
scope.

### Q06: Checker plan-parsing boundary

Question description: Step 2 requires the service to parse the root plan once
with `interactive=False`. Which parsing boundary must the read-only checker
use, given that the committing workflow exposes its own read-and-parse helper?

#### BBQ for Q06

A receiving desk can open one addressed parcel and classify absent, empty, or
damaged contents directly; forward it through a shipping desk that reports one
generic problem; or move all receiving work into the inventory warehouse. The
direct desk preserves the reason for rejection without coupling to shipping.
In this picture: the parcel is `<root>/a.commit`, the receiving desk is the
checker, the shipping desk is `_read_and_parse_content`, the warehouse is
`commit_plan_support.py`, and the rejection reasons are missing-plan,
empty-plan, and operational failure.

#### Options for Q06

- Option 6A: Read `<root>/a.commit` in the checker and parse with public
  `git_batch_commit_parsing.parse_clipboard_content(content,
  interactive=False)`.
  - pro: Classifies a missing file, empty content, and an OS read failure
    directly at their required states and statuses.
  - pro: Keeps the read-only checker independent of the committing workflow
    and uses an exported parsing function.
  - con: The checker owns a small exact-file read that the committing workflow
    implements separately.
- Option 6B: Reuse
  `git_batch_commit_workflow._read_and_parse_content(root,
  filename="a.commit", interactive=False)`.
  - pro: Reuses one existing read-and-parse path with no new reading code.
  - con: Missing, empty, and OS read failures collapse into one
    `GitBatchCommitError`, requiring exception-message matching to recover the
    required states.
  - con: Couples the read-only checker to a private committing helper with
    clipboard fallback and progress logging.
- Option 6C: Move the exact plan read and parse into
  `tools/commit_plan_support.py` beside staged inventory.
  - pro: Places plan loading and index inventory in one neutral module.
  - con: Widens Step 1 beyond the settled inventory extraction while the
    committing workflow still needs its distinct clipboard path.

#### Recommended option for Q06 (with arguments for this choice)

Option 6A: Let the checker own the exact root-plan read and use the public
content parser. It produces the settled missing, empty, and operational
outcomes from control flow instead of message matching, keeps Step 1 scoped to
the shared Git inventory boundary, and avoids a read-only dependency on commit
execution orchestration.

#### Answer to Q06: option 6A (with reason why it must be accepted as the answer)

Option 6A: Accept the public content parser because it is the only option that
preserves the required failure taxonomy directly while keeping the committing
workflow and read-only checker appropriately separated.

### Q07: Required ready evidence on the request input

Question description: Step 3 attaches one typed commit-plan result to
`CodeReviewRoundInput`. Should that field be required, and should
`__post_init__` reject a non-ready result so the public
`render_code_review_request` cannot emit a request carrying invalid evidence?

#### BBQ for Q07

A boarding pass form can require a cleared security record and reject an
uncleared passenger immediately, require the record but let the gate reject it
later, or make the record optional. Immediate validation makes an invalid pass
impossible to construct. In this picture: the boarding pass form is
`CodeReviewRoundInput`, the security record is `CommitPlanCheckResult`, the
form validation is `__post_init__`, and issuing a pass is request rendering.

#### Options for Q07

- Option 7A: Make the field required but enforce readiness only in
  `_render_from_arguments`.
  - pro: Keeps the enforced command order in one orchestration function and
    leaves the dataclass as a carrier.
  - con: Direct public renderer calls can still produce request content from a
    non-ready result.
- Option 7B: Make the field required and reject a non-ready result in
  `CodeReviewRoundInput.__post_init__`.
  - pro: Makes non-ready request content unconstructible, consistent with the
    type's existing identity, round, timestamp, and tree-shape checks.
  - con: Non-ready cases must be proven at two boundaries: the render path
    rejects before construction, and direct construction fails.
- Option 7C: Make the field optional with a `None` default.
  - pro: Leaves existing construction sites untouched.
  - con: Makes missing checker evidence representable and violates the design
    requirement that the request carry the complete checker result.

#### Recommended option for Q07 (with arguments for this choice)

Option 7B: Require a ready typed result at construction. All six existing
`CodeReviewRoundInput(` sites use keyword arguments, and the new field can be
supplied through their shared fixture, so this stronger invariant requires one
fixture-level compatibility change in the 550-line test rather than repeated
per-test edits.

#### Answer to Q07: option 7B (with reason why it must be accepted as the answer)

Option 7B: Accept construction-time readiness validation because the typed
request input already enforces every other prerequisite for safe rendering.
Making invalid checker evidence unrepresentable preserves the specialized
renderer as the settled publication boundary without material risk-band test
growth. The render path owns command order, while `__post_init__` owns
representability for direct public renderer use.
