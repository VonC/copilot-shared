# Design v0.11.0 -- Review status command

Reference feature request:
[feature-request.v0.11.0.review-status-command.md](feature-request.v0.11.0.review-status-command.md)

---

## Context for v0.11.0 review status

Review exchanges already persist their identity, ownership, round, lease, and
artifact locations. The missing piece is one family-neutral, read-only view
that discovers those records from the caller's repository and explains who
must continue, which umbrella owns the work, and what protocol action follows.

## Scope for v0.11.0 review status

The v0.11.0 outcomes are:

1. Discover every nonterminal specification and code-review exchange in the
   caller's repository.
2. Render the same trustworthy facts for humans and machine consumers.
3. Preserve damaged-exchange evidence without changing any review or Git state.

### In scope for v0.11.0 review status

- a repository-root `rvw_status` entry point that preserves caller context;
- a shared read-only status service with human and JSON renderers;
- canonical identity, role, umbrella, lease, artifact, and next-action fields;
- independent results for healthy and damaged exchanges; and
- stable success, untrustworthy-result, and operational-failure outcomes.

### Deferred from v0.11.0 review status

- selecting one exchange when several are active;
- renewing, reclaiming, repairing, cancelling, or completing an exchange;
- executing the reported next action; and
- the `rvw_resume` continuation command.

---

## Confirmed technical facts for v0.11.0 review status

**Exact state classification already exists**: `ReviewExchangeObserver` reads
one bound exchange without mutation, validates its live artifacts, evaluates
lease currency, and delegates to the pure `classify_snapshot` state table.

**Canonical paths already exist**: `derive_artifact_paths` returns the request,
answer, coordination, tombstone, transcript, and transition-lock paths from a
validated `ReviewContext`; transient filenames can also be parsed into an
`ExchangeIdentity`.

**Coordination records carry the required authority**: a strict
`CoordinationRecord` contains the exact context and family policy, `owner`,
`expected_next_actor`, round, lease timestamp, confirmation fields, and
incomplete-transition evidence.

**Lease expiry uses project configuration**: the observer compares
`lease_renewed_at` plus `ReviewConfiguration.wait_timeout_seconds` with an
injected wall clock.

**Caller-root precedent is available**: `commit-plan-check` discovers upward
from `Path.cwd()` unless `--root` is supplied, and its root launcher preserves
the caller's working directory while self-locating the shared Python runtime.

---

## Current behavior for v0.11.0 review status

The existing exchange command observes one identity supplied by its caller:

```txt
exact document and policy
  -> derive one artifact set
  -> observe and classify one exchange
  -> render one operation result
```

A returning caller must therefore remember enough identity to invoke that
single-exchange path. There is no repository-wide discovery result, no explicit
continuing-agent view, and no shared cardinality or trustworthiness outcome.

## Target behavior for v0.11.0 review status

```txt
caller working directory or explicit root
  -> validated Git repository root
  -> canonical coordination-record discovery
  -> strict record and filename validation per entry
  -> existing observer classification for valid identities
  -> normalized status records
  -> one human report or one versioned JSON result
```

Discovery never takes a review family, document, slug, step, round, occurrence,
role, or artifact path. It reads only protocol-owned coordination candidates at
the resolved repository root. Each candidate becomes either a validated
exchange status or a damaged-entry diagnostic; one bad candidate does not
discard healthy results.

---

## Repository and discovery boundary for v0.11.0 review status

### Caller repository resolution

The default root is discovered upward from the caller's current working
directory. An explicit `--root` selects a repository for controlled callers and
tests. Both the root launcher and direct shared entry point pass the same
resolved root into the status service; the launcher self-locates its runtime
without changing directories.

A missing Git root, unreadable root, or invalid explicit root is an operational
failure. It produces no guessed repository and no partial exchange result.

### Coordination-record discovery

Discovery enumerates only canonical active coordination filenames at the root.
For each candidate it:

1. parses the filename identity;
2. strictly parses the coordination record;
3. verifies that filename identity, record context, and derived canonical paths
   agree; and
4. invokes the existing observer with the record's exact context and policy.

The document and umbrella values come from durable exchange context. A legacy
record missing umbrella identity is repair-required; document metadata may be
shown as a hint but never promoted into authoritative identity.

