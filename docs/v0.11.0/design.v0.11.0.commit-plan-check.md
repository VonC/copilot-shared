# Design v0.11.0 -- Read-only commit-plan checking

Reference feature request:
[feature-request.v0.11.0.commit-plan-check.md](feature-request.v0.11.0.commit-plan-check.md)

---

## Context for v0.11.0 commit-plan checking

The batch commit workflow already parses `a.commit`, inventories staged paths,
and calls the side-effect-free `validate_commit_plan` API before it changes Git
state. Review-mode roles need that same decision without entering the batch
workflow that can reset the index and create commits.

This design adds a read-only application boundary over the existing parser,
staged inventory, and validator. It keeps commit execution in the batch
workflow and makes validation usable by humans, automation, and the code-review
requestor and reviewer roles.

## Scope for v0.11.0 commit-plan checking

The v0.11.0 outcomes are:

1. One typed checker result represents the parsed groups, staged membership,
   input-state failures, and validator diagnostics.
2. `commit-plan-check.bat` and
   `python -m tools.commit_plan_check` expose that result without changing the
   repository.
3. Code-review publication and reviewer assessment use the same checker as a
   shared mechanical readiness floor.

Everything else supports those outcomes or stays in the committing workflow.

### In scope for v0.11.0 commit-plan checking

- Project-root discovery and exact root `a.commit` resolution.
- Non-interactive parsing through the existing commit-plan parser.
- Exact staged-path inventory with `--no-renames` semantics.
- Stable human-readable and structured renderings of one typed result.
- Exit statuses zero, three, and two for success, expected non-readiness, and
  operational failure respectively.
- Enforced requestor-side validation and independent reviewer-side validation.
- State-preservation checks for successful and failing calls.

### Deferred beyond v0.11.0 commit-plan checking

- Repairing or rewriting `a.commit` from checker diagnostics.
- Adding commit actions or mutation flags to the checker.
- Changing the root batch workflow to accept
  `--root-a-commit --dry-run`.
- Active-review status and interrupted-review resumption, which are separate
  review-mode umbrella items.
- Reviewer-specific staged-path filtering or Git status classification.

---

## Confirmed technical facts for v0.11.0 commit-plan checking

These facts come from the current repository code.

**The validator is already side-effect free**:
`tools/git_batch_commit_validation.py` exports only
`validate_commit_plan(blocks, staged_paths)`. It returns immutable ordered
`CommitPlanGroup` values and diagnostic strings inside
`CommitPlanValidation`.

**The root parser path is reusable but private**:
`tools/git_batch_commit_workflow.py::_read_and_parse_content` accepts
`interactive=False` and returns the existing `CommitBlock` objects. It is in
that module's `__all__`, despite its private name.

**The staged inventory is private and unexported**:
`_staged_paths(root)` runs
`git diff --cached --name-only --no-renames -z`. Its result includes both sides
of a rename as distinct paths, but `_staged_paths` is absent from `__all__`.

**The current root command cannot be used safely by a reviewer**:
`--root-a-commit` rejects `--dry-run` and calls the commit phase after
validation succeeds.

**Code-review rendering already captures index identity**:
`tools/code_review_request.py` captures the request-time index tree and renders
it into the typed code-review evidence before publication.

**The paired-entry-point pattern already exists**:
`markdown-check.bat` delegates to a platform-neutral Python module and leaves
policy evaluation in shared Python code.

## Current behavior before read-only commit-plan checking

```txt
root a.commit
    -> _read_and_parse_content(interactive=False)
    -> _validate_missing_files_for_blocks
    -> _staged_paths(root)
    -> validate_commit_plan(blocks, staged_paths)
    -> git reset
    -> git add and git commit for each group
```

The reusable validation calls sit inside a command whose successful root-plan
path proceeds to mutation. Instructions can ask a reviewer to inspect the same
properties, but they cannot name a shipped read-only evidence command.

## Target behavior for read-only commit-plan checking

```txt
commit-plan-check.bat                     python -m tools.commit_plan_check
              \                           /
               -> command adapter and rendering
               -> check_commit_plan(root)
                    -> resolve root a.commit
                    -> parse with interactive=False
                    -> inventory exact staged paths
                    -> validate_commit_plan(blocks, staged_paths)
                    -> return one immutable checker result
               -> render human text or structured output
               -> return 0, 3, or 2

code-review requestor -> run checker -> render and publish only on status 0
code reviewer          -> rerun checker -> quote result as readiness evidence
```

