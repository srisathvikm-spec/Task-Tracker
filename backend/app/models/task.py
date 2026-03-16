"""Task ORM model."""

from sqlalchemy import Column, String, Text, Date, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database.base import Base, UUIDMixin, TimestampMixin

import enum


class TaskStatus(str, enum.Enum):
    """Allowed task statuses."""
    NEW = "new"
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"


class Task(Base, UUIDMixin, TimestampMixin):
    """A task belonging to a project, optionally assigned to a user."""

    __tablename__ = "tasks"

    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(
        SAEnum(TaskStatus, name="task_status", values_callable=lambda e: [s.value for s in e]),
        default=TaskStatus.NEW,
        nullable=False,
    )
    due_date = Column(Date, nullable=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    owner = relationship("User", foreign_keys=[owner_id], back_populates="owned_tasks")
    assignee = relationship("User", foreign_keys=[assigned_to], back_populates="assigned_tasks")
    project = relationship("Project", back_populates="tasks")