`idle` observations are excluded from the active list. Every other
`ArtifactState` value is included verbatim, including
`owning-action-pending`, abandoned, interrupted, repair-pending, escalated, and
inconsistent states.

## Normalized exchange result for v0.11.0 review status

### Stable machine record

The JSON document has a schema version, repository root, overall outcome,
active count, error flag, and an ordered `exchanges` array. Each exchange entry
contains:

- canonical family, type, version, slug, reviewed document, umbrella or null,
  implementation step or null, round, and occurrence;
- exact state and diagnostic;
- continuing role, role specialization, and owner;
- lease timestamp, configured timeout, and derived freshness;
- canonical artifact paths with applicability and observed presence; and
- stable next-action identity plus its human rendering.

Entries use a deterministic identity order so unchanged repository evidence
produces stable output.

### Continuing-agent mapping

For ordinary agent turns, the broad continuing role comes directly from
`expected_next_actor`, and family plus role supplies the specialization.
`owner` remains a separate field.

Two states intentionally record a human next actor. At `convergence-gate`, the
continuing agent is `requestor`, the owner remains `reviewer`, and the
next-action identity says that human confirmation is required. At `escalated`,
the continuing role is the agent named by the artifact shape and the next action
is human escalation resolution. A human next actor in any other state is
inconsistent. Genuine corruption reports role `unknown`; a healthy
owner/next-actor difference does not.

### Lease freshness

The raw `lease_renewed_at` value remains authoritative. The derived lease block
also reports the expiry timestamp, evaluation timestamp, configured timeout,
and one of `current`, `expired`, `not-held`, or `missing`. `not-held` means the
protocol deliberately cleared the lease at `convergence-gate` or `escalated`;
`missing` is a defect in a state that should carry lease evidence. Consumers can
derive elapsed or overdue duration from the fixed timestamps. Status does not
renew or reclaim the lease.

### Artifact completeness

Each of the six paths comes from `derive_artifact_paths`, never from locally
reconstructed names. Every path record carries an applicability value and an
observed presence boolean. Expected-but-missing and unexpected-but-present
shapes remain visible and feed the exchange diagnostic.

### Next-action identity

One closed action vocabulary describes protocol intent independently of display
text. Its values distinguish waiting for the counterpart, requestor or reviewer
work, human confirmation, authorized owning work, reclaim, repair, escalation
resolution, and no safe action. The human command or description is rendered
from that identity and the exact exchange context, so the two forms cannot
drift.

## Human report and command outcome for v0.11.0 review status

### Human-readable report

The human renderer starts with the repository and overall outcome, then prints
one labelled block per exchange. `Role`, `Specialization`, `Owner`, and
`Umbrella` are separate visible fields. Umbrella uses the exact
repository-relative path or the literal `none`. Damaged entries retain their
candidate path and diagnostic even when their full identity cannot be trusted.

### Trustworthiness and process status

- Status `0` means the query is trustworthy, whether it found zero, one, or
  several well-formed active exchanges.
- Status `3` means the command completed but at least one candidate is
  unreadable, malformed, inconsistent, or repair-required. Trustworthy partial
  entries remain in both output forms.
- Status `2` means invocation, root resolution, or another operational boundary
  prevented a trustworthy query.

The human and JSON renderers consume the same normalized result, and process
status is derived from its overall outcome rather than from renderer text.

## Read-only trust boundary for v0.11.0 review status

The status path opens artifacts for reading and performs bounded Git root
queries only. It never enters the exchange transition lock and never calls
store publication, lease, recovery, confirmation, completion, marker, index, or
ref mutation operations. Repeated calls over unchanged files and the same wall
clock freshness bucket return the same normalized identity and action data.

Filesystem races are reported as damaged or operational evidence rather than
retried through a mutating recovery path. The later resume feature consumes the
status result and owns every state-changing choice.

---

## Acceptance cases for v0.11.0 review status

