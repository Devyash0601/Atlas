"""ResearchProject Aggregate Root entity."""

import uuid
from datetime import datetime
from typing import Any, ClassVar

from src.domain.base.aggregate_root import AggregateRoot
from src.domain.enums.project_status import ProjectStatus
from src.domain.events.project_events import ProjectCreated
from src.domain.exceptions.domain_exceptions import StateTransitionError, ValidationError
from src.domain.value_objects.region_of_interest import RegionOfInterest
from src.domain.value_objects.research_question import ResearchQuestion


class ResearchProject(AggregateRoot):
    """ResearchProject Aggregate Root managing workflow states and project level invariants."""

    ALLOWED_TRANSITIONS: ClassVar[dict[ProjectStatus, set[ProjectStatus]]] = {
        ProjectStatus.CREATED: {ProjectStatus.PLANNED, ProjectStatus.FAILED},
        ProjectStatus.PLANNED: {ProjectStatus.RUNNING, ProjectStatus.FAILED},
        ProjectStatus.RUNNING: {ProjectStatus.COMPLETED, ProjectStatus.FAILED},
        ProjectStatus.COMPLETED: set(),
        ProjectStatus.FAILED: set(),
    }

    def __init__(
        self,
        title: str,
        question: ResearchQuestion,
        roi: RegionOfInterest,
        user_id: uuid.UUID,
        status: ProjectStatus = ProjectStatus.CREATED,
        entity_id: uuid.UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        """Initialize ResearchProject aggregate root."""
        super().__init__(entity_id=entity_id, created_at=created_at, updated_at=updated_at)
        if not title or not title.strip():
            raise ValidationError("Project title cannot be empty")

        self._title = title.strip()
        self._question = question
        self._roi = roi
        self._user_id = user_id
        self._status = status

        if entity_id is None:
            self.add_event(ProjectCreated(project_id=self.id, title=self._title))

    @property
    def title(self) -> str:
        """Return project title."""
        return self._title

    @property
    def question(self) -> ResearchQuestion:
        """Return research question."""
        return self._question

    @property
    def roi(self) -> RegionOfInterest:
        """Return region of interest."""
        return self._roi

    @property
    def user_id(self) -> uuid.UUID:
        """Return owner user UUID."""
        return self._user_id

    @property
    def status(self) -> ProjectStatus:
        """Return current project status."""
        return self._status

    def transition_to(self, new_status: ProjectStatus) -> None:
        """Transition project status adhering strictly to allowed state machine rules."""
        allowed = self.ALLOWED_TRANSITIONS.get(self._status, set())
        if new_status not in allowed:
            raise StateTransitionError(
                f"Cannot transition project status from '{self._status}' to '{new_status}'"
            )
        self._status = new_status
        self.touch()

    def to_dict(self) -> dict[str, Any]:
        """Serialize project state to dictionary representation."""
        return {
            "id": str(self.id),
            "title": self._title,
            "question": self._question.text,
            "region": self._roi.name,
            "user_id": str(self._user_id),
            "status": self._status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
