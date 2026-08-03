"""Typed exceptions for the Production Prompt Engine subsystem."""


class PromptEngineError(Exception):
    """Base exception for all Prompt Engine errors."""

    pass


class PromptValidationError(PromptEngineError):
    """Raised when prompt variable validation fails."""

    pass


class ContextOverflowError(PromptEngineError):
    """Raised when prompt rendering exceeds the allocated context window token budget."""

    pass


class TemplateNotFoundError(PromptEngineError):
    """Raised when a requested prompt template is not registered."""

    pass


class TemplateRenderingError(PromptEngineError):
    """Raised when prompt rendering fails due to syntax or key error."""

    pass


class StructuredOutputError(ValueError, PromptEngineError):
    """Raised when LLM output JSON validation or type coercion fails."""

    pass


class MemoryError(PromptEngineError):
    """Raised when an operation on a memory system fails."""

    pass


# Production Ollama Runtime Exceptions
class ModelNotInstalled(ValueError, PromptEngineError):
    """Raised when requested Ollama model is not installed locally."""

    pass


class RuntimeUnavailable(PromptEngineError):
    """Raised when local Ollama service cannot be reached."""

    pass


class GenerationTimeout(PromptEngineError):
    """Raised when LLM generation exceeds timeout limit."""

    pass


class StreamingCancelled(PromptEngineError):
    """Raised when active token streaming is cancelled."""

    pass


class InvalidModelResponse(PromptEngineError):
    """Raised when model returns malformed or invalid response payload."""

    pass


class ContextOverflow(PromptEngineError):
    """Raised when request prompt exceeds model context window limit."""

    pass


class QueueOverflow(PromptEngineError):
    """Raised when runtime request queue capacity is exceeded."""

    pass


class RetryLimitExceeded(PromptEngineError):
    """Raised when generation retries exceed maximum limit."""

    pass
