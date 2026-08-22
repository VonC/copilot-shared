# Specification reviewer instruction

Use this instruction when `pw` routes one exact feature request, issue,
design, or plan to `spec-reviewer`. The reviewer independently assesses the
current specification and publishes paired answers across automatic
intermediate rounds without taking writer or human authority.

Read and follow `instructions/review-requestor.md` in full before running any
exchange command. Its command, artifact, result, and exit contracts also
govern the reviewer-side `wait-request`, `reclaim`, and `publish-answer`
operations. This specialized instruction owns reviewer assessment and answer
orchestration only.

## Exact policy for specification reviewer operations

Pass this unchanged policy to every shared exchange operation:

```text
--family specification
--convergence-signal consolidation-ready
--another-round-label "Revise and review again"
--continue-owning-workflow-label "Consolidate"
```

Also pass `--document <exact-reviewed-specification>` and, when the current
effort has one, `--umbrella <exact-umbrella-draft>`. Do not pass an
implementation step for specification review. Let the shared model map a
source `design` document to the `design-specification` exchange type.

Do not search documentation folders for nearby work or enumerate live
artifacts. Use only the reviewed document and optional umbrella supplied by
`pw`, plus exact paths returned by `bin/review_exchange.bat`. Never create,
overwrite, rename, or delete protocol artifacts by hand.

## Ordered sequence for specification reviewer work

1. Run `status` with the exact document, optional umbrella, and fixed policy.
   Proceed only when its final JSON reports `request-pending` for the same
   identity and reviewer-owned round.
2. Run one bounded `wait-request` per round with that exact context. Do not add
   a polling loop or reconstruct the request path. Read only the returned
   `paths.request` file after the operation grants access.
3. Validate the complete request and read the full exact reviewed specification.
   Treat current specification text as authoritative and the request as the
   focus for the independent assessment.
4. Write assessment, question verdicts, writer instructions, disposition
   evidence, and any response to human guidance into separate ignored root
   `a.*` UTF-8 files. Record the current document digest and input paths in the
   retained-context manifest described below. Write it before rendering so a
   stopped round keeps recovery evidence; pass it to the renderer only when
   republishing retained findings.
5. Run `bin/spec_review_answer.bat` once with the exact context, round,
   disposition, expected document digest, caller-owned inputs, and two distinct
   ignored root outputs. One output is complete answer content and the other is
   the substantive transcript summary.
6. Run `publish-answer` through `bin/review_exchange.bat`, passing the complete
   answer through `--content-file` and the paired substantive summary through
   `--summary-file`. Do not publish either output independently.
7. When `publish-answer` reports `outcome: published`, remove the single-use
   retained manifest. Keep every protocol artifact under shared-core ownership.
8. When the published disposition is `changes-requested` and the returned state
   is `answer-pending`, immediately run the next bounded `wait-request` in this
   same reviewer session. Do not report the round as finished, return control
   to the user, or ask for another reviewer invocation first. The wait begins
   while the requestor owns `answer-pending`; it grants no requestor authority
   to the reviewer and simply watches for the replacement request.
9. When that wait returns `found` with `request-pending`, require the same
   exchange identity and the next reviewer-owned round, read only its returned
   `paths.request`, and continue at Step 3. Repeat the assess, publish, and wait
   cycle for every intermediate round.
10. When publication reports `convergence-gate`, stop for the durable human
    choice instead of waiting for another request. Also stop on any terminal
    wait outcome, preserving the shared timeout, escalation, and recovery
    contract.

Do not read the versioned transcript as assessment context. Do not use an old
request summary when it differs from the current specification. Return
`changes-requested` with a precise drift report instead.

Author every heading in the answer and in the transcript summary under the
heading rules in `instructions/review-requestor.md`: one top-level heading per
transcript, unique heading text, well-formed titles. The summary is appended to
a transcript that already holds the earlier rounds, so a bare `## Findings` or
`### Repairs made by the reviewer` collides with the same heading from the round
before. Qualify it with the step and round, or with the exchange where rounds
restart, and never author a `#` heading inside appended content.

## Pending request and reclaim boundary for specification reviewers

A normal invocation starts from `request-pending`. The shared wait validates
the request envelope, human-readable identity, current round, and reviewer
ownership before returning the exact request.

If the active lease expired during this reviewer session while assessment was
in progress, run `status`. When it reports one intact `abandoned-request` for
the same identity, round, and reviewer ownership, call `reclaim` once and
resume the exact round. Do not treat a malformed, interrupted, or escalated
round as reclaimable.

