# Report active review status and responsible role

## User story for review status

As a human or agent returning to an interrupted review, I want one read-only
repository command to report every active review exchange, including whether
the continuing agent is the requestor or the reviewer and which umbrella owns
the work, so I can understand the durable workflow state without reconstructing
its identity from prompt memory or transient shell state.

## Review-mode revision for `rvw_status`

The review-mode umbrella adds a repository-root `rvw_status` command, a shared
read-only implementation, a concise human-readable report, and a stable
machine-readable result. The command diagnoses specification and
implementation-code exchanges from protocol-owned coordination records.

The focused child draft adds two explicit identity rules:

1. Status must say plainly whether the continuing agent is a `requestor` or a
   `reviewer`; a generic actor label by itself is insufficient.
2. Status must visibly identify the exact umbrella draft when one exists and
   must state that no umbrella exists otherwise.

## Current review-status behavior in v0.11.0

- No repository-root `rvw_status` command provides a complete account of live
  review exchanges.
- A caller returning after a shell, VPN, terminal, computer, or agent restart
  must reconstruct the exchange family, reviewed document, round, artifacts,
  and responsible role from durable files and prior context.
- Review summaries carry identity, including umbrella context, but there is no
  single read-only diagnostic result that exposes those facts across all live
  specification and code exchanges.
- Existing requestor and reviewer workflows own their actions; neither role is
  the proper owner of family-neutral status discovery.

## Gap to close for active review diagnosis

1. Add a repository-root `rvw_status` launcher that needs no exchange-specific
   arguments.
2. Discover every live specification and implementation-code exchange from
   protocol-owned coordination records.
3. Return the complete durable identity and current state for each exchange.
4. Make the continuing role explicit as `requestor` or `reviewer` in both
   human-readable and machine-readable results.
5. Make the umbrella relationship a labelled first-class fact, using the exact
   repository-relative umbrella path when present and an explicit absence when
   not present.
6. Distinguish zero, one, and multiple live exchanges without silently choosing
   one.
7. Remain strictly read-only so diagnosis cannot alter or resume the workflow.

## Required `rvw_status` command contract

The command must inspect the repository containing the caller's working
directory by default, without changing to the launcher's installed location.
It may accept an explicit repository-root override for controlled callers and
tests. The repository-root launcher and shared entry point must report the same
repository when invoked from the same working directory, without requiring the
caller to remember or supply any of these exchange values:

- review family;
- reviewed document or slug;
- requestor or reviewer identity;
- implementation step;
- round or exchange occurrence; or
- request, answer, transcript, lease, or coordination-artifact path.

For every discovered exchange, the result must report:

- whether a review is active and its current protocol state;
- whether the family is specification or implementation-code review;
- the continuing role, explicitly labelled `requestor` or `reviewer` and
  derived from the protocol's `expected_next_actor`;
- the exchange `owner` as a separate responsibility from the continuing role;
- the more specific context when applicable, such as specification requestor,
  specification reviewer, code requestor, or code reviewer;
- the exact reviewed specification or implementation plan;
- the exact umbrella draft when one exists, otherwise an explicit `none`;
- the implementation step for code review when applicable;
- the current round and exchange occurrence;
- the protocol's canonical artifact paths:
  - request, answer, transcript, durable coordination, tombstone, and
    transition lock; and
  - for each path, its expected, present, missing, or not-applicable status;
- the durable `lease_renewed_at` timestamp and a derived freshness indication
  against the configured wait timeout; and
- the next protocol action owned by the reported role.

The continuing role describes who must perform the next protocol action, not
merely which side owns the exchange or last wrote an artifact. A healthy
record may therefore have different `owner` and `expected_next_actor` values.
Human-readable wording and structured identity must agree.

## Umbrella visibility rules

The human-readable report must display umbrella context as a clearly labelled
field. When an exchange belongs to the review-mode umbrella, it reports:

`docs/v0.11.0/draft.v0.11.0.review-mode.md`

The machine-readable result must expose the same repository-relative path as a
stable structured value. For a standalone effort, the human report states
`Umbrella: none`, and the structured result represents the same absence without
inventing a path.

