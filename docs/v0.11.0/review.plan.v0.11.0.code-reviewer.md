# Specification review transcript for v0.11.0

- Exchange: specification/plan/v0.11.0/code-reviewer
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-reviewer.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor

- Recorded: 2026-08-14T22:27:32+02:00
- Exchange: specification/plan/v0.11.0/code-reviewer
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Outcome: request

### Review identity for plan code-reviewer round 1

Umbrella draft: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
Reviewed specification: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-reviewer.md
Review round: 1

### Requestor assessment for plan code-reviewer round 1

The implementation plan translates the consolidated design into five tests-first slices: immutable request evidence, assessment primitives, paired answer rendering, reviewer routing and instruction, and end-to-end acceptance. It names every production, adapter, launcher, template, and test surface, records current physical line counts and repository risk bands, uses `ghog single` and `ghog day`, and keeps the validation skeleton aligned with the current five steps.

Six implementation-detail questions are open. Q01 selects a thin CLI and launcher over the evidence library. Q02 selects a pure `CommitBlock` plus staged-path validator shared by review and batch execution. Q03 selects a canonical JSON evidence block inside authored request content. Q04 makes route actor ownership an explicit typed field. Q05 recommends splitting the current assessment-primitives step so the completed batch/Git and `implementation-check` surfaces receive separate tests and implementation checks. Q06 uses real temporary Git repositories through public Python APIs plus one smoke test per launcher.

Each question has three materially distinct options, explicit pros and cons, a recommendation, and an answer. No question reopens the requirement or design. The reviewer should check whether any implementation surface, step-order dependency, line-budget constraint, or gate-test detail is still missing, and whether the validation skeleton must be expanded to six steps under E2.

### Change summary for plan code-reviewer round 1

Initial plan review. The new plan and validation skeleton were written from the consolidated feature request and design. The requirement and design also received the write-plans workflow's exact-path and file-IO clarification. No preceding plan-review round exists.

### Writer response for plan code-reviewer round 1

Writer response: The writer recommends A2, B2, C2, D2, E2, and F2. These choices give the reviewer a stable evidence launcher, keep commit validation pure, make request evidence self-contained without changing the shared envelope, record actor ownership once, split extensions to completed surfaces into focused steps, and test real Git behavior without repeating every case through batch launchers. The writer welcomes corrections to file ownership, step order, line budgets, test seams, and validation-plan alignment.

### Reviewer focus for plan code-reviewer round 1

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-1 -->

## Round 1 by reviewer

- Recorded: 2026-08-14T22:38:59+02:00
- Exchange: specification/plan/v0.11.0/code-reviewer
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Outcome: answer

### Reviewer assessment for plan code-reviewer round 1

This is an accurate plan. I checked every line count in the confirmed-facts
section against the tree and all fourteen match exactly, including the two
risk-band files that drive the "add a new test file instead of growing this one"
guidance: `tools/prompt_workflow_skill.py` at 583 and
`test_prompt_workflow_skill_tdd.py` at 614. The four host adapters listed for
Step 4 match what the completed `code-review-requestor` and `spec-reviewer`
roles actually carry, including the absence of a `.github/skills` entry for
review roles. `bin/code_review_request.bat` wraps `tools/code_review_request.py`
directly rather than a separate CLI module, so Step 1's file list needs no extra
entry for the command surface. That section is usually where a plan drifts from
the tree, and this one does not.

The five slices are correctly ordered: request evidence before assessment
primitives, primitives before the renderer, the renderer before the instruction
that calls it, acceptance last. Each step carries tests first, exact file lists
with create-or-update labels, `rg` completion checks, line budgets against the
650 ceiling with split guidance, and a `ghog single` line followed by `ghog
day`. The complexity bound and the file-IO clarification restate the design's
no-enumeration and read-once boundaries as checkable implementation constraints.

I agree with all six answers: A2, B2, C2, D2, E2, and F2.

Two things need work before implementation starts.

The first is that four of the six answers change the plan body, and the body
still describes the pre-answer shape. E2 is the largest: it splits Step 2 and
renumbers to six steps, so the summary line, the per-step goals, the scope
anchors, and the validation skeleton all still say five. A2 adds two production
files that appear in no file list, no new-surfaces list, no line budget, and no
`ghog single` line. D2 changes the `CodeReviewRoute` dataclass, which Step 4
does not mention. C2 needs a named heading for its JSON block so the reviewer
can tell it from the envelope's `## JSON` section. Consolidation has to
propagate all four, and the answer to the writer's own question is yes: the
validation plan must grow to six steps and be renumbered in the same pass,
because `implementation-check` reads it per step.

The second is a decision the plan does not make, and it is the one that decides
whether a design guarantee survives implementation. Step 2 puts reviewer
assessment mode in `instructions/implementation-check.md` and then says its test
leaf will prove that the mode "detects pass-path and fail-path umbrella
mutation". A Markdown instruction cannot be executed by a test; only its text
can be asserted. If the digest is captured and compared by an LLM following
prose, the design chose option C2 over C1 for a mechanism it does not get: C1
was rejected precisely because a prose boundary is advisory. The same question
applies to the validation state comparison that K2 requires and to the
reviewer-only patch attribution that B2 requires. The plan needs to say which
surface performs each machine check, and with A2 accepted there is an obvious
home for them.

Nothing else is missing. The test-tree snapshot preserves the existing packages,
the new leaves follow the one-leaf-per-surface convention, Step 5 names the
sixteen design acceptance cases and the eight requirement criteria, and the
deferred list matches the design's ownership boundary.

### Question verdicts for plan code-reviewer round 1

Six questions, six confirmed answers. Each asks an implementation-detail
question rather than reopening the requirement or design, and each option set is
materially distinct.

- **Q01, evidence helper exposure: A2 confirmed.** The reviewer is an LLM
  workflow that already drives `bin/review_exchange.bat` and will drive the new
  answer launcher, so evidence and manifest work needs the same non-interactive
  boundary. A1 leaves the workflow composing Git commands with no tested entry
  point, and A3 puts attribution and recovery rules back into prose, which is
  what the design spent two rounds removing. My answer is A2, with the operation
  set settled by the new question below.
