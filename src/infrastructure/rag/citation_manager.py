"""CitationManager formatting references in IEEE, APA, BibTeX, and Markdown formats."""

from src.infrastructure.rag.chunking import DocumentChunk


class CitationManager:
    """Formatter for scientific literature citations in IEEE, APA, BibTeX, and Markdown styles."""

    @staticmethod
    def format_ieee(author: str, title: str, journal: str, year: int, doi: str) -> str:
        """Format IEEE citation line."""
        return f'{author}, "{title}," {journal}, {year}. DOI: https://doi.org/{doi}'

    @staticmethod
    def format_apa(author: str, title: str, journal: str, year: int, doi: str) -> str:
        """Format APA citation line."""
        return f"{author} ({year}). {title}. {journal}. https://doi.org/{doi}"

    @staticmethod
    def format_bibtex(
        cite_key: str, author: str, title: str, journal: str, year: int, doi: str
    ) -> str:
        """Format BibTeX entry string."""
        return (
            f"@article{{{cite_key},\n"
            f"  author = {{{author}}},\n"
            f"  title = {{{title}}},\n"
            f"  journal = {{{journal}}},\n"
            f"  year = {{{year}}},\n"
            f"  doi = {{{doi}}}\n"
            f"}}"
        )

    @staticmethod
    def format_markdown(chunk: DocumentChunk) -> str:
        """Format inline markdown citation key."""
        author = chunk.metadata.get("title", "Remote Sensing Literature").split()[0]
        year = chunk.metadata.get("year", 2024)
        return f"[{author} et al., {year}]"
