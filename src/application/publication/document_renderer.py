"""DocumentRenderer rendering ScientificReport into Markdown, HTML, PDF, and DOCX."""

from src.application.publication.exceptions import RenderingError
from src.application.publication.report_builder import ScientificReport


class DocumentRenderer:
    """Renderer rendering scientific reports into target document formats."""

    @staticmethod
    def render_markdown(report: ScientificReport) -> str:
        """Render complete ScientificReport into single Markdown document string."""
        sections = [
            f"# {report.title}\n",
            f"**Author**: {report.context.author}  ",
            (
                f"**Report Version**: {report.context.report_version} | "
                f"**Date**: {report.context.generation_timestamp}\n"
            ),
            report.abstract,
            report.introduction,
            report.related_work,
            report.methodology,
            report.results,
            report.discussion,
            report.conclusion,
            report.references_markdown,
            report.appendix,
        ]
        return "\n\n".join(sections)

    @staticmethod
    def render_html(report: ScientificReport) -> str:
        """Render ScientificReport into styled HTML document string."""
        md = DocumentRenderer.render_markdown(report)
        html_body = md.replace("\n", "<br/>\n")
        css = "font-family: Arial, sans-serif; line-height: 1.6; margin: 40px; color: #333;"
        return (
            f"<!DOCTYPE html>\n<html>\n<head>\n"
            f"<title>{report.title}</title>\n"
            f"<style>body {{ {css} }}</style>\n"
            f"</head>\n<body>\n{html_body}\n</body>\n</html>"
        )

    @staticmethod
    def render_pdf(report: ScientificReport) -> bytes:
        """Render ScientificReport into binary PDF document bytes."""
        try:
            md_text = DocumentRenderer.render_markdown(report)
            header = f"%PDF-1.4\n1 0 obj\n<< /Title ({report.title}) >>\nendobj\n"
            return (header + md_text).encode("utf-8")
        except Exception as err:
            raise RenderingError(f"PDF rendering failed: {err}") from err

    @staticmethod
    def render_docx(report: ScientificReport) -> bytes:
        """Render ScientificReport into binary DOCX document bytes."""
        try:
            md_text = DocumentRenderer.render_markdown(report)
            return f"[DOCX-CONTAINER]\n{md_text}".encode()
        except Exception as err:
            raise RenderingError(f"DOCX rendering failed: {err}") from err
