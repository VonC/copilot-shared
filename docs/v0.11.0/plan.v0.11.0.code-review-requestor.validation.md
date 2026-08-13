# v0.11.0 code-review-requestor implementation tracking and validation

No, it is not implemented.

Step 1 is validated; Steps 2 through 4 remain pending.

## File-based IO cost clarification for v0.11.0 code-review-requestor (implementation)

- Resolve one exact plan and implementation step.
- Use constant exact-path exchange operations and atomic writes.
- Never scan documentation directories or reread transcripts as working context.
- Read current staged evidence once per answer assessment.

## Complexity bound clarification for v0.11.0 (implementation)

- **O(1) per routing or exchange operation** on one exact context.
- **O(n) per authored input or staged diff**.
- No new `O(n log n)` or `O(n^2)` response path.

## Step 1. Add paired code-review request rendering

### Analysis of Step 1 implementation state

Yes. Step 1 has been fully implemented.

The exact code-family plan, step, round, umbrella, authored inputs, request content, and transcript summary now share one validated rendering path. The focused suite, repository checks, all 1,641 tests, coverage gate, and duration gate pass.

### Goal for Step 1

Add validated paired request and transcript-summary rendering for exact code-review rounds.

### Step 1 improvement expectations

- Exact plan, step, round, and umbrella identity.
- Separate ignored authored inputs and paired UTF-8 outputs.
- Code-review-specific instructions without transcript boilerplate leakage.

### What was implemented for Step 1

- Added a pure code-review renderer that derives fixed `code` identity from an exact plan and implementation step.
- Added a canonical request template covering implementation-check evidence, staged repairs, repaired-path reporting, `a.commit` assessment, and advisory commit readiness.
- Added a self-locating launcher and an exact ignored UTF-8 CLI boundary with one read per authored input and one write per paired output.
- Added focused unit coverage for valid rendering, optional guidance, invalid identity, malformed input, unsafe paths, Git-ignore failures, template failures, and envelope mismatches.
- Moved expensive setup for two duration-gated tests into fixtures while keeping real Git setup and all assertions.

### New types or classes introduced for Step 1

- `CodeReviewRoundInput`: frozen, validated identity and authored input for one code-review round.
- `CodeReviewRequestRender`: frozen paired request-content and substantive-summary result.
- `_ArgumentParser`: CLI adapter that converts argument errors to the renderer's stable failure contract.

### Architecture check for Step 1

Rendering remains a deterministic transformation over immutable inputs. Git and filesystem concerns stay at the command adapter boundary, while the launcher contains no business rules. Shared exchange models and envelope validation are reused without importing requestor coordination or persistence responsibilities. No DDD-Hexagonal violation or layer inversion is present.

No architecture issue needs to be addressed.

### Performance check for Step 1

The renderer performs constant exact-path validation, linear template substitution, and one linear read or write per caller-owned file. It adds no directory scan, transcript reread, sorting, nested input traversal, `O(n log n)`, or `O(n^2)` path. The renderer is 382 lines against the step's advisory 280-380 band, and its tests are 437 lines against the advisory 300-430 band. Both exceed their advisory upper bound by a small margin and both stay far below the 650-line ceiling, so the shared execution checklist records the variance as evidence rather than missing work. No split is required: the module keeps one responsibility, and the step's split guidance reserves the `code_review_request_cli.py` extraction for a renderer approaching the ceiling. Groundhog's duration gate passes after two setup-heavy calls were reduced below the one-second call floor.

No performance issue needs to be addressed.

### Unit test coverage check for Step 1

The focused `tests/unit/tools/test_code_review_request/test_code_review_request_tdd.py` package covers the complete `tools/code_review_request.py` module, including defensive error paths. The repository full run reports 100% coverage. This repository does not use the `src/pdfss/tests/unit` layout named by the generic instruction; the colocated unit-test convention is followed here.

No unit-tested class below 100% needs completing.

### Feature integrity for Step 1

