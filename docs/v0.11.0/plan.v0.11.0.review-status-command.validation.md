# v0.11.0 review-status-command implementation validation plan

No, it is not implemented.

This validation plan mirrors
`plan.v0.11.0.review-status-command.md`. It records the evidence required to
decide whether each numbered implementation step is complete without changing
the settled review-status design.

## Validation scope

Validation covers the root `rvw_status` launcher, the typed status model,
candidate discovery and normalization, deterministic rendering, command-line
behavior, acceptance scenarios, and the read-only trust boundary. It excludes
changes to the review-exchange protocol, coordination schema, or writer
behavior.

## Complexity validation for v0.11.0 review status

The implementation check must confirm:

- root candidate discovery is linear in the number of matching directory
  entries;
- candidate normalization is linear in the number of discovered candidates;
- the only required super-linear operation is the deterministic `O(n log n)`
  result ordering;
- artifact projection remains constant per candidate because the supported
  artifact-kind set is fixed at six; and
- no candidate-to-candidate nested scan introduces accidental quadratic work.

## File-based IO cost validation for v0.11.0 review status

The implementation check must confirm one root prefix enumeration and one
configuration read per invocation. Each candidate may perform only the bounded
coordination fingerprint reads and the fixed observer/artifact reads required
by the design. The command must build one in-memory result before rendering and
must not acquire locks, write protocol files, or mutate Git state.

## Shared validation commands

Run the narrow unit or acceptance leaf named by each step first, then run the
repository workflow gate after the final step. Record actual command results in
the matching analysis section when implementation checks occur.

## Step 1 validation -- define the versioned review-status result model

### Analysis of Step 1 implementation state

Yes. Step 1 has been fully implemented.

The repository now has one immutable typed result model with the complete
closed vocabularies, tagged healthy and damaged entries, explicit wire
projection, and constructor invariants required before discovery or rendering.

### Step 1 goal

Confirm that the public result model represents repository identity, command
role, umbrella context, healthy and damaged candidate entries, leases,
artifact applicability and presence, semantic next actions, and the aggregate
status code without leaking mutable protocol objects.

### Step 1 improvement expectations

- The result is immutable and typed at the review-status boundary.
- Healthy and damaged candidates cannot be confused by consumers.
- The six supported artifact kinds and status-code meanings are explicit.
- Constructor validation rejects impossible combinations early.

### Step 1 files to validate

- `tools/review_status_models.py`
- `tests/unit/tools/test_review_status_models/__init__.py`
- `tests/unit/tools/test_review_status_models/test_review_status_models_tdd.py`

### What was implemented for Step 1

- **Closed machine vocabulary**: `ReviewStatusOutcome`, `LeaseFreshness`,
  `ArtifactApplicability`, `NextAction`, `ArtifactKind`, and
  `RoleSpecialization` define stable string values for every downstream
  consumer.
- **Immutable typed evidence**: frozen `ArtifactStatus`, `LeaseStatus`,
  `ExchangeStatus`, `DamagedCandidateStatus`, and `ReviewStatusResult` records
  validate paths, timestamps, protocol relationships, aggregate flags, and
  the fixed six-artifact mapping at construction time.
- **Stable serialization and status**: every public record has an explicit
  `to_dict()` projection, while the result root owns schema version, absolute
  repository root, ordered entries, active count, error flag, and process
  status mapping.
- **Validation evidence**: the focused invariant suite passes, the required
  symbol search finds every public component and its tests, and the final
  `ghog day` completed with `fail=0 warn=0 xfail=0 cov=100 outliers=0
  excluded=0 exit=0`.

### New types or classes introduced for Step 1

- `ReviewStatusModelError`: reports invalid or contradictory normalized
  review-status evidence.
- `ReviewStatusOutcome`, `LeaseFreshness`, `ArtifactApplicability`,
  `NextAction`, `ArtifactKind`, and `RoleSpecialization`: closed string-valued
  vocabularies for the versioned result.
