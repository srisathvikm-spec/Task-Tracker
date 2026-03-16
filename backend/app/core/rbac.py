"""Role-Based Access Control helpers."""

from __future__ import annotations

from typing import List

from fastapi import Depends, HTTPException, status

from app.core.security import get_current_user
from app.models.user import User


class RoleRequired:
    """FastAPI dependency that enforces one-of the specified roles.

    ``Admin`` always passes (full access).

    Usage::

        @router.get("/", dependencies=[Depends(RoleRequired(["Admin", "Manager"]))])
    """

    def __init__(self, allowed_roles: List[str]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_user)) -> User:
        user_role_names = {role.name for role in user.roles}
        if "Admin" in user_role_names:
            return user
        if user_role_names & set(self.allowed_roles):
            return user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )


# Pre-built shortcuts
require_admin = RoleRequired(["Admin"])
require_manager = RoleRequired(["Admin", "Manager"])
require_user = RoleRequired(["Admin", "Manager", "Read Only User"])
require_any = require_user
