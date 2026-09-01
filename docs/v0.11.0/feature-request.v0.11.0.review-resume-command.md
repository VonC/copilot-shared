# Resume interrupted reviews from their durable LLM role

## CDC revision that introduces review resumption

The earlier review-mode CDC defines durable specification and implementation
exchanges, requestor and reviewer roles, restart-safe coordination evidence,
and a read-only review-status command. It does not provide one LLM-native entry
point that can recover the current role and continue its work after an
interruption.

The revised CDC assigns the final `review-resume-command` umbrella item a
cross-cutting update. Runtime review artifacts move below a configurable
repository-local directory, exchanges trace the LLM nature acting in each
role, review status can migrate legacy evidence before observing it, and a
resume skill continues as requestor or reviewer from durable state.

## User story for review resumption

As a Claude, Codex, or Gemini session returning to a repository, I want one
resume skill to locate or migrate review evidence, determine which role I am
continuing, validate or complete that role's LLM trace, and immediately wait or
act according to the protocol, so I do not have to reconstruct an interrupted
exchange or manually choose its next workflow command.

## Current behavior in v0.11.0

- Protocol-owned runtime review artifacts are written directly below
  `PRJ_DIR`; there is no shared configurable artifact-home resolver with a
  `<PRJ_DIR>/.reviews` default.
- Existing review artifacts can remain at the repository root, and there is no
  fast migration preflight that distinguishes an already-correct layout from a
  safe migration or a blocking collision.
- Review status is strictly observational and cannot move legacy artifacts
  before collecting status.
- Exchanges record protocol roles but do not consistently record whether
  Claude, Codex, or Gemini acted as requestor or reviewer.
- Legacy artifacts without LLM nature and newer identity-bearing artifacts do
  not share one compatibility and backfill policy.
- There is no LLM-only resume skill that can select a role, wait, reclaim, act,
  or hand a requestor back to `pw skill`.

## Gap to close for configurable review evidence

1. Resolve every protocol-owned runtime review artifact through one
   configurable repository-local directory whose default is
   `<PRJ_DIR>/.reviews`.
2. Provide a migration tool that moves every recognized legacy review artifact
   stored directly in `PRJ_DIR` into the resolved directory.
3. Cover request, answer, coordination, lease, lock, tombstone, consumption,
   and every other artifact recognized by the shared exchange protocol.
4. Preserve durable identity during migration and refuse a collision, damaged
   layout, or ambiguous destination instead of overwriting evidence.
5. Update the shared exchange, requestor, reviewer, status, documentation, and
   test behavior delivered by completed umbrella items without reopening their
   completed documents or status rows.

## Required migration preflight

A fast `migration_check` tool must report one of these settled outcomes before
resume or migration-capable status collection continues:

- all recognized traces and artifacts are already under the configured or
  default artifact home;
- recognized legacy root artifacts require migration;
- a collision, damaged layout, or ambiguity prevents a safe migration
  decision.

The check must not perform the full review-status projection merely to decide
artifact placement.

Every resume invocation must run `migration_check` before it reads status or
selects a role. When migration is required, resume runs the migration tool and
repeats the check. A failed second check or blocking diagnostic stops the
resume attempt.

Review status, including the repository command `rvw_status` and its local
`rwst` alias, must be able to run the same check and migration. This bounded
preflight mutation is the only exception to the prior strictly read-only status
contract. Once the check passes, normal discovery, projection, and rendering
remain read-only. Status reports whether migration was unnecessary, completed,
or blocked.

## Required LLM nature trace

The shared host detector must determine whether the current session is Claude,
Codex, or Gemini from host evidence when possible. When detection is not
possible, it records an explicit unknown or unavailable result rather than
choosing a host silently.

Every new exchange must durably trace the LLM nature acting as requestor and
the LLM nature acting as reviewer. Requests, answers, coordination
transitions, status projections, and continuation instructions preserve those
role-specific identities. Human-readable and machine-readable review status
both report them.

Migration moves old evidence but does not invent an LLM nature. Legacy
identity completion belongs to the role-aware artifact policy below.

## Legacy and identity-bearing artifact policy

Readers must accept both legacy artifacts without LLM nature and newer
artifacts that record it. Artifact kind and durable exchange identity determine
which protocol role authored each artifact.