- `ArtifactStatus` and `LeaseStatus`: immutable subordinate evidence records
  that retain observed values and their derived categories together.
- `ExchangeStatus` and `DamagedCandidateStatus`: the tagged healthy and damaged
  entry union without guessed identity.
- `ReviewStatusResult`: the immutable repository result, wire-schema root, and
  process-status authority.

### Architecture check for Step 1

- **Protocol-model placement**: the new module contains only normalized domain
  records and pure validation/projection helpers; it performs no discovery,
  rendering, process, or filesystem work.
- **Dependency direction**: it imports only the standard library and the
  existing review-exchange identity and state types that it normalizes. No
  adapter or technical runtime dependency enters the model boundary.
- **Maintainability**: validation is split into small single-purpose helpers.
  The 408-line model and 455-line unit leaf remain below the plan's 550-line
  safe band and the repository's 650-line ceiling.

No, there is nothing that needs to be addressed for Step 1.

### Performance check for Step 1

- **No new `O(n^2)` or `O(n log n)` path**: constructor validation performs a
  fixed number of scalar checks and one pass over the six-key artifact map.
- **Projection bound**: subordinate records project in constant time;
  `ReviewStatusResult.to_dict()` is linear only in its ordered entry count.
- **IO bound**: the model performs no IO, locking, Git access, or protocol
  mutation.
- **Plan-bound alignment**: Step 1 remains pure in-memory validation and
  projection, as planned.

No, there is no performance issue that needs to be addressed for Step 1.

### Unit test coverage check for Step 1

- **Closed vocabularies and serialization**: exact enum values and every public
  `to_dict()` shape are asserted.
- **Immutable records and constructor guards**: healthy, damaged, artifact,
  lease, code-family, aggregate, invalid-path, invalid-type, and contradictory
  state branches are exercised by the dedicated unit leaf.
- **Coverage boundary**: the unit suite covers every executable line and
  branch in `tools/review_status_models.py`; the full repository run reports
  100% coverage.

No, there is no unit-tested class below 100% that needs completing for Step 1.

### Feature integrity for Step 1

- **Existing protocol behavior**: no existing exchange state, observer, store,
  or workflow behavior was changed.
- **Reporting boundary**: the model adds the stable facts later status
  collection and rendering steps will consume without introducing a competing
  output path.
- **Repository gate compatibility**: existing checks and all 2,149 tests pass
  with the new model and its focused suite present.

No existing feature or reporting capability appears impaired for Step 1.

## Step 2 validation -- discover and normalize every active candidate

### Analysis of Step 2 implementation state

Yes. Step 2 has been fully implemented.

The collector now discovers and normalizes every reserved-prefix candidate
through bounded read-only adapters, fails closed on damaged identity or role
evidence, and has independent exact mapping, filesystem, configuration,
ordering, race, and no-mutation coverage.

### Step 2 goal

Confirm that one repository snapshot discovers every root
`a.review-active.*` candidate, preserves damaged entries, derives ordinary and
escalated roles correctly, reports owner and lease state separately, projects
the fixed artifact set, and detects a coordination change during observation.

### Step 2 improvement expectations

- Candidate enumeration and output are deterministic regardless of directory
  enumeration order.
- The marker-present configuration branch reports its configured timeout.
- The marker-absent configuration branch reports disabled mode and its fallback
  timeout.
- Healthy and damaged candidates coexist in one complete result.
- Convergence, escalation, timeout, umbrella, and artifact states follow the
  settled rules.
- Observation remains bounded and read-only.

### Step 2 files to validate

- `tools/review_status.py`
- `tests/unit/tools/test_review_status/__init__.py`
- `tests/unit/tools/test_review_status/test_review_status_tdd.py`
- `tests/unit/tools/test_review_status/test_review_status_pbt.py`

### What was implemented for Step 2

