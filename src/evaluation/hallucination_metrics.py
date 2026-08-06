"""HallucinationMetrics evaluating unsupported claims and hallucination rate."""

from typing import Any


class HallucinationMetrics:
    """Evaluator computing hallucination rate and claim support ratio."""

    @staticmethod
    def evaluate(claims: list[dict[str, Any]]) -> dict[str, float]:
        """Compute hallucination scores."""
        if not claims:
            return {
                "hallucination_rate": 0.0,
                "claim_support_ratio": 1.0,
                "unsupported_claims_count": 0.0,
            }

        total = len(claims)
        supported = sum(1 for c in claims if c.get("confidence", 1.0) >= 0.70)
        unsupported = total - supported

        return {
            "hallucination_rate": round(unsupported / total, 4),
            "claim_support_ratio": round(supported / total, 4),
            "unsupported_claims_count": float(unsupported),
        }
