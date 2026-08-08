# v0.11.0 specification review requestor implementation tracking and validation

No, it is not implemented.

Step 1 is implemented and validated. The specialized orchestration, workflow
routing, and end-to-end acceptance slices in Steps 2 through 4 remain pending.

> Initial-skeleton note: each not-yet-checked section uses the literal empty
> placeholder required by the validation workflow. Implementation checks replace
> those placeholders with evidence and add a missing-work section only when a
> checked step is incomplete.

---

## File-based IO cost clarification for v0.11.0 specification review requestor implementation

All implementation work must preserve these plan constraints:

- Resolve one effort and inspect only its bounded exact document and
  coordination paths.
- Read each feedback or guidance input once and render paired outputs without
  reparsing generated Markdown.
- Publish, wait, reclaim, and complete through shared exact-path atomic
  operations.
- Never load sibling transcript history as routing or working context.

## Complexity bound clarification for v0.11.0 specification review requestor implementation

- **O(1) per render or protocol action** over a constant exact-path set.
- **O(n) per authored input** for feedback and guidance rendering.
- **O(k) per workflow resolution with constant k** for the bounded current
  effort candidates.

Every implementation check must reject documentation-tree scans, transcript
history reads, or repeated generated-Markdown parsing.

---

## Step 1. Add paired specification request rendering

### Analysis of Step 1 implementation state

Yes. Step 1 has been fully implemented.

The repository now provides one frozen, validated specification-round input,
one paired request and transcript-summary render result, a strict ignored-file
CLI and self-locating launcher, a canonical specialized template, public
exports, and focused tests covering every supported type and failure boundary.

### Goal for Step 1

Add one validated specification-round input that produces coherent complete
request content and substantive transcript-summary content for all supported
specification types.

### Step 1 improvement expectations

- Shared identity and Markdown validation are reused rather than copied.
- Request and summary identity, round, assessment, and changes cannot diverge.
- Guided replacement rounds emit the literal `Human guidance:` label and a
  separate writer response.
- Rendering performs one linear pass over caller-authored inputs and one write
  per output.

### What was implemented for Step 1

- **Paired renderer**: added `tools/spec_review_request.py` with exact filename
  identity derivation, the `design` to `design-specification` mapping, shared
  envelope rendering and parsing, and independent request and transcript
  composition from one immutable input.
- **Authored request boundary**: added
  `templates/spec-review-request.template.md` with unique round-qualified H2
  sections, the prescribed reviewer conclusion, and an exact answer artifact.
  The transcript summary uses H3 sections and excludes fixed conclusion
  boilerplate.
- **File command contract**: added `bin/spec_review_request.bat` and CLI flags
  for exact context and round, separate assessment, change-summary,
  writer-response, and optional-guidance inputs, plus two explicit output
  paths. Every caller-owned path must be an effectively ignored root `a.*`
  file, and all paths are validated before either output is written.
- **Guided override behavior**: preserved the literal `Human guidance:` value
  and a separately labeled writer response in both paired artifacts.
- **Package surface**: exported `SpecificationRoundInput`,
  `SpecificationRequestRender`, `specification_context`, and
  `render_specification_request` from `tools/__init__.py`.
- **Validation evidence**: the focused renderer suite, lifecycle split suite,
  and sensitive-commit suite pass. The final `ghog day` completed with 1,486
  passing tests, 100% coverage, zero outliers, zero exclusions, and `exit=0`.

### Step 1 implementation-to-plan variances

`tools/spec_review_request.py` finished at 413 lines rather than the advisory
240-340 estimate, and its focused test finished at 477 rather than 300-420.
Both remain below the plan's 550-line safe threshold and 650-line ceiling. The
extra lines provide strict caller-path, UTF-8, Git-ignore, template, shared
validation, and IO failure coverage without creating another production
module.

The existing 683-line lifecycle test was split into a 501-line transition
module and a 225-line recovery module so the repository-wide line ceiling
remains green. No lifecycle assertion was removed.

The Groundhog duration gate identified one unrelated real-Git unit test at
5.19 seconds. Its unborn-branch Git protocol was replaced by typed exact-output
doubles while preserving and strengthening its empty-tree, finding-location,
and no-pending assertions; its isolated call phase is now below 0.01 seconds.

### New types or classes introduced for Step 1

- `SpecificationRoundInput`: frozen exact context, positive round, timestamp,
  authored assessment, change summary, writer response, and optional literal
  human guidance.
- `SpecificationRequestRender`: frozen complete request content and substantive
  transcript summary pair.
- `_ArgumentParser`: internal command adapter that converts parse failures into
  the shared fail-closed validation error.

### Architecture check for Step 1

