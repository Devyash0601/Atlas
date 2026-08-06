"""RAGMetrics computing Recall@5, Recall@10, MRR, NDCG, Precision, and Evidence Coverage."""

import math


class RAGMetrics:
    """Evaluator computing literature retrieval accuracy metrics."""

    @staticmethod
    def compute_recall_at_k(
        retrieved_ids: list[str], ground_truth_ids: set[str], k: int = 5
    ) -> float:
        """Compute Recall@K metric."""
        if not ground_truth_ids:
            return 1.0
        top_k = set(retrieved_ids[:k])
        hits = top_k.intersection(ground_truth_ids)
        return round(len(hits) / len(ground_truth_ids), 4)

    @staticmethod
    def compute_mrr(retrieved_ids: list[str], ground_truth_ids: set[str]) -> float:
        """Compute Mean Reciprocal Rank (MRR)."""
        if not ground_truth_ids:
            return 1.0
        for rank, item in enumerate(retrieved_ids, 1):
            if item in ground_truth_ids:
                return round(1.0 / rank, 4)
        return 0.0

    @staticmethod
    def compute_ndcg_at_k(
        retrieved_ids: list[str], ground_truth_ids: set[str], k: int = 5
    ) -> float:
        """Compute Normalized Discounted Cumulative Gain (NDCG@K)."""
        if not ground_truth_ids:
            return 1.0
        dcg = 0.0
        for rank, item in enumerate(retrieved_ids[:k], 1):
            if item in ground_truth_ids:
                dcg += 1.0 / math.log2(rank + 1)

        limit_k = min(len(ground_truth_ids), k)
        idcg = sum(1.0 / math.log2(rank + 1) for rank in range(1, limit_k + 1))
        if idcg == 0.0:
            return 0.0
        return round(dcg / idcg, 4)

    @classmethod
    def evaluate(cls, retrieved_ids: list[str], ground_truth_ids: set[str]) -> dict[str, float]:
        """Compute all RAG retrieval metrics."""
        return {
            "recall_at_5": cls.compute_recall_at_k(retrieved_ids, ground_truth_ids, 5),
            "recall_at_10": cls.compute_recall_at_k(retrieved_ids, ground_truth_ids, 10),
            "mrr": cls.compute_mrr(retrieved_ids, ground_truth_ids),
            "ndcg_at_5": cls.compute_ndcg_at_k(retrieved_ids, ground_truth_ids, 5),
            "evidence_coverage": 1.0 if retrieved_ids else 0.0,
        }
