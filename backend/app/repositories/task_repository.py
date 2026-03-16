"""Repository – Task database access."""

from __future__ import annotations

from datetime import date
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session, Query

from app.models.task import Task


SORTABLE_FIELDS = {"created_at", "due_date", "status"}


class TaskRepository:
    """Database access layer for Task entities."""

    @staticmethod
    def get_by_id(db: Session, task_id: UUID) -> Optional[Task]:
        return db.query(Task).filter(Task.id == task_id).first()

    @staticmethod
    def query_all(
        db: Session,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
    ) -> Query:
        """Return base query with optional sorting.

        Args:
            sort_by: column name (created_at | due_date | status)
            sort_order: 'asc' or 'desc' (default: desc)
        """
        query = db.query(Task)
        if sort_by and sort_by in SORTABLE_FIELDS:
            col = getattr(Task, sort_by)
            query = query.order_by(col.asc() if sort_order == "asc" else col.desc())
        else:
            query = query.order_by(Task.created_at.desc())
        return query

    @staticmethod
    def create(db: Session, *, title: str, description: Optional[str], due_date: Optional[date], project_id: UUID, owner_id: UUID) -> Task:
        task = Task(
            title=title,
            description=description,
            due_date=due_date,
            project_id=project_id,
            owner_id=owner_id,
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def update(db: Session, task: Task, **kwargs) -> Task:
        for key, val in kwargs.items():
            setattr(task, key, val)
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def delete(db: Session, task: Task) -> None:
        db.delete(task)
        db.commit()