- **Domain boundary**: the two public dataclasses hold validated review content
  and depend on shared exchange value objects, not persistence or workflow
  orchestration.
- **Rendering boundary**: the pure paired renderer uses shared `Envelope`,
  `render_envelope_markdown`, and `parse_envelope_markdown` contracts. It does
  not derive one generated artifact by reparsing the other.
- **Adapter boundary**: Git-ignore checks, caller-owned file IO, argument
  parsing, and process exit handling remain in the thin command portion of the
  focused renderer module; publication stays delegated to the shared exchange.
- **Dependency direction**: the package root exports stable renderer values,
  while the renderer imports shared model and envelope modules directly and
  introduces no dependency on higher workflow layers.
- **Maintainability**: every modified or split Python file is below 550 lines,
  and no production file approaches the 650-line ceiling.

No, there is nothing that needs to be addressed for Step 1.

### Performance check for Step 1

- **Linear authored content**: request and summary composition each traverse
  the bounded authored strings once, so work is `O(n)` in supplied content.
- **Constant path set**: the CLI validates four authored inputs, optional
  guidance, and two outputs without a directory scan. Git ignore checks use a
  fixed command per supplied root path.
- **One-write result**: both output paths are validated before rendering, and
  each rendered artifact is written once.
- **No generated-output parsing for composition**: shared parsing validates the
  complete request envelope only; the transcript summary is composed directly
  from the frozen source input.

No, there is no performance issue that needs to be addressed for Step 1.

### Unit test coverage check for Step 1

- **Supported identities**: parameterized tests cover feature requests, issues,
  designs mapped to `design-specification`, and plans, with and without an
  umbrella.
- **Model and Markdown contract**: tests cover frozen values, positive rounds,
  required authored content, H1 and JSON-first structure, H2 request sections,
  paired identity fields, guidance preservation, and boilerplate exclusion.
- **CLI and filesystem boundary**: tests cover exact flags, missing and
  malformed UTF-8 inputs, non-root, tracked, duplicate, wrongly named, and
  directory paths, Git absence and failure, output errors, template failure,
  and shared-validation mismatch.
- **Coverage evidence**: the full suite reports 100% coverage, including every
  mapped defensive branch in `tools/spec_review_request.py`.

No, there is no unit-tested class below 100% that needs completing for Step 1.

### Feature integrity for Step 1

- **Shared exchange compatibility**: existing envelope and context validation
  remain the source of truth, and publication behavior is unchanged.
- **Lifecycle preservation**: the lifecycle-test split moved recovery cases
  without removing assertions; both focused modules pass.
- **Test reliability**: the sensitive-commit optimization replaces only slow
  subprocess setup with exact protocol doubles and retains the behavior under
  test. The full suite reports zero failures and zero duration warnings.
- **Adapter integrity**: the launcher follows the established self-locating
  `llm-shared` batch pattern, and the canonical template contains no
  provider-specific fork.

No, no existing feature or reporting capability appears impaired by Step 1.

---

## Step 2. Add the specialized requestor instruction and adapters

### Analysis of Step 2 implementation state

Yes. Step 2 has been fully implemented.

The canonical specialized role now registers the fixed specification policy,
coordinates every lifecycle transition through the shared requestor, and
gates consolidation on durable authorization. Thin workflow, Codex, and Claude
adapters expose that role without copying its policy, and focused contract tests
cover the instruction and adapter boundaries.

### Goal for Step 2

Add one discoverable specification requestor that owns assessment, edits, and
authorized consolidation while delegating every durable transition to the
shared requestor and exchange launcher.

### Step 2 improvement expectations

- The exact specification family policy is registered on every operation.
- Intermediate rounds, convergence, reclaim, escalation, and owning-action
  replay follow the shared protocol without manual artifact mutation.
- Canonical consolidation runs only after durable `Consolidate` authorization.
- The `.agent/workflows`, `.agents/llm-shared/instructions`,
  `.agents/llm-shared/skills`, and `.claude/skills` Markdown files redirect to
  the canonical instruction in the form each host loader resolves.

### What was implemented for Step 2

- Added `instructions/spec-review-requestor.md` with the fixed specification
  family, convergence signal, choice labels, shared lifecycle commands, paired
  renderer invocation, exact answer-path reading, replay behavior, and
  authorized consolidation flow.
- Added redirect-only adapters for the workflow, packaged Codex instruction,
  Codex skill, and Claude skill discovery surfaces. The junctioned workflow
  wrapper reuses the repository-wide locate steps so the body resolves when
  llm-shared is the workspace, a sibling clone, or a submodule, while the
  Codex and Claude hosts keep their loader-relative canonical links.
