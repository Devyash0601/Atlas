"""Domain service abstract contracts (Interfaces only - NO implementations in domain)."""

from abc import ABC, abstractmethod
from typing import Any

from src.domain.entities.evidence import Evidence
from src.domain.entities.report import Report
from src.domain.entities.verification import Verification
from src.domain.entities.workflow import Workflow
from src.domain.value_objects.research_question import ResearchQuestion


class WorkflowPlanner(ABC):
    """Abstract domain service interface for scientific workflow planning."""

    @abstractmethod
    async def create_plan(self, question: ResearchQuestion, region_name: str) -> Workflow:
        """Create structured execution workflow plan for research question."""
        pass


class EvidenceVerifier(ABC):
    """Abstract domain service interface for evidence claim verification."""

    @abstractmethod
    async def verify_claim(self, claim: str, evidence: Evidence) -> Verification:
        """Verify scientific claim against gathered evidence."""
        pass


class ScientificReasoner(ABC):
    """Abstract domain service interface for multi-modal scientific reasoning."""

    @abstractmethod
    async def reason_about_data(self, dataset_metadata: dict[str, Any]) -> dict[str, Any]:
        """Perform domain reasoning over dataset metadata."""
        pass


class ReportGenerator(ABC):
    """Abstract domain service interface for publication report assembly."""

    @abstractmethod
    async def generate_report(self, workflow_id: str, verifications: list[Verification]) -> Report:
        """Assemble verified scientific findings into publication report."""
        pass
