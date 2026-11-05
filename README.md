# AgentsVille Trip Planner

My project for Udacity's **Prompting for Effective LLM Reasoning and Planning** course, part of the FedEx IT Practitioner learning plan.

The goal is to generate a trip itinerary, check it, and let a second agent revise it using tools. The destination is fictional. Weather and activity data come from the supplied Python file; model responses come from the Vocareum API.

**Current status:** complete and ready for submission. The full notebook ran from a fresh local kernel on November 5, 2026. The final plan costs 103 of 130 units, has two activities per day, and passed all eight evaluations. The saved notebook includes the live outputs and trip summary.

The [rubric checklist](docs/rubric-checklist.md) links each requirement to its evidence. [Validation notes](docs/validation.md) record what has actually been tested.

## How it works

The notebook follows this sequence:

1. Validate the travelers, dates, interests, destination, and budget with Pydantic.
2. Load weather and activities for those dates.
3. Ask ItineraryAgent for a plan that matches the TravelPlan schema.
4. Check dates, prices, budget, source activity records, interests, and weather.
5. Give ItineraryRevisionAgent the plan and traveler feedback. It can calculate costs, look up activities, run evaluations, and return a final plan.
6. Check the revised plan again and display it.
7. Generate a short text summary from the checked plan.

The revision agent uses a ReAct loop: the model chooses an action, Python runs the tool, and the result goes back to the model as an observation. The notebook caps the full revision run at 15 steps. Python checks evaluation order and returns only the candidate that passed the final evaluation.

Pydantic checks the shape and types of the data. Separate evaluations check the trip itself. Passing one does not guarantee passing the other.

The code stays in the course notebook for now. Setup and tests live alongside it. Decisions and tradeoffs are in [ADR 0001: local setup](docs/adr/0001-local-notebook-setup.md), [ADR 0002: trip validation](docs/adr/0002-trip-validation.md), [ADR 0003: initial planner](docs/adr/0003-initial-planner-prompt.md), [ADR 0004: weather evaluation](docs/adr/0004-weather-evaluation.md), [ADR 0005: revision loop](docs/adr/0005-revision-loop.md), and [ADR 0006: trip summary](docs/adr/0006-trip-summary.md).

## Files

| File | Purpose |
| --- | --- |
| project_starter.ipynb | Course notebook, models, prompts, tools, and evaluations. |
| project_lib.py | Supplied chat helpers, display functions, mock weather, and mock activities. |
| local_setup.py | Loads the local API configuration and creates the client. |
| pyproject.toml / uv.lock | Direct dependencies and the full resolved environment. |
| scripts/setup.sh | Installs the environment and registers the notebook kernel inside it. |
| scripts/check_environment.py | Checks imports and sample data; can also check the provider model list. |
| scripts/check_project.py | Checks notebook syntax and reports unfinished TODO cells. |
| tests/ | Offline setup, SDK compatibility, sample data, and notebook-kernel checks. |
| docs/rubric-checklist.md | Requirement-by-requirement progress and evidence. |

## Requirements

