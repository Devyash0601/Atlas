"""ModelRegistry managing Ollama model specifications and metadata."""

from dataclasses import dataclass
from typing import ClassVar

from src.infrastructure.llm.exceptions import ModelNotInstalled


@dataclass(frozen=True)
class ModelSpec:
    """Specification metadata for a local AI model."""

    name: str
    provider: str
    modality: str
    parameter_count: str
    quantization: str
    context_window: int
    estimated_ram_mb: int
    embedding_dimensions: int | None = None
    alias_kind: str = ""

    @property
    def kind(self) -> str:
        """Alias for model role kind or modality."""
        return self.alias_kind or self.modality

    @property
    def vram_mb(self) -> int:
        """Alias for estimated RAM footprint."""
        return self.estimated_ram_mb

    @property
    def is_loaded(self) -> bool:
        """Return True when loaded in memory."""
        return True


class ModelRegistry:
    """Registry tracking supported local models, discovery, and RAM estimates."""

    SUPPORTED_MODELS: ClassVar[dict[str, ModelSpec]] = {
        "qwen2.5-coder:7b": ModelSpec(
            name="qwen2.5-coder:7b",
            provider="Alibaba/Ollama",
            modality="text-to-text",
            parameter_count="7B",
            quantization="Q4_K_M",
            context_window=8192,
            estimated_ram_mb=5500,
        ),
        "qwen2.5-coder:7b-instruct-q5_k_m": ModelSpec(
            name="qwen2.5-coder:7b-instruct-q5_k_m",
            provider="Alibaba/Ollama",
            modality="text-to-text",
            parameter_count="7B",
            quantization="Q5_K_M",
            context_window=8192,
            estimated_ram_mb=5500,
        ),
        "qwen2-vl:7b-instruct-q4_k_m": ModelSpec(
            name="qwen2-vl:7b-instruct-q4_k_m",
            provider="Alibaba/Ollama",
            modality="image-text-to-text",
            parameter_count="7B",
            quantization="Q4_K_M",
            context_window=4096,
            estimated_ram_mb=4200,
        ),
        "nomic-embed-text:v1.5": ModelSpec(
            name="nomic-embed-text:v1.5",
            provider="Nomic/Ollama",
            modality="text-to-embedding",
            parameter_count="137M",
            quantization="FP16",
            context_window=8192,
            estimated_ram_mb=300,
            embedding_dimensions=768,
        ),
    }

    def __init__(self) -> None:
        self._installed_models: set[str] = set(self.SUPPORTED_MODELS.keys())

    def register_installed(self, model_name: str) -> None:
        """Register a model name as installed locally."""
        self._installed_models.add(model_name)

    def is_installed(self, model_name: str) -> bool:
        """Check if model name is registered as installed."""
        return model_name in self._installed_models

    def get_spec(self, model_name: str) -> ModelSpec:
        """Retrieve ModelSpec metadata for a model."""
        if model_name not in self.SUPPORTED_MODELS:
            raise ModelNotInstalled(f"Model '{model_name}' is not registered in ModelRegistry.")
        return self.SUPPORTED_MODELS[model_name]

    def list_installed(self) -> list[ModelSpec]:
        """Return list of installed ModelSpec items."""
        return [
            self.SUPPORTED_MODELS[name]
            for name in self._installed_models
            if name in self.SUPPORTED_MODELS
        ]
