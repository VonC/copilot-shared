# v0.11.0 code-reviewer implementation tracking and validation

No, it is not implemented.

This skeleton tracks the six planned responder slices; no implementation check has run yet.

---

## File-based IO cost clarification for v0.11.0 code-reviewer implementation

- Resolve review artifacts and retained evidence from exact identity-derived paths.
- Read explicit request, plan, manifest, and answer inputs once per owning phase.
- Compare Git state only for the staged set and named repair or validation paths.
- Write paired outputs and the stable ignored manifest through their atomic boundaries.

---

## Complexity bound for v0.11.0 code-reviewer implementation

- Path derivation remains O(1) per round.
- Assessment remains O(n) over explicit staged paths, repair paths, commands, and commit groups.
- No implementation step may add directory enumeration for artifact selection.
- Every step's performance check must confirm the absence of a repository-wide nested comparison.

---

## Step 1. Publish immutable request evidence

### Analysis of Step 1 implementation state

Yes. Step 1 has been fully implemented.

The requestor now captures the exact Git index tree, resolves the mandatory
default-plus-addition validation set with source attribution, and renders both
values from one typed evidence object in the paired request artifacts. Focused
checks and the final post-review Groundhog walk pass with 1,707 tests, 100%
coverage, and no duration outliers or exclusion regressions.

### Goal for Step 1

Publish the request-time Git index tree and the resolved validation set with sources through the existing paired code-review request renderer.

### Step 1 improvement expectations

- Project defaults cannot be removed by plan or request additions.
- Request and transcript summary identify the same tree and validation set.
- Existing requestor publication behavior remains intact.

### What was implemented for Step 1

- Added `capture_index_tree` as the single capture-only Git index-tree helper.
- Added deterministic, additive validation resolution that preserves project
  defaults and merges project, plan, and request source labels.
- Extended `CodeReviewRoundInput` and its CLI boundary with mandatory request
  evidence, repeatable additive validation flags, and publication-time capture.
- Added one canonical fenced JSON object under `## Code review evidence` and a
  human-readable transcript section derived from the same typed evidence.
- Updated the canonical requestor instruction and template without changing the
  shared exchange envelope or paired publication lifecycle.
- Added real temporary-repository, resolver, renderer, instruction, IO, and
  requestor acceptance coverage for the completed surface.

### New types or classes introduced for Step 1

- `ResolvedValidationCommand`: one immutable command with ordered source labels.
- `ResolvedValidationSet`: one immutable, unique, deterministically ordered set
  of mandatory commands.
- `_CodeReviewEvidence`: the renderer-internal typed source for canonical JSON
  and its paired human-readable summary.

### Architecture check for Step 1

The capture-only Git adapter delegates subprocess portability to the existing
Git command helper. Validation resolution remains side-effect free, while the
request renderer composes those two boundaries and retains exchange-envelope
ownership in the existing shared model. Dependencies point from the request
adapter toward focused evidence and validation modules; no business-only layer
imports a new technical concern, and no DDD-Hexagonal boundary is inverted.

No architecture smell or violation needs to be addressed.

### Performance check for Step 1

Index capture delegates one `git write-tree` operation. Validation resolution is
O(n) over explicit command inputs with insertion-ordered dictionary lookup, and
rendering is O(n) over the resolved commands. No directory enumeration,
repository-wide nested comparison, O(n log n), or O(n^2) computation was added.
The real-Git tests moved process setup outside measured calls and the final full
suite reported zero duration outliers.

No performance issue needs to be addressed.

### Unit test coverage check for Step 1

The dedicated `test_code_review_evidence` and `test_code_review_validation`
leaves exercise every branch in the two new production modules. The existing
request renderer, requestor instruction, and requestor acceptance leaves cover
mandatory evidence validation, canonical dual-JSON rendering, envelope
round-trip behavior, source summaries, publication-time capture, additive CLI
inputs, read-once IO, and unchanged exchange transitions. The final Groundhog
walk reports 100% project coverage across 1,707 passing tests.

No unit-tested class or module is below 100% coverage or needs completing.

### Feature integrity for Step 1

