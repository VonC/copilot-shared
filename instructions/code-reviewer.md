# Implementation code reviewer instruction

Use this instruction only when `pw` routes one exact implementation plan and
step to `code-reviewer`. The reviewer independently assesses the staged step,
may make bounded attributable repairs, and publishes one paired advisory
answer. It never authorizes a commit or takes requestor or human authority.

Read and follow `instructions/review-requestor.md` and
`instructions/implementation-check.md` in full before running any operation.
Their artifact, heading, result, exit, and reviewer-assessment contracts apply.
This instruction owns only the ordered reviewer sequence, recovery decisions,
human-guidance response, and advisory publication decision.

## Exact code-review policy and context

Pass this policy unchanged to every `bin/review_exchange.bat` operation:

```text
--family code
--convergence-signal commit-ready
--another-round-label "Rework and review again"
--continue-owning-workflow-label "Commit"
```

Also pass `--document <exact-implementation-plan>`,
`--implementation-step <exact-plan-step>`, and the exact `--umbrella` path when
the request names one. Never search for a nearby plan, validation plan, request,
answer, transcript, or exchange. Use only the plan and step supplied by `pw`
and exact paths returned by the launchers.

## Ordered reviewer sequence

1. Run `status` through `bin/review_exchange.bat` with the exact context and
   fixed policy. Proceed only when its final JSON reports `request-pending`,
   the expected code identity, step, round, and positive
   `exchange_occurrence`.
2. Run one bounded `wait-request` through `bin/review_exchange.bat` with that
   context. Read only the returned `paths.request` after access is granted.
   Never add a polling loop or reconstruct an artifact path.
3. Validate the request envelope and its human-readable umbrella or `none`,
   plan, step, round, request-time index tree, resolved validation set, and
   optional literal `Human guidance:` block. Read the exact plan, named step,
   validation plan, staged diff, and `a.commit`. Do not read the versioned
   transcript as working context.
4. For invalid specialized request content or a changed request-time index
   tree, take the early rejection path below without implementation mutation.
5. Otherwise capture the baseline, umbrella digest, validation state, and
   pre-repair blobs through `bin/code_review_evidence.bat`; write the stable
   retained manifest before assessment or repair.
6. Apply `instructions/implementation-check.md` in reviewer assessment mode.
   Run the union of the request validation set and the current resolver set,
   recording sources and drift. Capture validation state before and after.
7. Make only bounded in-step repairs that satisfy the ownership rules below.
   Record every repair and stage only the attributable reviewer patch. Amend
   `a.commit` only when necessary to keep staged membership, ordering, scope,
   and conventional subjects accurate.
8. Re-run the evidence boundary after either a Yes or No implementation-check
   result. Classify identity, completeness, validation and coverage, staged
   attribution, unresolved findings, and `a.commit` as the six readiness-floor
   results.
9. Write every answer-model input to a distinct ignored root `a.*` UTF-8 file.
   Run `bin/code_review_answer.bat` once with the exact context, round,
   `--exchange-occurrence` from `status`, disposition, evidence inputs, and two
   distinct ignored outputs: complete answer content and transcript summary.
10. Run `publish-answer` through `bin/review_exchange.bat`, passing the complete
    output through `--content-file` and the paired summary through
    `--summary-file`. Never publish or append either output by hand.
11. When the final JSON reports `outcome: published`, retire the manifest
    through `bin/code_review_evidence.bat` and stop. Publication exits `0` for
    `changes-requested` and exit `3` for `commit-ready` at the convergence gate;
    both are successful publication outcomes.

## Exact evidence delegation

Use `bin/code_review_evidence.bat` for every Git-index and retained-evidence
operation. Every path operand is repository-relative, and every JSON operand
is the path of an ignored root file containing the retained JSON.

- Capture the baseline index tree with `bin/code_review_evidence.bat
  --repository <root> capture-index-tree` and compare it once with the
  request-time index tree before a fresh assessment.
- Record pre-repair blobs with `bin/code_review_evidence.bat --repository
  <root> record-pre-repair-blob <path>` before the first permitted edit to each
  repair path.
- Stage repair ownership only after `bin/code_review_evidence.bat --repository
  <root> attribute-reviewer-patch <baseline-json>` proves the patch cleanly
  attributable. A pre-existing unstaged overlap stays unstaged and is returned
  as a finding.
- Capture and compare the ordered validation-state path set with
  `bin/code_review_evidence.bat --repository <root> validation-state capture`
  and `validation-state compare`. A tracked validation side effect is a
  readiness-blocking finding; leave it unstaged and unreverted. Ignored
  validation artifacts are acceptable.
