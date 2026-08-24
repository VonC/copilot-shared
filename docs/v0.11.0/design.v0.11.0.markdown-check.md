# Design v0.11.0: Repository Markdown checker

Reference feature request: [feature-request.v0.11.0.markdown-check.md](feature-request.v0.11.0.markdown-check.md)

---

## Context for the v0.11.0 repository Markdown checker

Review-mode transcripts and ordinary repository documentation already have
declared heading and Markdown rules, but those rules are not enforced by an
executable repository check. The v0.11.0 design introduces a bounded Python
checker that interprets the repository configuration, classifies tracked
Markdown files, evaluates the supported rule catalog, compares residual
findings with a no-growth baseline, and participates in the existing shared
gate.

The checker is deliberately independent of Node and package downloads. Its
output and exit status become the authoritative machine result for the policy;
the adoption measurements in the feature request remain planning evidence only.

## Scope for the v0.11.0 repository Markdown checker

The v0.11.0 outcomes are:

1. Every tracked Markdown file is evaluated under one deterministic policy.
2. Structured documents and adapter documents receive the correct heading
   obligations without path-specific exemption lists.
3. Every unbaselined enforced finding fails both the direct checker and the
   repository shared gate.
4. Maintainers receive stable, source-located diagnostics and focused reference
   documentation for the supported catalog.

Everything else is supporting design context for those outcomes or is
explicitly deferred.

### Capabilities included in the v0.11.0 checker

- A direct Python entry point that discovers the repository and reads tracked
  Markdown paths.
- A repository-root launcher that requires no prior environment activation.
- Fence-aware Markdown parsing shared with existing review heading behavior
  where the existing parser is suitable.
- Adapter classification, configured `MD*` rules, mandatory heading rules, and
  repository-local `LS*` rules.
- A tracked no-growth baseline and deterministic diagnostics.
- Shared-gate integration, unit and acceptance coverage, and one Diataxis
  reference page.

### Capabilities deferred beyond the v0.11.0 checker

- Repairing every historical Markdown violation as part of this effort.
- Reproducing the complete external markdownlint implementation or depending on
  its JavaScript runtime.
- Incremental changed-file checking, editor integration, or automatic fixes.
- Changes to review-exchange ownership, state transitions, or recovery policy.

---

## Confirmed technical facts for the v0.11.0 repository Markdown checker

**The repository policy is small but open-ended by default**:
`.markdownlint.json` currently disables `MD013` and configures `MD033` to allow
`img`. Omitted external markdownlint rules would normally be enabled, so the
bounded Python implementation needs an explicit supported catalog rather than
claiming full markdownlint compatibility.

**The shared gate already has a uniform failure contract**: the root
`check.bat` captures each tool status, calls `record_failure <name> <status>`,
and reports the collected failures at the end. The Markdown launcher can join
that flow as one additional named check without changing the gate's ownership
model.

**A fence-aware heading transformer already exists**:
`tools/review_markdown_headings.py` recognizes authored headings outside fenced
code while preserving literal examples. The checker can reuse or extract its
fence-aware scanning behavior instead of introducing a second incompatible
interpretation of headings.

**The initial adoption population contains accepted debt**: the feature
request records residual `LS001`, `LS002`, and `MD033` findings. Rules measured
at zero, including `MD001`, `MD024`, and `LS003`, must remain at zero and must
not receive baseline entries. A fence-aware review measured two `MD032`
findings across the 375 tracked and pending Markdown files that this effort will
commit: `.claude/skills/humanizer/SKILL.md` line 260 and
`docs/v0.11.0/review.design-specification.v0.11.0.markdown-check.md` line 264.
The implementation repairs the skill file, and a human maintainer repairs the
protocol-owned transcript before committing the effort. Those two prerequisites
make `MD032` start at zero in the committed state with no baseline entry; no
agent edits the published transcript.

---

## Current validation flow before the v0.11.0 checker

Markdown policy is distributed across `.markdownlint.json`, writing rules,
review instructions, and human review. The shared gate invokes Python and shell
checks, but it never inventories Markdown files or interprets their structure.
Consequently, a malformed document can be committed even when the relevant
instruction calls its heading defect non-negotiable.