The umbrella, reviewed document, family, continuing role, state, round, and
exchange occurrence must agree with the protocol's machine-readable exchange
identity. Genuine corruption, such as a state and artifact set that cannot both
be true or an identity that disagrees with its own envelope, is reported as an
inconsistent or repair-needed state rather than guessed. Different healthy
`owner` and `expected_next_actor` values are not conflicting evidence.

## Multiplicity and diagnostic outcomes

`rvw_status` must distinguish:

1. no active review exchange;
2. exactly one active exchange, with its complete identity and next action;
3. multiple active exchanges, with each identity reported independently and no
   implicit selection; and
4. malformed, inconsistent, repair-required, or escalated coordination state,
   with enough evidence to explain why no role or next action can be selected
   safely.

Every implemented nonterminal state is active: `round-in-progress`,
`request-pending`, `answer-publication-in-progress`,
`transcript-repair-pending`, `answer-pending`, `convergence-gate`,
`owning-action-pending`, `escalated`, `abandoned-mid-round`,
`interrupted-answer-publication`, `interrupted-transcript-append`,
`abandoned-request`, `abandoned-answer`, and `inconsistent`. Only `idle` is
inactive. Reporting `owning-action-pending` explicitly lets a later requestor
finish an already-authorized owning action without repeating the human gate.

The machine-readable result must remain stable enough for the later
`rvw_resume` command to consume without parsing human prose.

## Read-only guarantees for `rvw_status`

Running status must not:

- create, overwrite, append, or delete request, answer, or transcript files;
- renew, reclaim, or otherwise change leases or coordination records;
- change Git refs, the index, or the working tree;
- create or delete review-mode markers; or
- start, resume, or complete requestor or reviewer work.

Repeated status calls over unchanged durable state must report the same
exchange identity and must leave that state unchanged. The command must work
after process or machine restarts without relying on the earlier prompt.

## Acceptance criteria for review status

1. A repository-root `rvw_status` command and shared implementation are
   available for specification and implementation-code reviews, resolve the
   caller repository by default, accept an explicit root override, and agree
   when invoked from the same working directory.
2. The command discovers live exchanges without requiring identity arguments
   or resolving the repository from the launcher's installed location.
3. Every active exchange explicitly reports the continuing agent as either a
   `requestor` or a `reviewer` in human-readable output.
4. The structured result carries the same unambiguous continuing-role identity.
5. An exchange with an umbrella visibly reports the exact umbrella draft path
   in both output forms.
6. An exchange without an umbrella explicitly reports that absence.
7. The result includes state, family, reviewed document, applicable step,
   round, occurrence, protocol-canonical artifact paths and their presence,
   separate owner and expected next actor, lease timestamp and derived
   freshness, and next protocol action.
8. Zero, one, and multiple exchanges are distinguished without guessing or
   silently selecting an exchange.
9. Every implemented nonterminal state is active, including
   `convergence-gate`, `owning-action-pending`, escalated, abandoned,
   interrupted, repair-pending, and inconsistent outcomes, while `idle` is
   inactive.
10. The structured result can be consumed by the later `rvw_resume` effort
   without scraping display text.
11. Status remains strictly read-only across review artifacts, coordination
    state, markers, Git state, and workflow actions.
12. Status derives its answer from durable repository evidence, reports lease
    freshness against the configured wait timeout, and works after the caller's
    prior shell or agent context has been lost.

## Scope boundaries and dependencies

This feature owns status discovery and reporting only. It does not implement
`rvw_resume`, renew or reclaim a lease, choose among multiple exchanges, or run
requestor or reviewer actions. Those continuation behaviors belong to the
separate `review-resume-command` umbrella item.

The feature depends on the settled review exchange core and the specification
and code requestor/reviewer roles whose durable coordination records it reads.

## Open questions for the v0.11.0 feature request

### Q01: Which role identity must every healthy status record expose?

Question description: The requirement says the status must make clear whether
the continuing agent is a requestor or reviewer and may also report a more
specific role. It must settle whether the broad role is itself a stable field
or may be derived from a four-way specialization or display text.

#### BBQ for Q01