- **Bounded discovery service**: `collect_review_status()` resolves the root,
  loads configuration and wall time once, enumerates only the reserved root
  prefix, and isolates each candidate failure from its siblings.
- **Strict candidate normalization**: candidate handling reuses
  `parse_transient_identity`, `parse_json_markdown`,
  `CoordinationRecord.from_dict`, canonical path derivation, the existing
  observer, and transcript occurrence authority.
- **Read-only race detection**: exact coordination bytes are compared before
  and after observation, six fixed paths are projected without entering a
  transition lock, and changed evidence becomes a damaged candidate.
- **Pure status projection**: helpers derive lease freshness, artifact
  applicability, next actions, trust outcomes, relative paths, and stable
  healthy-then-damaged ordering.
- **Initial test surface**: example and property leaves cover empty, healthy,
  malformed, mixed, mismatch, missing-file, changed-during-read, idle,
  projection-branch, IO-count, and ordering behavior.
- **Fail-closed role repair**: unsupported human next actors and ambiguous
  escalated artifact shapes now raise a stable diagnostic and are retained as
  damaged candidates instead of inheriting the durable owner.
- **Expanded boundary evidence**: real marker fallback and override, missing
  serialized umbrella identity, canonical mismatch, multiple valid exchanges,
  six named probes, and explicit mutation/transition-lock rejection are
  covered. The generated ordering property was shortened from 1.08 seconds to
  0.04 seconds without removing its assertion.
- **Independent state table evidence**: the exact action and artifact
  applicability expectations now live beside the exact role, specialization,
  owner, lease, and outcome expectations in a dedicated projection leaf.
- **Validation result**: focused leaves and the final repository Groundhog walk
  complete with `fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0`.

### New types or classes introduced for Step 2

- `_StatusDependencies`: a frozen private dependency bundle that keeps the
  public collector signature small while exposing every filesystem, observer,
  store, and occurrence boundary to read-count and no-write tests.
- `_StoreSpy`: a unit-test double intended to reject store mutation while
  retaining the derived fixed paths used by normalization.

### Architecture check for Step 2

- **Boundary placement**: repository enumeration and observer/store adapters
  remain in `review_status.py`, while the public immutable result vocabulary
  remains in `review_status_models.py`; no DDD-Hexagonal dependency inversion
  is introduced.
- **Protocol authority**: `_role_for()` now accepts only an agent-valued next
  actor for ordinary states and requires escalated artifact evidence to name
  exactly one continuing side; the owner remains a separate reported fact.
- **Module girth**: the 500-line service remains below the 650-line hard
  ceiling and remains cohesive around one read-only adapter boundary. The
  477-line example leaf and dedicated projection leaf keep each test
  responsibility below the repository ceiling.

No, there is nothing that needs to be addressed for Step 2.

### Performance check for Step 2

- **Discovery complexity**: one root `iterdir()` pass and one per-candidate
  normalization pass are linear in candidate count.
- **Fixed candidate cost**: coordination fingerprinting is bounded at two
  reads and artifact projection is constant over six kinds; there is no nested
  candidate scan.
- **Ordering complexity**: the sole super-linear operation is the required
  deterministic `sorted()` call, which is `O(n log n)`.

No, there is no performance issue that needs to be addressed for Step 2.

### Unit test coverage check for Step 2

- **Executable-line coverage**: the dedicated example and property leaves
  exercise every executable service line through the implementer's coverage
  gate.
- **Exact state coverage**: role, specialization, owner, lease, action,
  artifact applicability, and outcome are asserted against independent
  expected values for every active state; fail-closed human-turn and
  ambiguous-escalation branches are explicit.
- **Named boundary cases**: configuration propagation, absent serialized
  umbrella identity, canonical mismatch, multiple healthy candidates, and
  explicit no-lock/no-mutation evidence are now covered.

No, there is no unit-tested class below 100% that needs completing for Step 2.

### Feature integrity for Step 2

