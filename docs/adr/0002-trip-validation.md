# ADR 0002: Validate trip inputs before retrieving data

- Status: accepted
- Date: November 2, 2026
- Author: James Kline

## Context

The input-model rubric requires VacationInfo to match the supplied JSON and provide the dates used by the weather and activity lookups. The supplied dataset covers one city and six dates. Empty lookup results would leave the planner without the information it needs.

## Decision

Keep Traveler and VacationInfo in the notebook. Use Pydantic to parse dates and interests, reject missing or unknown fields, require nonempty travelers and interests, strip surrounding whitespace, and reject blank names or destinations. Age and budget must be whole nonnegative integers; booleans are rejected. Departure must be on or after arrival.

Keep city and dataset-date restrictions out of the model. Check availability in the lookup cells, which use the validated dates and include both endpoints. Stop with the missing city/date in the error if a forecast or a day's activities are unavailable.

Test the actual notebook definitions and retrieval cells. Also run the completed input stage in a real local kernel with network requests blocked.

## Tradeoffs

A well-formed trip can still be impossible to plan. A zero budget is valid input, for example, even if the dataset has no free activities. Budget feasibility belongs to planning and evaluation.

Rejecting unknown fields catches typos but requires explicit model changes if the input shape grows. Keeping definitions in the notebook also leaves tests dependent on its cell order. That is acceptable while preserving the course starter structure; splitting the models into a module would be a separate change.

The missing-data checks assume each trip day needs weather and activity options. They stop early rather than asking the planner to invent missing records.
