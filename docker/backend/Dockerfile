# Multi-stage Dockerfile for FastAPI Backend
FROM python:3.13-slim as builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --no-cache-dir .

FROM python:3.13-slim as runner

WORKDIR /app

RUN groupadd -r atlas && useradd -r -g atlas atlas

COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --chown=atlas:atlas src ./src

USER atlas

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=5s --retries=5 \
  CMD curl -f http://localhost:8000/api/v1/health || exit 1

CMD ["python", "-m", "uvicorn", "src.interfaces.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
