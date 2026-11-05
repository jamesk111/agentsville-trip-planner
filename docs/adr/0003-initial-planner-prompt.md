# ADR 0003: Generate the initial plan in one request

- Status: accepted
- Date: November 5, 2026
- Author: James Kline

## Context

The assignment asks for one LLM call to generate the initial itinerary. Its response must include JSON that validates against the supplied TravelPlan model. The prompt needs the vacation details, weather, and activity records; the model cannot look up missing facts at this stage.

## Decision

Keep the supplied ItineraryAgent and TravelPlan models. Complete ITINERARY_AGENT_SYSTEM_PROMPT in the notebook with a travel-planner role, a numbered planning process, cost and weather examples, the generated TravelPlan schema, and JSON versions of the retrieved context.

Use the course's gpt-4.1-mini model. Ask for the supplied ANALYSIS and FINAL OUTPUT sections: a brief planning summary with daily price sums, followed by one fenced JSON object. The summary records the plan's decisions and arithmetic; it is not used as a substitute for validation.

Copy selected activity records unchanged. Put weather accommodations and interest matches in reasons_for_recommendation. Describe only preferences actually listed for the named traveler.

Parse the response with the supplied notebook code, validate it with Pydantic, and run the five available Python evaluations before proceeding. The weather-judgment prompt and revision agent remain separate stages.

## Tradeoffs

A schema in the prompt guides the model but does not force correct output. The parser rejects malformed or incomplete plans, and content checks catch problems that a valid schema permits.

The first live attempt returned a valid structure but a wrong total: 110 stated versus 95 in selected activity prices. The prompt now requires daily price equations and a total recomputed after the final activity choices. A later review also found an unstated interest attributed to a traveler; the prompt now uses an explicit traveler/interest format and an intersection example. A final sorting reminder addresses an out-of-order activity list found during review.

Separate test requests check repeatability. Each itinerary still comes from one request. A few passing examples do not guarantee every possible trip will work.

## Reference

[OpenAI GPT-4.1 prompting guide](https://developers.openai.com/cookbook/examples/gpt4-1_prompting_guide). The project keeps the course model and API interface.
