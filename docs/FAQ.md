# Frequently Asked Questions (FAQ)

### Q1: Does ATLAS-EO require paid OpenAI or Anthropic API keys?
**No.** ATLAS-EO is built local-first. It relies on Ollama running open-weights models (`qwen3:8b`, `nomic-embed-text`) locally.

### Q2: Is Google Earth Engine required for Phase 1?
**No.** Phase 1 establishes the repository architecture, Docker containers, and API foundation. GEE integration occurs in Phase 7.

### Q3: Why Clean Architecture over standard FastAPI CRUD?
To ensure scientific reproducibility, unit testability, and independence from third-party frameworks and model APIs.
