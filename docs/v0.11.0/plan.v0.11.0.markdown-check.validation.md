# v0.11.0 Markdown checker implementation tracking and validation

No, it is not implemented.

This initial skeleton tracks the three planned implementation slices; no
implementation check has taken place yet.

## File-based IO cost clarification for v0.11.0 Markdown-check validation

- One Git tracked-path query per checker invocation.
- One configuration and one baseline read per invocation.
- One source read and parse per tracked Markdown file.
- No baseline or source write during normal checker execution.

## Complexity bound for v0.11.0 Markdown-check validation

- Per-file parsing and rule evaluation remain linear in source size and tokens.
- Baseline lookup remains constant time on average by path and rule key.
- Finding sorting may be `O(f log f)` and performs no source reread.

## Step 1. Shared source model and rule engine validation

### Analysis of Step 1 implementation state

Yes. Step 1 has been fully implemented.

The shared source model, pure document classifier, complete Step 1 rule catalog,
review-heading fence integration, focused examples, and property coverage are
present. The completed forced Groundhog walk reported `fail=0`, `warn=0`,
`xfail=0`, `cov=100`, `outliers=0`, `excluded=0`, and `exit=0`.

### Goal for Step 1 source and rules

Create one fence-aware parsed source model and pure evaluators for the supported
`MD*` and `LS*` rules while preserving review heading behavior.

### Step 1 improvement expectations

- One parse per Markdown fixture.
- Link tokens and pure syntactic adapter classification covered.
- Complete rule and overlap coverage.
- Property coverage for normalization and hierarchy streams.

### What was implemented for Step 1

- Added immutable source and finding records in
  `tools/markdown_check/models.py`.
- Added one fence-aware parse in `tools/markdown_check/source.py` for
  frontmatter, headings, list boundaries, raw HTML, Markdown links, inline code,
  source lines, and body metadata.
- Added the pure bounded-adapter classifier in
  `tools/markdown_check/classifier.py`.
- Added pure evaluators for MD001, MD024, MD025, MD032, MD033, MD038, LS001,
  LS002, and LS003 in `tools/markdown_check/rules.py`; MD001 compares
  consecutive headings and leaves first-heading policy to MD041.
- Reused `fenced_line_numbers` from the shared parser in
  `tools/review_markdown_headings.py`, preserving existing heading-rendering
  behavior.
- Added focused source-model and rule tests plus Hypothesis coverage for invalid
  consecutive heading increments, a fragment beginning at level two, and
  normalized heading collisions under `tests/unit/tools/markdown_check/`.

### New types or classes introduced for Step 1

- `SourceLine`, `Frontmatter`, `Heading`, `ListBlock`, `RawHtml`,
  `MarkdownLink`, `InlineCode`, `MarkdownSource`, and `Finding` are immutable
  records for parsed source and diagnostics.
- `DocumentKind` and `DocumentClassification` represent the pure structured or
  adapter classification and its reason.

### Architecture check for Step 1

The source adapter owns Markdown tokenization, the classifier consumes only the
immutable source model, and the rules consume only source and classification
values. Rule evaluation performs no filesystem access or output, while the
existing review-heading module depends only on the shared fence boundary
function. This preserves clear parsing, policy, and presentation boundaries and
introduces no DDD-Hexagonal dependency inversion or layer leak.

No architecture issue needs to be addressed.

### Performance check for Step 1

Each source is split and parsed once. Fence, frontmatter, heading, list, HTML,
link, and inline-code scans are linear in source size or token count; pure rule
evaluation is linear in the collected tokens. No new quadratic or `O(n log n)`
source traversal is present.

No performance issue needs to be addressed.

### Unit test coverage check for Step 1

The unit suites cover the source-model records through parser results, both
document classifications, every supported rule, adapter exemptions, MD038 edge
cases, clean rule paths, both fence styles, UTF-8 headings, line locations,
level-two fragment starts, and property-generated hierarchy and normalization
cases. The completed forced full walk reported `cov=100`, with no uncovered
Step 1 line.

No unit-tested class is below 100 percent or needs completing.

### Feature integrity for Step 1

The existing `tests/unit/tools/test_review_markdown_headings_tdd.py` suite passed
with the shared fence scanner, including backtick and tilde fences and
idempotent round qualification. The forced full suite passed with no failures,
warnings, xfails, duration outliers, or exclusions, so no existing feature or
reporting capability is impaired.

## Step 2. Policy, baseline, and launcher validation

### Analysis of Step 2 implementation state

Yes. Step 2 has been fully implemented.

