"""Security dependencies – current-user resolution."""

from __future__ import annotations

import logging
from typing import Optional

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.azure_auth import validate_token
from app.database.session import get_db  # re-exported for backward compatibility
from app.models.user import User

logger = logging.getLogger(__name__)


def get_current_user(
    db: Session = Depends(get_db),
    payload: dict = Depends(validate_token),
) -> User:
    """Resolve the current user from the validated token.

    If the user does not exist yet, auto-provision them with Read Only User
    role (first SSO login).  An admin must explicitly elevate their role.
    """
    email: Optional[str] = (
        payload.get("preferred_username")
        or payload.get("email")
        or payload.get("upn")
    )
    if not email:
        raise HTTPException(status_code=400, detail="Token does not contain an email claim")

    user = db.query(User).filter(User.email == email).first()

    if not user:
        name = payload.get("name", email.split("@")[0])
        user = User(name=name, email=email)

        # New users receive the least-privileged role by default.
        # Admins can elevate via PATCH /users/{id}/role.
        from app.models.role import Role
        user_role = db.query(Role).filter(Role.name == "Read Only User").first()
        if user_role:
            user.roles.append(user_role)

        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info("Auto-provisioned user %s (%s)", user.name, user.email)

    if not user.is_active:
        raise HTTPException(status_code=403, detail="User account is disabled")

    return user
