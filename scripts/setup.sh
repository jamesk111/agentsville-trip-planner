#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
uv sync --locked
uv run --locked python -m ipykernel install --sys-prefix \
  --name agentsville-trip-planner --display-name "Python (AgentsVille Trip Planner)"
if [[ ! -f .env ]]; then
  cp .env.example .env
fi
printf '%s\n' 'Local environment ready. Add your key to .env before running API cells.'
