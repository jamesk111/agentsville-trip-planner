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

## Rubric status

R5 is complete: the vacation model matches the sample JSON, and both lookups use its validated dates. R1, R2, R3, R4, and R6 remain pending. There is no generated itinerary yet, and provider inference access remains unverified.

Next: complete the initial planner prompt and include the TravelPlan schema, weather, activities, and traveler context. That stage will address R1 and part of R6, with actual model output required before marking them complete.
