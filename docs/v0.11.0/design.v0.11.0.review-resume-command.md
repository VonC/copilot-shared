# Design v0.11.0 -- Resume interrupted reviews from their durable LLM role

This design implements the behavior specified by
`feature-request.v0.11.0.review-resume-command.md`. It is a cross-cutting
revision of the review exchange: runtime artifacts gain a configurable home,
role ownership gains an LLM-nature trace, status gains a bounded migration
preflight, and an LLM-only resume skill continues the correct requestor or
reviewer workflow.

## Context for v0.11.0 review resumption

The durable exchange already records enough identity and state to diagnose an
interrupted review, but its runtime evidence is spread across project-root
files and it records only protocol roles, not the LLM host that acted in each
role. Existing exact-identity wait operations also cannot express a reviewer
waiting before any concrete request exists.

Resumption therefore cannot be a thin alias for one existing exchange command.
It must first normalize artifact placement, resolve and verify role identity,
and then dispatch to one of two deliberately different continuations:

- a reviewer is a persistent review-request consumer and either answers a
  concrete request or waits for any future specification or code request;
- a requestor owns one task workflow and either waits for its exact answer,
  performs its exact exchange action, or asks `pw skill` for the next task.

## Scope for v0.11.0 review resumption

### In scope for v0.11.0 review resumption

- one versioned repository declaration for the runtime artifact home;
- a shared artifact locator used by all review producers and consumers;
- a fast placement check and an all-or-none legacy migration;
- bounded migration from ordinary review-status collection;
- durable Claude, Codex, Gemini, or `unknown` evidence per protocol role;
- legacy identity inspection and current-role backfill;
- an LLM-only resume skill with thin host adapters;
- exact continuation for specification and code-review requestors and
  reviewers;
- identity-free, open-ended reviewer waiting for the next request;
- lease-independent human-invoked pickup with displaced-session rejection;
- schema, renderer, instruction, documentation, and regression-test updates
  required by these cross-cutting changes.

### Outside this design

- moving versioned `docs/.../review.*.md` transcripts away from their reviewed
  documents;
- reopening completed requirement, design, plan, validation, or umbrella
  status documents from earlier review-mode topics;
- a batch, shell, `rvw_resume`, or other non-LLM resume command;
- automatic ordering or processing of several simultaneously available
  requests;
- changing the authority of automated rounds or the human convergence gate;
- replacing a conflicting recorded LLM nature;
- a repository-wide identity rewrite unrelated to the selected occurrence.

## Confirmed technical facts for v0.11.0 review resumption

- `tools/review_exchange_paths.py` currently derives request, answer,
  coordination, tombstone, and transition-lock paths directly below the caller
  project root.
- Exchange activation currently submits all transient paths to one
  `git check-ignore -z --stdin` check and rejects uncovered paths.
- `tools/review_status.py` currently discovers root-level
  `a.review-active.*` coordination records and the status contract is described
  as strictly read-only.
- The typed status model currently has schema version 1 and distinguishes
  trustworthy, untrustworthy, and operational-failure outcomes.
- Request and answer envelopes and coordination records use strict schemas and
  do not currently carry LLM-nature evidence.
- Exact request and answer waits require a complete exchange identity and a
  bounded timeout.
- The existing host evidence recognizes Claude through `CLAUDECODE` and Codex
  through `CODEX_THREAD_ID`; falling back to Claude when neither is present is
  not reliable enough for identity evidence.
- Claude, Codex, and Gemini integrations are Markdown adapters over canonical
  shared instructions. Provider files must remain thin direct pointers.
- Current reviewer instructions stop at convergence and therefore do not yet
  implement the persistent-consumer behavior settled by the feature request.

## Target architecture for v0.11.0 review resumption

The feature is organized around five shared services and one orchestration
layer:

1. `ReviewArtifactConfiguration` loads and validates the versioned artifact-home
   declaration.
2. `ReviewArtifactLocator` maps every recognized runtime artifact identity to
   that home.
3. `ReviewArtifactMigration` checks placement, creates a safe home, and performs
   recoverable all-or-none migration.
4. `LlmNatureDetector` and `RoleNatureEvidence` detect, persist, reconcile, and
   backfill role-specific host identity.
5. Review status discovers through the locator and projects migration and role
   nature into schema version 2.
6. The canonical resume skill applies those services, resolves a role, and
   delegates to requestor or reviewer continuation.

All exchange commands, waiters, status readers, skills, and tests consume these
shared services. No caller reimplements path construction, artifact
classification, host detection, or role reconciliation.

## Versioned artifact-home declaration

The repository-root file `.review-artifacts.ini` is the sole durable setting
carrier. It is optional; its absence means the default home `.reviews`.

```ini
[review-artifacts]
home = .reviews
```

The parser accepts exactly one `[review-artifacts]` section and one `home`
property. The value is a non-empty repository-relative path. Resolution uses
the physical caller repository root, normalizes `.` and separators, resolves
links before boundary validation, and rejects:

- absolute, drive-relative, UNC, or environment-expanded values;
- a normalized path equal to or outside the repository root;
- the repository root itself;
- a path that names an existing tracked directory;
- an unreadable declaration, duplicate section or property, or unsupported
  property.

The declaration itself remains at the root and is intended to be versioned.
Environment variables, status arguments, resume arguments, and ignored
per-clone markers cannot replace its value. The resolved absolute path is an
internal value; machine output uses the repository-relative form so evidence is
portable between clones.

## Artifact registry and path resolution

`ReviewArtifactLocator` owns an explicit registry of protocol artifact kinds.
The registry covers request, answer, active coordination, lease and wait state,
transition lock, retained manifest, consumed tombstone, question-management
state, review guidance, review-mode runtime state, and any other runtime file
that a review workflow creates. Adding a new protocol artifact requires adding
its kind and name parser to this registry.

The registry is deliberately not a broad `a.*` or recursive glob. Migration
must never capture unrelated user files merely because their names resemble
temporary evidence. Each registered kind defines:

- its accepted legacy root name;
- its artifact-home name;
- whether it carries a full durable exchange identity;
- which role, if any, authored it;
- whether it can contain role-nature evidence;
- its collision and integrity checks.

All runtime artifact derivation goes through the locator. Transcripts continue
to derive from the reviewed document and remain in `docs`. The versioned
`.review-artifacts.ini` declaration is configuration, not a migrated runtime
artifact.

## Artifact-home ignore coverage

Before the home receives its first runtime artifact, creation writes a
home-local `.gitignore` containing a catch-all rule:

```gitignore
*
```

The rule covers the ignore file itself and every runtime descendant. Creation
then asks Git to verify effective ignore coverage for the ignore file and every
prospective artifact path. A newly created empty home is removed if writing or
validation fails.

An existing home is not silently repaired. Missing, malformed, or ineffective
coverage is a blocked layout with a diagnostic that names the home and failed
path. This preserves the existing activation invariant: artifacts are accepted
because Git ignores them, not because the new home receives an exception.

## Migration check and transactional migration

### Fast placement check

`migration_check` is a shared read-only operation. It loads the declaration,
then inspects only:

- recognized legacy artifacts directly below `PRJ_DIR`;
- the default `PRJ_DIR/.reviews` location;
- the configured home when it differs from the default.

It parses names and the minimum identity metadata needed to detect duplicate,
damaged, or ambiguous evidence. It does not build the full review-status model.
Its typed result is one of:

- `ready`: all recognized runtime artifacts are in the resolved home;
- `migration-required`: one or more recognized artifacts are in a legacy or
  superseded inspected location and the complete move is safe;
- `blocked`: configuration, ignore coverage, integrity, collision, or location
  ambiguity prevents a safe move.

The result includes the resolved home, inspected locations, source-to-target
map, and diagnostics. `ready` also distinguishes a pre-existing home from a
home that has not yet needed creation.

### All-or-none migration

Migration accepts only a fresh `migration-required` result. Under a
repository-scoped migration lock it repeats validation, creates and validates
the home when absent, and writes a migration journal inside that ignored home.
The journal records the complete source-to-target map, source fingerprints,
and phase before the first move.

Each move is an atomic same-volume rename where supported and is recorded in
the journal. Any ordinary failure triggers reverse-order rollback and restores
the original root layout. A later invocation that finds an incomplete journal
recovers before returning a placement result: it rolls back an uncommitted
migration or finishes cleanup after a committed one. The commit phase is
recorded only after every target exists with the expected fingerprint. Source
cleanup and journal removal follow that commit.

Thus callers observe either the complete source layout or the complete target
layout. A collision is detected before movement, never overwritten, and one
collision blocks the whole operation. The migration preserves bytes and file
timestamps where the platform permits; it does not rewrite legacy identity.

Resume always performs check, safe migration when required, and a second check
before status or role selection. Review status performs the same bounded
preflight automatically. A blocked result or a non-`ready` second result is an
operational failure and no exchange continuation follows.

## LLM-nature detection and durable evidence

### Detection contract

`LlmNatureDetector` returns `claude`, `codex`, `gemini`, or `unknown`, together
with a non-secret evidence source. Detection uses a trusted host hint supplied
by the installed provider entry point first, then known host-owned environment
signals. Contradictory known signals produce `unknown` with a conflict
diagnostic; absence of evidence also produces `unknown`. It never defaults to a
specific LLM.

The trusted hint is part of skill invocation context, not a user-selectable
resume argument and not durable repository configuration. Canonical logic
validates it against the supported enum. Claude and Codex retain their known
host signals, and the Gemini adapter supplies the `gemini` hint; environment
support can be extended when Gemini exposes a stable host-owned signal without
changing artifact schemas.

Only the enum value is persisted. Environment-variable names, values, session
IDs, and other host evidence are never written to review artifacts.

