"""AppendixBuilder formatting execution metadata and prompt versions."""

from src.application.publication.report_context import ReportContext


class AppendixBuilder:
    """Builder generating Appendix section containing execution metadata and environment hashes."""

    @staticmethod
    def build_appendix(context: ReportContext) -> str:
        """Build Markdown Appendix section."""
        lines: list[str] = [
            "## Appendix: Execution & Reproducibility Metadata\n",
            "| Parameter | Value |",
            "| --- | --- |",
            f"| **Research UUID** | `{context.research_uuid}` |",
            f"| **Report Version** | `{context.report_version}` |",
            f"| **Workflow Version** | `{context.workflow_version}` |",
            f"| **Prompt Spec Version** | `{context.prompt_version}` |",
            f"| **Ollama Model Version** | `{context.model_version}` |",
            f"| **Git Commit Hash** | `{context.git_commit_hash}` |",
            f"| **Configuration Hash** | `{context.config_hash}` |",
            f"| **Generation Timestamp** | `{context.generation_timestamp}` |",
            f"| **Author / Engine** | `{context.author}` |",
        ]
        return "\n".join(lines)
