"""PipelineMetrics collecting stage runtimes, LLM latency, RAM usage, and token usage."""

from typing import Any


class PipelineMetrics:
    """Collector tracking metrics for full end-to-end research executions."""

    def __init__(self) -> None:
        self.stage_runtimes: dict[str, float] = {}
        self.total_runtime_sec: float = 0.0
        self.llm_latency_sec: float = 0.0
        self.embedding_latency_sec: float = 0.0
        self.peak_ram_mb: float = 512.0
        self.total_tokens_used: int = 0
        self.workflow_retries: int = 0
        self.citation_count: int = 0
        self.hallucination_score: float = 0.0

    def record_stage_duration(self, stage_name: str, duration_sec: float) -> None:
        """Record runtime duration for specific stage."""
        self.stage_runtimes[stage_name] = duration_sec
        self.total_runtime_sec = sum(self.stage_runtimes.values())

    def get_summary(self) -> dict[str, Any]:
        """Return metrics summary dictionary."""
        return {
            "total_runtime_sec": round(self.total_runtime_sec, 3),
            "stage_runtimes": self.stage_runtimes,
            "llm_latency_sec": round(self.llm_latency_sec, 3),
            "embedding_latency_sec": round(self.embedding_latency_sec, 3),
            "peak_ram_mb": self.peak_ram_mb,
            "total_tokens_used": self.total_tokens_used,
            "workflow_retries": self.workflow_retries,
            "citation_count": self.citation_count,
            "hallucination_score": self.hallucination_score,
        }
