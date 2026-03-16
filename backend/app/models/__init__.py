"""Model registry – import every model so Alembic and create_all discover them."""

from app.models.user import User
from app.models.role import Role, user_roles
from app.models.project import Project
from app.models.task import Task
from app.models.comment import Comment
from app.models.activity_log import ActivityLog

__all__ = ["User", "Role", "user_roles", "Project", "Task", "Comment", "ActivityLog"]