### Role-nature representation

New strict schemas carry a role map:

```json
{
  "role_natures": {
    "requestor": "codex",
    "reviewer": null
  }
}
```

A string is the nature detected when that role acted. `null` means the role has
not yet produced attributable evidence in that exchange occurrence. The
explicit value `unknown` means the role acted but reliable host detection was
unavailable. Absence of `role_natures` identifies a legacy schema.

Each request, answer, coordination transition, retained or consumed state, and
transcript entry preserves the two-role snapshot known at creation. The first
request records the requestor and leaves an unobserved reviewer as `null`; the
reviewer's claim and answer add the reviewer value; later requestor transitions
preserve both. Status reconciles all snapshots and reports both the effective
value and the contributing artifact paths.

Role authorship comes from artifact kind and durable transition semantics, not
from a mutable prose label. New writes cannot silently change an already known
non-`unknown` nature for a role.

## Legacy role evidence and backfill

After migration and role selection, resume enumerates every artifact in the
selected exchange occurrence that the registry attributes to the selected
role. It partitions them into missing, matching, and conflicting nature sets.
Counterpart-role artifacts are readable, but missing counterpart nature is
ignored and never backfilled by the current role.

For a known current nature:

1. the complete set is scanned before any mutation;
2. any conflicting non-missing value stops the attempt and presents all
   conflicts together;
3. `Stop` changes nothing;
4. attempt-scoped `Override` preserves every conflicting value, fills only
   missing selected-role values, and permits continuation;
5. with no conflict, all missing selected-role values are filled atomically
   before continuation.

For an `unknown` current nature, resume performs the same role selection but
does not backfill missing values. It also cannot prove that an existing known
selected-role value conflicts, so that value is preserved and continuation does
not require the discrepancy override. The explicit role or human role choice is
the authority for this attempt.

Mutable JSON artifacts receive the new field through a validated atomic
rewrite. Immutable transcript history is not edited in place; one append-only
identity-completion entry records the affected role, occurrence, current
nature, and artifact paths. Its heading is
`### LLM nature completion for <role> (exchange <occurrence>)`. The role and
occurrence qualifiers keep every completion heading unique within a transcript,
and the entry identifier makes a repeated completion attempt idempotent.
Request and answer content files that are part of the current runtime occurrence
are atomically rewritten only when their parsed schema supports a lossless
legacy upgrade. Failure of any prospective rewrite prevents all backfill;
temporary replacements are validated before a commit phase and rolled back on
failure.

## Status model and migration-aware reporting

Review status schema advances from version 1 to version 2. Its top-level result
adds:

```json
{
  "migration": {
    "state": "unnecessary | completed",
    "artifact_home": ".reviews",
    "moved_count": 0
  }
}
```

`unnecessary` means the preflight began ready. `completed` means status safely
migrated evidence and the required second check returned ready. A blocked check,
migration failure, or failed second check returns the existing
`operational-failure` outcome with typed migration diagnostics instead of a
normal schema-2 exchange list.

Each exchange projection adds `requestor_llm_nature` and
`reviewer_llm_nature`. A value can be one supported enum, `unrecorded` for
legacy or not-yet-observed evidence, or `conflicting` with an accompanying
evidence list. Human rendering labels both roles explicitly. Machine consumers
read typed fields and never infer identity from report prose.

After migration succeeds or is unnecessary, status discovery and projection
are read-only and enumerate coordination records only through the configured
home. The canonical status instruction and published skill description state
this bounded mutation exception.

## Resume skill orchestration

Resume is implemented as one canonical LLM skill and canonical instruction.
Claude, Codex, and Gemini adapters contain only the provider-required direct
pointer to that canonical content plus the trusted provider hint mechanism
allowed by the adapter format. No adapter copies workflow rules.

Invocation accepts an optional protocol role, `requestor` or `reviewer`; it does
not accept an artifact-home override or exchange identity guess. The canonical
sequence is:

1. resolve the caller repository;
2. detect the current LLM nature;
3. run migration check, migrate if required, and require a ready recheck;
4. collect typed status and locate resumable evidence;
5. resolve or confirm the protocol role;
6. inspect and, when allowed, backfill selected-role identity;
7. acquire a fresh ownership capability for a concrete exchange when one
   exists;
8. dispatch immediately to the role-specific continuation.

Malformed, repair-required, escalated, artifact-inconsistent, or ambiguous
status stops before dispatch and shows the typed evidence. The only normal
ambiguities delegated to the human are role selection, known role conflict,
and selection among several simultaneously available requests.

## Role resolution

Role resolution reconciles all role-nature evidence in the selected occurrence:

- one role matches the known current LLM: select it without confirmation;
- neither role has nature and no argument exists: ask `requestor` or `reviewer`;
- an explicit role with no trace supplies the choice without confirmation;
- both roles match and no argument exists: ask which role to continue;
- an explicit role conflicts with known trace: show the mismatch and require
  one confirmation for this attempt;
