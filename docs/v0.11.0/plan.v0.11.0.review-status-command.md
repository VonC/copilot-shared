# v0.11.0 review-status-command implementation plan -- durable state diagnosis

Implement one read-only status pipeline over the existing review-exchange
protocol, with a typed result shared by human and JSON output.

- **Typed status records**: represent healthy exchanges and damaged candidates
  without guessing missing identity.
- **Bounded discovery**: scan the reserved coordination prefix once and reuse
  the existing observer and canonical path derivation.
- **One command surface**: expose the same result through the root launcher,
  direct Python entry point, and final acceptance suite.

> Markdown lint note: never leave a space immediately inside an inline code span
> (MD038); when a snippet starts or ends with a space, write that space as the
> literal token `[space]`, as in `` `[space]${x}` ``. End any line that would be
> only italic text with a period after the closing underscore (MD036).

## Plan goal for v0.11.0 review status

Implement the full v0.11.0 review-status command described by
`docs/v0.11.0/feature-request.v0.11.0.review-status-command.md` and
`docs/v0.11.0/design.v0.11.0.review-status-command.md` in four ordered slices.

- **Step 1 goal**: define the strict machine result and its closed vocabularies.
- **Step 2 goal**: discover, validate, observe, normalize, and order every active
  coordination candidate without mutation.
- **Step 3 goal**: render one result for humans and machines and expose both
  forms through `rvw_status`.
- **Step 4 goal**: prove launcher parity, full-state reporting, damaged-entry
  isolation, and the read-only contract with acceptance tests.

---

## Scope anchors for the v0.11.0 review-status plan

This plan implements these settled outcomes:

1. Discover all nonterminal specification and code-review exchanges from
   protocol-owned coordination candidates.
2. Report identity, role, umbrella, lease, artifacts, state, and next action in
   one normalized result.
3. Preserve independent healthy and damaged evidence while leaving protocol and
   Git state untouched.

The following are in scope:

- caller-root resolution with an explicit test override;
- tagged healthy and damaged result records;
- state-aware continuing-role, lease, artifact, and next-action projection;
- deterministic human and versioned JSON rendering; and
- root-launcher, direct-entry, and read-only acceptance coverage.

The following remain deferred to `review-resume-command`:

- choosing one exchange when several are active;
- renewing, reclaiming, repairing, cancelling, or completing an exchange;
- executing the reported next action; and
- emitting or installing continuation instructions.

---

## Complexity bound clarification for v0.11.0 review status

Let `r` be the number of entries at the repository root and `n` the number of
reserved active-coordination candidates.

- **O(r) root discovery**: enumerate the reserved prefix once without scanning
  the documentation tree.
- **O(1) work per candidate artifact kind**: the protocol has exactly six fixed
  artifact paths, so presence and applicability projection remains constant per
  exchange.
- **O(n) observation and normalization**: each candidate receives bounded
  parsing, fingerprint, observer, lease, role, action, and artifact work.
- **O(n log n) final ordering**: the design requires deterministic identity and
  damaged-candidate ordering; this is the single intentional sorting cost.

No status path may add nested candidate scans, per-artifact directory scans, or
an `O(n^2)` comparison. Rendering walks the already ordered in-memory result
once.

---

## File-based IO cost clarification for v0.11.0 review status

- Resolve the caller root once and load `ReviewConfiguration` once.
- Enumerate only the root `a.review-active.*` prefix; do not load documentation
  metadata or walk the repository.
- Read each coordination candidate before observation and once afterward for
  the changed-during-read fingerprint; the existing observer inspects only the
  six derived canonical paths.
- Reuse one normalized result for human output, JSON output, status mapping, and
  later `rvw_resume` consumption.
- Do not enter `transition_lock` or call any store publication, lease, recovery,
  confirmation, completion, marker, index, ref, or working-tree mutation API.

The loading phase is a bounded protocol-index read proportional to active
coordination candidates rather than a broad repository metadata pass.

---

## Confirmed technical facts for v0.11.0 plan viability

Physical line counts include blank lines and use the same per-line iteration
metric as the repository big-file scan.

**Files over the 650-line repository limit**:

- None of the Python files planned for creation or modification is currently
  over the limit.

**Files in the 550-through-650 risk band**:

- `tools/review_exchange_models.py`: **555 lines**. The status implementation
  imports its public identity, configuration, state, context, and path types but
  does not add code to this file.
- `tools/review_exchange_store.py`: **633 lines**. Discovery constructs the
  existing store and observer but does not grow the persistence class.

**Files below 550 and safe to extend**:

- No existing Python file needs modification. All production and focused test
  files are new and begin at zero lines.

**What does not exist yet**:

- `tools/review_status_models.py`.
- `tools/review_status.py`.
- `tools/review_status_render.py`.
- `tools/review_status_cli.py`.
- `rvw_status.bat`.
- Focused unit leaves for status models, discovery, rendering, and CLI behavior.
- The review-status acceptance package and test leaf.

**Other confirmed facts affecting implementation**:

- `tools/review_exchange_observer.py` is 139 lines and already provides the
  read-only `ReviewExchangeObserver.classify()` boundary.
- `tools/review_exchange_paths.py` is 231 lines and already derives all six
  canonical paths and parses transient identities.
- `tools/review_exchange_models_coordination.py` is 238 lines and strictly
  parses `CoordinationRecord`, including owner, next actor, round, lease,
  confirmation, and transition evidence.
