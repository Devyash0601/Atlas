#!/usr/bin/env bash
set -euo pipefail

echo "Starting ATLAS-EO Infrastructure & Stack..."
docker compose up --build -d

echo "Services started:"
echo " - FastAPI Backend: http://localhost:8000/api/v1/health"
echo " - Frontend Dashboard: http://localhost:3000"
