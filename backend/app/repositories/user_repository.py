"""Repository – User & Role database access."""

from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.role import Role


class UserRepository:
    """Database access layer for User and Role entities."""

    # ── User queries ──────────────────────────────────────────────────────

    @staticmethod
    def get_by_id(db: Session, user_id: UUID) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def query_all(db: Session):
        """Return a Query object (for pagination)."""
        return db.query(User).order_by(User.created_at.desc())

    @staticmethod
    def create(db: Session, *, name: str, email: str) -> User:
        user = User(name=name, email=email)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update(db: Session, user: User, **kwargs) -> User:
        for key, val in kwargs.items():
            setattr(user, key, val)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def delete(db: Session, user: User) -> None:
        db.delete(user)
        db.commit()

    # ── Role queries ──────────────────────────────────────────────────────

    @staticmethod
    def get_role_by_id(db: Session, role_id: UUID) -> Optional[Role]:
        return db.query(Role).filter(Role.id == role_id).first()

    @staticmethod
    def get_role_by_name(db: Session, name: str) -> Optional[Role]:
        return db.query(Role).filter(Role.name == name).first()

    @staticmethod
    def get_all_roles(db: Session) -> List[Role]:
        return db.query(Role).all()

    @staticmethod
    def get_roles_by_ids(db: Session, role_ids: List[UUID]) -> List[Role]:
        if not role_ids:
            return []
        return db.query(Role).filter(Role.id.in_(role_ids)).all()

    @staticmethod
    def add_role(db: Session, user: User, role: Role) -> User:
        if role not in user.roles:
            user.roles.append(role)
            db.commit()
            db.refresh(user)
        return user

    @staticmethod
    def remove_role(db: Session, user: User, role: Role) -> User:
        if role in user.roles:
            user.roles.remove(role)
            db.commit()
            db.refresh(user)
        return user

    @staticmethod
    def set_roles(db: Session, user: User, roles: List[Role]) -> User:
        user.roles = roles
        db.commit()
        db.refresh(user)
        return user
