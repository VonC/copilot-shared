# Independent review mode contract

<img src="../assets/logo-llm-shared-transparent.png" alt="llm-shared logo" width="200" align="right">

<!-- markdownlint-disable MD013 -->

This reference defines the observable marker, identity, artifact, state,
operation, result, and adapter contract for the marker-gated two-agent
exchange. Use the tutorials and how-to guides for procedures.

## Invocation model

Normal journeys start through `pw` and the appropriate writing or
implementation skill. Full launchers are for reference, recovery, and direct
reviewer operation. Every operation returns one final result; follow that
result instead of discovering nearby files.

Automatic intermediate exchange uses reciprocal bounded waits. The requestor
runs `wait-answer` after `publish-request`. A reviewer that publishes
`changes-requested` immediately runs `wait-request` in the same invocation and
remains there while the requestor owns `answer-pending`. After the requestor
consumes the answer, continues the round, and publishes the replacement, that
wait returns the next `request-pending` artifact and reviewer assessment resumes.
Convergence does not start another reviewer wait; it transfers the exchange to
the human gate.

The canonical [shared requestor instruction](../../instructions/review-requestor.md),
[specification reviewer instruction](../../instructions/spec-reviewer.md), and
[code reviewer instruction](../../instructions/code-reviewer.md) remain
authoritative for agent policy. This page states their user-visible contract in
reference form and does not replace those instructions.

When `bin/review_exchange.bat` runs from another repository's Git root, that
current root overrides an unrelated inherited `PRJ_DIR`. The launcher also
places llm-shared first on `PYTHONPATH`, so a consuming repository's own
`tools` package cannot replace the shared protocol modules.

## Marker and exchange identity

The project-root `a.review-mode` file opts later workflow entry into independent
review mode. An empty file selects the default wait. One line of the form
`wait_timeout_seconds=<positive integer>` selects another bounded wait. An
absent marker produces `state: disabled`; invalid marker content produces the
fatal result described below.

The default wait itself comes from a `.review-exchange.ini` file, read in this
order and stopping at the first usable value:

| Source | Wins over | On invalid content |
| --- | --- | --- |
| `wait_timeout_seconds=` in the project-root `a.review-mode` | everything | fatal |
| `.review-exchange.ini` at the reviewed repository root | the shipped file | ignored |
| `.review-exchange.ini` shipped with llm-shared, currently 10,800 seconds (three hours) | nothing | ignored |

The two treatments differ on purpose. A marker override was written for that
exchange, so a mistake in it must stop the run. A settings file may belong to a
repository that never meant to configure a review, so an unreadable file, a
missing section or key, or a value that is not a positive integer is ignored and
the next source applies. A broken settings file never stops a review.

Every exchange identity contains:

| Field | Meaning |
| --- | --- |
| `family` | `specification` or `code` |
| `type_token` | Reviewed document type, or `code` for implementation review |
| `version` | Exact `vX.Y.Z` token |
| `slug` | Exact effort slug |
| `implementation_step` | Positive step identifier for code review only |

The command context also carries the exact reviewed document, optional umbrella
draft, convergence signal, another-round label, and owning-workflow label.
Identity and context must agree with every durable envelope.

## Artifact and path contract

Artifact names help with orientation only. The final result's returned `paths`
object selects the files for the next action; do not reconstruct names, search
for a nearby version, or edit protocol artifacts by hand.

| Kind | Lifetime | Naming grammar or source |
| --- | --- | --- |
| Request | Transient | `a.review-requested.<type>.<version>.<slug>.md` |
| Answer | Transient | `a.review-answer.<type>.<version>.<slug>.md` |
| Coordination | Durable while live | `a.review-active.<family>.<type>.<version>.<slug>.md` |
| Consumed request tombstone | Transient while needed | `a.review-consumed.<family>.<type>.<version>.<slug>.md` |
| Transition lock | Process-local coordination | `a.review-lock.<family>.<type>.<version>.<slug>.lock` |
| Transcript | Versioned durable evidence | `review.<type>.<version>.<slug>.md` beside the reviewed document |
| Recovery archive | Ignored durable evidence | `a.review-archive.<family>.<type>.<version>.<slug>.<timestamp>.<kind>.md` |
| Code evidence manifest | Ignored reviewer evidence | `a.code-review-evidence.<version>.<slug>.step-<step>.json` |

Requests and answers are renderer-owned envelopes. Coordination and tombstones
make transitions recoverable. Transcript entries are append-only evidence.
Code reviewers retire their ignored evidence manifest after answer publication.

Renderer-owned section headings end with `(round N)`. Headings inside authored
assessment, change, response, and guidance blocks are nested below their parent
section, retain their relative depth, and receive the round identity as their
final suffix. Headings inside fenced examples remain literal. Human guidance is
rendered as a separate nested block below its generated label; publication
checks that canonical form while still accepting exact legacy guidance from an
older round. Callers supply section content and never rewrite renderer-owned
headings in a request, answer, or transcript.

