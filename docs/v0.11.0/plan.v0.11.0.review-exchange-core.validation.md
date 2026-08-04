# v0.11.0 review-exchange-core implementation tracking and validation

No, it is not implemented.

This validation records Step 1 as complete; Steps 2 through 5 have not yet been implemented.

---

## File-based IO cost clarification for v0.11.0 review-exchange-core implementation

All implementation checks must verify the IO contract from `docs/v0.11.0/plan.v0.11.0.review-exchange-core.md`:

- Operations receive one exact reviewed-document path and derive a constant path set once.
- Status and waiting read only the expected transient and coordination paths.
- Waiting never scans, rereads the transcript, or renews a lease.
- Before append, idempotent transcript repair persists the pre-append byte offset and stable entry identifier; repair reads only from that offset, truncates a torn suffix when needed, and never loads transcript history.
- Recovery touches only the fixed artifacts for the selected identity.

---

## Complexity bound clarification for v0.11.0 implementation

- **O(1) per state operation and wait poll** over a constant exact path set.
- **O(k) serialization** only in the content currently read or written.
- **O(r) recovery** over the fixed artifacts for one identity.

Every step's performance check must reject project-tree scans, transcript-history reads, and quadratic round processing.

---

## Step 1. Typed identity, configuration, envelopes, and derived paths

### Analysis of Step 1 implementation state

Yes. Step 1 has been fully implemented.

The repository now contains the validated protocol model, coordination, envelope, configuration, path derivation, and Git-ignore activation primitives required by Step 1, with focused unit and property tests and a green global gate.

### Goal for Step 1

Create validated exchange identity, context, configuration, envelope, coordination-record, and exact derived-path primitives, including effective Git-ignore gating.

### Step 1 improvement expectations

- Every artifact and summary shares one complete, validated identity.
- Invalid configuration or identity fails before writes.
- Specification and intentional `code.code` paths are distinct and stable.
- Property tests cover identity/path round trips and collision resistance.

### What was implemented for Step 1

- **Typed identity and policy**: added immutable exchange identity, review context, family policy, actor, status, disposition, outcome, transition, archive, and artifact-state models with strict serialization and validation.
- **Configuration and timestamps**: added opt-in `a.review-mode` loading, the 1,800-second default, positive override validation, and local ISO-8601 timestamps with numeric offsets.
- **Coordination and envelopes**: split durable coordination state and fenced-JSON envelopes into focused modules, including impossible-state rejection and machine-to-human summary identity validation.
- **Derived paths and activation**: added constant exact path derivation, round-trip parsing, archive naming, intentional `code.code` support, repository validation, and one effective `git check-ignore` call covering every transient path.
- **Package surface**: exported the public protocol types from `tools/__init__.py` without exposing path-adapter internals.
- **Validation evidence**: focused model and path tests pass, the tree-scan grep finds no `rglob`, `glob`, or `iterdir` use in the four production modules, and `ghog day` completed with 1,300 passing tests, 100% coverage, zero outliers, zero exclusions, and `exit=0`.

### Step 1 implementation-to-plan variances

The protocol model was split preemptively into `tools/review_exchange_models.py`, `tools/review_exchange_models_coordination.py`, and `tools/review_exchange_models_envelope.py`. The latter two production modules make the line-budget split explicit rather than waiting for the combined model to approach the ceiling.

`tests/unit/tools/test_review_exchange_models/test_review_exchange_models_validation_tdd.py` was added as a separate validation-focused leaf so invalid field shapes and coordination invariants do not overload the primary model test module.

`tools/__init__.py` gained 36 export lines for the stable public protocol classes. This follows the repository's public-class export convention; the plan's earlier statement that the package needed no export growth was incorrect.

### Repository-wide supporting changes included with Step 1

