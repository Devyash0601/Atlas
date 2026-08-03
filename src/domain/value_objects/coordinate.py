"""Geospatial coordinate value object."""

from dataclasses import dataclass

from src.domain.base.value_object import ValueObject
from src.domain.exceptions.domain_exceptions import ValidationError


@dataclass(frozen=True)
class Coordinate(ValueObject):
    """Geospatial coordinate representing latitude [-90, 90] and longitude [-180, 180]."""

    latitude: float
    longitude: float

    def __post_init__(self) -> None:
        """Validate latitude and longitude bounds."""
        if not (-90.0 <= self.latitude <= 90.0):
            msg = f"Latitude must be between -90.0 and 90.0 degrees, got {self.latitude}"
            raise ValidationError(msg)
        if not (-180.0 <= self.longitude <= 180.0):
            msg = f"Longitude must be between -180.0 and 180.0 degrees, got {self.longitude}"
            raise ValidationError(msg)