- `tools/review_exchange_models_envelope.py` is 220 lines and exposes
  `parse_json_markdown` for reading coordination content without using a private
  store method.
- `tools/review_exchange_state.py` is 277 lines and owns the complete
  `ArtifactState` classifier, including idle, abandoned, interrupted,
  convergence, authorization, escalation, repair, and inconsistency outcomes.
- `tools/review_exchange_transcript_identity.py` is 46 lines and exposes
  `current_request_occurrence` for restarted exchanges.
- `tools._models.find_project_root` already resolves `PRJ_DIR` or walks upward
  from the caller, and `commit-plan-check.bat` demonstrates a root launcher
  that preserves the caller's current directory.

---

## Current test-tree validation snapshot for v0.11.0 review status

Existing test areas that must remain green:

- `tests/unit/tools/test_review_exchange_models/` covers strict exchange,
  context, configuration, artifact-path, and coordination model validation.
- `tests/unit/tools/test_review_exchange_state/` covers every observable state
  and property-based classifier invariants.
- `tests/unit/tools/test_review_exchange_paths/` covers filename identity,
  canonical derivation, Git-root validation, and ignore behavior.
- `tests/unit/tools/test_review_exchange_lifecycle/` covers observer-driven
  transitions and restarted transcript occurrence.
- `tests/unit/tools/test_review_exchange_store/` covers strict coordination and
  artifact reads; its 528-line validation test is not modified.

New unit test leaf directories:

- `tests/unit/tools/test_review_status_models/`.
- `tests/unit/tools/test_review_status/`.
- `tests/unit/tools/test_review_status_render/`.
- `tests/unit/tools/test_review_status_cli/`.

New acceptance test leaf:

- `tests/acceptance/review_status/test_review_status_acceptance/`.

Property-based coverage is required for candidate enumeration order and result
ordering. Arbitrary valid identities and malformed reserved-prefix names must
produce the same ordered result regardless of source enumeration order;
parameterized examples remain the clearer coverage for the finite state, role,
lease, artifact, action, renderer, and process-status tables.

---

## Step 0 perf-gate assessment for v0.11.0 review status

No Step 0 wall-clock gate is added. The settled design defines bounded reads and
complexity but no duration threshold, and a filesystem timing assertion would
measure host load rather than the contract. Step 2 instead adds deterministic
read-count, fixed-artifact, configuration-load, changed-during-read, and
no-write tests. Step 4 repeats the no-mutation proof through the real launcher.

---

## Implementation constraints carried from the settled design

- Healthy and damaged entries share one ordered tagged-union collection.
- The absolute repository root appears once; all subordinate paths are
  repository-relative.
- `expected_next_actor` controls ordinary continuation, while convergence and
  escalation use the two confirmed state-aware mappings and owner stays
  separate.
- Lease evidence uses fixed timestamps and the four `current`, `expired`,
  `not-held`, and `missing` categories; no changing elapsed counter is stored.
- Artifact kind is a six-key object whose applicability and presence remain
  separate.
- Exit status is `0` for trustworthy results, `3` for results containing
  untrustworthy exchange evidence, and `2` for invocation or operational
  failure.
- Coordination changes during observation become an explicit diagnostic; the
  status path never acquires the transition lock.

---

## Shared execution command checklist for all v0.11.0 review-status steps

Apply this checklist to every numbered step with its step-specific paths.

1. Count physical lines before edits for every Python file in the step.
2. Add the step tests before production behavior.
3. Run `ghog single` with the step's focused test files.
4. Run the step-specific `rg` checks for types, observer reuse, fields,
   renderers, arguments, statuses, or launcher wiring.
5. Run `ghog day` repeatedly until it reports the objective with `exit=0`.
6. Count physical lines after edits and compare every Python file with its
   baseline, policy band, advisory estimate, and 650-line ceiling.
7. If a Python file exceeds 650 lines, stop and apply the responsibility split
   stated in the step before committing.
8. If a file exceeds only an advisory estimate while remaining at or below 650,
   record the variance without failing the step or requiring a split.

## Ready-to-run commands for all v0.11.0 review-status steps

- Physical line count: `(Get-Content -LiteralPath '<path>').Count`
- Targeted tests: `ghog single <step-test-files>`
- Grep checks: `rg -n '<step-pattern>' <step-paths>`
- Shared gate loop: `ghog day`, repeated fix-and-walk until it reports the
  objective with `exit=0`
- Physical line recount: `(Get-Content -LiteralPath '<path>').Count`

---

## Numbered implementation steps for v0.11.0 review status

### Step 1. Define the versioned review-status result model

#### Step 1 analysis and intent for typed status evidence

Issues to address:

- The exchange core exposes identity and state types but has no repository-wide
  tagged result for healthy and damaged candidates.
- Role specialization, lease category, next-action identity, artifact
  applicability, overall outcome, and schema version need closed values before
  discovery or rendering can depend on them.

Fix intent:

- Add immutable JSON-compatible status records that keep trusted exchange data
  separate from partial damaged-candidate evidence.
- Make all downstream renderers and the later resume effort consume the same
  typed fields rather than interpreting prose.

Expected outcome:

- One strict result owns schema version, repository root, outcome, active count,
  error flag, and ordered entries.
