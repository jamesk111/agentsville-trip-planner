"""Exercise the notebook revision loop and its evaluated-plan stopping rule."""

import ast
import contextlib
from copy import deepcopy
import io
import json
from pathlib import Path

import nbformat
import pytest

import project_lib

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def revision():
    notebook = nbformat.read(ROOT / "project_starter.ipynb", as_version=4)
    namespace = {"__name__": "revision_notebook", "client": object()}
    with contextlib.redirect_stdout(io.StringIO()):
        for index in (5, 7, 8, 10, 11, 13, 14, 17, 18, 19, 20, 21, 22, 25, 26, 27, 28, 30, 31, 33, 34):
            tree = ast.parse(notebook.cells[index].source)
            tree.body = [node for node in tree.body if isinstance(node, (ast.Import, ast.ImportFrom, ast.ClassDef, ast.FunctionDef))
                         or (isinstance(node, (ast.Assign, ast.AnnAssign)) and not any(
                             isinstance(part, ast.Call) and isinstance(part.func, (ast.Name, ast.Attribute))
                             and (getattr(part.func, "id", "") in {"get_eval_results", "ItineraryAgent", "ItineraryRevisionAgent"}
                                  or getattr(part.func, "attr", "") == "chat") for part in ast.walk(node)))]
            # Data loops and assertions are needed only in the original input cells.
            if index in (7, 8, 10, 11):
                tree = ast.parse(notebook.cells[index].source)
            exec(compile(tree, f"notebook cell {index + 1}", "exec"), namespace)
    namespace["initial"] = namespace["TravelPlan"].model_validate_json((ROOT / "docs/examples/initial-plan.json").read_text(encoding="utf-8"))
    return namespace


@pytest.fixture
def revised(revision):
    plan = revision["initial"].model_copy(deep=True)
    activity = revision["Activity"].model_validate(project_lib.call_activity_by_id_api_mocked("event-2025-06-12-1"))
    plan.itinerary_days[-1].activity_recommendations.insert(0, revision["ActivityRecommendation"](
        activity=activity, reasons_for_recommendation=["Hiro: music.", "Use the stated indoor rain backup."]))
    plan.total_cost += activity.price
    return plan


def action(name, **arguments):
    return "THOUGHT: Check the next requirement.\nACTION:\n" + json.dumps({"tool_name": name, "arguments": arguments})


def make_agent(revision, responses, outcomes):
    evaluations = []
    final_calls = []
    outcomes = iter(outcomes)

    def run_evals_tool(travel_plan):
        evaluations.append(deepcopy(travel_plan))
        success = next(outcomes)
        return {"success": success, "failures": [] if success else ["Candidate needs revision."]}

    def final_answer_tool(final_output):
        final_calls.append(deepcopy(final_output))
        return revision["TravelPlan"].model_validate(final_output)

    agent = revision["ItineraryRevisionAgent"]()
    agent.tools = [revision["calculator_tool"], revision["get_activities_by_date_tool"], run_evals_tool, final_answer_tool]
    messages = iter(responses)
    agent.get_response = lambda **kwargs: next(messages)
    return agent, evaluations, final_calls


def test_tool_description_and_returned_records_are_usable(revision):
    tool = revision["get_activities_by_date_tool"]
    description = revision["get_tool_descriptions_string"]([tool])
    for required in ("date (str)", "city (str)", "YYYY-MM-DD", "AgentsVille", "2025-06-15"):
        assert required in description
    records = tool("2025-06-12", "AgentsVille")
    assert len(records) == 4
    assert json.loads(json.dumps(records)) == records
    assert records[1]["start_time"] == "2025-06-12T12:00:00"
    assert tool("2025-06-16", "AgentsVille") == []
    assert tool("2025-06-12", "Other City") == []


def test_revision_prompt_contains_dynamic_tools_schema_and_feedback(revision):
    prompt = revision["ITINERARY_REVISION_AGENT_SYSTEM_PROMPT"]
    assert revision["get_tool_descriptions_string"](revision["ALL_TOOLS"]) in prompt
    assert json.dumps(revision["TravelPlan"].model_json_schema(), indent=2) in prompt
    assert revision["TRAVELER_FEEDBACK"] in prompt