| Scenario | Expected outcome | Reason |
| --- | --- | --- |
| No coordination records | Status `0`, active count `0`, empty exchange list | No active work is a trustworthy result. |
| One request pending | Reviewer continuing role, requestor owner, exact umbrella, wait-for-reviewer action | `expected_next_actor` controls the next agent while ownership remains separate. |
| Convergence gate | Requestor continuing role, reviewer owner, human-confirmation action, and `not-held` lease | The agent continuation, durable owner, and human authority remain distinct. |
| Owning action pending | Requestor role and authorized-owning-work action | A returning agent must not repeat the human gate. |
| Escalated exchange | Escalated state, artifact-shape continuing role, resolve-escalation action, `not-held` lease, overall status `3` | A valid human-resolution stop is diagnostic, not inconsistent. |
| Wait timeout escalation | Original request retained, artifact-shape reviewer role, resolve-escalation action, `not-held` lease, overall status `3` | An overnight stopped handoff remains identifiable and recoverable. |
| Standalone review | Visible `Umbrella: none` and JSON null | Confirmed absence is explicit in both renderers. |
| Legacy record missing umbrella | Status `3`, repair diagnostic, optional metadata hint | Missing identity is not silently inferred or changed to `none`. |
| Current and old leases | Raw timestamps plus current/expired freshness and age | State gives the kind of interruption; freshness gives its degree. |
| Missing expected answer | Canonical answer path marked missing and exchange diagnostic retained | Diagnosis reports both expected shape and observed evidence. |
| Healthy and damaged records together | Healthy entries plus damaged entry, overall status `3` | One defect does not hide independent exchanges. |
| Launcher called from another repository | That caller repository is reported and matches direct-entry output | Runtime location does not replace caller context. |
| Repeated unchanged query | No review artifact, lease, marker, index, ref, or working-tree change | Status remains strictly read-only. |

## Open questions for the v0.11.0 design

### Q01: Which filenames enter review-exchange discovery?

Question description: Status must find damaged exchanges as well as healthy
ones. The discovery boundary must decide whether only fully parseable canonical
coordination names enter the result or whether malformed files under the
reserved coordination prefix also appear as diagnostics.

#### BBQ for Q01

A mailroom should not ignore a parcel merely because its label is smudged, but
it also should not collect every object in the lobby. In this picture: the
mailroom is status discovery, the reserved prefix is the parcel area, and a
smudged label is a malformed coordination filename.

#### Options for Q01

- Option A1: Enumerate every root file under the reserved
  `a.review-active.*.md` prefix, parse canonical names normally, and return a
  damaged candidate for each near-match that cannot be parsed.
  - pro: Makes malformed coordination evidence visible instead of silently
    dropping it.
  - con: A stray user file under the reserved prefix becomes a status error.
- Option A2: Enumerate only filenames that match the canonical grammar.
  - pro: Every candidate begins with a usable exchange identity.
  - con: A damaged filename disappears from the command meant to diagnose it.
- Option A3: Read only coordination paths derived from versioned transcripts.
  - pro: Starts from durable, user-visible review history.
  - con: Misses an exchange before its transcript exists and makes transcripts
    an identity authority.

#### Recommended option for Q01 (with arguments for this choice)

Option A1: Treat the full reserved coordination prefix as the candidate
boundary and strict canonical parsing as validation. The prefix is already
protocol-owned, so a malformed file there is evidence worth reporting.

#### Answer to Q01: option A1 (with reason why it must be accepted as the answer)

Option A1: Accept this because hiding a malformed coordination filename would
make repository-wide status look trustworthy while unfinished review evidence
was present but unreadable.

### Q02: How should healthy and damaged entries share one JSON schema?

Question description: A damaged candidate may lack a trustworthy family,
document, role, or round. The schema must represent that partial evidence
without filling normal identity fields with guesses or nulls whose meanings
are unclear.

#### BBQ for Q02

An incident form should not make a witness invent a licence plate that was
never visible. It should clearly distinguish a complete vehicle record from a
partial sighting. In this picture: the licence plate is exchange identity, the
partial sighting is a damaged candidate, and the incident form is the JSON
entry schema.

#### Options for Q02

- Option B1: Use a tagged union with `kind: exchange` for validated records and
  `kind: damaged-candidate` for partial evidence.
  - pro: Consumers know which fields are valid before reading them.
  - con: Consumers must handle two entry shapes.
- Option B2: Use one flat entry with nullable identity fields.
  - pro: Every array element has the same keys.
  - con: Null can mean absent, inapplicable, or untrustworthy.
- Option B3: Put damaged candidates in a separate top-level array.
  - pro: Keeps the healthy exchange schema small.
  - con: Splits repository evidence across two collections and complicates
    stable ordering.

