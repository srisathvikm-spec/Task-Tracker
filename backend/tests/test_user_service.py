"""Tests for UserService."""

import pytest
from app.services.user_service import UserService
from app.utils.pagination import PaginationParams
from fastapi import HTTPException


class TestUserService:

    def test_get_user_found(self, db, admin_user):
        user = UserService.get_user(db, admin_user.id)
        assert user.email == "admin@test.com"

    def test_get_user_not_found(self, db):
        import uuid
        with pytest.raises(HTTPException) as exc:
            UserService.get_user(db, uuid.uuid4())
        assert exc.value.status_code == 404

    def test_list_users(self, db, admin_user, creator_user, readonly_user):
        result = UserService.list_users(db, PaginationParams(page=1, page_size=20))
        assert result.total == 3

    def test_assign_role(self, db, creator_user, admin_role):
        updated = UserService.assign_role(db, creator_user.id, admin_role.id)
        names = {r.name for r in updated.roles}
        assert "Admin" in names

    def test_assign_duplicate_role(self, db, admin_user, admin_role):
        with pytest.raises(HTTPException) as exc:
            UserService.assign_role(db, admin_user.id, admin_role.id)
        assert exc.value.status_code == 400
