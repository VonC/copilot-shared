# v0.11.0 review-resume-command implementation plan -- durable continuation

Implement configurable review evidence, role-specific LLM identity, and safe
continuation through ordered protocol slices.

- **Placement first**: centralize artifact discovery and complete legacy
  migration before changing exchange schemas.
- **One ownership contract**: add the generation and token-digest fence as its
  own cross-cutting step for ordinary and resumed actors.
- **Role-specific continuation**: finish with status integration, the LLM-only
  resume skill, persistent reviewer waiting, and full acceptance coverage.

## Plan goal for v0.11.0 review-resume-command

Implement the complete behavior from
`docs/v0.11.0/design.v0.11.0.review-resume-command.md` and its consolidated
feature request without reopening the settled choices.

- **Step 0 goal**: add time-bound and complexity guards before production work.
- **Step 1 goal**: implement the artifact-home declaration, registry, placement
  check, transactional migration, and locator adoption.
- **Step 2 goal**: add LLM-nature detection, strict two-role snapshots, legacy
  reconciliation, and missing-only backfill.
- **Step 3 goal**: implement uniform ownership capabilities and reject displaced
  or competing actors safely.
- **Step 4 goal**: advance review status to schema 2 with migration and role
  nature in human and machine output.
- **Step 5 goal**: add the LLM-only resume skill, role resolution, global
  reviewer wait, and requestor continuation.
- **Step 6 goal**: prove the complete feature through real launchers, concurrent
  sessions, migration recovery, adapters, and documentation acceptance tests.

---

## Scope anchors for v0.11.0 review-resume-command plan

This plan implements these settled outcomes:

1. Every protocol-owned runtime artifact resolves through one repository-local
   home, defaulting to `.reviews`, and legacy layouts migrate all or none.
2. Every new exchange preserves requestor and reviewer LLM nature while legacy
   evidence remains readable and can be completed by its owning role.
3. Direct resume resolves the role and continues immediately, while reviewers
   consume any future request and requestors progress only their owning task.
4. Every acting session uses the same generation and secret-token capability,
   with only the digest stored in coordination.

The following are in scope:

- `.review-artifacts.ini`, the explicit artifact registry, local ignore
  coverage, migration journal, recovery, and collision diagnostics;
- Claude, Codex, Gemini, and `unknown` host evidence;
- status schema 2 and the bounded status migration exception;
- request, answer, coordination, retained, consumed, transcript, wait, and
  continuation identity updates;
- an LLM skill with thin Claude, Codex, Gemini, and GitHub-compatible adapters;
- exact requestor continuation and identity-free reviewer waiting;
- existing specification, code-review, status, prompt-workflow, adapter, and
  documentation regression suites.

The following remain outside this plan:

- moving versioned review transcripts out of `docs`;
- a repository-root, batch, or shell `rvw_resume` command;
- automatic ordering of several available requests;
- replacing conflicting recorded LLM nature;
- reopening completed documents or umbrella status rows from earlier topics.

---

## Complexity bound clarification for v0.11.0 review resumption

- **O(1) amortized per file-system event**: directory notifications only mark
  the reviewer wait dirty; they never perform projection work in the callback.
- **O(n) per placement or status phase**: each recognized artifact in the three
  inspected locations is parsed, fingerprinted, or projected a bounded number
  of times.
- **O(n) per selected occurrence backfill**: selected-role evidence is scanned
  once before any rewrite and committed once after validation.
- **O(1) per transition**: ownership generation and token-digest checks operate
  on one coordination record under its transition lock.

No implementation may add pairwise artifact comparison, recursive repository
search, repeated full status projection inside `migration_check`, or event-loop
work with `O(n log n)` or `O(n^2)` cost.

---

## File-based IO cost clarification for v0.11.0 review resumption

| Flow | Reads | Writes | Bound |
| --- | --- | --- | --- |
| Artifact location | Optional root declaration and Git tracking evidence | None | One small configuration read per loaded workflow context; cache within one invocation. |
| Migration check | Root, default home, configured home, and registered candidate headers | None | Three non-recursive directory reads and one pass over recognized candidates; no status projection. |
| Migration | Validated source set and journal recovery state | Home ignore file, journal, atomic moves | One journaled transaction; no copy of unrelated files and no partial destination layout. |
| Status | Ready artifact home and active coordination candidates | Migration only when preflight requires it | One placement preflight followed by one ordinary read-only projection. |
| Role backfill | Selected occurrence and selected-role artifacts | Missing nature fields and one transcript completion entry | One pre-scan and one atomic missing-only commit; no repository-wide rewrite. |
| Ownership | One coordination record | One locked generation and digest transition | Constant work per actor claim or mutation. |
| Global reviewer wait | Request-artifact directory events and bounded rescans | Claim only after selection | Event hints plus bounded polling; full parse only for recognized request candidates. |

The runtime loading path must use the declaration and locator as a tiny index
read rather than repeatedly loading every artifact. Transcripts remain outside
the runtime artifact-home scan.

---

## Confirmed technical facts for v0.11.0 plan viability

**Relevant Python files over the 650-line repository limit**:

- None. No currently relevant production Python file exceeds 650 physical
  lines.

**Relevant Python files in the 550-through-650 risk band**:

- `tools/review_exchange_store.py`: 633 lines. Add no new ownership or migration
  responsibility in place; extract storage helpers into new modules.
- `tools/review_exchange_cli.py`: 558 lines. Add no resume or capability branch
  in place; route those operations through a new CLI support module.
- `tools/review_exchange_models.py`: 555 lines. Keep new nature and ownership
  records in focused modules and reduce imports if this file would grow.
- `tests/unit/tools/test_review_exchange_cli/test_review_exchange_cli_tdd.py`:
  615 lines. Put new capability and resume CLI cases in new test leaves.
- `tests/unit/tools/test_review_exchange_acceptance/test_review_exchange_acceptance_tdd.py`:
  604 lines. Put the new end-to-end scenarios under `tests/acceptance/review_resume`.

**Relevant Python files below 550 and safe to extend**:

- `tools/review_exchange_core.py`: 462 lines.
- `tools/review_exchange_paths.py`: 231 lines.
- `tools/review_exchange_models_envelope.py`: 220 lines.
- `tools/review_exchange_models_coordination.py`: 238 lines.
- `tools/review_exchange_state.py`: 277 lines.
- `tools/review_exchange_wait.py`: 209 lines.
- `tools/review_exchange_observer.py`: 196 lines.
- `tools/review_exchange_cli_parser.py`: 132 lines.
- `tools/review_status.py`: 509 lines; prefer focused migration and role-nature
  helpers before this file enters the risk band.
- `tools/review_status_models.py`: 408 lines.
- `tools/review_status_render.py`: 119 lines.
- `tools/review_status_cli.py`: 103 lines.
- `tools/prompt_workflow_render.py`: 88 lines.

**New production modules for v0.11.0**:

- `tools/review_artifact_configuration.py`.
- `tools/review_artifact_registry.py`.
- `tools/review_artifact_migration.py`.
- `tools/llm_nature.py`.
- `tools/review_role_nature.py`.
- `tools/review_exchange_ownership.py`.
- `tools/review_exchange_ownership_store.py`.
- `tools/review_exchange_cli_ownership.py`.
- `tools/review_status_migration.py`.
- `tools/review_status_role_nature.py`.
- `tools/review_resume.py`.
- `tools/review_resume_wait.py`.
- `tools/review_exchange_cli_resume.py`.

**Other facts affecting the plan**:

- `rvw_status.bat` is the existing public status launcher; status remains the
  only command allowed to migrate as part of ordinary reporting.
