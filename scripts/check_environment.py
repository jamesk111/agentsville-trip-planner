"""Verify local imports and data, optionally checking credentials without inference."""

import argparse
from importlib.metadata import version
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-api", action="store_true",
                        help="Read the configured provider's model list; no text generation.")
    args = parser.parse_args()
    import ipykernel
    import json_repair
    import jupyterlab
    import nbformat
    import numexpr
    import openai
    import pandas
    import pydantic
    import dotenv
    from project_lib import call_activities_api_mocked, call_weather_api_mocked
    from check_project import inspect_notebook

    if sys.version_info[:2] != (3, 12):
        print("FAIL: use the Python 3.12 project environment.")
        return 1
    for package in ("json-repair", "numexpr", "openai", "pandas", "pydantic",
                    "python-dotenv", "ipykernel", "jupyterlab", "nbformat"):
        print(f"PASS: {package} {version(package)} imports.")
    inspect_notebook(PROJECT_ROOT / "project_starter.ipynb")
    for date in ("2025-06-10", "2025-06-11", "2025-06-12"):
        if not call_weather_api_mocked(date, "AgentsVille") or not call_activities_api_mocked(date, "AgentsVille"):
            print(f"FAIL: supplied trip data missing for {date}.")
            return 1
    print("PASS: supplied weather and activities available for all three sample trip dates.")

    if args.check_api:
        from local_setup import create_client
        try:
            with create_client() as client:
                listed = {model.id for model in client.with_options(timeout=15, max_retries=0).models.list()}
        except (openai.BadRequestError, openai.NotFoundError) as error:
            print(f"UNVERIFIED: provider rejected its model-list endpoint (HTTP {error.status_code}).")
            print("Credential validity and inference access still need a model request at the model-running stage.")
            return 1
        except Exception as error:
            print(f"FAIL: provider connection or configuration ({type(error).__name__}). "
                  "Check .env, key activation, network access, and course budget.")
            return 1
        required = {"gpt-4.1", "gpt-4.1-mini"}
        missing = required - listed
        if missing:
            print("UNVERIFIED: the provider did not list: " + ", ".join(sorted(missing)))
            print("Model listing is not proof of inference access; verify during the model-running stage.")
            return 1
        print("PASS: provider model list includes both currently configured course models; no generation requested.")
        print("Inference permissions, available budget, and generation behavior remain unverified.")
    else:
        print("SKIPPED: provider connectivity; use --check-api after configuring .env.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
