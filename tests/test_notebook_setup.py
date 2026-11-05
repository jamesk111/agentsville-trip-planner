"""Run completed notebook stages in the registered local Jupyter kernel."""

import os
from pathlib import Path

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]


def test_completed_stages_run_in_project_kernel_without_network():
    notebook = nbformat.read(ROOT / "project_starter.ipynb", as_version=4)
    notebook.cells = notebook.cells[:24]
    notebook.cells[15] = nbformat.v4.new_code_cell(
        'travel_plan_1 = TravelPlan.model_validate_json((PROJECT_ROOT / "docs/examples/initial-plan.json").read_text(encoding="utf-8"))'
    )
    notebook.cells.append(nbformat.v4.new_code_cell("""
assert len(weather_for_dates) == 3
assert len(activities_for_dates) == 12
assert weather_for_dates[0]["date"] == vacation_info.date_of_arrival.isoformat()
assert weather_for_dates[-1]["date"] == vacation_info.date_of_departure.isoformat()
assert vacation_info.budget == 130
assert eval_results.success
assert len(eval_results.eval_functions) == 6
assert len(offline_weather_models) == 12
print("Completed stages passed: trip data, saved plan, and six evaluations.")
"""))
    notebook.cells.insert(0, nbformat.v4.new_code_cell("""
import socket

def reject_network(*args, **kwargs):
    raise AssertionError("Offline notebook replay must not make network requests")

socket.socket.connect = reject_network
socket.socket.connect_ex = reject_network

import project_lib
offline_weather_models = []

def offline_weather_completion(*, model, **kwargs):
    assert model == "gpt-4.1-mini"
    offline_weather_models.append(model)
    return "REASONING: The saved activity is suitable.\\nFINAL ANSWER: IS_COMPATIBLE"

project_lib.do_chat_completion = offline_weather_completion
"""))
    # Exported test values take precedence over a private .env, if one exists.
    environment = {**os.environ, "OPENAI_API_KEY": "voc-offline-kernel-test",
                   "OPENAI_BASE_URL": "https://openai.vocareum.com/v1"}
    NotebookClient(notebook, timeout=60, kernel_name="agentsville-trip-planner",
                   resources={"metadata": {"path": str(ROOT)}}).execute(env=environment)
    text = "".join(output.get("text", "") for cell in notebook.cells for output in cell.get("outputs", []))
    assert "Notebook dependencies imported successfully." in text
    assert "API client configured. No request has been sent." in text
    assert "VacationInfo data structure is valid!" in text
    assert "Completed stages passed: trip data, saved plan, and six evaluations." in text