## State matrix

The first fifteen rows come from `ArtifactState`. `disabled` is the
launcher-only absent-marker result. `fatal` is the stable exit-2 payload state.
Each row names the actor who owns the next decision or the recorded actor when
ownership depends on durable coordination.

| State | Lifecycle group | Owner | Next action |
| --- | --- | --- | --- |
| `idle` | Not yet started | requestor | Start a new round |
| `round-in-progress` | Active exchange | requestor | Author and publish the request |
| `request-pending` | Active exchange | reviewer | Assess the request and publish an answer |
| `answer-publication-in-progress` | Interrupted publication | reviewer | Retry the recorded answer publication |
| `transcript-repair-pending` | Interrupted transcript append | recorded actor | Retry the recorded append or repair the eligible request entry |
| `answer-pending` | Active exchange | requestor | Consume changes or present convergence to the human |
| `convergence-gate` | Human gate | human | Choose the registered another-round or owning-workflow label |
| `owning-action-pending` | Authorized continuation | requestor | Perform the authorized consolidation or commit, then complete |
| `escalated` | Stopped exchange | human | Choose forced reclaim, resolve, archive, or cancellation as applicable |
| `abandoned-mid-round` | Expired lease without counterpart artifact | recorded actor or human | Reclaim the round, or human-close it with forced completion |
| `interrupted-answer-publication` | Interrupted publication | reviewer | Resume the recorded publication transition |
| `interrupted-transcript-append` | Interrupted transcript append | recorded actor | Retry the recorded transcript transition |
| `abandoned-request` | Expired request lease | reviewer | Reclaim the intact request and continue assessment |
| `abandoned-answer` | Expired answer lease | requestor | Reclaim the intact answer and continue response handling |
| `inconsistent` | Invalid artifact shape | human | Stop automation and resolve or archive authoritative evidence |
| `disabled` | Not yet started | caller | Create a valid marker before starting independent review |
| `fatal` | Invalid input or refused operation | caller | Correct the input and re-run; payload has null `identity`, empty `paths`, null round, and `fatal-input` outcome |

The `answer-pending` owner remains the requestor even while the reviewer has an
active post-publication `wait-request`. The wait observes the state; it does not
grant answer consumption, round continuation, or any writer-owned action to the
reviewer.

## Operation summary

All commands enter through `bin/review_exchange.bat`. The caller supplies the
same exact context on every invocation.

| Operation | Actor and precondition | Successful effect and outcome |
| --- | --- | --- |
| `activate` | entering requestor or reviewer; valid marker and ignored paths | Validate the fixed path set; `activated` |
| `status` | any caller | Observe current state; `observed`, or `disabled` without the marker |
| `start` | requestor; idle exchange | Open round 1; `started` |
| `continue` | requestor; consumed intermediate answer | Advance to the next round; `continued` |
| `publish-request` | requestor; round in progress | Store request and append transcript; `published` |
| `wait-request` | reviewer; bounded entry wait or post-`changes-requested` wait | Return the next exact request as `found`, or `timed-out`, `abandoned`, `escalated`, `inconsistent`, or `repair-required` |
| `publish-answer` | reviewer; request pending | Consume request, expose answer, and append transcript; `published` |
| `wait-answer` | requestor; bounded wait | Return the same wait outcomes as `wait-request` |
| `consume-answer` | requestor; non-converged answer | Record response assessment; `consumed` |
| `reclaim` | expected actor; intact lease-expired round | Renew the same round; `reclaimed` |
| `reclaim --force` | human-authorized caller; intact escalated artifacts | Resume the same round and append the decision; `force-reclaimed` |
| `repair-request-transcript` | requestor; eligible final legacy request entry | Replace only that final entry; `repaired` |
| `escalate` | owning automated role; automation must stop | Preserve authored reason; `escalated` |
| `confirm` | human at convergence | Return `another-round` or `continue-owning-workflow` |
| `cancel` | human at convergence | End the exchange with authored evidence; `cancelled` |
| `complete` | requestor; authorized owning action succeeded | Remove live coordination; `completed` |
| `complete --force` | human-authorized caller; intact artifact-free abandonment | Append the close decision and remove coordination; `force-completed` |
| `resolve` | human-authorized caller; stopped authoritative evidence | Clear stopped artifacts and start a fresh round; `resolved` |
| `archive` | human-authorized caller; stopped authoritative evidence | Archive stopped artifacts and start a fresh round; `archived` |

## Operation outcome snapshot

Operation outcomes are the one contract column without a single typed model.
This v0.11.0 snapshot is pinned from plain `OperationResult` construction and
conditional `OperationResult` construction. It covers all `WaitOutcome` values
and both `ConfirmationOutcome` values, plus the CLI fatal payload. Later
launcher changes must update this table deliberately; this effort does not add
AST drift tooling.

