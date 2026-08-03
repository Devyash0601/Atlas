#!/usr/bin/env bash
set -euo pipefail

echo "Running Pytest test suite..."
python3 -m pytest tests/ --cov=src --cov-report=term-missing
