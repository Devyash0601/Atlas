"""ExportManager writing report files (MD, HTML, PDF, DOCX, BibTeX, JSON)."""

import json
from pathlib import Path
from typing import Any

from src.application.publication.document_renderer import DocumentRenderer
from src.application.publication.exceptions import ExportError
from src.application.publication.report_builder import ScientificReport


class ExportManager:
    """Manager writing generated scientific report documents and asset folders to disk."""

    def export_report(self, report: ScientificReport, output_dir: Path) -> dict[str, Any]:
        """Export all scientific paper formats and metadata JSON files to directory."""
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            exported_files: dict[str, str] = {}

            # 1. Export report.md
            md_content = DocumentRenderer.render_markdown(report)
            md_path = output_dir / "report.md"
            md_path.write_text(md_content, encoding="utf-8")
            exported_files["markdown"] = str(md_path)

            # 2. Export report.html
            html_content = DocumentRenderer.render_html(report)
            html_path = output_dir / "report.html"
            html_path.write_text(html_content, encoding="utf-8")
            exported_files["html"] = str(html_path)

            # 3. Export report.pdf
            pdf_bytes = DocumentRenderer.render_pdf(report)
            pdf_path = output_dir / "report.pdf"
            pdf_path.write_bytes(pdf_bytes)
            exported_files["pdf"] = str(pdf_path)

            # 4. Export report.docx
            docx_bytes = DocumentRenderer.render_docx(report)
            docx_path = output_dir / "report.docx"
            docx_path.write_bytes(docx_bytes)
            exported_files["docx"] = str(docx_path)

            # 5. Export references.bib
            bib_path = output_dir / "references.bib"
            bib_path.write_text(report.references_bibtex, encoding="utf-8")
            exported_files["bibtex"] = str(bib_path)

            # 6. Export workflow.json metadata
            metadata_dict = {
                "research_uuid": report.context.research_uuid,
                "title": report.title,
                "author": report.context.author,
                "versions": {
                    "report": report.context.report_version,
                    "workflow": report.context.workflow_version,
                    "prompt": report.context.prompt_version,
                    "model": report.context.model_version,
                },
                "hashes": {
                    "git_commit": report.context.git_commit_hash,
                    "config": report.context.config_hash,
                },
                "timestamp": report.context.generation_timestamp,
            }
            meta_path = output_dir / "workflow.json"
            meta_path.write_text(json.dumps(metadata_dict, indent=2), encoding="utf-8")
            exported_files["metadata"] = str(meta_path)

            return exported_files

        except Exception as err:
            raise ExportError(f"Report export failed: {err}") from err
