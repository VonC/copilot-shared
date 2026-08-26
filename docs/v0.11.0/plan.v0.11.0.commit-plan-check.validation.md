# v0.11.0 commit-plan-check implementation tracking and validation

No, it is not implemented.

This skeleton tracks later implementation review for the four ordered slices
of read-only commit-plan readiness evidence.

---

## File-based IO cost clarification for v0.11.0 commit-plan checking (implementation)

All implementation work must preserve the IO classification established in
`docs/v0.11.0/plan.v0.11.0.commit-plan-check.md`:

- read `<root>/a.commit` exactly once per checker call;
- obtain staged membership through one shared Git index command;
- reuse one in-memory typed result for validation and rendering; and
- perform no checker-owned repository writes or per-path file scans.

---

## Complexity bound clarification for v0.11.0 commit-plan checking (implementation)

- New orchestration remains linear in plan content and staged membership.
- Per-path and per-group accumulation remains `O(1)` amortized.
- The existing validator's deterministic mismatch sorting is not duplicated.
- No step introduces quadratic work, repeated parsing, or per-path
  subprocesses.

Every implemented step must be reviewed against these bounds in its
performance check.

---

## Step 1. Share exact staged-path inventory with the committing workflow

### Analysis of Step 1 implementation state

Yes. Step 1 has been fully implemented.

The exact staged-path inventory now has one public implementation, the batch
workflow preserves its private compatibility seam through delegation, and the
focused and global verification evidence covers the complete planned contract.

### Goal for Step 1

Extract the exact staged-path inventory into one public support boundary and
make the committing workflow delegate without changing its behavior.

### Step 1 improvement expectations

- One Git invocation owns `--cached --name-only --no-renames -z` semantics.
- Batch validation and the future checker receive the same ordered path tuple.
- Existing batch validation and commit execution remain unchanged.

### What was implemented for Step 1

- **Shared inventory boundary**: `tools/commit_plan_support.py` owns the exact
  `git diff --cached --name-only --no-renames -z` invocation and returns the
  ordered nonempty NUL-decoded path tuple.
- **Batch compatibility**: `git_batch_commit_workflow._staged_paths(root)` now
  delegates directly to `commit_plan_support.staged_paths(root)`, while
  `_validate_commit_plan_for_root` continues to pass that result to the
  unchanged public validator before mutation.
- **Focused verification**: the new support tests pin the Git arguments, root,
  capture and encoding options, whitespace preservation, deletion membership,
  both rename sides, order, and empty-segment handling. The updated workflow
  test proves the compatibility helper returns the public result unchanged.
- **Repository gate evidence**: the final forced `ghog day --force` bypassed
  the cached green no-op and completed with
  `fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0`.

### New types or classes introduced for Step 1

- `commit_plan_support.staged_paths(root)`: public read-only function for exact
  staged membership shared by committing and checking workflows.
- `test_commit_plan_support_tdd.py`: focused test suite for the subprocess and
  NUL-decoding boundary.

No new production class or domain type was needed; the step is a function
extraction with compatibility wiring.

### Architecture check for Step 1

- **Boundary direction**: the neutral support module depends only on the
  existing cross-platform Git command adapter. The committing workflow depends
  on that support boundary and no reverse dependency exists.
- **Responsibility placement**: Git inventory and decoding remain together;
  parser, validator, rendering, and commit execution responsibilities were not
  moved into the support module.
- **File girth**: the new support module is 38 lines, the workflow is 481 lines,
  the focused test is 135 lines, and the updated workflow test is 347 lines,
  all within their advisory budgets and the 650-line ceiling.

No, there is nothing that needs to be addressed for Step 1.

### Performance check for Step 1

`staged_paths(root)` performs exactly one Git subprocess call and one linear
split-and-filter pass over its NUL-delimited output. It adds no per-path file
probe, nested scan, sorting, O(n log n) work, or O(n^2) work.

No, there is no performance issue that needs to be addressed for Step 1.

### Unit test coverage check for Step 1

