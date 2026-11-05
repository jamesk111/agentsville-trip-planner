"""Verify final-verdict parsing and the notebook's weather evaluation path."""

import ast
import contextlib
import io
from pathlib import Path

import nbformat
import pytest

import project_lib

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def weather_namespace():
    notebook = nbformat.read(ROOT / "project_starter.ipynb", as_version=4)
    namespace = {"__name__": "weather_notebook", "client": object()}
    with contextlib.redirect_stdout(io.StringIO()):
        for index in (5, 7, 8, 13, 17):
            exec(compile(notebook.cells[index].source, f"notebook cell {index + 1}", "exec"), namespace)
    tree = ast.parse(notebook.cells[22].source)
    tree.body = [node for node in tree.body if isinstance(node, ast.FunctionDef)
                 or (isinstance(node, ast.Assign)
                     and any(isinstance(target, ast.Name) and target.id == "ACTIVITY_AND_WEATHER_ARE_COMPATIBLE_SYSTEM_PROMPT"
                             for target in node.targets))]
    exec(compile(tree, "weather evaluator definitions", "exec"), namespace)
    return namespace


@pytest.fixture
def saved_plan(weather_namespace):
    return weather_namespace["TravelPlan"].model_validate_json(
        (ROOT / "docs/examples/initial-plan.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("response,expected", [
    ("REASONING:\nIndoors.\nFINAL ANSWER:\nIS_COMPATIBLE", True),
    ("REASONING:\nOutdoors in rain.\nFINAL ANSWER:\nIS_INCOMPATIBLE", False),
    (" \nREASONING: Indoors.\nFINAL ANSWER: IS_COMPATIBLE \n", True),
    ("REASONING: IS_COMPATIBLE would be wrong here.\nFINAL ANSWER: IS_INCOMPATIBLE", False),
    ("REASONING: IS_INCOMPATIBLE is not the chosen verdict.\nFINAL ANSWER: IS_COMPATIBLE", True),
])
def test_only_the_final_verdict_determines_the_result(weather_namespace, response, expected):
    assert weather_namespace["parse_weather_verdict"](response) is expected


@pytest.mark.parametrize("response", [
    None, "", "IS_COMPATIBLE", "REASONING: Unknown. IS_COMPATIBLE",
    "FINAL ANSWER: IS_COMPATIBLE", "REASONING: \nFINAL ANSWER: IS_COMPATIBLE",
    "REASONING: Indoors.\nFINAL ANSWER: MAYBE",
    "REASONING: Indoors.\nFINAL ANSWER: IS_COMPATIBLE or IS_INCOMPATIBLE",
    "REASONING: Indoors.\nFINAL ANSWER: IS_COMPATIBLE\nExtra text",
    "REASONING: Indoors.\nFINAL ANSWER: IS_COMPATIBLE\nFINAL ANSWER: IS_INCOMPATIBLE",
    "REASONING: First. REASONING: Second.\nFINAL ANSWER: IS_COMPATIBLE",
])
def test_missing_ambiguous_or_malformed_verdicts_fail(weather_namespace, response):
    with pytest.raises(RuntimeError, match="Invalid weather response"):
        weather_namespace["parse_weather_verdict"](response)


def test_evaluator_uses_one_mini_call_per_activity(weather_namespace, saved_plan, monkeypatch):
    calls = []

    def compatible(**kwargs):
        calls.append(kwargs)
        return "REASONING: The setting suits the weather.\nFINAL ANSWER: IS_COMPATIBLE"

    monkeypatch.setattr(project_lib, "do_chat_completion", compatible)
    weather_namespace["eval_activities_and_weather_are_compatible"](weather_namespace["vacation_info"], saved_plan)
    recommendations = [(day, rec) for day in saved_plan.itinerary_days for rec in day.activity_recommendations]
    assert len(calls) == len(recommendations) == 6
    for call, (day, rec) in zip(calls, recommendations):
        assert call["model"] == "gpt-4.1-mini"
        assert call["client"] is weather_namespace["client"]
        assert call["messages"][0]["content"] == weather_namespace["ACTIVITY_AND_WEATHER_ARE_COMPATIBLE_SYSTEM_PROMPT"]
        assert rec.activity.description in call["messages"][1]["content"]
        assert day.weather.condition in call["messages"][1]["content"]


