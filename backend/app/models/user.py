"""User ORM model."""

from sqlalchemy import Column, String, Boolean, DateTime, text
from sqlalchemy.orm import relationship

from app.database.base import Base, UUIDMixin, TimestampMixin


class User(Base, UUIDMixin):
    """Represents a system user (provisioned on first SSO login)."""

    __tablename__ = "users"

    name = Column(String(150), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=text("now()"),
        nullable=False,
    )

    # Relationships
    roles = relationship("Role", secondary="user_roles", back_populates="users")
    owned_projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
    owned_tasks = relationship("Task", foreign_keys="Task.owner_id", back_populates="owner")
    assigned_tasks = relationship("Task", foreign_keys="Task.assigned_to", back_populates="assignee")