def test_successful_cycle_executes_tools_and_returns_the_evaluated_plan(revision, revised):
    original = revision["initial"].model_dump(mode="json")
    candidate = revised.model_dump(mode="json")
    messages = [action("run_evals_tool", travel_plan=original),
                action("get_activities_by_date_tool", date="2025-06-12", city="AgentsVille"),
                action("calculator_tool", input_expression="115 + 15"),
                action("run_evals_tool", travel_plan=candidate),
                action("final_answer_tool", final_output=candidate)]
    agent, evaluations, final_calls = make_agent(revision, messages, [False, True])
    result = agent.run_react_cycle(revision["initial"], max_steps=5)
    assert result == revised
    assert evaluations == [original, candidate]
    assert final_calls == [candidate]
    assert [entry["status"] for entry in agent.trace] == ["executed"] * 4 + ["completed"]
    assert "130.0" in agent.trace[2]["observation"]
    assert all(entry["observation"].startswith("OBSERVATION:") for entry in agent.trace)


@pytest.mark.parametrize("response", [
    "", "ACTION: {}", "THOUGHT: \nACTION: {}", "THOUGHT: choose\nACTION: broken",
    "THOUGHT: choose\nACTION: []", "THOUGHT: choose\nACTION: null",
    action("calculator_tool", input_expression="1+1") + "\nACTION: {}",
    'THOUGHT: choose\nACTION: {"tool_name": "calculator_tool", "arguments": [], "extra": 1}',
    'THOUGHT: choose\nACTION: {"tool_name": 1, "arguments": {}}',
])
def test_malformed_actions_are_rejected(revision, response):
    with pytest.raises(ValueError):
        revision["ItineraryRevisionAgent"].parse_action(response)


def test_invalid_action_recovers_through_an_observation(revision, revised):
    original = revision["initial"].model_dump(mode="json")
    candidate = revised.model_dump(mode="json")
    messages = ["THOUGHT: bad\nACTION: []", action("run_evals_tool", travel_plan=original),
                action("run_evals_tool", travel_plan=candidate), action("final_answer_tool", final_output=candidate)]
    agent, _, _ = make_agent(revision, messages, [False, True])
    assert agent.run_react_cycle(revision["initial"], max_steps=4) == revised
    assert agent.trace[0]["status"] == "rejected"
    assert "object" in agent.trace[0]["observation"]


def test_first_evaluation_must_use_the_original_plan(revision, revised):
    candidate = revised.model_dump(mode="json")
    agent, evaluations, _ = make_agent(revision, [action("run_evals_tool", travel_plan=candidate)], [])
    with pytest.raises(RuntimeError, match="within 1 steps"):
        agent.run_react_cycle(revision["initial"], max_steps=1)
    assert not evaluations
    assert "unchanged original" in agent.trace[0]["observation"]


def test_final_answer_requires_an_initial_and_later_evaluation(revision, revised):
    original = revision["initial"].model_dump(mode="json")
    candidate = revised.model_dump(mode="json")
    messages = [action("run_evals_tool", travel_plan=original), action("final_answer_tool", final_output=original),
                action("run_evals_tool", travel_plan=candidate), action("final_answer_tool", final_output=candidate)]
    agent, _, finals = make_agent(revision, messages, [True, True])
    assert agent.run_react_cycle(revision["initial"], max_steps=4) == revised
    assert agent.trace[1]["status"] == "rejected"
    assert finals == [candidate]


def test_final_plan_cannot_change_after_a_passing_evaluation(revision, revised):
    original = revision["initial"].model_dump(mode="json")
    candidate = revised.model_dump(mode="json")
    changed = deepcopy(candidate)
    changed["total_cost"] -= 1
    messages = [action("run_evals_tool", travel_plan=original), action("run_evals_tool", travel_plan=candidate),
                action("final_answer_tool", final_output=changed), action("final_answer_tool", final_output=candidate)]
    agent, _, finals = make_agent(revision, messages, [False, True])
    assert agent.run_react_cycle(revision["initial"], max_steps=4) == revised
    assert agent.trace[2]["status"] == "rejected"
    assert finals == [candidate]


