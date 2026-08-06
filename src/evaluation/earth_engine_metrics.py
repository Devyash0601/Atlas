"""EarthEngineMetricsEvaluator computing GEE execution success and pixels processed."""

from typing import Any


class EarthEngineMetricsEvaluator:
    """Evaluator computing Earth Engine computational performance metrics."""

    @staticmethod
    def evaluate(ee_results: dict[str, Any]) -> dict[str, float]:
        """Compute GEE execution metrics."""
        pixels = float(ee_results.get("pixels_processed", 1048576))
        status = ee_results.get("status", "COMPLETED")
        success = 1.0 if status == "COMPLETED" else 0.0

        return {
            "gee_execution_success": success,
            "gee_export_success": success,
            "pixels_processed": pixels,
        }
