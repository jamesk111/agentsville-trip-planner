# Stage 5: Weather evaluation

The weather prompt is complete. The notebook now asks an LLM whether each activity fits the weather, reads its final verdict, and reports incompatible activities through the existing evaluation runner.

## Judgment rules

- Indoor activities are compatible with rain and thunderstorms.
- Outdoor activities without an indoor backup are incompatible with rain and thunderstorms.
- A stated indoor rain backup makes an activity compatible with those conditions.
- An open-air canopy or veranda is still outdoors.
- If the activity setting or weather facts are insufficient, assume compatibility. This is the assignment's stated policy.

The prompt includes a role, task, exact output format, and four examples. It returns a short REASONING explanation and one FINAL ANSWER label.

## Live checks

| Case | Expected judgment | Result |
| --- | --- | --- |
| indoor-storm | Compatible | Passed |
| outdoor-rain | Incompatible | Passed |
| outdoor-storm | Incompatible | Passed |
| indoor-backup-storm | Compatible | Passed |
| outdoor-clear | Compatible | Passed |
| unknown-setting | Compatible | Passed |
| unknown-weather | Compatible | Passed |
| open-canopy-storm | Incompatible | Passed |
| outdoor-rain-backup | Incompatible | Passed |

All nine cases passed. The cases include supplied activity records and separate examples for missing information and open-air shelters. [Inputs](../tests/fixtures/weather-cases.json) and [recorded responses](examples/weather-evaluation-checks.json) are saved in the repository.

## Itinerary checks

The saved initial itinerary passed all six evaluations now available: dates, cost arithmetic, source activity records, traveler interests, budget, and weather compatibility.

I then replaced the June 12 indoor film event with the supplied outdoor writing-and-hiking activity. The modified plan cost 120 of 130 units and still passed the five Python evaluations. The weather evaluation correctly rejected it for the thunderstorm. The saved initial plan was left unchanged.

The live checks made 21 successful gpt-4.1-mini requests: nine individual cases, six weather judgments for the saved plan, and six for the deliberately incompatible plan. One earlier request to the starter nano model was rejected before generation.

## Model change

Vocareum returned HTTP 404 for gpt-4.1-nano, with a model-deprecated message. The weather evaluator now uses the course's working gpt-4.1-mini model. The [decision record](adr/0004-weather-evaluation.md) explains the change and links the official deprecation notice.

## Why the parser changed

The starter searches the whole response for verdict words. That can misread an explanation that mentions both labels. The parser now uses the final verdict only and requires one nonempty explanation and one final label. Missing sections, duplicate sections, unknown verdicts, and extra text after the verdict produce an error. A provider error also propagates.

The assignment's unknown-facts default applies to the model's judgment. A malformed model response is an execution error.

## Local verification

All 76 offline tests passed. These include verdict parsing, evaluation failure handling, replay of real responses, and a local Jupyter kernel running cells 1–24 with the saved planner output and mocked weather responses. Network requests are blocked in that kernel test. The live checks above provide the separate evidence for model judgments.

## Rubric progress

R2 is complete. R1, R2, R5, and R6 are now checked off. The activity-tool description (R3) and revision prompt (R4) remain unfinished. The later feedback evaluator will add the seventh evaluation.

To run the completed portion in JupyterLab, execute cells 1–24. Cell 23 checks weather; cell 24 reruns the six current evaluations. Both cells make weather-model requests. Stop before the unfinished activity-tool description in cell 28.

Next: document the activity lookup tool, complete the revision prompt, and trace the tool-use loop through a successful final answer.