- `bin/review_exchange.bat` is the shared protocol command surface; support
  operations may be added there, but no `rvw_resume` launcher may be created.
- Provider Markdown files are thin pointers to canonical instructions and must
  follow `rules/llm-specific-adapters.md`.
- Existing exact waits require a complete identity and bounded timeout; the
  global request watcher is a separate operation.
- Existing schemas are strict, so legacy and schema-2 parsing must be explicit
  rather than accepting unknown fields broadly.

---

## Current test-tree validation snapshot for v0.11.0 review resumption

Existing packages that must remain green:

- `tests/unit/tools/test_review_exchange_paths` for derivation and ignore
  validation.
- `tests/unit/tools/test_review_exchange_models` for strict envelope and
  coordination schemas.
- `tests/unit/tools/test_review_exchange_store` and
  `tests/unit/tools/test_review_exchange_lifecycle` for persistence, transition,
  recovery, and transcript behavior.
- `tests/unit/tools/test_review_exchange_cli` for command input and result
  contracts.
- `tests/unit/tools/test_review_status*` and `tests/acceptance/review_status` for
  status schema, projection, rendering, CLI, and launcher behavior.
- `tests/unit/tools/test_spec_review_requestor_acceptance`,
  `test_spec_reviewer_acceptance`, `test_code_review_requestor_acceptance`, and
  `test_code_reviewer_acceptance` for role workflows.
- `tests/unit/tools/test_prompt_workflow_skill` and
  `test_instruction_structure` for routing and thin adapters.
- `tests/unit/tools/test_review_mode_docs_acceptance` for documented public
  behavior.

New test leaves:

- `tests/unit/tools/test_review_resume_perf`.
- `tests/unit/tools/test_review_artifact_home`.
- `tests/unit/tools/test_llm_nature`.
- `tests/unit/tools/test_review_role_nature`.
- `tests/unit/tools/test_review_exchange_ownership`.
- `tests/unit/tools/test_review_status_migration`.
- `tests/unit/tools/test_review_resume`.
- `tests/unit/tools/test_review_resume_instruction`.
- `tests/acceptance/review_resume/test_review_resume_acceptance`.

Property tests are required for normalized repository-relative paths, artifact
registry round trips, role snapshot reconciliation, and monotonic ownership
generations. Time-bound examples are a better fit than property tests for file
notifications and process waits.

---

## Runtime file note for v0.11.0 review resumption

- `.review-artifacts.ini` is optional versioned configuration and is not a
  runtime artifact.
- `.reviews/.gitignore` is generated before first use and remains untracked
  under its own catch-all rule.
- `.reviews/*` contains only registered runtime artifacts, including the
  migration lock and journal.
- Caller-owned renderer inputs remain outside protocol artifact paths until all
  producing workflows are migrated through the shared locator.
- `docs/.../review.*.md` transcripts remain versioned beside reviewed documents.

---

## Shared execution command checklist for all v0.11.0 review-resume steps

Apply this checklist to every numbered step with its exact paths.

1. Count physical lines before edits for every involved file.
2. Add or update the step tests before production behavior.
3. Run `ghog single` with all focused test files for the step.
4. Run the step-specific `rg` checks for fields, operations, paths, instructions,
   adapters, and prohibited root assumptions.
5. Run `ghog day` repeatedly until it reports the objective with `exit=0`.
6. Count physical lines after edits and compare every Python file with its
   baseline, policy band, advisory estimate, and 650-line ceiling.
7. Stop and perform the stated responsibility split if a Python file exceeds
   650 lines.
8. Record advisory variance without marking the step incomplete when the file
   remains at or below 650.

## Ready-to-run commands for all v0.11.0 review-resume steps

- Physical line count: `(Get-Content -LiteralPath '<path>').Count`
- Targeted tests: `ghog single <step-test-files>`
- Grep checks: `rg -n '<step-pattern>' <step-paths>`
- Shared gate loop: `ghog day`, repeated until it reports `exit=0`
- Physical line recount: `(Get-Content -LiteralPath '<path>').Count`

---

## Numbered implementation steps for v0.11.0 review resumption

### Step 0. Establish migration and wait performance guards

#### Step 0 analysis and intent for bounded preflight behavior

Issues to address:

- `migration_check` must remain materially cheaper than full status collection.
- The open-ended reviewer wait must not busy-loop or depend solely on native
  events.
- No test currently guards the three-location scan or quiet-wait cost.

Fix intent:

- Add strict xfail performance and call-bound tests before production modules
  exist.
- Assign every gate to the step that removes its xfail marker.

Expected outcome:

- Migration tests fail if status projection is called or discovery becomes
  recursive.
- Wait tests fail if a quiet interval performs unbounded rescans or misses the
  polling fallback.

Step framing:

- Design link: Complexity bound and file-based IO cost clarifications.
- Execution checklist reference: Shared execution command checklist for all
  v0.11.0 review-resume steps.

#### Step 0 implementation for performance guards

**Files involved**:

- `tests/unit/tools/test_review_resume_perf/__init__.py` (new, to be created).
- `tests/unit/tools/test_review_resume_perf/test_review_resume_perf_tdd.py` (new,
  to be created).

**Tests first**:

- Mark strict xfail tests with `pytest.mark.timeout` for three non-recursive
  placement reads, linear candidate parsing, quiet global waiting, notification
  wake, polling fallback, and no full status call from migration check.
- Keep synthetic fixture sizes deterministic and assert call counts as well as
  elapsed bounds.

**Classes and behavior**:

- Test-only spies model configuration reads, directory enumeration, candidate
  parsing, status projection, notification hints, and fallback polls.

**Completion criteria**:

- `ghog single tests/unit/tools/test_review_resume_perf/test_review_resume_perf_tdd.py`
  passes with only the declared strict xfails.
- `rg -n "xfail|timeout|migration|notification|poll" tests/unit/tools/test_review_resume_perf`
  lists every gate and owning step.
- `ghog day` reports `exit=0`.

#### Step 0 addendums for performance guards

Line-budget checkpoint:

- `tests/unit/tools/test_review_resume_perf/__init__.py`: before 0; below-550
  safe; ceiling 650; expected at or below 5 lines (advisory).
- `tests/unit/tools/test_review_resume_perf/test_review_resume_perf_tdd.py`:
  before 0; below-550 safe; ceiling 650; expected at or below 260 lines
  (advisory).

Split guidance:

- Split notification timing into a sibling conventional test leaf if the test
  file approaches 550 lines; do not loosen timeouts to hide repeated IO.

Full workflow timing run readiness:

- `tests/unit/tools/test_review_resume_perf/test_review_resume_perf_tdd.py`;
  `ghog day`.

Time-gated status for Step 0:

- Strict xfails remain until Step 1 owns migration gates and Step 5 owns global
  wait gates.

---

### Step 1. Centralize artifact-home placement and migration

#### Step 1 analysis and intent for one runtime evidence home

Issues to address:

- Runtime paths are derived at the project root and status enumerates root-level
  coordination files.
- There is no strict versioned declaration, kind registry, home-local ignore
  coverage, or all-or-none migration recovery.
- The 633-line store module cannot absorb migration responsibility.

Fix intent:

- Add focused configuration, registry, and migration modules and route all
  exchange path derivation through them.
- Keep journal, rollback, collision checks, and home creation outside the store.
- Remove Step 0 migration xfails.

Expected outcome:

- Default and configured homes produce identical canonical runtime paths.
- Root/default/configured evidence migrates in one recoverable transaction or
  remains wholly at source.

Step framing:

- Design link: Versioned artifact-home declaration through transactional
  migration.