```txt
author edits Markdown
  -> optional visual review
  -> check.bat runs unrelated checks
  -> Markdown policy has no machine result
```

## Target validation flow for the v0.11.0 checker

The direct launcher and the shared gate use the same checker entry point and
therefore cannot disagree about policy. One run builds an immutable inventory,
parses each file once, evaluates enabled rules, compares findings with the
baseline, emits every actionable result in stable order, and returns one final
process status.

```txt
direct launcher or check.bat
  -> resolve repository and load policy
  -> obtain tracked Markdown inventory
  -> classify and parse each document
  -> evaluate the supported rule catalog
  -> compare residual findings with the baseline
  -> emit ordered findings and configuration errors
  -> return success or failure
```

Configuration, inventory, decoding, and baseline integrity errors are checker
failures. They are not converted into Markdown findings because no trustworthy
per-document policy result exists in those cases.

---

## Policy model for the v0.11.0 repository Markdown checker

### Supported rule catalog for repository policy

The checker owns a published catalog rather than dynamically accepting every
markdownlint key. The first catalog contains the rules required by the feature:
`MD001`, `MD013`, `MD024`, `MD025`, `MD032`, `MD033`, `LS001`, `LS002`, and
`LS003`.
`MD013` is present so the current explicit disable is valid configuration even
though it does not run. Each catalog entry declares its namespace, accepted
configuration shape, default enabled state, and whether it is mandatory.

`MD*` identifiers are used only when the implemented semantics match the named
markdownlint rule. Local classification and stronger repository semantics stay
under `LS*`. Unknown configuration keys fail policy loading so a misspelling or
unsupported external rule cannot be silently ignored.

`MD032` checks that every list block has a blank line before and after it. It
applies to structured documents and adapters alike, including lists inside
review artifacts.

Review transcripts are generated from caller-authored requestor and reviewer
content without normalizing blank lines around lists. Because those transcripts
are protocol-owned and append-only after publication, authors must satisfy the
renderer-specific boundary before publication. Caller content rendered as its
own block keeps a blank line before and after every list. Content inlined behind
a label, specifically requested-changes, covered-wording, and writer-response
fields, must not begin with a list: it begins with a prose sentence, then a blank
line, then any list. Renderer changes remain outside this effort.

### Configuration precedence for mandatory heading protection

Repository configuration is loaded before any Markdown file. A configured
`false` disables a supported optional rule, and a rule-specific object supplies
validated options. `MD024` and `MD025` remain mandatory at the effective-policy
layer, so configuration cannot remove them from evaluation. The reference page
lists mandatory rules separately from configurable rules.

Local `LS001`, `LS002`, and `LS003` behavior is defined by this design and the
feature request. They do not impersonate markdownlint options that have
different semantics.

### Stable finding model for policy evaluation

Every rule returns zero or more finding records with four required fields:
repository-relative path, positive source line, stable rule identifier, and a
concrete reason. Whole-file findings use line 1. Rules do not print directly;
the runner owns ordering and rendering so parallel or refactored evaluation
cannot change observable output accidentally.

Findings are ordered by normalized repository path, source line, rule
identifier, and reason. The direct process exits successfully only when policy
loading succeeds and every emitted finding is covered without growth by the
baseline.

## Document model for the v0.11.0 repository Markdown checker

### Tracked Markdown inventory boundary

The repository's Git index is the authority for scope. The checker asks Git for
tracked paths, retains Markdown suffixes case-insensitively, normalizes their
display form to forward-slash repository-relative paths, and evaluates a fixed
snapshot for the run. Untracked scratch files and ignored `a.*` workflow inputs
are outside the inventory.

Failure to obtain the inventory, a tracked path escaping the repository, or a
tracked Markdown file becoming unreadable during the run fails the checker with
an operational diagnostic.

### Fence-aware Markdown source representation

Each file is decoded as UTF-8 and scanned once into a lightweight source model.
The model records frontmatter bounds, fenced-code bounds, ATX headings with
their line and level, list-block boundaries, raw HTML elements, and non-blank
body lines. Heading-like text and list markers inside a fence are literal
content and never enter the structural model.

The scanning primitive used by `tools/review_markdown_headings.py` is reused or
factored into a shared helper so review rendering and checking agree about
fenced content. Rule evaluators receive the source model and never rescan raw
text independently.

