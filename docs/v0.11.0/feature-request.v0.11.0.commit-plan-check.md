# Validate commit plans without committing

## Review-mode need for read-only commit-plan validation

As an implementation reviewer or requestor, I want one repository command to
validate the root `a.commit` against the exact staged file set without changing
Git state, so both roles can use the batch workflow's real readiness floor
without entering its committing path.

This requirement belongs to the `commit-plan-check` item in the review-mode
umbrella. It adds a read-only entry point over existing commit-plan behavior;
it does not create a second validator or move commit-plan ownership into a
review role.

## Current commit-plan behavior in v0.11.0

- `tools/git_batch_commit_validation.py` exposes the public,
  side-effect-free `validate_commit_plan(blocks, staged_paths)` API.
- The API validates ordered groups, conventional subjects, supported `git add`
  commands, duplicate membership, and exact agreement with the staged paths.
- `tools/git_batch_commit_workflow.py` parses the root `a.commit` with
  `interactive=False` and calls the public validator before its commit phase.
- The shipped root-plan entry point rejects `--root-a-commit` together with
  `--dry-run`, so its successful path proceeds beyond validation to committing.
- Reviewer instructions currently describe how to assess `a.commit`, but do
  not name a safe command that produces the validator's typed evidence.

## Gap to close for commit-plan checking

The repository has the validation API but no command that exposes it for the
root plan as an explicitly read-only operation. A reviewer must therefore
inspect the plan manually or create an ad hoc import, even though batch
execution already relies on the authoritative rules.

The missing entry point must make the following behavior directly usable:

1. Read the project-root `a.commit` non-interactively.
2. Read the exact staged path set without changing it.
3. Pass the parsed blocks and staged paths to `validate_commit_plan`.
4. Report every typed group and diagnostic in a stable, quotable form.
5. Return without staging, unstaging, resetting, rewriting files, or committing.

## Required read-only command contract

The focused repository-root command is named `commit-plan-check.bat`. It must
run from a repository context and resolve the same project root, plan file,
parser, staged-path inventory, and public validator used by the batch workflow.
It must not weaken, reinterpret, or duplicate validation rules in a
launcher-specific implementation. Q08 settles whether the same shared function
must also be reachable as the platform-neutral
`python -m tools.commit_plan_check` entry point.

### Commit-plan inputs for the read-only command

- Plan source: the project-root `a.commit`.
- Parser mode: `interactive=False`.
- Membership source: the exact paths currently staged in Git.
- Validation call: `validate_commit_plan(blocks, staged_paths)`.

Malformed plan content and mismatches between planned and staged paths remain
validator diagnostics. The adapter must preserve their association with the
affected group, path, or rule.

### Repository-state guarantee for the read-only command

The command must not run `git reset`, `git add`, `git rm`, or `git commit`, and
must not rewrite `a.commit` or another repository file. Repeated calls with
unchanged inputs must leave the index and working tree unchanged.

Tests must compare the relevant Git state before and after successful and
failing validation calls. A failure is evidence about the plan, not authority
to repair or commit it automatically.

The command itself writes nothing under the repository root. A caller may
explicitly redirect its human or structured output into an ignored root `a.*`
evidence file; that caller-owned redirection does not weaken the command's
no-write guarantee.

### Validation evidence emitted by the command

The report must include the ordered typed groups returned by the public API and
every diagnostic it produces. Its structure must be stable enough for a code
reviewer to quote it as readiness-floor evidence and for a requestor to act on
the same result without scraping unrelated log prose.

Exit statuses follow the repository convention already used by
`bin/review_exchange.bat`: zero means validation completed successfully, three
means the expected stop of an invalid or non-ready plan, and two means invalid
invocation or an unexpected operational failure.

## Entry-point direction for commit-plan checking

Two implementation shapes are compatible with the existing validator:

1. Add a focused launcher whose interface exposes only root-plan validation.
2. Permit the existing batch launcher to combine `--root-a-commit` with
   `--dry-run` while proving that this combination cannot reach mutation or
   commit execution.

A focused `commit-plan-check.bat` launcher is the recommended requirement
direction because its public surface makes the no-commit promise explicit and
does not overload a command whose root-plan mode currently means validate and
commit. The design must still compare both shapes against reuse,
discoverability, and regression cost before settling the entry point.

## Shared review evidence for commit-plan checking

The code-reviewer instruction must name the resulting command where it
currently asks for a prose assessment of `a.commit`. Its result becomes the
readiness-floor evidence; it does not replace the reviewer's broader judgment
or grant commit authority.

