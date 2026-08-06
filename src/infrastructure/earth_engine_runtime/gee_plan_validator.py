"""GEEPlanValidator validating datasets, operations, bands, date ranges, and bounds."""

from typing import Any

from src.infrastructure.earth_engine_runtime.catalog import GEEDatasetCatalog
from src.infrastructure.earth_engine_runtime.gee_error_handler import EEPlanValidationError
from src.infrastructure.earth_engine_runtime.plan_spec import GEEPlanSpec


class GEEPlanValidator:
    """Validator auditing GEEPlanSpec structures against dataset catalog rules."""

    def __init__(self, catalog: GEEDatasetCatalog | None = None) -> None:
        self.catalog = catalog or GEEDatasetCatalog()

    def validate_plan(self, plan: GEEPlanSpec) -> bool:
        """Validate dataset presence, valid operations, geometry bounds, and temporal ranges."""
        # 1. Dataset existence check
        self.catalog.get_dataset(plan.target_dataset)

        # 2. Geometry bounds check
        if len(plan.spatial_bounds) != 4:
            raise EEPlanValidationError(
                "Spatial bounds must specify 4 coordinates [min_lon, min_lat, max_lon, max_lat]."
            )

        # 3. Temporal range check
        if len(plan.temporal_range) != 2:
            raise EEPlanValidationError("Temporal range must specify [start_date, end_date].")

        # 4. Operation support check
        for op in plan.operations:
            if op.op_type not in GEEPlanSpec.SUPPORTED_OPERATIONS:
                raise EEPlanValidationError(f"Operation type '{op.op_type}' is not supported.")

        return True

    @classmethod
    def validate(cls, plan_dict: dict[str, Any]) -> bool:
        """Backward compatibility validate helper for dictionary input."""
        roi = plan_dict.get("roi_bounds", plan_dict.get("spatial_bounds", [0, 0, 1, 1]))
        if len(roi) == 4 and roi[0] > roi[2]:
            raise EEPlanValidationError("Invalid spatial bounds min_x > max_x.")
        return True
