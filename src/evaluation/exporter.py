"""EvaluationExporter writing evaluation reports and leaderboard files to disk."""

import json
from pathlib import Path
from typing import Any

from src.evaluation.leaderboard import LeaderboardGenerator


class EvaluationExporter:
    """Exporter writing evaluation JSON, CSV, and Leaderboard files."""

    def export_suite_results(self, summary: dict[str, Any], output_dir: Path) -> dict[str, str]:
        """Export benchmark JSON, leaderboard.md, leaderboard.html, and metrics.csv."""
        output_dir.mkdir(parents=True, exist_ok=True)
        exported: dict[str, str] = {}

        # 1. benchmark.json
        json_path = output_dir / "benchmark.json"
        json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        exported["json"] = str(json_path)

        # 2. leaderboard.md
        md_text = LeaderboardGenerator.render_markdown(summary)
        md_path = output_dir / "leaderboard.md"
        md_path.write_text(md_text, encoding="utf-8")
        exported["markdown"] = str(md_path)

        # 3. leaderboard.html
        html_text = LeaderboardGenerator.render_html(summary)
        html_path = output_dir / "leaderboard.html"
        html_path.write_text(html_text, encoding="utf-8")
        exported["html"] = str(html_path)

        # 4. metrics.csv
        csv_lines = ["benchmark_id,category,overall_score,passed\n"]
        for res in summary.get("benchmark_results", []):
            csv_lines.append(
                f"{res.get('benchmark_id')},{res.get('category')},{res.get('overall_score')},{res.get('passed')}\n"
            )
        csv_path = output_dir / "metrics.csv"
        csv_path.write_text("".join(csv_lines), encoding="utf-8")
        exported["csv"] = str(csv_path)

        return exported
