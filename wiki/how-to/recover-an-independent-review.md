# Recover an independent review

<img src="../assets/logo-llm-shared-transparent.png" alt="llm-shared logo" width="200" align="right">

<!-- markdownlint-disable MD013 -->

## Invocation model

Use direct launchers only after the ordinary skill route reports an expired or
stopped state. Begin with `status`, read its final JSON, and copy the exact
family, document, optional umbrella, step, and policy context into the chosen
operation.

Do not reconstruct protocol filenames or edit protocol artifacts. Follow the
returned `paths` and stop on exit `2`.

## Continue an active code review in a new session

Use ownership pickup when a valid code-review exchange is still active but the
new requestor session does not hold the old ownership token. The durable record
stores only a digest, so the old plaintext token cannot and should not be
recovered.

1. Start the new agent session at the reviewed repository root.
2. Name the exact implementation plan, step, and umbrella when one exists.
3. Give the human authorization in one prompt. At convergence, use:

   ```text
   Commit selected. This is a new session; force requestor ownership pickup,
   record Commit, then continue the authorized commit process.
   ```

4. The requestor runs `status` with the exact context and then runs `pickup`
   before its first mutation. The successful result returns a new ownership
   generation and token for that session.

   ```powershell
   & "<LLM_SHARED_DIR>\bin\review_exchange.bat" pickup <exact-code-review-context-flags>
   ```

5. At `convergence-gate`, the requestor supplies that capability to `confirm`
   with the exact `Commit` label. At `owning-action-pending`, it supplies the
   capability to the remaining authorized mutations without asking again.

Pickup advances the generation and fences the old session; it does not reset
the review. Do not use `reclaim`, `resolve`, or `archive` just because the agent
session changed. This exact-context pickup is the Step 3 corrective path. Step
4's status schema and migration work does not restore session secrets. Step 5's
role-resolved resume interface will generalize this journey.

## Reclaim an expired live exchange

Use ordinary reclaim only for an intact live round whose lease expired while
the expected actor was still working.

1. Run status with the exact context and confirm the final JSON state is
   `abandoned-request`, `abandoned-answer`, or `abandoned-mid-round`.
2. Run:

   ```bat
   bin\review_exchange.bat reclaim <family-and-context-flags>
   ```

3. Read the final JSON `state`, `round`, and `paths`. Reclaim renews the same
   round without changing request, answer, or transcript content.
4. Resume the actor named by the returned state. Reclaim is idempotent while the
   round is live.

Do not use ordinary reclaim for an escalated, inconsistent, or interrupted
exchange. A timeout can lead to an abandoned lease, but it does not grant human
recovery authority by itself.

## Recover a stopped exchange

Stop automation for no-progress, explicit disagreement, inconsistent artifacts,
an interrupted transition, or escalation. Preserve the diagnostic and let the
human identify the authoritative evidence before selecting a command below.

## Human decision required

> **Authority:** only the human may choose a forced resume, forced close,
> resolution, or archive. **Precondition:** inspect the final JSON state and the
> artifact shape named by `paths`, then write the decision to an ignored root
> summary file. **Evidence effect:** every command appends or preserves the
> authored decision as described below; none may be substituted for manual
> artifact editing.

To resume an escalated exchange whose request, answer, and transcript remain
intact, preserving the same round and returning ownership from artifact shape:

```bat
bin\review_exchange.bat reclaim --force --summary-file a.human-reclaim.md <family-and-context-flags>
```

To close an intact, artifact-free `abandoned-mid-round` exchange without
manufacturing convergence or owning authorization:

```bat
bin\review_exchange.bat complete --force --summary-file a.human-close.md <family-and-context-flags>
```

To clear an escalated, inconsistent, or interrupted exchange and start a fresh
round from the human's authoritative decision:

```bat
bin\review_exchange.bat resolve --summary-file a.human-resolution.md <family-and-context-flags>
```

Use `archive --summary-file` instead of `resolve` when stopped evidence must be
preserved under derived archive names. Never resume the interrupted transition
itself.

The canonical [shared requestor instruction](../../instructions/review-requestor.md)
remains authoritative for exact preconditions and agent stopping policy.
