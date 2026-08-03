"""Production Prompt Engine single entry point for all LLM prompt rendering and package building."""

from typing import Any

from src.infrastructure.llm.context_builder import ContextBuilder
from src.infrastructure.llm.conversation_memory import ConversationMemory
from src.infrastructure.llm.prompt_package import PromptPackage
from src.infrastructure.llm.prompt_registry import PromptRegistry, PromptSchema
from src.infrastructure.llm.prompt_template import PromptTemplate
from src.infrastructure.llm.research_memory import ResearchMemory
from src.infrastructure.llm.retrieval_memory import RetrievalMemory
from src.infrastructure.llm.token_counter import TokenCounter
from src.infrastructure.llm.workflow_memory import WorkflowMemory


class PromptEngine:
    """Production single entry point for LLM prompt rendering and PromptPackage assembly."""

    def __init__(self, registry: PromptRegistry | None = None) -> None:
        self.registry = registry or PromptRegistry()
        self.context_builder = ContextBuilder()
        self.token_counter = TokenCounter()
        self._register_default_prompts()

    def _register_default_prompts(self) -> None:
        """Register core system default prompts into registry."""
        hypothesis_template = PromptTemplate(
            system_template="You are a lead Earth Observation scientist.",
            user_template=(
                "Formulate a hypothesis for research question: {question} in region: {region}."
            ),
        )
        hypothesis_schema = PromptSchema(
            id="hypothesis_generation",
            version="1.0",
            description="Generates formal scientific research hypothesis",
            owner="ATLAS-EO Core",
            input_schema={"question": "str", "region": "str"},
            output_schema={"required": ["hypothesis"]},
        )
        self.registry.register(hypothesis_template, hypothesis_schema)

        hypothesis_schema_alias = PromptSchema(
            id="hypothesis",
            version="1.0",
            description="Generates formal scientific research hypothesis",
            owner="ATLAS-EO Core",
            input_schema={"question": "str", "region": "str"},
            output_schema={"required": ["hypothesis"]},
        )
        self.registry.register(hypothesis_template, hypothesis_schema_alias)

    def render(self, template_id: str, **kwargs: Any) -> str:
        """Render prompt template string by ID."""
        template, _ = self.registry.get(template_id)
        rendered = template.render(**kwargs)
        return rendered.get("user") or rendered.get("system") or ""

    def render_package(
        self,
        template_id: str,
        version: str | None = None,
        conversation_memory: ConversationMemory | None = None,
        workflow_memory: WorkflowMemory | None = None,
        research_memory: ResearchMemory | None = None,
        retrieval_memory: RetrievalMemory | None = None,
        extra_citations: list[str] | None = None,
        context_window: int = 8192,
        reserved_output_tokens: int = 1024,
        **kwargs: Any,
    ) -> PromptPackage:
        """Validate variables, render template, and assemble PromptPackage."""
        self.registry.validate_variables(template_id, version, kwargs)
        template, schema = self.registry.get(template_id, version)

        rendered = template.render(**kwargs)

        return self.context_builder.build_package(
            system_prompt=rendered["system"],
            developer_prompt=rendered["developer"],
            user_prompt=rendered["user"],
            conversation_memory=conversation_memory,
            workflow_memory=workflow_memory,
            research_memory=research_memory,
            retrieval_memory=retrieval_memory,
            extra_citations=extra_citations,
            expected_output_schema=schema.output_schema,
            context_window=context_window,
            reserved_output_tokens=reserved_output_tokens,
        )
