"""Base exception hierarchy for domain and infrastructure layers."""

from typing import Any


class AtlasException(Exception):
    """Base exception class for all ATLAS-EO domain and system errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class DomainException(AtlasException):
    """Exception raised when a business rule or invariant is violated."""

    pass


class InfrastructureException(AtlasException):
    """Exception raised when an external system or provider encounters an error."""

    pass


class NotFoundException(DomainException):
    """Exception raised when a requested resource is not found."""

    pass


class ValidationException(DomainException):
    """Exception raised when input validation fails."""

    pass


class ProviderException(InfrastructureException):
    """Exception raised when a third-party AI or tool provider fails."""

    pass
