"""PromptPackage container representing full prompt payload for LLM inference."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PromptPackage:
    """Consolidated prompt package sent to local LLM model runtime."""

    system_prompt: str
    developer_prompt: str
    user_prompt: str
    retrieved_context: str
    citations: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    expected_output_schema: dict[str, Any] = field(default_factory=dict)
    total_prompt_tokens: int = 0

    def assemble_full_text(self) -> str:
        """Assemble full rendered prompt text string for execution."""
        parts: list[str] = []
        if self.system_prompt:
            parts.append(f"SYSTEM:\n{self.system_prompt}")
        if self.developer_prompt:
            parts.append(f"DEVELOPER:\n{self.developer_prompt}")
        if self.retrieved_context:
            parts.append(f"RETRIEVED CONTEXT:\n{self.retrieved_context}")
        if self.user_prompt:
            parts.append(f"USER:\n{self.user_prompt}")
        return "\n\n".join(parts)