def test_failed_evaluation_invalidates_the_previous_passing_result(revision, revised):
    original = revision["initial"].model_dump(mode="json")
    candidate = revised.model_dump(mode="json")
    messages = [action("run_evals_tool", travel_plan=original), action("run_evals_tool", travel_plan=candidate),
                action("run_evals_tool", travel_plan=candidate), action("final_answer_tool", final_output=candidate)]
    agent, _, finals = make_agent(revision, messages, [False, True, False])
    with pytest.raises(RuntimeError, match="within 4 steps"):
        agent.run_react_cycle(revision["initial"], max_steps=4)
    assert not finals


@pytest.mark.parametrize("bad_action", [action("unknown_tool"), action("calculator_tool", wrong="1+1"),
                                        action("calculator_tool", input_expression="invalid expression")])
def test_unknown_tools_and_argument_errors_return_observations(revision, revised, bad_action):
    original = revision["initial"].model_dump(mode="json")
    candidate = revised.model_dump(mode="json")
    messages = [action("run_evals_tool", travel_plan=original), bad_action,
                action("run_evals_tool", travel_plan=candidate), action("final_answer_tool", final_output=candidate)]
    agent, _, _ = make_agent(revision, messages, [False, True])
    assert agent.run_react_cycle(revision["initial"], max_steps=4) == revised
    assert agent.trace[1]["status"] == "rejected"
    assert "Error" in agent.trace[1]["observation"]


@pytest.mark.parametrize("limit", [0, -1, True, 1.5])
def test_invalid_step_limits_fail_before_a_model_request(revision, limit):
    agent, _, _ = make_agent(revision, [], [])
    with pytest.raises(ValueError, match="positive integer"):
        agent.run_react_cycle(revision["initial"], max_steps=limit)


def test_feedback_uses_final_label_and_checks_actual_daily_counts(revision, revised, monkeypatch):
    response = "ANALYSIS: FULLY_INCORPORATED would be inaccurate.\nFINAL OUTPUT: PARTIALLY_INCORPORATED\nREASON: One day is short."
    monkeypatch.setattr(project_lib.ChatAgent, "chat", lambda *args, **kwargs: response)
    with pytest.raises(revision["AgentError"], match="not fully incorporated"):
        revision["eval_traveler_feedback_is_incorporated"](revision["vacation_info"], revision["initial"])
    response = "ANALYSIS: Every day checked.\nFINAL OUTPUT: FULLY_INCORPORATED\nREASON: All days have two."
    with pytest.raises(revision["AgentError"], match="2025-06-12"):
        revision["eval_traveler_feedback_is_incorporated"](revision["vacation_info"], revision["initial"])
    revision["eval_traveler_feedback_is_incorporated"](revision["vacation_info"], revised)


@pytest.mark.parametrize("response", [None, "", "FULLY_INCORPORATED", "ANALYSIS: Fine\nFINAL OUTPUT: UNKNOWN", "ANALYSIS: Fine\nFINAL OUTPUT: MAYBE\nREASON: Unsure"])
def test_malformed_feedback_responses_fail(revision, response):
    with pytest.raises(RuntimeError, match="Invalid feedback response"):
        revision["parse_feedback_verdict"](response)


@pytest.mark.parametrize("mutation", ["missing_day", "wrong_city", "fake_weather", "duplicate", "wrong_day", "order", "empty_reasons", "unsupported_interest"])
def test_schedule_checks_reject_gaps_and_inconsistent_content(revision, revised, mutation):
    if mutation == "missing_day":
        revised.itinerary_days.pop(1)
    elif mutation == "wrong_city":
        revised.city = "Other City"
    elif mutation == "fake_weather":
        revised.itinerary_days[-1].weather.condition = "clear"
    elif mutation == "duplicate":
        revised.itinerary_days[0].activity_recommendations.append(revised.itinerary_days[0].activity_recommendations[0])
    elif mutation == "wrong_day":
        revised.itinerary_days[0].activity_recommendations = [revised.itinerary_days[1].activity_recommendations[0]]
    elif mutation == "order":
        revised.itinerary_days[0].activity_recommendations.reverse()
    elif mutation == "unsupported_interest":
        revised.itinerary_days[0].activity_recommendations[0].reasons_for_recommendation = ["Yuri: sports."]
    else:
        revised.itinerary_days[0].activity_recommendations[0].reasons_for_recommendation = []
    with pytest.raises(revision["AgentError"]):
        revision["eval_daily_schedule_is_valid"](revision["vacation_info"], revised)