- **Q02, `a.commit` validator input: B2 confirmed.** A pure function over parsed
  `CommitBlock` values and an explicit staged-path sequence matches how
  `parse_clipboard_content` already returns typed blocks and keeps the rules
  testable without Git or subprocess state. B1 hides IO inside validation and B3
  is the subprocess coupling the design rejected as option G2. The signature in
  the answer, `validate_commit_plan(blocks, staged_paths)`, is the right
  boundary. My answer is B2.
- **Q03, request evidence encoding: C2 confirmed, one detail to name.** A
  canonical JSON block inside authored content keeps the evidence immutable with
  the request without widening the shared envelope schema, and C3 would add the
  second artifact lifecycle the design avoided for the manifest. The option's
  own con is the real risk: the request already contains a `## JSON` section
  that the shared envelope parser reads. Name the evidence block's heading in
  the answer so the two are never ambiguous, for example:

  > The evidence block is rendered under its own `## Code review evidence`
  > heading as one fenced JSON object, so the shared envelope parser continues
  > to read only the `## JSON` section, and Step 1 tests assert that a request
  > carrying both blocks round-trips through the envelope parser unchanged.

- **Q04, route actor representation: D2 confirmed.** An explicit typed actor
  resolved once from the classified state makes the critical partition testable
  at resolution time and keeps ordinary and forced routing on one result. D1
  makes every renderer repeat the partition, and D3 duplicates context handling
  for a small module. Add the `CodeReviewRoute` change to Step 4's file and
  behavior list, since that step currently names only `command_for_route`. My
  answer is D2.
- **Q05, step granularity: E2 confirmed, and yes, the skeleton must grow.** The
  design review's plan-phase note asked exactly this: order extensions to
  completed surfaces so each lands with the tests covering the behavior it
  extends. Current Step 2 touches three of them at once (Git and batch-commit
  modules, the batch workflow, and a canonical instruction), which is one
  implementation check spanning three unrelated failure modes. E3 would delay a
  required primitive and mix canonical check behavior with host adapters. Under
  E2 the renumbering must keep reviewer-mode `implementation-check` before the
  routing and instruction step, since the canonical instruction calls it. The
  validation plan must be renumbered to the same six steps in the same pass,
  because `implementation-check` reads it per step and a five-step skeleton
  would mislabel every later step. My answer is E2.
- **Q06, acceptance seam: F2 confirmed.** Real temporary repositories are
  required for index trees, blob baselines, and hunk attribution, and F3 cannot
  prove any of them. F1 turns every case into a slow platform-bound subprocess
  run for no extra state coverage. One smoke test per launcher covers argument
  drift. Note that A2 adds a third launcher, so the smoke set is
  `bin/code_review_answer.bat`, `bin/code_review_evidence.bat`, and the existing
  `bin/code_review_request.bat` path touched by Step 1. My answer is F2.

One question is missing.

- **Q07: which operations does the evidence boundary expose, and which machine
  checks run there rather than in prose?** Step 2 assigns reviewer assessment
  mode to `instructions/implementation-check.md` and then claims its tests will
  prove the mode detects umbrella mutation on both the pass and fail paths. Only
  the instruction text can be asserted by a test; the detection itself happens
  wherever the digest is captured and compared. The same holds for the K2 state
  comparison around validation and the B2 staged-path collection. Options worth
  putting to the writer: G1, keep `code_review_evidence.py` to trees, blobs, and
  manifests and let the instruction perform the digest and state comparisons in
  prose, which is cheapest and reproduces the advisory boundary the design
  rejected; G2, expose one typed operation set covering index-tree capture,
  pre-repair blob recording, reviewer-only patch attribution, umbrella digest
  capture and compare, validation state capture and compare, and manifest write,
  read, and retire, with the instruction calling each through
  `bin/code_review_evidence.bat` and the tests asserting the instruction names
  those calls; G3, split the checks across `code_review_evidence.py` and a
  second reviewer-mode helper beside `implementation-check`. My recommendation
  is G2: it is the only option that keeps the design's enforcement claims
  machine-checkable, it gives the instruction tests something real to assert
  (that each boundary is delegated to a named command rather than described),
  and it puts every check behind the boundary A2 already accepted. G3 spreads
  one contract across two modules for no gain.

Two smaller corrections.

- **Anchor the Step 2 completion check on symbols rather than prose.** The
  current check searches for `umbrella digest` and `reviewer assessment mode`,
  phrases that live in documentation rather than in code, so the check passes on
  the instruction alone. Search for the identifier the implementation will use,
  for example `umbrella_digest`, together with `interactive=False`, so the
  criterion proves the code exists and not only that the instruction mentions
  it.
- **Carry A2's two files into every place Step 2 accounts for surfaces**: the
  new-production-surfaces list, the Step 2 file list, the line-budget checkpoint
  with an advisory ceiling, the `ghog single` line, and one launcher smoke test
  under F2.

### Requested changes for plan code-reviewer round 1

Requested changes: The plan is accurate and correctly ordered, its confirmed facts match the tree
exactly, and all six answers stand. Six edits remain, one of which is a new
decision.

- Add Q07 on the evidence-boundary operation set, recommended option G2, so the
  umbrella digest, validation state comparison, and patch attribution run behind
  a tested command rather than in instruction prose. A test can assert what an
  instruction says, not what it does.
- Split current Step 2 under E2, renumber to six steps everywhere in the body,
  and renumber the validation plan in the same pass. Keep reviewer-mode
  `implementation-check` before the routing and instruction step.
- Add `tools/code_review_evidence_cli.py` and `bin/code_review_evidence.bat`
  from A2 to the new-surfaces list, the step file list, the line budgets, the
  `ghog single` line, and the launcher smoke set.
- Name the `CodeReviewRoute` actor field and its consistency check from D2 in
  the routing step.
- Give the C2 evidence block its own heading, add the envelope round-trip
  assertion, and add the block to the request template.
- Anchor the reviewer-mode completion check on `umbrella_digest` rather than on
  prose phrases that match documentation alone.

### Writer instructions for plan code-reviewer round 1

Apply these changes to `docs/v0.11.0/plan.v0.11.0.code-reviewer.md` and, where
noted, to `docs/v0.11.0/plan.v0.11.0.code-reviewer.validation.md`, then publish
round 2. Do not consolidate. No selected answer changes.

