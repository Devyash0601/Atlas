.PHONY: help dev backend frontend test lint fmt typecheck docker clean docs benchmark verify setup

PYTHON := python3
PIP := pip
RUFF := ruff
MYPY := mypy
PYTEST := pytest

help:
	@echo "ATLAS-EO Developer Command Suite:"
	@echo "  make setup      - Run setup script to configure local environment"
	@echo "  make dev        - Launch full stack via Docker Compose"
	@echo "  make backend    - Run FastAPI backend locally"
	@echo "  make frontend   - Run Next.js frontend locally"
	@echo "  make lint       - Run Ruff code linter check"
	@echo "  make fmt        - Auto-format codebase with Ruff"
	@echo "  make typecheck  - Run MyPy strict type checker"
	@echo "  make test       - Run Pytest test suite"
	@echo "  make verify     - Run full quality verification (lint + typecheck + test)"
	@echo "  make docker     - Build Docker container images"
	@echo "  make clean      - Clean up caches, build artifacts, and containers"
	@echo "  make docs       - Serve local documentation"
	@echo "  make benchmark  - Run benchmark suite"

setup:
	@bash scripts/setup.sh

dev:
	@bash scripts/dev.sh

backend:
	@$(PYTHON) -m uvicorn src.interfaces.api.main:app --reload --host 0.0.0.0 --port 8000

frontend:
	@cd frontend && npm run dev

lint:
	@bash scripts/lint.sh

fmt:
	@bash scripts/format.sh

typecheck:
	@$(PYTHON) -m mypy src

test:
	@bash scripts/test.sh

verify:
	@bash scripts/verify.sh

docker:
	@docker compose build

clean:
	@rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage dist build *.egg-info
	@find . -type d -name "__pycache__" -exec rm -rf {} +

docs:
	@echo "Documentation available under docs/ and README.md"

benchmark:
	@bash scripts/benchmark.sh
