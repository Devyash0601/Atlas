# Coding & Development Workflow Guide

## Daily Workflow Cycle

1. **Pull latest changes**:
   ```bash
   git pull origin develop
   ```

2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Development & Testing**:
   - Write unit tests first in `tests/unit/`.
   - Implement logic in `src/`.
   - Run linter and type check:
     ```bash
     make lint
     make typecheck
     make test
     ```

4. **Verify entire repository before push**:
   ```bash
   make verify
   ```
