"""Repository – ActivityLog database access."""

from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.activity_log import ActivityLog


class ActivityLogRepository:
    """Database access layer for ActivityLog entities."""

    @staticmethod
    def get_by_task(db: Session, task_id: UUID) -> List[ActivityLog]:
        return (
            db.query(ActivityLog)
            .filter(ActivityLog.task_id == task_id)
            .order_by(ActivityLog.created_at.desc())
            .all()
        )

    @staticmethod
    def create(db: Session, *, task_id: UUID, user_id: UUID, action: str, details: Optional[str] = None) -> ActivityLog:
        entry = ActivityLog(task_id=task_id, user_id=user_id, action=action, details=details)
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry

    @staticmethod
    def create_no_commit(db: Session, *, task_id: UUID, user_id: UUID, action: str, details: Optional[str] = None) -> ActivityLog:
        """Create an entry without committing – caller handles the commit."""
        entry = ActivityLog(task_id=task_id, user_id=user_id, action=action, details=details)
        db.add(entry)
        return entry