Before continuing a resolved role, resume scans every artifact in the selected
exchange attributed to that role. It classifies each artifact as:

- missing LLM nature;
- matching the detected current LLM;
- recording a different LLM nature.

When none records a different nature, resume updates all missing-nature
artifacts attributed to the current role so they record the detected current
LLM. The update covers every missing-nature artifact attributed to that role in
the selected exchange occurrence, not only the first legacy artifact the
workflow happens to read. Already matching artifacts remain unchanged.

When any current-role artifact records a different nature, resume stops before
performing any missing-nature backfill and shows every conflicting artifact
path, the role, each recorded nature, and the current nature. It presents only:

- `Override` -- continue as the current LLM for the role and complete the
  missing-nature backfill while preserving every conflicting recorded value as
  evidence;
- `Stop` -- make no identity change and end the resume attempt.

Override never rewrites an existing conflicting LLM nature.

Artifacts authored by the counterpart role remain readable. When their LLM
nature is missing, the reader ignores that missing field and leaves the
artifact unchanged. A counterpart artifact carrying a different nature is
expected and does not block the current role.

## Resume skill and role selection

Resume is a public LLM skill with a shared implementation and host-specific
adapters. It must not add a CMD, batch, or repository-root `rvw_resume`
command, because continuation requires an active LLM session.

The skill supports specification requestor, specification reviewer,
implementation code-review requestor, and implementation code reviewer roles.
It resolves the role as follows:

1. Detect the current LLM nature and compare it with the durable requestor and
   reviewer traces.
2. When the trace identifies the current LLM as one role, select that role
   without asking the human to choose.
3. When legacy trace evidence contains no LLM nature and no role argument was
   passed, ask whether the session resumes as `requestor` or `reviewer`.
4. Accept an explicit `requestor` or `reviewer` argument without that role
   question when no LLM nature exists.
5. When the forced role conflicts with a known LLM-role trace, show the
   mismatch and require explicit confirmation before applying the override.
6. A matching role argument does not bypass the role-wide artifact identity
   scan or its `Override` or `Stop` decision.

Once the role and artifact identity gates are resolved, resume continues
without another confirmation.

## Reviewer continuation behavior

A resumed reviewer has exactly two protocol outcomes:

- When a review request exists, renew or reclaim its exact identity, round,
  occurrence, and lease as needed, assess it, and publish the matching answer.
- When nothing is available to review, including when no exchange or
  implementation step has started and no live request artifact exists, enter a
  global reviewer wait for any new specification- or code-review request
  artifact in the configured review directory. The future document, family,
  slug, step, round, and occurrence do not need to be known before the wait
  starts. An idle exchange is a valid wait entry point and must not be rejected
  merely because the existing exchange-specific `wait-request` operation has
  no concrete identity to target.

A reviewer resume never runs `pw skill`, starts writer work, or advances a
requestor workflow. Its open-ended wait wakes only for review-request
artifacts, not unrelated review files.

## Requestor continuation behavior

A resumed requestor follows the durable workflow state:

- When a review is in progress and its response has not arrived, start or
  restart the wait for the matching review-answer artifact.
- When the requestor owns the next review action, renew or reclaim the exact
  identity, round, occurrence, and lease as needed; consume an answer, apply
  requested work, publish a later request, or continue to the human convergence
  gate.
- When no review is in progress and no further request remains for the current
  task, run `pw skill` and immediately follow the command it returns.

The `pw skill` result may continue writing, implementation, a later task that
will publish its own review request, or any other workflow selected from the
repository's durable state. No second go-ahead is requested after role and
identity resolution.

## Recovery safety and protocol boundaries

- Direct human invocation of resume authorizes lease-independent pickup even
  when the recorded lease has not expired and without waiting for
  `wait_timeout_seconds`.
- Waiting, renewal, reclaim, and action preserve the exact exchange identity,
  family, reviewed document, umbrella, step when applicable, round,
  occurrence, artifacts, expected actor, and next action.
- Malformed, repair-required, escalated, artifact-inconsistent, or ambiguous
  multiple-exchange states stop with typed review-status evidence rather than
  a guessed continuation.
- Ordinary automated rounds, reviewer recommendations, and the durable
  `awaiting-human-confirmation` convergence gate retain their existing
  authority rules.
- Repeating resume against the same durable state is idempotent.

## Acceptance criteria for review resumption

