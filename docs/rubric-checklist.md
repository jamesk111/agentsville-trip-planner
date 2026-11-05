# Rubric checklist

Source: [Udacity project rubric](https://learn.udacity.com/cd14526?version=1.1.28&lessonKey=39b0a6da-dfbf-4314-ac52-1301c532334b&project=rubric), reviewed November 2, 2026. Requirements below are paraphrased. Cell numbers count all cells from 1, not execution counts.

**Status after Stage 4:** R1, R5, and R6 are complete. R2, R3, and R4 are pending. Completed items have implementation and test results recorded below; setup checks alone do not complete the rubric.

## General prompt design

### R1. Initial itinerary prompt — cell 15

- [x] Assign a travel-planner role.
- [x] Guide detailed daily planning through instructions or examples.
- [x] Specify JSON matching TravelPlan.
- [x] Supply vacation information, weather, and activities as context.

Verified November 5, 2026. The prompt in cell 15 includes the role, planning sequence, output format, examples, generated schema, and all context. The [planner tests](../tests/test_initial_planner.py) verify the embedded data and response handling. Three live checks of the final prompt passed; the [Stage 4 walkthrough](stage-4-initial-planner.md) and [recorded results](examples/initial-plan-checks.json) document the outputs and limits. Each itinerary used one request.

### R2. Weather compatibility prompt — cell 23

- [ ] Define the evaluator's role and task.
- [ ] Specify the exact expected output format.
- [ ] Include relevant examples for compatible and incompatible activities.

Evidence needed: final prompt and tests covering an indoor activity, outdoor activity in bad weather, and an explicit indoor backup. Follow the assignment's instruction to assume compatibility when evidence is insufficient. Check the model's final verdict rather than treating its explanation as proof.

## Agent reasoning and tool use

### R3. Activity lookup tool description — cell 28

- [ ] Explain the tool's purpose and when to use it.
- [ ] Document inputs, types, and formats: date as YYYY-MM-DD and city as a string.

Evidence needed: completed docstring, generated tool description, and a working lookup for a supported date/city.

### R4. Revision prompt and ReAct use — cell 35

- [ ] State the revision role and task.
- [ ] Explain the THINK-ACT-OBSERVE cycle.
- [ ] List all four tools with purposes and argument requirements.
- [ ] Specify ACTION as {"tool_name": "...", "arguments": {...}}.
- [ ] Require completion through final_answer_tool.
- [ ] Require run_evals_tool before final_answer_tool.

Evidence needed: final prompt and an actual trace showing valid actions, useful observations, revisions, a successful evaluation of the final candidate, and the final-answer action. Match the returned plan to the evaluated candidate.

The instructions are stricter than the rubric in two places: include tool descriptions dynamically, and evaluate both initially and again before finishing. I will follow those instructions as well.

## Structured output validation

### R5. VacationInfo — cells 9, 11, and 12

- [x] Define the fields to match the supplied traveler/vacation JSON.
- [x] Use the validated arrival and departure dates to retrieve weather and activities.

Verified November 2, 2026. [Model and lookup tests](../tests/test_trip_inputs.py) cover required fields, invalid input, missing data, and one-day, sample, and full-dataset date ranges. The [kernel test](../tests/test_notebook_setup.py) executes cells 1–12 with network requests blocked and checks three forecasts and 12 activities. See the [sample results](stage-3-trip-inputs.md).

### R6. TravelPlan schema — cells 15 and 35

- [x] Include the TravelPlan JSON schema in at least one output-producing system prompt.

Verified November 5, 2026. Cell 15 embeds TravelPlan.model_json_schema(); the context test compares the embedded JSON with the actual model schema. I still plan to include it in the revision prompt as recommended.

## Assignment and final-run checks

These checks supplement the six graded criteria. They do not replace them. The itinerary constraints below must be checked again on the final revised plan, even when an initial plan has passed them.

- [x] Download and inspect the official starter files.
- [x] Configure a local environment and keep credentials outside the notebook.
- [x] Verify planner inference through Vocareum with gpt-4.1-mini.
- [ ] Verify inference with the weather and traveler-feedback models.
- [x] Generate the initial TravelPlan and inspect the source-data matches.
- [ ] Keep the city and dates correct; include each trip day.
- [ ] Keep activity details unchanged from the supplied records.
- [ ] Calculate total cost correctly and stay within the 130-unit sample budget.
- [ ] Include activities relevant to both travelers.
- [ ] Handle weather constraints, including indoor backups.
- [ ] Incorporate feedback requesting at least two activities per day.
- [ ] Check duplicate activities and overlapping times.
- [ ] Exercise invalid tool calls and the revision step limit.
- [ ] Pass all seven final notebook evaluations.
- [ ] Run the completed notebook from a fresh kernel and record the result.
- [ ] Review saved outputs and the submission ZIP contents.

Optional narration is outside the six graded criteria. It is disabled by default.

## Evidence record

Update [validation.md](validation.md) as work progresses. For each completed criterion, record the relevant test, notebook output, or trace. A TODO scan is only an unfinished-work check; it does not grade prompt quality or trip correctness.
