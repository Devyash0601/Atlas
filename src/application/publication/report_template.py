"""ReportTemplate providing IEEE, Elsevier, and Generic scientific report layouts."""

from dataclasses import dataclass, field


@dataclass
class ReportTemplate:
    """Template defining section headers and layout order for scientific papers."""

    name: str = "IEEE"
    header_style: str = "IEEE"
    sections_order: list[str] = field(
        default_factory=lambda: [
            "title_abstract",
            "introduction",
            "related_work",
            "methodology",
            "results",
            "discussion_limitations",
            "conclusion",
            "references",
            "appendix",
        ]
    )

    @classmethod
    def get_template(cls, template_name: str = "IEEE") -> "ReportTemplate":
        """Factory returning named ReportTemplate layout specification."""
        name_upper = template_name.upper()
        if name_upper in ("IEEE", "ELSEVIER", "GENERIC"):
            return cls(name=name_upper, header_style=name_upper)
        return cls(name="GENERIC", header_style="GENERIC")