- an explicit role matches: select it, while still running the full artifact
  identity scan;
- current nature is `unknown`: use an explicit role or ask for one, without
  writing `unknown` into missing legacy identity.

Once this gate and any selected-role evidence gate pass, resume does not ask for
a second go-ahead before waiting or acting.

## Lease-independent pickup and displaced sessions

Every ordinary or resumed session acquires an ownership capability when it
claims its next actor-owned transition. `start`, `reclaim`, an exact wait that
wakes for its actor, and a global reviewer wait that selects a request perform a
locked compare-and-swap, increment a monotonic `ownership_generation`, and issue
a fresh random ownership token. Coordination stores only the token digest. The
secret is returned only to the claiming LLM session's machine result and is
never printed in human reports or recoverable from coordination.

Every mutating exchange command presents the generation and secret held by its
session. Under the transition lock, the core re-reads coordination, checks the
generation, and compares a digest of the presented secret with the stored
digest. A command never reads its token from coordination. Successful handoff
to a different expected actor requires that actor to claim a new capability;
the previous capability is invalidated by the new generation.

A human's direct resume invocation is an explicit recovery action, so it may
perform that claim even while the previous owner's lease is fresh. A displaced
session that rereads coordination learns the current generation but cannot
present its secret. Its next renewal, publication, consumption, or state
transition fails with a typed `ownership-superseded` result showing the durable
exchange identity and current generation. It cannot refresh its old lease or
overwrite resumed work.

Read-only polling does not require a capability, but a wake must claim or
validate one before acting. An ordinary session without the capability returned
by its claim, or with an invalid capability, cannot mutate and receives a typed
ownership failure. Repeating resume with the capability for an unchanged owned
generation is idempotent; a distinct later direct resume is another authorized
pickup and advances the generation.

A session holding no capability for a live exchange acquires one through a
direct resume pickup, which is authorized to claim while the previous lease is
fresh. Two ordinary situations reach that state: a later session that arrives
at the durable convergence gate without having run the wait that claims, and a
session whose secret is no longer available to it mid-round. `reclaim` does not
cover either, since it applies to a round abandoned through lease expiry.
Neither situation requires waiting for the lease to lapse.

## Reviewer continuation

Reviewer continuation is request-consumer-only:

- If exactly one valid request is available, resume claims or reclaims that
  request's complete identity and generation, runs the matching specification
  or code reviewer workflow, and publishes its exact answer.
- If no request is available, resume enters a global reviewer wait that watches
  only recognized request artifacts in the configured home.
- If several requests are available or arrive in one observation, it lists
  their family, document, step, round, occurrence, requestor nature, and age and
  asks the human to choose one.

When several reviewer waits race for one request, each tries the same locked
claim compare-and-swap. The first successful claim owns the request. Every loser
receives a typed `already-claimed` result, discards no evidence, and returns to
the global wait. Recorded reviewer nature does not reserve an unclaimed request;
it is identity evidence and a later discrepancy gate, not a scheduling lock.

The global wait is identity-free and has no exchange timeout before a request
exists. It uses the existing file-observation abstraction with a low-cost
directory change notification where supported and bounded polling fallback.
Each wake rescans and validates the complete candidate set, so events may be
coalesced without losing requests. It remains active until a request is selected
or the human cancels.

Idle, concluded, requestor-owned, and human-convergence-gate exchanges are all
valid entry states. A matching later round or occurrence and an entirely new
specification or code exchange wake the same wait. Unrelated artifacts do not.
After an intermediate answer, the reviewer returns to the global wait instead
of requiring an exact replacement-request wait. After convergence, it likewise
waits globally; it never performs the human or requestor action.

Reviewer resume never runs `pw skill`, writes a requirement or design,
implements code, publishes a request as requestor, or advances a requestor
workflow.

## Requestor continuation

Requestor continuation stays bound to the selected exchange until that exchange
hands control back to its owning workflow:

- `answer-pending` or an equivalent response-wait state starts or restarts the
  exact answer wait;
- a requestor-owned state claims or reclaims the complete exchange identity,
  consumes the answer, applies requested changes, publishes the next round, or
  presents the durable human convergence gate as directed by the existing
  requestor skill;
- when no review remains for the current task, it runs `pw skill` and
  immediately follows the returned writer, implementation, review-requestor,
  or other workflow handoff.

Requestor resume never waits for an arbitrary future request. If its current
workflow later needs a new review, it initiates that new exchange through the
normal requestor skill with the new exact identity.

## Failure and idempotency boundaries

- Configuration and placement failures stop before status collection.
- Migration and identity backfill validate their complete change sets before
  mutation and recover incomplete journaled work before retry.
- Ambiguous exchange identity is never resolved from filename ordering.
- Several requests require human selection; they are not treated as corrupt.
- A conflicting current-role nature requires `Override` or `Stop`; missing
  counterpart nature does not.