- **Existing exchange behavior**: the implementation only observes existing
  protocol APIs and does not change requestor, reviewer, store, or state-table
  behavior.
- **Status trust boundary**: malformed, concurrently changed, unsupported
  human-turn, and ambiguous-escalation candidates are retained independently
  without a guessed owner role.
- **Repository compatibility**: the final Groundhog evidence reports a green
  static gate, affected and full suites, 100% coverage, and no duration
  outlier, exclusion, warning, or failure.

No existing feature or reporting capability appears impaired for Step 2.

## Step 3 validation -- expose the status skill and rvw_status command

### Analysis of Step 3 implementation state

Yes. Step 3 has been fully implemented.

The implementation check found every planned Step 3 file and verified that one
normalized result drives both output forms, the CLI owns root and process
boundaries, the launcher preserves the caller repository, and the public
`$llm-shared:review-status-command` skill delegates to that launcher through
one canonical instruction. No missing implementation work remains for this
step.

### Step 3 goal

Confirm that the installed plugin exposes a discoverable read-only status
skill, and that deterministic human-readable output exposes the absolute
repository root, command role, umbrella state, every candidate detail, the
semantic next action, and aggregate trust status through a root Windows
launcher with exact exit-code propagation.

### Step 3 improvement expectations

- Repeated rendering of the same result is byte-identical.
- Output order follows normalized identity and path ordering.
- The launcher works from repository subdirectories.
- Exit codes remain exactly 0, 3, or 2 according to the typed result.
- Every host adapter links directly to the canonical instruction and copies no
  status or mutation policy.

### Step 3 files to validate

- `tools/review_status_render.py`
- `tools/review_status_cli.py`
- `rvw_status.bat`
- `instructions/review-status-command.md`
- `.agent/workflows/review-status-command.md`
- `.agents/llm-shared/instructions/review-status-command.md`
- `.agents/llm-shared/skills/review-status-command/SKILL.md`
- `.claude/skills/review-status-command/SKILL.md`
- `.github/skills/review-status-command/SKILL.md`
- `tests/unit/tools/test_instruction_structure/test_review_status_command_adapters_tdd.py`
- `tests/unit/tools/test_review_status_render/__init__.py`
- `tests/unit/tools/test_review_status_render/test_review_status_render_tdd.py`
- `tests/unit/tools/test_review_status_cli/__init__.py`
- `tests/unit/tools/test_review_status_cli/test_review_status_cli_tdd.py`

### What was implemented for Step 3

- `tools/review_status_render.py` renders one immutable result as either a
  stable labelled human report or compact Unicode JSON. Healthy blocks expose
  identity, reviewed document, umbrella, protocol position, distinct
  role/specialization/owner fields, lease evidence, all six artifacts, next
  action, and diagnostic. Damaged blocks retain only safe evidence.
- `tools/review_status_cli.py` resolves the Git root, collects and renders once,
  routes output by trust outcome, and returns typed status `0`, `3`, or `2`.
- `rvw_status.bat` self-locates the newest llm-shared Python, prepends its root
  to `PYTHONPATH`, retains `%CD%`, forwards arguments, and propagates status.
- `instructions/review-status-command.md` defines the read-only agent workflow,
  invokes `rvw_status` by full path from the caller repository, interprets
  statuses `0`, `3`, and `2`, and forbids mutation or duplicated state logic.
- Thin Codex, Claude, GitHub, and workflow adapters expose the exact
  `review-status-command` name and point directly to the canonical instruction.
- The planned test leaves cover complete output snapshots, compact JSON,
  damaged mixtures, no-IO rendering, roots, outcomes, streams, direct module
  execution, the real launcher through a controlled executable target, and
  adapter structure and discovery metadata.

### New types or classes introduced for Step 3

No new public domain type was needed. The CLI adds private `_InvocationError`
and `_ArgumentParser` adapter types so argparse failures obey status two instead
of terminating outside `main()`.

