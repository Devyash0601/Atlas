"""Prompt template rendering supporting system, user, developer sections, and dynamic variables."""

from typing import Any

from src.infrastructure.llm.exceptions import TemplateRenderingError


class PromptTemplate:
    """Deterministic prompt template rendering engine."""

    def __init__(
        self,
        system_template: str = "",
        developer_template: str = "",
        user_template: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.system_template = system_template
        self.developer_template = developer_template
        self.user_template = user_template
        self.metadata = metadata or {}

    def render(self, **kwargs: Any) -> dict[str, str]:
        """Render prompt templates with variable substitution."""
        try:
            rendered_system = self.system_template.format(**kwargs) if self.system_template else ""
            rendered_developer = (
                self.developer_template.format(**kwargs) if self.developer_template else ""
            )
            rendered_user = self.user_template.format(**kwargs) if self.user_template else ""
            return {
                "system": rendered_system,
                "developer": rendered_developer,
                "user": rendered_user,
            }
        except KeyError as err:
            msg = f"Missing variable during template rendering: {err}"
            raise TemplateRenderingError(msg) from err
        except Exception as err:
            raise TemplateRenderingError(f"Failed to render template: {err}") from err
