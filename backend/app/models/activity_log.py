"""ActivityLog ORM model."""

from sqlalchemy import Column, String, Text, ForeignKey, DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database.base import Base, UUIDMixin


class ActivityLog(Base, UUIDMixin):
    """Audit trail entry for task-level actions."""

    __tablename__ = "activity_logs"

    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(50), nullable=False)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=text("now()"), nullable=False)

    # Relationships
    task = relationship("Task", backref="activity_logs")
    user = relationship("User")