The requestor-side command is an enforced publication precondition rather than
an advisory instruction. `group-commits-msg` and the code-review requestor must
use the same validation result, and publication must refuse to proceed while
the plan is invalid or non-ready. The reviewer reruns the command against the
received state so both roles independently establish the same readiness floor.

The staged inventory must preserve exact batch-workflow semantics. Its current
source is the private `_staged_paths(root)` helper in
`tools/git_batch_commit_workflow.py`; reuse therefore requires exporting that
helper or extracting it into a shared module. It invokes
`git diff --cached --name-only --no-renames -z`, so both sides of a rename are
separate inventory paths and both must appear in a matching plan.

## Acceptance criteria for commit-plan checking

1. The shipped repository-root `commit-plan-check.bat` command validates the
   root `a.commit` against the exact staged paths without entering a commit
   workflow.
2. The command parses with `interactive=False` and calls the existing public
   `validate_commit_plan(blocks, staged_paths)` API.
3. The command reports ordered typed groups and all validator diagnostics in a
   stable human-readable form and a stable structured form suitable for review
   evidence and automation.
4. Successful and failing calls leave the index, working tree, `a.commit`, and
   `HEAD` unchanged.
5. Automated tests prove the no-mutation contract and exact reuse of the public
   parser, staged-path inventory, and validator.
6. The code-reviewer instructions name the command and explain how its output
   contributes to the readiness floor without authorizing a commit.
7. The chosen entry point explicitly resolves the current incompatibility
   between root-plan mode and `--dry-run`.
8. Invalid or non-ready plans use exit status three, successful validation uses
   zero, and invalid invocation or unexpected failure uses two.
9. Code-review request publication is blocked until requestor-side validation
   succeeds, and the reviewer independently reruns the same command.
10. Inventory semantics match `_staged_paths(root)`, including separate paths
    for both sides of a rename under `--no-renames`.
11. The command writes nothing under the repository root, while callers may
    explicitly redirect output into ignored `a.*` evidence files.

## Scope boundaries for commit-plan checking

- Do not reimplement or fork the public commit-plan validation rules.
- Do not add staging, reset, file-rewrite, or commit side effects.
- Do not make the command responsible for repairing `a.commit`.
- Do not fold the tool into the code-reviewer assessment role.
- Do not include active-review status or interrupted-review resumption; those
  remain the next separate review-mode umbrella items.

## Code references for commit-plan checking

- `tools/git_batch_commit_validation.py`: defines the typed public validator
  and its group, subject, command, duplicate, and staged-membership checks.
- `tools/git_batch_commit_workflow.py`: parses root `a.commit`, inventories the
  staged paths, invokes validation, rejects root-plan dry-run, and owns commit
  execution after validation.
- `tools/git_batch_commit_workflow.py::_staged_paths`: currently private and
  unexported; obtains exact staged membership with
  `git diff --cached --name-only --no-renames -z`, counting both rename sides.
- `tools/prompt_workflow_code_review.py`: invokes the committing root-plan path
  only after durable human commit authorization.
- `instructions/code-reviewer.md`: defines the current prose readiness-floor
  assessment that must name the read-only command.
- `instructions/group-commits-msg.md`: defines requestor-side grouping and is
  the decision point for optional pre-publication use of the same command.

## Open questions for the v0.11.0 commit-plan-check feature request

### Q01: Which public command surface must the feature expose?

Question description: The requirement proposes the dedicated repository-root
name `commit-plan-check.bat` but leaves the existing
`--root-a-commit --dry-run` combination as an alternative. The feature must
settle whether users receive that one unmistakable read-only command, an
extension of the batch command, or both interfaces with identical behavior.

#### BBQ for Q01

The validator is a grill that already checks whether every ingredient belongs
in the planned meal, but today its only public door leads directly into the
serving line. Should the restaurant add a separate tasting window, mark a safe
lane through the serving door, or expose both entrances? In this picture: the
grill is `validate_commit_plan`, the tasting window is a focused launcher, the
safe lane is `--root-a-commit --dry-run`, and serving the meal is committing.

#### Options for Q01

- Option A1: Ship the focused repository-root `commit-plan-check.bat` launcher.
  - pro: The command name and option surface make the no-commit promise clear.
  - con: Users and documentation must learn another launcher.
- Option A2: Lift the restriction and expose only
  `--root-a-commit --dry-run` through the batch launcher.
  - pro: It reuses an established command and familiar dry-run vocabulary.
  - con: Root-plan mode currently means validate and commit, so safety depends
    on a flag combination that is easier to invoke incorrectly.
