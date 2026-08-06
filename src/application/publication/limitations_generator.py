"""LimitationsGenerator summarizing low confidence claims, missing evidence, and dataset bounds."""

from typing import Any


class LimitationsGenerator:
    """Generator compiling scientific study limitations and threats to validity."""

    @staticmethod
    def generate_limitations(
        verified_claims: list[dict[str, Any]],
        evidence_items: list[dict[str, Any]],
    ) -> str:
        """Generate structured Limitations and Threats to Validity text block."""
        low_confidence = [c for c in verified_claims if c.get("confidence", 1.0) < 0.7]
        missing_evidence = [e for e in evidence_items if not e.get("has_pdf_source", True)]

        lines: list[str] = [
            "## Discussion & Limitations\n",
            "### Threats to Validity & System Constraints",
            (
                "1. **Spatial & Temporal Scope**: Results apply strictly to defined "
                "Region of Interest (ROI) and specified temporal windows."
            ),
            (
                "2. **Sensor Resolution**: Band resolutions (e.g. 10m Sentinel-2, "
                "30m Landsat) impose sub-pixel mixing limitations."
            ),
        ]

        if low_confidence:
            lines.append(
                f"3. **Claim Confidence Notice**: {len(low_confidence)} claims evaluated "
                "below 0.70 confidence threshold require further field validation."
            )

        if missing_evidence:
            lines.append(
                f"4. **Literature Coverage**: {len(missing_evidence)} claims rely on secondary "
                "metadata extractions without open-access PDF source text."
            )

        lines.append(
            "\n### Future Work\nFuture investigations will integrate SAR imagery (Sentinel-1) "
            "and commercial imagery to resolve sub-pixel land cover misclassifications."
        )

        return "\n\n".join(lines)
