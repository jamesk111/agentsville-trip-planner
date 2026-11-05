# Rubric checklist

Source: [Udacity project rubric](https://learn.udacity.com/cd14526?version=1.1.28&lessonKey=39b0a6da-dfbf-4314-ac52-1301c532334b&project=rubric), reviewed November 2, 2026. Requirements below are paraphrased. Cell numbers count all cells from 1, not execution counts.

**Status after Stage 6:** all six graded criteria are implemented and checked. The final fresh live notebook run and submission package remain pending. Completed items have implementation and test results recorded below; setup checks alone do not complete the rubric.

## General prompt design

### R1. Initial itinerary prompt — cell 15

- [x] Assign a travel-planner role.
- [x] Guide detailed daily planning through instructions or examples.
- [x] Specify JSON matching TravelPlan.
- [x] Supply vacation information, weather, and activities as context.

Verified November 5, 2026. The prompt in cell 15 includes the role, planning sequence, output format, examples, generated schema, and all context. The [planner tests](../tests/test_initial_planner.py) verify the embedded data and response handling. Three live checks of the final prompt passed; the [Stage 4 walkthrough](stage-4-initial-planner.md) and [recorded results](examples/initial-plan-checks.json) document the outputs and limits. Each itinerary used one request.

### R2. Weather compatibility prompt — cell 23

- [x] Define the evaluator's role and task.
- [x] Specify the exact expected output format.
- [x] Include relevant examples for compatible and incompatible activities.

Verified November 5, 2026. The prompt includes four examples and the assignment's insufficient-information rule. Nine live judgment cases passed. The saved itinerary passed all six current evaluations; an outdoor hike substituted on the storm day was rejected. [Weather tests](../tests/test_weather_evaluator.py) cover final-verdict parsing and evaluation behavior. See the [walkthrough](stage-5-weather-evaluation.md) and [recorded responses](examples/weather-evaluation-checks.json). Vocareum rejected the starter nano model, so this evaluator uses the working course mini model; see [ADR 0004](adr/0004-weather-evaluation.md).

## Agent reasoning and tool use

### R3. Activity lookup tool description — cell 28

- [x] Explain the tool's purpose and when to use it.
- [x] Document inputs, types, and formats: date as YYYY-MM-DD and city as a string.

Verified November 5, 2026. Cell 28 documents purpose, date/city names and types, ISO format, data limits, and returned records. Tests check the generated description and JSON-serializable lookup results. The [live trace](examples/revision-checks.json) includes a successful June 12 lookup.

### R4. Revision prompt and ReAct use — cell 35

- [x] State the revision role and task.
- [x] Explain the THINK-ACT-OBSERVE cycle.
- [x] List all four tools with purposes and argument requirements.
- [x] Specify ACTION as {"tool_name": "...", "arguments": {...}}.
- [x] Require completion through final_answer_tool.
- [x] Require run_evals_tool before final_answer_tool.

Verified November 5, 2026. Cell 35 includes the role, revision task, dynamic tool descriptions, full output protocol, feedback, weather, vacation details, and TravelPlan schema. The [live trace](examples/revision-checks.json) shows original evaluation, lookup, calculation, failed candidate evaluations, a passing evaluation, and final_answer_tool returning that exact candidate. Raw JSON syntax damage is handled with the starter's repair helper before action validation. [Revision tests](../tests/test_revision_agent.py) cover format errors, unknown tools, arguments, step limits, initial-evaluation order, stale/changed candidates, and final-tool mutation.

The instructions are stricter than the rubric in two places: include tool descriptions dynamically, and evaluate both initially and again before finishing. I will follow those instructions as well.

## Structured output validation

### R5. VacationInfo — cells 9, 11, and 12

- [x] Define the fields to match the supplied traveler/vacation JSON.
- [x] Use the validated arrival and departure dates to retrieve weather and activities.

Verified November 2, 2026. [Model and lookup tests](../tests/test_trip_inputs.py) cover required fields, invalid input, missing data, and one-day, sample, and full-dataset date ranges. The [kernel test](../tests/test_notebook_setup.py) executes cells 1–12 with network requests blocked and checks three forecasts and 12 activities. See the [sample results](stage-3-trip-inputs.md).

### R6. TravelPlan schema — cells 15 and 35

- [x] Include the TravelPlan JSON schema in at least one output-producing system prompt.

Verified November 5, 2026. Cell 15 embeds TravelPlan.model_json_schema(); the context test compares the embedded JSON with the actual model schema. The revision prompt now includes it as well.

## Assignment and final-run checks

These checks supplement the six graded criteria. They do not replace them. The itinerary constraints below must be checked again on the final revised plan, even when an initial plan has passed them.

- [x] Download and inspect the official starter files.
- [x] Configure a local environment and keep credentials outside the notebook.
- [x] Verify planner inference through Vocareum with gpt-4.1-mini.
- [x] Verify weather inference through Vocareum with gpt-4.1-mini.
- [x] Verify inference with the traveler-feedback model.
- [x] Generate the initial TravelPlan and inspect the source-data matches.
- [x] Keep the city and dates correct; include each trip day.
- [x] Keep activity details unchanged from the supplied records.
- [x] Calculate total cost correctly and stay within the 130-unit sample budget.
- [x] Include activities relevant to both travelers.
- [x] Handle weather constraints, including indoor backups.
- [x] Incorporate feedback requesting at least two activities per day.
- [x] Check duplicate activities and overlapping times.
- [x] Exercise invalid tool calls and the revision step limit.
- [x] Pass all seven supplied final evaluations plus schedule consistency.
- [x] Replay completed cells 1–38 in a local kernel using recorded/mocked model responses.
- [ ] Run the completed notebook from a fresh kernel and record the result.
- [ ] Review saved outputs and the submission ZIP contents.

Optional narration is outside the six graded criteria. It is disabled by default.

## Evidence record

Update [validation.md](validation.md) as work progresses. For each completed criterion, record the relevant test, notebook output, or trace. A TODO scan is only an unfinished-work check; it does not grade prompt quality or trip correctness.