- Healthy entries can represent the complete design field set, while damaged
  entries expose only safely parsed facts, candidate path, and diagnostics.

Step framing:

- Design links: Stable machine record, Continuing-agent mapping, Lease
  freshness, Artifact completeness, and Next-action identity.
- Execution checklist reference: Shared execution command checklist for all
  v0.11.0 review-status steps.

#### Step 1 implementation for typed status evidence

**Files involved**:

- `tools/review_status_models.py` (new, to be created).
- `tests/unit/tools/test_review_status_models/__init__.py` (new, to be created).
- `tests/unit/tools/test_review_status_models/test_review_status_models_tdd.py`
  (new, to be created).

**Tests first**:

- Cover strict enum values and immutable healthy, damaged, artifact, lease, and
  repository-result construction.
- Cover repository-relative path validation, six artifact keys, positive round
  and occurrence values, nullable umbrella and implementation step, error-flag
  consistency, and stable `to_dict()` output.
- Reject guessed identity on damaged candidates and inconsistent active counts
  or trustworthy outcomes.

**Classes and behavior**:

- `ReviewStatusOutcome`, `LeaseFreshness`, `ArtifactApplicability`, and
  `NextAction`: closed machine vocabularies from the settled design.
- `ArtifactStatus` and `LeaseStatus`: keep raw evidence, derived state, and
  fixed timestamps together.
- `ExchangeStatus` and `DamagedCandidateStatus`: form the tagged entry union.
- `ReviewStatusResult`: owns schema version, absolute root, ordered entries,
  active count, error flag, JSON projection, and process-status mapping.

**Completion criteria**:

- `ghog single tests/unit/tools/test_review_status_models/test_review_status_models_tdd.py`
  passes.
- `rg -n "ReviewStatusResult|ExchangeStatus|DamagedCandidateStatus|NextAction|LeaseFreshness" tools/review_status_models.py tests/unit/tools/test_review_status_models`
  shows every public result component and its tests.
- `ghog day` reports the objective with `exit=0`.

#### Step 1 addendums for typed status evidence

Line-budget checkpoint:

- `tools/review_status_models.py`: before 0; below-550 safe; repository ceiling
  650; expected at or below 280 lines (advisory).
- `tests/unit/tools/test_review_status_models/__init__.py`: before 0; below-550
  safe; repository ceiling 650; expected at or below 5 lines (advisory).
- `tests/unit/tools/test_review_status_models/test_review_status_models_tdd.py`:
  before 0; below-550 safe; repository ceiling 650; expected at or below 360
  lines (advisory).

Split guidance:

- If the model module would exceed 650, extract only JSON projection helpers to
  `tools/review_status_serialization.py`; keep the closed enums and immutable
  records together.
- If the unit file approaches 550, split serialization cases into a sibling
  conventional test leaf before adding more model cases.

Full workflow timing run readiness:

- `tests/unit/tools/test_review_status_models/test_review_status_models_tdd.py`;
  `ghog day`.

Time-gated status for Step 1:

- No wall-clock perf gate is affected; this step is pure in-memory validation
  and projection.

---

### Step 2. Discover and normalize every active coordination candidate

#### Step 2 analysis and intent for bounded repository discovery

Issues to address:

- No service enumerates the reserved active-coordination prefix or converts each
  candidate into independent healthy or damaged status evidence.
- The observer classifies one known context, while status must first validate
  filename identity and coordination content and must detect a concurrent
  coordination change without locking.

Fix intent:

- Build one read-only collection service that parses each candidate, verifies
  filename, record, context, and canonical-path agreement, then delegates valid
  exchanges to `ReviewExchangeObserver`.
- Normalize role, specialization, umbrella, occurrence, lease, artifacts, next
  action, and diagnostics with one evaluation timestamp and configuration load.

Expected outcome:

- Every non-idle valid exchange and every malformed reserved-prefix candidate
  appears independently in deterministic order.
- One damaged candidate cannot hide healthy exchanges, and a changed
  coordination fingerprint cannot produce a falsely trustworthy snapshot.

Step framing:

- Design links: Repository and discovery boundary, Normalized exchange result,
  Read-only trust boundary, and Design decisions Q01 through Q10.
- Execution checklist reference: Shared execution command checklist for all
  v0.11.0 review-status steps.

#### Step 2 implementation for bounded repository discovery

**Files involved**:

- `tools/review_status.py` (new, to be created).
- `tests/unit/tools/test_review_status/__init__.py` (new, to be created).
- `tests/unit/tools/test_review_status/test_review_status_tdd.py` (new, to be
  created).
- `tests/unit/tools/test_review_status/test_review_status_pbt.py` (new, to be
  created).

**Tests first**:

- Cover empty, single, multiple, malformed-name, malformed-content,
  filename-record mismatch, missing umbrella field, canonical-path mismatch,
  idle exclusion, mixed healthy/damaged, and changed-during-read cases.
- Cover configuration loading with the review-mode marker present, where the
  result reports its configured timeout.
- Cover configuration loading with the review-mode marker absent, where loading
  returns the disabled-mode fallback timeout.
- Parameterize every `ArtifactState` through continuing-role, specialization,
  owner, action, lease, artifact applicability, and overall outcome mapping.
- Spy on configuration loading, candidate enumeration, coordination reads,
  fixed artifact probes, observer construction, store mutation methods, and
  transition-lock access.
