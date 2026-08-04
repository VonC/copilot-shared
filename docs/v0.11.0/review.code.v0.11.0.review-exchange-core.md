# Code review transcript for v0.11.0

- Exchange: code/code/v0.11.0/review-exchange-core
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-exchange-core.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor - Step 2

- Recorded: 2026-08-04T14:30:30+02:00
- Exchange: code/code/v0.11.0/review-exchange-core
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-exchange-core.md
- Implementation step: 2
- Outcome: request

Step 2, "Implement the persistence adapter and role-neutral templates," is
reported fully implemented.

- Added `tools/review_exchange_store.py` with exact-path, identity-checked
  request and answer publication, short operating-system transition locks,
  consumed-request tombstones, transcript initialization and append repair,
  evidence archives, cleanup operations, and fail-closed recovery behavior.
- Added role-neutral request, answer, specification-transcript, and
  code-transcript templates under `templates/`.
- Added focused persistence and fault-injection tests under
  `tests/unit/tools/test_review_exchange_store/`, including Windows sharing
  denial, the POSIX lock adapter, malformed coordination, stale markers,
  archive conflicts, transient and permanent filesystem failures, and every
  transcript mutation window.
- Updated
  `docs/v0.11.0/plan.v0.11.0.review-exchange-core.validation.md`; its Step 2
  verdict begins exactly `Yes. Step 2 has been fully implemented.` while the
  overall effort remains incomplete because Steps 3 through 5 are pending.
- Preserved the staged user-owned Codex plugin version update and moved two
  unchanged prepare-release test setup paths into fixtures so their measured
  call phases remain below the duration gate without weakening assertions.

Verification evidence: Groundhog completed 1,337 tests with zero failures,
zero warnings, zero expected failures, 100 percent coverage, zero duration
outliers, and zero exclusions. Eleven implementation files are staged, no
commit has been made, and `a.commit` contains five groups covering the plugin
stamp, prepare-release timing, persistence implementation, persistence tests,
and Step 2 validation.

Use `$llm-shared:implementation-check` to independently verify the exact Step 2
completion criteria against the staged changes. Check atomic publication,
durable request consumption, offset-based append repair, fail-closed recovery,
cross-platform lock coverage, DDD/hexagonal boundaries, feature integrity,
bounded-time complexity, and preservation of unrelated staged work. Repair
only missing Step 2 work and amend `a.commit` if needed. Return
`changes-requested` for another implementation round or
`convergence-recommended` for the advisory human commit decision. Do not
commit.

<!-- review-entry-id: request-round-1 -->

## Round 1 by reviewer - Step 2

- Recorded: 2026-08-04T15:12:03+02:00
- Exchange: code/code/v0.11.0/review-exchange-core
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-exchange-core.md
- Implementation step: 2
- Outcome: answer

Step 2 was independently verified with the implementation-check method against
the staged changes, the plan, and the design. The verdict `Yes. Step 2 has
been fully implemented.` is confirmed.

Verified: atomic publication preserves the destination on failure, discards
temporary files on success and failure, and bounds transient sharing denials
to three attempts; answer publication renames the validated request to its
tombstone before the answer becomes visible; transcript initialization is
family-templated and preserves existing transcripts; append repair works only
from the persisted byte offset with truncate-then-append recovery and exact
idempotent recognition of a completed entry; malformed or cross-identity
artifacts fail closed everywhere; both lock adapters are covered; the store
depends only on Step 1 models and paths; all operations stay bounded to the
fixed path set; the unrelated plugin and prepare-release changes are preserved
with assertions intact. The 87 focused review-exchange tests pass and the
store file keeps 100% coverage.

One gap was found and repaired by the reviewer: `publish_atomic` accepted the
transcript as a target with no validation branch, so generic publication could
replace the append-only transcript wholesale. `_validate_content` now rejects
the transcript target fail-closed, a regression assertion covers it, the
validation record's failure-coverage bullet names it, and the fix is staged.

`a.commit` was amended: the feat group gains the rejection bullet, the test
group gains its coverage bullet, and the docs group now also records this
review transcript beside the plan.

Advisory notes without required action: the POSIX `flock` path blocks without
the bounded wait the Windows adapter inherits from `LK_LOCK`, which is
acceptable because the operating system releases the lock on process exit and
transitions are short; a crash between temporary-file preparation and
replacement can leave one `.review-exchange-*.tmp` file beside the transcript,
which is unreachable litter rather than protocol state.

Disposition: convergence-recommended. The staged changes are ready for the
human commit decision. This recommendation is advisory and does not authorize
a commit.

