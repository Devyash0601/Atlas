"""Prompt registry for versioning, metadata schema, validation, and overrides."""

from dataclasses import dataclass
from typing import Any

from src.infrastructure.llm.exceptions import PromptValidationError, TemplateNotFoundError
from src.infrastructure.llm.prompt_template import PromptTemplate


@dataclass
class PromptSchema:
    """Prompt metadata schema definition."""

    id: str
    version: str
    description: str
    owner: str
    input_schema: dict[str, str]
    output_schema: dict[str, Any]


class PromptRegistry:
    """Central thread-safe registry for managing prompt templates and schemas."""

    def __init__(self) -> None:
        self._templates: dict[tuple[str, str], tuple[PromptTemplate, PromptSchema]] = {}
        self._latest_versions: dict[str, str] = {}

    def register(
        self,
        template: PromptTemplate,
        schema: PromptSchema,
        is_latest: bool = True,
    ) -> None:
        """Register a prompt template with its schema."""
        key = (schema.id, schema.version)
        self._templates[key] = (template, schema)
        if is_latest or schema.id not in self._latest_versions:
            self._latest_versions[schema.id] = schema.version

    def get(
        self, template_id: str, version: str | None = None
    ) -> tuple[PromptTemplate, PromptSchema]:
        """Retrieve registered template and schema by ID and version."""
        ver = version or self._latest_versions.get(template_id)
        if not ver or (template_id, ver) not in self._templates:
            msg = f"Template '{template_id}' (version '{version}') not found."
            raise TemplateNotFoundError(msg)
        return self._templates[(template_id, ver)]

    def validate_variables(
        self, template_id: str, version: str | None, kwargs: dict[str, Any]
    ) -> None:
        """Validate input kwargs against template input schema."""
        _, schema = self.get(template_id, version)
        missing = [k for k in schema.input_schema if k not in kwargs]
        if missing:
            msg = f"Missing required input variables for '{template_id}': {missing}"
            raise PromptValidationError(msg)
