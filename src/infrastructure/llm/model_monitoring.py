"""Model health monitoring and performance benchmarking."""

from typing import Any

from src.infrastructure.llm.model_manager import ModelManager


class ModelHealthMonitor:
    """Monitor checking local model manager health and memory boundaries."""

    def __init__(self, manager: ModelManager) -> None:
        self.manager = manager

    def check_health(self) -> dict[str, Any]:
        """Perform health check on model manager."""
        usage = self.manager.get_memory_usage_mb()
        status = "healthy" if usage < 11000 else "warning_high_memory"
        return {
            "status": status,
            "used_vram_mb": usage,
            "max_vram_mb": 11000,
        }


class ModelBenchmark:
    """Benchmark recorder for local model inference speed."""

    @staticmethod
    def benchmark_inference(tokens_generated: int, elapsed_seconds: float) -> float:
        """Compute tokens per second rate."""
        if elapsed_seconds <= 0:
            return 0.0
        return round(tokens_generated / elapsed_seconds, 2)
