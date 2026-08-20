# Run an implementation code review

<img src="../assets/logo-llm-shared-transparent.png" alt="llm-shared logo" width="200" align="right">

<!-- markdownlint-disable MD013 -->

## Invocation model

Use this guide after selecting one implementation-plan step. The requestor owns
the staged subject and `a.commit`; the independent reviewer assesses immutable
evidence and may leave attributable repairs staged; the human owns commit.

Do not reconstruct protocol filenames or edit protocol artifacts. Read the one
final JSON result and use its `paths` member.

## Start an implementation code review

1. Activate the repository with [the opt-in guide](enable-independent-review-mode.md).
2. In the requestor agent session, start the ordinary implementation chain:

   ```text
   $llm-shared:implement-step on docs/v1.4.0/plan.v1.4.0.route-warnings.md step 2
   ```

3. Let the chain implement, validate, and group the step. After `a.commit` is
   prepared, `pw` routes to the code-review requestor and publishes immutable
   index and validation evidence.
4. In a separate reviewer agent session, run:

   ```text
   $llm-shared:code-reviewer
   ```

5. Return to the requestor after the bounded wait. Follow `paths.answer`, assess
   staged repairs, update writer-owned records, and publish a replacement round
   when the answer requests changes.

Stop when the requestor presents `Commit` and `Rework and review again`. Exit
`3` and a commit-ready recommendation do not authorize a commit.

## Resume an implementation code review

1. Open the same repository in the requestor agent session.
2. Run `$llm-shared:code-review-requestor on <plan-path> step <n>` with the exact
   repository-relative plan and step.
3. Follow the final JSON `state`, `round`, and `paths`. A persisted
   `owning-action-pending` state means the human already authorized the commit;
   do not ask again.
4. Keep `a.commit` aligned with the staged paths after accepted repairs. Never
   commit through private Git commands.
5. Stop on escalation, inconsistent evidence, or interrupted transition and use
   [the recovery guide](recover-an-independent-review.md).

The canonical [code-review requestor](../../instructions/code-review-requestor.md)
and [code reviewer](../../instructions/code-reviewer.md) instructions remain
authoritative for agent policy.

For the final result contract, see
[read review results and continue](read-independent-review-results-and-continue.md).
