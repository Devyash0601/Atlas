"""Report generation and registration commands."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class GenerateReportCommand:
    """Command to generate publication markdown report."""

    workflow_id: str


@dataclass(frozen=True)
class RegisterDatasetCommand:
    """Command to register retrieved dataset."""

    workflow_id: str
    satellite: str
    dataset_type: str
    start_date: str
    end_date: str
    spatial_resolution_meters: float


@dataclass(frozen=True)
class RegisterExperimentCommand:
    """Command to record experiment run parameters."""

    workflow_id: str
    parameters: dict[str, Any]
    status: str
    execution_time_seconds: float
    logs: str = ""
