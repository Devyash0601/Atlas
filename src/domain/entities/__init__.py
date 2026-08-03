"""Domain entities package."""

from src.domain.entities.dataset import Dataset
from src.domain.entities.evidence import Evidence
from src.domain.entities.execution_log import ExecutionLog
from src.domain.entities.experiment import Experiment
from src.domain.entities.generated_artifact import GeneratedArtifact
from src.domain.entities.report import Report
from src.domain.entities.research_project import ResearchProject
from src.domain.entities.scientific_paper import ScientificPaper
from src.domain.entities.verification import Verification
from src.domain.entities.workflow import Workflow

__all__ = [
    "Dataset",
    "Evidence",
    "ExecutionLog",
    "Experiment",
    "GeneratedArtifact",
    "Report",
    "ResearchProject",
    "ScientificPaper",
    "Verification",
    "Workflow",
]
