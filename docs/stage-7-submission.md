# Stage 7: Final run and submission

## What ran

On November 5, 2026, I ran the full notebook from a fresh local Python 3.12.3 kernel using the configured Vocareum key. No saved or mocked model replies were used in that run. All 31 code cells executed in order. The notebook retains the actual outputs, final evaluation result, activity tables, and generated text summary.

| Check | Result |
| --- | --- |
| Final cost | 103 of 130 fictional units; 27 left over. |
| Activities per day | Two on each of June 10, 11, and 12, 2025. |
| Revision loop | Five steps, ending through final_answer_tool. |
| Final evaluations | All seven supplied checks plus schedule consistency passed. |
| Weather | The storm-day picnic uses its stated Harmony Hall indoor backup; the evening event is indoors. |
| Source records and timing | All six selected activities match the supplied records and do not overlap. |
| Traveler interests | Yuri has tennis, cooking, and technology matches. Hiro has art and music matches. |
| Summary | Generated from the checked plan and reviewed against its dates, events, cost, interests, and weather. |

The daily costs are 35, 38, and 30 units. Each activity price is counted once, as in the starter evaluations.

## Reading this result

The fresh initial plan already had two activities on every day and passed the feedback check. The revision agent evaluated it, looked up June 12 activities, checked the 103-unit sum with the calculator, evaluated it again, and returned the same plan. It did not need to add an activity in this run.

Some model decision text incorrectly described June 12 as having only one activity. The actual plan had two, and both the initial and final evaluation results were correct. The saved trace preserves that inconsistency. The two large-plan actions also needed JSON syntax repair before tool argument and plan validation. This is why the tool results and returned data matter more than the model's explanation.

The earlier [Stage 6 example](stage-6-itinerary-revision.md) demonstrates an actual correction: a 115-unit plan was revised to 130 units after feedback and rejected candidates. I kept that example and its replay tests alongside the final run.

An earlier complete pass reached the final summary, but the separate results-export cell had a quoting error. The summary also invented a relationship between the travelers and used dollars instead of fictional units. I corrected the export and tightened the summary instructions, then ran the whole notebook again. The saved submission notebook is that second complete run. The summary's facts were checked manually; its requested word range is guidance, not a validated constraint.

## Saved evidence

- [Final plan](examples/final-plan.json)
- [Final run results and five-step trace](examples/final-live-run.json)
- [Generated trip summary](examples/final-trip-summary.md)
- [Rubric checklist](rubric-checklist.md)

## Submission contents

The ZIP contains the executed notebook and all supporting source, setup, configuration templates, tests, and documentation. It excludes the real API key, local environment, Git history, caches, logs, and development artifacts. The supplied project_lib.py is unchanged.

The archive contains 44 files. Every archived file was compared with its source, and the notebook has 31 consecutive execution counts with no error outputs. The credential and attribution scans passed.

From a clean extracted copy, bash scripts/setup.sh installed the locked environment and registered its local kernel. All 126 offline tests passed, including the full notebook replay with network access blocked. Environment and strict completion checks passed too. The existing Windows ZeroMQ fallback warning appeared; it did not fail the test. The real key was never copied into that extracted folder.

The course upload is a manual step.
