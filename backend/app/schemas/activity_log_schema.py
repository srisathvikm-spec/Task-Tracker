"""Pydantic schemas for ActivityLog entities."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ActivityLogResponse(BaseModel):
    """Returned when reading an activity log entry."""
    id: UUID
    task_id: UUID
    user_id: Optional[UUID] = None
    action: str
    details: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