1. With no configuration, every new runtime review artifact is placed below
   `<PRJ_DIR>/.reviews`.
2. With a configured artifact home, every producer, consumer, waiter, status
   reader, migration tool, and resume path uses that same resolved directory.
3. `migration_check` quickly distinguishes ready, migration-required, and
   blocked layouts without collecting the full status model.
4. Resume always runs the migration check first, migrates recognized misplaced
   evidence when safe, repeats the check, and refuses to continue on an unsafe
   or incomplete result.
5. Review status and `rvw_status` can perform and report the same bounded
   migration; after the preflight they remain observational.
6. New exchanges trace Claude, Codex, Gemini, or an explicit unknown result for
   both requestor and reviewer roles, and status exposes those values in human
   and machine output.
7. A selected role with only matching or missing identities backfills every
   missing-nature artifact attributed to that role before continuing.
8. A single conflicting identity prevents partial backfill and presents the
   complete conflict set with `Override` and `Stop` choices.
9. Override preserves conflicting values, fills only missing current-role
   identities, and continues; Stop leaves all identity evidence unchanged.
10. A counterpart-role artifact without LLM nature remains readable and
    unchanged.
11. Missing trace nature with no role argument prompts for requestor or
    reviewer; an explicit role supplies that choice, subject to known-trace
    conflict confirmation.
12. A reviewer with a request reclaims and answers it; a reviewer without one,
    including before any exchange or implementation step starts, waits
    globally for any future specification- or code-review request artifact
    without requiring its identity.
13. A requestor waits for an in-progress answer, performs owned review work, or
    runs and follows `pw skill` when no review remains.
14. Once role and identity gates pass, resume acts or waits without another
    confirmation.
15. All affected tests from the shared exchange, requestor, reviewer,
    review-status, adapter, waiting, and documentation topics are updated for
    the artifact-home and LLM-nature rules. The canonical review-status
    instruction and published skill description are updated to replace their
    strictly read-only wording with the bounded migration exception.
16. Creation of an artifact home establishes effective Git ignore coverage
    before any artifact moves into it, and migration preflight blocks a home
    whose required coverage is absent.
17. One versioned repository declaration carries the artifact-home setting;
    invalid locations outside the repository and existing tracked directories
    are rejected.
18. The typed status result distinguishes migration that was unnecessary from
    migration that completed, advances its schema version, and reports a
    blocked migration as an operational failure with a diagnostic.

## Scope boundaries and dependencies

This effort depends on `review-exchange-core`, `review-status-command`,
`spec-review-requestor`, `spec-reviewer`, `code-review-requestor`,
`code-reviewer`, and `review-mode-docs`.

The implementation updates their shared code and affected tests through this
topic. It does not reopen their completed requirement, design, plan, validation
documents, or umbrella statuses. It does not create a shell resume command,
weaken the convergence-only human authority gate, overwrite conflicting LLM
identity evidence, or treat counterpart missing identity as damage.

This effort supersedes two rules the umbrella draft states for earlier items:
runtime protocol artifacts no longer stay directly at the project root under
the `a.*` ignore rule, and the resume entry point is an LLM skill rather than
the repository-root `rvw_resume` command the umbrella originally regrouped for
this item, because continuation requires an active LLM session. The umbrella
draft is updated with both revisions; no completed requirement, design, plan,
validation document, or completed umbrella row is reopened.

## Open questions for the v0.11.0 feature request

### Q01: Which review artifacts belong in the configured artifact home?

Question description: The requirement puts protocol-owned runtime artifacts
below the configured directory, but the umbrella also calls versioned
`docs/.../review.*.md` transcripts review artifacts. The feature must state
whether those documentation transcripts move too.

#### BBQ for Q01

We need to decide whether the filing cabinet stores only the live case files or
also the published case history kept in the library. Moving both gives one
location, but it also removes documentation from its established shelf. In
this picture: the filing cabinet is `.reviews`, live case files are runtime
protocol artifacts, and the library history is versioned review transcripts.

#### Options for Q01

- Option Q01-A: Move only protocol-owned runtime artifacts.
  - pro: Keeps transient coordination evidence together without changing the
    versioned documentation contract.
  - con: Review-related files still exist in two intentional locations.
