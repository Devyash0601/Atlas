"""Application layer typed exceptions."""

from typing import Any


class ApplicationException(Exception):
    """Base exception class for all application layer errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ValidationFailed(ApplicationException):
    """Exception raised when input command validation fails."""

    pass


class CommandFailed(ApplicationException):
    """Exception raised when command execution fails."""

    pass


class QueryFailed(ApplicationException):
    """Exception raised when query execution fails."""

    pass


class TransactionFailed(ApplicationException):
    """Exception raised when UnitOfWork transaction fails."""

    pass


class ConfigurationError(ApplicationException):
    """Exception raised when application orchestration configuration is invalid."""

    pass
