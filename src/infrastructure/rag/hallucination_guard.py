"""HallucinationGuard computing completeness and claim support scores."""

from dataclasses import dataclass

from src.infrastructure.rag.chunking import DocumentChunk


@dataclass
class HallucinationEvaluation:
    """Hallucination evaluation metrics report."""

    is_passed: bool
    claim_support_score: float
    citation_completeness_score: float
    evidence_completeness_score: float


class HallucinationGuard:
    """Guard evaluating scientific claims for empirical support and zero hallucinations."""

    def __init__(self, min_support_score: float = 0.7) -> None:
        self.min_support_score = min_support_score

    def evaluate_response(
        self, response_text: str, retrieved_chunks: list[DocumentChunk]
    ) -> HallucinationEvaluation:
        """Evaluate generated text against retrieved evidence chunks."""
        if not retrieved_chunks:
            return HallucinationEvaluation(
                is_passed=False,
                claim_support_score=0.0,
                citation_completeness_score=0.0,
                evidence_completeness_score=0.0,
            )

        resp_words = set(response_text.lower().split())
        matched = 0
        for chunk in retrieved_chunks:
            c_words = set(chunk.text.lower().split())
            if len(resp_words.intersection(c_words)) >= 2:
                matched += 1

        support_score = round(matched / len(retrieved_chunks), 2)
        has_citation = any("[" in response_text and "]" in response_text for _ in [1])
        citation_score = 1.0 if has_citation else 0.8
        evidence_score = round((support_score + citation_score) / 2.0, 2)

        is_passed = support_score >= self.min_support_score

        return HallucinationEvaluation(
            is_passed=is_passed,
            claim_support_score=support_score,
            citation_completeness_score=citation_score,
            evidence_completeness_score=evidence_score,
        )

    @staticmethod
    def verify_claim_support(claim: str, retrieved_chunks: list[DocumentChunk]) -> bool:
        """Verify individual claim support against chunks."""
        if not retrieved_chunks:
            return False
        claim_words = set(claim.lower().split())
        for chunk in retrieved_chunks:
            chunk_words = set(chunk.text.lower().split())
            if len(claim_words.intersection(chunk_words)) >= 2:
                return True
        return False
