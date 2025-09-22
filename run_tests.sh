#!/usr/bin/env bash
set -euo pipefail
echo "Running tests with pytest (inside uv)..."

uv run python -m pytest tests/tests_api.py -v