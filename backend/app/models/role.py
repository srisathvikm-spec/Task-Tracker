"""Role and UserRole ORM models."""

import uuid

from sqlalchemy import Column, String, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database.base import Base, UUIDMixin


# Association table
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("role_id", UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), nullable=False),
)


class Role(Base, UUIDMixin):
    """Application role (Admin, Manager, Read Only User)."""

    __tablename__ = "roles"

    name = Column(String(50), unique=True, index=True, nullable=False)

    # Relationships
    users = relationship("User", secondary=user_roles, back_populates="roles")
