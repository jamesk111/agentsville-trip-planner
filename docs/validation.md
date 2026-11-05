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

## Rubric status

R1, R5, and R6 are complete. R2, R3, and R4 remain pending. The sample initial plan still has only one activity on June 12, which meets the initial requirement. The revision stage must handle the later request for at least two activities per day and pass all final evaluations.

Next: complete the LLM weather-evaluation prompt, then the activity-tool description and revision prompt. Full-kernel execution, the final revision trace, and submission packaging remain pending.
