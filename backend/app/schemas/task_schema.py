"""Pydantic schemas for Task entities."""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from app.models.task import TaskStatus
from app.schemas.user_schema import UserSummary


class _DueDateMixin(BaseModel):
    """Shared validator: due_date must not be in the past."""

    @model_validator(mode="after")
    def _due_date_not_in_past(self):
        if hasattr(self, "due_date") and self.due_date is not None and self.due_date < date.today():
            raise ValueError("due_date cannot be in the past")
        return self


class TaskCreate(_DueDateMixin):
    """Body for POST /tasks."""
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=2000, description="Task description")
    due_date: Optional[date] = Field(None, description="Due date (cannot be in the past)")
    project_id: UUID = Field(..., description="UUID of the parent project")


class TaskUpdate(_DueDateMixin):
    """Body for PUT /tasks/{task_id}."""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=2000, description="Task description")
    due_date: Optional[date] = Field(None, description="Due date (cannot be in the past)")
    status: Optional[TaskStatus] = Field(None, description="New task status")
    assigned_to: Optional[UUID] = Field(None, description="UUID of the assignee")


class TaskStatusUpdate(BaseModel):
    """Body for PATCH /tasks/{id}/status."""
    status: TaskStatus


class TaskAssign(BaseModel):
    """Body for PATCH /tasks/{id}/assign."""
    assigned_to: UUID


class TaskResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    status: TaskStatus
    due_date: Optional[date] = None
    owner_id: Optional[UUID] = None
    project_id: UUID
    assigned_to: Optional[UserSummary] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
