# ADR 0003: Local-First Open-Source AI Execution Stack

- **Status**: Accepted
- **Date**: 2026-08-02
- **Author**: Chief System Architect

## Context
Scientific researchers require privacy, zero API cost overhead, reproducible execution, and Apple Silicon hardware acceleration without relying on third-party SaaS AI APIs (OpenAI/Anthropic).

## Decision
We enforce a strict local-first AI stack powered by Ollama:
- LLM: `qwen3:8b`
- Embeddings: `nomic-embed-text`
- Vision: `qwen2.5-vl`
- Vector Store: Qdrant

No paid cloud LLM APIs are permitted in Version 1.

## Consequences
- **Positive**: Zero operational API cost, local data privacy, offline capabilities, reproducible runs.
- **Negative**: Constrained by local GPU/RAM resources (e.g., Apple Silicon unified memory).

## Alternatives Considered
- Cloud LLM APIs (OpenAI/Anthropic): Rejected per project vision and core principles.
