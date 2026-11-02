# ADR 0001: Keep the course notebook and run it locally

- Status: accepted
- Date: November 2, 2026
- Author: James Kline

## Context

The submission is a Jupyter notebook with a supplied helper library. I want to complete it locally, keep each stage understandable, and make the environment reproducible. The original setup assumes a hosted workspace and offers a hardcoded API-key placeholder.

## Decision

Keep the course notebook's cell order and the supplied helper library. Put local configuration in local_setup.py. Use Python 3.12.3 and uv, keep the six supplied library versions, and commit uv.lock. Install the named Jupyter kernel inside .venv rather than registering a global kernel.

Use .env for the course key and API URL. Exported environment variables take precedence. Configure the Vocareum endpoint by default and reject a Vocareum key paired with a different host.

Change only the notebook setup and optional narration cells during the setup stage. Leave the seven learning TODO cells for their own stages. Keep narration off by default and use a project-relative output path when enabled.

Track rubric requirements separately from environment checks. A syntax check or an offline test cannot establish that a prompt generates a correct itinerary.

## Tradeoffs

The notebook remains dependent on cell execution order. That fits the course submission and makes it easy to compare against the starter, but it is less modular than a packaged application. If the project grows beyond the course, extracting models and tools into modules would be a separate decision.

Keeping the supplied SDK version limits changes from the course baseline. It also means current SDK examples may use features absent from this project. Test the installed version instead of assuming examples for the latest release apply.

The environment can be checked offline after installation. Actual generation still requires an active provider key, model access, and budget. These checks are recorded separately.

## Alternatives considered

- Work in the hosted workspace: useful for downloading the starter files, but local development is the chosen workflow.
- Rewrite the project as an application: adds scope before the course requirements are complete.
- Install packages from notebook cells: makes repeated runs slower and allows environment changes during execution.
