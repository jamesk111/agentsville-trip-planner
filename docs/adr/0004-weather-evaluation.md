# ADR 0004: Keep weather judgments in the LLM and parse the final verdict

- Status: accepted
- Date: November 5, 2026
- Author: James Kline

## Context

The assignment requires an LLM to compare an activity description with the weather. It also specifies a compatibility default when the facts are insufficient and says to consider indoor backups.

The starter checks verdict words anywhere in the response. An explanation that mentions a verdict can therefore affect the result even when the final answer says something else.

## Decision

Complete the weather prompt with a role, explicit judgment rules, the required REASONING and FINAL ANSWER sections, and examples for indoor, outdoor, indoor-backup, and unknown-setting cases. Keep the model call inside the supplied evaluation function, once per activity.

Read only the verdict under FINAL ANSWER. Require one explanation and one unambiguous final label. Missing, duplicate, or malformed output sections raise an error; an incompatible verdict remains an AgentError reported by the existing evaluation runner.

Use gpt-4.1-mini for weather judgments. The course starter names gpt-4.1-nano, but Vocareum rejected that model with HTTP 404 and a deprecation message on November 5, 2026. Mini is already used successfully by this course project. The [official deprecation record](https://developers.openai.com/api/docs/deprecations) lists the nano shutdown on October 23, 2026.

## Tradeoffs

The replacement changes the starter's model choice. Mini is already used successfully for planning in this project, and the weather check continues to use an LLM as required.

Strict verdict parsing catches format errors instead of silently treating them as a passing judgment. It cannot make an incorrect model judgment correct. Live cases and a deliberately incompatible plan test that behavior separately.

The assignment's insufficient-information default can accept an activity with an unknown setting. That is part of this project's evaluation policy. A stated outdoor setting during rain is enough information to return incompatibility.

The existing feedback evaluator is outside this change and will be reviewed with the revision agent.
