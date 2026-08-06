"""FigureManager managing figure numbering, captions, image paths, and cross-references."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class ReportFigure:
    """Scientific report figure metadata container."""

    figure_id: str
    figure_number: int
    title: str
    caption: str
    image_path: str
    source_artifact_uuid: str
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)


class FigureManager:
    """Manager for numbering and embedding figures into scientific reports."""

    def __init__(self) -> None:
        self._figures: list[ReportFigure] = []

    def add_figure(
        self,
        figure_id: str,
        title: str,
        caption: str,
        image_path: str,
        source_artifact_uuid: str = "art_unknown",
    ) -> ReportFigure:
        """Register new figure with auto-incrementing figure number."""
        fig_num = len(self._figures) + 1
        fig = ReportFigure(
            figure_id=figure_id,
            figure_number=fig_num,
            title=title,
            caption=caption,
            image_path=image_path,
            source_artifact_uuid=source_artifact_uuid,
        )
        self._figures.append(fig)
        return fig

    def get_figures(self) -> list[ReportFigure]:
        """Return list of all registered figures."""
        return list(self._figures)

    def render_markdown(self) -> str:
        """Render all figures as Markdown text blocks."""
        lines: list[str] = []
        for fig in self._figures:
            lines.append(f"![Figure {fig.figure_number}: {fig.title}]({fig.image_path})")
            lines.append(
                f"*Figure {fig.figure_number}: {fig.caption} "
                f"(Source Artifact: {fig.source_artifact_uuid})*\n"
            )
        return "\n".join(lines)
