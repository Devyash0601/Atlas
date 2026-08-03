"""WorkflowContext holding research question, evidence, settings, and constraints."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class WorkflowContext:
    """Context payload containing research configuration and parameters."""

    research_question: str
    prompt_package_id: str | None = None
    retrieved_evidence_ids: list[str] = field(default_factory=list)
    memory_references: dict[str, str] = field(default_factory=dict)
    execution_settings: dict[str, Any] = field(default_factory=dict)
    user_constraints: dict[str, Any] = field(default_factory=dict)
    configuration: dict[str, Any] = field(default_factory=dict)

    def update_setting(self, key: str, value: Any) -> None:
        """Update context execution setting."""
        self.execution_settings[key] = value
