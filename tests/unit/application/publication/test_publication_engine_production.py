"""Unit tests for Sprint 5 Production Publication Engine Subsystem."""

from pathlib import Path

import pytest

from src.application.publication.artifact_collector import (
    WorkflowArtifactBundle,
)
from src.application.publication.bibliography_manager import BibliographyManager
from src.application.publication.citation_manager import CitationEntry, CitationManager
from src.application.publication.document_renderer import DocumentRenderer
from src.application.publication.exceptions import (
    CitationError,
    ReportValidationError,
)
from src.application.publication.figure_manager import FigureManager
from src.application.publication.publication_engine import PublicationEngine
from src.application.publication.quality_checker import ReportQualityChecker
from src.application.publication.report_builder import ReportBuilder, ScientificReport
from src.application.publication.report_context import ReportContext
from src.application.publication.report_template import ReportTemplate
from src.application.publication.table_manager import TableManager


def test_report_context_and_template() -> None:
    """Verify ReportContext initialization and ReportTemplate factory layout specifications."""
    context = ReportContext(
        research_uuid="res_12345",
        research_question="How does urban heat island severity correlate with NDVI in Paris?",
    )
    assert context.research_uuid == "res_12345"
    assert "Paris" in context.research_question

    tmpl = ReportTemplate.get_template("IEEE")
    assert tmpl.name == "IEEE"
    assert len(tmpl.sections_order) > 0

    elsevier_tmpl = ReportTemplate.get_template("ELSEVIER")
    assert elsevier_tmpl.name == "ELSEVIER"


def test_figure_and_table_managers() -> None:
    """Verify FigureManager and TableManager numbering, registration, and markdown rendering."""
    fig_mgr = FigureManager()
    fig1 = fig_mgr.add_figure(
        figure_id="fig_ndvi",
        title="NDVI Map",
        caption="Normalized Difference Vegetation Index.",
        image_path="figures/ndvi.png",
    )
    assert fig1.figure_number == 1
    assert len(fig_mgr.get_figures()) == 1
    assert "figures/ndvi.png" in fig_mgr.render_markdown()

    tbl_mgr = TableManager()
    tbl1 = tbl_mgr.add_table(
        table_id="tbl_stats",
        title="NDVI Statistics",
        headers=["Parameter", "Value"],
        rows=[["Mean", 0.48], ["Median", 0.45]],
        caption="Statistical summary table.",
    )
    assert tbl1.table_number == 1
    assert len(tbl_mgr.get_tables()) == 1
    assert "| Parameter | Value |" in tbl_mgr.render_markdown()


def test_citation_and_bibliography_managers() -> None:
    """Verify CitationManager inline tag formatting (IEEE/APA) and BibliographyManager outputs."""
    cite_mgr = CitationManager(style="IEEE")
    cite_entry = CitationEntry(
        citation_id="smith2024",
        authors=["Smith, J.", "Doe, A."],
        title="Remote Sensing of Urban Vegetation",
        journal_or_venue="Remote Sensing of Environment",
        year=2024,
        doi="10.1016/j.rse.2024.10000",
    )
    cite_mgr.add_citation(cite_entry)

    tag = cite_mgr.format_inline("smith2024")
    assert tag == "[1]"

    apa_mgr = CitationManager(style="APA")
    apa_mgr.add_citation(cite_entry)
    assert apa_mgr.format_inline("smith2024") == "(Smith, J. et al., 2024)"

    with pytest.raises(CitationError):
        cite_mgr.format_inline("invalid_cite_id")

    citations = cite_mgr.list_citations()
    ref_md = BibliographyManager.render_markdown(citations, style="IEEE")
    ref_bib = BibliographyManager.render_bibtex(citations)

    assert "Smith, J." in ref_md
    assert "@article{smith2024" in ref_bib


def test_report_builder_and_quality_checker() -> None:
    """Verify ReportBuilder assembly and ReportQualityChecker validation rules."""
    context = ReportContext(
        research_uuid="res_67890",
        research_question="What is the impact of drought on Amazon canopy moisture?",
    )
    bundle = WorkflowArtifactBundle(
        research_question=context.research_question,
        evidence_items=[
            {
                "citation_id": "silva2023",
                "authors": ["Silva, M."],
                "title": "Amazon Canopy Dynamics",
                "journal": "Nature Climate Change",
                "year": 2023,
            }
        ],
        verified_claims=[{"claim": "NDWI declined by 15%", "confidence": 0.85}],
        ee_results={"pixels_processed": 2097152},
        figures=[
            {
                "figure_id": "fig_ndwi",
                "title": "NDWI Canopy Map",
                "caption": "Canopy water index.",
                "image_path": "figures/ndwi.png",
            }
        ],
        tables=[
            {
                "table_id": "tbl_canopy",
                "title": "Canopy Statistics",
                "headers": ["Year", "Mean NDWI"],
                "rows": [[2020, 0.42], [2023, 0.35]],
            }
        ],
        execution_history=[{"node_id": "node_1", "task_type": "DataIngest", "status": "COMPLETED"}],
        metrics={"total_execution_time_sec": 4.5},
    )

    builder = ReportBuilder(context)
    report = builder.build(bundle)

    assert report.title == context.title
    assert "Amazon" in report.abstract
    assert ReportQualityChecker.validate_report(report) is True

    # Invalid empty title check
    invalid_report = ScientificReport(
        context=context,
        template=ReportTemplate(),
        title="",
        abstract="Abstract",
        introduction="Intro",
        related_work="Work",
        methodology="Method",
        results="Results",
        discussion="Discussion",
        conclusion="Conclusion",
        references_markdown="Refs",
        references_bibtex="Bib",
        appendix="App",
    )
    with pytest.raises(ReportValidationError):
        ReportQualityChecker.validate_report(invalid_report)


def test_document_renderer_and_publication_engine(tmp_path: Path) -> None:
    """Verify DocumentRenderer exports (MD/HTML/PDF/DOCX) and PublicationEngine end-to-end flow."""
    context = ReportContext(
        research_uuid="res_e2e",
        research_question="Evaluating coastal erosion rates using Sentinel-2 time series.",
    )
    bundle = WorkflowArtifactBundle(
        research_question=context.research_question,
        evidence_items=[],
        verified_claims=[],
        ee_results={"pixels_processed": 500000},
        figures=[],
        tables=[],
        execution_history=[],
        metrics={"total_execution_time_sec": 1.5},
    )

    engine = PublicationEngine(template_name="IEEE")
    outcome = engine.generate_report(context=context, bundle=bundle, output_dir=tmp_path)

    assert outcome["status"] == "COMPLETED"
    assert isinstance(outcome["report"], ScientificReport)

    exported = outcome["exported_files"]
    assert Path(exported["markdown"]).exists()
    assert Path(exported["html"]).exists()
    assert Path(exported["pdf"]).exists()
    assert Path(exported["docx"]).exists()
    assert Path(exported["bibtex"]).exists()
    assert Path(exported["metadata"]).exists()

    md_text = DocumentRenderer.render_markdown(outcome["report"])
    html_text = DocumentRenderer.render_html(outcome["report"])
    pdf_bytes = DocumentRenderer.render_pdf(outcome["report"])
    docx_bytes = DocumentRenderer.render_docx(outcome["report"])

    assert len(md_text) > 0
    assert "<html>" in html_text
    assert len(pdf_bytes) > 0
    assert len(docx_bytes) > 0
