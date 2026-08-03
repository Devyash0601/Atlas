#!/usr/bin/env bash
set -euo pipefail

echo "Running Ruff code linter..."
ruff check .
