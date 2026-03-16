"""Project management router."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.rbac import require_manager, require_admin, require_any
from app.core.security import get_db
from app.models.user import User
from app.schemas.project_schema import ProjectCreate, ProjectUpdate, ProjectResponse
from app.schemas.task_schema import TaskResponse
from app.services.project_service import ProjectService
from app.services.task_service import TaskService
from app.utils.pagination import PaginationParams
from app.utils.responses import success_response

router = APIRouter()


@router.get(
    "/",
    summary="List projects (all roles)",
    description="Paginated project listing with optional filtering by name or owner UUID.",
    response_description="Paginated array of projects",
)
def list_projects(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    name: Optional[str] = Query(None, description="Filter by project name (partial match)"),
    owner_id: Optional[UUID] = Query(None, description="Filter by owner UUID"),
    db: Session = Depends(get_db),
    _current: User = Depends(require_any),
):
    result = ProjectService.list_projects(
        db, PaginationParams(page=page, limit=limit),
        name_filter=name, owner_id=owner_id,
    )
    return success_response(
        data=[ProjectResponse.model_validate(p).model_dump() for p in result.items],
        meta={"total": result.total, "page": result.page, "limit": result.page_size, "total_pages": result.total_pages},
    )


@router.post(
    "/",
    summary="Create project",
    description="Create a new project. Requires Manager or Admin role.",
    response_description="The newly created project",
)
def create_project(
    body: ProjectCreate,
    db: Session = Depends(get_db),
    current: User = Depends(require_manager),
):
    project = ProjectService.create_project(db, body, owner=current)
    return success_response(
        data=ProjectResponse.model_validate(project).model_dump(),
        message="Project created",
    )


@router.get(
    "/{project_id}",
    summary="Get project",
    description="Retrieve a single project by UUID.",
    response_description="Project details",
)
def get_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    _current: User = Depends(require_any),
):
    project = ProjectService.get_project(db, project_id)
    return success_response(data=ProjectResponse.model_validate(project).model_dump())


@router.put(
    "/{project_id}",
    summary="Update project",
    description="Update an existing project. Requires Manager or Admin role.",
    response_description="Updated project",
)
def update_project(
    project_id: UUID,
    body: ProjectUpdate,
    db: Session = Depends(get_db),
    _current: User = Depends(require_manager),
):
    project = ProjectService.update_project(db, project_id, body)
    return success_response(
        data=ProjectResponse.model_validate(project).model_dump(),
        message="Project updated",
    )


@router.delete(
    "/{project_id}",
    summary="Delete project",
    description="Permanently remove a project and all its tasks. Requires Admin role.",
)
def delete_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    _current: User = Depends(require_admin),
):
    ProjectService.delete_project(db, project_id)
    return success_response(message="Project deleted")


# ── Nested project-tasks endpoint ─────────────────────────────────────────


@router.get(
    "/{project_id}/tasks",
    summary="List tasks for a project",
    description="Returns all tasks belonging to a specific project, with pagination and sorting.",
    response_description="Paginated array of tasks",
)
def list_project_tasks(
    project_id: UUID,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: Optional[str] = Query(None, description="Sort field: created_at | due_date | status"),
    sort_order: Optional[str] = Query("desc", description="Sort direction: asc | desc"),
    db: Session = Depends(get_db),
    current: User = Depends(require_any),
):
    role_names = {role.name for role in current.roles}
    assigned_to = None
    if "Read Only User" in role_names and "Manager" not in role_names and "Admin" not in role_names:
        assigned_to = current.id

    # Verify project exists
    ProjectService.get_project(db, project_id)
    result = TaskService.list_tasks(
        db, PaginationParams(page=page, limit=limit),
        project_id=project_id, assigned_to=assigned_to, sort_by=sort_by, sort_order=sort_order or "desc",
    )
    return success_response(
        data=[TaskResponse.model_validate(t).model_dump() for t in result.items],
        meta={"total": result.total, "page": result.page, "limit": result.page_size, "total_pages": result.total_pages},
    )