A venue badge should say plainly whether someone is staff or a guest before it
adds their department. Making everyone decode a department name to learn which
side of the desk they belong on defeats the point of the badge. In this picture:
the staff-or-guest label is `requestor` or `reviewer`, the department is the
specification/code specialization, and the badge is one status record.

#### Options for Q01

- Option A1: Require a stable broad `requestor` or `reviewer` role and also
  report the specification/code specialization.
  - pro: Directly satisfies the user's requirement in both output forms.
  - pro: Lets general consumers branch on two roles while specialized consumers
    retain the four-way context.
  - con: Carries two related identity values that must remain consistent.
- Option A2: Report only one of four specialized roles and let consumers derive
  requestor versus reviewer.
  - pro: Stores one role value and avoids duplicate fields.
  - con: Makes every caller repeat the broad-role mapping.
  - con: Does not state requestor or reviewer as directly as requested.
- Option A3: Put requestor or reviewer only in human-readable prose.
  - pro: Keeps the structured result smaller.
  - con: Prevents `rvw_resume` and other tools from consuming the role without
    parsing display text.

#### Recommended option for Q01 (with arguments for this choice)

Option A1: Treat the broad role as mandatory identity and the specialization as
additional context. The small consistency cost is justified because humans and
automation both need the same direct answer to “who am I in this exchange?”

#### Answer to Q01: option A1 (with reason why it must be accepted as the answer)

Option A1: Accept this because it preserves the explicit requestor/reviewer
contract while retaining enough family context for precise diagnosis and later
resume routing.

### Q02: Which role owns an exchange at the convergence gate?

Question description: At convergence, the protocol enters `convergence-gate`,
the implemented state for the umbrella's human-confirmation concept. The reviewer has made an advisory recommendation,
the requestor presents the decision, and the human supplies authority. Status
must identify one continuing agent role without implying that the agent owns
the human decision.

#### BBQ for Q02

A waiter can be responsible for a table while the diner is still choosing. The
waiter owns the next service step, but does not choose the meal for the diner.
In this picture: the waiter is the requestor, the diner is the human approver,
and choosing the meal is the consolidation or commit decision.

#### Options for Q02

- Option B1: Report `requestor` as the continuing role and separately state that
  the next action is human confirmation.
  - pro: Matches the existing convergence workflow where the requestor retains
    and presents the evidence.
  - pro: Preserves a requestor/reviewer answer without assigning human authority
    to an agent.
  - con: Requires readers to distinguish role ownership from action authority.
- Option B2: Report a third role named `human`.
  - pro: Makes the immediate decision maker explicit.
  - con: Breaks the requirement that the continuing agent role be requestor or
    reviewer.
  - con: Gives `rvw_resume` no agent role to resume after the human responds.
- Option B3: Report both requestor and reviewer until the human decides.
  - pro: Shows that both roles contributed to convergence.
  - con: Fails to identify one current owner and makes continuation ambiguous.

#### Recommended option for Q02 (with arguments for this choice)

Option B1: Keep the requestor as the current agent role and make the human gate
an independent state and next-action fact. This follows the settled protocol
and avoids inventing a third agent role.

#### Answer to Q02: option B1 (with reason why it must be accepted as the answer)

Option B1: Accept this because the requestor owns presenting and consuming the
human decision, while the status still states plainly that only the human can
authorize consolidation or commit.

### Q03: What should role status say when durable evidence conflicts?

Question description: Healthy exchanges must always state requestor or reviewer.
Their `owner` and `expected_next_actor` normally differ because they describe
different responsibilities; that is not a conflict. Genuinely malformed or
inconsistent evidence may instead describe a state and artifact set that cannot
both be true, or an identity that disagrees with its own envelope. The
requirement forbids guessing, so it must define the visible exception to the
normal role rule.

#### BBQ for Q03

Two road signs pointing in opposite directions should trigger a warning, not a
coin toss. A driver still needs to see both signs and why the route cannot be
chosen. In this picture: the road signs are conflicting coordination records,
the route is the requestor/reviewer role, and the warning is an inconsistent
status result.

#### Options for Q03

