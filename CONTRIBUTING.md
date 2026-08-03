# Contributing to ATLAS-EO

Thank you for your interest in contributing to ATLAS-EO!

## Guidelines

1. **Clean Architecture**: Respect layer isolation (`domain`, `application`, `infrastructure`, `interfaces`, `shared`).
2. **Quality Standards**:
   - Python 3.13 with 100% strict type hints.
   - Code must pass `ruff check .` and `mypy src`.
   - All functions must have Google-style docstrings.
   - Maximum 500 lines per file.
3. **Commit Convention**:
   - `feat(scope): description`
   - `fix(scope): description`
   - `docs(scope): description`
4. **Pull Requests**:
   - Target the `develop` branch.
   - All CI checks must pass before merging.
