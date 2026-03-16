"""Task management router."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.rbac import require_admin, require_manager, require_any
from app.core.security import get_db, get_current_user
from app.models.user import User
from app.schemas.task_schema import (
    TaskCreate, TaskUpdate, TaskResponse,
    TaskStatusUpdate, TaskAssign,
)
from app.schemas.comment_schema import CommentCreate, CommentResponse
from app.schemas.activity_log_schema import ActivityLogResponse
from app.services.task_service import TaskService
from app.services.comment_service import CommentService
from app.services.activity_log_service import ActivityLogService
from app.utils.pagination import PaginationParams
from app.utils.responses import success_response

router = APIRouter()


def _is_plain_user(user: User) -> bool:
    role_names = {role.name for role in user.roles}
    return "Read Only User" in role_names and "Manager" not in role_names and "Admin" not in role_names


# ── List & CRUD ───────────────────────────────────────────────────────────


@router.get(
    "/",
    summary="List tasks (all roles)",
    description="Paginated task listing with optional filtering by project, status, assignee, and free-text search. Supports sorting by created_at, due_date, or status.",
    response_description="Paginated array of tasks inside the standard envelope",
)
def list_tasks(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    project_id: Optional[UUID] = Query(None, description="Filter by project UUID"),
    status: Optional[str] = Query(None, description="Filter by status (new, in_progress, completed, …)"),
    assigned_to: Optional[UUID] = Query(None, description="Filter by assignee UUID"),
    search: Optional[str] = Query(None, description="Free-text search on task title"),
    sort_by: Optional[str] = Query(None, description="Sort field: created_at | due_date | status"),
    sort_order: Optional[str] = Query("desc", description="Sort direction: asc | desc"),
    db: Session = Depends(get_db),
    current: User = Depends(require_any),
):
    user_role_names = {role.name for role in current.roles}
    # Users only see tasks assigned to them
    if "Read Only User" in user_role_names and "Manager" not in user_role_names and "Admin" not in user_role_names:
        assigned_to = current.id

    result = TaskService.list_tasks(
        db, PaginationParams(page=page, limit=limit),
        project_id=project_id, status=status, assigned_to=assigned_to,
        search=search, sort_by=sort_by, sort_order=sort_order or "desc",
    )
    return success_response(
        data=[TaskResponse.model_validate(t).model_dump() for t in result.items],
        meta={"total": result.total, "page": result.page, "limit": result.page_size, "total_pages": result.total_pages},
    )


@router.post(
    "/",
    summary="Create task",
    description="Create a new task within a project. Requires Manager or Admin role.",
    response_description="The newly created task",
)
def create_task(
    body: TaskCreate,
    db: Session = Depends(get_db),
    current: User = Depends(require_manager),
):
    task = TaskService.create_task(db, body, owner=current)
    return success_response(
        data=TaskResponse.model_validate(task).model_dump(),
        message="Task created",
    )


@router.get(
    "/{task_id}",
    summary="Get task",
    description="Retrieve a single task by UUID.",
    response_description="Task details",
)
def get_task(
    task_id: UUID,
    db: Session = Depends(get_db),
    current: User = Depends(require_any),
):
    task = TaskService.get_task(db, task_id)
    if _is_plain_user(current) and task.assigned_to != current.id:
        raise HTTPException(status_code=403, detail="You can only view tasks assigned to you")
    return success_response(data=TaskResponse.model_validate(task).model_dump())


@router.put(
    "/{task_id}",
    summary="Update task",
    description="Full update of a task. Admin, task owner, or assigned user may update.",
    response_description="Updated task",
)
def update_task(
    task_id: UUID,
    body: TaskUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    task = TaskService.update_task(db, task_id, body, current)
    return success_response(
        data=TaskResponse.model_validate(task).model_dump(),
        message="Task updated",
    )


@router.delete(
    "/{task_id}",
    summary="Delete task",
    description="Permanently remove a task. Requires Admin role.",
)
def delete_task(
    task_id: UUID,
    db: Session = Depends(get_db),
    _current: User = Depends(require_admin),
):
    TaskService.delete_task(db, task_id)
    return success_response(message="Task deleted")


# ── Dedicated PATCH endpoints ─────────────────────────────────────────────


@router.patch(
    "/{task_id}/status",
    summary="Update task status",
    description="Change a task's status. Read-only users may only mark their assigned tasks as completed.",
    response_description="Task with updated status",
)
def update_task_status(
    task_id: UUID,
    body: TaskStatusUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    task = TaskService.update_status(db, task_id, body.status, current)
    return success_response(
        data=TaskResponse.model_validate(task).model_dump(),
        message="Status updated",
    )


@router.patch(
    "/{task_id}/assign",
    summary="Assign task",
    description="Assign a task to a user by UUID. Requires Manager or Admin role.",
    response_description="Task with updated assignee",
)
def assign_task(
    task_id: UUID,
    body: TaskAssign,
    db: Session = Depends(get_db),
    current: User = Depends(require_manager),
):
    task = TaskService.assign_task(db, task_id, body.assigned_to, current)
    return success_response(
        data=TaskResponse.model_validate(task).model_dump(),
        message="Task assigned",
    )


# ── Comments ──────────────────────────────────────────────────────────────


@router.post(
    "/{task_id}/comments",
    summary="Add comment to task",
    description="Post a comment on a task. Any authenticated user may comment.",
    response_description="The created comment",
)
def add_comment(
    task_id: UUID,
    body: CommentCreate,
    db: Session = Depends(get_db),
    current: User = Depends(require_any),
):
    comment = CommentService.add_comment(db, task_id, body.content, author=current)
    return success_response(
        data=CommentResponse.model_validate(comment).model_dump(),
        message="Comment added",
    )


@router.get(
    "/{task_id}/comments",
    summary="List task comments",
    description="Retrieve all comments for a task, ordered by creation time.",
    response_description="Array of comments",
)
def list_comments(
    task_id: UUID,
    db: Session = Depends(get_db),
    current: User = Depends(require_any),
):
    task = TaskService.get_task(db, task_id)
    if _is_plain_user(current) and task.assigned_to != current.id:
        raise HTTPException(status_code=403, detail="You can only view comments for your assigned tasks")
    comments = CommentService.list_comments(db, task_id)
    return success_response(
        data=[CommentResponse.model_validate(c).model_dump() for c in comments],
    )


# ── Activity Log ──────────────────────────────────────────────────────────


@router.get(
    "/{task_id}/activity",
    summary="Task activity log",
    description="Retrieve the audit trail for a task, ordered newest first.",
    response_description="Array of activity log entries",
)
def get_activity(
    task_id: UUID,
    db: Session = Depends(get_db),
    current: User = Depends(require_any),
):
    task = TaskService.get_task(db, task_id)
    if _is_plain_user(current) and task.assigned_to != current.id:
        raise HTTPException(status_code=403, detail="You can only view activity for your assigned tasks")
    logs = ActivityLogService.get_activity(db, task_id)
    return success_response(
        data=[ActivityLogResponse.model_validate(a).model_dump() for a in logs],
    )