- Option C1: Report role as `unknown` for that exchange, list the conflicting
  evidence, and mark the state inconsistent or repair-required.
  - pro: Makes uncertainty explicit without hiding the relevant records.
  - pro: Prevents a later command from acting as the wrong role.
  - con: Introduces one diagnostic role value outside requestor and reviewer.
- Option C2: Prefer the newest coordination record and still report requestor
  or reviewer.
  - pro: Always produces one of the normal role values.
  - con: Silently guesses that recency establishes authority.
- Option C3: Omit the conflicting exchange from status output.
  - pro: Keeps the remaining output internally consistent.
  - con: Hides the exchange most in need of diagnosis.

#### Recommended option for Q03 (with arguments for this choice)

Option C1: Allow `unknown` only as an explicit error result with the conflicting
evidence attached. Healthy and resumable exchanges still always identify the
agent as requestor or reviewer, while corrupt state cannot trigger a guessed
continuation.

#### Answer to Q03: option C1 (with reason why it must be accepted as the answer)

Option C1: Accept this because the no-guessing rule is more important than
forcing a false role label, and because visible evidence gives the human a
repair path. A healthy difference between `owner` and `expected_next_actor`
does not trigger this exception.

### Q04: Which durable states count as active review exchanges?

Question description: The command reports active reviews, but the requirement
does not yet define whether active means only immediately resumable dialogue or
every implemented nonterminal exchange, including `convergence-gate`,
`owning-action-pending`, escalated, abandoned, interrupted, and inconsistent
states.

#### BBQ for Q04

A departures board should show delayed and gate-closed flights as well as those
currently boarding; otherwise the journeys needing attention disappear. It
does not need to show yesterday's completed flights. In this picture: flights
are review exchanges, delayed or gate-closed entries are nonterminal blocked
states, and yesterday's flights are completed exchanges.

#### Options for Q04

- Option D1: Treat every nonterminal durable exchange as active: `round-in-progress`,
  `request-pending`, `answer-publication-in-progress`,
  `transcript-repair-pending`, `answer-pending`, `convergence-gate`,
  `owning-action-pending`, `escalated`, `abandoned-mid-round`,
  `interrupted-answer-publication`, `interrupted-transcript-append`,
  `abandoned-request`, `abandoned-answer`, and `inconsistent`. Only `idle` is
  inactive.
  - pro: Gives a complete account of unfinished review work.
  - pro: Makes blocked exchanges discoverable instead of silently dropping them.
  - con: Some active entries are diagnostic rather than immediately resumable.
- Option D2: Treat only exchanges with an immediately runnable requestor or
  reviewer action as active.
  - pro: Every listed exchange can be acted on at once.
  - con: Hides human gates, escalation, and repair work.
- Option D3: Include both nonterminal and recently completed exchanges.
  - pro: Adds recent history for orientation.
  - con: Blurs status with audit history and requires an arbitrary retention
    boundary.

#### Recommended option for Q04 (with arguments for this choice)

Option D1: Define active as durable and nonterminal, then report the exact
implemented state, including `owning-action-pending` so a returning requestor
can finish already-authorized work without repeating the human gate. Completed
history remains in transcripts and outside the live-status result.

#### Answer to Q04: option D1 (with reason why it must be accepted as the answer)

Option D1: Accept this because interruption diagnosis must not hide unfinished
work merely because its next step is blocked or belongs to a human.

### Q05: How should status handle an absent umbrella value in older evidence?

Question description: New exchanges carry explicit umbrella identity or none,
but older durable records may omit the field while the reviewed child document
names an umbrella. The requirement must decide whether status may infer that
relationship or must expose missing protocol evidence.

#### BBQ for Q05

A parcel missing its destination label should not be routed by guessing from the
sender's neighbourhood. The address can help explain the problem, but it is not
a replacement shipping label. In this picture: the parcel label is durable
exchange identity, the neighbourhood is the reviewed document's metadata, and
routing is reporting an authoritative umbrella.

#### Options for Q05