Neither entry point calls the root batch workflow. Both call the same checker
service, so the launcher name and operating system cannot change validation
policy.

---

## Read-only checker model for commit plans

The checker service owns input orchestration, while
`validate_commit_plan` remains the authority for group and membership rules.
The service returns data and does not write output streams itself. The CLI
adapter is the only component that renders stdout and stderr.

### Root and plan input resolution for the checker

The service accepts an explicit repository root from its adapter after normal
project-root discovery. It resolves only `<root>/a.commit`; it does not accept
an alternate plan path because the public feature is specifically the root
commit-plan readiness check.

Input handling distinguishes:

- missing `a.commit`;
- unreadable `a.commit`;
- an empty plan file or a parse with no commit blocks;
- a nonempty plan with an empty staged set;
- parsed and staged inputs passed to the public validator.

Missing and empty readiness inputs return typed non-ready diagnostics. An I/O
or Git execution problem that prevents a trustworthy decision is an
operational failure rather than an invalid plan.

### Typed result boundary for the checker

The proposed checker result wraps, rather than changes,
`CommitPlanValidation`. It carries:

- a stable result state such as `valid`, `missing-plan`, `empty-plan`,
  `empty-staged-set`, `invalid-plan`, or `operational-failure`;
- the ordered `CommitPlanGroup` values when parsing succeeds;
- every diagnostic in deterministic order;
- the exact staged paths used for the decision; and
- a boolean readiness property derived from the state and diagnostics.

Keeping an orchestration result outside `CommitPlanValidation` preserves the
public validator's narrow contract. Batch execution can continue consuming the
existing validator result, while the checker adds input-state meaning required
by a command boundary.

### Failure taxonomy for plan checking

Expected non-readiness includes malformed plan content, unsupported plan
commands, missing or empty readiness inputs, duplicate planned paths, and
planned-versus-staged membership differences. These conditions produce status
three because the command ran and found a plan that cannot proceed.

Invalid command arguments, repository discovery failure, unreadable inputs,
Git subprocess failure, encoding failure, or an unexpected exception produce
status two. They do not claim that the plan itself is invalid because the
checker could not complete its decision.

## Shared staged inventory for commit-plan parity

The checker and batch execution must call one staged-inventory function. No
adapter may recreate its Git command or filter its result.

### Public inventory boundary for staged paths

The preferred design extracts the inventory operation from the committing
workflow into a small shared commit-plan support boundary. That boundary owns
the cross-platform Git call and returns the existing tuple of repository-
relative paths.

Batch execution and read-only checking then depend on the shared boundary. A
private compatibility wrapper may remain in the batch module if existing tests
or imports require it, but it must delegate without changing the result.

### Rename and deletion semantics for staged membership

The inventory command remains exactly
`git diff --cached --name-only --no-renames -z`. The NUL delimiter preserves
paths containing whitespace, and `--no-renames` makes a rename appear as a
deleted source path plus an added destination path. Both paths must be named by
the commit plan.

Deletions remain staged paths even when the worktree file no longer exists.
The batch workflow's `_check_missing_files` already tolerates a staged deletion
of a committed file: it flags an absent worktree path only when that path is
also untracked and absent from `HEAD`. The read-only checker still does not use
that separate precondition, because its authority is exact index membership and
the public validator rather than worktree and `HEAD` state.

### Repository-state proof around checker calls

Acceptance tests capture `HEAD`, the index tree, staged-path inventory, tracked
worktree diff, root `a.commit` bytes, and relevant ignored-root inventory before
and after both valid and invalid calls. Equality proves the command did not
stage, unstage, reset, rewrite, or commit.

The checker does not create evidence files. Shell redirection remains a caller
action, including redirection to an ignored root `a.*` file.

## Output contracts for commit-plan evidence

Human and structured output are projections of the same checker result. The
adapter runs the service once per invocation, then selects one renderer.

### Human-readable commit-plan report

The default report begins with the result state, then lists groups in declared
order with their conventional subject and ordered paths. Diagnostics follow in
their deterministic service order. Each line is independently quotable and no
debug logging is mixed into stdout.

A valid report still lists every group and path so reviewer evidence proves
what was checked. An invalid report preserves all groups that parsed
successfully and prints every diagnostic rather than stopping at the first
membership error.

### Structured commit-plan report

The structured form is one JSON object produced from the same result. Its
proposed fields are:

```json
{
  "schema_version": 1,
  "state": "valid",
  "ready": true,
  "staged_paths": ["path/in/index"],
  "groups": [
    {
      "position": 1,
      "subject": "feat(scope): example",
      "paths": ["path/in/index"]
    }
  ],
  "diagnostics": []
}
```

The adapter uses deterministic key and list ordering. Structured output goes to
stdout even for expected non-readiness so automation can parse the evidence
before observing status three. Operational diagnostics go to stderr and status
two when no trustworthy checker result exists.

### Exit status mapping for checker adapters

| Checker outcome | Exit status | Stream contract |
| --- | --- | --- |
| Ready plan | `0` | Complete human or structured result on stdout |
| Expected invalid or non-ready plan | `3` | Complete human or structured result on stdout |
| Invalid invocation or operational failure | `2` | Stable diagnostic on stderr |

The root batch launcher's current status behavior is unchanged. These statuses
belong to the new read-only command boundary only.

## Code-review integration for commit-plan evidence

The checker is mechanical evidence. Requestors and reviewers still own their
role-specific assessment, exchange transitions, and human authority boundaries.

### Enforced requestor publication gate

The specialized code-review request renderer is the enforcement boundary. It
runs the shared checker against the current project root before it writes the
paired request artifacts. A non-ready or operational result prevents artifact
rendering, so the canonical requestor sequence cannot reach `publish-request`
with an unchecked plan.

To bind the check to the request evidence, the renderer captures the index tree
before validation, runs the checker, captures the index tree again, and requires
both tree identities to match. The stable tree becomes the existing
`request_index_tree`. A changed tree rejects rendering and requires a fresh
request attempt.

The request content carries the structured checker result beside the existing
index tree and resolved validation set. The reviewer can then compare its rerun
with the plan and exact staged state received for that round.

This enforcement covers the canonical renderer-to-publication path, not every
possible direct protocol call. Shared `publish-request` validates the role,
identity, document, umbrella, implementation step, and round through
`_validate_envelope`; it does not prove that content came from the specialized
renderer. A caller that hand-authors a matching request envelope can therefore
bypass the checker gate. The design accepts that residual because closing it
would couple the role-neutral exchange core to `a.commit` and staged Git state.

### Independent reviewer readiness check

The code-reviewer instruction names `commit-plan-check.bat` in the readiness
floor. The reviewer reruns it before assessing grouping, ordering, scope, and
subjects, and records the result state, groups, diagnostics, and staged paths in
its evidence inputs.

A valid checker result does not prove implementation completeness, test
results, repair attribution, or commit authority. Any failure blocks a
commit-ready recommendation, but success satisfies only the mechanical
`a.commit` part of the six-part readiness floor.

### Grouping workflow use of the checker

The grouped-commit workflow runs the read-only checker after `a.commit` is
formatted and the intended set is staged. A status-three result returns the
diagnostics for plan repair. Status zero permits the existing commit menu or
authorized batch continuation; it does not itself approve a commit.

The final batch command still runs its own validator before mutation. The
read-only check is an earlier shared gate, not a replacement for defensive
validation inside commit execution.

## Acceptance cases for v0.11.0 commit-plan checking

| Scenario | Expected outcome | Reason |
| --- | --- | --- |
| Valid root plan and matching staged set | Both entry points report identical ordered groups and return `0` | One service owns validation and both renderers use its result |
| Planned path missing from the index | All parsed groups and the missing-membership diagnostic are reported with status `3` | Expected non-readiness must fail closed without hiding evidence |
| Empty `a.commit` and empty staged set | The result is `empty-plan` with status `3` | Empty set equality is not commit readiness |
| Nonempty plan and empty staged set | The result is `empty-staged-set` with status `3` | The caller receives a distinct recovery action |
| Missing root `a.commit` | The result is `missing-plan` with status `3` | Missing planning is expected non-readiness |
| Unreadable plan or failed Git inventory | A stable stderr diagnostic is returned with status `2` | The command cannot make a trustworthy plan decision |
| Staged rename | Source and destination paths both participate in membership | The checker matches `--no-renames` batch semantics |
| Caller redirects stdout to ignored `a.*` | The checker remains read-only and the caller owns the evidence file | Redirection is outside command behavior |
| Requestor plan is invalid | Code-review request rendering produces no paired outputs | Publication cannot proceed without status zero |
| Index changes during request rendering | Rendering stops before publication | Checker evidence and request index identity must describe one state |
| Reviewer rerun is valid | The result is recorded as mechanical readiness evidence only | Success does not grant commit authority |