A cold route that first observes `abandoned-request` belongs to
`spec-review-requestor`, which restores `request-pending` before routing back
to the reviewer. Do not reclaim from that cold route. Report the exact state
and requestor handoff without starting another reviewer round.

## Independent assessment for specification reviewers

Read the full exact reviewed specification and validated request. Assess the
current open questions and also identify missing decisions that the writer did
not express as questions. For every relevant question, cover:

- whether it is missing, redundant, unclear, or outside the selected scope;
- whether its options are materially distinct and state relevant consequences;
- whether the recommended answer follows from confirmed requirements and
  implementation constraints;
- the answer the reviewer would choose and the reason for that choice; and
- concrete replacement wording when the available evidence supports it.

Use `changes-requested` whenever substantive work, disagreement, missing
evidence, cross-document correction, or more than wording-only change remains.
Supply concrete writer instructions and requested changes. If the current
document has no open question for a live request, direct the writer to settle
or cancel that inconsistent round.

Use `convergence-recommended` only when every in-scope decision is settled and
no more than wording-only edits remain. Supply the covered wording and
convergence rationale. A convergence recommendation is advisory and never
authorizes consolidation.

When the request includes a literal `Human guidance:` block, address it in a
separate guidance-response input. Guidance informs the assessment but cannot
override identity, safety, current-document authority, or scope.

## Retained context and republication for specification reviewers

Before rendering, calculate SHA-256 over the exact current reviewed-document
bytes. Pass the lowercase digest through `--expected-document-sha256`. Keep a
single ignored root retained manifest with exactly these JSON fields:

- `document_sha256`: the assessed working-tree byte digest;
- `identity`: the exact specification exchange identity;
- `original_round_number`: the positive round that produced the findings; and
- `assessment_input_paths`: the exact absolute POSIX-form caller input paths.

Pass that file through `--retained-manifest-file` whenever retained findings
are rendered or republished. The renderer validates the digest, identity,
round, and input paths before producing either output.

After human recovery starts a fresh round, validate its request and reread the
current document. When the digest and substantive context are unchanged,
reuse the retained findings under the fresh identity. When material drift is
present, update the assessment and manifest before rendering. Never publish a
cached answer carrying a stale round or digest.

Rendering or failed publication leaves the manifest intact. Only after
`publish-answer` reports `outcome: published` may the reviewer remove the
single-use retained manifest. That outcome accompanies exit `0` when the answer
requests changes and exit `3` when the answer reaches the convergence gate,
where the stop is the pending human confirmation rather than a failure. A
failed publication never reports `published` and exits `2`. Do not key
retirement on exit `0` alone: a convergence round always stops with exit `3`,
so that reading would leak the single-use manifest on every convergence.
Other caller-owned assessment files remain available until the calling session
intentionally retires them.

## Stopped-state handling for specification reviewers

Use the shared final JSON outcome without recreating its classifier:

| Observed result | Reviewer action |
| --- | --- |
| `request-pending` | Run the exact bounded wait and assess once. |
| In-session `answer-pending` after publishing `changes-requested` | Stay active in the next bounded `wait-request`; the requestor remains the owner. |
| `convergence-gate` after publication | Stop for the human choice; do not start a post-answer wait. |
| In-session `abandoned-request` | Reclaim the same intact reviewer-owned round once. |
| Cold-route `abandoned-request` | Stop and hand recovery to `spec-review-requestor`. |
| `disabled` | Stop and report that review mode must be restored. |
| `mismatched` | Stop with the exact identity diagnostic. |
| `interrupted` | Stop for human recovery with caller evidence retained. |
| `repair-required` | Stop for shared repair; do not edit artifacts. |
| `escalated` | Stop for human recovery; never reclaim or publish. |
| Any other writer or human-owned state seen on cold entry | Stop and return control to its owning role. |

Timeout, ambiguity, lost ownership, malformed input, and unexpected fatal
results also stop. Do not create a replacement request, start a fresh round,
or turn a diagnostic into authority.

## Reviewer-forbidden operations and actions

The reviewer may call only `status`, `wait-request`, an eligible in-session
`reclaim`, and `publish-answer`. Never call `consume-answer`, `continue`,
`confirm`, `complete`, `cancel`, `resolve`, or `archive` from this role.

Do not edit or consolidate the reviewed specification. Do not answer questions
in place, consume the answer, append transcript content, confirm convergence,
perform the writer's owning workflow, or make a human recovery decision. When
the shared state stops automation, retain caller-owned assessment evidence and
stop for human recovery.
