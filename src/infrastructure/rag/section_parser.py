"""SectionParser parsing document section hierarchies."""

from src.infrastructure.rag.pdf_parser import ParsedSection


class SectionParser:
    """Parser extracting hierarchical sections and subsections."""

    @staticmethod
    def parse_sections(sections: list[ParsedSection]) -> list[dict[str, str]]:
        """Format section hierarchy list."""
        return [
            {"title": s.title, "content": s.content, "page": str(s.page_number)} for s in sections
        ]
