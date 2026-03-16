"""Comment ORM model."""

from sqlalchemy import Column, String, Text, ForeignKey, DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database.base import Base, UUIDMixin


class Comment(Base, UUIDMixin):
    """A comment on a task."""

    __tablename__ = "comments"

    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=text("now()"), nullable=False)

    # Relationships
    task = relationship("Task", backref="comments")
    author = relationship("User")
