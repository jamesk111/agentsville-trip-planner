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

## Rubric status

No graded criterion is complete yet. The remaining TODO cells are 9, 11, 12, 15, 23, 28, and 35. The [rubric checklist](rubric-checklist.md) identifies the implementation and verification work for each criterion.

The next stage defines VacationInfo and retrieves the trip data. That will address R5 after its model and lookup checks pass.