### Adapter classification before structured checks

Classification is deterministic and precedes rule evaluation. A document is an
adapter when it has YAML frontmatter with a non-empty `description`, when it is
a bounded canonical pointer in one of the approved adapter roots, or when it is
a reusable `templates/` fragment whose first heading is level two or deeper.

The bounded pointer classifier counts at most five non-blank body lines after
frontmatter and requires the body to contain only a canonical-instruction
pointer plus optional explanatory pointer text. The fragment classifier has no
line bound. Classification exempts only `LS001` and `LS002`; all other enabled
rules receive both adapter and structured documents.

### Complete heading hierarchy and uniqueness evaluation

`LS001` requires one level-one title for structured documents. `LS002` requires
at least two level-two sections for structured documents. `MD025` reports every
level-one heading after the first in any checked file.

`MD001` evaluates the ordered heading stream and reports a heading whose level
has no preceding immediate parent or skips a level. Levels one through six are
valid when their ancestry is complete. Adapter status does not weaken this
hierarchy check.

`LS003` normalizes every heading title by dropping inline formatting,
lowercasing while retaining non-ASCII characters, removing punctuation other
than hyphens, and replacing whitespace runs with one hyphen. It reports every
occurrence after the first normalized title across the complete file,
regardless of heading level or parent. `MD024` remains in the mandatory catalog
for its matching duplicate-heading semantics.

## Baseline model for the v0.11.0 repository Markdown checker

### No-growth comparison for residual findings

The repository-root `.markdownlint-baseline.json` is a tracked, versioned JSON
document containing aggregate allowances with explicit path, rule, and count
fields. After evaluation, the runner groups findings by the same key. A key
fails when its actual count exceeds its allowance; a new key has an implicit
allowance of zero. A count below the allowance passes and identifies baseline
debt that can be reduced in a later deliberate update.

Rules with no measured findings have no entries. The baseline cannot waive
configuration, inventory, decoding, or baseline-format errors.

### Baseline integrity and maintenance boundary

`.markdownlint-baseline.json` is parsed under a versioned schema, rejects
duplicate keys, requires positive counts, and rejects unsupported rule
identifiers. Paths use the same normalization as findings so alternate
separators cannot create a second allowance. The reference page explains how
maintainers verify a shrink before updating an allowance; normal checker
execution never rewrites the baseline.

## Runtime integration for the v0.11.0 repository Markdown checker

### Platform-neutral direct launcher contract

The root launcher self-locates the repository and the llm-shared Python
environment, accepts no interactive input, and invokes the checker with the
repository root, configuration, and baseline resolved by the checker contract.
Calling it from the repository root requires no prior `senv.bat` activation.
The same Python entry point remains callable on non-Windows hosts.

The process writes findings and policy errors to standard output or standard
error according to the documented diagnostic contract and returns zero only
for a complete passing evaluation. No network or Node lookup is attempted.

### Windows shared-gate connection

`check.bat` invokes the repository-root Markdown launcher once, captures its
exit status, reports the local success or failure message, and calls
`record_failure markdown <status>` on failure. The gate continues to its final
aggregate report so Markdown failures appear beside the other check names.

The integration does not duplicate rule configuration or baseline logic in
batch code. The direct launcher result and the shared-gate result therefore use
one policy authority.

## Acceptance cases for the v0.11.0 repository Markdown checker

| Scenario | Expected outcome | Reason |
| --- | --- | --- |
| Structured file with one `#`, two `##` sections, nested `###`, and unique titles | Heading checks pass | The complete structured outline is present |
| Structured file with no `#` | `LS001` at line 1 | The local title rule owns adapter-aware absence |
| Adapter with frontmatter `description` and no `#` | No `LS001` or `LS002` | Adapter classification removes only structured obligations |
| File with a second `#` | `MD025` at the second title | Multiple top-level titles are always forbidden |
| File jumping from `#` to `###` | `MD001` at the `###` line | The immediate parent heading is absent |
| Repeated normalized title under another parent | `LS003` at each later occurrence | Uniqueness is global across the file |
| Exact repeated heading at one later occurrence | Both `MD024` and `LS003` at that occurrence | Mandatory literal and normalized uniqueness rules report independently |
| List touching adjacent prose without a blank line | `MD032` at the list boundary | Every list block must be surrounded by blank lines |
| Raw `img` element under current configuration | No `MD033` | The configured element is allowed |
| Raw non-`img` element with no matching allowance | `MD033` at its source line | The enabled raw-HTML rule applies |
| Finding count above a matching baseline allowance | Checker failure | Residual debt may not grow |
| Finding count below a matching baseline allowance | Checker success with shrink visible in results | Debt may shrink without automatic baseline mutation |
| Unknown configuration key | Checker failure before file evaluation | Unsupported policy cannot be ignored |
| Direct launcher invoked without environment setup | Complete deterministic run | The launcher owns environment resolution |

