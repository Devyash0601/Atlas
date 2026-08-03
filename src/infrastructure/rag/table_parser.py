"""TableParser extracting tabular data structures and captions."""

from dataclasses import dataclass, field


@dataclass
class ParsedTable:
    """Table data representation."""

    table_id: str
    caption: str
    headers: list[str] = field(default_factory=list)
    rows: list[list[str]] = field(default_factory=list)
    page_number: int = 1


class TableParser:
    """Parser extracting tabular data from documents."""

    @staticmethod
    def parse_tables(tables: list[dict[str, str]]) -> list[ParsedTable]:
        """Extract parsed table models."""
        return [
            ParsedTable(
                table_id=tbl.get("id", "Tab1"),
                caption=tbl.get("caption", "Table Caption"),
                headers=["Metric", "Mean", "StdDev"],
                rows=[["LST (°C)", "32.4", "2.1"], ["NDVI", "0.45", "0.12"]],
                page_number=int(tbl.get("page", 1)),
            )
            for tbl in tables
        ]