- `.vscode/settings.json`: added spell-checker vocabulary used by the protocol and review documentation.
- `tools/open_questions_md.py` and `tests/unit/tools/test_open_questions_md.py`: kept open-question document lookup compatible with the versioned documentation layout and added the matching rejection coverage.
- `tests/unit/tools/test_prompt_workflow_docs/__init__.py` and `tests/unit/tools/test_prompt_workflow_docs/test_prompt_workflow_docs_document_lookup_tdd.py`: split document-lookup coverage into a focused test leaf.
- `tests/unit/tools/test_prompt_workflow_main.py`: preserved prompt-workflow missing-document coverage after the document-test split.
- `tests/unit/tools/test_instruction_structure/__init__.py`, `tests/unit/tools/test_instruction_structure/test_instruction_structure_tdd.py`, and `tests/unit/tools/test_instruction_structure/test_instruction_structure_prompt_workflow_tdd.py`: split instruction-structure coverage without changing its assertions.
- `tests/unit/tools/test_instruction_structure/test_codex_plugin_structure_tdd.py` and `tests/unit/tools/test_prompt_workflow_integration.py`: moved repeated repository setup out of measured calls while retaining the structural and integration assertions.
- `tests/unit/tools/sensitive_history/test_sensitive_commit_check.py` and `tests/unit/tools/sensitive_history/test_install_hooks.py`: moved repeated real-Git setup into fixtures while retaining the original checks.
- `tests/unit/tools/prepare_release/test_prepare_release_plan_workflow.py` and `tests/unit/tools/prepare_release/test_prepare_release_plan_git.py`: reused fixture-level repositories for the same release-plan and Git assertions.

### New types or classes introduced for Step 1

- `ReviewExchangeError`: stable fail-closed validation error.
- `ReviewFamily`, `ReviewRole`, `CoordinationStatus`, `ReviewDisposition`, `ConfirmationOutcome`, `Actor`, `IncompleteTransitionKind`, `ArtifactState`, and `ArchiveKind`: closed protocol vocabularies.
- `ExchangeIdentity` and `ReviewContext`: canonical exchange identity and review-summary context.
- `FamilyPolicy`: immutable family convergence signal and confirmation-label mapping.
- `ReviewConfiguration`: marker-backed activation and bounded-wait configuration.
- `ArtifactPaths`: constant transcript and transient path set.
- `CoordinationRecord`: durable recovery, progress, escalation, and confirmation state.
- `Envelope`: machine-readable review artifact metadata.

### Architecture check for Step 1

- **Protocol model boundary**: `review_exchange_models.py` contains value types and standard-library validation only; it does not depend on persistence or workflow orchestration.
- **Focused model splits**: coordination and envelope modules depend on the protocol foundation, while the foundation does not import them, keeping dependency direction acyclic.
- **Adapter boundary**: `review_exchange_paths.py` owns filesystem naming and the injected Git command boundary; protocol types remain independent of Git subprocess details.
- **Package surface**: `tools/__init__.py` re-exports stable public models without moving adapter behavior into the package root.
- **Maintainability**: all new production modules stay below the plan's 550-line safe target after the coordination and envelope splits.

No, there is nothing that needs to be addressed for Step 1.

### Performance check for Step 1

- **No new `O(n^2)` or `O(n log n)` path**: identity checks, state validation, and path derivation operate over fixed fields and a constant path tuple.
- **Hot-path bound**: deriving or parsing one exchange path is `O(1)` in the number of artifacts and `O(k)` only in the bounded identity text being processed.
- **Activation bound**: Git repository validation and ignore coverage use bounded commands, with all transient paths supplied to one `git check-ignore` call.
- **Plan-bound alignment**: the required grep confirms the production path contains no project-tree scan.

No, there is no performance issue that needs to be addressed for Step 1.

### Unit test coverage check for Step 1

- **Protocol models**: test-driven and validation-focused suites cover valid round trips, every invalid field shape, impossible coordination states, configuration failures, timestamp constraints, and summary mismatches.
- **Identity properties**: Hypothesis tests cover exact JSON round trips and collision resistance across distinct identities.
- **Path adapter**: unit tests cover both families, intentional `code.code` names, archive kinds, parse-back behavior, non-Git failure, ignore gaps, bounded subprocess arguments, and Git diagnostic failures.
- **Coverage evidence**: focused affected coverage and the final full suite both report 100% coverage.