- Option A3: Support both interfaces as aliases over one read-only operation.
  - pro: It provides a clear command while preserving batch-command discovery.
  - con: Two supported surfaces increase documentation and compatibility work.

#### Recommended option for Q01 (with arguments for this choice)

Option A1: Ship the focused repository-root `commit-plan-check.bat` launcher.
The feature exists to make the safe boundary obvious, and a named command that
cannot express a commit action provides a stronger user-facing guarantee than
a dry-run branch inside the committing interface. It still reuses the same
parser, inventory, and validator.

#### Answer to Q01: option A1 (with reason why it must be accepted as the answer)

Option A1: Accept `commit-plan-check.bat` because it gives reviewers a named,
quotable command whose entire public contract is validation without commit,
while leaving batch execution semantics unchanged.

### Q02: Which output forms must be part of the stable evidence contract?

Question description: The requirement asks for stable, quotable typed groups
and diagnostics but does not say whether stability applies only to human text,
to machine-readable output, or to both. Review automation and future commands
need to know what output they may rely on.

#### BBQ for Q02

A food inspector can receive a readable checklist, a barcode record for the
central system, or both. A checklist alone is easy to quote but hard to parse;
a barcode alone is precise but unfriendly during a review. In this picture:
the checklist is human-readable output, the barcode is structured output, and
the central system is workflow automation consuming validation evidence.

#### Options for Q02

- Option B1: Guarantee only concise human-readable text.
  - pro: It directly serves reviewers and keeps the interface small.
  - con: Automation must scrape prose or import Python internals.
- Option B2: Guarantee only machine-readable structured output.
  - pro: It provides an exact contract for automation.
  - con: Reviewers lose convenient evidence they can read and quote directly.
- Option B3: Provide human-readable output by default and a stable structured
  mode containing the same groups and diagnostics.
  - pro: Humans and automation use one command and one validation result.
  - con: The feature must define and test two renderings.

#### Recommended option for Q02 (with arguments for this choice)

Option B3: Provide both forms. Human output satisfies the immediate reviewer
need, while a structured mode prevents later workflow commands from scraping
prose. Both should render the same typed result rather than run validation twice.

#### Answer to Q02: option B3 (with reason why it must be accepted as the answer)

Option B3: Accept default human output plus a stable structured mode because
the feature explicitly serves quotable review evidence and reusable workflow
automation, and neither audience should depend on the other's representation.

### Q03: How must process exit status distinguish validation outcomes?

Question description: Diagnostics alone do not define whether an invalid plan
causes a nonzero command result or how invocation failures differ from ordinary
validation failures. Shell callers need a dependable success boundary.

#### BBQ for Q03

A traffic signal can stay green while a sign describes a blocked road, turn
red for every kind of problem, or use different signals for a blocked road and
a broken signal controller. In this picture: the traffic signal is process exit
status, the sign is diagnostic output, the blocked road is an invalid plan, and
the broken controller is an invocation or environment failure.

#### Options for Q03

- Option C1: Always exit zero when the command itself ran, and encode validity
  only in output.
  - pro: Invocation errors are easy to distinguish from validation results.
  - con: Shell gates can accidentally accept an invalid plan.
- Option C2: Exit zero only for a valid plan and use one nonzero result for all
  other outcomes.
  - pro: It gives simple pass/fail behavior to scripts and humans.
  - con: Callers cannot distinguish invalid content from command failure by
    status alone.
- Option C3: Follow the repository convention: zero for successful validation,
  three for an expected invalid or non-ready plan, and two for invalid usage or
  an unexpected operational failure.
  - pro: It supports safe shell gates and precise recovery behavior.
  - con: The public contract must reserve and document multiple statuses.

#### Recommended option for Q03 (with arguments for this choice)

Option C3: Use zero, three, and two consistently with
`bin/review_exchange.bat`. An invalid plan must never look successful to a
shell gate, while a caller must be able to tell whether to repair `a.commit` or
repair invocation.

#### Answer to Q03: option C3 (with reason why it must be accepted as the answer)

Option C3: Accept zero for success, three for the expected invalid-plan stop,
and two for invalid invocation or unexpected failure because the command is a
readiness floor and should not introduce a third exit-status scheme into the
review workflow.

### Q04: Must requestors run the same check before publishing code review?

Question description: The requirement leaves requestor-side use by
`group-commits-msg` unsettled. The feature must decide whether every published
code-review request begins with validator-backed evidence or whether validation
remains a reviewer-only readiness check.

#### BBQ for Q04

