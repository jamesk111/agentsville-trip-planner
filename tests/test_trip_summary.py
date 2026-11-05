"""Check the final summary's inputs and failure handling without an API call."""
import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import nbformat
import pytest

ROOT = Path(__file__).resolve().parents[1]


def summary_function(completion):
    notebook = nbformat.read(ROOT / "project_starter.ipynb", as_version=4)
    tree = ast.parse(notebook.cells[39].source)
    tree.body = [node for node in tree.body if isinstance(node, ast.FunctionDef)]
    namespace = {"do_chat_completion": completion}
    exec(compile(tree, "summary cell", "exec"), namespace)
    return namespace["summarize_trip"]


def test_summary_sends_actual_trip_and_plan():
    completion = Mock(return_value="  A three-day trip.  ")
    summarize = summary_function(completion)
    trip = SimpleNamespace(model_dump_json=lambda: '{"travelers": ["Yuri", "Hiro"]}')
    plan = SimpleNamespace(model_dump_json=lambda: '{"total_cost": 130}')
    client = object()
    assert summarize(trip, plan, SimpleNamespace(success=True), client, "gpt-4.1-mini") == "A three-day trip."
    kwargs = completion.call_args.kwargs
    assert kwargs["client"] is client
    assert kwargs["model"] == "gpt-4.1-mini"
    prompt = kwargs["messages"][0]["content"]
    assert trip.model_dump_json() in prompt
    assert plan.model_dump_json() in prompt
    assert "Do not invent" in prompt
    assert "fictional units, with no currency" in prompt
    assert "without assuming a" in prompt
    assert "use future tense" in prompt


def test_failed_evaluation_does_not_request_summary():
    completion = Mock()
    with pytest.raises(ValueError, match="pass its evaluations"):
        summary_function(completion)(None, None, SimpleNamespace(success=False), None, None)
    completion.assert_not_called()


@pytest.mark.parametrize("response", [None, "", "  ", 123])
def test_empty_or_nontext_summary_is_rejected(response):
    completion = Mock(return_value=response)
    data = SimpleNamespace(model_dump_json=lambda: "{}")
    with pytest.raises(ValueError, match="returned no text"):
        summary_function(completion)(data, data, SimpleNamespace(success=True), None, None)
