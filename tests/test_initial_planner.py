"""Check the notebook planner's schema context and response handling offline."""

from copy import deepcopy
import contextlib
import io
from pathlib import Path

import nbformat
import pytest
from pydantic import ValidationError

from project_lib import call_activities_api_mocked

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def planner():
    notebook = nbformat.read(ROOT / "project_starter.ipynb", as_version=4)
    namespace = {"__name__": "planner_notebook", "client": object()}
    with contextlib.redirect_stdout(io.StringIO()):
        for index in (5, 7, 8, 10, 11, 13, 14):
            exec(compile(notebook.cells[index].source, f"notebook cell {index + 1}", "exec"), namespace)
    return namespace


@pytest.fixture
def sample_plan(planner):
    days = []
    for weather in planner["weather_for_dates"]:
        activity = deepcopy(call_activities_api_mocked(weather["date"], "AgentsVille")[-1])
        days.append({"date": weather["date"],
                     "weather": {key: weather[key] for key in ("temperature", "temperature_unit", "condition")},
                     "activity_recommendations": [{"activity": activity, "reasons_for_recommendation": ["Test fixture"]}]})
    return {"city": "AgentsVille", "start_date": "2025-06-10", "end_date": "2025-06-12",
            "total_cost": sum(day["activity_recommendations"][0]["activity"]["price"] for day in days),
            "itinerary_days": days}


def test_prompt_embeds_actual_schema_and_context(planner):
    import json
    prompt = planner["ITINERARY_AGENT_SYSTEM_PROMPT"]
    for tag, expected in (
        ("travel_plan_schema", planner["TravelPlan"].model_json_schema()),
        ("vacation_info", planner["vacation_info"].model_dump(mode="json")),
        ("weather_records", planner["weather_for_dates"]),
        ("activity_records", planner["activities_for_dates"]),
    ):
        embedded = prompt.split(f"<{tag}>")[1].split(f"</{tag}>")[0]
        assert json.loads(embedded) == expected


def test_one_request_produces_a_validated_plan(planner, sample_plan, monkeypatch):
    import json
    calls = []

    def fake_chat(self, **kwargs):
        calls.append(kwargs)
        return "ANALYSIS:\nTest summary.\nFINAL OUTPUT:\n```json\n" + json.dumps(sample_plan) + "\n```"

    monkeypatch.setattr(planner["ItineraryAgent"], "chat", fake_chat)
    agent = planner["ItineraryAgent"](client=object(), model=planner["MODEL"])
    plan = agent.get_itinerary(planner["vacation_info"])
    assert plan == planner["TravelPlan"].model_validate(sample_plan)
    assert len(calls) == 1
    assert json.loads(calls[0]["user_message"]) == planner["vacation_info"].model_dump(mode="json")
    assert calls[0]["model"] == "gpt-4.1-mini"


@pytest.mark.parametrize("response", ["not JSON", "{}", "```json\n{broken}\n```"])
def test_malformed_or_incomplete_output_is_rejected(planner, monkeypatch, response):
    monkeypatch.setattr(planner["ItineraryAgent"], "chat", lambda self, **kwargs: response)
    agent = planner["ItineraryAgent"](client=object(), model=planner["MODEL"])
    with pytest.raises(ValidationError):
        agent.get_itinerary(planner["vacation_info"])


def test_recorded_live_plan_passes_supplied_checks(planner):
    import datetime
    notebook = nbformat.read(ROOT / "project_starter.ipynb", as_version=4)
    namespace = planner.copy()
    plan = planner["TravelPlan"].model_validate_json((ROOT / "docs/examples/initial-plan.json").read_text(encoding="utf-8"))
    namespace["travel_plan_1"] = plan
    with contextlib.redirect_stdout(io.StringIO()):
        for index in (17, 18, 19, 20, 21):
            exec(compile(notebook.cells[index].source, f"notebook cell {index + 1}", "exec"), namespace)
        result = namespace["get_eval_results"](namespace["vacation_info"], plan, [namespace[name] for name in (
            "eval_start_end_dates_match", "eval_total_cost_is_accurate", "eval_total_cost_is_within_budget",
            "eval_itinerary_events_match_actual_events", "eval_itinerary_satisfies_interests")])
    assert result.success, result.failures
    vacation = namespace["vacation_info"]
    assert plan.city == vacation.destination
    expected_dates = [vacation.date_of_arrival + datetime.timedelta(days=n)
                      for n in range((vacation.date_of_departure - vacation.date_of_arrival).days + 1)]
    assert [day.date for day in plan.itinerary_days] == expected_dates
    seen = set()
    for day in plan.itinerary_days:
        assert day.activity_recommendations
        previous_end = None
        for rec in day.activity_recommendations:
            activity = rec.activity
            assert activity.activity_id not in seen
            seen.add(activity.activity_id)
            assert activity.start_time.date() == day.date == activity.end_time.date()
            assert activity.start_time < activity.end_time
            assert previous_end is None or previous_end <= activity.start_time
            previous_end = activity.end_time
            for reason in rec.reasons_for_recommendation:
                for traveler in vacation.travelers:
                    prefix = traveler.name + ": "
                    if reason.startswith(prefix):
                        claimed = set(reason[len(prefix):].rstrip(".").split(", "))
                        assert claimed <= set(traveler.interests) & set(activity.related_interests)