1. Add Q07 through `oqm` on the evidence-boundary operation set, following the
   existing BBQ and options shape, with G2 recommended. This is the one decision
   the plan does not make, and it decides whether the design's umbrella-digest,
   validation-state, and attribution guarantees are executable or prose.
2. Propagate E2 into the body: split current Step 2 into evidence and
   commit-plan validation first, then reviewer-mode `implementation-check`,
   renumber the later steps, and update the summary line, the per-step goals,
   and the scope anchors that still say five. Keep reviewer-mode
   `implementation-check` before the routing and instruction step. Renumber
   `plan.v0.11.0.code-reviewer.validation.md` to the same six steps in the same
   pass: a five-step skeleton would mislabel every step after the split, and
   `implementation-check` reads it per step.
3. Propagate A2: add `tools/code_review_evidence_cli.py` and
   `bin/code_review_evidence.bat` to the new-production-surfaces list, to the
   owning step's file list, to its line-budget checkpoint, and to its `ghog
   single` line, and add one launcher smoke test under F2.
4. Propagate D2: name the `CodeReviewRoute` actor field and its consistency
   check in the routing step's files-and-behavior section, not only
   `command_for_route`.
5. Propagate C2: give the evidence block its own heading, quoted in the
   verdicts, and add the round-trip assertion that a request carrying both JSON
   blocks still parses through the shared envelope unchanged. Add the block to
   `templates/code-review-request.template.md` in the same step.
6. Anchor the reviewer-mode completion check on an implementation identifier
   such as `umbrella_digest` instead of the prose phrases `umbrella digest` and
   `reviewer assessment mode`.

Item 1 is the only new decision. Items 2 to 5 propagate answers you have already
selected into the body an implementer will follow, and item 6 makes one
completion criterion prove code rather than documentation. With these applied,
round 2 can converge.

Nothing in the confirmed-facts section needs correction. I verified all fourteen
line counts, the adapter set, and the launcher wiring against the tree, and they
are exact.

### Final reviewer decision for plan code-reviewer round 1

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-1 -->

## Round 2 by requestor

- Recorded: 2026-08-14T23:05:46+02:00
- Exchange: specification/plan/v0.11.0/code-reviewer
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Outcome: request

### Review identity for plan code-reviewer round 2

Umbrella draft: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
Reviewed specification: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-reviewer.md
Review round: 2

### Requestor assessment for plan code-reviewer round 2

## Writer assessment for plan code-reviewer round 2

The round 1 answer was accepted without disagreement. All six existing answers remain sufficient and selected: A2, B2, C2, D2, E2, and F2. The requested missing implementation decision is now Q07, with G2 recommended and answered.

The plan body now implements those decisions rather than leaving them only in the question section. It has six dependency-ordered steps and the validation skeleton has the same six identifiers. The executable evidence boundary owns index-tree capture, pre-repair blobs, patch attribution, umbrella digest comparison, validation-state comparison, and manifest lifecycle operations. Reviewer-mode implementation-check follows as its own step and delegates machine checks to that boundary.

No additional implementation-plan question is currently known. Round 2 should verify that the new G2 operation set is sufficient, that A2 through F2 reached every affected file list, test list, line budget, and completion check, and that the six-step plan and validation skeleton remain aligned.

### Change summary for plan code-reviewer round 2

## Changes since plan code-reviewer round 1

- Added Q07 with G2 recommended: one typed evidence library, CLI, and launcher own the full capture, comparison, attribution, and retained-manifest operation set.
- Split the former assessment-primitives step into Step 2 executable Git evidence and commit validation, followed by Step 3 reviewer-mode implementation checks; renumbered answers, routing, and acceptance to Steps 4 through 6.
- Rebuilt the validation skeleton with the same six step identifiers and 36 untouched implementation-check placeholders.
- Added `tools/code_review_evidence_cli.py` and `bin/code_review_evidence.bat` to production surfaces, files, line budgets, focused tests, and launcher smoke coverage.
- Defined the authored request evidence under `## Code review evidence` and added the shared-envelope round-trip assertion.
- Added `CodeReviewRoute.actor`, its typed resolution, and actor/state consistency validation to the routing step.
- Anchored reviewer-mode completion on executable identifiers including `umbrella_digest` and `validation_state`.

### Writer response for plan code-reviewer round 2

Writer response: ## Writer response to plan code-reviewer round 1

Accepted all requested changes with no disagreement.

Q07 was added through the managed open-question companion with G2 as the answer. Step 2 now owns the complete executable evidence operation set through `bin/code_review_evidence.bat`; Step 3 owns only the canonical reviewer-mode instruction and tests that it delegates to named commands on both criteria result paths.

The plan and validation skeleton now agree on six steps. A2's CLI and launcher appear in every required accounting location and in the F2 smoke matrix. C2 names `## Code review evidence` and requires a request with both JSON sections to round-trip through the shared envelope parser unchanged. D2 names the typed `CodeReviewRoute.actor` field and its consistency check. The completion check now searches implementation identifiers instead of prose phrases.

### Reviewer focus for plan code-reviewer round 2

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-2 -->

## Round 2 by reviewer

- Recorded: 2026-08-14T23:21:29+02:00
- Exchange: specification/plan/v0.11.0/code-reviewer
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Outcome: answer

### Reviewer assessment for plan code-reviewer round 2

All six round-1 items landed. Q07 is well formed and G2 is answered. The body
now carries six dependency-ordered steps with reviewer-mode
`implementation-check` as Step 3, ahead of the routing step that calls it. The
A2 files reached the new-surfaces list, the Step 2 file list, the line budgets,
the focused test line, and the Step 6 launcher smoke set, which now covers all
three launchers. The C2 evidence block has its own `## Code review evidence`
heading, the round-trip assertion against the shared envelope parser, and the
template in Step 1's file list. D2's actor field, its typed resolution, and its
consistency check are in Step 5. The reviewer-mode completion checks now anchor
on `umbrella_digest`, `validation_state`, and `retire_manifest` rather than on
prose phrases.

The round-1 finding is fully resolved for `implementation-check`. Step 3 now
asserts that the instruction names the evidence launcher's operations on both
criteria paths and explicitly reuses the Step 2 executable tests as the proof
that detection happens, which is the correct division: instruction tests assert
text, behavior tests execute code.

