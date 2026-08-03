"""Pure Python domain typed exceptions."""

from typing import Any


class DomainError(Exception):
    """Base exception for all domain layer business errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ValidationError(DomainError):
    """Exception raised when value object or entity attribute validation fails."""

    pass


class StateTransitionError(DomainError):
    """Exception raised when an invalid entity status transition is attempted."""

    pass


class EntityNotFoundError(DomainError):
    """Exception raised when a domain entity is not found."""

    pass


class BusinessRuleViolationError(DomainError):
    """Exception raised when an invariant business rule is broken."""

    pass
