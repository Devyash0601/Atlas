"""Project Data Transfer Object (DTO)."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ProjectDTO:
    """Read-only DTO representing a research project."""

    id: str
    title: str
    question: str
    region_name: str
    south_west_lat: float
    south_west_lon: float
    north_east_lat: float
    north_east_lon: float
    user_id: str
    status: str
    created_at: str
    updated_at: str

    def to_dict(self) -> dict[str, Any]:
        """Convert DTO to dictionary representation."""
        return {
            "id": self.id,
            "title": self.title,
            "question": self.question,
            "region_name": self.region_name,
            "south_west_lat": self.south_west_lat,
            "south_west_lon": self.south_west_lon,
            "north_east_lat": self.north_east_lat,
            "north_east_lon": self.north_east_lon,
            "user_id": self.user_id,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