- Option Q01-B: Move runtime artifacts and versioned transcripts.
  - pro: Places every file called a review artifact below one directory.
  - con: Breaks the established rule that transcripts live beside the reviewed
    documents and remain normal project documentation.
- Option Q01-C: Configure runtime and transcript locations independently.
  - pro: Supports repositories that want both categories relocated.
  - con: Adds two settings and cross-location discovery rules to one feature.

#### Recommended option for Q01 (with arguments for this choice)

Option Q01-A: Move only protocol-owned runtime artifacts. The requested
migration targets files currently stored at `PRJ_DIR`, while versioned
transcripts already have a stable documentation purpose and location.

#### Answer to Q01: option Q01-A (with reason why it must be accepted as the answer)

Option Q01-A: Accept this boundary so `.reviews` becomes the runtime protocol
home without silently relocating versioned documentation or reopening its
history contract. This feature therefore supersedes the umbrella's earlier
project-root placement rule for runtime artifacts only.

### Q02: Which legacy locations must migration_check inspect?

Question description: The requirement names current root artifacts and a new
default directory, but a configured directory may differ from the default. The
feature must define which known legacy locations are checked without turning
the preflight into an unrestricted repository scan.

#### BBQ for Q02

When moving house, we can check only the old front room, check the front room
and the standard storage unit, or search every building in town. The last
choice finds more but is slow and may collect someone else's property. In this
picture: the front room is `PRJ_DIR`, the storage unit is `.reviews`, and the
town is the entire repository tree.

#### Options for Q02

- Option Q02-A: Inspect only artifacts directly below `PRJ_DIR`.
  - pro: Matches the original legacy layout and keeps the check small.
  - con: Misses artifacts in `.reviews` after configuration changes to another
    directory.
- Option Q02-B: Inspect `PRJ_DIR`, the default `.reviews`, and the configured
  directory.
  - pro: Covers the known old, default, and current homes with bounded work.
  - con: Cannot discover an arbitrary previously configured path that is no
    longer recorded.
- Option Q02-C: Recursively scan the repository for artifact-shaped names.
  - pro: Can find evidence left in unexpected folders.
  - con: Risks false matches, slower checks, and migration of unrelated files.

#### Recommended option for Q02 (with arguments for this choice)

Option Q02-B: Inspect the root, default, and configured locations. These are
the locations the protocol can identify safely without guessing from filenames
across the repository.

#### Answer to Q02: option Q02-B (with reason why it must be accepted as the answer)

Option Q02-B: Accept the bounded three-location check because it covers normal
legacy and configuration transitions while keeping `migration_check` fast and
trustworthy.

### Q03: Can one session override the repository artifact-home setting?

Question description: Every producer and consumer must resolve the same
artifact home. The requirement does not settle whether a session environment
or skill argument may temporarily override the durable repository setting.

#### BBQ for Q03

Two coworkers need to agree which mailbox receives the forms. A personal note
that redirects one coworker to another mailbox is flexible, but the other
coworker may wait forever at the old one. In this picture: the mailbox is the
artifact home, the coworkers are requestor and reviewer sessions, and the
personal note is a per-session override.

#### Options for Q03

- Option Q03-A: Use one durable repository setting, with the default when it is
  absent.
  - pro: Every role resolves the same location across sessions and restarts.
  - con: A temporary alternate location requires changing repository state.
- Option Q03-B: Let environment variables override the repository setting.
  - pro: Supports temporary and automation-specific locations.
  - con: Different sessions can silently watch different directories.
- Option Q03-C: Let every resume or status invocation pass a path argument.
  - pro: Makes one-off testing convenient.
  - con: Weakens durable discovery and requires the caller to remember context.

#### Recommended option for Q03 (with arguments for this choice)

Option Q03-A: Use one durable repository setting. Restart-safe coordination
depends on every participant deriving the same location without sharing shell
state or command arguments.

#### Answer to Q03: option Q03-A (with reason why it must be accepted as the answer)

Option Q03-A: Accept one durable setting plus the default so artifact discovery
remains consistent across Claude, Codex, Gemini, and later sessions. Q13
selects the durable carrier and its repository-boundary validation.

### Q04: Should ordinary review status migrate automatically?

Question description: Resume must migrate before continuing, while review
status only needs to be able to check and migrate. The feature must settle
whether a normal `rvw_status` call performs safe migration automatically or
requires an explicit migration request.