## Design constraints for later implementation planning

- Preserve `validate_commit_plan` as the single authority for group and exact
  membership rules.
- Keep Git inventory in one shared boundary used by checking and committing.
- Keep rendering outside the checker service and run the service once per CLI
  invocation.
- Keep the checker free of staging, reset, repair, evidence-file, and commit
  operations.
- Keep code-review exchange coordination in its existing requestor and reviewer
  workflows.
- Keep root batch execution and its `--root-a-commit --dry-run` rejection
  unchanged.

## Open questions for the v0.11.0 commit-plan-check design

### Q01: Where should the shared staged-path inventory live?

Question description: The batch workflow's `_staged_paths(root)` function has
the required `--no-renames -z` behavior, but it is private and absent from the
module's `__all__`. The design must choose whether to extract a public support
boundary, export the existing helper from the committing module, or duplicate
the Git call in the checker.

#### BBQ for Q01

Two inspectors need the same warehouse manifest. They can move the manifest to
a shared desk, let the second inspector reach into the shipping office, or make
a copy that can drift. In this picture: the inspectors are batch execution and
read-only checking, the manifest is staged-path inventory, the shared desk is a
public support boundary, and the shipping office is the committing workflow.

#### Options for Q01

- Option A1: Extract staged inventory into a public commit-plan support
  boundary used by both workflows.
  - pro: Validation and committing depend on one neutral inventory authority.
  - con: Existing batch imports and tests must move or use a compatibility
    wrapper.
- Option A2: Export `_staged_paths(root)` directly from the batch workflow.
  - pro: It is the smallest change to existing code.
  - con: A read-only tool depends on a module whose main responsibility is
    mutation and commit execution.
- Option A3: Recreate the Git inventory call inside the checker.
  - pro: The new checker stays independent of batch internals.
  - con: Two implementations can diverge on renames, delimiters, or path
    normalization.

#### Recommended option for Q01 (with arguments for this choice)

Option A1: Extract a neutral public boundary. The inventory semantics are part
of both workflows, while commit execution is not. One shared function gives
the checker a proper dependency direction and keeps exact parity testable.

#### Answer to Q01: option A1 (with reason why it must be accepted as the answer)

Option A1: Accept extraction because the requirement forbids semantic drift
and already identifies export or extraction as the real reuse cost. A neutral
boundary does not make read-only checking depend on the committing adapter.

### Q02: How should checker-specific input states relate to the public validator result?

Question description: `CommitPlanValidation` contains groups and diagnostics
for parsed inputs, while the new command must also distinguish a missing plan,
an empty plan, an empty staged set, and operational failure. The design must
decide whether to wrap the validator result, extend its public model, or express
these states through exceptions and renderer-specific values.

#### BBQ for Q02

A laboratory result covers the sample that reached the machine, but reception
also needs to report a missing vial or a broken refrigerator. Reception can add
a cover sheet, rewrite the laboratory form, or pass loose notes. In this
picture: the laboratory form is `CommitPlanValidation`, the cover sheet is a
checker result, and the reception conditions are input and operational states.

#### Options for Q02

- Option B1: Add a checker result that wraps the unchanged validator result and
  carries the broader state taxonomy.
  - pro: The validator stays narrow while adapters receive one typed outcome.
  - con: Callers must traverse one additional model layer.
- Option B2: Extend `CommitPlanValidation` with input and operational states.
  - pro: Every caller uses one public model.
  - con: A pure parsed-plan validator becomes coupled to filesystem, Git, and
    command-boundary concerns.
- Option B3: Keep the validator model and express other states through
  exceptions or untyped renderer data.
  - pro: It adds the fewest model declarations.
  - con: Human and JSON renderers can classify the same failure differently.

#### Recommended option for Q02 (with arguments for this choice)

Option B1: Wrap the validator result in a checker-specific immutable model.
The validator remains reusable by batch execution, and the checker gains one
typed source for state, readiness, groups, staged paths, and diagnostics.

#### Answer to Q02: option B1 (with reason why it must be accepted as the answer)

Option B1: Accept a wrapper because orchestration failures do not belong in a
function that validates already-parsed blocks against already-collected paths.
The separate model preserves that boundary without leaving adapters to guess.

### Q03: How should callers select structured output?

Question description: The requirement mandates default human-readable output
and a stable structured form but does not name the selection interface. The
choice affects compatibility, future renderings, help text, and test shape for
both the batch launcher and Python module entry point.

#### BBQ for Q03