That same division is missing one step away. Step 5 writes
`instructions/code-reviewer.md`, and that instruction is the main caller of the
evidence boundary: it captures the baseline, records blobs, attributes the
reviewer-only patch, compares validation state, and writes and retires the
manifest. The Q07 answer says the canonical instruction should remain a thin
ordered caller, but Step 5 never binds it to the launcher. Its behavior list
names only the ordered sequence, recovery, guidance, and publication, and its
`rg` check looks for routing identifiers in three files without checking that
the instruction delegates anything. If that instruction describes evidence work
in prose, G2's boundary is bypassed by its principal caller, and the plan would
have applied the enforcement pattern to the secondary instruction while leaving
the primary one advisory.

Three wording items also remain, listed in the requested changes. One is a wrong
cross-reference introduced by the split: Step 3 cites design Q07 for validation
side effects, but design Q07 is the `a.commit` interface and design Q08 is
validation side effects.

I agree with all seven answers: A2, B2, C2, D2, E2, F2, and G2.

One limit on this round's evidence. The validation plan is a separate document
that this exchange does not carry, so I did not open it. The six-step alignment,
the matching step identifiers, and the 36 untouched placeholders are the
writer's assertion rather than something I verified. The plan document itself is
consistent with six steps throughout.

### Question verdicts for plan code-reviewer round 2

Seven questions, seven confirmed answers. No option changes and no question is
missing.

- **Q01, evidence helper exposure: A2 confirmed.** The two files now appear
  everywhere the plan accounts for surfaces, and Step 6 smokes all three
  launchers.
- **Q02, validator input: B2 confirmed.** `validate_commit_plan(blocks,
  staged_paths)` is named as the public boundary in Step 2's behavior list and
  in the answer, and the batch workflow calls the same function.
- **Q03, evidence encoding: C2 confirmed.** The distinct heading, the
  derived-from-one-object rule, and the envelope round-trip assertion all
  landed, so the second JSON block can never be confused with the envelope's.
- **Q04, route actor: D2 confirmed.** `CodeReviewActor`, the required
  `CodeReviewRoute.actor` field, the construction-time consistency check, and a
  test that rejects a disagreeing actor and state are in Step 5.
- **Q05, step granularity: E2 confirmed.** Six steps, correctly ordered:
  reviewer-mode `implementation-check` is Step 3, after the evidence boundary it
  delegates to and before the routing step whose instruction calls it.
- **Q06, acceptance seam: F2 confirmed.** Scenario coverage stays on public
  Python entry points over real temporary repositories, with one smoke
  invocation per launcher in a dedicated Step 6 module.
- **Q07, executable evidence operations: G2 confirmed.** This is the answer I
  recommended, and the option text is stronger than my phrasing: G1's con names
  exactly what it would cost, and G3's con names the real risk, which is
  fragmenting one assessment identity across several state models. Step 2 lists
  the full operation set behind `bin/code_review_evidence.bat` and Step 3
  consumes it instead of restating it.

One gap remains, and it is the round-1 finding one step away from where it was
fixed.

- **Bind the canonical reviewer instruction to the evidence and answer
  launchers in Step 5.** Step 3 requires `instructions/implementation-check.md`
  to name `bin/code_review_evidence.bat` operations and anchors its completion
  check on them. Step 5 writes `instructions/code-reviewer.md`, which performs
  far more of the evidence work: baseline capture, blob recording, patch
  attribution, validation-state comparison, and manifest write, read, and
  retire. Nothing in Step 5 requires it to delegate any of that, and its `rg`
  check searches only for routing identifiers. Suggested additions to Step 5.

  Tests first:

  > Assert the canonical reviewer instruction names `bin/code_review_evidence.bat`
  > for baseline capture, pre-repair blobs, patch attribution, validation-state
  > comparison, and manifest write, read, and retire, and
  > `bin/code_review_answer.bat` for paired rendering, rather than describing
  > equivalent Git or filesystem operations.

  Classes and behavior:

  > Canonical instruction: a thin ordered caller that delegates every executable
  > evidence and rendering operation to the accepted launchers and owns only
  > sequence, recovery, guidance, and publication decisions.

  Completion criteria:

  > `rg -n 'code_review_evidence.bat|code_review_answer.bat|review_exchange.bat'
  > instructions/code-reviewer.md` finds the delegated boundary for evidence,
  > rendering, and protocol operations.

  Without this, an implementer can satisfy every Step 5 criterion with an
  instruction that composes Git commands in Markdown, which is option A3 and
  option G1 arriving through the back door after both were rejected.

Three wording items.

- **Step 3 cites the wrong design question.** Its framing reads "Design links:
  Q03 enforceable reviewer mode, Q07 validation side effects". Design Q07 is the
  `a.commit` validation interface; design Q08 is validation side effects. Change
  it to Q08.
- **Step 2's design-link list still carries Q03**, whose instruction work moved
  to Step 3. Keep it only if the intent is the digest mechanism that Step 2 now
  implements, and say so; otherwise drop it. While editing both lines, consider
  writing design references as "design Q0x", since this plan's own questions
  reuse the same numbering and a bare "Q03" is now ambiguous between two
  documents.
- **The test-tree note about a second CLI test module** still says CLI-heavy
  answer tests may add a `test_*_cli_tdd.py` in the same leaf. The evidence leaf
  now has one too, so name both.

### Requested changes for plan code-reviewer round 2

Requested changes: All six round-1 items landed and all seven answers stand, so this round asks for
no option change and no new question. Four edits remain, one of which changes
what gets built.

- Bind the canonical reviewer instruction to the accepted launchers in Step 5:
  add the test that asserts it names the evidence and answer commands, the
  behavior line describing it as a thin ordered caller, and the `rg` check over
  `instructions/code-reviewer.md`. Step 3 already requires this of
  `implementation-check`, while Step 5 writes the instruction that performs most
  of the evidence work and currently requires nothing of it.
- Correct Step 3's design link from Q07 to Q08: design Q07 is the `a.commit`
  interface, design Q08 is validation side effects.
- Resolve Step 2's remaining `Q03` design link, and consider writing design
  references as "design Q0x" now that this plan reuses the same numbering.
- Extend the second-CLI-test-module note to cover the evidence leaf as well as
  the answer leaf.

Please also confirm the validation plan's six step identifiers match this plan
exactly. That document is outside this exchange, so I did not verify it.

### Writer instructions for plan code-reviewer round 2

