# v0.11.0 independent review-mode documentation coverage

This effort record starts with Step 1 and stays versioned while later plan
steps replace pending rows with exact page, test, command, or scope evidence.
It is acceptance evidence outside the wiki, not a Diataxis page.

## Acceptance evidence after Step 4

| Criterion | Evidence type | Status | Step 4 evidence or remaining work |
| --- | --- | --- | --- |
| AC01 | Page evidence | Complete | `README.md` and `wiki/README.md` lead to the connected explanation, tutorials, how-to guides, and central reference |
| AC02 | Page evidence | Complete | `wiki/explanation/independent-review-mode-and-human-authority.md` defines requestor, reviewer, and human authority |
| AC03 | Page evidence | Complete | `wiki/tutorials/09-run-your-first-specification-review.md` and `wiki/tutorials/10-run-your-first-implementation-code-review.md` are cross-linked first-use journeys |
| AC04 | Page evidence | Complete | Five focused how-to pages cover opt-in, both review families, results, authorized continuation, reclaim, and stopped recovery |
| AC05 | Page evidence | Complete | `wiki/reference/independent-review-mode-contract.md` defines marker, identity, artifacts, states, operations, outcomes, and exits |
| AC06 | Page and source evidence | Complete | The tutorials, guides, and central reference distinguish both review modes, automated rounds, and all four human choices |
| AC07 | Page evidence | Complete | `wiki/how-to/recover-an-independent-review.md` assigns expired, stopped, forced, and resolution paths to their owners and stop rules |
| AC08 | Page and source evidence | Complete | The explanation and central reference state the user contract, link canonical policy, and record the three-host adapter matrix with the absent Claude wrapper |
| AC09 | Page evidence | Complete | Navigation retains explanation, tutorials, how-to guides, then reference and links every delivered page in its matching category |
| AC10 | Validation evidence | Pending | Step 5 records project, whitespace, link, path, and manual Markdown checks |
| AC11 | Scope evidence | Pending | Step 5 records that no deferred launcher or checker was added |
| AC12 | Coverage evidence | Partial | This table contains every criterion and inventory candidate; later steps replace pending rows |

## Candidate inventory dispositions after Step 4

Each candidate's existing subject supports a narrow discovery entry. None
copies the central contract or canonical policy.

| Candidate | Status | Disposition or next action |
| --- | --- | --- |
| `wiki/reference/skills-catalog.md` | Update | Link the coordinator and family skill inventory to the adapter matrix |
| `wiki/reference/artifact-files.md` | Update | Add transcript, transient exchange, and code-evidence manifest entries plus the central reference link |
| `wiki/reference/aliases-and-launchers.md` | Update | Add the six exchange and family launchers plus the central reference link |
| `wiki/reference/templates.md` | Update | Inventory all eight shared, family, and transcript templates and link the central reference |
| `wiki/reference/automation-and-direct-invocation.md` | Update | Add the normal workflow owner and direct diagnostic boundary plus the central reference link |
| `wiki/reference/repository-layout.md` | Update | Add adapter gaps and executable review locations plus the central reference link |

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

## Step 4 executable evidence

- `test_step_4_reference_pins_every_state_and_fatal_payload` derives the
  fifteen typed states and pins the separate `disabled` and `fatal` rows,
  including the fatal exit-2 shape and retry action.
- `test_step_4_reference_pins_result_artifact_and_human_contract` pins the
  seven mandatory result fields, six returned paths, three exits, four human
  choices, and standard-output authority.
- `test_step_4_reference_pins_reviewed_outcomes_and_sources` pins the exact
  24-value v0.11.0 outcome snapshot and its construction sources.
- `test_step_4_adapters_and_inventory_dispositions_are_complete` pins every
  host row and verifies that all six inventory decisions have matching links.
- `wiki/reference/independent-review-mode-contract.md` owns the lookup contract;
  the six inventory pages carry only subject-matched entries and links.
