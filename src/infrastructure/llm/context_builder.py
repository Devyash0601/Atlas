"""Context builder merging 4 memory systems, user requests, and citations into a PromptPackage."""

from typing import Any

from src.infrastructure.llm.conversation_memory import ConversationMemory
from src.infrastructure.llm.prompt_package import PromptPackage
from src.infrastructure.llm.research_memory import ResearchMemory
from src.infrastructure.llm.retrieval_memory import RetrievalMemory
from src.infrastructure.llm.token_counter import TokenCounter
from src.infrastructure.llm.workflow_memory import WorkflowMemory


class ContextBuilder:
    """Builder assembling structured context from memories and user inputs into PromptPackage."""

    def __init__(self, token_counter: TokenCounter | None = None) -> None:
        self.token_counter = token_counter or TokenCounter()
        self._extra_parts: list[str] = []

    def add_system_instruction(self, instruction: str) -> "ContextBuilder":
        """Add extra system instruction string."""
        self._extra_parts.append(f"SYSTEM: {instruction}")
        return self

    def add_retrieved_evidence(self, citation: str, claim: str) -> "ContextBuilder":
        """Add extra retrieved evidence string."""
        self._extra_parts.append(f"EVIDENCE [{citation}]: {claim}")
        return self

    def build(self) -> str:
        """Build combined text from extra context parts."""
        return "\n\n".join(self._extra_parts)

    def build_package(
        self,
        system_prompt: str,
        developer_prompt: str,
        user_prompt: str,
        conversation_memory: ConversationMemory | None = None,
        workflow_memory: WorkflowMemory | None = None,
        research_memory: ResearchMemory | None = None,
        retrieval_memory: RetrievalMemory | None = None,
        extra_citations: list[str] | None = None,
        expected_output_schema: dict[str, Any] | None = None,
        context_window: int = 8192,
        reserved_output_tokens: int = 1024,
    ) -> PromptPackage:
        """Merge memories and inputs into a validated PromptPackage."""
        context_blocks: list[str] = []
        citations: set[str] = set(extra_citations or [])

        # 1. Add Research Memory Hypothesis
        if research_memory and research_memory.hypothesis:
            context_blocks.append(f"RESEARCH HYPOTHESIS: {research_memory.hypothesis}")

        # 2. Add Workflow Memory Summary
        if workflow_memory:
            steps = workflow_memory.search("")
            if steps:
                formatted_steps = [f"Step {s['step_id']}: {s['decision']}" for s in steps]
                context_blocks.append("WORKFLOW HISTORY:\n" + "\n".join(formatted_steps))

        # 3. Add Retrieval Memory Chunks and Citations
        if retrieval_memory:
            chunks = retrieval_memory.search("")
            for c in chunks:
                citation = c["citation"]
                citations.add(citation)
                context_blocks.append(f"EVIDENCE [{citation}]: {c['text']}")

        # 4. Add Conversation Memory Dialogue
        if conversation_memory:
            messages = conversation_memory.search("")
            if messages:
                turns = [f"{m['role'].upper()}: {m['content']}" for m in messages]
                context_blocks.append("CONVERSATION HISTORY:\n" + "\n".join(turns))

        retrieved_context = "\n\n".join(context_blocks)

        package = PromptPackage(
            system_prompt=system_prompt,
            developer_prompt=developer_prompt,
            user_prompt=user_prompt,
            retrieved_context=retrieved_context,
            citations=sorted(citations),
            expected_output_schema=expected_output_schema or {},
        )

        full_text = package.assemble_full_text()
        total_tokens = self.token_counter.validate_budget(
            full_text,
            context_window=context_window,
            reserved_output_tokens=reserved_output_tokens,
        )
        package.total_prompt_tokens = total_tokens
        return package