def test_original_evaluation_default_uses_the_supplied_plan(revision, revised):
    candidate = revised.model_dump(mode="json")
    messages = [action("run_evals_tool"), action("run_evals_tool", travel_plan=candidate),
                action("final_answer_tool", final_output=candidate)]
    agent, evaluations, _ = make_agent(revision, messages, [False, True])
    assert agent.run_react_cycle(revision["initial"], max_steps=3) == revised
    assert evaluations[0] == revision["initial"].model_dump(mode="json")
    assert agent.trace[0]["used_original_default"] is True


def test_minor_json_damage_is_repaired_but_action_shape_is_still_checked(revision):
    response = 'THOUGHT: Check cost.\nACTION: {"tool_name": "calculator_tool", "arguments": {"input_expression": "1+1"}'
    _, parsed = revision["ItineraryRevisionAgent"].parse_action(response)
    assert parsed == {"tool_name": "calculator_tool", "arguments": {"input_expression": "1+1"}}


def test_agent_reuse_starts_a_fresh_evaluation_history(revision, revised):
    candidate = revised.model_dump(mode="json")
    cycle = [action("run_evals_tool"), action("run_evals_tool", travel_plan=candidate),
             action("final_answer_tool", final_output=candidate)]
    agent, evaluations, _ = make_agent(revision, cycle + cycle, [False, True, False, True])
    agent.run_react_cycle(revision["initial"], max_steps=3)
    agent.run_react_cycle(revision["initial"], max_steps=3)
    assert len(agent.trace) == 3
    assert len(evaluations) == 4


def test_recorded_live_trace_replays_to_the_saved_final_plan(revision):
    record = json.loads((ROOT / "docs/examples/revision-checks.json").read_text(encoding="utf-8"))
    expected = revision["TravelPlan"].model_validate_json((ROOT / "docs/examples/revised-plan.json").read_text(encoding="utf-8"))
    outcomes = [json.loads(entry["observation"].removeprefix("OBSERVATION: "))["success"]
                for entry in record["trace"] if entry.get("action", {}).get("tool_name") == "run_evals_tool"
                and entry["status"] == "executed"]
    agent, _, _ = make_agent(revision, [entry["response"] for entry in record["trace"]], outcomes)
    assert agent.run_react_cycle(revision["initial"], max_steps=len(record["trace"])) == expected
    assert [entry["status"] for entry in agent.trace] == [entry["status"] for entry in record["trace"]]


def test_final_tool_cannot_change_the_evaluated_result(revision, revised):
    candidate = revised.model_dump(mode="json")
    messages = [action("run_evals_tool"), action("run_evals_tool", travel_plan=candidate),
                action("final_answer_tool", final_output=candidate)]
    agent, _, _ = make_agent(revision, messages, [False, True])

    def final_answer_tool(final_output):
        changed = deepcopy(final_output)
        changed["total_cost"] -= 1
        return changed

    agent.tools[-1] = final_answer_tool
    with pytest.raises(RuntimeError, match="within 3 steps"):
        agent.run_react_cycle(revision["initial"], max_steps=3)
    assert "changed the evaluated candidate" in agent.trace[-1]["observation"]


def test_provider_error_stops_the_cycle(revision):
    import httpx
    from openai import APIConnectionError

    agent, _, _ = make_agent(revision, [action("run_evals_tool")], [])

    def run_evals_tool(travel_plan):
        raise APIConnectionError(request=httpx.Request("POST", "https://example.invalid"))

    agent.tools = [run_evals_tool]
    with pytest.raises(APIConnectionError):
        agent.run_react_cycle(revision["initial"], max_steps=3)