- `unknown` detection is supported but is not used to fill legacy evidence.
- A missing, stale, or invalid ownership capability cannot mutate an exchange,
  whether the actor entered through an ordinary workflow or direct resume.
- Repeating check, migration after completion, backfill after completion, wait,
  or resume against unchanged state has no additional durable effect.
- The convergence gate and all existing requestor/reviewer authority checks
  remain in force after pickup.

## Acceptance cases for v0.11.0 review resumption

1. With no declaration, all new runtime artifacts resolve below `.reviews` and
   transcripts remain beside reviewed documents.
2. A valid `.review-artifacts.ini` redirects every producer, consumer, waiter,
   status reader, migration path, and resume path to the same repository-local
   home.
3. External, root, tracked-directory, malformed, or contradictory home
   declarations fail before artifact access.
4. A new home receives effective local ignore coverage before its first
   artifact; an existing uncovered home blocks without silent repair.
5. The fast check distinguishes ready, migration-required, and blocked layouts
   by inspecting only root, default, and configured locations.
6. A complete legacy set migrates together, one collision moves nothing, and
   interrupted migration recovers to one complete layout.
7. Resume and ordinary status both perform check, migration, and ready recheck;
   status schema 2 reports unnecessary or completed migration and uses
   operational failure for a block.
8. New requestor and reviewer actions record the detected Claude, Codex,
   Gemini, or explicit `unknown` role nature without persisting host secrets.
9. Status renders and serializes both role natures and identifies unrecorded or
   conflicting evidence.
10. A known selected role with matching and missing legacy evidence fills every
    missing selected-role artifact in the occurrence before continuation.
11. One selected-role conflict prevents partial backfill and lists the full
    conflict set; Override preserves conflicts and Stop changes nothing.
12. Missing counterpart identity remains readable and unchanged, while an
    unknown current host can continue after role selection without backfill.
13. Resume infers one matching role, asks when legacy evidence cannot decide,
    and confirms only an explicit mismatch or two-role match.
14. Direct resume displaces a live lease by advancing ownership generation, and
    the old session receives `ownership-superseded` on its next mutation.
15. Ordinary requestor and reviewer sessions acquire a generation and token
    when they claim actor-owned work and can complete normal mutations through
    the same fence used by resumed sessions.
16. A session holding no capability picks up a live exchange through direct
    resume, advances the generation, and completes the mutation its role owns,
    including a human confirmation at the convergence gate.
17. A reviewer answers one available request or waits globally from idle,
    concluded, requestor-owned, and convergence-gate states.
18. The global wait wakes for a same-exchange replacement or any new
    specification or code request, ignores other artifacts, persists until
    request or cancellation, and asks when several requests coexist.
19. Two reviewer waits racing for one request produce one successful claim; a
    loser receives `already-claimed` and resumes its global wait.
20. A requestor waits for its exact answer, performs its owned exchange action,
    or follows `pw skill`; it never waits for arbitrary review requests.
21. After role and evidence gates pass, both continuations wait or act without
    another confirmation.
22. Existing exchange, status, requestor, reviewer, adapter, waiting,
    documentation, and regression suites use the shared locator and updated
    schemas and no longer assume root-level artifacts or a default Claude host.

## Design decisions for v0.11.0 review resumption

| Decision | Choice | Rationale |
| --- | --- | --- |
| Artifact-home carrier | Optional versioned root `.review-artifacts.ini`; default `.reviews`. | Every participant and clone derives one location without session state. |
| Configuration syntax | Strict INI section `[review-artifacts]` with repository-relative `home`. | It matches existing lightweight configuration practice while keeping validation narrow. |
| Artifact membership | Explicit shared registry of protocol runtime kinds. | It covers every known artifact without sweeping unrelated `a.*` files. |
| Ignore coverage | Home-local catch-all `.gitignore`, created and verified before use. | Coverage follows the configured home and preserves the existing Git safety invariant. |
| Migration discovery | Inspect root, default home, and configured home only. | It is fast, deterministic, and matches the settled requirement boundary. |
| Migration atomicity | Prevalidated map, repository lock, journal, reversible moves, and recovery. | Root files cannot be renamed as one directory, so journaled rollback provides the required all-or-none observable result. |
| Host detection | Trusted provider hint, then known host evidence, else `unknown`. | Gemini can identify itself without inventing an unstable environment variable, and no host is silently assumed. |
| Durable role trace | Two-role nature snapshot in strict schemas, with `null` for not yet observed. | Every transition preserves known identity while legacy absence remains distinguishable. |
| Legacy completion | Scan the whole selected role and occurrence before atomic missing-only backfill. | This prevents partial evidence repair and preserves conflicting history. |
| Status evolution | Schema version 2 with typed migration and role-nature fields. | Resume can consume structured evidence without scraping prose. |
| Resume surface | Canonical LLM skill plus thin Claude, Codex, and Gemini adapters. | Continuation requires a live LLM and shared rules must not diverge by host. |
| Ownership fence | Uniform actor claims with monotonic generation, a session-held token, and only its digest in coordination. | Ordinary and resumed workflows use one transition contract, while direct resume can supersede a fresh lease without exposing the replacement capability. |
| Reviewer wait | Identity-free, open-ended request-only watcher. | A reviewer remains available across rounds and exchanges even before the next identity exists. |
| Requestor continuation | Exact exchange action followed by `pw skill` when released. | A requestor progresses its own task and initiates, rather than consumes, future review requests. |