- Add Hypothesis coverage proving enumeration-order independence and stable
  identity/candidate ordering for arbitrary distinct valid and malformed names.

**Classes and behavior**:

- `collect_review_status(root, wall_clock)`: load configuration and evaluation
  time once, collect candidates, normalize entries, sort them, and return one
  `ReviewStatusResult`.
- Candidate parsing: use `parse_transient_identity`, `parse_json_markdown`, and
  `CoordinationRecord.from_dict`, then compare filename identity, record
  context, and `derive_artifact_paths` before observation.
- Valid observation: construct `ReviewExchangeStore` and
  `ReviewExchangeObserver`, reuse `classify()`, exclude only `idle`, and derive
  occurrence with `current_request_occurrence`.
- Fingerprint guard: compare exact coordination bytes before and after
  observation and convert a mismatch into changed-during-read evidence.
- Pure projection helpers: implement the settled state-aware role, lease,
  artifact, next-action, outcome, and deterministic sort tables.

**Completion criteria**:

- `ghog single tests/unit/tools/test_review_status/test_review_status_tdd.py tests/unit/tools/test_review_status/test_review_status_pbt.py`
  passes.
- `rg -n "ReviewExchangeObserver|parse_transient_identity|parse_json_markdown|current_request_occurrence|changed-during-read" tools/review_status.py tests/unit/tools/test_review_status`
  shows reuse of every required authority and the race guard.
- Read-count tests show one configuration load, one prefix enumeration, bounded
  per-candidate reads, no documentation walk, no transition lock, and no write.
- `ghog day` reports the objective with `exit=0`.

#### Step 2 addendums for bounded repository discovery

Line-budget checkpoint:

- `tools/review_status.py`: before 0; below-550 safe; repository ceiling 650;
  expected at or below 450 lines (advisory).
- `tests/unit/tools/test_review_status/__init__.py`: before 0; below-550 safe;
  repository ceiling 650; expected at or below 5 lines (advisory).
- `tests/unit/tools/test_review_status/test_review_status_tdd.py`: before 0;
  below-550 safe; repository ceiling 650; expected at or below 500 lines
  (advisory).
- `tests/unit/tools/test_review_status/test_review_status_pbt.py`: before 0;
  below-550 safe; repository ceiling 650; expected at or below 180 lines
  (advisory).

Split guidance:

- If `tools/review_status.py` would exceed 650, extract only pure state-to-role,
  lease, artifact, action, and ordering projection into
  `tools/review_status_projection.py`; keep root enumeration and observer
  orchestration in the service.
- If the example test approaches 550, move read-boundary spies into a sibling
  `test_review_status_io` leaf rather than weakening coverage.

Full workflow timing run readiness:

- `tests/unit/tools/test_review_status/test_review_status_tdd.py` and
  `tests/unit/tools/test_review_status/test_review_status_pbt.py`; `ghog day`.

Time-gated status for Step 2:

- No wall-clock timeout is added. Deterministic IO-count and complexity tests
  own the bounded-loading requirement.

---

### Step 3. Render and expose the `rvw_status` command

#### Step 3 analysis and intent for command and output parity

Issues to address:

- The normalized result needs concise human output and stable versioned JSON
  without separate data gathering or status logic.
- The repository has no caller-preserving `rvw_status` launcher or direct CLI
  with human/JSON selection and explicit root override.

Fix intent:

- Add two renderers over the same immutable result and one thin CLI that maps
  result outcome to process status.
- Follow the root-launcher precedent so installed runtime location never
  replaces the caller repository.

Expected outcome:

- Human output visibly separates Role, Specialization, Owner, and Umbrella for
  each exchange and retains candidate diagnostics when identity is damaged.
- JSON and human forms agree, direct and batch entry points select the same
  repository, and fatal invocation errors return status `2` without a partial
  trustworthy payload.

Step framing:

- Design links: Human report and command outcome, Stable machine record, and
  Caller repository resolution.
- Execution checklist reference: Shared execution command checklist for all
  v0.11.0 review-status steps.

#### Step 3 implementation for command and output parity

**Files involved**:

- `tools/review_status_render.py` (new, to be created).
- `tools/review_status_cli.py` (new, to be created).
- `rvw_status.bat` (new, to be created).
- `tests/unit/tools/test_review_status_render/__init__.py` (new, to be created).
- `tests/unit/tools/test_review_status_render/test_review_status_render_tdd.py`
  (new, to be created).
- `tests/unit/tools/test_review_status_cli/__init__.py` (new, to be created).
- `tests/unit/tools/test_review_status_cli/test_review_status_cli_tdd.py` (new,
  to be created).

**Tests first**:

- Cover zero, healthy, damaged, and mixed human reports; assert separate role,
  specialization, owner, umbrella, lease, artifact, next-action, and diagnostic
  labels.
- Cover deterministic compact JSON, Unicode/path handling, schema version,
  null standalone umbrella, tagged entries, and renderer no-IO behavior.
- Cover `--format human`, `--format json`, `--root`, upward caller discovery,
  invalid roots, operational failures, stdout/stderr separation, and statuses
  `0`, `3`, and `2`.
- Cover launcher self-location, newest llm-shared Python selection, caller
  directory preservation, `PYTHONPATH`, and exit-code forwarding.

**Classes and behavior**:

- `render_human(result)`: print repository and outcome once, then one stable
  labelled exchange or damaged-candidate block per ordered entry.
- `render_json(result)`: serialize the same typed result with no new discovery
  or path normalization.
- `review_status_cli.main(argv)`: parse arguments, resolve and validate root,
  collect once, render once, route streams, and return the typed status.
- `rvw_status.bat`: self-locate the llm-shared runtime while retaining `%CD%`
  as the default discovery origin and forwarding all arguments and exit status.

**Completion criteria**:

- `ghog single tests/unit/tools/test_review_status_render/test_review_status_render_tdd.py tests/unit/tools/test_review_status_cli/test_review_status_cli_tdd.py`
  passes.
- `rg -n "Role:|Specialization:|Owner:|Umbrella:|schema_version|--format|--root" tools/review_status_render.py tools/review_status_cli.py rvw_status.bat tests/unit/tools/test_review_status_render tests/unit/tools/test_review_status_cli`
  shows the required visible fields and command contract.
- Renderer tests prove no filesystem or subprocess access after collection.
- `ghog day` reports the objective with `exit=0`.

#### Step 3 addendums for command and output parity

Line-budget checkpoint:

- `tools/review_status_render.py`: before 0; below-550 safe; repository ceiling
  650; expected at or below 220 lines (advisory).
- `tools/review_status_cli.py`: before 0; below-550 safe; repository ceiling 650;
  expected at or below 180 lines (advisory).
- `rvw_status.bat`: before 0; non-Python launcher; Python ceiling not
  applicable; expected at or below 35 physical lines (advisory).
- `tests/unit/tools/test_review_status_render/__init__.py`: before 0; below-550
  safe; repository ceiling 650; expected at or below 5 lines (advisory).
- `tests/unit/tools/test_review_status_render/test_review_status_render_tdd.py`:
  before 0; below-550 safe; repository ceiling 650; expected at or below 330
  lines (advisory).
- `tests/unit/tools/test_review_status_cli/__init__.py`: before 0; below-550
  safe; repository ceiling 650; expected at or below 5 lines (advisory).
- `tests/unit/tools/test_review_status_cli/test_review_status_cli_tdd.py`: before
  0; below-550 safe; repository ceiling 650; expected at or below 330 lines
  (advisory).

Split guidance:

- If the renderer module would exceed 650, separate human and JSON presentation
  while keeping both dependent only on `ReviewStatusResult`.
- If CLI or launcher tests approach 550, split launcher-process cases into a
  focused sibling leaf; keep parser and status-mapping cases together.

Full workflow timing run readiness:

- `tests/unit/tools/test_review_status_render/test_review_status_render_tdd.py`
  and `tests/unit/tools/test_review_status_cli/test_review_status_cli_tdd.py`;
  `ghog day`.

Time-gated status for Step 3:

- No perf gate changes; renderers must remain in-memory and CLI work stays one
  collection plus one render.

---

### Step 4. Prove end-to-end status behavior and read-only rollout

#### Step 4 analysis and intent for acceptance and rollout

Issues to address:

- Unit tests cannot prove that the real launcher, direct module, ignored review
  files, Git state, and caller-root selection behave together.
- The final feature needs permanent coverage for every acceptance shape that
  previously required manual state reconstruction, including overnight-style
  escalation and healthy/damaged mixtures.

Fix intent:

- Exercise the public launcher and direct Python entry against temporary Git
  repositories populated through real review-exchange models and stores.
- Snapshot protocol artifacts and Git evidence before and after status calls to
  prove that repeated diagnosis is read-only.

Expected outcome:

- No, one, multiple, convergence, authorization, escalation, standalone,
  umbrella, malformed, inconsistent, missing-artifact, and changed-state cases
  produce the designed output and process status.
- The root launcher and direct entry report identical structured results from a
  nested caller directory, and repeated calls leave every observed byte and Git
  fact unchanged.

Step framing:

- Design link: Acceptance cases for v0.11.0 review status.
- Execution checklist reference: Shared execution command checklist for all
  v0.11.0 review-status steps.

#### Step 4 implementation for acceptance and rollout

**Files involved**:

- `tests/acceptance/review_status/__init__.py` (new, to be created).
- `tests/acceptance/review_status/conftest.py` (new, to be created).
- `tests/acceptance/review_status/test_review_status_acceptance/__init__.py`
  (new, to be created).
- `tests/acceptance/review_status/test_review_status_acceptance/test_review_status_acceptance_tdd.py`
  (new, to be created).

**Tests first**:

- Build real temporary repositories with zero, one, and multiple specification
  and code exchanges, umbrella and standalone contexts, fixed timestamps, and
  every designed nonterminal category.
- Assert broad role and specialization, separate owner, exact umbrella, step,
  round, occurrence, lease, six artifacts, next action, diagnostics, ordering,
  active count, error flag, and statuses `0`, `3`, and `2`.
- Mix healthy and malformed candidates and prove healthy records remain in both
  outputs while the repository outcome becomes untrustworthy.
- Compare recursive protocol-file hashes, `git status --porcelain`, index tree,
  current ref, review marker, and coordination bytes before and after repeated
  launcher and direct-entry calls.

**Classes and behavior**:

- Acceptance fixtures in `tests/acceptance/review_status/conftest.py` use
  `ReviewContext`, `CoordinationRecord`,
  `ReviewExchangeStore`, and canonical paths to create valid durable evidence;
  they write malformed candidates directly only for damage cases.