#### BBQ for Q04

A receptionist can move misplaced files while checking the register, or report
the misplaced files and wait for permission. Automatic filing is convenient,
but callers who expected only a report may be surprised by moved files. In
this picture: the receptionist is `rvw_status`, the register check is status
collection, and filing is artifact migration.

#### Options for Q04

- Option Q04-A: Automatically migrate whenever `migration_check` says the move
  is safe.
  - pro: A simple status call repairs the legacy layout and immediately reports
    current state.
  - con: A command previously treated as read-only now moves files by default.
- Option Q04-B: Check by default and require an explicit status migration mode.
  - pro: Preserves observational behavior for normal status callers.
  - con: Leaves status unable to complete until the caller invokes migration.
- Option Q04-C: Never migrate from status; report the migration command only.
  - pro: Keeps a strict separation between observation and mutation.
  - con: Does not satisfy the requested ability for status to perform migration
    itself.

#### Recommended option for Q04 (with arguments for this choice)

Option Q04-A: Automatically migrate safe legacy layouts and report the action.
The revised CDC explicitly accepts bounded preflight mutation, and automatic
migration gives both resume and status one predictable entry behavior.

#### Answer to Q04: option Q04-A (with reason why it must be accepted as the answer)

Option Q04-A: Accept automatic safe migration so `rvw_status` can return a
current, trustworthy result without a second command while still stopping on
every collision or ambiguity.

### Q05: Is migration all-or-nothing when one artifact conflicts?

Question description: The requirement refuses destructive collisions but does
not say whether safe files may move before a later conflict stops migration.
That choice affects recovery and the meaning of the repeated preflight.

#### BBQ for Q05

A mover can inspect every box before loading the truck, or load clear boxes
until finding one with a duplicate label. The second approach makes progress,
but leaves belongings split between houses. In this picture: boxes are review
artifacts, duplicate labels are destination collisions, and the two houses are
the legacy and configured directories.

#### Options for Q05

- Option Q05-A: Validate the complete move first and migrate all artifacts or
  none.
  - pro: Never leaves one exchange split across locations after a known
    conflict.
  - con: One collision blocks movement of every otherwise safe artifact.
- Option Q05-B: Move non-conflicting artifacts and report the blocked subset.
  - pro: Reduces the remaining migration work.
  - con: Creates a partial layout that every reader must understand during
    repair.
- Option Q05-C: Keep the source copy when a destination exists and continue.
  - pro: Avoids overwriting either copy.
  - con: Leaves duplicate identities and makes the authoritative artifact
    ambiguous.

#### Recommended option for Q05 (with arguments for this choice)

Option Q05-A: Use an all-or-nothing migration after a complete preflight. The
protocol's durable identity is more important than partial progress, and a
split exchange would make resume and status less trustworthy.

#### Answer to Q05: option Q05-A (with reason why it must be accepted as the answer)

Option Q05-A: Accept atomic migration so a failed attempt leaves the legacy
layout intact and gives the human one complete conflict report to resolve.

### Q06: How should resume choose when both roles record the same LLM nature?

Question description: A single Codex, Claude, or Gemini nature may appear as
both requestor and reviewer. In that case nature detection does not identify
one role even though neither trace is missing.

#### BBQ for Q06

One person has keys for both the writer's office and the reviewer's office.
Recognizing the person does not say which desk they should use today. In this
picture: the person is the detected LLM nature, the offices are the two roles,
and the desk choice is resume routing.

#### Options for Q06

- Option Q06-A: Ask for requestor or reviewer when both traces match and no role
  argument was passed.
  - pro: Resolves the real ambiguity without guessing from transient state.
  - con: Adds a role question even though both traces contain LLM nature.
- Option Q06-B: Select whichever role owns the next protocol action.
  - pro: Keeps simple resume automatic in many cases.
  - con: Conflates current protocol state with proof of which role the session
    intends to play.
- Option Q06-C: Refuse unless the caller passes an explicit role argument.
  - pro: Makes automation deterministic.
  - con: A human simple resume cannot proceed without restarting with an
    argument.

#### Recommended option for Q06 (with arguments for this choice)

Option Q06-A: Ask only in this genuinely ambiguous case. It follows the rule
that resume must not guess a role while still letting a simple interactive
invocation continue.

#### Answer to Q06: option Q06-A (with reason why it must be accepted as the answer)

