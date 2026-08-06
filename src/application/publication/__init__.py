"""Publication Engine package."""

from src.application.publication.appendix_builder import AppendixBuilder
from src.application.publication.artifact_collector import (
    ArtifactCollector,
    WorkflowArtifactBundle,
)
from src.application.publication.bibliography_manager import BibliographyManager
from src.application.publication.citation_manager import CitationEntry, CitationManager
from src.application.publication.document_renderer import DocumentRenderer
from src.application.publication.exceptions import (
    CitationError,
    ExportError,
    PublicationError,
    RenderingError,
    ReportValidationError,
)
from src.application.publication.export_manager import ExportManager
from src.application.publication.figure_manager import FigureManager, ReportFigure
from src.application.publication.limitations_generator import LimitationsGenerator
from src.application.publication.publication_engine import PublicationEngine
from src.application.publication.quality_checker import ReportQualityChecker
from src.application.publication.report_builder import ReportBuilder, ScientificReport
from src.application.publication.report_context import ReportContext
from src.application.publication.report_template import ReportTemplate
from src.application.publication.table_manager import ReportTable, TableManager
from src.application.publication.workflow_summary import WorkflowSummaryGenerator

__all__ = [
    "AppendixBuilder",
    "ArtifactCollector",
    "BibliographyManager",
    "CitationEntry",
    "CitationError",
    "CitationManager",
    "DocumentRenderer",
    "ExportError",
    "ExportManager",
    "FigureManager",
    "LimitationsGenerator",
    "PublicationEngine",
    "PublicationError",
    "QualityChecker",
    "RenderingError",
    "ReportBuilder",
    "ReportContext",
    "ReportFigure",
    "ReportQualityChecker",
    "ReportTable",
    "ReportTemplate",
    "ReportValidationError",
    "ScientificReport",
    "TableManager",
    "WorkflowArtifactBundle",
    "WorkflowSummaryGenerator",
]
