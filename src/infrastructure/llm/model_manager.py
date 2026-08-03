"""Production Ollama ModelManager with lazy loading and idle unloading."""

import time
from typing import Any, ClassVar

from src.infrastructure.llm.exceptions import ModelNotInstalled
from src.infrastructure.llm.model_registry import ModelRegistry, ModelSpec


class ModelManager:
    """Local model manager for Ollama inference engines with lazy loading and idle unloading."""

    SUPPORTED_MODELS: ClassVar[dict[str, str]] = {
        "reasoning": "qwen2.5-coder:7b-instruct-q5_k_m",
        "vision": "qwen2-vl:7b-instruct-q4_k_m",
        "embedding": "nomic-embed-text:v1.5",
        "reranker": "bge-reranker-base",
    }

    def __init__(
        self,
        ollama_host: str = "http://localhost:11434",
        idle_timeout_seconds: float = 300.0,
    ) -> None:
        self.ollama_host = ollama_host
        self.idle_timeout_seconds = idle_timeout_seconds
        self.registry = ModelRegistry()
        self._loaded_models: dict[str, float] = {}  # model_name -> last_access_timestamp

    def is_model_available(self, alias: str) -> bool:
        """Check if model alias is registered in supported models."""
        return alias in self.SUPPORTED_MODELS

    def load_model(self, alias: str) -> ModelSpec:
        """Load local model lazily and track last access timestamp."""
        model_name = self.SUPPORTED_MODELS.get(alias, alias)
        spec = self.registry.get_spec(model_name)
        if alias in self.SUPPORTED_MODELS:
            spec = ModelSpec(
                name=spec.name,
                provider=spec.provider,
                modality=spec.modality,
                parameter_count=spec.parameter_count,
                quantization=spec.quantization,
                context_window=spec.context_window,
                estimated_ram_mb=spec.estimated_ram_mb,
                embedding_dimensions=spec.embedding_dimensions,
                alias_kind=alias,
            )
        self._loaded_models[model_name] = time.time()
        return spec

    def unload_model(self, alias: str) -> bool:
        """Unload local model from memory."""
        model_name = self.SUPPORTED_MODELS.get(alias, alias)
        if model_name in self._loaded_models:
            del self._loaded_models[model_name]
            return True
        return False

    def unload_idle_models(self) -> list[str]:
        """Unload any models that have exceeded the idle timeout limit."""
        now = time.time()
        unloaded: list[str] = []
        for name, last_seen in list(self._loaded_models.items()):
            if now - last_seen > self.idle_timeout_seconds:
                del self._loaded_models[name]
                unloaded.append(name)
        return unloaded

    def get_memory_usage_mb(self) -> int:
        """Return total estimated RAM used by loaded models."""
        total = 0
        for name in self._loaded_models:
            try:
                spec = self.registry.get_spec(name)
                total += spec.estimated_ram_mb
            except ModelNotInstalled:
                total += 1000
        return total

    def get_status(self) -> dict[str, Any]:
        """Return model manager status dictionary."""
        return {
            "ollama_host": self.ollama_host,
            "loaded_models": list(self._loaded_models.keys()),
            "total_vram_mb": self.get_memory_usage_mb(),
            "idle_timeout_seconds": self.idle_timeout_seconds,
        }