Apply these four changes to `docs/v0.11.0/plan.v0.11.0.code-reviewer.md`, then
publish round 3. Do not consolidate. No question is added and no answer changes.

1. Add the three quoted additions to Step 5 so the canonical reviewer
   instruction is bound to the accepted launchers: a test that asserts it names
   the evidence and answer commands, a behavior line describing it as a thin
   ordered caller, and an `rg` completion check over
   `instructions/code-reviewer.md`. Step 3 already does this for
   `implementation-check`; Step 5 writes the instruction that performs most of
   the evidence work and currently requires nothing of it.
2. Correct Step 3's design link from Q07 to Q08. Design Q07 is the `a.commit`
   validation interface and design Q08 is validation side effects.
3. Decide Step 2's remaining `Q03` design link: keep it with a phrase naming the
   digest mechanism Step 2 implements, or drop it now that the instruction work
   is Step 3. Consider qualifying both lists as "design Q0x", since this plan's
   own questions now reuse Q01 through Q07.
4. Extend the test-tree note so the second `test_*_cli_tdd.py` convention covers
   the evidence leaf as well as the answer leaf.

Item 1 changes what gets built and verified; items 2 to 4 are corrections.

One thing I could not check. The validation plan is not part of this exchange,
so its six-step alignment, matching identifiers, and untouched placeholders are
your assertion rather than my verification. Before implementation starts, please
confirm that its step identifiers match the six in this plan exactly, since
`implementation-check` reads it per step and a stale identifier would mislabel
every step after the split.

With item 1 applied, round 3 can converge: the seven answers cover the
implementation decisions, the confirmed facts match the tree, the six steps are
correctly ordered, and each step carries its own tests, budgets, and checks.

### Final reviewer decision for plan code-reviewer round 2

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-2 -->

## Round 3 by requestor

- Recorded: 2026-08-14T23:41:22+02:00
- Exchange: specification/plan/v0.11.0/code-reviewer
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Outcome: request

### Review identity for plan code-reviewer round 3

Umbrella draft: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
Reviewed specification: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-reviewer.md
Review round: 3

### Requestor assessment for plan code-reviewer round 3

## Writer assessment for plan code-reviewer round 3

The round 2 answer was accepted without disagreement. All seven answers remain sufficient and selected: A2, B2, C2, D2, E2, F2, and G2. No new question was requested or found.

Step 5 now binds the canonical reviewer instruction to the accepted executable boundaries. Its tests require explicit evidence and answer launcher calls, its behavior describes the instruction as a thin ordered caller, and its completion check verifies evidence, rendering, and exchange launcher names in the canonical file.

The wording corrections are applied: design references are qualified, Step 3 points to design Q08 for validation side effects, Step 2 keeps design Q03 only as the umbrella-digest enforcement mechanism it implements, and the CLI-heavy test note covers both evidence and answer leaves.

The validation plan was independently checked before this request. Its six step numbers and titles exactly match the implementation plan, in order, and it contains 36 untouched implementation-check placeholders.

### Change summary for plan code-reviewer round 3

## Changes since plan code-reviewer round 2

- Added a Step 5 instruction test requiring `bin/code_review_evidence.bat` for baseline, blob, attribution, validation-state, and manifest operations, plus `bin/code_review_answer.bat` for paired rendering.
- Defined the canonical reviewer instruction as a thin ordered caller of the evidence, answer, and shared exchange launchers.
- Added a completion check over `instructions/code-reviewer.md` for all three delegated command boundaries.
- Corrected the Step 3 validation-side-effect reference from design Q07 to design Q08 and qualified numbered design references to distinguish them from plan questions.
- Kept design Q03 in Step 2 specifically for the executable umbrella-digest enforcement mechanism.
- Extended the secondary CLI test-module convention to both evidence and answer test leaves.
- Verified the validation plan has six exactly matching step identifiers and 36 untouched placeholders.

### Writer response for plan code-reviewer round 3

Writer response: ## Writer response to plan code-reviewer round 2

Accepted all four requested changes with no disagreement.

The principal canonical reviewer instruction is now bound to the same enforcement pattern as `implementation-check`: tests assert named launcher calls, executable behavior remains in the Step 2 boundary, and the instruction owns only sequencing and role decisions. The Step 5 completion check covers evidence, answer, and exchange launchers directly.

All three wording items were applied. The separately maintained validation plan was also checked directly: its six ordered identifiers match the plan exactly and all 36 validation fields retain the untouched placeholder.

### Reviewer focus for plan code-reviewer round 3

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-3 -->

## Round 3 by reviewer

- Recorded: 2026-08-14T23:47:03+02:00
- Exchange: specification/plan/v0.11.0/code-reviewer
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Outcome: answer

### Reviewer assessment for plan code-reviewer round 3

All four round-2 items landed exactly. Step 5 now asserts that the canonical
reviewer instruction names `bin/code_review_evidence.bat` for baseline, blobs,
attribution, validation state, and manifest lifecycle and
`bin/code_review_answer.bat` for paired rendering, describes that instruction as
a thin ordered caller that also delegates protocol work to
`bin/review_exchange.bat`, and adds a completion check over
`instructions/code-reviewer.md` for all three boundaries. Step 3 now cites
design Q08 for validation side effects, Step 2 keeps design Q03 with the reason
it belongs there, every design reference is qualified so it cannot be confused
with this plan's own numbering, and the second CLI test module convention covers
both the evidence and answer leaves.

All seven answers stand: A2, B2, C2, D2, E2, F2, and G2.

One gap remains, and it is a step-order question rather than a missing rule.
Step 1 captures the Git index tree at publication and renders it into the
request. Step 2 creates the evidence boundary whose first listed operation is
index-tree capture, and G2 says that operation set belongs behind one typed
library, CLI, and launcher. So the plan currently has one operation with two
owners, in the wrong order: the first consumer runs a step before the boundary
that owns it exists. An implementer following the plan literally would write a
second capture in the request module or compose `git write-tree` in the
requestor instruction, and both are the fragmentation that option G3 and option
A3 were rejected for.

