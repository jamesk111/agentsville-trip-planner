"""Exercise the actual notebook model and lookups without model requests."""

from copy import deepcopy
import datetime
from pathlib import Path

import nbformat
import pytest
from pydantic import ValidationError

import project_lib

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def notebook():
    return nbformat.read(ROOT / "project_starter.ipynb", as_version=4)


@pytest.fixture(scope="module")
def trip_definitions(notebook):
    namespace = {"__name__": "trip_notebook"}
    for index in (7, 8):
        exec(compile(notebook.cells[index].source, f"notebook cell {index + 1}", "exec"), namespace)
    return namespace


@pytest.fixture
def sample(trip_definitions):
    return deepcopy(trip_definitions["VACATION_INFO_DICT"])


def run_lookups(notebook, vacation):
    namespace = {"vacation_info": vacation}
    for index in (10, 11):
        exec(compile(notebook.cells[index].source, f"notebook cell {index + 1}", "exec"), namespace)
    return namespace


def test_sample_becomes_typed_trip_with_nested_travelers(trip_definitions, sample):
    vacation = trip_definitions["VacationInfo"].model_validate(sample)
    assert vacation.date_of_arrival == datetime.date(2025, 6, 10)
    assert vacation.date_of_departure == datetime.date(2025, 6, 12)
    assert vacation.budget == 130
    assert [traveler.name for traveler in vacation.travelers] == ["Yuri", "Hiro"]
    assert all(isinstance(traveler, trip_definitions["Traveler"]) for traveler in vacation.travelers)
    assert project_lib.Interest.TENNIS in vacation.travelers[0].interests
    assert vacation.model_dump(mode="json") == sample


@pytest.mark.parametrize("field", ["travelers", "destination", "date_of_arrival", "date_of_departure", "budget"])
def test_required_vacation_fields_cannot_be_omitted(trip_definitions, sample, field):
    del sample[field]
    with pytest.raises(ValidationError) as error:
        trip_definitions["VacationInfo"].model_validate(sample)
    assert error.value.errors()[0]["loc"] == (field,)


@pytest.mark.parametrize("changes", [
    {"travelers": []},
    {"destination": "   "},
    {"date_of_arrival": "not-a-date"},
    {"date_of_departure": "2025-06-09"},
    {"budget": -1},
    {"budget": 12.5},
    {"budget": True},
    {"budegt": 130},
])
def test_invalid_vacation_details_are_rejected(trip_definitions, sample, changes):
    sample.update(changes)
    with pytest.raises(ValidationError):
        trip_definitions["VacationInfo"].model_validate(sample)


@pytest.mark.parametrize("changes", [
    {"name": "   "}, {"age": -1}, {"age": True},
    {"interests": []}, {"interests": ["unsupported-interest"]},
])
def test_invalid_traveler_details_are_rejected(trip_definitions, sample, changes):
    sample["travelers"][0].update(changes)
    with pytest.raises(ValidationError):
        trip_definitions["VacationInfo"].model_validate(sample)


@pytest.mark.parametrize("arrival,departure", [
    ("2025-06-10", "2025-06-12"),
    ("2025-06-15", "2025-06-15"),
    ("2025-06-10", "2025-06-15"),
])
def test_lookups_use_validated_dates_including_both_endpoints(
    notebook, trip_definitions, sample, monkeypatch, arrival, departure
):
    sample.update(date_of_arrival=arrival, date_of_departure=departure)
    vacation = trip_definitions["VacationInfo"].model_validate(sample)
    calls = {"weather": [], "activities": []}
    real_weather = project_lib.call_weather_api_mocked
    real_activities = project_lib.call_activities_api_mocked

    def weather_spy(date, city):
        calls["weather"].append((date, city))
        return real_weather(date=date, city=city)

    def activities_spy(date, city):
        calls["activities"].append((date, city))
        return real_activities(date=date, city=city)

    monkeypatch.setattr(project_lib, "call_weather_api_mocked", weather_spy)
    monkeypatch.setattr(project_lib, "call_activities_api_mocked", activities_spy)
    result = run_lookups(notebook, vacation)
    day_count = (vacation.date_of_departure - vacation.date_of_arrival).days + 1
    expected_dates = [(vacation.date_of_arrival + datetime.timedelta(days=offset)).isoformat()
                      for offset in range(day_count)]
    assert calls["weather"] == [(date, "AgentsVille") for date in expected_dates]
    assert calls["activities"] == calls["weather"]
    assert [weather["date"] for weather in result["weather_for_dates"]] == expected_dates
    assert len(result["weather_for_dates_df"]) == day_count
    expected_activities = [activity for date in expected_dates for activity in real_activities(date, "AgentsVille")]
    assert result["activities_for_dates"] == expected_activities
    assert len(result["activities_for_dates_df"]) == len(expected_activities)


@pytest.mark.parametrize("changes,missing", [
    ({"destination": "Another City"}, "Another City"),
    ({"date_of_arrival": "2025-06-09"}, "2025-06-09"),
    ({"date_of_departure": "2025-06-16"}, "2025-06-16"),
])
def test_unavailable_dataset_fails_with_the_missing_city_or_date(
    notebook, trip_definitions, sample, changes, missing
):
    sample.update(changes)
    vacation = trip_definitions["VacationInfo"].model_validate(sample)
    with pytest.raises(ValueError, match="No weather data") as error:
        run_lookups(notebook, vacation)
    assert missing in str(error.value)


def test_missing_activities_on_a_trip_day_are_not_silently_skipped(
    notebook, trip_definitions, sample, monkeypatch
):
    real_activities = project_lib.call_activities_api_mocked

    def unavailable_one_day(date, city):
        return [] if date == "2025-06-11" else real_activities(date, city)

    monkeypatch.setattr(project_lib, "call_activities_api_mocked", unavailable_one_day)
    vacation = trip_definitions["VacationInfo"].model_validate(sample)
    with pytest.raises(ValueError, match="No activities for AgentsVille on 2025-06-11"):
        run_lookups(notebook, vacation)


def test_zero_budget_and_one_day_trip_are_valid_inputs(trip_definitions, sample):
    sample.update(budget=0, date_of_departure=sample["date_of_arrival"])
    vacation = trip_definitions["VacationInfo"].model_validate(sample)
    assert vacation.budget == 0
    assert vacation.date_of_arrival == vacation.date_of_departure
