"""ContextWindowManager trimming context while preserving scientific citations and instructions."""

from src.infrastructure.llm.exceptions import ContextOverflow
from src.infrastructure.llm.token_counter import TokenCounter


class ContextWindowManager:
    """Context window manager estimating context budget and prioritizing scientific evidence."""

    def __init__(self, token_counter: TokenCounter | None = None) -> None:
        self.token_counter = token_counter or TokenCounter()

    def trim_context(
        self,
        retrieved_context: str,
        max_tokens: int,
        preserve_citations: list[str] | None = None,
    ) -> str:
        """Trim retrieved context string to fit inside token budget."""
        current_tokens = self.token_counter.count_tokens(retrieved_context)
        if current_tokens <= max_tokens:
            return retrieved_context

        paragraphs = retrieved_context.split("\n\n")
        preserved: list[str] = []

        citations = preserve_citations or []
        # First pass: keep evidence paragraphs containing citations
        for p in paragraphs:
            if any(c in p for c in citations):
                preserved.append(p)

        # Second pass: fill remaining budget with non-citation paragraphs
        for p in paragraphs:
            if p not in preserved:
                candidate = "\n\n".join([*preserved, p])
                if self.token_counter.count_tokens(candidate) <= max_tokens:
                    preserved.append(p)

        result = "\n\n".join(preserved)
        if self.token_counter.count_tokens(result) > max_tokens:
            raise ContextOverflow("Unable to trim context to fit within token limit.")

        return result