- Windows with Git Bash, Git, and [uv](https://docs.astral.sh/uv/getting-started/installation/).
- Python 3.12.3. uv uses the version in .python-version and can install it if needed.
- Internet access to download dependencies and use the model API.
- A Vocareum API key from the Udacity course. The setup also accepts a personal OpenAI key if the API URL is changed.

There is no model training step or GPU requirement. The notebook and tests run locally. Model requests still go to an external API.

## Setup

Run these commands in **Git Bash**:

~~~bash
git clone https://github.com/jamesk111/agentsville-trip-planner.git
cd agentsville-trip-planner
bash scripts/setup.sh
~~~

If using the submission ZIP, extract it into one folder, open Git Bash there, and run bash scripts/setup.sh. The ZIP contains the same setup and test files.

The script runs uv sync --locked, registers the **Python (AgentsVille Trip Planner)** kernel in .venv, and creates .env from .env.example if it does not already exist. It leaves an existing .env alone. No global Python environment or global Jupyter kernel is changed.

The six course libraries keep their supplied versions. The lockfile also records JupyterLab, the kernel, and test dependencies. Use the locked commands below so the notebook and tests use the same environment.

## Configuration

Open .env in your editor and set these values:

~~~dotenv
OPENAI_API_KEY=your_course_key
OPENAI_BASE_URL=https://openai.vocareum.com/v1
~~~

Enter the real key only in .env. That file is ignored by Git. Do not put a key in the notebook or its output. Variables already exported in the shell take precedence over .env; unset them if the notebook keeps using old settings.

For a personal OpenAI key, set OPENAI_BASE_URL to https://api.openai.com/v1. Vocareum keys must use the Vocareum URL. The configuration helper catches that mismatch before sending a request.

The notebook uses gpt-4.1-mini for planning and weather judgments, and gpt-4.1 for traveler-feedback judgments. The starter's weather model, gpt-4.1-nano, was rejected by Vocareum as deprecated. [ADR 0004](docs/adr/0004-weather-evaluation.md) records the replacement. Course access and budget need to be available before running those cells.

The client has a 60-second request timeout and one retry. Creating it does not send a request. See the [OpenAI Python SDK documentation](https://developers.openai.com/api/reference/python) for the environment-variable configuration pattern; this project keeps the course's pinned SDK version.

## Run locally

From the repository root:

~~~bash
uv run --locked python scripts/check_environment.py
uv run --locked jupyter lab
~~~

Open project_starter.ipynb and select **Python (AgentsVille Trip Planner)**. Run cells in order. The full notebook is implemented. Cell 16 generates the initial plan; cell 35 previews a revision message; cell 36 runs the revision loop; cell 37 checks the returned plan. Weather and feedback checks also make API requests, so rerunning every cell repeats those requests. The [Stage 6 walkthrough](docs/stage-6-itinerary-revision.md) explains the earlier feedback-correction example. [Stage 7](docs/stage-7-submission.md) records the final complete run. Cell 40 generates the text summary after the final checks pass.

The sample trip is June 10–12, 2025, including both endpoints, with a budget of 130 fictional units. Keep those dates while building the project. The supplied data only covers June 10–15, 2025; changing to today's dates returns no activities or weather.

The starter cost calculation adds each selected activity's price once. It does not multiply that price by the number of travelers.

The final summary makes one additional text request. It uses the evaluated plan and appears in the notebook. Audio is optional in the assignment and is not generated by this version.

## Check and test

~~~bash
uv run --locked pytest -q
uv run --locked python scripts/check_environment.py
uv run --locked python scripts/check_project.py
~~~

The offline tests use fake keys and mocked responses. The notebook test replays the full notebook in a real local kernel with the saved initial plan, recorded revision responses, and mocked weather/feedback judgments and summary text; outbound connections are blocked. Other tests cover input failures, source data, prompt context, response parsing, and replay of recorded live results. The offline suite sends no model requests.

After configuring a key, this optional check reads the provider's model list without generating text:

~~~bash
uv run --locked python scripts/check_environment.py --check-api
~~~

A successful model-list response confirms connectivity and listed models. It does not prove inference access, remaining course budget, or prompt quality.

Before submission, this command must also pass:

~~~bash
uv run --locked python scripts/check_project.py --require-complete
~~~

It now passes because all TODOs are filled. This scan checks syntax and unfinished markers; the live evaluations and recorded trace provide separate evidence for the behavior. The final live run is recorded in [Stage 7](docs/stage-7-submission.md), including the output review and packaging checks.

## Shutdown

Save the notebook, then use **Kernel > Shut Down All Kernels** in JupyterLab. Stop the Jupyter server with Ctrl+C in the terminal and confirm shutdown if prompted. Closing the browser tab alone does not stop the server or kernel.

## Troubleshooting

| Problem | What to check |
| --- | --- |
| Wrong Python or missing imports | Run bash scripts/setup.sh, then select the project kernel. Check sys.executable in the notebook; it should point into .venv. |
| Project kernel missing | Rerun bash scripts/setup.sh. Start Jupyter with uv run --locked jupyter lab from this folder. |
| Missing API key | Edit .env in the repository root. Restart the kernel if settings were already loaded. |
| Old key or URL still used | Check for exported OPENAI_API_KEY or OPENAI_BASE_URL variables. Exported values override .env. |
| Authentication error or inactive resource | Check the course's Cloud Resources panel and key activation. A local environment does not activate a course resource. |
| Budget, model-access, or rate-limit error | Check course budget and allowed models. Avoid repeatedly rerunning the entire notebook while debugging one cell. |
| No weather or activities | Use AgentsVille and dates within June 10–15, 2025. |
| Model-list check fails | The provider may block that endpoint. The check reports failure; it does not substitute a different model or claim generation works. |
| Revision loop reaches its step limit | Inspect the last tool call and observation. Fix the prompt or failing tool before increasing the limit. |
| Summary is empty or inaccurate | The final cell rejects empty text. Review the generated text against the final table; the checked itinerary is the source for activity details and cost. |

## Submission

The submission is agentsville-trip-planner-submission.zip. It contains the executed notebook, supplied helper, local configuration helper, locked environment files, setup/check scripts, tests, and documentation. The .env.example file is a template; the real .env, .venv, caches, logs, and development artifacts are excluded.

The notebook imports local_setup.py, so keep the files together when extracting the ZIP. Follow the setup instructions above to run it. The [Stage 7 notes](docs/stage-7-submission.md) describe the final review. The ZIP is prepared for manual upload to the course submission page; the GitHub repository retains the project history.

## Course sources

- [Project instructions](https://learn.udacity.com/cd14526?version=1.1.28&lessonKey=39b0a6da-dfbf-4314-ac52-1301c532334b&conceptKey=965a0fea-5378-4113-b266-35aa4d14a7bb)
- [Project rubric](https://learn.udacity.com/cd14526?version=1.1.28&lessonKey=39b0a6da-dfbf-4314-ac52-1301c532334b&project=rubric)
