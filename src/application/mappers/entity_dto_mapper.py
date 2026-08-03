"""Bidirectional entity-to-DTO conversion mappers."""

from src.application.dto.dataset_dto import DatasetDTO
from src.application.dto.evidence_dto import EvidenceDTO
from src.application.dto.execution_log_dto import ExecutionLogDTO
from src.application.dto.experiment_dto import ExperimentDTO
from src.application.dto.generated_artifact_dto import GeneratedArtifactDTO
from src.application.dto.project_dto import ProjectDTO
from src.application.dto.report_dto import ReportDTO
from src.application.dto.scientific_paper_dto import ScientificPaperDTO
from src.application.dto.verification_dto import VerificationDTO
from src.application.dto.workflow_dto import WorkflowDTO
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


class EntityDTOMapper:
    """Pure conversion utilities mapping Domain Entities to Application DTOs."""

    @staticmethod
    def project_to_dto(project: ResearchProject) -> ProjectDTO:
        """Map ResearchProject aggregate root to ProjectDTO."""
        return ProjectDTO(
            id=str(project.id),
            title=project.title,
            question=project.question.text,
            region_name=project.roi.name,
            south_west_lat=project.roi.bounds.south_west.latitude,
            south_west_lon=project.roi.bounds.south_west.longitude,
            north_east_lat=project.roi.bounds.north_east.latitude,
            north_east_lon=project.roi.bounds.north_east.longitude,
            user_id=str(project.user_id),
            status=project.status.value,
            created_at=project.created_at.isoformat(),
            updated_at=project.updated_at.isoformat(),
        )

    @staticmethod
    def workflow_to_dto(workflow: Workflow) -> WorkflowDTO:
        """Map Workflow entity to WorkflowDTO."""
        return WorkflowDTO(
            id=str(workflow.id),
            project_id=str(workflow.project_id),
            planner_output=workflow.planner_output,
            status=workflow.status.value,
            created_at=workflow.created_at.isoformat(),
            updated_at=workflow.updated_at.isoformat(),
        )

    @staticmethod
    def evidence_to_dto(evidence: Evidence) -> EvidenceDTO:
        """Map Evidence entity to EvidenceDTO."""
        return EvidenceDTO(
            id=str(evidence.id),
            workflow_id=str(evidence.workflow_id),
            source_citation=evidence.source_citation,
            claim_summary=evidence.claim_summary,
            confidence_score=evidence.confidence.score,
            created_at=evidence.created_at.isoformat(),
        )

    @staticmethod
    def verification_to_dto(verification: Verification) -> VerificationDTO:
        """Map Verification entity to VerificationDTO."""
        return VerificationDTO(
            id=str(verification.id),
            workflow_id=str(verification.workflow_id),
            evidence_id=str(verification.evidence_id),
            status=verification.status.value,
            confidence_score=verification.confidence.score,
            notes=verification.notes,
            created_at=verification.created_at.isoformat(),
        )

    @staticmethod
    def dataset_to_dto(dataset: Dataset) -> DatasetDTO:
        """Map Dataset entity to DatasetDTO."""
        return DatasetDTO(
            id=str(dataset.id),
            workflow_id=str(dataset.workflow_id),
            satellite=dataset.satellite.value,
            dataset_type=dataset.dataset_type.value,
            start_date=dataset.time_range.start_date.isoformat(),
            end_date=dataset.time_range.end_date.isoformat(),
            spatial_resolution_meters=dataset.spatial_resolution_meters,
            created_at=dataset.created_at.isoformat(),
        )

    @staticmethod
    def experiment_to_dto(experiment: Experiment) -> ExperimentDTO:
        """Map Experiment entity to ExperimentDTO."""
        return ExperimentDTO(
            id=str(experiment.id),
            workflow_id=str(experiment.workflow_id),
            parameters=experiment.parameters,
            status=experiment.status.value,
            execution_time_seconds=experiment.execution_time_seconds,
            logs=experiment.logs,
            created_at=experiment.created_at.isoformat(),
        )

    @staticmethod
    def scientific_paper_to_dto(paper: ScientificPaper) -> ScientificPaperDTO:
        """Map ScientificPaper entity to ScientificPaperDTO."""
        return ScientificPaperDTO(
            id=str(paper.id),
            title=paper.title,
            authors=paper.authors,
            year=paper.year,
            doi=paper.doi,
            abstract=paper.abstract,
            created_at=paper.created_at.isoformat(),
        )

    @staticmethod
    def artifact_to_dto(artifact: GeneratedArtifact) -> GeneratedArtifactDTO:
        """Map GeneratedArtifact entity to GeneratedArtifactDTO."""
        return GeneratedArtifactDTO(
            id=str(artifact.id),
            workflow_id=str(artifact.workflow_id),
            artifact_type=artifact.artifact_type.value,
            file_path=artifact.file_path,
            size_bytes=artifact.size_bytes,
            created_at=artifact.created_at.isoformat(),
        )

    @staticmethod
    def report_to_dto(report: Report) -> ReportDTO:
        """Map Report entity to ReportDTO."""
        return ReportDTO(
            id=str(report.id),
            workflow_id=str(report.workflow_id),
            markdown_content=report.markdown_content,
            export_path=report.export_path,
            created_at=report.created_at.isoformat(),
        )

    @staticmethod
    def execution_log_to_dto(log: ExecutionLog) -> ExecutionLogDTO:
        """Map ExecutionLog entity to ExecutionLogDTO."""
        return ExecutionLogDTO(
            id=str(log.id),
            workflow_id=str(log.workflow_id),
            step_name=log.step_name,
            message=log.message,
            is_error=log.is_error,
            created_at=log.created_at.isoformat(),
        )
