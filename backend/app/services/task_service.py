"""Service layer – TaskService.

Business logic with **granular RBAC enforcement** for task operations.
"""

from __future__ import annotations

import logging
from typing import Optional, Set
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.task import Task, TaskStatus
from app.models.user import User
from app.repositories.task_repository import TaskRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.user_repository import UserRepository
from app.repositories.activity_log_repository import ActivityLogRepository
from app.schemas.task_schema import TaskCreate, TaskUpdate
from app.utils.pagination import PaginationParams, PaginatedResult, paginate

logger = logging.getLogger(__name__)


def _role_names(user: User) -> Set[str]:
    return {r.name for r in user.roles}


class TaskService:
    """Business logic for tasks with granular RBAC."""

    # ── Queries ────────────────────────────────────────────────────────────

    @staticmethod
    def get_task(db: Session, task_id: UUID) -> Task:
        task = TaskRepository.get_by_id(db, task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task

    @staticmethod
    def list_tasks(
        db: Session,
        params: PaginationParams,
        *,
        project_id: Optional[UUID] = None,
        status: Optional[str] = None,
        assigned_to: Optional[UUID] = None,
        search: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
    ) -> PaginatedResult:
        query = TaskRepository.query_all(db, sort_by=sort_by, sort_order=sort_order)
        if project_id:
            query = query.filter(Task.project_id == project_id)
        if status:
            query = query.filter(Task.status == status)
        if assigned_to:
            query = query.filter(Task.assigned_to == assigned_to)
        if search:
            query = query.filter(Task.title.ilike(f"%{search}%"))
        return paginate(query, params)

    # ── Mutations ──────────────────────────────────────────────────────────

    @staticmethod
    def create_task(db: Session, data: TaskCreate, owner: User) -> Task:
        project = ProjectRepository.get_by_id(db, data.project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        logger.info("Creating task '%s' in project %s", data.title, data.project_id)
        task = TaskRepository.create(
            db,
            title=data.title,
            description=data.description,
            due_date=data.due_date,
            project_id=data.project_id,
            owner_id=owner.id,
            assigned_to=data.assigned_to,
        )
        ActivityLogRepository.create(
            db, task_id=task.id, user_id=owner.id,
            action="task_created", details=f"Task '{data.title}' created",
        )
        return task

    @staticmethod
    def update_task(db: Session, task_id: UUID, data: TaskUpdate, current_user: User) -> Task:
        """Full update – Admin / Manager / owner / assignee can update.

        Read-only users can only set status -> completed on their assigned tasks.
        """
        task = TaskService.get_task(db, task_id)
        roles = _role_names(current_user)
        is_privileged = bool(roles & {"Admin", "Manager"})
        is_owner = task.owner_id == current_user.id
        is_assignee = task.assigned_to == current_user.id

        if not is_privileged and not is_owner and not is_assignee:
            raise HTTPException(status_code=403, detail="Only admin, task owner, or assigned user can update this task")

        if not is_privileged and not is_owner:
            # Assignee with Read Only User role
            changes = data.model_dump(exclude_unset=True)
            if set(changes.keys()) != {"status"} or changes.get("status") != TaskStatus.COMPLETED:
                raise HTTPException(status_code=403, detail="Read-only users can only mark tasks as completed")

        update_data = data.model_dump(exclude_unset=True)
        logger.info("Updating task %s by user %s", task_id, current_user.id)
        updated = TaskRepository.update(db, task, **update_data)
        ActivityLogRepository.create(
            db, task_id=task_id, user_id=current_user.id,
            action="task_updated", details=str(update_data),
        )
        return updated

    @staticmethod
    def update_status(db: Session, task_id: UUID, new_status: TaskStatus, current_user: User) -> Task:
        """PATCH /tasks/{id}/status – dedicated status-update endpoint."""
        task = TaskService.get_task(db, task_id)
        roles = _role_names(current_user)
        old_status = task.status

        if not (roles & {"Admin", "Manager"}):
            if task.assigned_to != current_user.id:
                raise HTTPException(status_code=403, detail="You can only update tasks assigned to you")
            if new_status != TaskStatus.COMPLETED:
                raise HTTPException(status_code=403, detail="Read-only users can only mark tasks as completed")

        task.status = new_status
        db.commit()
        db.refresh(task)
        logger.info("Task %s status %s → %s by user %s", task_id, old_status, new_status, current_user.id)
        ActivityLogRepository.create(
            db, task_id=task_id, user_id=current_user.id,
            action="status_changed", details=f"{old_status} → {new_status.value}",
        )
        return task

    @staticmethod
    def assign_task(db: Session, task_id: UUID, assignee_id: UUID, current_user: User) -> Task:
        """PATCH /tasks/{id}/assign – assign a task to a user."""
        task = TaskService.get_task(db, task_id)
        assignee = UserRepository.get_by_id(db, assignee_id)
        if not assignee:
            raise HTTPException(status_code=404, detail="Assignee not found")
        task.assigned_to = assignee_id
        db.commit()
        db.refresh(task)
        logger.info("Task %s assigned to %s by %s", task_id, assignee_id, current_user.id)
        ActivityLogRepository.create(
            db, task_id=task_id, user_id=current_user.id,
            action="task_assigned", details=f"Assigned to {assignee.email}",
        )
        return task

    @staticmethod
    def delete_task(db: Session, task_id: UUID) -> None:
        task = TaskService.get_task(db, task_id)
        logger.info("Deleting task %s", task_id)
        TaskRepository.delete(db, task)