## Open questions for the v0.11.0 review-resume-command design

### Q01: How should protocol-owned artifact kinds be recognized?

Question description: Migration, placement checks, status, and global reviewer
waiting need the same exact definition of a review runtime artifact. The design
currently chooses an explicit shared registry, but a namespace rule or schema
inspection could reduce the maintenance needed when new artifact kinds appear.

#### BBQ for Q01

Think of migration as a removal crew deciding which labeled boxes belong to the
review office. A packing list is precise but must be maintained; a label-prefix
rule is convenient but can claim somebody else's box; opening every box to
inspect its contents is flexible but slow and unsafe for unknown formats. In
this picture: the packing list is the explicit artifact registry, the label is
the filename namespace, opening boxes is schema inspection, and the removal
crew is every migration, status, and wait consumer.

#### Options for Q01

- Option A: Use one explicit registry of artifact kinds, names, parsers,
  authorship, and migration rules.
  - pro: Every consumer shares a precise, testable boundary and unrelated files
    cannot be swept into migration.
  - con: Every new artifact kind must update the registry before it participates
    in placement, status, or waiting.
- Option B: Treat every file matching the review namespace as protocol-owned.
  - pro: New artifact kinds participate automatically with little maintenance.
  - con: A broad filename rule can move or wake on unrelated files and cannot
    supply kind-specific integrity or authorship rules.
- Option C: Discover candidates by opening files and recognizing their schemas.
  - pro: Recognition can survive filename evolution when structured content is
    self-describing.
  - con: It makes the fast check expensive and gives malformed or prose-based
    artifacts an ambiguous ownership boundary.

#### Recommended option for Q01 (with arguments for this choice)

Option A: Use the explicit registry. The feature's refusal to guess or overwrite
evidence requires a closed ownership boundary, and the maintenance cost is
appropriate because adding an artifact kind already requires protocol tests and
path derivation changes.

#### Answer to Q01: option A (with reason why it must be accepted as the answer)

Option A: Accept the explicit shared registry because it is the only option
that makes migration safety, role attribution, status discovery, and reviewer
wake filtering use the same deterministic definition without capturing user
files.

### Q02: What should migration do when valid artifacts occupy several inspected locations?

Question description: A repository can contain legacy root artifacts, a former
default `.reviews` home, and a newly configured home at the same time. The
requirement says to inspect all three and move all or none, but the design must
decide whether valid, non-colliding evidence can be merged into the configured
home or whether multiple populated locations are inherently ambiguous.

#### BBQ for Q02

Imagine three archive rooms whose folders must end in one chosen room. The
archivist can merge distinct catalog entries, refuse whenever more than one
room is occupied, or move only the oldest room and leave another archive behind.
In this picture: the rooms are the project root, default home, and configured
home; catalog entries are durable artifact identities; and the archivist is the
transactional migration service.

#### Options for Q02

- Option A: Merge every validated, identity-distinct source into the configured
  home and block only collisions, damage, or identity ambiguity.
  - pro: It restores one complete home automatically after a configuration
    change while honoring the all-or-none rule.
  - con: The validation and journal must cover several source directories in
    one transaction.
- Option B: Block whenever recognized artifacts exist in more than one
  inspected location.
  - pro: It is conservative and makes any split layout visible to the human.
  - con: It rejects safely mergeable repositories and forces manual movement
    outside the guarded migration tool.
- Option C: Move root artifacts only and leave a populated former default home
  untouched.
  - pro: It keeps the original legacy migration narrowly focused on project-root
    files.
  - con: Status and resume would still have divided evidence and could silently
    omit a valid occurrence.

#### Recommended option for Q02 (with arguments for this choice)

Option A: Merge all identity-distinct sources in one prevalidated transaction.
The configured home is meant to become the sole runtime location, and a
collision or ambiguous identity remains a hard block rather than an overwrite.

#### Answer to Q02: option A (with reason why it must be accepted as the answer)

Option A: Accept a multi-source transactional merge because it is the only
choice that both converges all inspected evidence into the configured home and
keeps automatic migration safe through complete collision and identity checks.
The same durable artifact identity appearing in two inspected locations with
different bytes is an ambiguity and blocks the whole migration.

### Q03: Where should the two role natures be stored?

Question description: Requests are initially authored before a reviewer is
known, while later answers and transitions know more. The design currently
copies the best-known requestor and reviewer nature snapshot into every strict
artifact schema, using `null` for a role that has not acted. Alternatives store
only the current actor or maintain a separate identity ledger.

