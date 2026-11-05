# ADR 0005: Enforce evaluation order in the revision loop

- Status: accepted
- Date: November 5, 2026
- Author: James Kline

## Context

The assignment requires a THOUGHT/ACTION/OBSERVATION loop, dynamically included tool descriptions, an initial evaluation, and another evaluation before final_answer_tool. The starter can return a schema-valid final plan without checking that it is the plan that passed evaluation. Its action parser also assumes the decoded JSON is an object.

## Decision

Keep the notebook and its four tools. Build the revision prompt from the actual tool docstrings, vacation data, weather, feedback, and TravelPlan schema. Keep the manual protocol required by the assignment.

Parse one THOUGHT and one ACTION. Use the starter's json-repair dependency for minor syntax damage, then require an object with tool_name and arguments. Resolve only registered tools and bind the documented argument names before executing them. Report ordinary tool and format errors as observations. Provider errors stop the run. Retain a trace and a step limit.

Require the first executed tool to evaluate the unchanged original plan. Empty arguments to run_evals_tool mean the supplied original itinerary; revised evaluations carry a complete TravelPlan. The loop supplies the original passed to that run, so reused agents cannot accidentally evaluate an earlier run's original.

Track evaluations and the last successfully evaluated plan using canonical JSON values. Clear that success when another evaluation begins. Require at least two completed evaluations and an exact plan match before invoking final_answer_tool. Invoke the actual final-answer tool, validate its result, and reject a changed result. Reset conversation, trace, and evaluation state on every run.

Read the feedback evaluator's final label separately from its analysis. Keep its gpt-4.1 call, and independently count activities to enforce the fixed course feedback of at least two per day.

Add one schedule-consistency evaluation to the seven supplied evaluations. It checks city, full daily coverage, source weather, activity placement, duplicates, time order/overlaps, recommendation reasons, and named interest claims. Named claims must match both the traveler's preferences and the activity tags.

## Tradeoffs

An omitted original-plan argument avoids making the model copy a large known object before it can obtain any feedback. The initial live attempt spent its 15 steps on malformed or changed copies of that object. Subsequent candidate plans still have to be complete and valid.

JSON repair can recover a missing brace, but it does not establish a valid tool call or a correct plan. Structural checks, exact original/final comparisons, and evaluations still apply afterward.

The first completed live revision passed the supplied checks but attributed unstated interests in its explanations. The additional named-interest check addresses that case. Free-text weather judgments and general explanations still require review.

The notebook now runs eight evaluations: the seven supplied checks plus schedule consistency. The fixed two-activity count guard must be revisited if the course feedback text changes to a different requirement.

## Reference

[OpenAI GPT-4.1 prompting guide](https://developers.openai.com/cookbook/examples/gpt4-1_prompting_guide). The course's required manual action protocol determines this implementation's interface.