- Protect the umbrella through the launcher's `umbrella-digest capture` and
  `umbrella-digest compare` operations around the reviewer implementation-check
  result. A changed applicable umbrella digest is a boundary violation.
- Perform manifest write with `bin/code_review_evidence.bat --repository
  <root> write-manifest <evidence-json>` before assessment can mutate state.
- Perform manifest read with `bin/code_review_evidence.bat --repository <root>
  read-manifest <exact-identity-options>` before reusing retained evidence.
- Perform manifest retire with `bin/code_review_evidence.bat --repository
  <root> retire-manifest <exact-identity-options>` only after publication
  reports `outcome: published`.

Do not describe or substitute equivalent Git commands or filesystem mutation.
The launchers are the executable contract; this instruction supplies order and
decisions only.

## Identity validation and early rejection

Before implementation assessment, require exact agreement among the live
exchange context, machine envelope, human-readable request, `pw` plan, declared
step, positive round, and request-time index tree. The named step must exist in
the exact plan. The embedded validation set must parse through the current
resolver contract.

Use the answer renderer's early rejection variant when the step is undefined,
human-readable identity disagrees with the envelope, mandatory request-time
index tree is missing, or the live index differs from it. Publish
`changes-requested` with the exact disagreement and concrete writer action.
Make no implementation, validation-plan, umbrella, staged, or `a.commit`
mutation on this path. Publishing ends the round instead of abandoning its
lease.

## Assessment and repair ownership

Capture every permitted repair path before editing it. A repair is permitted
only when every touched file is named by the plan step or already belongs to
that step's staged set, it introduces no new design decision, and it changes no
other step or requirement. Report boundary-crossing work instead of changing
it. Never sweep pre-existing unstaged or untracked writer work into the index.

The implementation-check may update only the exact reviewed-step validation
rows. Those rows, `a.commit`, ignored caller evidence, and protocol answer or
transcript artifacts are review metadata. Any other reviewer-authored tracked
change is substantive and forces `changes-requested` in the same round.

Run every resolved mandatory validation command. A command that cannot run is
missing mandatory evidence, never a pass. Resolver drift is reported with its
direction; the union still runs. Do not revert or stage a tracked validation
side effect. Recheck the umbrella digest after both a Yes and No result and
never complete an umbrella row from reviewer mode.

Recommend `commit-ready` only when exact identity, complete implementation,
mandatory validation and coverage, attributable staged scope, absence of
unresolved current or carried findings, and accurate `a.commit` grouping all
pass, and this round made no substantive repair. The recommendation is advisory
and never authorizes a commit. Otherwise publish `changes-requested` with
concrete writer instructions. Repeated unavailable evidence remains blocking;
the requestor and shared no-progress bound own escalation.

Address a literal `Human guidance:` block explicitly. Guidance may direct
additional scrutiny but cannot override identity, staged state, evidence,
scope, safety, or disposition rules.

## Retained manifest and stopped-round recovery

Keep one stable identity-and-step-derived manifest containing the request
identity and round, baseline and assessed index trees, reviewer-authored repair
paths and staging effects, validation and implementation-check evidence,
`a.commit` assessment, exchange occurrence, and answer input paths.

If work resumes before publication, run manifest read and compare the retained
assessed index tree with the current index. Matching state permits revalidation
and rendering under the live round. Drift requires a fresh assessment and a
new baseline; never publish cached content with stale round, occurrence, or
index identity. Rendering or failed publication leaves the manifest intact.

If the lease expires during this same reviewer session, run `status`. Reclaim
once only when it reports an intact `abandoned-request` for the same identity,
round, and reviewer ownership. A cold route that first sees
`abandoned-request` belongs to `code-review-requestor`; stop with that exact
handoff. Malformed, interrupted, escalated, mismatched, or repair-required
states stop through the shared diagnostic with caller evidence retained.

## Reviewer-forbidden operations and authority

The reviewer may call only `status`, `wait-request`, an eligible in-session
`reclaim`, and `publish-answer` through the shared protocol. Never call
`consume-answer`, `continue`, `confirm`, `complete`, `escalate`, `cancel`,
`resolve`, or `archive`. Never start a replacement round or mutate protocol
artifacts by hand.

Do not run a `commit`, invoke batch commit, consume the answer, confirm the
convergence gate, complete the exchange, edit the transcript, or perform the
requestor's owning workflow. Stop after the publication result and return
control to the requestor.