### Architecture check for Step 3

- Both renderers depend only on `ReviewStatusResult`; the no-IO test rejects
  filesystem or subprocess access after collection.
- Root discovery, clock creation, stream routing, and process status remain in
  the thin CLI. The service is called once and renderers repeat no status logic.
- The canonical skill owns only invocation and result interpretation. Every
  provider wrapper is a thin direct reference, so no host-specific policy fork
  can drift from `rvw_status`.
- The real batch-process test proves runtime selection, caller preservation,
  `PYTHONPATH`, argument forwarding, and status propagation.
- Ty, Pyright, Ruff, Radon, Vulture, file-size, Markdown, ShellCheck, and EOF
  checks pass. Every planned Python file remains below 650 lines.

No, there is nothing that needs to be addressed for Step 3.

### Performance check for Step 3

- Rendering is an in-memory linear projection; CLI work remains one root
  resolution, one collection, and one render.
- Profiling found 0.617 seconds of the initial 0.69-second launcher-test call in
  Windows subprocess startup/join. The unchanged real process and assertions
  now use a module-scoped fixture, leaving the measured call below the floor.
- The final full run reports no duration outlier; its slowest measured call is
  an unrelated recovery test at 0.34 seconds against the 0.50-second floor.

No, there is no performance issue that needs to be addressed for Step 3.

### Unit test coverage check for Step 3

- The renderer and CLI leaves retain their 19 passing calls. The new adapter
  leaf adds three passing calls for canonical references, public discovery
  metadata, and absence of copied policy.
- The final detached `ghog day` reached `state=done`, `exit=0`: static checks,
  three affected calls, and all 2,205 full-suite calls passed at 100% coverage,
  with zero warnings, failures, or outliers.
- The skill creator reports `Skill is valid!`, and plugin validation passes for
  `.agents/llm-shared` after refreshing the cachebuster to
  `0.1.0+codex.20260831140034`.
- Coverage includes existing non-Git roots, absent Git ancestors, the aware
  production clock, and direct module status forwarding.

No, there is no unit-tested class below 100% that needs completing for Step 3.

### Feature integrity for Step 3

- Human and JSON output share the model projection and preserve ordered tagged
  healthy/damaged evidence.
- Umbrella absence is `none` for humans and `null` for machines; exact paths
  and Unicode repository roots survive without renderer normalization.
- Operational failures emit no partial stdout payload, while untrustworthy
  candidate evidence remains available on stdout with status `3`.
- The complete repository gate found no existing feature regression.

No existing feature or reporting capability appears impaired for Step 3.

## Step 4 validation -- prove end-to-end behavior and read-only rollout

### Analysis of Step 4 implementation state

Not started. Step 4 is not implemented because no implementation check has taken place and the planned files have not been created.

### Step 4 goal

Confirm the complete command against no-candidate, one-candidate,
multiple-candidate, convergence, owning-action, escalation, timeout, umbrella,
and damaged-mixture repositories while proving that repeated invocations leave
the working tree and protocol files unchanged.

### Step 4 improvement expectations

- Acceptance coverage exercises every settled state boundary.
- Mixed healthy and damaged candidates preserve complete diagnosis.
- Read-only assertions compare protocol bytes and Git state before and after.
- The final repository workflow gate passes without weakening existing tests.

### Step 4 files to validate

- `tests/acceptance/review_status/__init__.py`
- `tests/acceptance/review_status/conftest.py`
- `tests/acceptance/review_status/test_review_status_acceptance/__init__.py`
- `tests/acceptance/review_status/test_review_status_acceptance/test_review_status_acceptance_tdd.py`

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

## Final rollout validation

After all four step checks are complete, confirm that the narrow leaves pass,
the full `ghog day` workflow reaches its recorded done state, coverage remains
at the project gate, the launcher returns the specified aggregate statuses, and
the implementation leaves the repository and all review-exchange artifacts
unchanged after observation.

---
