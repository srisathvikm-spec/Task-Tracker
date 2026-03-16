"""Repository – Project database access."""

from __future__ import annotations

from typing import Any, Optional
from uuid import UUID

from sqlalchemy.orm import Session, Query

from app.models.project import Project


class ProjectRepository:
    """Database access layer for Project entities."""

    @staticmethod
    def get_by_id(db: Session, project_id: UUID) -> Optional[Project]:
        return db.query(Project).filter(Project.id == project_id).first()

    @staticmethod
    def query_all(db: Session) -> Query:
        """Return base query – caller can add filters / pagination."""
        return db.query(Project).order_by(Project.created_at.desc())

    @staticmethod
    def create(db: Session, *, name: str, description: Optional[str], start_date: Any, end_date: Any, owner_id: UUID) -> Project:
        project = Project(
            name=name,
            description=description,
            start_date=start_date,
            end_date=end_date,
            owner_id=owner_id,
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def update(db: Session, project: Project, **kwargs) -> Project:
        for key, val in kwargs.items():
            setattr(project, key, val)
        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def delete(db: Session, project: Project) -> None:
        db.delete(project)
        db.commit()