#### Recommended option for Q02 (with arguments for this choice)

Option B1: Use an explicit discriminant and give damaged candidates only the
candidate path, facts that parsed safely, and diagnostics. This keeps missing
evidence distinct from valid null values such as a standalone umbrella.

#### Answer to Q02: option B1 (with reason why it must be accepted as the answer)

Option B1: Accept this because the command must never turn untrusted evidence
into apparently valid identity fields, while machine callers still need one
ordered result collection.

### Q03: Which paths are portable fields and which identify the repository?

Question description: The command knows an absolute repository root, while the
requirement calls for exact repository-relative document and umbrella paths.
The schema must settle path representation for artifacts and identity fields.

#### BBQ for Q03

A street address needs the city once, not repeated on every room label inside
the building. In this picture: the city is the absolute repository root, room
labels are repository-relative review paths, and the address book is the JSON
result.

#### Options for Q03

- Option C1: Report one absolute `repository_root` and make every reviewed
  document, umbrella, candidate, and artifact path repository-relative.
  - pro: Results remain portable when the repository moves.
  - con: Consumers must join a path with the root before opening it.
- Option C2: Report absolute paths everywhere.
  - pro: Every returned path can be opened directly.
  - con: Results are machine-specific and duplicate the root in every field.
- Option C3: Report both absolute and relative forms for every path.
  - pro: Supports direct access and portable comparison.
  - con: Doubles path fields and creates consistency obligations.

#### Recommended option for Q03 (with arguments for this choice)

Option C1: Make the repository root the single absolute anchor and use relative
paths everywhere below it. This matches the requirement's umbrella contract
and keeps equality independent of checkout location.

#### Answer to Q03: option C1 (with reason why it must be accepted as the answer)

Option C1: Accept this because later resume logic can resolve paths from one
trusted root without baking one workstation's checkout location into exchange
identity.

### Q04: How are human turns mapped to a continuing agent?

Question description: Most continuing roles come from `expected_next_actor`,
but both `convergence-gate` and `escalated` record a human next actor while
status must still identify the agent who continues after the human decision.
The design must make both supported human-turn mappings explicit.

#### BBQ for Q04

A referee may be waiting for the captain's decision while still knowing which
official restarts play afterward. If a dispute stops the match, the match record
still names the official who resumes once the dispute is settled. In this
picture: the captain is the human at `convergence-gate`, the restarting official
is the requestor, the dispute is `escalated`, and the official named by the
match record is the artifact-shape agent.

#### Options for Q04

- Option D1: Use a state-aware role resolver: agent-valued next actors map
  directly; `convergence-gate` maps to requestor; and `escalated` maps to the
  agent named by the artifact shape.
  - pro: Implements the general next-actor rule and both protocol-supported
    human-turn states.
  - con: Role resolution depends on state as well as actor.
- Option D2: Always report `owner` when the expected next actor is human.
  - pro: Reuses a durable agent field for every human turn.
  - con: Treats ownership as a general role fallback beyond the two confirmed
    states.
- Option D3: Report role `unknown` while a human is expected.
  - pro: Avoids a special mapping.
  - con: Breaks the confirmed requestor identity at convergence.

#### Recommended option for Q04 (with arguments for this choice)

Option D1: Encode the convergence and escalation rules as the two valid
human-turn mappings and treat a human next actor in any other state as
inconsistent.

#### Answer to Q04: option D1 (with reason why it must be accepted as the answer)

Option D1: Accept this because it preserves `expected_next_actor` as the normal
authority without turning `owner` into an undocumented fallback rule. At
`convergence-gate`, status reports continuing role `requestor` beside owner
`reviewer`. At `escalated`, the artifact shape identifies the agent who resumes
after human resolution; reporting `unknown` there would hide the interruption
this command exists to diagnose.

### Q05: What exact lease-freshness evidence should the result expose?

Question description: The requirement asks for the raw renewal timestamp and a
derived freshness indication. The design must settle whether degree of
staleness is a changing age, a fixed expiry time, or only a category.

#### BBQ for Q05

A parking ticket can print when the meter expires and let anyone compare that
fixed time with the clock. Printing only "expired" loses useful detail, while a
counter that changes every second makes snapshots noisy. In this picture: the
ticket time is lease expiry, the clock is evaluation time, and the status
snapshot is the command result.