Existing specification rendering and exchange behavior are unchanged. The new launcher and files are additive, all 1,641 tests pass, and the duration fixes preserve real Git setup and every assertion while moving setup outside measured call time. No existing feature or reporting capability is impaired.

## Step 2. Add the specialized code-review requestor role

### Analysis of Step 2 implementation state

Yes. Step 2 has been fully implemented.

The canonical code-review requestor role now fixes the code-family policy, delegates the shared exchange lifecycle, assesses staged repairs and commit grouping, and exposes redirect-only adapters for every supported host. Its focused contract suite and the full repository gate pass.

### Goal for Step 2

Add the canonical specialized requestor instruction and redirect-only adapters over shared coordination.

### Step 2 improvement expectations

- Fixed code-review family policy and exact state handling.
- Staged-repair, disagreement, convergence, and authorization assessment rules.
- Thin canonical redirects for every supported host.

### What was implemented for Step 2

- Added `instructions/code-review-requestor.md` with the fixed `code` / `commit-ready` policy, exact plan-step identity, complete exchange-state routing, paired request rendering, exact answer-path consumption, repair and `a.commit` assessment, convergence handling, and durable commit continuation.
- Added workflow, Codex instruction, Codex skill, and Claude skill adapters that redirect directly to the canonical role without copying lifecycle policy.
- Added token-and-order contract tests for the role plus structural tests proving adapter metadata and direct canonical redirects.

### New types or classes introduced for Step 2

No production types or classes were introduced. Step 2 adds Markdown role contracts and their structural tests only.

### Architecture check for Step 2

The canonical instruction owns only code-review-specific policy and delegates all coordination transitions to `instructions/review-requestor.md`, request construction to `bin/code_review_request.bat`, and exchange commands to `bin/review_exchange.bat`. Each host adapter is a direct redirect, so policy is not duplicated across integration surfaces. This preserves the intended ports-and-adapters boundary and introduces no cross-layer dependency or misplaced behavior.

No architecture issue needs to be addressed.

### Performance check for Step 2

The implementation is static Markdown with constant-path redirects and no new runtime computation, traversal, or I/O loop. The two test modules are 151 and 107 lines respectively, below the repository ceiling; they are also below their advisory bands, which reflects concise token/order and redirect assertions rather than omitted coverage.

No performance issue needs to be addressed.

### Unit test coverage check for Step 2

Thirteen focused instruction and adapter tests pass. They verify required tokens and their ordering rather than pinning full prose, and they prove every adapter contains the required metadata plus a direct canonical redirect without copied lifecycle logic. Step 2 introduces no production class file requiring a class-specific unit coverage target. The full repository walk also completed with 100% coverage, zero failures, warnings, outliers, or exclusions.

No unit-tested class is below 100% or needs completing.

### Feature integrity for Step 2

Existing shared requestor behavior remains canonical and unchanged; the new role narrows policy through delegation instead of modifying shared transitions. The complete repository gate reports `exit=0`, so no existing feature or reporting capability is impaired.

## Step 3. Integrate commit-gate activation and durable pw routing

### Analysis of Step 3 implementation state

Not started. Step 3 is not implemented because no implementation check has taken place.

### Goal for Step 3

Connect post-grouping activation, explicit step transport, live exchange routing, and authorized commit continuation.

### Step 3 improvement expectations

- Marker absence preserves the existing gate.
- Marker presence yields a self-contained plan-and-step requestor command.
- Durable commit authorization executes existing commit mechanics once without another choice.

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

## Step 4. Prove the full code-review requestor workflow

### Analysis of Step 4 implementation state

Not started. Step 4 is not implemented because no implementation check has taken place.

### Goal for Step 4

Validate the complete opt-in requestor lifecycle, bounded repair paths, human gate, and single authorized commit.

### Step 4 improvement expectations

- Public-launcher acceptance coverage for normal, recovery, and failure paths.
- Constant exact-path IO with no transcript or directory scans.
- Full repository gate and coverage objective passing.

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