## Documentation contract for the v0.11.0 repository Markdown checker

One focused page under `wiki/reference/` lists the supported rule catalog,
mandatory rules, configuration behavior, adapter classification, direct
launcher, diagnostic fields, `.markdownlint-baseline.json` semantics, and
shared-gate name. It
defines the exact `LS003` normalization and distinguishes it from `MD024`, and
identifies hierarchy findings as `MD001` and list-boundary findings as `MD032`.
It also tells requestors and reviewers to leave a blank line before and after
every list rendered as its own block. For requested-changes, covered-wording,
and writer-response fields inlined behind labels, it requires an opening prose
sentence followed by a blank line before any list. Published transcripts cannot
be edited by an agent to repair a later `MD032` finding.

Existing Diataxis navigation links the page in the repository order:
explanation, tutorials, how-to guides, then reference. The page remains a
reference contract and does not become an implementation walkthrough.

## Design boundaries for the v0.11.0 repository Markdown checker

This design specifies policy interpretation, document classification, data
flow, baseline semantics, diagnostic behavior, and gate integration. It leaves
file-by-file implementation sequencing, module names, detailed test placement,
and rollout commands to the implementation plan.

The checker does not edit documents, update its own baseline, fetch packages,
alter review-exchange state, or normalize caller-authored review content.
Historical debt remains visible and bounded without turning this effort into a
repository-wide Markdown rewrite.

Before this effort is committed, a human maintainer repairs the existing
`MD032` finding at line 264 of the protocol-owned design-review transcript. This
human-only prerequisite preserves the review-exchange ownership boundary and
the decision that `MD032` has no baseline allowance.

## Open questions for the v0.11.0 repository Markdown checker design

### Q01: Overlapping duplicate-heading findings

Question description: `MD024` remains mandatory for matching markdownlint
duplicate-heading semantics, while `LS003` applies a stronger normalized,
document-wide equality rule. An exact repeated heading can therefore satisfy
both rules. Should the checker report both findings or assign each repeated
heading to only one rule?

#### BBQ for Q01

Two inspectors can reject the same mislabeled box for different reasons. One
checks whether the printed label is literally repeated, while the other checks
whether labels become equal after normalizing their typography. Recording both
inspections preserves both controls, but it can look like one physical defect
was counted twice. In this picture: the box is a heading occurrence, the
literal-label inspector is `MD024`, the normalized-label inspector is `LS003`,
and the inspection record is the emitted finding set.

#### Options for Q01

- Option A1: Evaluate and report both rules independently.
  - pro: Preserves an observable result for every mandatory rule and matches
    the supported-catalog model.
  - con: One repeated heading can produce two diagnostics and two baseline
    dimensions.
- Option A2: Report `LS003` only whenever the same occurrence also matches
  `MD024`.
  - pro: Produces one concise diagnostic for the strongest rule.
  - con: Makes mandatory `MD024` enforcement invisible for overlapping cases.
- Option A3: Report `MD024` for exact duplicates and reserve `LS003` for
  normalization-only collisions.
  - pro: Produces one finding while keeping both identifiers observable across
    their distinct populations.
  - con: `LS003` no longer literally reports every normalized repeat described
    by the requirement.

#### Recommended option for Q01 (with arguments for this choice)

Option A1: Evaluate both rules independently. The requirement deliberately
keeps `MD024` mandatory while introducing `LS003` under a different namespace,
and a rule catalog is clearest when each rule has an independent result. Stable
ordering and keyed baseline counts make the additional diagnostic manageable.

#### Answer to Q01: option A1 (with reason why it must be accepted as the answer)

