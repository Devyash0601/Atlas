"""TableManager formatting dataset summaries, statistics, and metrics into markdown tables."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ReportTable:
    """Scientific report table container."""

    table_id: str
    table_number: int
    title: str
    headers: list[str]
    rows: list[list[Any]]
    caption: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class TableManager:
    """Manager for numbering and rendering tables in scientific reports."""

    def __init__(self) -> None:
        self._tables: list[ReportTable] = []

    def add_table(
        self,
        table_id: str,
        title: str,
        headers: list[str],
        rows: list[list[Any]],
        caption: str = "",
    ) -> ReportTable:
        """Register new table with auto-incrementing table number."""
        tbl_num = len(self._tables) + 1
        tbl = ReportTable(
            table_id=table_id,
            table_number=tbl_num,
            title=title,
            headers=headers,
            rows=rows,
            caption=caption,
        )
        self._tables.append(tbl)
        return tbl

    def get_tables(self) -> list[ReportTable]:
        """Return list of all registered tables."""
        return list(self._tables)

    def render_markdown(self) -> str:
        """Render all registered tables into Markdown table strings."""
        lines: list[str] = []
        for tbl in self._tables:
            lines.append(f"**Table {tbl.table_number}: {tbl.title}**\n")
            lines.append("| " + " | ".join(tbl.headers) + " |")
            lines.append("| " + " | ".join(["---"] * len(tbl.headers)) + " |")
            for row in tbl.rows:
                lines.append("| " + " | ".join(str(val) for val in row) + " |")
            if tbl.caption:
                lines.append(f"\n*Table {tbl.table_number} Note: {tbl.caption}*")
            lines.append("\n")
        return "\n".join(lines)