- Execution checklist reference: Shared execution command checklist for all
  v0.11.0 review-resume steps.

#### Step 1 implementation for artifact placement

**Files involved**:

- `tools/review_artifact_configuration.py` (new, to be created).
- `tools/review_artifact_registry.py` (new, to be created).
- `tools/review_artifact_migration.py` (new, to be created).
- `tools/review_exchange_paths.py` (existing, to be updated).
- `tools/review_exchange_core.py` (existing, to be updated).
- `tools/review_exchange_store.py` (existing, to be updated only for delegation).
- `tools/review_exchange_observer.py` (existing, to be updated).
- `tests/unit/tools/test_review_artifact_home/__init__.py` (new, to be created).
- `tests/unit/tools/test_review_artifact_home/test_review_artifact_configuration_tdd.py`
  (new, to be created).
- `tests/unit/tools/test_review_artifact_home/test_review_artifact_registry_tdd.py`
  (new, to be created).
- `tests/unit/tools/test_review_artifact_home/test_review_artifact_registry_pbt.py`
  (new, to be created).
- `tests/unit/tools/test_review_artifact_home/test_review_artifact_migration_tdd.py`
  (new, to be created).
- `tests/unit/tools/test_review_exchange_paths/test_review_exchange_paths_tdd.py`
  (existing, to be updated).
- `tests/unit/tools/test_review_exchange_store/test_review_exchange_store_validation_tdd.py`
  (existing, to be updated).

**Tests first**:

- Cover absent and valid declaration, every invalid path class, symlink escape,
  tracked-directory rejection, duplicate keys, and portable relative output.
- Cover every registered artifact kind, role attribution, identity parser,
  transcript exclusion, and unrelated `a.*` rejection; property-test registry
  render/parse round trips.
- Cover new-home ignore creation and Git verification, existing uncovered home,
  multi-source merge, collision, byte mismatch, journal rollback, committed
  cleanup, repeated check, and repeated migration.
- Update path and store tests so no runtime artifact assumes `PRJ_DIR` directly.
- Remove the Step 0 migration xfails without changing their bounds.

**Classes and behavior**:

- `ReviewArtifactConfiguration`: strict `.review-artifacts.ini` parsing and
  repository-boundary validation.
- `ReviewArtifactRegistry`: closed artifact-kind metadata and name parsing.
- `ReviewArtifactLocator`: home-aware derivation replacing direct root joins.
- `MigrationCheckResult` and `ReviewArtifactMigration`: ready,
  migration-required, blocked, journaling, rollback, and recovery.

**Completion criteria**:

- `ghog single tests/unit/tools/test_review_resume_perf/test_review_resume_perf_tdd.py tests/unit/tools/test_review_artifact_home tests/unit/tools/test_review_exchange_paths tests/unit/tools/test_review_exchange_store/test_review_exchange_store_validation_tdd.py`
  passes.
- `rg -n "project_root /.*review|glob\(.*review-active" tools/review_exchange_* tools/review_status.py`
  finds no runtime path bypass outside the registry implementation.
- `ghog day` reports `exit=0`.

#### Step 1 addendums for artifact placement

Line-budget checkpoint:

- New production modules: before 0; below-550 safe; ceiling 650; configuration
  target 220, registry 320, migration 480 lines (advisory).
- `tools/review_exchange_paths.py`: before 231; below-550 safe; ceiling 650;
  expected at or below 300 lines (advisory).
- `tools/review_exchange_core.py`: before 462; below-550 safe; ceiling 650;
  expected at or below 500 lines (advisory).
- `tools/review_exchange_store.py`: before 633; risk band; ceiling 650; target at
  or below 620 only because migration-related path logic is extracted.
- `tools/review_exchange_observer.py`: before 196; below-550 safe; ceiling 650;
  expected at or below 230 lines (advisory).
- New artifact-home tests: before 0; each below-550 safe; ceiling 650; each
  expected at or below 450 lines (advisory).
- Existing path test: before 350; below-550 safe; ceiling 650; expected at or
  below 470 lines (advisory).

Split guidance:

- Do not grow `review_exchange_store.py`; move all journal and migration IO into
  `review_artifact_migration.py` and storage seams into focused helpers.
- Split migration recovery tests from ordinary migration examples before either
  test file reaches 550 lines.

Full workflow timing run readiness:

- Step 1 focused tests listed above; `ghog day`.

Time-gated status for Step 1:

- Migration-check performance gates are active and no longer xfailed.

---

### Step 2. Add role-specific LLM nature and legacy completion

#### Step 2 analysis and intent for host identity evidence

Issues to address:

- Host detection silently defaults to Claude and has no Gemini or `unknown`.
- Strict envelopes and coordination records carry roles but no role-nature map.
- Legacy evidence needs complete selected-role scanning and atomic missing-only
  completion without changing counterpart evidence or conflicts.

Fix intent:

- Add focused detector and reconciliation modules, then extend strict schemas
  and transcript publication with two-role snapshots.
- Keep legacy parsing explicit and append transcript completion entries with
  unique role and occurrence headings.

Expected outcome:

- New exchanges preserve both role natures as they become known.
- Legacy selected-role evidence is classified and completed exactly once, while
  conflicts and `unknown` follow the settled rules.

Step framing:

- Design link: LLM-nature detection through legacy role evidence and backfill.
- Execution checklist reference: Shared execution command checklist for all
  v0.11.0 review-resume steps.

#### Step 2 implementation for role identity

**Files involved**:

- `tools/llm_nature.py` (new, to be created).
- `tools/review_role_nature.py` (new, to be created).
- `tools/review_exchange_models_envelope.py` (existing, to be updated).
- `tools/review_exchange_models_coordination.py` (existing, to be updated).
- `tools/review_exchange_publication.py` (existing, to be updated).
- `tools/review_exchange_transcript_identity.py` (existing, to be updated).
- `tools/prompt_workflow_render.py` (existing, to be updated).
- `tests/unit/tools/test_llm_nature/__init__.py` (new, to be created).
- `tests/unit/tools/test_llm_nature/test_llm_nature_tdd.py` (new, to be created).
- `tests/unit/tools/test_review_role_nature/__init__.py` (new, to be created).
- `tests/unit/tools/test_review_role_nature/test_review_role_nature_tdd.py` (new,
  to be created).
- `tests/unit/tools/test_review_role_nature/test_review_role_nature_pbt.py` (new,
  to be created).
- `tests/unit/tools/test_review_exchange_models/test_review_exchange_models_tdd.py`
  (existing, to be updated).
- `tests/unit/tools/test_review_exchange_models/test_review_exchange_models_validation_tdd.py`
  (existing, to be updated).
- `tests/unit/tools/test_review_exchange_lifecycle/test_review_exchange_transcript_identity_tdd.py`
  (existing, to be updated).

**Tests first**:

- Cover trusted host hint precedence, Claude, Codex, Gemini, no evidence,
  conflicting evidence, and non-persistence of secret environment values.
- Cover legacy absent field, `null`, all supported enums, unknown, strict unknown
  values, requestor-first and reviewer-later snapshots, and preservation across
  transitions.
- Property-test reconciliation ordering and complete conflict collection.
- Cover current-role missing-only backfill, counterpart omission, conflict
  Override and Stop, unknown no-backfill, atomic failure, unique transcript
  completion headings, and idempotent repeats.

**Classes and behavior**:

- `LlmNature` and `LlmNatureDetector`: closed nature and evidence result.
- `RoleNatureSnapshot`: strict requestor/reviewer map with legacy parser.
- `RoleNatureReconciler` and `RoleNatureBackfill`: selected-occurrence scan,
  conflict result, atomic mutable upgrades, and transcript completion.

