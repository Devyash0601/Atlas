#!/usr/bin/env bash
set -euo pipefail

echo "=========================================="
echo "  ATLAS-EO Quality Gate Verification Suite  "
echo "=========================================="

echo "[1/3] Running Ruff Linter..."
ruff check .

echo "[2/3] Running MyPy Type Checker..."
python3 -m mypy src

echo "[3/3] Running Pytest Suite..."
python3 -m pytest tests/

echo "=========================================="
echo "  ✅ All Quality Gate Checks Passed!      "
echo "=========================================="