<!-- review-entry-id: answer-round-1 -->

## Round 1 by requestor - Step 3

- Recorded: 2026-08-04T19:46:13+02:00
- Exchange: code/code/v0.11.0/review-exchange-core
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-exchange-core.md
- Implementation step: 3
- Outcome: request

Step 3, "Lifecycle state machine, bounded waits, repair, escalation, and
confirmation," is reported fully implemented.

- Added `ReviewExchangeCore` with start, request and answer publication,
  answer consumption, automated continuation, escalation, confirmation,
  completion, and fresh-round resolution transitions.
- Split pure state classification, exact-path observation, monotonic waiting,
  and durable human transitions into focused production modules while keeping
  every file below the plan's line ceiling.
- Extended transcript append with a backward-compatible `clear_marker`
  option so lifecycle markers stay durable through post-append cleanup and the
  final coordination write.
- Added table, property, lifecycle, confirmation, recovery, wait, and
  fail-closed boundary tests, including injected crash windows and exact
  idempotent repair.
- Recorded the independent implementation-check verdict in
  `docs/v0.11.0/plan.v0.11.0.review-exchange-core.validation.md`; its Step 3
  status begins exactly `Yes. Step 3 has been fully implemented.`.
- Prepared `a.commit` with three groups covering the lifecycle engine, focused
  tests, and trailing validation and review documentation. No commit has been
  made.

Verification evidence: the final Groundhog walk exercised 1,398 tests with
zero failures, zero warnings, zero expected failures, 100 percent coverage,
zero duration outliers, zero exclusions, and `exit=0`. The generated-shape
property's measured call phase was reduced from 5.58 seconds to 0.70 seconds
without removing assertions; formerly probabilistic defensive branches now
have deterministic tests.

Use `$llm-shared:implementation-check` to independently verify the exact Step
3 completion criteria against all staged changes. Check the observable state
table, identity-first fail-closed behavior, marker-first transition ordering,
request and answer repair, the single monotonic wait deadline, absence of lease
renewal during polling, no-progress and clarification escalation, retained
convergence evidence, durable owning-action authorization replay, fresh-round
resolution, DDD/hexagonal boundaries, fixed-path complexity, and feature
integrity. Repair only missing Step 3 work and amend `a.commit` if needed.
Return `changes-requested` for another implementation round or
`convergence-recommended` for the advisory human commit decision. Do not
commit.

<!-- review-entry-id: request-step-3-round-1 -->

## Round 1 by reviewer - Step 3

- Recorded: 2026-08-04T20:26:51+02:00
- Exchange: code/code/v0.11.0/review-exchange-core
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-exchange-core.md
- Implementation step: 3
- Outcome: answer

Step 3 was independently verified with the implementation-check method against
the staged changes, the plan, and the design. The verdict `Yes. Step 3 has
been fully implemented.` is confirmed after two reviewer repairs.

Verified: the classifier reproduces the complete design state table with
marker overlays, envelope-authoritative convergence recovery, orphan-evidence
rows, and a fail-closed catch-all; every transcript-appending transition is
marker-first with a persisted pre-append offset and idempotent repair; answer
publication resumes from request, tombstone, or visible-answer evidence and
never re-asks a human; no-progress, clarification, cancellation, escalation
idempotence, owning-action replay, and fresh-round resolution follow the
consolidated decisions; waiting uses one monotonic deadline, never renews a
lease, and reports progress in process; module boundaries stay inward-facing
and every production file is below the 650-line ceiling.

Two gaps were found and repaired by the reviewer, both staged:

1. The bounded wait aborted with `repair-required` whenever a poll observed a
   repair state, so an unlocked poll landing inside the counterpart's healthy
   in-flight publication ended the wait prematurely. The wait now polls
   through the counterpart's own publication marker and reserves
   `repair-required` for foreign markers. A deterministic regression test
   drives the in-flight window through the injected sleeper hook.
2. The step-qualified round headings amended into the design and this
   transcript were not implemented in `_render_transcript_entry`, so future
   core-written entries would have regressed `MD024`. The renderer now appends
   ` - Step <identifier>` when the context carries an implementation step, and
   the store test pins the qualified heading.

The validation record documents both repairs, `a.commit` gained matching feat
and test bullets plus the modified store-test staging line, and all 149
focused review-exchange tests pass with every review-exchange module at 100%
coverage after the fixes.

Disposition: convergence-recommended. The staged changes are ready for the
human commit decision. This recommendation is advisory and does not authorize
a commit.

<!-- review-entry-id: answer-round-1-step-3 -->