def test_incompatible_activities_are_reported_as_evaluation_failures(weather_namespace, saved_plan, monkeypatch):
    def incompatible(**kwargs):
        return "REASONING: IS_COMPATIBLE is inappropriate for this case.\nFINAL ANSWER: IS_INCOMPATIBLE"

    monkeypatch.setattr(project_lib, "do_chat_completion", incompatible)
    result = weather_namespace["get_eval_results"](
        weather_namespace["vacation_info"], saved_plan,
        [weather_namespace["eval_activities_and_weather_are_compatible"]])
    assert not result.success
    assert len(result.failures) == 1
    for day in saved_plan.itinerary_days:
        for rec in day.activity_recommendations:
            assert rec.activity.name in result.failures[0]


def test_bad_model_format_is_an_error_rather_than_a_passing_eval(weather_namespace, saved_plan, monkeypatch):
    monkeypatch.setattr(project_lib, "do_chat_completion", lambda **kwargs: "IS_COMPATIBLE")
    with pytest.raises(RuntimeError, match="Invalid weather response"):
        weather_namespace["get_eval_results"](
            weather_namespace["vacation_info"], saved_plan,
            [weather_namespace["eval_activities_and_weather_are_compatible"]])


def test_provider_error_is_not_silently_converted_to_compatibility(weather_namespace, saved_plan, monkeypatch):
    def provider_error(**kwargs):
        raise RuntimeError("provider unavailable")

    monkeypatch.setattr(project_lib, "do_chat_completion", provider_error)
    with pytest.raises(RuntimeError, match="provider unavailable"):
        weather_namespace["eval_activities_and_weather_are_compatible"](weather_namespace["vacation_info"], saved_plan)


def test_recorded_live_probe_verdicts_match_expected_results(weather_namespace):
    import json
    results = json.loads((ROOT / "docs/examples/weather-evaluation-checks.json").read_text(encoding="utf-8"))
    assert len(results["probe_results"]) == 9
    for case in results["probe_results"]:
        parsed = weather_namespace["parse_weather_verdict"](case["response"])
        assert parsed is (case["expected"] == "IS_COMPATIBLE")
        assert case["actual"] == case["expected"]


def test_saved_itinerary_passes_using_recorded_weather_responses(weather_namespace, saved_plan, monkeypatch):
    import json
    results = json.loads((ROOT / "docs/examples/weather-evaluation-checks.json").read_text(encoding="utf-8"))
    responses = iter(results["saved_plan_weather_responses"])

    def replay(**kwargs):
        recorded = next(responses)
        assert kwargs["messages"][1]["content"] == recorded["input"]
        return recorded["response"]

    monkeypatch.setattr(project_lib, "do_chat_completion", replay)
    result = weather_namespace["get_eval_results"](
        weather_namespace["vacation_info"], saved_plan,
        [weather_namespace["eval_activities_and_weather_are_compatible"]])
    assert result.success
    assert next(responses, None) is None


def test_bad_storm_day_plan_fails_using_recorded_weather_responses(weather_namespace, saved_plan, monkeypatch):
    import json
    results = json.loads((ROOT / "docs/examples/weather-evaluation-checks.json").read_text(encoding="utf-8"))
    responses = iter(results["negative_plan_weather_responses"])
    bad_activity = weather_namespace["Activity"].model_validate(
        project_lib.call_activity_by_id_api_mocked("event-2025-06-12-2"))
    saved_plan.itinerary_days[-1].activity_recommendations[0].activity = bad_activity

    def replay(**kwargs):
        recorded = next(responses)
        assert kwargs["messages"][1]["content"] == recorded["input"]
        return recorded["response"]

    monkeypatch.setattr(project_lib, "do_chat_completion", replay)
    result = weather_namespace["get_eval_results"](
        weather_namespace["vacation_info"], saved_plan,
        [weather_namespace["eval_activities_and_weather_are_compatible"]])
    assert not result.success
    assert bad_activity.name in result.failures[0]
    assert next(responses, None) is None
