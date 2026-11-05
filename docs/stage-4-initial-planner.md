# Stage 4: The first generated itinerary

The initial planner now runs through the Vocareum API. It receives the vacation details, retrieved weather and activities, and the JSON schema generated from TravelPlan. Each itinerary comes from one model request.

## What the prompt does

The prompt gives the agent a travel-planner role and a numbered planning process. It asks for daily coverage, source activity records, stated interest matches, weather choices, nonoverlapping times, and a checked price sum. It includes examples for costs, interest matches, and indoor backups.

The response keeps the starter format: a short ANALYSIS section followed by FINAL OUTPUT with one fenced JSON object. The supplied parser reads that object and Pydantic validates it. The context and schema are inserted from the current notebook values, so they change with the trip.

## Saved sample result

| Date | Activities | Daily cost |
| --- | --- | --- |
| 2025-06-10 | FutureTech Breakfast Meet-Up; Serve & Savor: Tennis and Taste Luncheon; AgentsVille Twilight Writing Escape | 55 |
| 2025-06-11 | Tech Lunch & Learn: AI Frontiers; Palette & Palate: Art Meets Cooking Experience | 45 |
| 2025-06-12 | Tech & Film Fusion Night | 15 |

Total: **115 of 130 units**. The [saved JSON](examples/initial-plan.json) is the actual parsed model output.

The June 12 activity is held indoors. Manual review of the other passing checks confirmed the Soundtrack Picnic describes an indoor fallback at Harmony Hall. The automatic LLM weather evaluation is still a separate TODO.

The sample has one activity on June 12. That is allowed for the initial plan. The later revision stage must incorporate the request for at least two per day.

## Live checks of the final prompt

| Case | Model requests | Cost / budget | Result |
| --- | --- | --- | --- |
| sample | 1 | 115 / 130 | Passed |
| sample-repeat | 1 | 105 / 130 | Passed |
| one-day | 1 | 30 / 30 | Passed |

All three responses validated against TravelPlan and passed the five supplied Python evaluations: matching trip boundaries, accurate cost, cost within budget, source activity integrity, and traveler interest coverage. Additional checks covered city, every trip day, weather record values, activity dates, ordering, overlapping times, duplicate activities, and nonempty explanations. Named interest-match explanations were checked against the intersection of traveler interests and activity tags.

The requested model was gpt-4.1-mini; the provider reported gpt-4.1-mini-2025-04-14. [Recorded check results](examples/initial-plan-checks.json) include model names, token counts, selected activities, and evaluation results. These are three passing examples, not a guarantee for arbitrary trips.

## What the review caught

Four earlier development requests exposed a wrong total, unstated interests attributed to travelers, and an out-of-order activity list. The first response stated 110 although its activities added up to 95. The final prompt requires daily price sums, exact traveler/interest matches with an example, and a final sorting pass. Seven generation requests were made in this stage, with one request per generated itinerary.

The saved sample is the validated response, with Pydantic normalizing date/time representations.

## Rubric progress

R1 is complete: role, guided daily planning, JSON output, and the required context are in the prompt and were checked with real responses. R6 is complete because this system prompt includes the generated TravelPlan schema. R5 was completed in Stage 3.

R2, R3, and R4 remain pending: the weather-evaluation prompt, activity-tool docstring, and revision prompt. The full notebook, feedback evaluator, revision trace, and final itinerary checks are still ahead.

## Run this stage

In JupyterLab, run cells 1–22 in order. Cell 16 makes the initial planner request. Stop before cell 23, which contains the unfinished weather prompt. The live development checks used a 6,000-token output limit, a 120-second request timeout, and no automatic retries; these were test-run settings, not changes to the supplied notebook client defaults.

The offline tests replay the saved sample through the supplied checks without using the API.

Next: complete the LLM weather-evaluation prompt and test its judgments on indoor, outdoor-only, and indoor-backup activities.