**Completion criteria**:

- `ghog single tests/unit/tools/test_llm_nature tests/unit/tools/test_review_role_nature tests/unit/tools/test_review_exchange_models tests/unit/tools/test_review_exchange_lifecycle/test_review_exchange_transcript_identity_tdd.py`
  passes.
- `rg -n "default.*claude|CLAUDECODE|CODEX_THREAD_ID|role_natures" tools instructions`
  shows centralized detection and schema use without a silent Claude fallback.
- `ghog day` reports `exit=0`.

#### Step 2 addendums for role identity

Line-budget checkpoint:

- New detector and role modules: before 0; below-550 safe; ceiling 650; expected
  at or below 180 and 420 lines respectively (advisory).
- Envelope model: before 220; below-550 safe; ceiling 650; expected at or below
  300 lines (advisory).
- Coordination model: before 238; below-550 safe; ceiling 650; expected at or
  below 330 lines (advisory).
- Publication: before 358; below-550 safe; ceiling 650; expected at or below 430
  lines (advisory).
- Transcript identity: before 46; below-550 safe; ceiling 650; expected at or
  below 110 lines (advisory).
- Prompt renderer: before 88; below-550 safe; ceiling 650; expected at or below
  120 lines (advisory).
- New tests: before 0; each below-550 safe; ceiling 650; expected at or below 450
  lines (advisory).
- Existing model test: before 470; below-550 safe; ceiling 650; expected at or
  below 540 lines (advisory); put new validation cases in its existing 359-line
  sibling before crossing the risk band.

Split guidance:

- Keep backfill transaction IO separate from pure reconciliation.
- Add a new schema-v2 test leaf rather than growing any existing test beyond
  650 lines.

Full workflow timing run readiness:

- Step 2 focused tests listed above; `ghog day`.

Time-gated status for Step 2:

- No Step 0 time gate changes; identity work is bounded by artifact count.

---

### Step 3. Fence every acting session with ownership capabilities

#### Step 3 analysis and intent for safe transition ownership

Issues to address:

- Fresh-lease pickup can displace a live session without a mechanical fence.
- Ordinary and resumed actors need one claim contract, and plaintext tokens must
  never be recoverable from coordination.
- CLI and store files are already in the risk band.

Fix intent:

- Add focused ownership, ownership-store, and CLI support modules.
- Claim on start, reclaim, actor wake, and selected global request; require the
  generation and secret on every mutation and store only the digest.
- Keep all new branches outside risk-band files except narrow delegation.

Expected outcome:

- Stale, missing, or invalid capabilities fail before mutation.
- Direct resume advances ownership while ordinary workflows still claim and
  complete normally.

Step framing:

- Design link: Lease-independent pickup and displaced sessions, Q05.
- Execution checklist reference: Shared execution command checklist for all
  v0.11.0 review-resume steps.

#### Step 3 implementation for ownership fencing

**Files involved**:

- `tools/review_exchange_ownership.py` (new, to be created).
- `tools/review_exchange_ownership_store.py` (new, to be created).
- `tools/review_exchange_cli_ownership.py` (new, to be created).
- `tools/review_exchange_models_coordination.py` (existing, to be updated).
- `tools/review_exchange_state.py` (existing, to be updated).
- `tools/review_exchange_core.py` (existing, to be updated).
- `tools/review_exchange_store.py` (existing, to be reduced to delegation).
- `tools/review_exchange_wait.py` (existing, to be updated).
- `tools/review_exchange_cli_parser.py` (existing, to be updated).
- `tools/review_exchange_cli.py` (existing, to be reduced to delegation).
- `tests/unit/tools/test_review_exchange_ownership/__init__.py` (new, to be
  created).
- `tests/unit/tools/test_review_exchange_ownership/test_review_exchange_ownership_tdd.py`
  (new, to be created).
- `tests/unit/tools/test_review_exchange_ownership/test_review_exchange_ownership_pbt.py`
  (new, to be created).
- `tests/unit/tools/test_review_exchange_ownership/test_review_exchange_ownership_cli_tdd.py`
  (new, to be created).
- `tests/unit/tools/test_review_exchange_lifecycle/test_review_exchange_lifecycle_recovery_tdd.py`
  (existing, to be updated).
- `tests/unit/tools/test_review_exchange_cli/test_review_exchange_cli_boundaries_tdd.py`
  (existing, to be updated).

**Tests first**:

- Cover ordinary claim and mutation, actor handoff, digest-only coordination,
  wrong secret, stale generation, missing capability, duplicate claim,
  lease-independent pickup, lost secret pickup, convergence-gate pickup, and
  typed `ownership-superseded`.
- Cover generation and token flags as one required pair, including omitted,
  empty, malformed, duplicated, and mismatched values plus secret redaction from
  diagnostics and transcript output.
- Property-test strict generation increase and rejection of every earlier
  generation.
- Cover crash boundaries before and after capability persistence and require the
  transition lock for every compare-and-swap.
- Prove human rendering and transcripts never contain the secret.

**Classes and behavior**:

- `OwnershipCapability`, `OwnershipClaim`, and `OwnershipFailure` typed records.
- `OwnershipService`: token generation, digest comparison, ordinary claim,
  forced pickup, validation, and handoff invalidation.
- Ownership CLI support parses capability inputs and removes those branches from
  `review_exchange_cli.py`.

**Completion criteria**:

- `ghog single tests/unit/tools/test_review_exchange_ownership tests/unit/tools/test_review_exchange_lifecycle/test_review_exchange_lifecycle_recovery_tdd.py tests/unit/tools/test_review_exchange_cli/test_review_exchange_cli_boundaries_tdd.py`
  passes.
- `rg -n "ownership[-_](generation|token|digest)|ownership-superseded" tools tests/unit/tools/test_review_exchange_ownership`
  shows digest storage and typed fencing at every mutation seam.
- `ghog day` reports `exit=0`.

#### Step 3 addendums for ownership fencing

Line-budget checkpoint:

- New ownership modules: before 0; below-550 safe; ceiling 650; service target
  360, store target 260, CLI support target 220 lines (advisory).
- Coordination model: before the recorded Step 2 final count; use Step 2's
  below-550 or risk-band classification; ceiling 650; expected at or below 380
  lines after Step 3 (advisory).
- State: before 277; below-550 safe; ceiling 650; expected at or below 340 lines
  (advisory).
- Core: before the recorded Step 1 final count; use Step 1's recorded policy
  band; ceiling 650; expected at or below 540 lines (advisory).
- Store: before the recorded Step 1 final count; use Step 1's recorded risk band;
  mandatory target at or below 600 because ownership storage is explicitly
  extracted.
- Wait: before 209; below-550 safe; ceiling 650; expected at or below 290 lines
  (advisory).
- CLI parser: before 132; below-550 safe; ceiling 650; expected at or below 190
  lines (advisory).
- CLI: before 558; risk band; mandatory target at or below 540 because ownership
  dispatch is explicitly extracted.
- New ownership tests: before 0; each below-550 safe; ceiling 650; expected at or
  below 480 lines (advisory).
- Lifecycle recovery test: before 498; below-550 safe; ceiling 650; expected at
  or below 560 lines (advisory).

Split guidance:

- The store and CLI extraction targets are mandatory goals of this step; do not
  leave either risk-band file larger after adding ownership.
- Keep token cryptography and compare-and-swap storage in separate modules so
  neither new module approaches 550 lines.

Full workflow timing run readiness:

- Step 3 focused tests listed above; `ghog day`.

Time-gated status for Step 3:

