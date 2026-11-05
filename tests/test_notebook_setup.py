"""Replay the completed notebook stages in the registered local kernel."""

import os
from pathlib import Path

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]


def test_completed_stages_run_in_project_kernel_without_network():
    notebook = nbformat.read(ROOT / "project_starter.ipynb", as_version=4)
    notebook.cells[15] = nbformat.v4.new_code_cell(
        'travel_plan_1 = TravelPlan.model_validate_json((PROJECT_ROOT / "docs/examples/initial-plan.json").read_text(encoding="utf-8"))'
    )
    notebook.cells.insert(0, nbformat.v4.new_code_cell(r'''
import socket
import json
from pathlib import Path
import project_lib

def reject_network(*args, **kwargs):
    raise AssertionError("Offline notebook replay must not make network requests")

socket.socket.connect = reject_network
socket.socket.connect_ex = reject_network
record = json.loads((Path.cwd() / "docs/examples/revision-checks.json").read_text(encoding="utf-8"))
revision_responses = iter(entry["response"] for entry in record["trace"])
offline_weather_models = []
offline_feedback_models = []
offline_summary_models = []

def offline_completion(*, model, messages, **kwargs):
    prompt = messages[0]["content"]
    if "Write a short narrative summary" in prompt:
        assert model == "gpt-4.1-mini"
        offline_summary_models.append(model)
        return "Yuri and Hiro visit AgentsVille for three days, with activities costing 130 units."
    if "THINK-ACT-OBSERVE" in prompt:
        assert model == "gpt-4.1-mini"
        if messages[-1]["content"].startswith("Here is the itinerary for revision: "):
            return 'THOUGHT: Evaluate the original plan.\nACTION: {"tool_name": "run_evals_tool", "arguments": {}}'
        return next(revision_responses)
    if model == "gpt-4.1":
        offline_feedback_models.append(model)
        plan = json.loads(messages[-1]["content"].split("Revised Travel Plan:", 1)[1].strip())
        complete = all(len(day["activity_recommendations"]) >= 2 for day in plan["itinerary_days"])
        verdict = "FULLY_INCORPORATED" if complete else "PARTIALLY_INCORPORATED"
        return f"ANALYSIS: Counted the activities on each day.\nFINAL OUTPUT: {verdict}\nREASON: Daily counts checked."
    assert model == "gpt-4.1-mini"
    offline_weather_models.append(model)
    return "REASONING: The saved activity is suitable.\nFINAL ANSWER: IS_COMPATIBLE"

project_lib.do_chat_completion = offline_completion
'''))
    notebook.cells.append(nbformat.v4.new_code_cell('''
assert len(weather_for_dates) == 3
assert len(activities_for_dates) == 12
assert eval_results_2.success
assert len(eval_results_2.eval_functions) == 8
assert all(len(day.activity_recommendations) >= 2 for day in travel_plan_2.itinerary_days)
assert travel_plan_2.total_cost == 130
assert len(offline_weather_models) >= 12
assert len(offline_feedback_models) >= 3
assert offline_summary_models == ["gpt-4.1-mini"]
assert "Yuri and Hiro" in trip_summary
assert itinerary_revision_agent.trace[-1]["status"] == "completed"
print("Completed stages passed: revised plan and all eight evaluations.")
'''))
    environment = {**os.environ, "OPENAI_API_KEY": "voc-offline-kernel-test",
                   "OPENAI_BASE_URL": "https://openai.vocareum.com/v1"}
    NotebookClient(notebook, timeout=60, kernel_name="agentsville-trip-planner",
                   resources={"metadata": {"path": str(ROOT)}}).execute(env=environment)
    text = "".join(output.get("text", "") for cell in notebook.cells for output in cell.get("outputs", []))
    assert "Notebook dependencies imported successfully." in text
    assert "Completed stages passed: revised plan and all eight evaluations." in text