This needs a decision rather than a directive, because the obvious fix is not
free. Reordering so the evidence boundary precedes request evidence is clean and
safe, since Step 2 needs nothing from Step 1, but it renumbers a validation
skeleton that was just rebuilt and verified at six steps. Creating the evidence
module in Step 1 with capture only, then extending it in Step 2, keeps the
numbering and the skeleton intact at the cost of one file list, one test leaf,
and one line-budget baseline. I recommend the second, and the question belongs
in the plan so the choice is recorded rather than made during implementation.

One smaller item concerns where an assertion lives. Step 5 assigns substantial
canonical-instruction content assertions to no named module: its test list has a
route test, a skill-route test, and an adapters test, while the completed
requestor effort keeps instruction content in its own
`test_code_review_requestor_instruction/` leaf and this plan gives reviewer-mode
`implementation-check` its own leaf for the same purpose. Name the owner, either
by adding the matching leaf or by saying the adapters module carries it.

Everything else holds. The confirmed facts still match the tree, the six steps
are correctly ordered apart from the capture question above, each step carries
tests first, exact file lists, line budgets against the 650 ceiling, split
guidance, and `rg` checks that prove code rather than prose, and Step 6 covers
the sixteen design acceptance cases, the eight requirement criteria, and one
smoke invocation per launcher.

I did not open the validation plan; it is outside this exchange. Its six
matching identifiers and 36 untouched placeholders remain your verification, now
stated as independently checked.

### Question verdicts for plan code-reviewer round 3

Seven questions, seven confirmed answers, no option change.

- **Q01, evidence helper exposure: A2 confirmed.** Library, CLI, and launcher
  appear in every surface list, budget, focused-test line, and smoke set.
- **Q02, validator input: B2 confirmed.** `validate_commit_plan(blocks,
  staged_paths)` is the named public boundary and the batch workflow calls it.
- **Q03, evidence encoding: C2 confirmed.** Distinct heading, one typed object
  behind both renderings, and the envelope round-trip assertion.
- **Q04, route actor: D2 confirmed.** Typed actor, required field,
  construction-time consistency check, and a test that rejects disagreement.
- **Q05, step granularity: E2 confirmed.** Six steps, with reviewer-mode
  `implementation-check` between the boundary it delegates to and the routing
  step whose instruction calls it.
- **Q06, acceptance seam: F2 confirmed.** Public Python over real temporary
  repositories, one smoke invocation per launcher in its own module.
- **Q07, executable evidence operations: G2 confirmed.** Step 2 owns the full
  operation set, Step 3 consumes it, and Step 5 now binds the reviewer
  instruction to it as well. The round-2 addition closed the last way an
  instruction could have described evidence work in prose.

One question is missing.

- **Q08: which step owns request-time index-tree capture?** Step 1 captures the
  Git index tree at publication; Step 2's evidence library and CLI list
  index-tree capture as their first operation, and G2 places that operation set
  behind one boundary. The first consumer therefore runs one step before its
  owner exists. Options worth putting to the writer: H1, let Step 1 implement
  its own capture inside the request module and leave the Step 2 boundary for
  reviewer use, which is the smallest edit and creates two implementations of
  one operation, exactly the split G3 was rejected for; H2, create
  `tools/code_review_evidence.py` in Step 1 with index-tree capture only, add its
  test leaf there, and extend the module with the remaining operations, the CLI,
  and the launcher in Step 2, adjusting Step 2's baseline for that file from 0 to
  its Step 1 count; H3, reorder so the evidence boundary precedes request
  evidence, since Step 2 depends on nothing from Step 1.

  My recommendation is H2. H3 is cleaner in isolation and I would prefer it on a
  new plan, but it renumbers a six-step validation skeleton that was rebuilt and
  independently verified this round, and the churn buys only ordering elegance.
  H2 keeps one owner for the operation, keeps every step identifier stable, and
  costs one file list entry, one test leaf reference, and one baseline number.
  H1 is the option to avoid: two captures of the same tree can disagree, and a
  disagreement here is invisible until a reviewer rejects a request whose tree
  its own requestor computed differently.

One placement item.

- **Name the module that owns the canonical-instruction assertions in Step 5.**
  The step now asserts launcher delegation, canonical policy, exact answer-path
  reads, one bounded wait, manifest lifecycle, early rejection, repair staging,
  validation side effects, publication exits 0 and 3, and forbidden operations.
  Its test list contains a route test, a skill-route test, and
  `test_code_reviewer_adapters_tdd.py`, whose stated purpose is adapter
  linkage. The completed requestor effort keeps instruction content in
  `tests/unit/tools/test_code_review_requestor_instruction/`, and this plan
  already gives reviewer-mode `implementation-check` its own leaf for the same
  reason. Either add the matching leaf:

  > - `tests/unit/tools/test_code_reviewer_instruction/__init__.py` (new, to be
  >   created).
  > - `tests/unit/tools/test_code_reviewer_instruction/test_code_reviewer_instruction_tdd.py`
  >   (new, to be created).

  and add it to the new-test-leaf list, the line budgets, and the Step 5 `ghog
  single` line, or state explicitly that the adapters module carries instruction
  content as well as adapter linkage. Either is fine; leaving it unsaid means
  the assertions land wherever the implementer happens to put them.

### Requested changes for plan code-reviewer round 3

Requested changes: All four round-2 items landed and all seven answers stand, so this round asks
for no option change. Two edits remain.

- Add Q08 on request-time index-tree capture ownership, recommended option H2.
  Step 1 captures the index tree while Step 2's evidence boundary owns
  index-tree capture under G2, so one operation currently has two owners and the
  first consumer runs before its owner exists. H2 creates the evidence module in
  Step 1 with capture only and extends it in Step 2, which keeps one owner
  without renumbering the six-step validation skeleton you just verified. Apply
  the selected answer to Step 1's file list, Step 1's behavior section, and
  Step 2's baseline for that file.
- Name the module that owns Step 5's canonical-instruction assertions: either
  add a `test_code_reviewer_instruction/` leaf matching the completed requestor
  convention, and carry it into the new-test-leaf list, line budgets, and `ghog
  single` line, or say that the adapters module covers instruction content too.

### Writer instructions for plan code-reviewer round 3

Apply these two changes to `docs/v0.11.0/plan.v0.11.0.code-reviewer.md`, then
publish round 4. Do not consolidate. No existing answer changes.

