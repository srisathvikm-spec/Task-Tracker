"""Authentication router."""

import logging

from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.models.user import User
from app.schemas.user_schema import UserResponse
from app.utils.responses import success_response

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/me",
    summary="Current user info",
    description="Return the currently authenticated user. Auto-provisions on first SSO login.",
    response_description="Authenticated user details",
)
def auth_me(current_user: User = Depends(get_current_user)):
    """Return the currently authenticated user (auto-provisions on first call)."""
    logger.info("User login: %s (%s)", current_user.email, current_user.id)
    return success_response(data=UserResponse.model_validate(current_user).model_dump())
