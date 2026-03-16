"""Service layer – ProjectService.

Business logic for project CRUD operations.
"""

from __future__ import annotations

import logging
from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.user import User
from app.repositories.project_repository import ProjectRepository
from app.schemas.project_schema import ProjectCreate, ProjectUpdate
from app.utils.pagination import PaginationParams, PaginatedResult, paginate

logger = logging.getLogger(__name__)


class ProjectService:
    """Business logic for projects."""

    @staticmethod
    def get_project(db: Session, project_id: UUID) -> Project:
        project = ProjectRepository.get_by_id(db, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return project

    @staticmethod
    def list_projects(
        db: Session,
        params: PaginationParams,
        *,
        name_filter: Optional[str] = None,
        owner_id: Optional[UUID] = None,
    ) -> PaginatedResult:
        query = ProjectRepository.query_all(db)
        if name_filter:
            query = query.filter(Project.name.ilike(f"%{name_filter}%"))
        if owner_id:
            query = query.filter(Project.owner_id == owner_id)
        return paginate(query, params)

    @staticmethod
    def create_project(db: Session, data: ProjectCreate, owner: User) -> Project:
        logger.info("Creating project '%s' by user %s", data.name, owner.id)
        return ProjectRepository.create(
            db,
            name=data.name,
            description=data.description,
            start_date=data.start_date,
            end_date=data.end_date,
            owner_id=owner.id,
        )

    @staticmethod
    def update_project(db: Session, project_id: UUID, data: ProjectUpdate) -> Project:
        project = ProjectService.get_project(db, project_id)
        update_data = data.model_dump(exclude_unset=True)
        logger.info("Updating project %s", project_id)
        return ProjectRepository.update(db, project, **update_data)

    @staticmethod
    def delete_project(db: Session, project_id: UUID) -> None:
        project = ProjectService.get_project(db, project_id)
        logger.info("Deleting project %s", project_id)
        ProjectRepository.delete(db, project)