Option Q06-A: Accept the role question when both role traces match the current
LLM because nature alone cannot distinguish the intended responsibility.

### Q07: What should resume do when the current LLM nature is unknown?

Question description: Host detection can produce unknown or unavailable. The
feature must settle whether resume may continue with an explicit role and what
happens to missing-nature legacy artifacts in that session.

#### BBQ for Q07

A worker can prove which job they were assigned but their identity badge is
unreadable. They can still do the job, but stamping old paperwork with
"unknown" may make later identification harder. In this picture: the job is
the protocol role, the badge is LLM nature detection, and the paperwork is the
legacy artifact set.

#### Options for Q07

- Option Q07-A: Allow role selection but leave missing artifact natures
  unchanged until a known LLM resumes.
  - pro: Continues useful work without writing a weak identity over legacy
    evidence.
  - con: The exchange remains partly untraced.
- Option Q07-B: Backfill the explicit value `unknown` into current-role
  artifacts.
  - pro: Records that identity handling ran during the session.
  - con: Converts recoverable absence into a durable value that still cannot
    select a future role.
- Option Q07-C: Refuse resume until Claude, Codex, or Gemini is detected.
  - pro: Every continuation has a concrete identity.
  - con: Blocks other or newly introduced hosts even when the role is explicit.

#### Recommended option for Q07 (with arguments for this choice)

Option Q07-A: Continue with an explicit or selected role but do not backfill
unknown. This preserves legacy evidence for a later known session while
keeping the protocol usable on unsupported hosts.

#### Answer to Q07: option Q07-A (with reason why it must be accepted as the answer)

Option Q07-A: Accept role continuation without unknown backfill so the feature
does not confuse inability to detect a host with a durable participant nature.

### Q08: How broad is one role-wide identity backfill?

Question description: The requirement says to update all artifacts for a role,
but it can mean the selected exchange, every occurrence for the same reviewed
document, or every artifact for that role in the repository.

#### BBQ for Q08

Correcting the author's name can mean fixing one case folder, every edition of
one book, or every document in the archive. The broader the correction, the
greater the chance of changing work from another session. In this picture: the
case folder is one exchange occurrence, the editions are one reviewed topic's
occurrences, and the archive is the repository.

#### Options for Q08

- Option Q08-A: Backfill all current-role artifacts in the selected exchange
  occurrence only.
  - pro: Uses one exact durable identity and keeps the mutation bounded.
  - con: Other legacy exchanges for the same role remain unfilled.
- Option Q08-B: Backfill every occurrence for the same reviewed document and
  role.
  - pro: Completes identity history for one topic at once.
  - con: May attribute older occurrences created by another session of the same
    role.
- Option Q08-C: Backfill every repository artifact attributed to that role.
  - pro: Removes missing nature broadly in one pass.
  - con: Incorrectly assumes one current LLM authored all historical work for
    that role.

#### Recommended option for Q08 (with arguments for this choice)

Option Q08-A: Limit backfill to the selected exchange occurrence. That is the
largest set whose durable context the resume invocation has actually selected
and validated.

#### Answer to Q08: option Q08-A (with reason why it must be accepted as the answer)

Option Q08-A: Accept exchange-scoped backfill to satisfy the all-artifacts rule
without claiming ownership of unrelated historical exchanges.

### Q09: How long does an identity discrepancy override last?

Question description: `Override` authorizes continuation despite current-role
artifacts naming another LLM, while preserving those names. The feature must
state whether that authority expires with the current resume attempt or changes
future routing.

#### BBQ for Q09

A supervisor can admit a substitute for one shift, for the whole project, or
permanently change the staff register. A narrow pass is repetitive but does not
silently alter later access. In this picture: the substitute is the current
LLM, the shift is one resume attempt, and the staff register is durable role
identity.

#### Options for Q09

- Option Q09-A: Apply Override only to the current resume attempt.
  - pro: Future sessions re-evaluate the preserved discrepancy.
  - con: Repeated resumes may ask again about the same evidence.
- Option Q09-B: Persist Override for the selected exchange occurrence.
  - pro: Avoids repeated prompts while that exchange continues.
  - con: Adds a second durable authority record that later readers must honor.
