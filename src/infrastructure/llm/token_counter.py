"""Local token counter and context budget estimator."""

from src.infrastructure.llm.exceptions import ContextOverflowError


class TokenCounter:
    """Estimator computing prompt token budget and output token reservations."""

    def __init__(self, chars_per_token: float = 4.0) -> None:
        self.chars_per_token = chars_per_token

    @staticmethod
    def count_tokens(text: str, chars_per_token: float = 4.0) -> int:
        """Estimate token count for a text string."""
        if not text:
            return 0
        return max(1, int(len(text) / chars_per_token))

    def validate_budget(
        self,
        prompt_text: str,
        context_window: int = 8192,
        reserved_output_tokens: int = 1024,
    ) -> int:
        """Validate prompt fits inside context budget and return total tokens."""
        prompt_tokens = self.count_tokens(prompt_text)
        max_prompt_tokens = context_window - reserved_output_tokens

        if prompt_tokens > max_prompt_tokens:
            msg = (
                f"Prompt tokens ({prompt_tokens}) exceed budget ({max_prompt_tokens}) "
                f"for context window {context_window} and output reserve {reserved_output_tokens}."
            )
            raise ContextOverflowError(msg)
        return prompt_tokens
