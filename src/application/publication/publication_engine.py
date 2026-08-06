"""PublicationEngine main facade converting workflow artifact bundles into scientific reports."""

from pathlib import Path
from typing import Any

from src.application.publication.artifact_collector import WorkflowArtifactBundle
from src.application.publication.export_manager import ExportManager
from src.application.publication.quality_checker import ReportQualityChecker
from src.application.publication.report_builder import ReportBuilder, ScientificReport
from src.application.publication.report_context import ReportContext
from src.application.publication.report_template import ReportTemplate


class PublicationEngine:
    """Production facade orchestrating automated scientific report generation."""

    def __init__(
        self,
        template_name: str = "IEEE",
        quality_checker: ReportQualityChecker | None = None,
        export_manager: ExportManager | None = None,
    ) -> None:
        self.template_name = template_name
        self.quality_checker = quality_checker or ReportQualityChecker()
        self.export_manager = export_manager or ExportManager()

    def generate_report(
        self,
        context: ReportContext,
        bundle: WorkflowArtifactBundle,
        output_dir: Path | None = None,
    ) -> dict[str, Any]:
        """Build, validate, render, and export scientific paper from workflow bundle."""
        template = ReportTemplate.get_template(self.template_name)
        builder = ReportBuilder(context=context, template=template)

        report: ScientificReport = builder.build(bundle)
        self.quality_checker.validate_report(report)

        exported_paths: dict[str, str] = {}
        if output_dir is not None:
            exported_paths = self.export_manager.export_report(report, output_dir)

        return {
            "status": "COMPLETED",
            "report": report,
            "exported_files": exported_paths,
        }