- Option Q09-C: Replace the conflicting recorded nature with the current LLM.
  - pro: Makes future routing simple.
  - con: Destroys the evidence the requirement explicitly says to preserve.

#### Recommended option for Q09 (with arguments for this choice)

Option Q09-A: Limit Override to one resume attempt. The recorded mismatch stays
visible, and every later session makes its own explicit decision.

#### Answer to Q09: option Q09-A (with reason why it must be accepted as the answer)

Option Q09-A: Accept attempt-scoped Override because it grants the requested
continuation without converting a human exception into silent permanent role
ownership.

### Q10: Does an open-ended reviewer wait expire?

Question description: Existing review waits have timeout and escalation rules,
but a reviewer waiting for an unknown future request has no exchange to renew
or escalate. The expected lifetime of that wait needs a feature-level rule.

#### BBQ for Q10

A duty officer can remain on call until a case arrives, end the shift after a
timer, or repeatedly clock out and back in. A timeout makes sense for a late
response to an existing case, but not necessarily before any case exists. In
this picture: the officer is the resumed reviewer, the case is a new request
artifact, and the shift timer is the exchange timeout.

#### Options for Q10

- Option Q10-A: Wait until a request arrives or the human cancels the wait.
  - pro: Matches the requirement to remain available for an unknown future
    request.
  - con: The session can remain occupied indefinitely.
- Option Q10-B: Apply the ordinary review timeout and escalate when it expires.
  - pro: Keeps all waits bounded by one policy.
  - con: There is no exchange identity or counterpart failure to escalate.
- Option Q10-C: Poll once and return when no request exists.
  - pro: Never occupies the session for long.
  - con: Does not satisfy the requested reviewer resume behavior.

#### Recommended option for Q10 (with arguments for this choice)

Option Q10-A: Keep the reviewer wait active until a request arrives or the
human cancels. Exchange timeout rules begin only after a concrete request and
exchange identity exist.

#### Answer to Q10: option Q10-A (with reason why it must be accepted as the answer)

Option Q10-A: Accept the open-ended wait because reviewer resume is explicitly
an availability mode when no request identity is known.

### Q11: What happens when several review requests appear for one reviewer?

Question description: An open-ended reviewer may observe more than one new
request. Existing status behavior refuses ambiguous multiple exchanges, but
resume must say whether it keeps that rule or automatically orders work.

#### BBQ for Q11

If two case files land on a reviewer's desk together, they can ask which one is
urgent, take the oldest, or work through the whole stack. Automatic ordering is
convenient, but it creates a priority rule the requester never stated. In this
picture: case files are review requests, desk arrival is the configured-folder
wait, and priority is resume selection.

#### Options for Q11

- Option Q11-A: Stop, list all requests, and ask the human to select one.
  - pro: Preserves the established refusal to guess among multiple exchanges.
  - con: Interrupts otherwise automatic reviewer operation.
- Option Q11-B: Select the oldest request deterministically.
  - pro: Lets reviewer resume continue without a human choice.
  - con: Introduces an age-based priority that may not match project needs.
- Option Q11-C: Process every request sequentially in discovery order.
  - pro: Eventually answers the full queue automatically.
  - con: Widens one resume invocation across independent exchanges and makes
    failure recovery harder.

#### Recommended option for Q11 (with arguments for this choice)

Option Q11-A: Keep the existing ambiguity boundary and ask for one selection.
The feature promises exact durable continuation, not an implicit review queue
policy.

#### Answer to Q11: option Q11-A (with reason why it must be accepted as the answer)

Option Q11-A: Accept explicit selection for concurrent requests so resume never
chooses an exchange priority that the protocol did not record.

### Q12: How does the configured artifact home remain ignored by Git?

Question description: Exchange activation requires every transient path to be
effectively ignored. The root `a.*` rule does not cover artifacts moved below a
configured subdirectory, so the home needs an explicit ignore-coverage rule.

#### BBQ for Q12

A secure records room must be marked private before files are carried inside.
The sign can be installed on the building, on the room itself, or the guard can
be told to ignore the missing sign. In this picture: the room is the configured
artifact home, the sign is Git ignore coverage, and the guard is activation's
ignore validation.

#### Options for Q12

- Option Q12-A: Add the configured home to the repository's root `.gitignore`.
  - pro: Keeps ignore policy visible in one versioned file.
  - con: A configurable path requires rewriting repository ignore rules each
    time the setting changes.
