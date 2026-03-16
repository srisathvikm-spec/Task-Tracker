"""Tests for ProjectService."""

import uuid
import pytest
from app.services.project_service import ProjectService
from app.schemas.project_schema import ProjectCreate, ProjectUpdate
from app.utils.pagination import PaginationParams
from fastapi import HTTPException


class TestProjectService:

    def test_create_project(self, db, admin_user):
        data = ProjectCreate(name="Alpha", description="first")
        proj = ProjectService.create_project(db, data, owner=admin_user)
        assert proj.name == "Alpha"
        assert proj.owner_id == admin_user.id

    def test_get_project_not_found(self, db):
        with pytest.raises(HTTPException):
            ProjectService.get_project(db, uuid.uuid4())

    def test_list_with_filter(self, db, admin_user):
        ProjectService.create_project(db, ProjectCreate(name="Beta App"), owner=admin_user)
        ProjectService.create_project(db, ProjectCreate(name="Gamma Server"), owner=admin_user)
        result = ProjectService.list_projects(db, PaginationParams(page=1, page_size=10), name_filter="Beta")
        assert result.total == 1

    def test_update_project(self, db, sample_project):
        updated = ProjectService.update_project(db, sample_project.id, ProjectUpdate(description="new desc"))
        assert updated.description == "new desc"

    def test_delete_project(self, db, sample_project):
        ProjectService.delete_project(db, sample_project.id)
        with pytest.raises(HTTPException):
            ProjectService.get_project(db, sample_project.id)