- Option E1: Require umbrella-or-none in durable exchange identity; report
  missing legacy identity as repair-required and may show document metadata only
  as non-authoritative evidence.
  - pro: Keeps the status and resume contract based on protocol-owned identity.
  - pro: Prevents a document edit from silently changing exchange identity.
  - con: Older exchanges may need repair before they are resumable.
- Option E2: Infer the umbrella from the reviewed document whenever the durable
  record omits it.
  - pro: Produces a useful umbrella for more legacy exchanges.
  - con: Turns document discovery into an undocumented identity authority.
- Option E3: Report `Umbrella: none` whenever the field is absent.
  - pro: Keeps output simple and avoids inference.
  - con: Falsely describes missing evidence as a confirmed standalone effort.

#### Recommended option for Q05 (with arguments for this choice)

Option E1: Keep durable exchange identity authoritative and distinguish missing
from confirmed none. Showing document metadata as a repair hint is useful, but
it must not be promoted silently into identity.

#### Answer to Q05: option E1 (with reason why it must be accepted as the answer)

Option E1: Accept this because umbrella visibility must be trustworthy, and a
repair-needed result is safer than either guessed association or false absence.

### Q06: Which artifact paths should a status record report?

Question description: The requirement asks for applicable request, answer,
transcript, and coordination paths. It must clarify whether a path is reported
only when a file exists or whether expected-but-missing artifacts are also part
of diagnosis.

#### BBQ for Q06

A checklist is most useful when it shows both boxes that are filled and boxes
that should be filled but are empty. Listing only the papers already on a desk
cannot explain why work stopped. In this picture: checklist boxes are expected
artifact paths, papers are existing files, and the empty box is a missing
protocol artifact.

#### Options for Q06

- Option F1: Report every state-applicable path together with its expected,
  present, missing, or not-applicable status.
  - pro: Diagnoses missing artifacts without losing the canonical path.
  - pro: Gives machine consumers an explicit completeness model.
  - con: Produces more fields than a list of existing files.
- Option F2: Report only artifact paths that currently exist.
  - pro: Every returned path can be opened immediately.
  - con: Cannot distinguish a legitimately inapplicable artifact from a missing
    required one.
- Option F3: Report only the paths expected for the current state.
  - pro: Describes the protocol shape concisely.
  - con: Does not say whether each file actually exists.

#### Recommended option for Q06 (with arguments for this choice)

Option F1: Pair canonical paths with their observed presence. This supports both
normal orientation and malformed-state diagnosis without requiring a second
filesystem reconstruction by every caller.

#### Answer to Q06: option F1 (with reason why it must be accepted as the answer)

Option F1: Accept this because status should explain both what the protocol
expects and what durable evidence is actually present. It reports the
protocol's own canonical artifact paths rather than reconstructing nearby
artifact names.

### Q07: Should one damaged exchange suppress healthy exchanges?

Question description: A repository may contain several live exchanges. One may
be malformed while others are intact. The requirement must decide whether
status returns partial per-exchange results or fails the entire report.

#### BBQ for Q07

One broken platform display should not blank every other platform, but the
station board must still flag the broken display prominently. In this picture:
platforms are independent review exchanges, the broken display is malformed
coordination evidence, and the station board is the repository-wide status
result.

#### Options for Q07

- Option G1: Return every discoverable exchange independently, preserving
  healthy results and attaching diagnostics to damaged entries; mark the
  repository-wide result as having errors.
  - pro: Keeps valid review status available without hiding defects.
  - pro: Supports repair of one exchange while another continues.
  - con: Callers must inspect both per-entry and overall status.
- Option G2: Fail the complete report when any exchange is damaged.
  - pro: Gives callers one simple all-or-nothing validity rule.
  - con: Makes one unrelated defect block diagnosis of every healthy exchange.
- Option G3: Return only healthy exchanges and summarize the number of skipped
  damaged entries.
  - pro: Keeps the main result easy to consume.
  - con: Hides the evidence needed to repair the skipped exchanges.

#### Recommended option for Q07 (with arguments for this choice)

Option G1: Use per-exchange results plus an overall error indication. Review
exchanges are independent durable units, and complete diagnosis requires both
the intact identities and the damaged evidence.

