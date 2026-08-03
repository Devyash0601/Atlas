# ADR 0001: Clean Architecture Pattern

- **Status**: Accepted
- **Date**: 2026-08-02
- **Author**: Chief System Architect

## Context
ATLAS-EO is designed as a long-term scientific research laboratory platform. Coupling domain entities and business reasoning to external frameworks (FastAPI, SQLAlchemy, Ollama, Earth Engine SDK) creates technical debt and prevents model/infrastructure replacement.

## Decision
We adopt Clean Architecture with strict inward dependency rules:
`interfaces` $\rightarrow$ `application` $\rightarrow$ `domain` $\leftarrow$ `infrastructure`.

`domain/` contains zero framework code and must never import external dependencies or infrastructure packages.

## Consequences
- **Positive**: Domain entities are 100% testable in isolation; infrastructure providers can be replaced without touching core business logic.
- **Negative**: Requires mapping code between API DTOs, domain models, and ORM entities.

## Alternatives Considered
- Direct FastAPI-SQLAlchemy CRUD pattern: Rejected due to coupling business logic to API frameworks.
