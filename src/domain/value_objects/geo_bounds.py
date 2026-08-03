"""Geospatial bounding box value object."""

from dataclasses import dataclass

from src.domain.base.value_object import ValueObject
from src.domain.exceptions.domain_exceptions import ValidationError
from src.domain.value_objects.coordinate import Coordinate


@dataclass(frozen=True)
class GeoBounds(ValueObject):
    """Geospatial bounding box composed of southwest and northeast coordinates."""

    south_west: Coordinate
    north_east: Coordinate

    def __post_init__(self) -> None:
        """Validate bounding box coordinate consistency."""
        if self.south_west.latitude >= self.north_east.latitude:
            msg = "Southwest latitude must be strictly less than northeast latitude"
            raise ValidationError(msg)
        if self.south_west.longitude >= self.north_east.longitude:
            msg = "Southwest longitude must be strictly less than northeast longitude"
            raise ValidationError(msg)