#### Answer to Q07: option G1 (with reason why it must be accepted as the answer)

Option G1: Accept this because a status command should reveal all repository
state it can establish while refusing to describe damaged entries as healthy.

### Q08: Which outcomes should count as a successful status query?

Question description: Zero, one, and multiple well-formed active exchanges are
all expected repository states, while malformed evidence and operational read
failures are not. Automation needs a stable distinction between an expected
answer and an untrustworthy one.

#### BBQ for Q08

A headcount can succeed with zero, one, or ten people in a room; it fails when
the door is locked and nobody can count. In this picture: the people are active
exchanges, the count is a well-formed status result, and the locked door is an
operational or evidence-integrity failure.

#### Options for Q08

- Option H1: Treat zero, one, and multiple well-formed exchanges as successful
  queries; return a non-success outcome when any result is operationally
  unreadable, malformed, inconsistent, or repair-required.
  - pro: Separates normal cardinality from inability to trust the answer.
  - pro: Lets scripts handle multiple exchanges without treating them as a tool
    malfunction.
  - con: A partial result with one damaged exchange is non-success even though
    healthy entries remain useful.
- Option H2: Treat only exactly one healthy exchange as successful.
  - pro: Direct callers can proceed only when selection is unambiguous.
  - con: Confuses status discovery with resume selection and treats no work as
    an error.
- Option H3: Treat every completed invocation as successful and encode all
  problems only in the payload.
  - pro: Callers always receive the fullest possible report.
  - con: Shell automation can easily overlook an untrustworthy result.

#### Recommended option for Q08 (with arguments for this choice)

Option H1: Define success by trustworthiness rather than cardinality. Preserve
partial payloads on non-success so damaged repositories still provide repair
evidence.

#### Answer to Q08: option H1 (with reason why it must be accepted as the answer)

Option H1: Accept this because status must distinguish “there are several” from
“the command cannot establish the truth,” while retaining useful diagnostics in
both cases.

### Q09: What must the reported next protocol action contain?

Question description: The requirement asks for the next protocol action and
expects `rvw_resume` to consume status without scraping prose. It must clarify
whether that action is only a human hint, only a machine identity, or both.

#### BBQ for Q09

A train board can show both a platform code for the signalling system and a
plain instruction for passengers. Keeping only one makes either the machines or
the people guess. In this picture: the platform code is a stable action
identity, the passenger instruction is the human-readable next step, and the
train board is one exchange status record.

#### Options for Q09

- Option I1: Report a stable machine-readable action identity plus a concise
  human-readable description or command derived from that same identity.
  - pro: Supports `rvw_resume` and human diagnosis from one consistent fact.
  - pro: Avoids making automation parse prose or humans decode internal values.
  - con: The two representations need consistency checks.
- Option I2: Report only a human-readable next-step command.
  - pro: A user can act on the result directly.
  - con: `rvw_resume` would have to parse presentation text.
- Option I3: Report only a stable machine action identifier.
  - pro: Keeps the structured contract small and precise.
  - con: Human output no longer explains plainly what should happen next.

#### Recommended option for Q09 (with arguments for this choice)

Option I1: Make one stable action identity authoritative and render the human
instruction from it. This serves both audiences and keeps the later resume
feature independent of display wording.

#### Answer to Q09: option I1 (with reason why it must be accepted as the answer)

Option I1: Accept this because the status command is explicitly both a human
diagnostic and a machine-readable input to `rvw_resume`, and neither audience
should have to reconstruct the other's representation.

### Q10: Which durable field determines the continuing agent role?

Question description: Coordination records distinguish the exchange owner from
the actor expected to perform the next protocol action. Status must decide which
field answers whether the continuing agent is the requestor or reviewer.

#### BBQ for Q10

A parcel label can name both the sender who owns the shipment and the courier
who must move it next. The next courier is the useful answer when deciding who
should continue, while the sender remains useful context. In this picture: the
sender is `owner`, the courier is `expected_next_actor`, and the parcel is the
review exchange.

#### Options for Q10

