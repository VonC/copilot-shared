# Selectable document layouts for project efforts

## User story for document layouts

As a project maintainer using the llm-shared document workflow, I want to
choose how versioned effort documents are organized under `docs/` when a draft
is processed, so that each project can use a flat, minor-version, full-version,
or nested minor/full-version structure without breaking later workflow tools.

The selected organization must remain stable for the complete effort. Drafts,
requirements, designs, plans, validation plans, review commands, and release
checks must all refer to the same directory without requiring the user to pass
that directory again at every phase.

## Branch revision that introduces document layouts

Before the `docs` branch, draft processing and document writers primarily
assumed that effort files lived directly under `docs/`. Partial support for a
version directory did not provide one shared organization contract across
`process-draft`, `new_draft`, `pw`, `oqm`, implementation handoffs, release
preparation, the packaged Codex skills, and the Diátaxis wiki.

The `docs` branch introduces one common layout rule, makes the layout a
`process-draft` choice, carries the selected directory through the document
workflow, and adds a stateless document locator based on version, slug, and
document type.

## Current behavior before document layouts in v0.10.0

- `process-draft` does not ask where versioned effort documents should live.
- `new_draft` relocates a classified draft to the flat `docs/` directory.
- Writers and implementation instructions reconstruct flat document paths
  instead of following the canonical draft's parent directory.
- `pw` needs branch, memory, or draft-path context to select the effort folder
  and does not expose a direct version/slug/type lookup.
- Document discovery does not consistently cover minor-version and nested
  minor/full-version directories.
- `oqm` and release preparation can miss a document when it is stored below a
  supported version directory.
- The workflow documentation describes flat paths as if they were the only
  supported organization.

## Expected document-layout behavior in v0.10.0

### Layout choice during draft processing

`process-draft` must present these four choices after the target version is
known and before branch placement is selected:

| Choice | Tool value | Effort directory for `vX.Y.Z` |
| --- | --- | --- |
| Flat | `flat` | `docs/` |
| Minor version | `minor` | `docs/vX.Y/` |
| Full version | `version` | `docs/vX.Y.Z/` |
| Minor and full version | `minor-version` | `docs/vX.Y/vX.Y.Z/` |

The full-version layout is the recommended choice. The workflow must not add a
topic subdirectory because version and topic are already present in document
filenames.

### Layout persistence through the effort

The parent directory of the canonical classified draft is the persisted layout
choice for that effort. Requirement, design, plan, and validation-plan writers
must write sibling files in that directory. Review, consolidation,
implementation, and release instructions must use the exact paths supplied by
the workflow rather than rebuild paths under flat `docs/`.

An item created from an umbrella draft must inherit the umbrella layout kind.
The child version is used to compute its own directory for that same layout.

### Folder-independent document lookup

A caller that knows a version, topic slug, and document type must be able to
find the document without also knowing its directory. The prompt-workflow
launcher must expose:

```text
pw document <version> <slug> <type>
```

Supported types are `draft`, `requirement`, `feature-request`, `issue`,
`design`, `plan`, and `validation-plan`. The logical `requirement` type accepts
either a feature-request or issue filename. Hyphens and underscores in a slug
must compare as equivalent.

Lookup is exact for the supplied slug and must check only the four directories
supported for the supplied version. A missing document returns the
not-applicable result. More than one exact match across supported layouts is an
error; the tool must not choose a copy by modification time or directory
order.

## Acceptance criteria for document layouts

1. `new_draft --from-draft` accepts `--docs-layout` with `flat`, `minor`,
   `version`, and `minor-version` values.
2. Each value places the canonical draft in the corresponding directory for
   its confirmed `vX.Y.Z` version.
3. `process-draft` asks for the documentation layout and passes the selected
   value to `new_draft`.
4. The classified draft and every later effort document remain siblings; no
   extra topic directory is introduced.
5. Umbrella continuation preserves the umbrella's layout kind for each child
   effort.
6. `pw` discovers documents in all four layouts and prefers the canonical
   draft directory during state-based workflow routing.
7. `pw document <version> <slug> <type>` resolves one exact path without Git
   branch state, a canonical draft path, or `a.prompt_memory`.
8. Stateless lookup treats hyphens and underscores as equivalent, rejects an
   unsupported version or type, reports no match as not applicable, and fails
   when duplicate exact matches exist.
9. `oqm` accepts exact repository-relative paths in every supported layout.
10. Release preparation scans effort documents, drafts, and validation plans
    in every supported layout.
11. Root instructions and their packaged Codex copies describe the same path
    behavior, and the packaged plugin contains the shared layout rule it links
    to.
12. The Diátaxis wiki explains the human layout choice, teaches it in the
    draft-to-requirement tutorial, shows how to locate a document, and records
    the exact layout and selector contracts in reference pages.
13. Automated tests cover draft placement, workflow discovery, stateless
    lookup, ambiguity handling, exact open-question paths, plugin packaging,
    and Diátaxis coverage.

## Concrete examples for document layouts

For version `v0.10.0` and slug `document-layouts`, the same plan may be stored
at any one of these paths:

```text
docs/plan.v0.10.0.document-layouts.md
docs/v0.10/plan.v0.10.0.document-layouts.md
docs/v0.10.0/plan.v0.10.0.document-layouts.md
docs/v0.10/v0.10.0/plan.v0.10.0.document-layouts.md
```

This invocation must print whichever unique path exists:

```text
pw document v0.10.0 document_layouts plan
```

If both the flat path and the full-version path exist, the command must report
an ambiguity instead of selecting one.

## Code and workflow references for document layouts

- `rules/docs_layout.md`: defines the four layout values and persistence rule.
- `tools/new_draft_models.py`: maps a confirmed version and layout to an effort
  directory.
- `tools/new_draft_workflow.py`: accepts `--docs-layout` and moves the draft.
- `tools/prompt_workflow_docs.py`: discovers supported directories and resolves
  exact version/slug/type selectors.
- `tools/prompt_workflow.py`: exposes the `pw document` command.
- `tools/prompt_workflow_skill.py`: keeps generated paths beside the canonical
  draft.
- `tools/open_questions_md.py`: resolves exact document paths for `oqm`.
- `instructions/process-draft.md`: owns the human layout choice and passes it
  to `new_draft`.
- `instructions/prepare-release.md`: scans nested effort documents during
  feature completion and release preparation.
- `wiki/reference/artifact-files.md`: records the document-layout and selector
  contracts for users and tool authors.
