"""CitationManager formatting inline citations in IEEE, APA, BibTeX, and Markdown styles."""

from dataclasses import dataclass

from src.application.publication.exceptions import CitationError


@dataclass(frozen=True)
class CitationEntry:
    """Scientific paper citation entry container."""

    citation_id: str
    authors: list[str]
    title: str
    journal_or_venue: str
    year: int
    doi: str = ""
    volume: str = ""
    issue: str = ""
    pages: str = ""


class CitationManager:
    """Manager providing inline citation formatting and traceability checks."""

    def __init__(self, style: str = "IEEE") -> None:
        self.style = style.upper()
        self._citations: dict[str, CitationEntry] = {}
        self._order: list[str] = []

    def add_citation(self, entry: CitationEntry) -> None:
        """Register citation entry."""
        if entry.citation_id not in self._citations:
            self._citations[entry.citation_id] = entry
            self._order.append(entry.citation_id)

    def format_inline(self, citation_id: str) -> str:
        """Format inline citation reference tag."""
        if citation_id not in self._citations:
            raise CitationError(f"Citation ID '{citation_id}' is not registered.")

        if self.style == "IEEE":
            num = self._order.index(citation_id) + 1
            return f"[{num}]"
        elif self.style == "APA":
            entry = self._citations[citation_id]
            first_author = entry.authors[0] if entry.authors else "Unknown"
            if len(entry.authors) > 1:
                return f"({first_author} et al., {entry.year})"
            return f"({first_author}, {entry.year})"
        else:
            return f"[{citation_id}]"

    def list_citations(self) -> list[CitationEntry]:
        """Return list of ordered citation entries."""
        return [self._citations[cid] for cid in self._order]
