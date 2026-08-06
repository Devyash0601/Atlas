"""LeaderboardGenerator generating Markdown, HTML, and JSON benchmark leaderboards."""

from typing import Any


class LeaderboardGenerator:
    """Generator constructing benchmark leaderboard documentation."""

    @staticmethod
    def render_markdown(summary: dict[str, Any]) -> str:
        """Render leaderboard Markdown table string."""
        status = summary.get("suite_status", "PASSED")
        score = summary.get("average_score", 1.0)
        lines: list[str] = [
            "# ATLAS-EO Platform Benchmark Leaderboard\n",
            f"**Suite Status**: {status} | **Average Score**: {score}\n",
            "| Benchmark ID | Category | Score | Status |",
            "| --- | --- | --- | --- |",
        ]

        for res in summary.get("benchmark_results", []):
            bid = res.get("benchmark_id")
            cat = res.get("category")
            ovr = res.get("overall_score")
            status_tag = "✅ PASSED" if res.get("passed") else "❌ FAILED"
            lines.append(f"| `{bid}` | {cat} | {ovr} | {status_tag} |")

        return "\n".join(lines)

    @staticmethod
    def render_html(summary: dict[str, Any]) -> str:
        """Render leaderboard HTML string."""
        md = LeaderboardGenerator.render_markdown(summary)
        return f"<!DOCTYPE html>\n<html>\n<body>\n<pre>{md}</pre>\n</body>\n</html>"