- Add bounded concurrent-claim tests; no wall-clock wait longer than the focused
  test timeout.

---

### Step 4. Project migration and role nature through status schema 2

#### Step 4 analysis and intent for migration-aware diagnosis

Issues to address:

- Status schema 1 has no migration record or LLM nature and discovers only
  root-level coordination.
- `rvw_status` is documented as strictly read-only although safe migration is
  now its required bounded exception.
- The 509-line projection service should not absorb migration orchestration.

Fix intent:

- Add focused status migration and role-nature projection helpers.
- Advance machine output to schema 2 and update human rendering, exit mapping,
  canonical instruction, adapters, and acceptance fixtures.

Expected outcome:

- Status reports unnecessary or completed migration and both role natures.
- Blocked migration returns operational failure before ordinary projection;
  ready projection remains read-only.

Step framing:

- Design link: Status model and migration-aware reporting.
- Execution checklist reference: Shared execution command checklist for all
  v0.11.0 review-resume steps.

#### Step 4 implementation for schema-2 status

**Files involved**:

- `tools/review_status_migration.py` (new, to be created).
- `tools/review_status_role_nature.py` (new, to be created).
- `tools/review_status_models.py` (existing, to be updated).
- `tools/review_status.py` (existing, to be updated by delegation).
- `tools/review_status_render.py` (existing, to be updated).
- `tools/review_status_cli.py` (existing, to be updated).
- `rvw_status.bat` (existing, to be verified and updated only if arguments
  change).
- `instructions/review-status-command.md` (existing, to be updated).
- `.agent/workflows/review-status-command.md` (existing, to be updated).
- `.agents/llm-shared/skills/review-status-command/SKILL.md` (existing, to be
  updated).
- `.claude/skills/review-status-command/SKILL.md` (existing, to be updated).
- `.github/skills/review-status-command/SKILL.md` (existing, to be updated).
- `tests/unit/tools/test_review_status_migration/__init__.py` (new, to be
  created).
- `tests/unit/tools/test_review_status_migration/test_review_status_migration_tdd.py`
  (new, to be created).
- `tests/unit/tools/test_review_status_models/test_review_status_models_tdd.py`
  (existing, to be updated).
- `tests/unit/tools/test_review_status_projection/test_review_status_projection_tdd.py`
  (existing, to be updated).
- `tests/unit/tools/test_review_status_render/test_review_status_render_tdd.py`
  (existing, to be updated).
- `tests/unit/tools/test_review_status_cli/test_review_status_cli_tdd.py`
  (existing, to be updated).
- `tests/acceptance/review_status/test_review_status_acceptance/test_review_status_acceptance_tdd.py`
  (existing, to be updated).

**Tests first**:

- Cover schema 2 serialization, unnecessary/completed migration, moved count,
  relative home, requestor/reviewer nature, unrecorded, conflicting evidence,
  and evidence paths.
- Cover check, migrate, ready recheck ordering and no projection on blocked or
  failed migration.
- Update human and JSON snapshots plus status codes for normal, completed, and
  operational-failure cases.
- Prove status bytes are unchanged after the bounded preflight and repeated
  calls do not migrate twice.

**Classes and behavior**:

- `MigrationStatus`, schema-2 repository result fields, and role-nature status
  fields.
- `ReviewStatusMigrationPreflight`: shared check/migrate/recheck adapter.
- `ReviewStatusRoleNatureProjection`: reconcile snapshots into enum,
  `unrecorded`, or `conflicting` plus evidence.

**Completion criteria**:

- `ghog single tests/unit/tools/test_review_status_migration tests/unit/tools/test_review_status_models tests/unit/tools/test_review_status_projection tests/unit/tools/test_review_status_render tests/unit/tools/test_review_status_cli tests/acceptance/review_status/test_review_status_acceptance/test_review_status_acceptance_tdd.py`
  passes.
- `rg -n "schema_version.*2|migration|requestor_llm_nature|reviewer_llm_nature|strictly read-only" tools/review_status* instructions/review-status-command.md`
  shows schema-2 fields and no obsolete absolute read-only claim.
- `ghog day` reports `exit=0`.

#### Step 4 addendums for schema-2 status

Line-budget checkpoint:

- New status helpers: before 0; below-550 safe; ceiling 650; expected at or below
  240 lines each (advisory).
- Status models: before 408; below-550 safe; ceiling 650; expected at or below
  520 lines (advisory).
- Status service: before 509; below-550 safe; ceiling 650; expected at or below
  540 lines because helpers own all new projection and migration logic.
- Status render and CLI: before 119 and 103; below-550 safe; ceiling 650;
  expected at or below 180 and 150 lines (advisory).
- Status instruction and adapters: before 38 and 6-7 lines; non-Python; expected
  instruction at or below 90 and adapters at or below 10 lines (advisory).
- New migration test: before 0; below-550 safe; ceiling 650; expected at or below
  420 lines (advisory).
- Existing status tests: before 455, 155, 230, 330, and 291 lines; below-550 safe;
  ceiling 650; put schema-2 overflow in the new migration leaf before any file
  crosses 650.

Split guidance:

- Keep `review_status.py` below 550 if practical by delegating both new concerns.
- Split schema serialization tests before growing the 455-line models test into
  the risk band.

Full workflow timing run readiness:

- Step 4 focused tests listed above; `ghog day`.

Time-gated status for Step 4:

- Reuse the active migration-check bounds; status may add only one ordinary
  projection after a ready preflight.

---

### Step 5. Add LLM-only resume and persistent reviewer waiting

#### Step 5 analysis and intent for role-specific continuation

Issues to address:

- There is no public resume skill, role resolver, identity-free request wait, or
  several-reviewer race handling.
- Existing reviewer instructions stop at convergence and exact replacement
  waits, while the settled behavior is persistent across exchanges.
- Requestor resume must stay bound to its task and follow `pw skill` only after
  exchange release.

Fix intent:

- Add focused resume services and CLI support operations without adding a
  public resume launcher.
- Add one canonical resume instruction and thin adapters.
- Update all role instructions to carry nature, capability, global reviewer
  waiting, and exact requestor continuation.
- Remove Step 0 global-wait xfails.

Expected outcome:

- A simple resume detects or asks for role once, applies migration and identity
  gates, then acts or waits without another confirmation.
- Reviewers answer one request or wait for any future request; requestors never
  consume arbitrary requests.

Step framing:

- Design link: Resume skill orchestration through requestor continuation, Q06
  and Q07.
- Execution checklist reference: Shared execution command checklist for all
  v0.11.0 review-resume steps.

#### Step 5 implementation for resume workflows

**Files involved**:

- `tools/review_resume.py` (new, to be created).
- `tools/review_resume_wait.py` (new, to be created).
- `tools/review_exchange_cli_resume.py` (new, to be created).
- `tools/review_exchange_cli_parser.py` (existing, to be updated).
- `tools/review_exchange_cli.py` (existing, to be reduced to delegation).
- `tools/review_exchange_wait.py` (existing, to be updated).
- `tools/prompt_workflow_skill_review.py` (existing, to be updated).
- `instructions/review-resume.md` (new, to be created).
- `.agent/workflows/review-resume.md` (new, to be created).
- `.agents/llm-shared/skills/review-resume/SKILL.md` (new, to be created).
- `.claude/skills/review-resume/SKILL.md` (new, to be created).
- `.github/skills/review-resume/SKILL.md` (new, to be created).
- `instructions/review-requestor.md` (existing, to be updated).
- `instructions/spec-review-requestor.md` (existing, to be updated).
- `instructions/code-review-requestor.md` (existing, to be updated).
- `instructions/spec-reviewer.md` (existing, to be updated).
- `instructions/code-reviewer.md` (existing, to be updated).
- `tests/unit/tools/test_review_resume/__init__.py` (new, to be created).
- `tests/unit/tools/test_review_resume/test_review_resume_tdd.py` (new, to be
  created).
