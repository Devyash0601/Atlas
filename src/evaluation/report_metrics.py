"""ReportMetrics evaluating section completeness and reproducibility score."""

from typing import Any


class ReportMetrics:
    """Evaluator computing publication report quality scores."""

    @staticmethod
    def evaluate(report_data: dict[str, Any]) -> dict[str, float]:
        """Compute report completeness and reproducibility score."""
        title = bool(report_data.get("title"))
        abstract = bool(report_data.get("abstract"))
        intro = bool(report_data.get("introduction"))
        results = bool(report_data.get("results"))

        sections_present = sum([title, abstract, intro, results])
        completeness = round(sections_present / 4.0, 4)

        return {
            "section_completeness": completeness,
            "reproducibility_score": 1.0 if completeness >= 0.75 else 0.5,
        }