Option A1: Accept independent findings because it preserves the exact contract
of both rule identifiers and prevents a reporting optimization from silently
weakening the mandatory `MD024` control.

### Q02: Mandatory-rule configuration conflict

Question description: The effective policy must not allow configuration to
disable `MD024` or `MD025`, but the requirement does not say whether an attempted
disable is an invalid configuration or a valid configuration whose `false`
value is ignored. Which boundary should the checker expose?

#### BBQ for Q02

A building has two fire doors that must never be locked. A facilities file that
says to lock one door can either stop the opening inspection immediately or be
accepted while the inspector silently leaves the door unlocked. In this
picture: the facilities file is `.markdownlint.json`, the fire doors are
`MD024` and `MD025`, and opening inspection is effective-policy loading.

#### Options for Q02

- Option B1: Reject the configuration before scanning documents.
  - pro: Makes an invalid weakening attempt explicit and immediately
    actionable.
  - con: A repository with otherwise valid Markdown cannot pass until the
    configuration is repaired.
- Option B2: Ignore `false` for mandatory rules and continue with an advisory.
  - pro: Keeps the safety rule active and still completes the document scan.
  - con: The committed configuration does not describe the effective policy.
- Option B3: Ignore `false` silently and always force mandatory rules on.
  - pro: Has the smallest runtime surface.
  - con: Hides a policy conflict and can mislead maintainers.

#### Recommended option for Q02 (with arguments for this choice)

Option B1: Treat the attempted disable as a policy-loading error. This follows
the existing decision that unknown keys fail clearly and makes the declared
configuration trustworthy instead of maintaining a silent override layer.

#### Answer to Q02: option B1 (with reason why it must be accepted as the answer)

Option B1: Accept fail-fast validation because a mandatory policy and a
contradictory configuration must not coexist behind a green checker result.

### Q03: Canonical pointer adapter recognition

Question description: A short file under an approved adapter root is exempt
only when it serves as a pointer to canonical instructions. What structural
signal should distinguish a true pointer from an underspecified short document?
Of the 35 current bounded pointer candidates, 34 already contain a
repository-relative Markdown link. The remaining
`templates/code-review-answer.template.md` independently qualifies as a
`templates/` fragment because its first heading is level two, so the explicit
link contract reclassifies no current file.

#### BBQ for Q03

A sign in a lobby may point visitors to the full handbook, while a similarly
short note may merely omit important instructions. The exemption should apply
only when the destination is unambiguous. In this picture: the sign is the
bounded Markdown adapter, the handbook is the canonical instruction document,
and the destination test is the pointer classifier.

#### Options for Q03

- Option C1: Require at least one repository-relative Markdown link to a
  canonical instruction or rule, allowing only brief explanatory prose around
  it.
  - pro: Is deterministic and preserves useful human-readable adapter text.
  - con: A future pointer adapter using a different link form would need repair
    or an intentional classifier change.
- Option C2: Accept any body containing a path-like reference to another
  Markdown file.
  - pro: Supports several current prose styles.
  - con: Path-like text can classify an ordinary short document accidentally.
- Option C3: Classify every file within the approved roots and five-line bound
  as a pointer.
  - pro: Is simple and predictable by location.
  - con: Turns the line bound into a broad path exemption and stops verifying
    that the file is actually an adapter.

#### Recommended option for Q03 (with arguments for this choice)

Option C1: Require a resolvable repository-relative Markdown link to a
canonical instruction or rule and permit only explanatory prose around it. The
explicit link supplies machine evidence for the exemption while retaining the
bounded adapter style.

#### Answer to Q03: option C1 (with reason why it must be accepted as the answer)

Option C1: Accept the explicit-link contract because adapter status should be
proved by content as well as location and size.

### Q04: Reduced baseline debt behavior

Question description: An actual finding count below its baseline allowance is
valid no-growth progress, but the baseline is then stale. Should that shrink be
a passing advisory, a failing maintenance obligation, or silent success?

#### BBQ for Q04

A warehouse permit allows ten stored crates, and an inspection finds only six.
The site is compliant, but the permit can now be tightened. In this picture:
the crates are residual findings, the permit is the baseline allowance, and
the inspection result is the checker outcome.