#### BBQ for Q03

Consider a relay log where each checkpoint can copy the whole current team
roster, record only the runner who arrived, or refer to a separate roster book.
In this picture: checkpoints are requests, answers, and coordination
transitions; runners are requestor and reviewer LLMs; the roster snapshot is the
two-role map; and the roster book is a separate identity artifact.

#### Options for Q03

- Option A: Store a two-role snapshot in every identity-bearing artifact, with
  `null` for a role that has not acted.
  - pro: Each artifact is self-describing and later transitions preserve all
    known identity without another required file.
  - con: Readers must reconcile repeated snapshots and detect disagreement.
- Option B: Store only the nature of the role that authored each artifact and
  aggregate roles during status collection.
  - pro: Each record carries only directly attributable evidence and has a
    smaller schema.
  - con: No individual transition preserves both traces, and missing artifacts
    can erase the only evidence for one role.
- Option C: Store both roles in one dedicated occurrence identity ledger and
  reference it from other artifacts.
  - pro: Role identity has one canonical mutable location.
  - con: The ledger becomes a new mandatory artifact and single failure point,
    while requests and answers cease to be independently self-describing.

#### Recommended option for Q03 (with arguments for this choice)

Option A: Use repeated two-role snapshots. Strict reconciliation can expose
conflicts rather than hide them, while every durable transition retains the
identity known when it was written.

#### Answer to Q03: option A (with reason why it must be accepted as the answer)

Option A: Accept the two-role snapshot because it best satisfies the requirement
that requests, answers, coordination transitions, status, and continuation all
preserve role-specific identities, including the period before a reviewer acts.

### Q04: How should legacy identity completion affect append-only transcripts?

Question description: Resume must update all missing-nature artifacts attributed
to its selected role, but review transcripts are versioned, append-only history
beside the reviewed document. The design currently upgrades mutable runtime
artifacts and appends one transcript identity-completion entry instead of
rewriting prior transcript entries.

#### BBQ for Q04

Picture a bound ship's log whose older entries omitted the captain's name. The
clerk can add a signed correction on today's page, erase and rewrite every old
page, or declare the log outside the correction policy. In this picture: the
ship's log is the review transcript, the captain is the role's LLM nature, the
new correction entry is append-only completion evidence, and the clerk is
resume backfill.

#### Options for Q04

- Option A: Rewrite eligible runtime artifacts but append one validated
  identity-completion entry to the transcript.
  - pro: It covers the transcript while preserving historical bytes and an
    auditable correction trail.
  - con: Consumers must understand that transcript completion can be represented
    by a later entry rather than an inline field.
- Option B: Rewrite every old transcript entry in place with the detected
  nature.
  - pro: Each historical entry becomes locally complete and easy to read.
  - con: It mutates versioned history, creates large diffs, and obscures when
    identity was actually completed.
- Option C: Exclude transcripts from identity completion and update runtime
  artifacts only.
  - pro: It leaves versioned documentation entirely untouched.
  - con: The durable transcript remains incomplete even though the requirement
    covers all selected-role artifacts in the occurrence.

#### Recommended option for Q04 (with arguments for this choice)

Option A: Append completion evidence. It preserves the transcript's historical
record while making the completed role identity durable and attributable to the
resume action.

#### Answer to Q04: option A (with reason why it must be accepted as the answer)

Option A: Accept the split update strategy because mutable runtime evidence can
be upgraded directly while an append-only transcript correction satisfies
identity completion without rewriting prior review history. Append that entry as
`### LLM nature completion for <role> (exchange <occurrence>)`; the role and
occurrence qualifiers keep headings unique across both roles and every exchange
recorded in one transcript.

### Q05: How should a direct resume fence out a displaced live session?

Question description: The requirement authorizes lease-independent pickup and
explicitly leaves displaced-session rejection to design. The current design
combines a monotonic ownership generation with an unguessable per-owner token
that every later mutation must present.

#### BBQ for Q05

Imagine replacing the crew holding a control-room key while the old crew may
still be nearby. Changing only the shift number identifies who is newer;
changing only the key invalidates the old crew; changing both proves the current
shift and its holder. In this picture: the shift number is ownership generation,
the key is the ownership token, the old crew is the displaced LLM session, and
the control-room action is any exchange mutation.

#### Options for Q05

- Option A: Give every ordinary or resumed actor claim both a monotonic
  ownership generation and a fresh secret token; persist only the token digest.
  - pro: It detects stale state and proves possession by the current resumed
    session, even while the prior lease remains fresh.
  - con: Every mutating command and in-memory continuation must carry two fence
    values.
- Option B: Use a monotonic generation only and reject commands carrying an old
  value.
  - pro: It is simpler to serialize, report, and test.
  - con: Any process that can reread coordination can copy the current
    generation and is not distinguished from its owner.