1. Add Q08 through `oqm` on request-time index-tree capture ownership, following
   the existing BBQ and options shape, with H2 recommended. Then apply the
   selected answer to the body: under H2, add `tools/code_review_evidence.py`
   and its test leaf to Step 1's file list with capture-only scope, note in
   Step 1's behavior section that `CodeReviewRoundInput` receives the tree from
   that helper rather than computing it, and change Step 2's line-budget
   baseline for that file from 0 to its Step 1 count. If you select H3 instead,
   the validation skeleton has to be renumbered again, so weigh that before
   choosing.
2. Name the module that owns Step 5's canonical-instruction assertions: either
   add the `test_code_reviewer_instruction/` leaf quoted in the verdicts and
   carry it into the new-test-leaf list, the line budgets, and the Step 5 `ghog
   single` line, or state that `test_code_reviewer_adapters_tdd.py` covers
   instruction content as well as adapter linkage.

Item 1 is a decision that belongs in the plan rather than in the implementer's
head. Item 2 is placement.

With both applied, round 4 can converge. The seven existing answers cover the
implementation decisions, the confirmed facts match the tree, the six steps
carry tests first with exact file lists, line budgets, split guidance, and
completion checks that prove code rather than documentation, and Step 6 covers
every design acceptance case, the requirement's eight criteria, and one smoke
invocation per launcher.

### Final reviewer decision for plan code-reviewer round 3

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-3 -->

## Round 4 by requestor

- Recorded: 2026-08-14T23:56:22+02:00
- Exchange: specification/plan/v0.11.0/code-reviewer
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Outcome: request

### Review identity for plan code-reviewer round 4

Umbrella draft: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
Reviewed specification: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-reviewer.md
Review round: 4

### Requestor assessment for plan code-reviewer round 4

## Writer assessment for plan code-reviewer round 4

The round 3 answer was accepted without disagreement. The seven existing answers remain selected and sufficient, and Q08 now records H2 as the recommended and accepted ownership choice. No additional implementation-plan question is currently known.

The request-time index tree has one implementation owner. Step 1 creates `tools/code_review_evidence.py` with capture-only scope before request publication calls it; Step 2 extends that same module with the remaining G2 operations and uses the recorded Step 1 count as its line-budget baseline. The six step identifiers and the separately verified validation skeleton remain unchanged.

Step 5 now names `tests/unit/tools/test_code_reviewer_instruction/` as the owner of canonical reviewer instruction content assertions. The leaf appears in the global test snapshot, the Step 5 file list, its line budget, and its focused `ghog single` command, while adapter linkage remains in its existing dedicated module.

### Change summary for plan code-reviewer round 4

## Changes since plan code-reviewer round 3

- Added Q08 with H2 recommended and answered for request-time index-tree capture ownership.
- Moved creation of `tools/code_review_evidence.py` and its initial capture tests into Step 1, before the request renderer consumes the shared helper.
- Made `CodeReviewRoundInput` receive the tree from `capture_index_tree` rather than compute it.
- Changed Step 2 to extend the existing evidence module and tests, using the recorded Step 1 final line count instead of a zero baseline.
- Added `tests/unit/tools/test_code_reviewer_instruction/` as the explicit owner of canonical reviewer instruction assertions and carried it into the test snapshot, Step 5 files, line budget, and focused test command.
- Preserved the six plan and validation step identifiers and all 36 untouched validation placeholders.

### Writer response for plan code-reviewer round 4

Writer response: ## Writer response to plan code-reviewer round 3

Accepted both requested changes with no disagreement.

Q08 selects H2. The evidence library now begins in Step 1 with the one shared index-tree capture implementation and grows in Step 2, eliminating both the duplicate owner and the dependency inversion without renumbering the verified validation skeleton.

The canonical reviewer instruction assertions now belong to their own `test_code_reviewer_instruction` leaf, matching the completed requestor convention. Adapter-linkage tests remain focused on host adapters.

### Reviewer focus for plan code-reviewer round 4

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-4 -->

## Round 4 by reviewer

- Recorded: 2026-08-15T00:01:39+02:00
- Exchange: specification/plan/v0.11.0/code-reviewer
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Outcome: answer

### Reviewer assessment for plan code-reviewer round 4

Both round-3 items landed, and each reached every place that had to move with
it.

Q08 is well formed: three materially distinct options, honest cons, and H2
answered. Its consequences are applied rather than left in the question section.
`capture_index_tree` is named as the single requestor-and-reviewer
implementation, `tools/code_review_evidence.py` is created in Step 1 with
capture-only scope, its test leaf and temporary-repository capture cases are in
Step 1, `CodeReviewRoundInput` receives the tree from that helper instead of
computing it, Step 1's completion check greps for the helper, and Step 1's
focused test line names the evidence test module. Step 2 now marks the module
and its test as existing after Step 1, extends them, and takes the recorded Step
1 count as its baseline instead of zero. One operation, one owner, and the owner
now exists before its first consumer.

The instruction test leaf is equally complete.
`tests/unit/tools/test_code_reviewer_instruction/` appears in the global test
snapshot, in Step 5's file list, in the test that asserts launcher delegation,
in the line budget with a note keeping content assertions separate from adapter
linkage, and in Step 5's focused test line, while
`test_code_reviewer_adapters_tdd.py` keeps adapter linkage.

Every implementation decision is settled. I agree with all eight answers: A2,
B2, C2, D2, E2, F2, G2, and H2.

I re-checked the contracts that cross step boundaries and they hold. The
evidence module has one owner across two steps with matching baselines. Every
executable guarantee the design promised now has a named surface that a test can
run: capture and attribution in Step 2, `umbrella_digest` and `validation_state`
comparisons in Step 2 with Step 3 consuming them, and both canonical
instructions bound to those commands by their own completion checks. The six
step identifiers are stable, the confirmed facts still match the tree, and each
step carries tests first, exact file lists, line budgets against the 650
ceiling, split guidance, and `rg` checks anchored on implementation identifiers
rather than prose.

One wording edit remains, listed in the covered wording. It changes no behavior
and can be applied during consolidation.

This review found the same defect class in every round: an operation or an
assertion with no named owner. Round 1 found four of them plus a missing
decision, round 2 found one, round 3 found two. I found none this round.

One limit stands, unchanged. The validation plan is outside this exchange, so I
did not open it. Its six matching identifiers and 36 untouched placeholders
remain your independent verification.

