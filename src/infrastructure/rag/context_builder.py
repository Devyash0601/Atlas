"""RAG ContextBuilder constructing structured LLM context preserving document hierarchy."""

from typing import Any

from src.infrastructure.rag.chunking import DocumentChunk
from src.infrastructure.rag.citation_manager import CitationManager


class RAGContextBuilder:
    """ContextBuilder combining ranked claims, sections, figures, tables, and equations."""

    @staticmethod
    def build_structured_context(
        chunks: list[DocumentChunk],
        figures: list[dict[str, Any]] | None = None,
        tables: list[dict[str, Any]] | None = None,
        equations: list[dict[str, Any]] | None = None,
    ) -> str:
        """Build formatted scientific evidence context string preserving hierarchy."""
        parts: list[str] = []

        if chunks:
            parts.append("### SCIENTIFIC EVIDENCE & CLAIMS:")
            for chunk in chunks:
                citation = CitationManager.format_markdown(chunk)
                parts.append(f"[{citation}] ({chunk.section}): {chunk.text}")

        if figures:
            parts.append("\n### SUPPORTING FIGURES:")
            for fig in figures:
                parts.append(f"- Figure {fig.get('id')}: {fig.get('caption')}")

        if tables:
            parts.append("\n### SUPPORTING TABLES:")
            for tbl in tables:
                parts.append(f"- Table {tbl.get('id')}: {tbl.get('caption')}")

        if equations:
            parts.append("\n### MATHEMATICAL FORMULAS:")
            for eq in equations:
                parts.append(f"- Equation {eq.get('id')}: {eq.get('text')}")

        return "\n".join(parts)
