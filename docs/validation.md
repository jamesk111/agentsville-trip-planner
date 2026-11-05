# Validation notes

## Stage 2 — November 2, 2026

Tested on Windows using Git Bash, uv 0.11.11, and Python 3.12.3.

| Check | Result |
| --- | --- |
| Locked dependency installation | Passed. The six course libraries retain their supplied versions. |
| Installed-package compatibility | Passed: 108 installed packages checked. |
| Offline tests | Passed: 20 tests. |
| Notebook setup in a real local kernel | Passed with a fake key and outbound connections blocked in the test cells. |
| Local JupyterLab startup | Passed: interface responded over authenticated localhost access and the project kernel was listed. |
| Local JupyterLab shutdown | Passed: stopped after the startup check. |
| Notebook format and Python syntax | Passed. |
| Supplied weather/activity lookups | Passed for June 10, 11, and 12, 2025. |
| Strict completion check | Correctly fails while the seven learning TODO cells remain. |
| Vocareum model-list request | Rejected with HTTP 400. Model-list access, credential validity, and inference access are not verified by this request. |
| Actual model generation | Not run at this stage. |
| Full notebook and final evaluations | Pending implementation. |

The tests cover missing keys, placeholder keys, exported-variable precedence, endpoint validation, a Vocareum endpoint mismatch, SDK/course-helper compatibility with a mocked response, sample trip data, the unfinished-work gate, invalid notebook syntax, and the real notebook setup cells.

The Windows kernel test emitted a ZeroMQ warning about adding a selector thread for event-loop support. The test completed successfully. It is recorded here rather than hidden with a warning filter.

The first JupyterLab startup-check script waited for metadata under its parent process ID. Windows used a different server process ID. The check was corrected to identify the server by its selected local port, then passed. This was a check-script issue; no application-code change was needed.

The supplied project_lib.py is unchanged, including three existing trailing-whitespace lines. The new-file whitespace check excludes that supplied file.

The course key is stored in an ignored local .env file. No real key or executed notebook output is included in the repository. The provider listing request did not generate text. Actual model access and generation behavior will be checked when the first planner prompt is ready.

## Stage 3 — November 2, 2026

Completed the VacationInfo model and both date-based lookup cells. Traveler names and destination must be nonblank, travelers and interests cannot be empty, ages and budgets must be whole nonnegative integers, and departure cannot precede arrival. Unknown fields are rejected. The lookup cells use the validated date objects and include both endpoints.

| Check | Result |
| --- | --- |
| Full offline test suite | Passed: 47 tests, including the existing setup tests. |
| Real local notebook kernel | Passed: cells 1–12, using a fake key and blocked network connections. |
| Sample lookup results | Passed: June 10–12, 2025; three forecasts and 12 activities. |
| Alternate date ranges | Passed: one-day trip on June 15 and the full June 10–15 dataset. |
| Invalid input | Rejected: missing fields, blank values, empty travelers/interests, unsupported interests, invalid/reversed dates, negative or noninteger budget, and invalid ages. |
| Missing data | Clear failure for an unsupported city, out-of-range dates, or missing activities on one requested day. |
| Notebook format and syntax | Passed. Remaining TODO cells: 15, 23, 28, 35. |
| Environment and mock-data checks | Passed. |
| Model requests | None made in this stage. |

The same Windows ZeroMQ fallback warning appeared in the kernel test. The test passed and the kernel was shut down by the test client.

The sample weather is clear on June 10, partly cloudy on June 11, and thunderstorms on June 12. The [Stage 3 walkthrough](stage-3-trip-inputs.md) lists the retrieved activities and explains the input rules.

## Stage 4 — November 5, 2026

Completed the initial planner prompt in cell 15. It includes the role, a numbered planning process, explicit output sections, examples, the generated TravelPlan schema, and the current vacation/weather/activity context. The supplied ItineraryAgent, parser, models, and helper library remain unchanged.

| Check | Result |
| --- | --- |
| Offline suite | Passed: 53 tests, including the saved live sample replay. |
| Schema/context embedding | Passed: the prompt contains JSON matching the actual model schema and notebook data. |
| Response handling | Passed: one mocked request returns a typed plan; malformed or incomplete JSON is rejected. |
| Final prompt, live sample | Passed: 115 / 130 units. |
| Final prompt, sample repeat | Passed: 105 / 130 units. |
| Final prompt, one-day stormy trip | Passed: 30 / 30 units. |
| Five supplied Python evaluations | Passed on all three final-prompt responses. |
| Additional review | Passed: city, daily coverage, weather records, activity dates, chronology, overlaps, duplicate activity IDs, and stated interest matches. |
| Weather suitability | Manually reviewed on the recorded responses. The LLM weather prompt remains unfinished. |
| Notebook syntax/TODO scan | Passed; remaining TODO cells are 23, 28, and 35. |
| Weather/feedback model access | Not yet checked. Only planner inference is verified. |

Each generated itinerary used one request. Seven generation requests were made in this stage: four development runs and three checks of the final prompt. Development review caught an inaccurate total (110 stated, 95 calculated), explanations attributing an unstated interest, and an out-of-order activity list. The prompt was revised to require price equations, exact traveler/interest matches with an example, and final sorting.

