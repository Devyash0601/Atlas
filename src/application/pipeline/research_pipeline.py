"""ResearchPipeline main facade orchestrating autonomous research pipeline executions."""

import uuid
from pathlib import Path
from typing import Any

from src.application.pipeline.pipeline_context import PipelineContext
from src.application.pipeline.pipeline_executor import PipelineExecutor
from src.application.pipeline.pipeline_metrics import PipelineMetrics
from src.application.pipeline.pipeline_state import PipelineState


class ResearchPipeline:
    """Production facade orchestrating end-to-end research pipelines."""

    def __init__(self, executor: PipelineExecutor | None = None) -> None:
        self.executor = executor or PipelineExecutor()

    def run_research(
        self,
        question: str,
        location: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        dataset_preference: str | None = None,
        output_format: str = "all",
        output_dir: Path | None = None,
    ) -> dict[str, Any]:
        """Execute complete 11-stage research pipeline from natural language question."""
        research_uuid = f"res_{uuid.uuid4().hex[:8]}"
        context = PipelineContext(
            research_uuid=research_uuid,
            question=question,
            location=location,
            start_date=start_date,
            end_date=end_date,
            dataset_preference=dataset_preference,
            output_format=output_format,
        )

        state = PipelineState()
        metrics = PipelineMetrics()
        base_dir = output_dir or Path("projects")

        return self.executor.execute_pipeline(
            context=context,
            state=state,
            metrics=metrics,
            output_base_dir=base_dir,
        )
