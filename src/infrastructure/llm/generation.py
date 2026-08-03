"""Generation config, request, and response containers integrated with PromptPackage."""

from dataclasses import dataclass, field
from typing import Any

from src.infrastructure.llm.prompt_package import PromptPackage


@dataclass
class GenerationConfig:
    """Hyperparameters for LLM generation requests."""

    temperature: float = 0.2
    max_tokens: int = 2048
    seed: int | None = 42
    top_p: float = 0.95
    stop: list[str] = field(default_factory=list)


@dataclass
class GenerationRequest:
    """LLM Generation request wrapping PromptPackage and config."""

    prompt_package: PromptPackage
    model_name: str = "qwen2.5-coder:7b-instruct-q5_k_m"
    config: GenerationConfig = field(default_factory=GenerationConfig)
    request_id: str = "req_default"
    priority: int = 0


@dataclass
class GenerationResponse:
    """LLM Generation response outcome payload."""

    request_id: str
    content: str
    parsed_json: dict[str, Any] | None = None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    latency_seconds: float = 0.0
    tokens_per_second: float = 0.0
    model_name: str = ""