- Subprocess coverage invokes `rvw_status.bat` from a nested caller path and the
  direct module with the same root, parses JSON, and compares full payloads.
- No production type is added in this step; it closes the feature with public
  behavior and non-mutation evidence.

**Completion criteria**:

- `ghog single tests/acceptance/review_status/test_review_status_acceptance/test_review_status_acceptance_tdd.py`
  passes.
- `rg -n "rvw_status|convergence|owning-action|escalated|Umbrella|git status|index" tests/acceptance/review_status`
  shows public command, state, identity, and read-only coverage.
- The acceptance file covers every row in the design acceptance table and both
  entry points.
- `ghog day` reports the objective with `exit=0`.

#### Step 4 addendums for acceptance and rollout

Line-budget checkpoint:

- `tests/acceptance/review_status/__init__.py`: before 0; below-550 safe;
  repository ceiling 650; expected at or below 5 lines (advisory).
- `tests/acceptance/review_status/conftest.py`: before 0; below-550 safe;
  repository ceiling 650; expected at or below 240 lines (advisory).
- `tests/acceptance/review_status/test_review_status_acceptance/__init__.py`:
  before 0; below-550 safe; repository ceiling 650; expected at or below 5
  lines (advisory).
- `tests/acceptance/review_status/test_review_status_acceptance/test_review_status_acceptance_tdd.py`:
  before 0; below-550 safe; repository ceiling 650; expected at or below 380
  lines (advisory).

The proactive split raises the combined advisory estimate from 520 to 620 lines
because the extracted fixture module needs its own imports, docstring, fixture
decorators, and explicit signatures; both files remain below the risk band.

Split guidance:

- Keep repository and durable-exchange builders in
  `tests/acceptance/review_status/conftest.py` from the start and keep public
  scenario assertions in the test leaf.
- If `conftest.py` itself approaches 550, split protocol-state
  construction from subprocess invocation rather than weakening scenarios.

Full workflow timing run readiness:

- `tests/acceptance/review_status/test_review_status_acceptance/test_review_status_acceptance_tdd.py`;
  `ghog day`.

Time-gated status for Step 4:

- No wall-clock threshold is introduced. Repeated-call byte equality, bounded
  read-count unit evidence, and full Git-state equality are the rollout gates.

---

# eof

## Open questions for the v0.11.0 review-status-command implementation plan

### Q01: Concrete immutable record mechanism

Question description: Step 1 requires immutable typed records and closed
vocabularies, but it does not name the concrete Python mechanism. Which
mechanism should `tools/review_status_models.py` use so validation, comparison,
and later JSON projection stay explicit without adding a dependency?

#### BBQ for Q01

The plan has specified the compartments of a toolbox but not the material used
to make them. A rigid molded tray makes every tool location obvious, while a
looser bag is quicker to assemble but easier to misuse. In this picture: the
toolbox is the status result, the compartments are its typed fields, and the
material is the Python record mechanism.

#### Options for Q01

- Option 1A: Use frozen standard-library dataclasses plus string-valued enums.
  - pro: Matches the no-new-dependency constraint and gives explicit fields,
    validation hooks, equality, and immutability.
  - con: Requires deliberate constructor validation and serialization code.
- Option 1B: Use `NamedTuple` records plus enums.
  - pro: Produces compact immutable values with tuple equality.
  - con: Makes nontrivial validation and schema evolution awkward.
- Option 1C: Add a runtime validation library such as Pydantic.
  - pro: Provides rich validation and serialization facilities.
  - con: Adds a dependency and a second model convention to the repository.

#### Recommended option for Q01 (with arguments for this choice)

Option 1A: Frozen dataclasses and string-valued enums provide the strict typed
boundary the plan needs while following the repository's standard-library
model style. Their small amount of explicit validation is useful because it
makes the status schema rules visible in the implementation.

#### Answer to Q01: option 1A (with reason why it must be accepted as the answer)

Option 1A: Accept frozen dataclasses plus string-valued enums because they keep
the new public result immutable, dependency-free, and straightforward to test.

### Q02: Ownership of JSON schema projection

Question description: Step 1 calls for stable `to_dict()` output, and Step 3
adds a JSON renderer. Should each model explicitly project its schema, should a
single serializer inspect all records, or should generic dataclass conversion
define the wire format?

#### BBQ for Q02

A shipping manifest can be filled out at each packing station, reconstructed by
one clerk at the loading dock, or inferred from whatever happens to be in each
box. In this picture: packing stations are individual model types, the loading
dock is the JSON renderer, and the manifest is the versioned machine schema.

#### Options for Q02

- Option 2A: Give each public record an explicit `to_dict()` projection and let
  the top-level result compose those projections.
  - pro: Keeps wire names, enum values, nulls, and field order intentional and
    close to the owning type.
  - con: Adds repetitive projection methods across several small records.
- Option 2B: Put all projection logic in one serializer module.
  - pro: Centralizes the machine-format implementation.
  - con: Couples one function to every model field and can drift from model
    validation.
- Option 2C: Use `dataclasses.asdict()` followed by generic enum conversion.
  - pro: Requires the least handwritten code.
  - con: Accidentally turns internal field layout into the public schema and
    makes later refactoring risky.

#### Recommended option for Q02 (with arguments for this choice)