- `tests/unit/tools/test_review_resume/test_review_resume_wait_tdd.py` (new, to
  be created).
- `tests/unit/tools/test_review_resume/test_review_resume_role_tdd.py` (new, to
  be created).
- `tests/unit/tools/test_review_resume_instruction/__init__.py` (new, to be
  created).
- `tests/unit/tools/test_review_resume_instruction/test_review_resume_instruction_tdd.py`
  (new, to be created).
- `tests/unit/tools/test_instruction_structure/test_spec_reviewer_adapters_tdd.py`
  (existing, to be updated).
- `tests/unit/tools/test_instruction_structure/test_code_reviewer_adapters_tdd.py`
  (existing, to be updated).
- `tests/unit/tools/test_review_requestor_instruction/test_review_requestor_instruction_tdd.py`
  (existing, to be updated).

**Tests first**:

- Cover inferred requestor, inferred reviewer, legacy no-nature prompt, explicit
  role, forced mismatch confirmation, two matching roles, unknown host, selected
  role conflict, counterpart omission, migration-first ordering, and no second
  confirmation.
- Cover reviewer wait before any exchange, after conclusion, after intermediate
  answer, at convergence, and during requestor ownership; same and new exchange
  wakes; unrelated artifact ignore; human cancellation.
- Cover several requests for one reviewer and one request for several reviewers,
  including first claim, typed loser, and return to wait.
- Cover requestor exact-answer wait, owned action, convergence pickup, lost
  secret pickup, exchange release, and immediate `pw skill` continuation.
- Assert there is no `rvw_resume.bat` and every provider adapter remains a thin
  direct pointer.
- Remove Step 0 wait xfails without changing timeout bounds.

**Classes and behavior**:

- `ResumeContext`, `ResumeRoleResolution`, and `ReviewResumeService` implement
  preflight, role selection, evidence gate, ownership claim, and typed next
  action.
- `GlobalReviewerWait` uses notification hints, bounded polling, authoritative
  rescans, candidate selection, and first-claim-wins.
- Resume support operations are exposed through `review_exchange.bat`; the LLM
  instruction remains the only public resume entry point.

**Completion criteria**:

- `ghog single tests/unit/tools/test_review_resume_perf/test_review_resume_perf_tdd.py tests/unit/tools/test_review_resume tests/unit/tools/test_review_resume_instruction tests/unit/tools/test_instruction_structure/test_spec_reviewer_adapters_tdd.py tests/unit/tools/test_instruction_structure/test_code_reviewer_adapters_tdd.py tests/unit/tools/test_review_requestor_instruction`
  passes.
- `rg -n "rvw_resume|wait-request|wait globally|pw skill|already-claimed|review-resume" bin tools instructions .agent .agents .claude .github`
  shows no public resume launcher and the settled role split.
- `ghog day` reports `exit=0`.

#### Step 5 addendums for resume workflows

Line-budget checkpoint:

- New resume modules: before 0; below-550 safe; ceiling 650; service target 430,
  wait target 360, CLI support target 220 lines (advisory).
- CLI parser: before the recorded Step 3 final count; use Step 3's recorded
  policy band; ceiling 650; expected at or below 230 lines after Step 5
  (advisory).
- CLI: before the recorded Step 3 final count; use Step 3's recorded policy
  band; mandatory target at or below 520 because resume dispatch joins the Step
  3 extraction.
- Wait module: before the recorded Step 3 final count; use Step 3's recorded
  policy band; ceiling 650; expected at or below 360 lines (advisory).
- Prompt review routing: before 208; below-550 safe; ceiling 650; expected at or
  below 250 lines (advisory).
- Canonical instructions: before 235, 166, 183, 233, and 238 lines; non-Python;
  keep role rules centralized and adapters at 10 lines or fewer (advisory).
- New resume tests: before 0; each below-550 safe; ceiling 650; expected at or
  below 500 lines (advisory).
- Existing instruction tests: before 66-143 lines; below-550 safe; ceiling 650;
  expected below 220 lines each (advisory).

Split guidance:

- Keep observation mechanics separate from role and workflow decisions.
- Do not copy continuation rules into adapters or `prompt_workflow_skill_review.py`.
- Complete the CLI extraction if the main CLI remains above 550 after Step 3.

Full workflow timing run readiness:

- Step 5 focused tests listed above; `ghog day`.

Time-gated status for Step 5:

- Notification and polling gates are active and no longer xfailed; concurrency
  tests use bounded synthetic waits.

---

### Step 6. Prove cross-workflow acceptance and documentation rollout

#### Step 6 analysis and intent for complete feature acceptance

Issues to address:

- Unit seams cannot prove migration, strict schemas, ownership, status,
  adapters, separate LLM sessions, and workflow continuation together.
- Completed review-mode topics have broad tests that still encode root paths,
  no nature, old status schema, exact-only waits, and convergence stops.
- Public documentation must describe the artifact home and role-specific resume
  behavior without reopening completed topic documents.

Fix intent:

- Add real temporary-repository acceptance coverage and update affected shipped
  suites together.
- Exercise launchers and canonical instructions across specification and code
  exchanges, legacy and new evidence, three LLM natures, status migration,
  displacement, reviewer races, and requestor `pw skill` release.
- Update current public documentation and keep earlier completed effort records
  unchanged.

Expected outcome:

- Every feature-request acceptance criterion has a named executable scenario.
- All earlier review workflows pass with configured-home, nature, and ownership
  behavior.

Step framing:

- Design link: Acceptance cases for v0.11.0 review resumption.
- Execution checklist reference: Shared execution command checklist for all
  v0.11.0 review-resume steps.

#### Step 6 implementation for acceptance and rollout

**Files involved**:

- `tests/acceptance/review_resume/__init__.py` (new, to be created).
- `tests/acceptance/review_resume/conftest.py` (new, to be created).
- `tests/acceptance/review_resume/test_review_resume_acceptance/__init__.py`
  (new, to be created).
- `tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_acceptance_tdd.py`
  (new, to be created).
- `tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_concurrency_tdd.py`
  (new, to be created).
- `tests/unit/tools/test_review_exchange_acceptance/test_review_exchange_acceptance_tdd.py`
  (existing, to be updated only for shared fixtures and schema expectations).
- `tests/unit/tools/test_spec_review_requestor_acceptance/test_spec_review_requestor_acceptance_tdd.py`
  (existing, to be updated).
- `tests/unit/tools/test_spec_reviewer_acceptance/test_spec_reviewer_acceptance_tdd.py`
  (existing, to be updated).
- `tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_acceptance_tdd.py`
  (existing, to be updated).
- `tests/unit/tools/test_code_reviewer_acceptance/test_code_reviewer_acceptance_tdd.py`
  (existing, to be updated).
- `tests/unit/tools/test_prompt_workflow_skill/test_prompt_workflow_skill_spec_reviewer_tdd.py`
  (existing, to be updated).
- `tests/unit/tools/test_prompt_workflow_skill/test_prompt_workflow_skill_code_reviewer_tdd.py`
  (existing, to be updated).
- `tests/unit/tools/test_review_mode_docs_acceptance/test_review_mode_docs_final_acceptance_tdd.py`
  (existing, to be updated).
- `README.md` (existing, to be updated).

**Tests first**:

