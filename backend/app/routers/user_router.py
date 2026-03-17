"""User management router – Role-based access control."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.rbac import require_admin, require_manager, require_any
from app.core.security import get_db
from app.models.user import User
from app.schemas.user_schema import UserResponse, UserCreateWithRole, UserAdminUpdate, UserUpdate, RoleAssign, RoleResponse
from app.services.user_service import UserService
from app.utils.pagination import PaginationParams
from app.utils.responses import success_response

router = APIRouter()


@router.post(
    "/",
    summary="Create user (Manager+)",
    description="Create a new user and assign a role. Requires Manager or Admin role.",
    response_description="Created user",
)
def create_user(
    body: UserCreateWithRole,
    db: Session = Depends(get_db),
    _current: User = Depends(require_manager),
):
    user = UserService.create_user(db, body)
    return success_response(
        data=UserResponse.model_validate(user).model_dump(),
        message="User created",
    )


@router.get(
    "/",
    summary="List all users (All roles)",
    description="Paginated list of all users. Accessible to all authenticated users. Read-only users can only view.",
    response_description="Paginated array of users",
)
def list_users(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    _current: User = Depends(require_any),
):
    result = UserService.list_users(db, PaginationParams(page=page, limit=limit))
    return success_response(
        data=[UserResponse.model_validate(u).model_dump() for u in result.items],
        meta={"total": result.total, "page": result.page, "limit": result.page_size, "total_pages": result.total_pages},
    )


@router.get(
    "/{user_id}",
    summary="Get user by ID (All roles)",
    description="Retrieve a single user by UUID. Accessible to all authenticated users.",
    response_description="User details",
)
def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    _current: User = Depends(require_any),
):
    user = UserService.get_user(db, user_id)
    return success_response(data=UserResponse.model_validate(user).model_dump())


@router.patch(
    "/{user_id}",
    summary="Update user details and roles (Manager+)",
    description="Update user profile fields and replace assigned roles. Requires Manager or Admin role.",
    response_description="Updated user",
)
def update_user_admin(
    user_id: UUID,
    body: UserAdminUpdate,
    db: Session = Depends(get_db),
    _current: User = Depends(require_manager),
):
    user = UserService.admin_update_user(db, user_id, body)
    return success_response(
        data=UserResponse.model_validate(user).model_dump(),
        message="User updated",
    )


@router.delete(
    "/{user_id}",
    summary="Delete user (Admin)",
    description="Delete a user by UUID. Admin only. Cannot delete own account.",
)
def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current: User = Depends(require_admin),
):
    if user_id == current.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    UserService.delete_user(db, user_id)
    return success_response(message="User deleted")


@router.patch(
    "/{user_id}/role",
    summary="Assign role to user (Admin)",
    description="Add a role to a user. Admin only.",
    response_description="Updated user with new role",
)
def assign_role(
    user_id: UUID,
    body: RoleAssign,
    db: Session = Depends(get_db),
    _current: User = Depends(require_admin),
):
    user = UserService.assign_role(db, user_id, body.role_id)
    return success_response(
        data=UserResponse.model_validate(user).model_dump(),
        message="Role assigned",
    )


@router.delete(
    "/{user_id}/role/{role_id}",
    summary="Remove role from user (Admin)",
    description="Remove a specific role assigned to a user. Admin only.",
    response_description="Updated user",
)
def remove_role(
    user_id: UUID,
    role_id: UUID,
    db: Session = Depends(get_db),
    _current: User = Depends(require_admin),
):
    user = UserService.remove_role(db, user_id, role_id)
    return success_response(
        data=UserResponse.model_validate(user).model_dump(),
        message="Role removed",
    )


@router.get(
    "/roles/all",
    summary="List all roles (All roles)",
    description="Retrieve the list of available roles. Accessible to all authenticated users.",
    response_description="Array of roles",
)
def list_roles(
    db: Session = Depends(get_db),
    _current: User = Depends(require_any),
):
    roles = UserService.list_roles(db)
    return success_response(
        data=[RoleResponse.model_validate(r).model_dump() for r in roles],
    )