A ticket machine can offer a format selector, a single JSON button, or a second
machine for coded tickets. In this picture: the ticket is checker evidence, the
selector is `--format`, the JSON button is `--json`, and the second machine is a
separate structured-output command.

#### Options for Q03

- Option C1: Use `--format human|json`, with `human` as the default.
  - pro: The interface names both contracts and can add a future format without
    another boolean flag.
  - con: It is more typing than a single `--json` switch.
- Option C2: Use an optional `--json` flag and human output otherwise.
  - pro: It is concise and familiar for a two-format command.
  - con: Adding another format later creates more mutually exclusive flags.
- Option C3: Expose a separate command or module for structured output.
  - pro: Each entry point has one stream shape.
  - con: Separate commands can drift and weaken the one-service public surface.

#### Recommended option for Q03 (with arguments for this choice)

Option C1: Use `--format human|json`. It makes the default explicit in help,
keeps both adapters identical, and treats output shape as one extensible value
rather than a growing set of switches.

#### Answer to Q03: option C1 (with reason why it must be accepted as the answer)

Option C1: Accept the format selector because the two required renderings are
peer projections of one result. An explicit value is stable for automation and
clear in acceptance tests.

### Q04: Which boundary must enforce requestor-side validation?

Question description: The requirement says publication must refuse an invalid
plan. The design proposes enforcement in the specialized code-review renderer,
which blocks the canonical renderer-to-publication path. Shared
`publish-request` accepts matching hand-authored envelope content without
proving the renderer ran, so the design must either accept that deliberate
bypass, couple the family-neutral exchange core to commit-plan policy, or leave
the check as an instruction-only duty.

#### BBQ for Q04

A parcel can be weighed at the packing station, at the central mail gate, or by
asking the clerk to remember. In this picture: the parcel is the code-review
request, the packing station is the specialized renderer, the mail gate is the
shared exchange core, and the clerk's reminder is an instruction-only check.

#### Options for Q04

- Option D1: Enforce checking in the specialized code-review renderer before it
  writes paired request artifacts.
  - pro: Invalid evidence cannot enter the canonical publication sequence, and
    the family-neutral core stays free of commit-plan policy.
  - con: The renderer gains a dependency on the checker service and repository
    state.
  - con: A caller can deliberately bypass the gate by hand-authoring a matching
    request envelope and calling `publish-request` directly.
- Option D2: Enforce checking inside shared `publish-request` for code-family
  identities.
  - pro: No caller can publish through the protocol without the check.
  - con: The role-neutral exchange core must understand `a.commit`, staged Git
    state, and code-review-specific evidence.
- Option D3: Run the command from the requestor instruction immediately before
  publication.
  - pro: It changes no renderer or protocol code.
  - con: The duty is documented but not enforced by the executable boundary.

#### Recommended option for Q04 (with arguments for this choice)

Option D1: Put the gate in the specialized renderer. That adapter already
captures request-time index evidence and must succeed before the requestor can
publish its paired artifacts, while the shared core remains role neutral. This
accepts the direct hand-authored publication bypass rather than making the core
read `a.commit` and staged Git state.

#### Answer to Q04: option D1 (with reason why it must be accepted as the answer)

Option D1: Accept renderer enforcement because it is the narrowest executable
boundary that owns code-review evidence and can stop publication without
teaching the shared protocol about commit plans. The residual applies only to a
caller that deliberately avoids the canonical renderer and supplies a valid
envelope directly to `publish-request`; it is recorded rather than hidden.

### Q05: Should the checker reuse the batch missing-file precheck?

Question description: Exact staged inventory includes deletions, while the
batch root workflow separately calls `_validate_missing_files_for_blocks`. Its
underlying `_check_missing_files` flags a path only when the worktree file is
absent, the path is untracked, and the path is absent from `HEAD`, so a staged
deletion of a committed file already passes. The checker must decide whether
that broader worktree-and-HEAD precondition belongs in a read-only index
membership decision.

#### BBQ for Q05

A warehouse has an index manifest and a separate form that flags a missing box
only when no earlier ledger shows it belongs there. A new inspector can ignore
that form, quote it as advice, or make it part of entry approval. In this
picture: the manifest is the Git index, the earlier ledger is `HEAD`, the
separate form is the batch missing-file precheck, and entry approval is checker
readiness.

#### Options for Q05