- Build real Git repositories for default, configured, legacy root, former
  default, collision, damaged journal, uncovered home, and repeated migration.
- Run status, specification requestor/reviewer, code requestor/reviewer, and
  resume flows through public launchers and separate simulated LLM sessions.
- Cover Claude, Codex, Gemini, unknown, legacy completion, conflict Override and
  Stop, counterpart omission, fresh-lease displacement, lost capability,
  convergence pickup, same/new exchange reviewer wake, simultaneous requests,
  competing reviewers, and requestor workflow release.
- Compare artifact bytes, transcript headings, Git ignore evidence, ownership
  generations, secret absence, schema-2 JSON, human reports, process statuses,
  and clean Git state.
- Map each feature acceptance criterion to at least one test name.

**Classes and behavior**:

- Acceptance fixtures create configured repositories, session host evidence,
  protocol artifacts, concurrent waiters, and deterministic notifications.
- README documents `.review-artifacts.ini`, migration-aware `rvw_status`, the
  resume skill, role detection, reviewer waiting, and requestor continuation.

**Completion criteria**:

- `ghog single tests/acceptance/review_resume tests/acceptance/review_status tests/unit/tools/test_spec_review_requestor_acceptance tests/unit/tools/test_spec_reviewer_acceptance tests/unit/tools/test_code_review_requestor_acceptance tests/unit/tools/test_code_reviewer_acceptance tests/unit/tools/test_prompt_workflow_skill tests/unit/tools/test_review_mode_docs_acceptance`
  passes.
- `rg -n "\.reviews|\.review-artifacts\.ini|review-resume|requestor_llm_nature|reviewer_llm_nature|already-claimed" README.md instructions tools tests`
  shows public documentation and acceptance evidence.
- `rg --files | rg "rvw_resume\.bat$"` returns no path.
- `ghog day` reports `exit=0`.

#### Step 6 addendums for acceptance and rollout

Line-budget checkpoint:

- New acceptance package and init files: before 0; below-550 safe; ceiling 650;
  each init target 5 lines, conftest target 420 lines, scenario files target 500
  lines each (advisory).
- Existing review-exchange acceptance test: before 604; risk band; ceiling 650;
  no growth beyond fixture/schema edits; put every new scenario in the new
  acceptance package.
- Existing status acceptance test: before the recorded Step 4 final count; use
  Step 4's recorded policy band; ceiling 650; expected at or below 380 lines
  after Step 6 (advisory).
- Existing role acceptance and prompt tests: count before edits; below-550 files
  may grow to the 650 ceiling, while any risk-band file receives only fixture or
  expectation replacements and no new scenario block.
- README: before 1068; non-Python; no Python ceiling; keep additions focused and
  link canonical instructions rather than copying them.

Split guidance:

- Keep repository/session builders in `conftest.py`, sequential scenarios in the
  main acceptance file, and race/timing scenarios in the concurrency file.
- Split any existing test already in the risk band before adding a new behavior
  section to it.

Full workflow timing run readiness:

- Step 6 focused acceptance and regression suites listed above; `ghog day`.

Time-gated status for Step 6:

- Run notification, polling, migration, and competing-reviewer gates under the
  final public launcher fixtures with their Step 0 bounds unchanged.

## Open questions for the v0.11.0 review-resume-command implementation plan

### Q01: How should a session pass its ownership secret to later commands?

Question description: The claiming command returns a secret to the LLM session,
and every later mutation must present it without writing it to coordination or
another durable artifact. The plan must name a transport that works across
separate `review_exchange.bat` process invocations without exposing the secret
unnecessarily. The fence protects against a displaced LLM session with
repository access, which is the adversary the design's ownership generation
exists to reject. That session reads any repository file but not another
session's process arguments or context. Transport must therefore avoid a durable
copy; it need not defend against a local user inspecting live process arguments.

#### BBQ for Q01

Think of a worker who receives a one-use door code and must present it at the
next guarded door. They can hand it to the guard on a slip, leave it in an
office-wide memo slot, or say it at the door where only whoever is present hears
it. In this picture: the worker is the LLM session, the door code is the
ownership token, the slip is standard input, the memo slot is an environment
variable, and speaking at the door is a command-line argument.

#### Options for Q01

- Option A: Pass the generation as an ordinary flag and send the secret through
  a dedicated standard-input field read once by the mutating command.
  - pro: The token stays out of process arguments, environment snapshots,
    coordination, and files.
  - con: The LLM caller can feed standard input only by embedding the secret in
    a shell command or redirecting a file, which reintroduces argument exposure
    or a durable copy.
- Option B: Pass the token through one dedicated process environment variable.
  - pro: Existing non-interactive commands remain single calls and Python can
    remove the variable after reading it.
  - con: Process environments can be inspected by same-user processes and are
    easy to inherit accidentally into child commands.
- Option C: Pass both generation and token as command-line flags.
  - pro: It is the simplest parser and produces self-contained replayable test
    calls.
  - con: A hostile local user inspecting live process arguments could see the
    secret, which is outside the stated displaced-session threat model.

#### Recommended option for Q01 (with arguments for this choice)

Option C: Use generation and token flags. The actual LLM caller can issue them
in one non-interactive call, and the stated adversary cannot recover another
session's process arguments after the command exits. A repository file or
environment copy would remain readable or inheritable for longer.

#### Answer to Q01: option C (with reason why it must be accepted as the answer)

Option C: Accept generation and token flags. Under the stated threat model a
displaced session cannot recover a secret from another session's process
arguments, while any file or environment copy is reachable. Flags keep mutating
commands single-call, replayable in tests, and free of a second durable copy.

### Q02: Which implementation should provide directory notifications?

Question description: The design requires native directory notification when
available plus bounded polling fallback. Python has no portable standard-library
watcher, while `watchdog` already appears transitively in the lock file but is
not a declared runtime dependency.

#### BBQ for Q02

Imagine fitting doorbells in buildings on Windows, Linux, and macOS. The team
can buy one supported doorbell kit for all buildings, wire each building's
electrical system by hand, or skip bells and have someone check every door on a
schedule. In this picture: the kit is `watchdog`, custom wiring is an OS-native
adapter, scheduled checks are polling, and the buildings are supported hosts.

#### Options for Q02

- Option A: Declare `watchdog` as a direct runtime dependency behind a small
  observer adapter and retain bounded polling fallback.
  - pro: One maintained cross-platform API supplies native events, and the
    dependency is already represented in the repository lock.
  - con: The runtime dependency set grows and tests need a fake adapter rather
    than depending on real OS event timing.
- Option B: Implement separate standard-library or `ctypes` native adapters per
  supported operating system plus polling fallback.
  - pro: It adds no third-party runtime dependency and permits exact platform
    control.
  - con: It creates substantial platform-specific code and testing for behavior
    already maintained by a specialist library.
- Option C: Implement bounded polling only.
  - pro: It is the smallest and most predictable implementation.
  - con: It does not implement the settled notification-plus-polling design and
    pays repeated idle scan cost indefinitely.

#### Recommended option for Q02 (with arguments for this choice)

Option A: Declare and wrap `watchdog`. A narrow adapter keeps tests deterministic
and supplies the designed native hint on supported hosts while polling remains
the correctness fallback.

#### Answer to Q02: option A (with reason why it must be accepted as the answer)

Option A: Accept a direct `watchdog` dependency because it implements the
settled cross-platform notification path with far less platform code, and the
authoritative rescan means library events remain hints rather than protocol
evidence.

### Q03: How should thin provider adapters supply the trusted LLM hint?

