"""Abstract repository interfaces for domain entities."""

import uuid
from abc import ABC, abstractmethod

from src.domain.base.repository import Repository
from src.domain.entities.dataset import Dataset
from src.domain.entities.evidence import Evidence
from src.domain.entities.experiment import Experiment
from src.domain.entities.report import Report
from src.domain.entities.research_project import ResearchProject
from src.domain.entities.scientific_paper import ScientificPaper
from src.domain.entities.verification import Verification
from src.domain.entities.workflow import Workflow


class ProjectRepository(Repository[ResearchProject], ABC):
    """Repository contract for ResearchProject aggregate root."""

    @abstractmethod
    async def find_by_user_id(self, user_id: uuid.UUID) -> list[ResearchProject]:
        """Find projects owned by user."""
        pass


class WorkflowRepository(Repository[Workflow], ABC):
    """Repository contract for Workflow entity."""

    @abstractmethod
    async def find_by_project_id(self, project_id: uuid.UUID) -> list[Workflow]:
        """Find workflows attached to project."""
        pass


class DatasetRepository(Repository[Dataset], ABC):
    """Repository contract for Dataset entity."""

    @abstractmethod
    async def find_by_workflow_id(self, workflow_id: uuid.UUID) -> list[Dataset]:
        """Find datasets attached to workflow."""
        pass


class EvidenceRepository(Repository[Evidence], ABC):
    """Repository contract for Evidence entity."""

    @abstractmethod
    async def find_by_workflow_id(self, workflow_id: uuid.UUID) -> list[Evidence]:
        """Find evidence gathered for workflow."""
        pass


class ReportRepository(Repository[Report], ABC):
    """Repository contract for Report entity."""

    @abstractmethod
    async def find_by_workflow_id(self, workflow_id: uuid.UUID) -> Report | None:
        """Find report generated for workflow."""
        pass


class ExperimentRepository(Repository[Experiment], ABC):
    """Repository contract for Experiment entity."""

    @abstractmethod
    async def find_by_workflow_id(self, workflow_id: uuid.UUID) -> list[Experiment]:
        """Find experiments associated with workflow."""
        pass


class VerificationRepository(Repository[Verification], ABC):
    """Repository contract for Verification entity."""

    @abstractmethod
    async def find_by_workflow_id(self, workflow_id: uuid.UUID) -> list[Verification]:
        """Find verifications executed for workflow."""
        pass


class ScientificPaperRepository(Repository[ScientificPaper], ABC):
    """Repository contract for ScientificPaper entity."""

    @abstractmethod
    async def find_by_doi(self, doi: str) -> ScientificPaper | None:
        """Find paper by DOI identifier."""
        pass