- Option E1: Do not call the working-file existence precheck from the read-only
  checker; rely on parser and exact staged membership validation.
  - pro: Staged deletions remain valid plan members and checker policy stays
    aligned with the index it claims to inspect.
  - con: The checker does not predict the batch precheck's rejection of an
    absent path that is also untracked and absent from `HEAD`.
- Option E2: Run the batch precheck for informational diagnostics without
  making it part of checker readiness.
  - pro: The report can expose a likely later batch obstacle while preserving
    index-and-validator authority.
  - con: The output gains a second diagnostic source outside the required
    validator contract.
- Option E3: Reuse the batch precheck unchanged as a checker readiness gate.
  - pro: The checker mirrors that additional batch precondition exactly.
  - con: Read-only validity becomes coupled to worktree tracking and `HEAD`
    history beyond the requirement's staged-membership boundary.

#### Recommended option for Q05 (with arguments for this choice)

Option E1: Keep the checker on plan syntax and exact index membership. The
feature's authority is `validate_commit_plan`, not the committing workflow's
separate absent-untracked-and-not-in-`HEAD` precondition. Batch-only readiness
rules remain outside this command unless a separate requirement brings them
into the checker contract.

#### Answer to Q05: option E1 (with reason why it must be accepted as the answer)

Option E1: Accept membership-only checking because the requirement explicitly
preserves the staged inventory without filtering. The current batch precheck
already accepts committed deletions, and a read-only validator still should not
consult worktree and `HEAD` state to make an index-membership decision.

### Q06: How much checker evidence should the code-review request carry?

Question description: The requestor must pass the checker before publication
and the reviewer must rerun it, but the requirement does not state whether the
request artifact embeds the full structured result, only a validity marker, or
no checker output at all.

#### BBQ for Q06

A sender can attach the full packing list, attach only a passed-inspection
stamp, or keep the inspection private. In this picture: the packing list is the
structured checker result, the stamp is a readiness boolean, and the parcel is
the published code-review request.

#### Options for Q06

- Option F1: Embed the full structured checker result beside the request-time
  index tree and resolved validation set.
  - pro: The request records exactly which groups, paths, and diagnostics the
    requestor saw, and the reviewer can compare its rerun.
  - con: Request artifacts become larger and must carry a versioned schema.
- Option F2: Embed only a passed marker and the index tree.
  - pro: The request stays compact while proving the gate ran.
  - con: The reviewer cannot compare requestor group and path evidence without
    reconstructing it from `a.commit`.
- Option F3: Embed no checker evidence and use the result only as a publication
  gate.
  - pro: Existing request content changes minimally.
  - con: The transcript cannot show what mechanical decision permitted the
    request to be published.

#### Recommended option for Q06 (with arguments for this choice)

Option F1: Embed the structured result. The review workflow is evidence driven,
and the existing request already carries typed index and validation data. Full
checker evidence makes requestor and reviewer parity directly auditable.

#### Answer to Q06: option F1 (with reason why it must be accepted as the answer)

Option F1: Accept the full result because the command exists to produce stable,
quotable evidence. Keeping that evidence out of the durable request would leave
only an unverifiable assertion that the gate passed.

### Q07: How should automation select the repository root?

Question description: The command must run from a repository context and use
the project-root `a.commit`, while the platform-neutral entry point also needs
testability and use from automation. The public CLI can rely only on current-
directory discovery, accept an optional root flag, or require a positional
repository path.

#### BBQ for Q07

A courier can infer the depot from the street, accept an optional depot address,
or require the address on every trip. In this picture: the depot is the Git
project root, street inference is upward discovery from the current directory,
and the explicit address is a CLI root argument.

#### Options for Q07

- Option G1: Discover from the current directory by default and accept an
  optional `--root <path>` override.
  - pro: Local use stays short while tests and automation can name an exact
    repository without changing process working directory.
  - con: The adapter must define precedence and validate the explicit path.
- Option G2: Support only current-directory project-root discovery.
  - pro: It matches the shortest repository command contract.
  - con: Automation must change process working directory to target another
    repository.
- Option G3: Require a repository path on every invocation.
  - pro: The target is always explicit.
  - con: It makes the common root command noisy and diverges from existing
    self-locating launchers.

#### Recommended option for Q07 (with arguments for this choice)

Option G1: Combine discovery with an optional root override. Both paths resolve
to the same validated root before calling the checker, so testability does not
create a second policy path.

#### Answer to Q07: option G1 (with reason why it must be accepted as the answer)

Option G1: Accept the optional root flag because it preserves simple local use
and gives platform-neutral automation an explicit target through the same
adapter and service.
