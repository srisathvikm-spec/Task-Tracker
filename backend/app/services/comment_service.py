"""Service layer – CommentService."""

from __future__ import annotations

import logging
from typing import List
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.comment import Comment
from app.models.user import User
from app.repositories.comment_repository import CommentRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.activity_log_repository import ActivityLogRepository

logger = logging.getLogger(__name__)


class CommentService:
    """Business logic for task comments."""

    @staticmethod
    def add_comment(db: Session, task_id: UUID, content: str, author: User) -> Comment:
        task = TaskRepository.get_by_id(db, task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        comment = CommentRepository.create(db, task_id=task_id, author_id=author.id, content=content)
        ActivityLogRepository.create(db, task_id=task_id, user_id=author.id, action="comment_added", details=content[:200])
        logger.info("Comment added to task %s by user %s", task_id, author.id)
        return comment

    @staticmethod
    def list_comments(db: Session, task_id: UUID) -> List[Comment]:
        task = TaskRepository.get_by_id(db, task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return CommentRepository.get_by_task(db, task_id)
