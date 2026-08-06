"""BenchmarkSuite facade orchestrating platform evaluations and exports."""

from pathlib import Path
from typing import Any

from src.evaluation.benchmark_runner import BenchmarkRunner
from src.evaluation.exporter import EvaluationExporter


class BenchmarkSuite:
    """Production facade running benchmark suites and exporting evaluation packages."""

    def __init__(
        self,
        runner: BenchmarkRunner | None = None,
        exporter: EvaluationExporter | None = None,
    ) -> None:
        self.runner = runner or BenchmarkRunner()
        self.exporter = exporter or EvaluationExporter()

    def run_and_export(self, output_dir: Path | None = None) -> dict[str, Any]:
        """Execute benchmark suite and export leaderboard documentation."""
        summary = self.runner.run_suite()
        target_dir = output_dir or Path("artifacts/benchmarks")

        exported_files = self.exporter.export_suite_results(summary, target_dir)

        return {
            "status": "COMPLETED",
            "summary": summary,
            "exported_files": exported_files,
        }