| Outcome | Source shape |
| --- | --- |
| `disabled` | Plain operation result |
| `activated` | Plain operation result |
| `observed` | Plain operation result |
| `started` | Plain operation result |
| `continued` | Plain operation result |
| `reclaimed` | Plain operation result |
| `force-reclaimed` | Plain operation result |
| `completed` | Conditional operation result |
| `force-completed` | Conditional operation result |
| `published` | Plain operation result |
| `repaired` | Plain operation result |
| `found` | Wait outcome |
| `timed-out` | Wait outcome |
| `abandoned` | Wait outcome |
| `escalated` | Wait outcome or plain operation result |
| `inconsistent` | Wait outcome |
| `repair-required` | Wait outcome |
| `consumed` | Plain operation result |
| `cancelled` | Plain operation result |
| `archived` | Conditional operation result |
| `resolved` | Conditional operation result |
| `another-round` | Confirmation outcome |
| `continue-owning-workflow` | Confirmation outcome |
| `fatal-input` | CLI fatal payload |

## Final result contract

Each invocation writes one final JSON object on standard output. During a wait,
standard error is progress only. The returned `paths` object is authoritative
for artifact access; a caller must not infer a path from the identity grammar.

The success payload always has seven fields:

| Field | Meaning |
| --- | --- |
| `diagnostic` | Human-readable state or failure detail |
| `identity` | Exact family, type, version, and slug, except null on fatal input |
| `operation` | Requested CLI operation |
| `outcome` | One value from the reviewed snapshot |
| `paths` | Six fixed path keys, except an empty object on fatal input |
| `round` | Current positive round, or null when no round exists |
| `state` | One value from the state matrix |

The six success-path keys are:

| Key | Artifact |
| --- | --- |
| `answer` | Current reviewer answer |
| `coordination` | Durable live exchange record |
| `request` | Current request |
| `tombstone` | Consumed request evidence |
| `transcript` | Versioned append-only review record |
| `transition_lock` | Transition lock |

Additional fields are conditional. `exchange_occurrence` appears for a pending
request, `owning_action_authorized` appears after human confirmation, and some
operations report removed or archived paths.

- Exit `0` means the operation completed and the result grants its reported
  next action.
- Exit `3` is an expected stop such as disabled mode, a bounded wait result,
  recovery state, convergence, or pending authorized work.
- Exit `2` reports invalid input or an unexpected fatal error. Correct the
  input; do not open or edit an artifact from the empty fatal `paths` object.

Specification convergence presents `Consolidate` and
`Revise and review again`. Code convergence presents `Commit` and
`Rework and review again`. A reviewer recommendation is advisory; only the
registered human choice can authorize consolidation or commit.

## Host adapter matrix

Host adapters contain discovery metadata and delegate to canonical root
instructions. They do not copy policy bodies.

| Host | Wrapper location | Prefix | Review wrappers or gap | Delegation boundary |
| --- | --- | --- | --- | --- |
| Codex | `.agents/llm-shared/skills/` | `$` | `review-requestor`, both family requestors, and both reviewers | Each `SKILL.md` reads the canonical root instruction |
| Claude Code | `.claude/skills/` | `/` | shared `review-requestor` is absent; use the existing family-specific requestor or reviewer | Each family `SKILL.md` reads the canonical root instruction |
| Antigravity | `.agent/workflows/` | `/` | `review-requestor`, both family requestors, and both reviewers | Each workflow locates and reads the canonical root instruction |

The missing Claude shared wrapper is recorded rather than hidden. Adding host
wrappers is outside this documentation effort.

## Focused procedures and policy owners

Use these task pages instead of deriving a procedure from the tables:

- [Activate or deactivate independent review mode](../how-to/enable-independent-review-mode.md)
- [Run specification review](../how-to/run-specification-review.md)
- [Run implementation code review](../how-to/run-implementation-code-review.md)
- [Read results and continue authorized work](../how-to/read-independent-review-results-and-continue.md)
- [Recover an independent review](../how-to/recover-an-independent-review.md)

The shared requestor instruction owns coordination and human recovery policy.
The family requestor instructions own writer-side specialization. The
specification and code reviewer instructions own independent assessment and
answer publication. Launchers and typed models remain authoritative for
machine-readable state and result shapes.

## Shipped sources

- [Review exchange models](../../tools/review_exchange_models.py)
- [Review exchange CLI](../../tools/review_exchange_cli.py)
- [Artifact path derivation](../../tools/review_exchange_paths.py)
- [Specification requestor instruction](../../instructions/spec-review-requestor.md)
- [Code requestor instruction](../../instructions/code-review-requestor.md)
- [Review request template](../../templates/review-request.template.md)
- [Review answer template](../../templates/review-answer.template.md)

Related: [pw launcher](pw-launcher.md),
[artifact files](artifact-files.md),
[aliases and launchers](aliases-and-launchers.md), and
[document templates](templates.md).