No, there is no unit-tested class below 100% that needs completing for Step 1.

### Feature integrity for Step 1

- **Existing workflow behavior**: focused regression tests preserve open-question document lookup and prompt-workflow missing-document handling after the small supporting refactor needed by the global gate.
- **Reporting and diagnostics**: invalid protocol input and Git activation failures produce stable diagnostics before any write.
- **Test-suite reliability**: slow structural and real-Git assertions were redesigned to keep the measured call phase deterministic while retaining repository setup and every assertion.
- **Compatibility**: review exchange behavior remains opt-in through `a.review-mode`; existing workflows are unchanged when the marker is absent.

No, no existing feature or reporting capability appears impaired by Step 1.

---

## Step 2. Atomic artifact store, transcript, tombstone, and archive primitives

### Analysis of Step 2 implementation state

Not started. Step 2 is not implemented because the artifact store, templates, and focused storage tests do not exist yet.

### Goal for Step 2

Implement atomic exact-path storage, short transition locks, idempotent append-only transcripts, consumed-request tombstones, evidence archives, and role-neutral templates.

### Step 2 improvement expectations

- Partial publication and append failures remain recoverable.
- A torn transcript append is truncated to the persisted pre-append offset and regenerated exactly once.
- Request removal precedes answer visibility without destroying evidence.
- Agents append complete entries without reading transcript history.
- Family transcript templates initialize only missing transcripts.

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

## Step 3. Lifecycle state machine, bounded waits, repair, escalation, and confirmation

### Analysis of Step 3 implementation state

Not started. Step 3 is not implemented because the lifecycle classifier, transitions, wait policy, repair, escalation, and confirmation service do not exist yet.

### Goal for Step 3

Implement every observable state and safe transition, bounded waiting and abandonment, automated round control, escalation, durable convergence confirmation, and idempotent owning-action authorization replay.

### Step 3 improvement expectations

- Every reachable state is classified or fails closed.
- Waiting is bounded and polls never renew a dead actor's lease.
- One in-process monotonic wait exposes periodic progress callbacks without persisted wall-time slices.
- Every transcript-appending transition repairs from its persisted pre-append offset and target entry identity.
- Intermediate rounds stay automated while convergence alone waits for a human.
- Interrupted human-authorized owning work resumes without asking the human twice.

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

## Step 4. Non-interactive utility, templates, and canonical requestor adapters

### Analysis of Step 4 implementation state

Not started. Step 4 is not implemented because the CLI, launcher, canonical requestor instruction, adapters, and their focused tests do not exist yet.

### Goal for Step 4

Expose all core operations through one stable non-interactive launcher and one canonical requestor instruction with provider-specific redirect-only adapters.

### Step 4 improvement expectations

- Later roles call one shared utility instead of reproducing protocol mechanics.
- CLI status and exit codes are stable and machine-readable.
- Wait progress is emitted only on standard error and exactly one final JSON result is emitted on standard output.
- Caller-owned substantive input files are accepted only under the effectively ignored project-root `a.*` convention.
- Every request summary validates umbrella, exact document or plan/step, and round.
- Provider Markdown contains no copy of the canonical instruction body.

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

## Step 5. Integrated acceptance and rollout verification

### Analysis of Step 5 implementation state

Not started. Step 5 is not implemented because the temporary-repository end-to-end acceptance suite does not exist yet.

### Goal for Step 5

Validate the public core boundary across real Git repositories, both artifact families, subprocess interruption and repair, automated rounds, escalation, and both convergence outcomes.

### Step 5 improvement expectations

- Opt-in activation and effective-ignore failure behave correctly in consuming repositories.
- Cross-document isolation and same-document exclusion hold across process boundaries.
- Crash windows repair or escalate without losing evidence.
- Torn transcript appends truncate to the persisted offset and re-append exactly one complete entry across the acceptance boundary.
- Long waits expose periodic standard-error progress while producing one final standard-output JSON result under one monotonic deadline.
- Convergence confirmation, override guidance, and continuing authorization survive session interruption.

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