Question description: Claude and Codex have known environment evidence, but the
design also requires a trusted provider-entry hint and specifically relies on it
for Gemini when no stable environment signal exists. Provider Markdown bodies
must remain direct pointers to canonical instructions, although discovery
metadata is allowed.

#### BBQ for Q03

Picture identical forwarding envelopes sent from three branch offices. Each
envelope may carry a small branch stamp, the mailroom may guess the branch from
the shelf where it found the envelope, or the recipient may inspect the weather
outside and infer the city. In this picture: the branch stamp is adapter front
matter, the shelf is the provider-specific path, weather is environment
evidence, and the envelope body is the mandatory canonical pointer.

#### Options for Q03

- Option A: Add a validated `llm_nature` metadata field to each thin adapter and
  have the adapter invocation pass that non-secret hint to the canonical resume
  support operation.
  - pro: The identity is explicit, works for Gemini, and leaves adapter bodies as
    direct pointers.
  - con: Adapter-structure tests and each provider format need to recognize the
    metadata field.
- Option B: Infer the nature from the provider-specific adapter path that
  initiated the skill.
  - pro: It adds no metadata and the directory already names the integration.
  - con: Canonical execution may not retain the adapter path, and path inference
    couples runtime identity to installation layout.
- Option C: Use environment signals only and return `unknown` for Gemini when no
  signal exists.
  - pro: It requires no adapter protocol change.
  - con: It fails to use the trusted provider entry point and makes Gemini
    identity unavailable in the normal adapter path.

#### Recommended option for Q03 (with arguments for this choice)

Option A: Use declarative adapter metadata. The adapter rule expressly permits
discovery metadata, and one validated enum supplies the host hint without
copying any canonical workflow content.

#### Answer to Q03: option A (with reason why it must be accepted as the answer)

Option A: Accept provider metadata because it gives all three supported hosts a
portable trusted hint while preserving the thin-pointer body and keeping the
hint non-secret and schema-validated.

### Q04: What concrete format should the migration recovery journal use?

Question description: The design settles a versioned journal, per-move recording,
rollback, and committed cleanup but leaves the physical update format to the
plan. Recovery must distinguish an incomplete write from a valid phase and must
not require scanning unrelated home files.

#### BBQ for Q04

Think of movers recording a job as it proceeds. They can replace one complete
clipboard sheet after each box, append one new line to a running notebook, or
leave a separate marker card beside every moved box. In this picture: the sheet
is an atomically replaced JSON snapshot, the notebook is JSON Lines, marker
cards are per-artifact files, and the movers are the migration transaction.

#### Options for Q04

- Option A: Store one strict versioned JSON journal and atomically replace the
  complete snapshot after each recorded move and phase transition.
  - pro: Recovery reads one bounded file and either sees a complete validated
    state or the previous complete state.
  - con: Each move rewrites a small journal containing the complete source map.
- Option B: Append checksummed JSON Lines records for prepare, each move, commit,
  rollback, and cleanup.
  - pro: Each successful move adds one short write and retains transition
    history.
  - con: Recovery must detect and ignore torn final records and replay a log to
    derive current state.
- Option C: Create one phase marker and one marker file per moved artifact.
  - pro: Individual marker creation can use atomic filesystem operations.
  - con: Recovery needs another directory enumeration and must reconcile many
    marker files with the source map.

#### Recommended option for Q04 (with arguments for this choice)

Option A: Use one atomically replaced strict JSON snapshot. The artifact count
is bounded and the simplest recovery contract is to validate one complete
versioned state rather than replay or reconcile fragmented evidence.

#### Answer to Q04: option A (with reason why it must be accepted as the answer)

Option A: Accept the atomic JSON snapshot because it gives recovery one strict
source of truth, rejects malformed or unsupported phases directly, and keeps
journal discovery to one known path.

### Q05: Which shared operations should the resume skill call?

Question description: Resume must remain an LLM skill rather than a public
command, but its canonical instruction needs typed support for migration, role
inspection, ownership claim, and identity-free waiting. The plan currently says
to add support operations without naming the command surface.

#### BBQ for Q05

Imagine a dispatcher coordinating a recovery crew. The dispatcher can call
separate clearly labeled service numbers, call one switchboard and state an
action code, or call a second private company that duplicates the main service
desk. In this picture: the dispatcher is the resume skill, labeled numbers are
explicit `review_exchange` operations, the switchboard is a generic action
operation, and the second company is a separate support launcher.

#### Options for Q05

- Option A: Add explicit typed operations to `review_exchange.bat` for
  `migration-check`, `migrate-artifacts`, `resume-inspect`, `claim`, and
  `wait-any-request`, while keeping role orchestration in the skill.
  - pro: Existing JSON, exit, root, locking, and test conventions apply to each
    support action without creating a public resume command.
  - con: The parser and operation registry gain several names and need focused
    CLI delegation.
- Option B: Add one generic `resume-support --action <name>` operation to the
  shared launcher.
  - pro: The top-level command registry gains one operation.
  - con: Action-specific inputs and outputs become a second dispatch layer and
    are harder to discover and validate independently.
- Option C: Add a separate `review_resume_support.bat` launcher containing all
  support actions.
  - pro: Resume-related parser code stays outside the exchange launcher.
  - con: It creates a second protocol command surface close to the forbidden
    resume command and duplicates caller-root and result handling.

#### Recommended option for Q05 (with arguments for this choice)

Option A: Add explicit operations to the existing shared launcher and keep the
skill as the only resume entry point. Focused CLI modules prevent growth in the
risk-band main parser and dispatcher.

#### Answer to Q05: option A (with reason why it must be accepted as the answer)

Option A: Accept explicit shared operations because each gains a strict typed
contract and existing protocol safety while the LLM skill, not a new batch
launcher, remains responsible for choosing and sequencing them.

### Q06: How should existing review tests adopt the new common context?

Question description: Many specification, code-review, status, lifecycle, and
prompt tests independently construct project-root artifacts and legacy schemas.
The final step must update all affected suites without duplicating configured
home, LLM nature, and ownership capability setup in every package.

#### BBQ for Q06

Picture several workshops that all need the same new safety jig. The team can
build one shared jig and let each workshop add its own attachment, build a copy
inside every workshop, or leave old benches in place and patch each test by hand.
In this picture: the jig is a shared test-support builder, attachments are local
fixtures, workshops are existing test packages, and benches are the duplicated
legacy setup functions.

#### Options for Q06

- Option A: Add `tests/unit/tools/review_exchange_test_support.py` with shared
  repository, artifact-home, nature, and capability builders; keep scenario
  assertions and specialized wrappers in local fixtures.
  - pro: One helper owns schema-2 defaults and migration layout construction,
    while each suite retains its domain-specific assertions.
  - con: Many packages depend on one test-support module and changes to its
    defaults can affect a broad test set.
- Option B: Extend each package's `conftest.py` or `fixtures.py` independently.
  - pro: Fixture behavior remains local and failures are isolated to one suite.
  - con: Home, nature, capability, and legacy setup logic is repeated and can
    drift across specification, code, and status tests.
- Option C: Update existing inline constructors in place without a new helper.
  - pro: It adds no shared test module or import changes.
  - con: It maximizes repetitive edits and grows several files already near the
    repository line ceiling.

#### Recommended option for Q06 (with arguments for this choice)

Option A: Add one shared builder module with narrow explicit inputs, and keep
scenario policy local. This reduces repeated setup and avoids growing risk-band
acceptance and CLI files while retaining readable tests.

#### Answer to Q06: option A (with reason why it must be accepted as the answer)

Option A: Accept the shared builder because the cross-cutting schema and path
defaults need one maintained source in tests, while local fixtures can still
express each workflow's distinct behavior and expected result.
