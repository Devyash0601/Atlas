"""PipelineValidator auditing project package completeness before final release."""

from pathlib import Path

from src.shared.exceptions.base import AtlasException


class PipelineValidationError(AtlasException):
    """Raised when completed research project directory validation fails."""

    pass


class PipelineValidator:
    """Validator inspecting exported project package directories."""

    @staticmethod
    def validate_project_directory(project_dir: Path) -> bool:
        """Validate presence of required report, metadata, and data files."""
        if not project_dir.exists():
            raise PipelineValidationError(f"Project directory '{project_dir}' does not exist.")

        required_files = [
            "report.md",
            "report.html",
            "report.pdf",
            "report.docx",
            "references.bib",
            "workflow.json",
            "README.md",
            "checksums.json",
        ]

        for req in required_files:
            file_path = project_dir / req
            if not file_path.exists():
                raise PipelineValidationError(
                    f"Required project artifact '{req}' is missing from '{project_dir}'."
                )

        return True
