# ADR 0006: Keep the final trip summary in text

- Status: accepted
- Date: November 5, 2026
- Author: James Kline

## Context

The last assignment step asks for a narrative summary of the trip. The supplied helper also requests speech and suppresses any speech error. That makes it hard to tell whether the audio step worked.

## Decision

Generate and display a short text summary in cell 40 after the final itinerary passes evaluation. Give the model the actual vacation information and evaluated plan. Ask it to describe each day, the total cost, and any indoor rain backup without inventing facts. Reject an empty response. Review the generated text before submission.

Keep project_lib.py unchanged. The notebook uses its existing text-completion wrapper and the same mini model as the planner. Audio is outside this submission.

## Tradeoffs

The final cell adds one text request to a complete run. It produces a readable result directly in the saved notebook without depending on speech access. The prompt limits unsupported details, but the summary still needs a manual check against the plan.