A shipment can be weighed before leaving the warehouse, only when it reaches
customs, or optionally at either point. Early weighing catches mistakes sooner;
customs-only weighing avoids another warehouse step. In this picture: the
shipment is `a.commit` plus the staged set, the warehouse is the requestor, the
customs desk is the reviewer, and the scale is the read-only validation command.

#### Options for Q04

- Option D1: Make successful requestor-side validation an enforced precondition
  that blocks every code-review publication while the plan is invalid, and let
  the reviewer rerun it against the received state.
  - pro: Both roles start from the same readiness floor and invalid plans are
    caught before publication.
  - con: Every publication adds another validation call.
- Option D2: Keep the command reviewer-only.
  - pro: Request publication remains unchanged and validation stays independent.
  - con: Review rounds may begin with preventable plan errors.
- Option D3: Make requestor-side validation optional or advisory.
  - pro: Projects can adopt it incrementally.
  - con: Review evidence becomes inconsistent across requests and projects.

#### Recommended option for Q04 (with arguments for this choice)

Option D1: Enforce successful validation before publication and repeat it during
review. The command is read-only and reuses the exact staged inventory, so its
small cost buys a shared, deterministic floor without transferring reviewer
judgment or commit authority to the requestor. A documented but unenforced duty
would not deliver this option's claimed early-failure guarantee.

#### Answer to Q04: option D1 (with reason why it must be accepted as the answer)

Option D1: Accept an enforced publication gate because a requestor must not be
able to publish a mechanically invalid plan, while the reviewer's independent
rerun still verifies the actual state it receives.

### Q05: How broad is the command's no-write guarantee?

Question description: The acceptance criteria protect the index, working tree,
`a.commit`, and `HEAD`, but do not explicitly address ignored repository files,
cache files, or a generated evidence artifact. The read-only promise needs a
clear repository boundary.

#### BBQ for Q05

A museum visitor may be forbidden to touch the exhibits, forbidden to touch
anything inside the building, or allowed to leave a note at the front desk.
The safest audit has no unexplained traces in the museum. In this picture: the
exhibits are tracked Git state, the building is the repository root including
ignored files, and the front-desk note is a generated evidence file.

#### Options for Q05

- Option E1: Protect only tracked files, index, and `HEAD`; ignored caches or
  reports may be written inside the repository.
  - pro: Implementations may use convenient local caches and evidence files.
  - con: Repeated validation can still leave repository-local side effects.
- Option E2: Forbid every repository-root write and emit evidence only to
  stdout or an explicitly requested path outside the repository.
  - pro: The command is observably read-only across tracked and ignored state.
  - con: Persistent evidence requires caller-managed redirection.
- Option E3: Forbid implicit writes but allow an explicit output-file option
  inside the repository.
  - pro: Users can preserve evidence deliberately.
  - con: The command's no-write claim becomes conditional on invocation flags.

#### Recommended option for Q05 (with arguments for this choice)

Option E2: Forbid all command-owned repository-root writes. The immediate
consumers can quote stdout, and a caller may explicitly redirect human or
structured output into an ignored root `a.*` evidence file. A strict command
boundary makes repeated validation easy to prove and avoids hidden ignored-file
debt.

#### Answer to Q05: option E2 (with reason why it must be accepted as the answer)

Option E2: Accept a zero-command-write repository contract because the feature
is defined by validation without mutation. Caller-owned redirection into an
ignored `a.*` evidence file remains allowed and keeps persistence outside the
validator's behavior.

### Q06: What result is required when the plan or staged set is empty?

Question description: Exact membership can make an empty plan and empty staged
set appear mutually consistent, but a code-review readiness floor normally
expects work to review. Missing, empty, and mismatched inputs need explicit
feature behavior.

#### BBQ for Q06

An inventory clerk can approve an empty manifest for an empty truck, reject it
because there is no shipment, or distinguish an intentionally empty shipment
from a lost manifest. In this picture: the manifest is `a.commit`, the truck is
the staged set, approval is a valid result, and a lost manifest is a missing or
unreadable plan file.

#### Options for Q06

- Option F1: Treat an empty plan and empty staged set as valid exact membership.
  - pro: It follows set equality literally.
  - con: It can report commit readiness when there is nothing to commit.
- Option F2: Treat every missing or empty input combination as the same invalid
  plan result.
  - pro: It fails closed with a small behavior matrix.
  - con: It hides the difference between no work, a lost plan, and a mismatch.
- Option F3: Define distinct diagnostics for a missing plan, an empty plan, an
  empty staged set, and membership mismatch, with none considered commit-ready.
  - pro: It fails closed and tells the caller what state must change.
  - con: The command adds explicit input-state diagnostics around the validator.

