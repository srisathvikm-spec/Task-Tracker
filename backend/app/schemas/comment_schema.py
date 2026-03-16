"""Pydantic schemas for Comment entities."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class CommentCreate(BaseModel):
    """Body for POST /tasks/{task_id}/comments."""
    content: str = Field(..., min_length=1, max_length=5000, description="Comment text")


class CommentResponse(BaseModel):
    """Returned when reading a comment."""
    id: UUID
    task_id: UUID
    author_id: Optional[UUID] = None
    content: str
    created_at: datetime

    class Config:
        from_attributes = True
