"""Repository – Comment database access."""

from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.comment import Comment


class CommentRepository:
    """Database access layer for Comment entities."""

    @staticmethod
    def get_by_task(db: Session, task_id: UUID) -> List[Comment]:
        return (
            db.query(Comment)
            .filter(Comment.task_id == task_id)
            .order_by(Comment.created_at.asc())
            .all()
        )

    @staticmethod
    def create(db: Session, *, task_id: UUID, author_id: UUID, content: str) -> Comment:
        comment = Comment(task_id=task_id, author_id=author_id, content=content)
        db.add(comment)
        db.commit()
        db.refresh(comment)
        return comment