- Added focused instruction-contract tests for fixed policy, lifecycle states,
  renderer inputs, writer-owned wording changes, durable authorization, and
  post-consolidation completion.
- Added adapter-structure tests that keep host files to metadata plus one direct
  canonical redirect and pin the repository-wide Codex redirect forms.
- Reached the Groundhog objective with 1,494 passing tests, 100% coverage, no
  warnings, no duration outliers, and no exclusions.

### New types or classes introduced for Step 2

No production types or classes were introduced. This step adds canonical
Markdown orchestration and redirect adapters only.

### Architecture check for Step 2

- **Role boundary**: the specialized instruction owns specification assessment,
  writer edits, and the authorized consolidation decision while delegating
  durable state transitions to `instructions/review-requestor.md`.
- **Protocol boundary**: status, activation, publication, waiting, answer
  consumption, continuation, confirmation, reclaim, and completion remain
  shared exchange operations; the instruction forbids manual artifact changes.
- **Rendering boundary**: the role invokes the paired renderer using exact
  caller-owned inputs and outputs and reads only the authoritative answer path.
- **Adapter boundary**: all four host adapters contain only discovery metadata
  where needed and one redirect to the canonical instruction, each in the form
  its own loader resolves.
- **Dependency direction**: provider adapters point inward to canonical prose;
  canonical prose references the shared role and launcher contracts without
  duplicating their implementation.

No, there is nothing that needs to be addressed for Step 2.

### Performance check for Step 2

- **Bounded paths**: the role uses exact document, coordination, answer, and
  caller-owned render paths without a documentation-tree scan.
- **Single authoritative answer**: each assessment reads the exact answer path
  once and never reloads the sibling transcript as working context.
- **Linear authored content**: paired rendering remains linear in supplied
  feedback, writer response, and optional guidance; no nested collection work
  is introduced.
- **Static adapters**: host redirects add no runtime computation or repeated IO.

No, there is no performance issue that needs to be addressed for Step 2.

### Unit test coverage check for Step 2

- **Instruction policy**: focused tests cover the exact family, convergence
  signal, choice labels, command sequence, answer-path rule, reclaim boundary,
  wording gate, consolidation authorization, and completion route.
- **Adapter structure**: focused tests cover every requested host, reject copied
  lifecycle policy, require discovery metadata, and assert exact Codex plugin
  redirects. A regression test pins the workflow wrapper to the shared
  `review-requestor` locate body with only the instruction name substituted, so
  it cannot drift back to a clone-relative link that a junctioned project
  cannot resolve.
- **Class coverage**: this Markdown-only step introduces no class file requiring
  a class-specific unit-test package.
- **Coverage evidence**: the full suite reports 100% project coverage and all
  focused instruction and structure tests pass.

No, there is no unit-tested class below 100% that needs completing for Step 2.

### Feature integrity for Step 2

- **Shared lifecycle preservation**: the specialized role explicitly delegates
  state authority to the existing exchange and shared requestor contracts.
- **Provider consistency**: redirects follow established workflow, Codex, and
  Claude adapter shapes, including the global Codex plugin format checks.
- **Writer ownership**: assessment edits and convergence wording remain with the
  writer before the human gate; no automated consolidation bypass is added.
- **Regression evidence**: the complete Groundhog walk passes with no failures,
  warnings, duration outliers, or excluded tests.

No, no existing feature or reporting capability appears impaired by Step 2.

---

## Step 3. Route new questions and resume live exchanges through pw

### Analysis of Step 3 implementation state

Yes. Step 3 has been fully implemented.

Both question workflows now delegate marker-enabled new questions through
`pw`, while a focused exact-path adapter gives one matching live specification
exchange precedence over ordinary routing. Forced delegation, ambiguity
handling, explicit holds, no-question behavior, and replay states are covered
without adding exchange parsing to the main skill router.

### Goal for Step 3

Connect both question workflows to one specialized requestor and make an exact
matching live exchange authoritative over ordinary disk-derived routing without
growing the at-risk workflow module beyond 650 lines.

### Step 3 improvement expectations

- Marker absence, no-question passes, and direct holds preserve existing
  behavior and create no exchange state.
- Marker-present new questions delegate through `pw` to the exact current
  requirement, design, or plan.
- Current, reclaimable, escalated, convergence, and owning-action states route
  according to the shared contract.
- Routing checks a constant candidate set with no tree scan or transcript read.

### What was implemented for Step 3

- Added `tools/prompt_workflow_review.py` to derive at most the resolved
  requirement, design, and plan contexts, map designs to
  `design-specification`, resolve the declared umbrella, and classify exact
  exchanges through the shared observer.
- Added forced `spec-review-requestor` targeting for one question-bearing
  document and ordinary `pw skill` precedence for one non-idle live exchange.