#### Options for Q05

- Option E1: Report renewal timestamp, derived expiry timestamp, evaluation
  timestamp, configured timeout, and `current`, `expired`, `not-held`, or
  `missing` state. `not-held` applies when the protocol deliberately clears the
  lease for a human turn; `missing` remains damaged evidence elsewhere.
  - pro: Preserves fixed evidence and makes the comparison reproducible.
  - con: Consumers calculate elapsed or overdue duration when they need it.
- Option E2: Also report elapsed or overdue seconds.
  - pro: Humans and callers receive the degree directly.
  - con: The result changes every second even when repository evidence does not.
- Option E3: Report only the freshness category with the renewal timestamp.
  - pro: Keeps the lease block compact.
  - con: Does not show by how much the lease is current or expired.

#### Recommended option for Q05 (with arguments for this choice)

Option E1: Return the fixed lease timestamps, the evaluation timestamp, the
timeout, and a category that separates an intentionally unheld lease from lost
evidence. Together they expose the degree of staleness without making an extra
counter authoritative.

#### Answer to Q05: option E1 (with reason why it must be accepted as the answer)

Option E1: Accept this because a consumer can reproduce the freshness decision
and calculate minutes or days from explicit timestamps while stable evidence
remains separate from display-time calculations. `not-held` keeps healthy
`convergence-gate` and `escalated` records distinct from a damaged record whose
lease evidence is unexpectedly missing.

### Q06: What should the next-action identity represent?

Question description: Status needs one stable machine action identity and a
human rendering. The action vocabulary can name protocol intent, existing CLI
operations, or complete commands.

#### BBQ for Q06

A road sign should name the destination, not prescribe one particular make of
car. In this picture: the destination is protocol intent, the car is a CLI
operation, and the road sign is the next-action identity.

#### Options for Q06

- Option F1: Use a closed semantic vocabulary such as wait, perform requestor
  work, perform reviewer work, confirm, finish authorized work, reclaim,
  repair, resolve escalation, or no safe action.
  - pro: Remains stable when launcher or skill names change.
  - con: Resume must map semantic actions to concrete operations.
- Option F2: Reuse `review_exchange` operation names as action identities.
  - pro: Maps directly to current protocol commands.
  - con: Some next steps are role workflows or human decisions rather than one
    exchange operation.
- Option F3: Store the complete host command as the identity.
  - pro: A caller can execute the value directly.
  - con: Host prefix, wording, and installation details become schema data.

#### Recommended option for Q06 (with arguments for this choice)

Option F1: Keep the identity at protocol-intent level and derive the human
description or command from that value plus exact exchange context.

#### Answer to Q06: option F1 (with reason why it must be accepted as the answer)

Option F1: Accept this because the later resume feature needs a durable routing
fact, not a presentation string tied to today's launcher names.

### Q07: How should artifact completeness be shaped in JSON?

Question description: Every validated exchange reports six canonical paths and
their applicability and presence. The schema must decide whether artifact kind
is a stable key or repeated data inside a list.

#### BBQ for Q07

A toolbox works fastest when each labelled slot always holds the same tool.
In this picture: the slots are artifact-kind keys, the tools are canonical
paths, and an empty slot is expected-but-missing evidence.

#### Options for Q07

- Option G1: Use an object keyed by the six stable artifact kinds, each holding
  path, applicability, and presence.
  - pro: Callers can address one artifact without searching a list.
  - con: Adding an artifact kind extends the object schema.
- Option G2: Use a list of artifact records with a `kind` field.
  - pro: New artifact kinds do not add object keys.
  - con: Consumers must search and guard against duplicate kinds.
- Option G3: Use separate `paths`, `applicability`, and `presence` objects.
  - pro: Groups values by data type.
  - con: Parallel maps can drift and require repeated joins.

#### Recommended option for Q07 (with arguments for this choice)

Option G1: Use one keyed record per canonical artifact kind and validate that
the complete six-key set is present for every healthy exchange.

#### Answer to Q07: option G1 (with reason why it must be accepted as the answer)

Option G1: Accept this because canonical artifact kinds are already a closed
protocol set and direct keyed access makes missing evidence unambiguous.