Option 2A: Explicit projections make the versioned output a deliberate API and
allow tests to pin every nested shape without teaching the renderer about model
internals. The repetition is bounded because the artifact set and record types
are fixed.

#### Answer to Q02: option 2A (with reason why it must be accepted as the answer)

Option 2A: Accept per-record explicit projection because schema stability is
more important than minimizing a small amount of deterministic mapping code.

### Q03: Initial placement of pure projection helpers

Question description: Step 2 estimates `tools/review_status.py` at up to 450
lines and defers `tools/review_status_projection.py` until the service would
exceed 650. Should role, lease, artifact, action, outcome, and ordering helpers
start in the service or be separated immediately?

#### BBQ for Q03

A workshop can keep measuring tools beside the assembly bench until space runs
out, or build a dedicated measuring station before the first product. In this
picture: the assembly bench is `review_status.py`, the measuring tools are the
pure projection tables, and the dedicated station is
`review_status_projection.py`.

#### Options for Q03

- Option 3A: Keep private pure helpers in `review_status.py` initially and split
  only if the repository ceiling or a clear responsibility boundary requires
  it.
  - pro: Keeps one cohesive collection implementation and follows the current
    file list and advisory estimate.
  - con: The service may become visually dense before reaching the hard limit.
- Option 3B: Create `review_status_projection.py` in Step 2 from the start.
  - pro: Separates pure mapping tests from filesystem orchestration immediately.
  - con: Adds a production module and cross-module API before measured size
    shows that it is needed.
- Option 3C: Put the projection helpers on the result models.
  - pro: Reduces the number of service-level helpers.
  - con: Mixes observed protocol-state interpretation into transport records.

#### Recommended option for Q03 (with arguments for this choice)

Option 3A: Begin with private pure helpers in the service because the expected
450 lines remain below the 550-line risk band and the plan already defines a
specific extraction boundary if growth proves the estimate wrong.

#### Answer to Q03: option 3A (with reason why it must be accepted as the answer)

Option 3A: Accept the single initial service module because it avoids premature
surface area while preserving a ready, responsibility-based split path.

### Q04: Read-boundary injection for bounded IO tests

Question description: Step 2 requires exact assertions for configuration loads,
candidate enumeration, coordination reads, artifact probes, and forbidden
writes. How should tests control those boundaries without complicating the
public `collect_review_status(root, wall_clock)` API?

#### BBQ for Q04

To audit a meter, inspectors can replace the whole pipe network, attach a test
panel behind the public gauge, or watch every valve with scattered cameras. In
this picture: the gauge is `collect_review_status`, the test panel is a private
dependency bundle, and the cameras are individual monkeypatches at filesystem
call sites.

#### Options for Q04

- Option 4A: Keep the public function simple and route its IO through a small
  private dependency bundle whose default uses the real repository APIs.
  - pro: Enables precise deterministic counts and race simulation while keeping
    callers unaware of test seams.
  - con: Introduces an internal abstraction used mainly for orchestration tests.
- Option 4B: Monkeypatch `Path`, parser, store, and observer functions directly
  in each test.
  - pro: Adds no production abstraction.
  - con: Produces brittle tests coupled to import locations and makes exact
    read accounting hard to understand.
- Option 4C: Add optional collaborators to the public collector signature.
  - pro: Makes every dependency explicit and directly replaceable.
  - con: Exposes test-oriented parameters in the command's production API.

#### Recommended option for Q04 (with arguments for this choice)

Option 4A: A private dependency bundle gives the read-count and
changed-during-read tests one controlled seam while the public collector keeps
only meaningful production inputs. It also makes forbidden lock and write
access easy to fail immediately.

#### Answer to Q04: option 4A (with reason why it must be accepted as the answer)

Option 4A: Accept a private IO dependency bundle because it provides strong,
stable bounded-read evidence without widening the public command contract.

### Q05: Property-based test boundary

Question description: Step 2 requires Hypothesis coverage for enumeration-order
independence across valid and malformed names. Should each generated example
build filesystem candidates, exercise pure ordering inputs, or combine both
levels?

#### BBQ for Q05

A sorter can be stress-tested with labels on a tabletop, with full parcels on a
conveyor, or with labels for volume and a few parcels for integration. In this
picture: labels are normalized status entries, parcels are filesystem-backed
candidates, and the sorter is deterministic result ordering.

#### Options for Q05

- Option 5A: Generate normalized entries for high-volume permutation properties
  and keep representative filesystem permutations in parameterized tests.
  - pro: Gives broad, fast ordering coverage while preserving focused discovery
    integration evidence.
  - con: The property test alone does not exercise parsing and IO.
- Option 5B: Build a temporary filesystem for every generated example.
  - pro: Exercises the complete discovery pipeline under generated inputs.
  - con: Makes shrinking slow and can turn an ordering property into a flaky IO
    workload.
- Option 5C: Test only a fixed matrix of filesystem permutations.
  - pro: Is simple and easy to diagnose.
  - con: Does not satisfy the plan's explicit arbitrary-order property goal.

#### Recommended option for Q05 (with arguments for this choice)

Option 5A: Keep the high-cardinality permutation property pure, then use
parameterized filesystem tests to prove that discovery supplies the same
normalized inputs. This preserves both speed and boundary coverage.

#### Answer to Q05: option 5A (with reason why it must be accepted as the answer)