#### Recommended option for Q06 (with arguments for this choice)

Option F3: Distinguish the states and consider none commit-ready. A reviewer
needs actionable evidence, and an empty equality is not a usable commit plan.
The adapter may perform these input preconditions before returning the public
validator's groups and diagnostics for nonempty inputs.

#### Answer to Q06: option F3 (with reason why it must be accepted as the answer)

Option F3: Accept distinct fail-closed diagnostics because missing planning,
missing staged work, and membership errors require different recovery actions,
and no empty state should authorize progression toward a commit.

### Q07: Must staged-path semantics exactly match batch execution?

Question description: The requirement says to use the exact staged set but does
not explicitly prohibit a reviewer-oriented inventory from filtering deletions,
renames, or other index states. The feature must define whether parity with the
batch workflow is absolute.

#### BBQ for Q07

Two auditors can count the same warehouse using one shared inventory sheet, or
each can apply a different rule about returned and relocated boxes. Different
rules make identical shelves produce different totals. In this picture: the
auditors are batch execution and read-only review, the inventory sheet is the
shared staged-path helper, and returned or relocated boxes are staged Git path
states such as deletions and renames.

#### Options for Q07

- Option G1: Reuse the exact staged-path inventory helper and semantics from
  batch execution without reviewer-specific filtering.
  - pro: Both paths validate identical Git state and cannot drift semantically.
  - con: The current `_staged_paths(root)` helper is private and absent from
    `__all__`, so reuse requires exporting it or extracting a shared module;
    its `--no-renames` inventory also counts both rename sides as separate paths.
- Option G2: Build a reviewer-specific staged inventory with richer filtering
  or classification.
  - pro: Review output can tailor path treatment to reviewer needs.
  - con: Requestor, reviewer, and committing paths may disagree on membership.
- Option G3: Use the batch inventory for validity but add optional descriptive
  classification that does not alter membership.
  - pro: Validity remains identical while output can explain Git path states.
  - con: Additional classification expands the feature beyond the minimum gap.

#### Recommended option for Q07 (with arguments for this choice)

Option G1: Reuse the exact batch inventory without filtering by exporting
`_staged_paths(root)` or extracting it into a shared module. Preserve its
`git diff --cached --name-only --no-renames -z` semantics, under which both
sides of a rename are separate planned paths. The central value of this feature
is exposing the same decision safely.

#### Answer to Q07: option G1 (with reason why it must be accepted as the answer)

Option G1: Accept absolute inventory parity, including the two-path rename
semantics and the helper export or extraction cost, because one staged state
must yield one commit-plan result regardless of whether validation is invoked
by the requestor, reviewer, or authorized committing workflow.

### Q08: Must commit-plan checking have a platform-neutral entry point?

Question description: Q01 names the repository-root Windows launcher
`commit-plan-check.bat`. The markdown-check precedent also exposes a Python
module entry point over the same policy authority, but the immediate consumers
of this command are requestor and reviewer roles. The feature must decide
whether portability is part of the public contract now.

#### BBQ for Q08

A workshop can provide a front door sized for the local delivery truck, a
second loading dock usable by any carrier, or only internal access to the same
machine. The machine should behave identically regardless of entrance. In this
picture: the front door is `commit-plan-check.bat`, the loading dock is
`python -m tools.commit_plan_check`, the carriers are operating systems, and
the machine is the shared read-only validation function.

#### Options for Q08

- Option H1: Ship both `commit-plan-check.bat` and the platform-neutral
  `python -m tools.commit_plan_check` entry point over one shared function.
  - pro: It follows the markdown-check precedent and supports non-Windows
    automation without duplicating validation behavior.
  - con: Two invocation forms require launcher and module-entry tests.
- Option H2: Ship only `commit-plan-check.bat` for the current reviewer and
  requestor consumers.
  - pro: It is the smallest surface needed by the present local workflow.
  - con: Non-Windows callers must import internals or wait for a later feature.
- Option H3: Ship only the platform-neutral Python entry point and omit a root
  batch launcher.
  - pro: One command form works wherever the Python environment is available.
  - con: It breaks the repository-root launcher convention used by local users.

#### Recommended option for Q08 (with arguments for this choice)

Option H1: Ship both forms over one shared function. The extra adapter is small,
the repository already established this pattern for markdown-check, and a
read-only evidence command is especially useful to automation outside the
Windows reviewer shell.

#### Answer to Q08: option H1 (with reason why it must be accepted as the answer)

Option H1: Accept the paired entry points because they preserve one validation
authority while making the same no-write evidence contract available to local
Windows roles and platform-neutral automation.
