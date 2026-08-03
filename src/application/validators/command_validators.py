"""Command input parameter validation routines."""

import uuid

from src.application.commands.evidence_commands import AddEvidenceCommand, VerifyEvidenceCommand
from src.application.commands.project_commands import (
    ApproveWorkflowCommand,
    CreateProjectCommand,
    CreateWorkflowCommand,
    ExecuteWorkflowCommand,
)
from src.application.exceptions.application_exceptions import ValidationFailed


class CommandValidator:
    """Validator routines enforcing syntactic and format invariants on application commands."""

    @staticmethod
    def validate_create_project(cmd: CreateProjectCommand) -> None:
        """Validate CreateProjectCommand parameters."""
        if not cmd.title or not cmd.title.strip():
            raise ValidationFailed("Project title cannot be empty.")
        if not cmd.question_text or len(cmd.question_text.strip()) < 10:
            raise ValidationFailed("Research question text must be at least 10 characters.")
        if not cmd.region_name or not cmd.region_name.strip():
            raise ValidationFailed("Region name cannot be empty.")

        try:
            uuid.UUID(cmd.user_id)
        except ValueError as err:
            raise ValidationFailed(f"Invalid user_id UUID: {cmd.user_id}") from err

        if not (-90.0 <= cmd.south_west_lat <= 90.0) or not (-90.0 <= cmd.north_east_lat <= 90.0):
            raise ValidationFailed("Latitude must be between -90 and 90 degrees.")
        if cmd.south_west_lat >= cmd.north_east_lat:
            raise ValidationFailed("south_west_lat must be strictly less than north_east_lat.")

    @staticmethod
    def validate_create_workflow(cmd: CreateWorkflowCommand) -> None:
        """Validate CreateWorkflowCommand parameters."""
        try:
            uuid.UUID(cmd.project_id)
        except ValueError as err:
            raise ValidationFailed(f"Invalid project_id UUID: {cmd.project_id}") from err

    @staticmethod
    def validate_approve_workflow(cmd: ApproveWorkflowCommand) -> None:
        """Validate ApproveWorkflowCommand parameters."""
        try:
            uuid.UUID(cmd.workflow_id)
            uuid.UUID(cmd.approver_user_id)
        except ValueError as err:
            raise ValidationFailed(f"Invalid UUID string format in command: {err}") from err

    @staticmethod
    def validate_execute_workflow(cmd: ExecuteWorkflowCommand) -> None:
        """Validate ExecuteWorkflowCommand parameters."""
        try:
            uuid.UUID(cmd.workflow_id)
        except ValueError as err:
            raise ValidationFailed(f"Invalid workflow_id UUID: {cmd.workflow_id}") from err

    @staticmethod
    def validate_add_evidence(cmd: AddEvidenceCommand) -> None:
        """Validate AddEvidenceCommand parameters."""
        try:
            uuid.UUID(cmd.workflow_id)
        except ValueError as err:
            raise ValidationFailed(f"Invalid workflow_id UUID: {cmd.workflow_id}") from err

        if not cmd.source_citation or not cmd.source_citation.strip():
            raise ValidationFailed("Source citation cannot be empty.")
        if not (0.0 <= cmd.confidence_score <= 1.0):
            raise ValidationFailed("Confidence score must be between 0.0 and 1.0.")

    @staticmethod
    def validate_verify_evidence(cmd: VerifyEvidenceCommand) -> None:
        """Validate VerifyEvidenceCommand parameters."""
        try:
            uuid.UUID(cmd.workflow_id)
            uuid.UUID(cmd.evidence_id)
        except ValueError as err:
            raise ValidationFailed(f"Invalid UUID in verify command: {err}") from err

        if not (0.0 <= cmd.confidence_score <= 1.0):
            raise ValidationFailed("Confidence score must be between 0.0 and 1.0.")