The three passing final-prompt checks used gpt-4.1-mini. Vocareum reported the gpt-4.1-mini-2025-04-14 snapshot. The [recorded results](examples/initial-plan-checks.json) preserve the successful checks and token usage. The [saved sample](examples/initial-plan.json) is parsed model output, without manual edits to its selected activities or total. Three passing examples are limited evidence, not proof of reliability on every trip.

The sample's June 12 activity is indoors. The repeat and one-day cases also use a picnic with an explicit indoor fallback. Its source location and description remain unchanged; the fallback is described in the recommendation.

The existing Windows ZeroMQ fallback warning appeared in the offline kernel test; the test passed.

## Stage 5 — November 5, 2026

Completed the weather prompt in cell 23, with explicit rules and examples for indoor, outdoor, backup-venue, and insufficient-information cases. Added a final-verdict parser so labels mentioned in an explanation do not determine the result.

| Check | Result |
| --- | --- |
| Offline suite | Passed: 76 tests. |
| Live weather cases | Passed: 9 / 9 expected judgments. |
| Saved itinerary | Passed all six current evaluations, including six live weather judgments. |
| Deliberately incompatible itinerary | Correctly failed weather evaluation after the storm-day indoor event was replaced by the outdoor hike. The other five evaluations passed. |
| Actual model access | gpt-4.1-mini succeeded through Vocareum. The provider reported gpt-4.1-mini-2025-04-14. |
| Starter weather model | gpt-4.1-nano was rejected with HTTP 404 and model_not_found/deprecated. The model replacement is recorded in ADR 0004. |
| Local notebook replay | Passed: cells 1–24 in a real local kernel, using the saved planner result and mocked weather responses with network requests blocked. |
| Format failure cases | Correctly rejected missing, duplicate, ambiguous, and malformed verdict sections. Provider errors propagate. |
| Environment and notebook syntax | Passed. Remaining TODO cells: 28 and 35. |

The live checks used 21 successful mini-model requests and one earlier rejected nano request. The nine cases cover indoor protection, outdoor rain/storm exposure, an indoor rain backup, clear weather, unknown setting, unknown weather, an open-sided canopy, and an outdoor veranda backup. The [recorded results](examples/weather-evaluation-checks.json) include the exact inputs, responses, verdicts, and token usage.

The sample initial itinerary was reused without another planner request. The negative plan was a separate copy; its recalculated total was 120 of the 130-unit budget, leaving weather as its only evaluation failure. It did not replace the saved initial plan.

The existing Windows ZeroMQ fallback warning appeared in the kernel test; the test passed.

## Stage 6 — November 5, 2026

Completed the activity lookup docstring and revision prompt. Tool descriptions are generated from the actual functions. The prompt includes the required role, feedback, tool parameters, THOUGHT/ACTION/OBSERVATION protocol, TravelPlan schema, initial evaluation, later evaluation, and final-answer exit.

| Check | Result |
| --- | --- |
| Offline suite | Passed: 120 tests. |
| Final live revision | Passed in 8 model steps, within the 15-step limit. |
| Saved final cost | 130 / 130 units, up from the 115-unit initial plan. |
| Activities per day | 3 on June 10, 2 on June 11, and 2 on June 12. |
| All supplied evaluations | Passed all seven, including the gpt-4.1 traveler-feedback judgment. |
| Added schedule evaluation | Passed city, coverage, source weather, placement, duplicates, timing, reasons, and named interest claims. |
| Exact final candidate | The returned plan matched the successful evaluation candidate. The actual final_answer_tool was invoked. |
| Independent final evaluation | Passed all eight checks again after the agent returned. |
| Recorded trace replay | Passed with the actual tools and replayed model responses. |
| Local kernel replay | Passed cells 1–38 with the saved initial plan, recorded revision messages, mocked weather/feedback replies, and blocked network access. |
| Strict completion check | Passed: no TODO markers remain. |
| Environment check | Passed. |

The final recorded run made 47 model requests: 8 revision responses, 34 weather judgments, and 5 feedback judgments, including the independent final evaluation. Vocareum reported gpt-4.1-mini-2025-04-14 and gpt-4.1-2025-04-14. The [saved plan](examples/revised-plan.json) and [trace/check results](examples/revision-checks.json) retain the actual output and model usage.

The loop rejected an initial lookup before evaluating the original plan. Later evaluations rejected an out-of-order activity list and an unsupported interest claim. The model corrected both before final_answer_tool was allowed to return. Four large-plan actions needed the starter's JSON-repair helper; repaired objects were still checked against the tool interface, schema, and stopping rules.

Development checks exposed copying/format problems in a 15-step run and inaccurate preference explanations in a completed candidate. These led to the documented original-plan default and the named-interest check. A trace-check harness initially assumed the first response had been an executed action; it was corrected to inspect the first executed tool, preserving rejected responses in the trace.

The feedback evaluator now reads its final label separately from its analysis and also counts activities for the fixed course feedback. Schedule consistency is an additional evaluation, bringing the current list to eight while preserving all seven supplied checks. Decisions and tradeoffs are in ADR 0005.

The existing Windows ZeroMQ fallback warning appeared in the kernel test; the test passed. The helper library remains unchanged.

## Rubric status

All six graded criteria are implemented and checked. The full fresh live notebook run, narrative summary, final saved-output review, and submission ZIP are still pending. The recorded local replay does not replace that final live run.

Next: run the complete notebook from a fresh kernel, review the result against the rubric, prepare the narrative summary, and package the submission without credentials or the local environment.
