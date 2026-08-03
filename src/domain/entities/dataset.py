"""Dataset domain entity."""

import uuid
from datetime import datetime

from src.domain.base.entity import Entity
from src.domain.enums.dataset_type import DatasetType, SatelliteType
from src.domain.value_objects.time_range import TimeRange


class Dataset(Entity):
    """Dataset entity representing satellite data collections."""

    def __init__(
        self,
        workflow_id: uuid.UUID,
        satellite: SatelliteType,
        dataset_type: DatasetType,
        time_range: TimeRange,
        spatial_resolution_meters: float,
        entity_id: uuid.UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        """Initialize Dataset entity."""
        super().__init__(entity_id=entity_id, created_at=created_at, updated_at=updated_at)
        self._workflow_id = workflow_id
        self._satellite = satellite
        self._dataset_type = dataset_type
        self._time_range = time_range
        self._spatial_resolution_meters = spatial_resolution_meters

    @property
    def workflow_id(self) -> uuid.UUID:
        """Return workflow UUID."""
        return self._workflow_id

    @property
    def satellite(self) -> SatelliteType:
        """Return satellite constellation."""
        return self._satellite

    @property
    def dataset_type(self) -> DatasetType:
        """Return dataset category."""
        return self._dataset_type

    @property
    def time_range(self) -> TimeRange:
        """Return dataset time range."""
        return self._time_range

    @property
    def spatial_resolution_meters(self) -> float:
        """Return spatial resolution in meters."""
        return self._spatial_resolution_meters
