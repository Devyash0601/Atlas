# Troubleshooting Guide

## Common Issues & Solutions

### 1. Docker Containers Fail to Start
- **Symptom**: `docker compose up` fails with port conflict or permission denied.
- **Solution**: Check if ports 5432, 6379, 6333, 11434, 8000, or 3000 are already in use. Run `make clean` and restart:
  ```bash
  make clean
  docker compose up -d
  ```

### 2. MyPy Type Check Errors
- **Symptom**: `mypy src` reports missing imports or generic type warnings.
- **Solution**: Ensure strict type hints are provided for all parameters and return types. Run `make typecheck` to verify.

### 3. Ollama Connection Error
- **Symptom**: Backend logs connection refused to `http://localhost:11434`.
- **Solution**: Ensure Ollama service is running (`ollama serve` or via Docker container).