#### Options for Q04

- Option D1: Pass and emit a distinct debt-reduced advisory for each stale key.
  - pro: Rewards cleanup while making the safe baseline reduction visible.
  - con: Adds non-finding output that consumers must distinguish.
- Option D2: Fail until every allowance equals the actual count.
  - pro: Guarantees the tracked baseline is always minimal.
  - con: Makes fixing a Markdown defect fail the gate for a separate metadata
    edit.
- Option D3: Pass silently whenever actual count is below the allowance.
  - pro: Keeps the checker output limited to failures.
  - con: Baseline debt can remain overstated indefinitely.

#### Recommended option for Q04 (with arguments for this choice)

Option D1: Pass with a deterministic debt-reduced advisory. A no-growth
baseline should never punish cleanup, while visible shrink gives maintainers a
clear follow-up without automatic file mutation.

#### Answer to Q04: option D1 (with reason why it must be accepted as the answer)

Option D1: Accept a passing advisory because it preserves green no-growth
semantics and still prevents obsolete allowances from becoming invisible.

### Q05: Tracked baseline representation

Question description: The baseline needs a versioned schema keyed by path,
rule, and count. Which tracked representation should be the public maintenance
contract?

#### BBQ for Q05

A stock ledger can be a structured register, a simple row list, or a set of
settings grouped by item. All can count inventory, but they differ in how well
people and tools detect malformed or duplicated entries. In this picture: the
stock ledger is the baseline file, an inventory row is one path-rule allowance,
and the auditor is the checker parser.

#### Options for Q05

- Option E1: Use versioned JSON with an array of explicit path, rule, and count
  records.
  - pro: Supports strict schema validation and clear future evolution.
  - con: Manual edits require JSON punctuation and quoting.
- Option E2: Use a line-oriented tab-separated format with a version header.
  - pro: Is compact and easy to diff or generate.
  - con: Needs a custom escaping and parsing contract for unusual paths.
- Option E3: Extend `.markdownlint.json` with repository-local baseline data.
  - pro: Keeps policy inputs in one file.
  - con: Mixes external rule configuration with measured repository debt and
    complicates unknown-key validation.

#### Recommended option for Q05 (with arguments for this choice)

Option E1: Use a separate repository-root `.markdownlint-baseline.json` with a
versioned schema and explicit records. It keeps measured debt separate from
rule configuration and gives the checker a strict, extensible validation
boundary.

#### Answer to Q05: option E1 (with reason why it must be accepted as the answer)

Option E1: Accept repository-root `.markdownlint-baseline.json` because baseline
integrity is easier to validate and review when every key component and the
public maintenance path are explicit.

### Q06: Diagnostic channel and line syntax

Question description: Every finding must contain path, line, rule, and reason,
but the precise syntax and the separation between findings, advisories, and
operational failures are not yet fixed. What output contract should launchers
and future tools rely on?

#### BBQ for Q06

A station display separates scheduled departures from service alerts while
using one predictable layout for every train. Mixing the two makes automation
and passengers guess what each line means. In this picture: departures are
Markdown findings, service alerts are operational errors or debt advisories,
and the display layout is the command-line output contract.

#### Options for Q06

- Option F1: Write findings as `path:line: RULE: reason` to standard output and
  write operational errors and debt advisories to standard error.
  - pro: Is source-locator friendly and gives consumers a stable channel split.
  - con: Capturing a complete human report requires both streams.
- Option F2: Write every message to standard output with textual severity
  prefixes.
  - pro: Produces one complete stream for logs.
  - con: Automated consumers must parse message kinds before extracting
    findings.
- Option F3: Emit JSON Lines for all result records.
  - pro: Gives automation a strongly structured interface.
  - con: Is less convenient for direct terminal use and editor navigation.

#### Recommended option for Q06 (with arguments for this choice)

Option F1: Use `path:line: RULE: reason` for ordered findings on standard output
and reserve standard error for operational errors and passing advisories. This
matches common source-locator expectations while keeping non-finding events out
of the finding stream.

#### Answer to Q06: option F1 (with reason why it must be accepted as the answer)

Option F1: Accept the split text contract because it satisfies the human
diagnostic requirement, remains editor-friendly, and avoids treating checker
health messages as Markdown violations.