- Added fail-closed diagnostics containing every exact identity, document, and
  state when more than one specification exchange is live for a topic.
- Added matching marker-gated delegation blocks to both canonical question
  workflows after question placement and after the explicit hold decision.
- Added focused routing, skill integration, and instruction contract tests,
  including every defensive routing branch required for 100% coverage.
- Reached the Groundhog objective with 1,515 passing tests, 100% coverage, no
  warnings, no duration outliers, and no exclusions.

### New types or classes introduced for Step 3

- `SpecificationReviewRoutingError`: prompt-workflow error that carries exact
  fail-closed ambiguity or context diagnostics to the command adapter.
- `_LiveRoute`: private frozen pairing of one validated `ReviewContext` with
  its observed `ArtifactState` during bounded candidate selection.

### Architecture check for Step 3

- **Routing boundary**: `prompt_workflow_review` owns specification candidate
  derivation and shared observer construction; `prompt_workflow_skill` only
  asks for a forced or live target and renders the resulting command.
- **Exchange boundary**: state classification remains in `ReviewExchangeCore`
  and its observer, so the new router neither parses coordination nor mutates
  protocol artifacts.
- **Writer boundary**: both question instructions retain question detection,
  explicit holds, and existing non-review handoffs while delegating all round
  work to the specialized role.
- **Dependency direction**: the adapter depends inward on prompt state and the
  shared exchange surface; the shared exchange has no dependency on `pw`.
- **File size**: the focused adapter remains below 550 lines, and
  `prompt_workflow_skill.py` remains at the 650-line repository ceiling.

No, there is nothing that needs to be addressed for Step 3.

### Performance check for Step 3

- **Constant candidates**: routing checks only `state.requirement`,
  `state.design`, and `state.plan`; it uses no glob, recursive scan, or
  directory enumeration.
- **Exact artifacts**: each candidate delegates classification to the shared
  fixed-path observer and never reads a versioned transcript.
- **Linear draft marker**: the child draft is read once to resolve its optional
  umbrella declaration, with work linear only in that bounded document text.
- **No nested traversal**: live and question-bearing selections are single
  passes over at most three candidates, so no `O(n log n)` or `O(n^2)` path is
  introduced.

No, there is no performance issue that needs to be addressed for Step 3.

### Unit test coverage check for Step 3

- **Context derivation**: tests cover requirement, design, and plan mapping,
  standalone and umbrella drafts, invalid umbrella markers, missing or outside
  umbrellas, and topic mismatches.
- **State routing**: tests cover current, abandoned, escalated, and
  owning-action states, marker absence, live precedence, forced selection, and
  all ambiguity branches.
- **Integration contracts**: tests cover forced and ordinary `pw` commands,
  unchanged fallback, exact error propagation, and both question instructions.
- **Coverage evidence**: the new routing module and the full project report
  100% coverage in the final Groundhog walk.

No, there is no unit-tested class below 100% that needs completing for Step 3.

### Feature integrity for Step 3

- **Ordinary routing**: marker absence or no live exchange returns the exact
  pre-existing disk-derived command.
- **Question workflow behavior**: no-question passes, direct holds, and absent
  review mode retain their existing human or settled-document handoffs.
- **Durable resumption**: all non-idle states, including escalation and
  owning-action replay, return to the one specialized role rather than being
  bypassed by document phase routing.
- **Regression evidence**: all 1,515 tests pass with no warning, exclusion, or
  duration finding.

No, no existing feature or reporting capability appears impaired by Step 3.

---

## Step 4. Prove the full specification requestor workflow

### Analysis of Step 4 implementation state

Not started. Step 4 is not implemented because no end-to-end requestor
acceptance or IO acceptance suite exists.

### Goal for Step 4

Validate the complete opt-in requestor behavior across every specification
type, repeated rounds, session recovery, transcript aggregation, convergence,
durable authorization, canonical consolidation, and completion.

### Step 4 improvement expectations

- Public launchers and canonical contracts compose without private state
  mutation or specialized transport exceptions.
- Every supported artifact identity and failure boundary is exercised.
- Transcript aggregation remains append-only evidence and is never read as
  working context.
- Acceptance IO checks prove bounded exact-path behavior and the repository
  coverage gate remains green.

### What was implemented for Step 4

_(empty — no check has taken place yet.)_.

### New types or classes introduced for Step 4

_(empty — no check has taken place yet.)_.

### Architecture check for Step 4

_(empty — no check has taken place yet.)_.

### Performance check for Step 4

_(empty — no check has taken place yet.)_.

### Unit test coverage check for Step 4

_(empty — no check has taken place yet.)_.

### Feature integrity for Step 4

_(empty — no check has taken place yet.)_.
