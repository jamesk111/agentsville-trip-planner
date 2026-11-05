# Stage 6: Tools and itinerary revision

The activity lookup description and revision prompt are complete. The saved revision starts from the 115-unit initial plan, adds a suitable activity on June 12, and returns a 130-unit plan with at least two activities per day.

## Tool descriptions

The prompt gets the four tool descriptions directly from the Python functions. The activity lookup docstring explains when to call it, its date and city arguments, the supported date range, and its return value. Lookup results use JSON date/time strings.

The first evaluation can use empty arguments to evaluate the supplied original plan. Later evaluations carry the complete candidate plan. The loop resolves that default from the original passed to the current run.

## Recorded live run

| Step | Requested tool | Result |
| --- | --- | --- |
| 1 | get_activities_by_date_tool | Rejected: initial evaluation must come first |
| 2 | run_evals_tool | Traveler feedback was not fully incorporated. The traveler requested at least two activities per day. While June 10 and June 11 each meet or exceed this requirement with three and two activities respectively, June 12 only has one activity, so the feedback is only partially incorporated. Days with fewer than two activities: ['2025-06-12'] |
| 3 | get_activities_by_date_tool | Retrieved activities for June 12 |
| 4 | calculator_tool | Calculated total: 130 |
| 5 | run_evals_tool | Activities are out of order or overlap on 2025-06-12. |
| 6 | run_evals_tool | Unsupported interest claim for Hiro in event-2025-06-12-1. Use only these matches: ['music']. |
| 7 | run_evals_tool | All evaluations passed |
| 8 | final_answer_tool | Returned the evaluated plan |

The first lookup request was blocked before execution. The agent then evaluated the original plan, found the missing activity, retrieved options, and checked the cost. Evaluations rejected an out-of-order day and an unsupported interest claim before accepting the corrected candidate. The final-answer tool returned that same candidate.

The course uses a manual THOUGHT/ACTION protocol. The saved responses contain both sections. Large plan arguments needed the starter's JSON-repair helper on steps 5, 6, 7, 8. The repaired objects still had to pass action-shape, argument, schema, evaluation-order, and final-plan checks.

## Revised plan

| Date | Activities | Daily cost |
| --- | --- | --- |
| 2025-06-10 | FutureTech Breakfast Meet-Up; Serve & Savor: Tennis and Taste Luncheon; AgentsVille Twilight Writing Escape | 55 |
| 2025-06-11 | Tech Lunch & Learn: AI Frontiers; Palette & Palate: Art Meets Cooking Experience | 45 |
| 2025-06-12 | Soundtrack Picnic: Lunchtime Movies & Melodies; Tech & Film Fusion Night | 30 |

Total: **130 of 130 units**. Daily activity counts are **3, 2, and 2**. The added Soundtrack Picnic has a stated indoor rain backup at Harmony Hall, and its recommendation explains that backup. Source activity records stay unchanged.

The [revised JSON](examples/revised-plan.json) and [recorded trace](examples/revision-checks.json) preserve the actual result. It was checked again after the agent returned.

## Stopping rules

Python requires the original plan to be evaluated first. It tracks the last successfully evaluated candidate and rejects a final answer if the candidate changes, a later evaluation fails, or fewer than two evaluations have completed. The actual final_answer_tool is called before the validated result is returned. A reused agent starts with fresh conversation and evaluation state.

Tool and format errors become observations that the agent can correct. Provider errors stop execution. The notebook limits a revision run to 15 steps.

## Evaluations

The final plan passed the seven supplied evaluations plus one added schedule-consistency check. The added check covers city, daily coverage, source weather, activity placement, duplicate activities, ordering/overlap, recommendation reasons, and named interest claims. The feedback evaluator still uses gpt-4.1; a separate daily count also enforces the fixed two-activity requirement.

The final recorded run used 47 model requests: 8 revision responses, 34 weather judgments, and 5 feedback judgments. This includes the independent final evaluation. Earlier development runs exposed copying/format problems and inaccurate preference descriptions; those findings led to the original-plan default, complete response example, and added interest checks.

## Verification and rubric

All 120 offline tests passed. The local kernel replay runs cells 1–38 with the saved initial plan and recorded revision responses. Weather and feedback replies are mocked for that replay, and network access is blocked. Separate live requests provide the evidence above.

R3 and R4 are complete, so all six graded rubric criteria are implemented and checked. The final stage remains: a fresh complete live notebook run, a final output review, the narrative summary, and submission packaging. See [ADR 0005](adr/0005-revision-loop.md) for the implementation decisions.
