# ADR 0002: Polymorphic Provider Abstractions for AI and Geospatial Engines

- **Status**: Accepted
- **Date**: 2026-08-02
- **Author**: Chief System Architect

## Context
AI models (LLMs, Vision, Embeddings) and remote sensing APIs (Google Earth Engine) evolve rapidly. Direct usage of specific vendor SDKs across the codebase leads to vendor lock-in.

## Decision
All AI, vector store, and Earth Engine operations must be isolated behind domain provider interfaces:
- `LLMProvider`
- `EmbeddingProvider`
- `VisionProvider`
- `VectorStoreProvider`
- `EarthEngineProvider`
- `StorageProvider`

Services and agents interact strictly through abstract contracts via FastAPI dependency injection.

## Consequences
- **Positive**: LLMs can be swapped (e.g., Qwen3 to Gemma or Llama) with zero modifications to application logic.
- **Negative**: Requires writing polymorphic adapter implementations in `infrastructure/`.

## Alternatives Considered
- Direct Ollama and Earth Engine SDK usage in services: Rejected due to violation of Dependency Inversion Principle.
