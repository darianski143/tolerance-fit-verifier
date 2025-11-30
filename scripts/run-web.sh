#!/usr/bin/env bash
set -euo pipefail

# Simple launcher for Linux (web only)
# Usage:
#   scripts/run-web.sh           # dev (Flask built-in)
#   scripts/run-web.sh prod      # production (Waitress)

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
cd "$PROJECT_ROOT"

export PYTHONPATH=src
MODE="${1:-dev}"
PORT="${PORT:-5000}"
HOST="${HOST:-127.0.0.1}"

# Choose Python interpreter (prefer local venv)
if [[ -x ".venv/bin/python" ]]; then
  PY=".venv/bin/python"
else
  PY="python3"
fi

if [[ "$MODE" == "prod" ]]; then
  # Production-ish: waitress WSGI server
  if ! command -v waitress-serve >/dev/null 2>&1; then
    echo "waitress-serve not found; installing in active environment..."
    "$PY" -m pip install --quiet waitress
  fi
  echo "Starting Waitress on http://${HOST}:${PORT} ..."
  exec waitress-serve --host "$HOST" --port "$PORT" app.web:app
else
  echo "Starting Flask dev server on http://${HOST}:${PORT} ..."
  exec "$PY" -m flask --app app.web run --host "$HOST" --port "$PORT" --debug
fi
