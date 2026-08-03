#!/usr/bin/env bash
set -euo pipefail

echo "=========================================="
echo "  ATLAS-EO Development Environment Setup  "
echo "=========================================="

if [ ! -f ".env" ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
fi

echo "Installing Python dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install -e ".[dev]"

echo "Setup completed successfully!"
