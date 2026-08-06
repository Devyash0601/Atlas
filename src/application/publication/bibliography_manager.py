"""BibliographyManager sorting, deduplicating, and building reference lists."""

from src.application.publication.citation_manager import CitationEntry


class BibliographyManager:
    """Manager sorting and formatting full bibliography and reference lists."""

    @staticmethod
    def render_markdown(citations: list[CitationEntry], style: str = "IEEE") -> str:
        """Render reference list into Markdown."""
        lines: list[str] = ["## References\n"]
        style_upper = style.upper()

        for idx, cite in enumerate(citations, 1):
            authors_str = ", ".join(cite.authors) if cite.authors else "Anonymous"
            doi_str = f" DOI: https://doi.org/{cite.doi}" if cite.doi else ""

            if style_upper == "IEEE":
                lines.append(
                    f'[{idx}] {authors_str}, "{cite.title}," '
                    f"*{cite.journal_or_venue}*, {cite.year}.{doi_str}"
                )
            elif style_upper == "APA":
                lines.append(
                    f"{authors_str} ({cite.year}). {cite.title}. "
                    f"*{cite.journal_or_venue}*.{doi_str}"
                )
            else:
                lines.append(
                    f"- **[{cite.citation_id}]** {authors_str} ({cite.year}). "
                    f"{cite.title}. *{cite.journal_or_venue}*.{doi_str}"
                )

        return "\n".join(lines)

    @staticmethod
    def render_bibtex(citations: list[CitationEntry]) -> str:
        """Render citation entries into BibTeX string."""
        entries: list[str] = []
        for cite in citations:
            authors_str = " and ".join(cite.authors) if cite.authors else "Unknown"
            doi_line = f"  doi = {{{cite.doi}}},\n" if cite.doi else ""
            entries.append(
                f"@article{{{cite.citation_id},\n"
                f"  author = {{{authors_str}}},\n"
                f"  title = {{{cite.title}}},\n"
                f"  journal = {{{cite.journal_or_venue}}},\n"
                f"  year = {{{cite.year}}},\n"
                f"{doi_line}"
                f"}}"
            )
        return "\n\n".join(entries)
