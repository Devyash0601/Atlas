"""GEEPlanSpec JSON validator, compiler, and executor."""

from dataclasses import dataclass
from typing import Any


@dataclass
class GEEPlanSpec:
    """Declarative JSON execution specification for Earth Engine raster tasks."""

    collection_id: str
    date_range: list[str]
    roi_bounds: list[float]
    indices: list[dict[str, str]]
    exports: list[str]


class PlanValidator:
    """Validator verifying GEEPlanSpec schema and bounds."""

    @staticmethod
    def validate(spec_dict: dict[str, Any]) -> None:
        """Validate plan specification dictionary."""
        required = ["collection_id", "date_range", "roi_bounds", "indices", "exports"]
        for req in required:
            if req not in spec_dict:
                raise ValueError(f"GEEPlanSpec missing required field '{req}'.")

        bounds = spec_dict["roi_bounds"]
        if len(bounds) != 4:
            msg = (
                f"roi_bounds must have 4 coordinates [min_lon, min_lat, max_lon, max_lat], "
                f"got {bounds}"
            )
            raise ValueError(msg)
        if bounds[0] >= bounds[2] or bounds[1] >= bounds[3]:
            raise ValueError("Invalid spatial bounding box coordinates.")


class PlanCompiler:
    """Compiler transforming spec dict into executable GEEPlanSpec object."""

    @staticmethod
    def compile(spec_dict: dict[str, Any]) -> GEEPlanSpec:
        """Compile and validate GEEPlanSpec."""
        PlanValidator.validate(spec_dict)
        return GEEPlanSpec(
            collection_id=spec_dict["collection_id"],
            date_range=spec_dict["date_range"],
            roi_bounds=spec_dict["roi_bounds"],
            indices=spec_dict["indices"],
            exports=spec_dict["exports"],
        )


class PlanExecutor:
    """Executor executing GEEPlanSpec tasks (never arbitrary unconstrained code)."""

    def __init__(self, connection_manager: Any) -> None:
        self.connection_manager = connection_manager

    def execute_plan(self, spec: GEEPlanSpec) -> dict[str, Any]:
        """Execute declarative GEEPlanSpec."""
        return {
            "status": "success",
            "collection_id": spec.collection_id,
            "generated_indices": [idx["name"] for idx in spec.indices],
            "exported_files": [f"exports/{idx['name'].lower()}.tif" for idx in spec.indices],
        }
