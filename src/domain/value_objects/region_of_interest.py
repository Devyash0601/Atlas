"""Region of Interest (AOI) value object."""

from dataclasses import dataclass

from src.domain.base.value_object import ValueObject
from src.domain.exceptions.domain_exceptions import ValidationError
from src.domain.value_objects.geo_bounds import GeoBounds


@dataclass(frozen=True)
class RegionOfInterest(ValueObject):
    """Region of Interest containing a location name and bounding box."""

    name: str
    bounds: GeoBounds

    def __post_init__(self) -> None:
        """Validate region name."""
        if not self.name or not self.name.strip():
            raise ValidationError("Region name cannot be empty")
