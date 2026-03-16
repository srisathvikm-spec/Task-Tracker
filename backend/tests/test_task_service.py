"""Tests for TaskService – including RBAC enforcement."""

import uuid
import pytest
from app.services.task_service import TaskService
from app.models.task import Task, TaskStatus
from app.schemas.task_schema import TaskCreate, TaskUpdate
from app.utils.pagination import PaginationParams
from fastapi import HTTPException


class TestTaskService:

    def test_create_task(self, db, sample_project, admin_user):
        data = TaskCreate(title="New", project_id=sample_project.id)
        task = TaskService.create_task(db, data, owner=admin_user)
        assert task.title == "New"
        assert task.status == TaskStatus.NEW

    def test_create_task_invalid_project(self, db, admin_user):
        with pytest.raises(HTTPException):
            TaskService.create_task(db, TaskCreate(title="X", project_id=uuid.uuid4()), owner=admin_user)

    def test_list_tasks_filter_status(self, db, sample_task):
        result = TaskService.list_tasks(db, PaginationParams(), status="new")
        assert result.total == 1

    def test_list_tasks_search(self, db, sample_task):
        result = TaskService.list_tasks(db, PaginationParams(), search="Test")
        assert result.total == 1

    # ── RBAC ──────────────────────────────────────────────────────────

    def test_admin_can_update_any_field(self, db, sample_task, admin_user):
        updated = TaskService.update_task(db, sample_task.id, TaskUpdate(title="Changed"), admin_user)
        assert updated.title == "Changed"

    def test_readonly_can_complete_assigned(self, db, sample_task, readonly_user):
        result = TaskService.update_status(db, sample_task.id, TaskStatus.COMPLETED, readonly_user)
        assert result.status == TaskStatus.COMPLETED

    def test_readonly_cannot_change_other_status(self, db, sample_task, readonly_user):
        with pytest.raises(HTTPException) as exc:
            TaskService.update_status(db, sample_task.id, TaskStatus.IN_PROGRESS, readonly_user)
        assert exc.value.status_code == 403

    def test_readonly_cannot_update_unassigned_task(self, db, sample_project, admin_user, readonly_user):
        t = Task(title="Other", status="new", project_id=sample_project.id,
                 owner_id=admin_user.id, assigned_to=admin_user.id)
        db.add(t); db.commit(); db.refresh(t)
        with pytest.raises(HTTPException) as exc:
            TaskService.update_status(db, t.id, TaskStatus.COMPLETED, readonly_user)
        assert exc.value.status_code == 403

    def test_assign_task(self, db, sample_task, admin_user, creator_user):
        updated = TaskService.assign_task(db, sample_task.id, creator_user.id, admin_user)
        assert updated.assigned_to == creator_user.id

    def test_delete_task(self, db, sample_task):
        TaskService.delete_task(db, sample_task.id)
        with pytest.raises(HTTPException):
            TaskService.get_task(db, sample_task.id)