- Option J1: Derive the continuing role from `expected_next_actor` and report
  `owner` separately.
  - pro: Identifies the agent who must perform the next protocol action.
  - pro: Preserves ownership without conflating it with turn-taking.
  - con: Adds two related role fields that readers must distinguish.
- Option J2: Derive the continuing role from `owner`.
  - pro: Uses the exchange's durable owner as the single role identity.
  - con: Can name the requestor while the reviewer is expected to act next.
- Option J3: Report both fields without designating a continuing role.
  - pro: Exposes all evidence without preferring one interpretation.
  - con: Fails the requirement to say plainly who must continue.

#### Recommended option for Q10 (with arguments for this choice)

Option J1: Make `expected_next_actor` authoritative for the continuing role and
show `owner` as a separate responsibility. This matches the protocol's explicit
next-actor field and keeps status useful for resumption.

#### Answer to Q10: option J1 (with reason why it must be accepted as the answer)

Option J1: Accept this because a healthy request-pending exchange may be owned
by the requestor while requiring the reviewer to act next; reporting the owner
as the continuing role would direct the wrong agent.

### Q11: Must status report lease freshness?

Question description: Every nonterminal exchange is active, including exchanges
whose lease expired long ago. The result must decide whether and how it exposes
the distinction between a live exchange and an abandoned-looking one.

#### BBQ for Q11

Two parked cars may look alike, but a warm engine tells which one was used
recently. The timestamp is the engine reading and the freshness indication is
the quick interpretation. In this picture: the cars are nonterminal exchanges
and the configured wait timeout defines how long the engine counts as warm.

#### Options for Q11

- Option K1: Report the durable `lease_renewed_at` timestamp and a derived
  freshness indication against the configured wait timeout.
  - pro: Distinguishes a live exchange from a long-abandoned nonterminal one.
  - pro: Supplies the fact `rvw_resume` needs when choosing renewal or reclaim.
  - con: The derived indication depends on a configured timeout that may change.
- Option K2: Report only the raw `lease_renewed_at` timestamp.
  - pro: Exposes durable evidence without interpretation.
  - con: Makes every caller reimplement the freshness comparison.
- Option K3: Report no lease information.
  - pro: Keeps the result focused on identity and next action.
  - con: Makes an old abandoned-looking exchange indistinguishable from a live one.

#### Recommended option for Q11 (with arguments for this choice)

Option K1: Report both the durable timestamp and a derived freshness indication.
The raw evidence remains auditable, while callers receive the protocol-relevant
interpretation needed for safe continuation.

#### Answer to Q11: option K1 (with reason why it must be accepted as the answer)

Option K1: Accept this because the state alone says only that a lease has
expired, while the timestamp and derived freshness say by how much, which is
what separates a momentary interruption from long-abandoned work.

### Q12: How does `rvw_status` resolve the repository it inspects?

Question description: The command discovers exchanges from repository-root
coordination records. It must decide how that root is resolved.

#### BBQ for Q12

A building directory should describe the building where the visitor is
standing, not the factory that printed the directory. In this picture: the
visitor's building is the caller repository, the factory is the tool's install
location, and the directory is `rvw_status`.

#### Options for Q12

- Option L1: Discover the root from the caller's working directory by default,
  accept an explicit override, and require both entry points to report the same
  repository from the same working directory.
  - pro: Reports the repository the caller is actually standing in.
  - pro: Makes launcher and shared-entry-point parity testable.
  - con: Requires the launcher to preserve the caller's working directory.
- Option L2: Always resolve the root from the command's installed location.
  - pro: Behaves identically no matter where it is invoked.
  - con: Can report the tooling repository instead of the caller's repository.
- Option L3: Require an explicit repository argument.
  - pro: Removes ambiguity about which repository is meant.
  - con: Contradicts the no-remembered-arguments command contract.

#### Recommended option for Q12 (with arguments for this choice)

Option L1: Treat the caller's working directory as the default context, retain
an explicit override for controlled callers and tests, and verify both entry
points against the same repository.

#### Answer to Q12: option L1 (with reason why it must be accepted as the answer)

Option L1: Accept this because the status command must diagnose the repository
the caller is working in, while an override and entry-point parity check make
that behavior explicit and testable.
