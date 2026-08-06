"""PipelineState tracking progress across all 11 execution stages."""

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class PipelineState:
    """State object tracking status, completed stages, and stage timings."""

    current_stage: str = "STAGE_1_QUESTION_VALIDATION"
    status: str = "IDLE"  # IDLE, RUNNING, COMPLETED, FAILED, PAUSED
    completed_stages: list[str] = field(default_factory=list)
    stage_timestamps: dict[str, str] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    STAGES: list[str] = field(
        default_factory=lambda: [
            "STAGE_1_QUESTION_VALIDATION",
            "STAGE_2_RESEARCH_PLANNING",
            "STAGE_3_LITERATURE_RETRIEVAL",
            "STAGE_4_EVIDENCE_VERIFICATION",
            "STAGE_5_WORKFLOW_GRAPH_CONSTRUCTION",
            "STAGE_6_GEE_PLAN_GENERATION",
            "STAGE_7_GEE_EXECUTION",
            "STAGE_8_RESULT_PROCESSING",
            "STAGE_9_PUBLICATION_ENGINE",
            "STAGE_10_EVALUATION_METRICS",
            "STAGE_11_PROJECT_EXPORT",
        ]
    )

    def mark_stage_completed(self, stage_name: str) -> None:
        """Mark stage as completed and record timestamp."""
        if stage_name not in self.completed_stages:
            self.completed_stages.append(stage_name)
        self.stage_timestamps[stage_name] = datetime.now(UTC).isoformat()
