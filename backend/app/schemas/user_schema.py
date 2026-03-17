"""Pydantic schemas for User and Role entities."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# ── Role ───────────────────────────────────────────────────────────────────


class RoleResponse(BaseModel):
    id: UUID
    name: str

    class Config:
        from_attributes = True


class RoleAssign(BaseModel):
    """Body for PATCH /users/{id}/role."""
    role_id: UUID


# ── User ───────────────────────────────────────────────────────────────────


class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    email: EmailStr


class UserCreateWithRole(UserCreate):
    role_id: UUID


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    is_active: Optional[bool] = None


class UserAdminUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    role_ids: Optional[List[UUID]] = None


class UserSummary(BaseModel):
    """Minimal user info for embedding in other responses."""
    id: UUID
    name: str
    email: str

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: UUID
    name: str
    email: str
    is_active: bool
    created_at: datetime
    roles: List[RoleResponse] = []

    class Config:
        from_attributes = True
