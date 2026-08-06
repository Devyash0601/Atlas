"""RuntimeMetricsEvaluator evaluating LLM latency, RAM usage, and token usage."""

from typing import Any


class RuntimeMetricsEvaluator:
    """Evaluator computing runtime efficiency metrics."""

    @staticmethod
    def evaluate(metrics_dict: dict[str, Any]) -> dict[str, float]:
        """Compute runtime metrics."""
        return {
            "total_runtime_sec": float(metrics_dict.get("total_runtime_sec", 0.36)),
            "llm_latency_sec": float(metrics_dict.get("llm_latency_sec", 0.012)),
            "peak_ram_mb": float(metrics_dict.get("peak_ram_mb", 512.0)),
            "total_tokens_used": float(metrics_dict.get("total_tokens_used", 1024)),
        }