- Option Q12-B: Write a `.gitignore` inside the artifact home when it is
  created.
  - pro: Ignore coverage travels with any configured repository-local home and
    preserves the existing validation rule.
  - con: The migration and directory-creation paths must maintain one extra
    control file.
- Option Q12-C: Let ignore validation accept the resolved home without a Git
  rule.
  - pro: Avoids creating or changing ignore files.
  - con: Weakens the existing safety check and can leave transient evidence
    visible to Git tooling.

#### Recommended option for Q12 (with arguments for this choice)

Option Q12-B: Create an internal `.gitignore` before placing artifacts in the
home. This works for the default and configured locations without teaching
activation an exception.

#### Answer to Q12: option Q12-B (with reason why it must be accepted as the answer)

Option Q12-B: Accept the home-local ignore rule. Migration creates a missing
home and its ignore rule before moving anything. A home that already exists
without effective coverage is a blocking layout: `migration_check` reports it
rather than adding the rule on its behalf. The generated home-local
`.gitignore` is itself untracked under its own rule, so a fresh clone
establishes coverage when first use creates the home.

### Q13: Where does the durable artifact-home setting live?

Question description: Every participant must derive one location across
sessions and machines. The feature must select a durable configuration carrier
and reject locations that would expose or relocate protocol evidence unsafely.

#### BBQ for Q13

All staff need the same recorded address for the records room. A private note
works only for one employee, a shared register travels with the office, and a
miscellaneous settings ledger may already have unrelated owners. In this
picture: the address is the artifact-home path, the private note is
`a.review-mode`, and the shared register is a versioned declaration.

#### Options for Q13

- Option Q13-A: Store the path in the ignored `a.review-mode` marker.
  - pro: Keeps all review-mode controls in one per-clone file.
  - con: Other clones and machines do not receive the same setting.
- Option Q13-B: Add a dedicated versioned repository declaration beside
  `.review-validation`.
  - pro: Every participant derives the same path without shared shell state.
  - con: Adds one project-level configuration surface.
- Option Q13-C: Reuse an existing versioned project settings file.
  - pro: Avoids another root declaration.
  - con: Couples review protocol configuration to a file with unrelated
    ownership or a format not shared by all consuming projects.

#### Recommended option for Q13 (with arguments for this choice)

Option Q13-B: Use a dedicated versioned declaration because the setting must
remain identical across sessions, restarts, clones, and machines.

#### Answer to Q13: option Q13-B (with reason why it must be accepted as the answer)

Option Q13-B: Accept a dedicated versioned repository declaration. Its exact
file name and syntax are left to design. Its path must resolve inside the
repository; a path outside the repository or an existing tracked directory is
invalid and blocks migration, status, and resume.

### Q14: How does typed review status report migration?

Question description: Resume consumes the stable status result without
scraping prose. The result must represent unnecessary, completed, and blocked
migration while preserving the existing operational-failure meaning.

#### BBQ for Q14

A delivery receipt can add a new relocation field, reuse its failure stamp when
delivery is blocked, or leave the details only in a handwritten note. In this
picture: the receipt is the typed status schema, relocation is migration, and
the failure stamp is the operational-failure outcome.

#### Options for Q14

- Option Q14-A: Add a typed migration record and advance the schema version.
  - pro: Resume and both renderers receive validated unnecessary or completed
    migration state.
  - con: Every schema consumer and fixture must adopt the new version.
- Option Q14-B: Represent a blocked migration with the existing
  operational-failure outcome and a diagnostic.
  - pro: Preserves the established meaning that status could not produce a
    trustworthy result.
  - con: The migration-specific reason still needs a typed diagnostic record.
- Option Q14-C: Report migration only in human-readable status output.
  - pro: Avoids a schema change.
  - con: Forces resume to scrape prose or rediscover migration state.

#### Recommended option for Q14 (with arguments for this choice)

Options Q14-A and Q14-B together: add the typed migration record and schema
version for unnecessary and completed results, while using the existing
operational-failure outcome when migration is blocked.

#### Answer to Q14: options Q14-A and Q14-B (with reason why they must be accepted as the answer)

Accept Q14-A and Q14-B together. The schema version must advance because the
typed result changes; a blocked layout returns operational failure with a
migration diagnostic because no trustworthy status projection can follow.
