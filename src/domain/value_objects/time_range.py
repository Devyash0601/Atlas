"""Time range value object."""

from dataclasses import dataclass
from datetime import datetime

from src.domain.base.value_object import ValueObject
from src.domain.exceptions.domain_exceptions import ValidationError


@dataclass(frozen=True)
class TimeRange(ValueObject):
    """Time range defined by start and end timestamps."""

    start_date: datetime
    end_date: datetime

    def __post_init__(self) -> None:
        """Validate start date is on or before end date."""
        if self.start_date > self.end_date:
            msg = (
                f"Start date ({self.start_date.isoformat()}) must be on or "
                f"before end date ({self.end_date.isoformat()})"
            )
            raise ValidationError(msg)
