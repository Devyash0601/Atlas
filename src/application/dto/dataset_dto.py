"""Dataset DTO."""

from dataclasses import dataclass


@dataclass(frozen=True)
class DatasetDTO:
    """Read-only DTO for Dataset."""

    id: str
    workflow_id: str
    satellite: str
    dataset_type: str
    start_date: str
    end_date: str
    spatial_resolution_meters: float
    created_at: str
