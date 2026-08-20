# v0.11.0 independent review-mode documentation coverage

This effort record starts with Step 1 and stays versioned while later plan
steps replace pending rows with exact page, test, command, or scope evidence.
It is acceptance evidence outside the wiki, not a Diataxis page.

## Acceptance evidence after Step 3

| Criterion | Evidence type | Status | Step 3 evidence or remaining work |
| --- | --- | --- | --- |
| AC01 | Page evidence | Partial | `README.md` and `wiki/README.md` link the authority explanation; later pages remain pending |
| AC02 | Page evidence | Complete | `wiki/explanation/independent-review-mode-and-human-authority.md` defines requestor, reviewer, and human authority |
| AC03 | Page evidence | Complete | `wiki/tutorials/09-run-your-first-specification-review.md` and `wiki/tutorials/10-run-your-first-implementation-code-review.md` are cross-linked first-use journeys |
| AC04 | Page evidence | Complete | Five focused how-to pages cover opt-in, both review families, results, authorized continuation, reclaim, and stopped recovery |
| AC05 | Page evidence | Pending | Step 4 adds the central contract reference |
| AC06 | Page and source evidence | Partial | Tutorials and task guides pin family terms, intermediate rounds, exact human choices, and continuation; Step 4 adds lookup evidence |
| AC07 | Page evidence | Complete | `wiki/how-to/recover-an-independent-review.md` assigns expired, stopped, forced, and resolution paths to their owners and stop rules |
| AC08 | Page and source evidence | Partial | The explanation names the three canonical policy owners; Step 4 adds adapter coverage |
| AC09 | Page evidence | Partial | Navigation retains explanation, tutorials, how-to guides, then reference and adds all five task guides; Step 4 reference remains pending |
| AC10 | Validation evidence | Pending | Step 5 records project, whitespace, link, path, and manual Markdown checks |
| AC11 | Scope evidence | Pending | Step 5 records that no deferred launcher or checker was added |
| AC12 | Coverage evidence | Partial | This table contains every criterion and inventory candidate; later steps replace pending rows |

## Candidate inventory dispositions after Step 3

Each candidate remains pending until Step 4 assesses whether its established
subject supports a narrow discovery link.

| Candidate | Status | Disposition or next action |
| --- | --- | --- |
| `wiki/reference/skills-catalog.md` | Pending | Assess skill discovery in Step 4 |
| `wiki/reference/artifact-files.md` | Pending | Assess review artifact discovery in Step 4 |
| `wiki/reference/aliases-and-launchers.md` | Pending | Assess launcher discovery in Step 4 |
| `wiki/reference/templates.md` | Pending | Assess template discovery in Step 4 |
| `wiki/reference/automation-and-direct-invocation.md` | Pending | Assess ownership discovery in Step 4 |
| `wiki/reference/repository-layout.md` | Pending | Assess repository-location discovery in Step 4 |

## Step 1 executable evidence

- `tests/unit/tools/test_review_mode_docs_acceptance/test_review_mode_docs_acceptance_tdd.py` pins entry-point discovery, Diataxis order, terminology, logos, canonical authority links, local links, named paths, and this closed enumeration.
- `tests/unit/tools/test_review_mode_docs_acceptance/conftest.py` bounds repository reads to declared paths, ignores external URLs, resolves relative local files, and checks fragments against target headings.
- Step 1 verification completed with 1,882 tests, `cov=100`,
  `outliers=0`, and `exit=0`; both earlier focused fix runs also closed green.

## Step 2 executable evidence

- `test_step_2_tutorials_append_numbers_cross_link_and_resolve` pins filenames,
  conceptual order, reciprocal links, generic logos, and local targets.
- `test_step_2_tutorials_show_two_agent_sessions_and_round_trip` pins the
  requestor and reviewer sessions, bounded wait, returned `paths.answer`,
  intermediate answer, and replacement round.
- `test_step_2_family_evidence_and_human_choices_stay_distinct` pins the
  specification identity and choices separately from code-review immutable
  evidence, validation comparison, `a.commit`, and commit choices.
- `test_step_2_coverage_records_completed_tutorial_evidence` pins the completed
  AC03 row, both page paths, and the pending Step 3 boundary.

## Step 3 executable evidence

- `test_step_3_five_how_to_pages_assign_all_seven_goals` pins the five-page
  topology, seven goals, wiki links, generic logos, and local targets.
- `test_step_3_procedures_follow_returned_paths_and_exit_contract` pins final
  JSON authority, returned `paths`, the artifact-editing prohibition, all three
  exit meanings, and owning-action authorization.
- `test_step_3_recovery_separates_reclaim_from_human_operations` pins ordinary
  reclaim before the marked human section and the forced command preconditions.
- `test_step_3_coverage_records_task_and_recovery_evidence` pins completed AC04
  and AC07 rows while leaving the Step 4 reference boundary pending.

The five Step 3 guides are:

- `wiki/how-to/enable-independent-review-mode.md`
- `wiki/how-to/run-specification-review.md`
- `wiki/how-to/run-implementation-code-review.md`
- `wiki/how-to/read-independent-review-results-and-continue.md`
- `wiki/how-to/recover-an-independent-review.md`
