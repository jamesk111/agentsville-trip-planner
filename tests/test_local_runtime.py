"""Check SDK compatibility and the local mock-data path without API calls."""

import json

import httpx
import pytest
from openai import OpenAI

from project_lib import call_activities_api_mocked, call_weather_api_mocked, do_chat_completion


def test_sdk_and_course_completion_wrapper_work_together():
    requests = []

    def respond(request):
        requests.append(request)
        return httpx.Response(200, json={
            "id": "test-completion", "object": "chat.completion", "created": 0,
            "model": "gpt-4.1-mini",
            "choices": [{"index": 0, "message": {"role": "assistant", "content": "test response"}, "finish_reason": "stop"}],
        })

    with OpenAI(api_key="unit-test", base_url="https://example.invalid/v1",
                http_client=httpx.Client(transport=httpx.MockTransport(respond))) as client:
        answer = do_chat_completion(messages=[{"role": "user", "content": "test"}],
                                    model="gpt-4.1-mini", client=client)
    assert answer == "test response"
    assert len(requests) == 1
    assert requests[0].url.path == "/v1/chat/completions"
    assert json.loads(requests[0].content)["messages"] == [{"role": "user", "content": "test"}]


@pytest.mark.parametrize("date", ["2025-06-10", "2025-06-11", "2025-06-12"])
def test_sample_trip_has_usable_weather_and_activity_data(date):
    weather = call_weather_api_mocked(date, "AgentsVille")
    activities = call_activities_api_mocked(date, "AgentsVille")
    assert weather["date"] == date
    assert weather["city"] == "AgentsVille"
    assert len(activities) >= 2
    assert all(activity["start_time"].startswith(date) for activity in activities)
    assert all(activity["price"] >= 0 for activity in activities)


def test_completion_wrapper_requires_explicit_client_and_model():
    with pytest.raises(ValueError, match="client"):
        do_chat_completion(messages=[], model="gpt-4.1-mini")
    with pytest.raises(ValueError, match="model"):
        do_chat_completion(messages=[], client=object())