- Option C: Replace the lease owner with a new random nonce and use that nonce as
  the only fence.
  - pro: It directly invalidates the old owner with one value.
  - con: Diagnostics and idempotency lose a monotonic ordering that explains
    which pickup superseded which session.

#### Recommended option for Q05 (with arguments for this choice)

Option A: Use generation plus token. The generation gives durable ordering and
typed stale-session evidence, while a session-held token whose digest alone is
stored ensures that rereading the record does not grant mutation authority.
Applying the same claim to ordinary and resumed sessions gives every mutating
command one uniform fence instead of introducing a pickup-only exception.

#### Answer to Q05: option A (with reason why it must be accepted as the answer)

Option A: Accept the two-part fence because direct resume must be able to revoke
a still-live owner mechanically, and generation plus possession provides both
clear diagnostics and strong transition authorization. Every acting session
acquires its capability through a locked claim; coordination stores only the
digest, and a command presents its in-memory secret rather than reading one from
the record.

### Q06: How should the identity-free reviewer wait observe future requests?

Question description: A reviewer may wait for an exchange that does not yet
exist, so it cannot use the exact-identity waiter. The design proposes directory
change notification where supported, with bounded polling as a portability and
lost-event fallback, followed by a complete validated rescan on every wake.

#### BBQ for Q06

Think of a receptionist waiting for any review envelope. A doorbell is fast but
may not exist in every building; checking the tray periodically works everywhere
but costs repeated visits; using both lets the bell prompt a check while regular
checks catch a missed ring. In this picture: the doorbell is an operating-system
directory notification, the tray check is bounded polling, envelopes are review
request artifacts, and the receptionist is the global reviewer wait.

#### Options for Q06

- Option A: Use directory notification when available plus bounded polling and
  a complete rescan after either signal.
  - pro: It responds quickly, remains portable, and tolerates coalesced or lost
    file events.
  - con: It has two observation mechanisms and therefore more concurrency tests.
- Option B: Use bounded polling only.
  - pro: It is simple, portable, and close to the existing exact wait behavior.
  - con: An open-ended global wait repeatedly scans even when the repository is
    quiet and introduces polling latency.
- Option C: Require native directory notification with no polling fallback.
  - pro: It avoids periodic work and normally wakes immediately.
  - con: Unsupported filesystems or lost/coalesced events can make a valid
    request invisible indefinitely.

#### Recommended option for Q06 (with arguments for this choice)

Option A: Combine notifications with bounded polling and always validate by
rescan. The wait is intentionally open-ended, so it needs both low idle cost and
a portable recovery path rather than treating file events as authoritative.

#### Answer to Q06: option A (with reason why it must be accepted as the answer)

Option A: Accept the hybrid observer because it delivers prompt wakeups without
making correctness depend on platform-specific event delivery; the artifact
rescan remains the sole source of truth.

### Q07: Which reviewer should win when several waits observe one request?

Question description: Several Claude, Codex, or Gemini reviewer sessions can be
parked globally when one new request appears. The design must decide whether the
first atomic claimant owns it, the requestor's recorded reviewer nature reserves
it, or the race itself requires human selection.

#### BBQ for Q07

Imagine several librarians waiting at different desks when one returned book
lands in the sorting tray. The first librarian can scan it and take ownership,
the patron's old preferred-librarian note can reserve it, or every librarian can
stop and call a supervisor. In this picture: librarians are parked reviewer
sessions, the returned book is one review request, scanning is the locked
ownership claim, the preference note is recorded reviewer nature, and the
supervisor is the human.

#### Options for Q07

- Option A: The first locked compare-and-swap claim wins; every loser receives
  typed `already-claimed` and returns to its global wait.
  - pro: It reuses the ownership fence, produces exactly one reviewer, and keeps
    losing sessions available for later requests.
  - con: Which reviewer wins depends on scheduling rather than a stable host
    preference.
- Option B: A request's recorded reviewer nature reserves it for a matching
  waiter, and non-matching waiters continue waiting.
  - pro: It favors continuity with a reviewer nature already present in the
    occurrence.
  - con: New requests have no reviewer yet, and a recorded nature may refer to a
    session that is no longer running, leaving work unclaimed.
- Option C: Every competing waiter stops and asks the human to choose the
  reviewer.
  - pro: The human controls which LLM handles a contested request.
  - con: It creates a human gate for a scheduling race and stops all otherwise
    available reviewers.

#### Recommended option for Q07 (with arguments for this choice)

Option A: Let the first atomic claim win and return losers to waiting. This is
the same coordination primitive already needed for ownership, keeps exactly one
answer producer, and leaves human selection for the settled case of one reviewer
facing several requests.

#### Answer to Q07: option A (with reason why it must be accepted as the answer)

Option A: Accept first-claim-wins because it resolves the race without inventing
a host-priority policy or a new human gate. The typed loser result and automatic
return to the global wait preserve both safety and reviewer availability.
