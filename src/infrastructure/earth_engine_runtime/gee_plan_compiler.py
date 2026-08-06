"""GEEPlanCompiler translating GEEPlanSpec into deterministic API call trees."""

from typing import Any

from src.infrastructure.earth_engine_runtime.plan_spec import GEEPlanOperation, GEEPlanSpec


class GEEPlanCompiler:
    """Deterministic compiler compiling GEEPlanSpec into structured API execution trees."""

    @staticmethod
    def compile_plan(plan: GEEPlanSpec) -> dict[str, Any]:
        """Compile plan spec into deterministic Earth Engine API call payload."""
        call_tree: list[dict[str, Any]] = []

        for op in plan.operations:
            call_tree.append(
                {
                    "step": op.op_type,
                    "arguments": op.params,
                    "target_dataset": plan.target_dataset,
                }
            )

        return {
            "plan_id": plan.plan_id,
            "target_dataset": plan.target_dataset,
            "spatial_bounds": plan.spatial_bounds,
            "temporal_range": plan.temporal_range,
            "compiled_call_tree": call_tree,
        }

    @classmethod
    def compile(cls, plan_dict: dict[str, Any]) -> GEEPlanSpec:
        """Backward compatibility compile helper returning GEEPlanSpec."""
        return GEEPlanSpec(
            plan_id=plan_dict.get("plan_id", "plan_compiled"),
            target_dataset=plan_dict.get(
                "collection_id", plan_dict.get("target_dataset", "LANDSAT/LC08/C02/T1_L2")
            ),
            operations=[GEEPlanOperation("LoadCollection"), GEEPlanOperation("NDVI")],
            spatial_bounds=plan_dict.get("roi", [2.2, 48.5, 2.5, 49.0]),
            temporal_range=plan_dict.get("time_range", ["2024-01-01", "2024-06-01"]),
        )
