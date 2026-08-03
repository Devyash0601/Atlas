# Comprehensive Contributing Guide

Thank you for contributing to **ATLAS-EO**!

## 1. Architectural Integrity & Rules
- **Layer Isolation**: Code in `domain/` must NEVER import `infrastructure/`, `interfaces/`, or third-party web frameworks.
- **Provider Abstraction**: All AI model calls, vector store operations, and Earth Engine tasks MUST use provider interfaces.
- **File Length Limit**: Files must not exceed **500 lines**.

## 2. Quality Checklist Before Opening a PR
Run the verification pipeline:
```bash
make verify
```
This automatically runs:
- `ruff check .`
- `mypy src`
- `pytest tests/`

## 3. Conventional Commit Format
Format: `type(scope): summary`
- `feat(planner): add workflow plan validation`
- `fix(gee): resolve cloud mask thresholding`
- `docs(adr): add local-first architecture record`
