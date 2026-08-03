"""FigureParser extracting figures, captions, and section references."""

from dataclasses import dataclass


@dataclass
class ParsedFigure:
    """Figure representation with caption and page number."""

    figure_id: str
    caption: str
    page_number: int
    referenced_section: str


class FigureParser:
    """Parser extracting figure metadata and linking to claims."""

    @staticmethod
    def parse_figures(figures: list[dict[str, str]]) -> list[ParsedFigure]:
        """Extract parsed figures."""
        return [
            ParsedFigure(
                figure_id=fig.get("id", "Fig1"),
                caption=fig.get("caption", "Figure Caption"),
                page_number=int(fig.get("page", 1)),
                referenced_section="Results",
            )
            for fig in figures
        ]
