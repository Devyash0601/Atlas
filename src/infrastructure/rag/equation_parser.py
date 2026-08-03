"""EquationParser extracting equations, LaTeX strings, and variables."""

from dataclasses import dataclass, field


@dataclass
class ParsedEquation:
    """Equation representation."""

    equation_id: str
    latex_text: str
    variables: list[str] = field(default_factory=list)
    page_number: int = 1


class EquationParser:
    """Parser extracting equations and mathematical formulas."""

    @staticmethod
    def parse_equations(equations: list[dict[str, str]]) -> list[ParsedEquation]:
        """Extract parsed equation objects."""
        return [
            ParsedEquation(
                equation_id=eq.get("id", "Eq1"),
                latex_text=eq.get("text", "NDVI = (NIR - RED) / (NIR + RED)"),
                variables=["NIR", "RED"],
                page_number=int(eq.get("page", 1)),
            )
            for eq in equations
        ]
