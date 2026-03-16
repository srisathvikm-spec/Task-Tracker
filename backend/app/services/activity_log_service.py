"""Service layer – ActivityLogService."""

from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.activity_log import ActivityLog
from app.repositories.activity_log_repository import ActivityLogRepository
from app.repositories.task_repository import TaskRepository


class ActivityLogService:
    """Business logic for reading task activity logs."""

    @staticmethod
    def get_activity(db: Session, task_id: UUID) -> List[ActivityLog]:
        task = TaskRepository.get_by_id(db, task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return ActivityLogRepository.get_by_task(db, task_id)
