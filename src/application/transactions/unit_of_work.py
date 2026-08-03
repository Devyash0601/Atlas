"""Abstract UnitOfWork interface defining transaction boundaries and repository accessors."""

from abc import ABC, abstractmethod
from types import TracebackType

from src.domain.repositories.interfaces import (
    DatasetRepository,
    EvidenceRepository,
    ExperimentRepository,
    ProjectRepository,
    ReportRepository,
    ScientificPaperRepository,
    VerificationRepository,
    WorkflowRepository,
)


class UnitOfWork(ABC):
    """Abstract UnitOfWork pattern managing transactions across repositories."""

    projects: ProjectRepository
    workflows: WorkflowRepository
    datasets: DatasetRepository
    evidence: EvidenceRepository
    reports: ReportRepository
    experiments: ExperimentRepository
    verifications: VerificationRepository
    papers: ScientificPaperRepository

    async def __aenter__(self) -> "UnitOfWork":
        """Enter transaction async context manager."""
        await self.begin()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit transaction context manager, rolling back if exception occurred."""
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()

    @abstractmethod
    async def begin(self) -> None:
        """Begin transaction boundary."""
        pass

    @abstractmethod
    async def commit(self) -> None:
        """Commit transaction changes."""
        pass

    @abstractmethod
    async def rollback(self) -> None:
        """Roll back transaction changes."""
        pass