Existing request identity, staged-repair policy, optional human guidance,
caller-owned ignored-file validation, exact-path access, paired output, and
shared envelope parsing remain covered. Requests now fail closed when tree or
validation evidence is absent or malformed, while both evidence headings
round-trip without changing shared exchange mechanics. No existing reporting
or requestor capability is impaired.

---

## Step 2. Add executable Git evidence and commit validation

### Analysis of Step 2 implementation state

Not started. Step 2 is not implemented because the executable evidence boundary, commit validation, manifest recovery, and tests have not been added.

### Goal for Step 2

Provide machine-checkable snapshots, repair attribution, umbrella and validation-state comparisons, stable retained evidence, and shared `a.commit` validation through public typed boundaries.

### Step 2 improvement expectations

- Reviewer patches exclude pre-existing writer hunks.
- Batch execution and review use one commit-plan validator.
- The evidence CLI captures and compares umbrella digests and validation state, and owns manifest write/read/retire operations.

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

## Step 3. Enforce reviewer-mode implementation checks

### Analysis of Step 3 implementation state

Not started. Step 3 is not implemented because the canonical implementation check does not yet expose a reviewer mode that delegates its machine checks to the evidence launcher.

### Goal for Step 3

Bound advisory implementation checks to reviewed-step validation rows and require executable umbrella and validation-state comparisons on both criteria outcomes.

### Step 3 improvement expectations

- Reviewer mode never marks an umbrella row completed.
- Pass and fail paths both call the evidence boundary by named operation.
- `Umbrella draft: none` records digest comparison as not applicable.

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

## Step 4. Build paired code-review answers

### Analysis of Step 4 implementation state

Not started. Step 4 is not implemented because the typed answer model, CLI, template, launcher, and tests do not exist.

### Goal for Step 4

Render separately validated early-rejection and assessment answers plus their paired substantive transcript summaries.

### Step 4 improvement expectations

- Assessment-derived fields are prohibited in early rejection.
- Paired outputs share one exact identity and finding source.
- CLI IO failures do not leave a partial accepted pair.

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

---

## Step 5. Route and instruct the independent reviewer

### Analysis of Step 5 implementation state

Not started. Step 5 is not implemented because the reviewer route, typed actor, canonical instruction, host adapters, and structure tests are absent.

### Goal for Step 5

Route only an exact pending code request to the advisory reviewer and expose the same bounded workflow through every supported host adapter.

### Step 5 improvement expectations

- Ordinary and forced routing agree on actor and identity.
- `CodeReviewRoute.actor` is resolved once and cannot disagree with the classified state.
- Every non-pending live state remains requestor-owned.
- Canonical prose forbids owner, escalation, and commit operations.

### What was implemented for Step 5

_(empty — no check has taken place yet.)_.

### New types or classes introduced for Step 5

_(empty — no check has taken place yet.)_.

### Architecture check for Step 5

_(empty — no check has taken place yet.)_.

### Performance check for Step 5

_(empty — no check has taken place yet.)_.

### Unit test coverage check for Step 5

_(empty — no check has taken place yet.)_.

### Feature integrity for Step 5

_(empty — no check has taken place yet.)_.

---

## Step 6. Prove responder acceptance and recovery

### Analysis of Step 6 implementation state

Not started. Step 6 is not implemented because end-to-end temporary-repository acceptance, recovery, launcher smoke, and IO checks have not run.

### Goal for Step 6

Prove all requirement and design acceptance cases through real staged-state, exchange, publication, and recovery behavior.

### Step 6 improvement expectations

- Both answer shapes reach the correct durable exchange state.
- Request, evidence, and answer launchers each have one public-seam smoke test.
- Repair, drift, validation side effects, guidance, and reclaim preserve ownership boundaries.
- Commit-ready remains advisory and exit-3 publication retires retained evidence.

### What was implemented for Step 6

_(empty — no check has taken place yet.)_.

### New types or classes introduced for Step 6

_(empty — no check has taken place yet.)_.

### Architecture check for Step 6

_(empty — no check has taken place yet.)_.

### Performance check for Step 6

_(empty — no check has taken place yet.)_.

### Unit test coverage check for Step 6

_(empty — no check has taken place yet.)_.

### Feature integrity for Step 6

_(empty — no check has taken place yet.)_.
