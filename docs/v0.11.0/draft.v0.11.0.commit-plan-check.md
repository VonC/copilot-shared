# Expose commit-plan validation without committing

- Type: feature-request
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md

`validate_commit_plan(blocks, staged_paths)` is already the public,
side-effect-free validation API. Step 2 of the code-reviewer effort created it
precisely so that review and batch execution share one commit-plan decision, and
`tools/git_batch_commit_workflow.py` calls it before changing the index. No
launcher exposes it, so a reviewer who must assess `a.commit` cannot run it.

## Why a reviewer needs it

Every code-review request carries the same scope sentence: inspect and amend
`a.commit` only when membership, grouping, order, scope, or the conventional
subject no longer matches the staged work, and do not commit. The canonical
reviewer instruction turns that into a readiness-floor result, requiring the
reviewer to keep "staged membership, ordering, scope, and conventional subjects
accurate" and to classify `a.commit` as one of six floor results.

Both statements ask for a decision that the shipped validator already makes, and
neither names a command that produces it. That is the same shape as the Step 3
finding about the implementation check: an instruction describing in prose what
an executable boundary should decide. A reviewer following the instruction today
either eyeballs the plan or writes a throwaway script that imports the validator.

The one shipped entry point cannot help, because it commits. `--root-a-commit`
runs the root plan workflow and refuses to combine with `--dry-run`:

```text
Cannot combine --root-a-commit with --dry-run
```

So the only way to reach the validator on the root plan is the path that resets
and commits, which the reviewer is explicitly forbidden to take.

## Shape of the need

A launcher that validates the root `a.commit` against the exact staged path set
and reports the typed groups and diagnostics without touching the index, plus
the reviewer instruction naming it where it currently says to assess `a.commit`.

## Questions for the requirement and design phases

- Whether this is a new launcher over the existing public validator or a
  `--root-a-commit --dry-run` combination inside the batch-commit tool, which
  today is rejected.
- What the output contract is, given that the reviewer must quote it as
  readiness-floor evidence and the requestor must act on it.
- Whether the writer-side `group-commits-msg` step should use the same command
  before publishing a request, so both roles judge the plan identically.
- Whether the check belongs in the shared gate at all, since `a.commit` is a
  transient working file rather than committed content.
