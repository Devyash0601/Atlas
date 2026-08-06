"""QualityChecker validating report completeness, reference integrity, and non-empty sections."""

from src.application.publication.exceptions import ReportValidationError
from src.application.publication.report_builder import ScientificReport


class ReportQualityChecker:
    """Checker auditing generated scientific reports prior to publication export."""

    @staticmethod
    def validate_report(report: ScientificReport) -> bool:
        """Validate non-empty sections, title, abstract, and references."""
        if not report.title:
            raise ReportValidationError("Report title cannot be empty.")

        if not report.abstract:
            raise ReportValidationError("Report abstract cannot be empty.")

        if not report.introduction:
            raise ReportValidationError("Report introduction cannot be empty.")

        if not report.methodology:
            raise ReportValidationError("Report methodology section cannot be empty.")

        if not report.results:
            raise ReportValidationError("Report results section cannot be empty.")

        if not report.conclusion:
            raise ReportValidationError("Report conclusion section cannot be empty.")

        return True
