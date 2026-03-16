"""Application settings driven by environment variables / .env file."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralised configuration for the Task Tracker API."""

    PROJECT_NAME: str = "Task Tracker API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    DATABASE_URL: str = "postgresql://postgres:9411@localhost:5432/task_tracker"

    AZURE_CLIENT_ID: str = ""
    AZURE_TENANT_ID: str = ""

    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000,https://task-tracker-dusky-two.vercel.app,https://task-tracker-hiuy.vercel.app"
    ALLOWED_ORIGIN_REGEX: str = "^https://.*\\.vercel\\.app$"
    AUTO_CREATE_TABLES: bool = False

    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")


settings = Settings()
