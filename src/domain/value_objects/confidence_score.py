"""Confidence score value object."""

from dataclasses import dataclass

from src.domain.base.value_object import ValueObject
from src.domain.exceptions.domain_exceptions import ValidationError


@dataclass(frozen=True)
class ConfidenceScore(ValueObject):
    """Scientific claim verification confidence score between 0.0 and 1.0."""

    score: float

    def __post_init__(self) -> None:
        """Validate confidence score range."""
        if not (0.0 <= self.score <= 1.0):
            raise ValidationError(f"Confidence score must be between 0.0 and 1.0, got {self.score}")
