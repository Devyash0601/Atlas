"""atlas research CLI entry point using argparse and formatted output."""

import argparse
import sys
from pathlib import Path
from typing import Any

from src.application.pipeline.research_pipeline import ResearchPipeline


def main(args: list[str] | None = None) -> int:
    """CLI main function parsing command line arguments and executing pipeline."""
    parser = argparse.ArgumentParser(description="ATLAS-EO Autonomous Research Pipeline CLI")
    parser.add_argument(
        "--question", "-q", required=True, help="Natural language research question"
    )
    parser.add_argument("--location", "-l", default=None, help="Optional study location")
    parser.add_argument("--start-date", default=None, help="Optional start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", default=None, help="Optional end date (YYYY-MM-DD)")
    parser.add_argument("--dataset", default=None, help="Optional preferred dataset asset ID")
    parser.add_argument("--output", "-o", default="projects", help="Output directory path")
    parser.add_argument(
        "--format",
        choices=["pdf", "docx", "md", "all"],
        default="all",
        help="Export report format",
    )

    parsed_args = parser.parse_args(args)

    print("==================================================")
    print("  ATLAS-EO Autonomous Research Execution Pipeline  ")
    print("==================================================")
    print(f"Research Question: {parsed_args.question}")
    if parsed_args.location:
        print(f"Study Area:        {parsed_args.location}")
    print(f"Output Directory:  {parsed_args.output}\n")

    pipeline = ResearchPipeline()
    result: dict[str, Any] = pipeline.run_research(
        question=parsed_args.question,
        location=parsed_args.location,
        start_date=parsed_args.start_date,
        end_date=parsed_args.end_date,
        dataset_preference=parsed_args.dataset,
        output_format=parsed_args.format,
        output_dir=Path(parsed_args.output),
    )

    print("✅ Pipeline Completed Successfully!")
    print(f"Project Package: {result['project_dir']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
