#!/usr/bin/env bash
set -euo pipefail

echo "Formatting Python code with Ruff..."
ruff format .
ruff check --fix .
