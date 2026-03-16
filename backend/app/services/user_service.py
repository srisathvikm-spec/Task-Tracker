"""Service layer – UserService.

Business logic and authorization for user / role operations.
"""

from __future__ import annotations

import logging
from typing import List
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.role import Role
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import UserCreateWithRole, UserAdminUpdate
from app.utils.pagination import PaginationParams, PaginatedResult, paginate

logger = logging.getLogger(__name__)

ALLOWED_ROLE_NAMES = {"Admin", "Manager", "Read Only User"}


class UserService:
    """Business logic for users and roles."""

    @staticmethod
    def get_user(db: Session, user_id: UUID) -> User:
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    @staticmethod
    def list_users(db: Session, params: PaginationParams) -> PaginatedResult:
        query = UserRepository.query_all(db)
        return paginate(query, params)

    @staticmethod
    def create_user(db: Session, data: UserCreateWithRole) -> User:
        existing = UserRepository.get_by_email(db, data.email)
        if existing:
            raise HTTPException(status_code=400, detail="Email already exists")

        role = UserRepository.get_role_by_id(db, data.role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        if role.name not in ALLOWED_ROLE_NAMES:
            raise HTTPException(status_code=400, detail="Role is not allowed")

        user = UserRepository.create(db, name=data.name, email=data.email)
        user = UserRepository.add_role(db, user, role)
        logger.info("Created user %s with role '%s'", user.email, role.name)
        return user

    @staticmethod
    def update_user(db: Session, user_id: UUID, **kwargs) -> User:
        user = UserService.get_user(db, user_id)
        logger.info("Updating user %s", user_id)
        return UserRepository.update(db, user, **kwargs)

    @staticmethod
    def assign_role(db: Session, user_id: UUID, role_id: UUID) -> User:
        user = UserService.get_user(db, user_id)
        role = UserRepository.get_role_by_id(db, role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        if role.name not in ALLOWED_ROLE_NAMES:
            raise HTTPException(status_code=400, detail="Role is not allowed")
        if role in user.roles:
            raise HTTPException(status_code=400, detail=f"User already has role '{role.name}'")
        logger.info("Assigning role '%s' to user %s", role.name, user_id)
        return UserRepository.add_role(db, user, role)

    @staticmethod
    def remove_role(db: Session, user_id: UUID, role_id: UUID) -> User:
        user = UserService.get_user(db, user_id)
        role = UserRepository.get_role_by_id(db, role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        if role not in user.roles:
            raise HTTPException(status_code=400, detail="User does not have this role")
        if len(user.roles) <= 1:
            raise HTTPException(status_code=400, detail="User must have at least one role")
        logger.info("Removing role '%s' from user %s", role.name, user_id)
        return UserRepository.remove_role(db, user, role)

    @staticmethod
    def admin_update_user(db: Session, user_id: UUID, data: UserAdminUpdate) -> User:
        user = UserService.get_user(db, user_id)
        update_data = data.model_dump(exclude_unset=True)

        if "email" in update_data and update_data["email"] != user.email:
            existing = UserRepository.get_by_email(db, update_data["email"])
            if existing and existing.id != user.id:
                raise HTTPException(status_code=400, detail="Email already exists")

        role_ids = update_data.pop("role_ids", None)
        if role_ids is not None:
            roles = UserRepository.get_roles_by_ids(db, role_ids)
            if len(roles) != len(set(role_ids)):
                raise HTTPException(status_code=404, detail="One or more roles not found")
            if not roles:
                raise HTTPException(status_code=400, detail="User must have at least one role")
            disallowed = [r.name for r in roles if r.name not in ALLOWED_ROLE_NAMES]
            if disallowed:
                raise HTTPException(status_code=400, detail="One or more roles are not allowed")
            user = UserRepository.set_roles(db, user, roles)

        if update_data:
            user = UserRepository.update(db, user, **update_data)

        logger.info("Admin updated user %s", user_id)
        return user

    @staticmethod
    def delete_user(db: Session, user_id: UUID) -> None:
        user = UserService.get_user(db, user_id)
        logger.info("Deleting user %s", user_id)
        UserRepository.delete(db, user)

    @staticmethod
    def list_roles(db: Session) -> List[Role]:
        return UserRepository.get_all_roles(db)