- **`commit_plan_support.staged_paths`**: focused tests execute the sole Git
  seam, nonempty and empty decoding branches, whitespace paths, deletions, and
  two-sided rename membership; the global coverage gate reports 100%.
- **Batch delegate and validator wiring**: existing and updated workflow tests
  cover delegation, successful validation input, diagnostics, and unchanged
  commit control flow.

No, there is no unit-tested class below 100% that needs completing for Step 1.

### Feature integrity for Step 1

- **Existing batch behavior**: the public validator still receives the same
  ordered tuple through `_staged_paths`, and commit execution remains unchanged.
- **Rename and deletion reporting**: `--no-renames` continues to expose both
  rename sides, while deleted worktree paths remain exact staged members.
- **Regression evidence**: all 2,010 full-suite tests pass with no warning,
  expected failure, coverage gap, or duration outlier.

No existing feature or reporting capability appears impaired by Step 1.

---

## Step 2. Expose one typed read-only checker through both entry points

### Analysis of Step 2 implementation state

Not started. Step 2 is not implemented because no implementation check has
taken place yet.

### Goal for Step 2

Add the immutable checker service, equivalent human and JSON evidence, stable
status mapping, Python CLI, and focused root launcher without repository
mutation.

### Step 2 improvement expectations

- One service call distinguishes ready, expected non-ready, and operational
  outcomes.
- Human and JSON output preserve the same groups, paths, and diagnostics.
- Both entry points share one service and return statuses `0`, `3`, and `2`.

### What was implemented for Step 2

_(empty — no check has taken place yet.)_.

### New types or classes introduced for Step 2

_(empty — no check has taken place yet.)_.

### Architecture check for Step 2

_(empty — no check has taken place yet.)_.

### Performance check for Step 2

_(empty — no check has taken place yet.)_.

### Unit test coverage check for Step 2

_(empty — no check has taken place yet.)_.

### Feature integrity for Step 2

_(empty — no check has taken place yet.)_.

---

## Step 3. Enforce commit-plan readiness before code-review request rendering

### Analysis of Step 3 implementation state

Not started. Step 3 is not implemented because no implementation check has
taken place yet.

### Goal for Step 3

Require a ready checker result and identical before/after index trees before
the specialized code-review renderer writes paired request artifacts.

### Step 3 improvement expectations

- Non-ready, operational, and index-drift outcomes produce no request outputs.
- The request carries the full structured checker result beside the stable
  request index tree and validation set.
- Human and JSON evidence derive from the same typed source.

### What was implemented for Step 3

_(empty — no check has taken place yet.)_.

### New types or classes introduced for Step 3

_(empty — no check has taken place yet.)_.

### Architecture check for Step 3

_(empty — no check has taken place yet.)_.

### Performance check for Step 3

_(empty — no check has taken place yet.)_.

### Unit test coverage check for Step 3

_(empty — no check has taken place yet.)_.

### Feature integrity for Step 3

_(empty — no check has taken place yet.)_.

---

## Step 4. Roll out shared review guidance and acceptance evidence

### Analysis of Step 4 implementation state

Not started. Step 4 is not implemented because no implementation check has
taken place yet.

### Goal for Step 4

Make grouped-commit and reviewer instructions use the shared read-only command
and prove entry-point parity plus exact repository immutability in acceptance
tests.

### Step 4 improvement expectations

- Requestors and reviewers independently establish the same mechanical
  readiness floor without transferring commit authority.
- Grouped-commit preparation repairs non-ready plans before commit choices.
- Real-repository tests cover the failure taxonomy, renames, both adapters, and
  complete before/after state equality.

### What was implemented for Step 4

_(empty — no check has taken place yet.)_.

### New types or classes introduced for Step 4

_(empty — no check has taken place yet.)_.

### Architecture check for Step 4

_(empty — no check has taken place yet.)_.

### Performance check for Step 4

_(empty — no check has taken place yet.)_.

### Unit test coverage check for Step 4

_(empty — no check has taken place yet.)_.

### Feature integrity for Step 4

_(empty — no check has taken place yet.)_.
