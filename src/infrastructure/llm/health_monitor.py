"""RuntimeHealthMonitor auditing Ollama service and model health status."""

from typing import Any

from src.infrastructure.llm.model_manager import ModelManager


class RuntimeHealthMonitor:
    """Health monitor evaluating runtime service status and RAM pressure."""

    def __init__(self, model_manager: ModelManager) -> None:
        self.model_manager = model_manager

    def check_health(self) -> dict[str, Any]:
        """Perform comprehensive health check."""
        memory_mb = self.model_manager.get_memory_usage_mb()
        status = "healthy" if memory_mb < 11000 else "warning_high_memory"

        return {
            "status": status,
            "ollama_host": self.model_manager.ollama_host,
            "memory_usage_mb": memory_mb,
            "max_memory_limit_mb": 11000,
            "loaded_models": list(self.model_manager.get_status()["loaded_models"]),
        }
