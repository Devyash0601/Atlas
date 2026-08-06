"""PipelineArtifacts managing project directory tree and reproducibility files."""

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from src.application.pipeline.pipeline_context import PipelineContext


class PipelineArtifacts:
    """Manager creating project folder structures and writing checksums & README."""

    def create_project_structure(
        self,
        base_dir: Path,
        project_name: str,
        context: PipelineContext,
        metrics_summary: dict[str, Any],
    ) -> Path:
        """Create structured project directory tree and populate reproducibility files."""
        project_dir = base_dir / project_name
        project_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        subdirs = ["maps", "figures", "tables", "artifacts", "logs", "appendix", "reproducibility"]
        for sub in subdirs:
            (project_dir / sub).mkdir(exist_ok=True)

        # Write environment.json
        env_dict = {
            "research_uuid": context.research_uuid,
            "created_at": context.created_at,
            "prompt_version": context.prompt_version,
            "model_version": context.model_version,
            "system": "ATLAS-EO Production Architecture",
            "git_commit": "v0.5.0-core-platform",
        }
        env_json = json.dumps(env_dict, indent=2)
        (project_dir / "environment.json").write_text(env_json, encoding="utf-8")

        # Write metrics.json
        metrics_json = json.dumps(metrics_summary, indent=2)
        (project_dir / "metrics.json").write_text(metrics_json, encoding="utf-8")

        # Write README.md
        start_d = context.start_date or "2024-01-01"
        end_d = context.end_date or "2024-12-31"
        readme_text = (
            f"# {project_name} — Reproducible Scientific Research Package\n\n"
            f"**Research Question**: {context.question}\n\n"
            f"**Location**: {context.location or 'Global / Specified ROI'}\n"
            f"**Date Range**: {start_d} to {end_d}\n"
            f"**Generated**: {datetime.now(UTC).isoformat()}\n\n"
            f"## Package Contents\n"
            f"- `report.pdf`, `report.docx`, `report.md`, `report.html`: Complete paper\n"
            f"- `references.bib`: BibTeX citations\n"
            f"- `workflow.json`, `environment.json`, `metrics.json`: Metadata\n"
            f"- `checksums.json`: SHA-256 integrity checksums\n"
        )
        (project_dir / "README.md").write_text(readme_text, encoding="utf-8")

        # Generate checksums.json
        checksums: dict[str, str] = {}
        for item in project_dir.iterdir():
            if item.is_file():
                checksums[item.name] = hashlib.sha256(item.read_bytes()).hexdigest()
        chk_json = json.dumps(checksums, indent=2)
        (project_dir / "checksums.json").write_text(chk_json, encoding="utf-8")

        return project_dir