Option 5A: Accept the layered property strategy because it proves ordering over
many inputs without making filesystem cost dominate the test suite.

### Q06: Renderer regression evidence

Question description: Step 3 asks for stable human and compact JSON output but
does not say whether tests should rely on complete golden strings, targeted
field assertions, or a mixture. Which evidence best protects formatting and
schema stability while keeping failures readable?

#### BBQ for Q06

A printer can be checked by comparing the whole proof sheet, measuring only key
marks, or doing both at different levels. In this picture: the proof sheet is a
complete renderer snapshot, the key marks are field assertions, and the printer
is the pair of status renderers.

#### Options for Q06

- Option 6A: Assert complete compact JSON strings and complete representative
  human blocks, with focused assertions for variant fields.
  - pro: Pins ordering, whitespace, labels, nulls, and tags while limiting large
    expected fixtures.
  - con: Intentional presentation changes require updating representative
    snapshots.
- Option 6B: Assert every complete output for every scenario.
  - pro: Maximizes byte-level regression detection.
  - con: Creates repetitive fixtures and noisy failures for small formatting
    changes.
- Option 6C: Assert only parsed JSON fields and human substrings.
  - pro: Produces resilient, concise tests.
  - con: Does not prove byte stability, complete field presence, or label order.

#### Recommended option for Q06 (with arguments for this choice)

Option 6A: Complete representative outputs establish the stable formatting
contract, while targeted variant assertions keep the finite state matrix from
duplicating large strings.

#### Answer to Q06: option 6A (with reason why it must be accepted as the answer)

Option 6A: Accept mixed golden and focused assertions because it protects the
wire and human contracts without making every test a bulky snapshot.

### Q07: Launcher coverage split between unit and acceptance tests

Question description: Step 3 assigns launcher self-location and exit forwarding
to the CLI unit leaf, while Step 4 invokes the real batch launcher end to end.
How should those tests divide responsibility so the same subprocess scenarios
are not duplicated?

#### BBQ for Q07

A vehicle can be checked on a component bench and again on a road, but repeating
the entire road course in both places wastes time. In this picture: the
component bench is the Step 3 unit leaf, the road is Step 4 acceptance, and the
vehicle is `rvw_status.bat` plus its Python entry point.

#### Options for Q07

- Option 7A: Keep Step 3 launcher tests focused on argument and exit-code
  forwarding with a controlled Python target, and reserve real-repository
  caller-root parity for Step 4.
  - pro: Gives fast launcher diagnostics without duplicating acceptance setup.
  - con: Requires a narrow test hook or controlled environment for the batch
    process.
- Option 7B: Run the same real temporary-repository subprocess matrix in both
  steps.
  - pro: Gives maximal end-to-end confidence at each layer.
  - con: Duplicates slow setup and makes ownership of failures unclear.
- Option 7C: Test the batch launcher only in Step 4.
  - pro: Keeps unit tests entirely inside Python.
  - con: Delays discovery of quoting or exit-forwarding defects until the final
    step.

#### Recommended option for Q07 (with arguments for this choice)

Option 7A: A narrow Step 3 process test should pin the batch contract, while
Step 4 alone owns real nested repositories and payload parity. This catches
launcher defects early without repeating the feature matrix.

#### Answer to Q07: option 7A (with reason why it must be accepted as the answer)

Option 7A: Accept the focused-unit and real-acceptance split because each layer
then has distinct evidence and faster failures.

### Q08: Acceptance fixture extraction timing

Question description: The original Step 4 draft estimated one acceptance file
at 520 lines, only 30 lines below the risk band, and proposed `conftest.py` only
after the file reached 550. Should reusable repository and exchange builders be
extracted from the start or only after measured growth?

#### BBQ for Q08

A crowded kitchen can install a prep counter before opening, wait until the main
counter is full, or move every station into a separate room. In this picture:
the main counter is the acceptance test leaf, the prep counter is
`conftest.py`, and prepared ingredients are reusable repository and exchange
builders.

#### Options for Q08

- Option 8A: Create `tests/acceptance/review_status/conftest.py` in Step 4 from
  the start for repository and durable-exchange builders.
  - pro: Keeps the scenario leaf focused and provides margin below the risk band.
  - con: Adds one planned file before an actual line count proves it mandatory.
- Option 8B: Keep all helpers in the acceptance leaf until it reaches 550 lines,
  then extract them.
  - pro: Follows measured growth and avoids a speculative file.
  - con: Makes a near-threshold file likely and forces a mechanical split during
    the final implementation step.
- Option 8C: Create multiple helper modules immediately.
  - pro: Maximizes responsibility separation from the start.
  - con: Spreads one acceptance suite across more files than current evidence
    justifies.

#### Recommended option for Q08 (with arguments for this choice)

Option 8A: The estimate is already close enough to the risk band that one
conventional `conftest.py` is justified. It keeps builders reusable and leaves
the public scenario file at an estimated 380 lines, 170 lines below the
550-line risk band instead of only 30, without over-fragmenting the suite.

#### Answer to Q08: option 8A (with reason why it must be accepted as the answer)

Option 8A: Accept one acceptance `conftest.py` from the start because the
planned scenario breadth makes the split predictable and responsibility-based;
the separate 240-line fixture estimate leaves the 380-line scenario leaf with
170 lines of estimated risk-band headroom.