This is a convergence recommendation and nothing more. It is advisory, it
authorizes no consolidation, and the choice between `Consolidate` and `Revise
and review again` stays with the human at the requestor's gate.

### Question verdicts for plan code-reviewer round 4

Eight questions, eight confirmed answers, no option change and no question
missing.

- **Q01, evidence helper exposure: A2.** Library, CLI, and launcher appear in
  every surface list, budget, focused-test line, and the three-launcher smoke
  set.
- **Q02, validator input: B2.** `validate_commit_plan(blocks, staged_paths)` is
  the named public boundary, called by both the reviewer and batch execution.
- **Q03, evidence encoding: C2.** Distinct `## Code review evidence` heading,
  one typed object behind both renderings, and the envelope round-trip
  assertion.
- **Q04, route actor: D2.** `CodeReviewActor`, the required
  `CodeReviewRoute.actor`, its construction-time consistency check, and a test
  that rejects disagreement between actor and classified state.
- **Q05, step granularity: E2.** Six stable identifiers, with reviewer-mode
  `implementation-check` between the boundary it delegates to and the routing
  step whose instruction calls it.
- **Q06, acceptance seam: F2.** Public Python over real temporary repositories,
  one smoke invocation per launcher in its own module.
- **Q07, evidence operation boundary: G2.** Step 2 owns the full operation set;
  Step 3 and Step 5 consume it, and both canonical instructions are held to that
  delegation by their own completion checks.
- **Q08, capture ownership: H2.** This is the answer I recommended and the
  option text states the trade honestly: H2's con names the split module and the
  cross-step baseline it costs, and H3's con names the renumbering it would
  force on a skeleton that was rebuilt and verified. H1's con names the failure
  mode that matters, two implementations of one identity operation that can
  disagree.

Cross-checks that hold in the current text: the evidence module's Step 1 and
Step 2 baselines agree; the capture helper is created before the request
renderer that consumes it; the Step 2 CLI operation set matches the G2 answer
item for item; Step 3 asserts instruction text while Step 2 executes the
behavior it names; Step 5 does the same for the reviewer instruction and keeps
content assertions in their own module; the test-tree snapshot lists all seven
new leaves and states which two carry a second CLI module; and the confirmed
line counts, risk bands, and adapter set still match the tree.

One wording edit remains.

- **Step 2's first test line still lists index-tree capture**, which Step 1 now
  owns. Since Step 2 extends the same module and test file the sentence is not
  wrong, but a reader can take it for a second set of capture cases. Suggested
  replacement for that line:

  > Use temporary Git repositories to extend the Step 1 capture cases with
  > pre-repair blobs, created and writer-deleted files, reviewer-only patch
  > attribution, drift, and stable manifest write, read, and retirement.

### Convergence evidence for plan code-reviewer round 4

Covered wording: One wording edit remains. It changes no behavior and can be applied during
consolidation.

- Step 2's first "Tests first" line still opens with index-tree capture, which
  Q08 moved to Step 1. Step 2 extends the same module and test file, so the
  sentence is not wrong, but it reads as a second set of capture cases.
  Suggested replacement:

  > Use temporary Git repositories to extend the Step 1 capture cases with
  > pre-repair blobs, created and writer-deleted files, reviewer-only patch
  > attribution, drift, and stable manifest write, read, and retirement.

Convergence rationale: Four rounds closed everything they opened. Round 1 found a decision that would
have left the design's enforcement claims as prose, plus four accepted answers
that had not reached the body an implementer follows. Round 2 found the same
prose-versus-code gap one step away, in the reviewer's own canonical
instruction. Round 3 found one operation with two owners, running before its
owner existed. This round found nothing.

Convergence is warranted because the three conditions this review has been
measuring are met. Every implementation decision is answered, and each answer
names a file, a function, a command, or a count rather than an intention. Every
executable guarantee the design promised has a named surface a test can run, and
every canonical instruction that consumes one is held to that delegation by its
own completion check. The plan's confirmed facts match the tree: I verified the
line counts, the risk bands, the adapter set, and the launcher wiring in round 1
and they have not drifted.

The plan is also checkable on its own terms. Six stable step identifiers, tests
first in every step, exact file lists with create-or-update labels, line budgets
against the 650 ceiling with split guidance, `rg` checks anchored on
implementation identifiers rather than documentation phrases, and a final step
that covers the sixteen design acceptance cases, the requirement's eight
criteria, and one smoke invocation per launcher.

What remains is one sentence of polish that changes no behavior, which is the
convergence threshold this exchange set at round 1.

One limit belongs in the record. The validation plan is a separate document that
this exchange does not carry, so I never opened it. Its six matching step
identifiers and 36 untouched placeholders are the writer's independent
verification, not mine, and this recommendation assumes that verification holds.

This recommendation is advisory. It does not consolidate the plan, does not
authorize consolidation, and does not settle the choice between `Consolidate`
and `Revise and review again`. That choice belongs to the human at the
requestor's confirmation gate, with the option to override this recommendation
and add guidance for another round.

### Writer instructions for plan code-reviewer round 4

Do not consolidate on this answer. This is a convergence recommendation, it is
advisory, and consolidation stays behind the human confirmation gate.

1. Take the one wording edit in the covered wording during consolidation. It
   changes no behavior, so it does not need another review round.
2. Present the human with the identity, this recommendation, the current plan,
   and your own assessment, then offer `Consolidate` or `Revise and review
   again`. If the human overrides with guidance, carry that guidance into the
   replacement request.
3. Nothing else is outstanding. All eight answers stand as selected, and no
   question needs to be added, split, or removed.

Two notes for implementation rather than for this document. First, this
recommendation assumes your independent verification of the validation plan,
since that document is outside this exchange and I did not open it; if its six
identifiers ever drift from the plan's, `implementation-check` will mislabel
every step after the split. Second, Step 1 and Step 2 share one module with a
cross-step baseline, so record `tools/code_review_evidence.py`'s final Step 1
count when Step 1 completes and carry that exact number into Step 2's
line-budget checkpoint rather than the advisory estimate.

### Final reviewer decision for plan code-reviewer round 4

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-4 -->

## Round 4 by human

- Recorded: 2026-08-15T00:13:43+02:00
- Exchange: specification/plan/v0.11.0/code-reviewer
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Outcome: human-confirmation

Human choice: Consolidate
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-4 -->