Step 2 now provides strict policy loading, immutable baseline
comparison, one tracked-Markdown inventory, deterministic diagnostics, the
platform-neutral CLI, and the repository-root Windows launcher. The focused
Step 2 suite and the full Groundhog day both pass.

### Goal for Step 2 checker execution

Compose the rule engine with validated configuration, Git inventory, versioned
baseline comparison, deterministic diagnostics, and a repository-root launcher.

### Step 2 improvement expectations

- Fail-fast configuration validation.
- Inventory-backed adapter-link existence refinement.
- Stable stdout findings and stderr health messages.
- Growth, unchanged debt, and shrink behavior covered at 100 percent.

### What was implemented for Step 2

- Added closed-catalog `.markdownlint.json` loading with mandatory `MD024` and
  `MD025` enforcement and the confirmed `MD033` `img` allowance.
- Added strict version-1 baseline parsing, normalized aggregate path/rule
  allowances, no-growth failures, and deterministic `debt-reduced`
  advisories without baseline mutation.
- Added a single `git ls-files` Markdown inventory, strict UTF-8 source reads,
  inventory-backed bounded-pointer refinement, deterministic evaluation, and
  `path:line: RULE: reason` rendering.
- Added `python -m tools.markdown_check.cli` and root `markdown-check.bat`
  entry points that converge on `cli.main`.
- Added the accepted legacy baseline for LS001, LS002, and MD033 only. MD032
  and MD038 remain unallowlisted and are therefore still enforced for Step 3.

### New types or classes introduced for Step 2

- `MarkdownPolicy` models validated enabled rules and allowed HTML elements.
- `BaselineAllowance`, `BaselineComparison`, and `Baseline` model immutable
  aggregate debt and comparison results.
- `CheckerResult` and `CheckerRunner` compose the inventory, parser, rule
  engine, baseline comparison, and output streams.
- `PolicyError`, `BaselineError`, and `InventoryError` preserve fail-closed
  operational boundaries.

### Architecture check for Step 2

Pass. Configuration, baseline, inventory/evaluation, and CLI responsibilities
are separated into `policy.py`, `baseline.py`, `runner.py`, and `cli.py`.
The Step 1 classifier gained only repository-relative target resolution; the
runner owns the inventory existence check. Both public commands enter the
same `cli.main` boundary, and no Node or network dependency was introduced.

No architecture issue needs to be addressed.

### Performance check for Step 2

Pass. The runner executes one Git inventory command and reads each selected
Markdown source once. Groundhog duration profiling moved repository setup out
of measured test calls: the real inventory call dropped from 1.13 seconds to
below the reporting threshold, and the CLI stream call dropped from 1.09
seconds to below 0.01 seconds. The irreducible real batch-to-Python launcher
integration dropped from 1.73 to 0.85 seconds and is recorded at that measured
baseline through `ghog exclude`; its assertions remain unchanged.

No performance issue needs to be addressed.

### Unit test coverage check for Step 2

Pass. The exact four-file completion command ran 34 focused tests with no
failures. Policy, malformed baseline, growth/shrink, Git failure and decoding,
path containment, pointer refinement, deterministic streams, direct CLI, and
clean-environment launcher paths are covered. The final detached `ghog day`
completed with `exit=0`, 1,987 passing tests, and 100 percent coverage.

No unit-tested class is below 100 percent or needs completing.

### Feature integrity for Step 2

Pass. A direct checker run with the populated baseline suppresses only the
confirmed LS001, LS002, and MD033 legacy counts. Its remaining output contains
only MD032 and MD038 findings, proving those rules were not weakened or folded
into the baseline ahead of the Step 3 repository repair. The baseline remains
an input artifact and is never rewritten by the checker.

## Step 3. Shared gate and documentation validation

### Analysis of Step 3 implementation state

Not started. Step 3 is not implemented because zero-debt repairs, gate wiring,
acceptance coverage, and reference documentation are still absent.

### Goal for Step 3 repository rollout

Establish the authoritative repository baseline, add the checker to `check.bat`,
and verify the complete direct and shared-gate contract with acceptance tests and
reference documentation.

### Step 3 improvement expectations

- Human and implementation repair responsibilities verified before activation.
- One shared result through direct and gate launchers.
- Acceptance coverage for passing, failing, configuration, and baseline cases.

### What was implemented for Step 3

_(empty — no check has taken place yet.)_.

### New types or classes introduced for Step 3

_(empty — no check has taken place yet.)_.

### Architecture check for Step 3

_(empty — no check has taken place yet.)_.

### Performance check for Step 3

_(empty — no check has taken place yet.)_.

### Unit test coverage check for Step 3

_(empty — no check has taken place yet.)_.

### Feature integrity for Step 3

_(empty — no check has taken place yet.)_.
