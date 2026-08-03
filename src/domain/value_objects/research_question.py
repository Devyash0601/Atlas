"""Research question value object."""

from dataclasses import dataclass

from src.domain.base.value_object import ValueObject
from src.domain.exceptions.domain_exceptions import ValidationError


@dataclass(frozen=True)
class ResearchQuestion(ValueObject):
    """Scientific research objective text with length validation."""

    text: str

    def __post_init__(self) -> None:
        """Validate research question text invariants."""
        cleaned = self.text.strip() if self.text else ""
        if not cleaned:
            raise ValidationError("Research question text cannot be empty")
        if len(cleaned) < 10:
            raise ValidationError("Research question must be at least 10 characters long")
        if len(cleaned) > 1000:
            raise ValidationError("Research question cannot exceed 1000 characters")