### Q08: In what order should repository-wide entries appear?

Question description: Filesystem enumeration order is not stable across hosts.
The result needs a deterministic ordering for readable diffs and repeatable
machine output.

#### BBQ for Q08

A library shelves books by a published rule rather than the order they arrived
at the returns desk. In this picture: books are exchange entries, the shelf
rule is identity ordering, and returns-desk order is filesystem enumeration.

#### Options for Q08

- Option H1: Sort by validated identity fields, then candidate path for damaged
  entries.
  - pro: Stable across filesystems and independent of changing urgency.
  - con: The most actionable exchange is not necessarily first.
- Option H2: Sort by urgency and next actor.
  - pro: Puts blocked or damaged work first for humans.
  - con: Ordering changes when state changes and needs a policy ranking.
- Option H3: Preserve filesystem enumeration order.
  - pro: Requires no sorting step.
  - con: Output varies by host and directory history.

#### Recommended option for Q08 (with arguments for this choice)

Option H1: Sort healthy entries by family, type, version, slug, step, and
occurrence, then sort damaged candidates by repository-relative path.

#### Answer to Q08: option H1 (with reason why it must be accepted as the answer)

Option H1: Accept this because stable identity order supports repeatable output
without embedding a debatable urgency policy in status discovery.

### Q09: Which process-status mapping should the command adopt?

Question description: The feature settled successful versus untrustworthy
outcomes but left numeric process statuses to design. Existing repository
diagnostics use zero for a trustworthy answer, three for an expected negative
or stopped result, and two for operational failure.

#### BBQ for Q09

A traffic light should reuse colours drivers already know instead of inventing
a new signal for the next junction. In this picture: the colours are process
statuses 0, 3, and 2, and the next junction is `rvw_status`.

#### Options for Q09

- Option I1: Use `0` for trustworthy cardinality, `3` for results containing
  untrustworthy exchange evidence, and `2` for invocation or operational
  failure.
  - pro: Matches `commit-plan-check` and review-exchange command conventions.
  - con: Status `3` covers several diagnostic states distinguished in payload.
- Option I2: Allocate a distinct process status to each damaged state.
  - pro: Shell callers can branch without parsing JSON.
  - con: Exhausts a growing numeric contract and duplicates payload detail.
- Option I3: Always return zero when any payload was rendered.
  - pro: Keeps process handling simple.
  - con: Shell automation can miss an untrustworthy repository result.

#### Recommended option for Q09 (with arguments for this choice)

Option I1: Adopt the repository's existing three-way process contract and keep
specific states and diagnostics in the normalized result.

#### Answer to Q09: option I1 (with reason why it must be accepted as the answer)

Option I1: Accept this because it distinguishes a trustworthy answer, a
completed but unsafe answer, and inability to answer without inventing another
status convention.

### Q10: How should discovery detect files changing during a status read?

Question description: Status cannot take the mutating exchange transition lock,
yet a requestor or reviewer may publish while discovery reads several files.
The design must define the consistency boundary for that race.

#### BBQ for Q10

A photographer can compare the clock visible at the start and end of a shot to
know whether the scene changed, without asking everyone to freeze. In this
picture: the clock is the coordination file fingerprint, the scene is one
exchange's artifact set, and freezing everyone is the transition lock.

#### Options for Q10

- Option J1: Read and fingerprint the coordination record before observation,
  read it again afterward, and mark the entry changed-during-read if the two
  versions differ.
  - pro: Detects mixed snapshots without creating a lock or retrying forever.
  - con: Adds a second read for every candidate.
- Option J2: Accept a best-effort single pass with no consistency check.
  - pro: Minimizes filesystem reads.
  - con: May combine identity and artifacts from different transition moments.
- Option J3: Acquire the exchange transition lock while reading.
  - pro: Produces a stable per-exchange snapshot.
  - con: Lock acquisition changes protocol state on disk and violates the
    strict read-only boundary.

#### Recommended option for Q10 (with arguments for this choice)

Option J1: Use an optimistic per-entry fingerprint check and return an explicit
diagnostic when evidence changes during the observation window.

#### Answer to Q10: option J1 (with reason why it must be accepted as the answer)

Option J1: Accept this because it detects a mixed snapshot while preserving the
command's promise that status never creates a lock or mutates review state.
