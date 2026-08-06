"""CitationMetrics evaluating citation precision, completeness, and DOI coverage."""

from typing import Any


class CitationMetrics:
    """Evaluator computing paper citation metrics."""

    @staticmethod
    def evaluate(citations: list[dict[str, Any]]) -> dict[str, float]:
        """Compute citation quality metrics."""
        if not citations:
            return {
                "citation_precision": 1.0,
                "citation_completeness": 1.0,
                "broken_references_count": 0.0,
                "doi_coverage": 1.0,
            }

        total = len(citations)
        with_doi = sum(1 for c in citations if c.get("doi"))
        valid = sum(1 for c in citations if c.get("citation_id") and c.get("authors"))

        return {
            "citation_precision": round(valid / total, 4),
            "citation_completeness": round(valid / total, 4),
            "broken_references_count": float(total - valid),
            "doi_coverage": round(with_doi / total, 4),
        }
