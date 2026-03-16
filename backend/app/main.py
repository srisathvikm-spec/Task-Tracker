"""FastAPI application entry point."""

import logging
import sys

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.config.settings import settings
from app.database.base import Base
from app.database.session import engine
from app.models import *  # noqa: F401, F403  – register all models
from app.routers import auth_router, user_router, project_router, task_router
from app.utils.responses import error_response

# ── Logging ────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)-30s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# ── App ────────────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Production-grade Task Tracker API with RBAC, pagination, filtering, sorting, comments, and activity logs.",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.on_event("startup")
def startup_initialize() -> None:
    """Optional local-only schema initialization.

    In cloud environments the DB may be provisioned independently.
    We avoid crashing the whole app if DB is temporarily unavailable.
    """
    if not settings.AUTO_CREATE_TABLES:
        logger.info("AUTO_CREATE_TABLES disabled; skipping schema creation")
        return
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database schema checked/created successfully")
    except Exception as exc:  # noqa: BLE001
        logger.exception("Schema auto-create failed at startup: %s", exc)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Error Handling Middleware ──────────────────────────────────────────────


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic / query-param validation errors → 422."""
    logger.warning("Validation error on %s %s: %s", request.method, request.url, exc.errors())
    return JSONResponse(
        status_code=422,
        content=error_response("Validation error", details=exc.errors()),
    )


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    """Handle database constraint violations → 409."""
    logger.error("DB integrity error on %s %s: %s", request.method, request.url, str(exc.orig))
    return JSONResponse(
        status_code=409,
        content=error_response("Database conflict", details=str(exc.orig)),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Catch-all for unexpected errors → 500."""
    logger.exception("Unhandled error on %s %s", request.method, request.url)
    return JSONResponse(status_code=500, content=error_response("Internal server error"))


# ── Routers ────────────────────────────────────────────────────────────────
prefix = settings.API_V1_STR
app.include_router(auth_router.router, prefix=f"{prefix}/auth", tags=["auth"])
app.include_router(user_router.router, prefix=f"{prefix}/users", tags=["users"])
app.include_router(project_router.router, prefix=f"{prefix}/projects", tags=["projects"])
app.include_router(task_router.router, prefix=f"{prefix}/tasks", tags=["tasks"])


@app.get("/health", tags=["health"], summary="Health Check", description="Returns OK if the API is running.")
def health_check():
    return {"status": "ok"}


logger.info("%s v%s started", settings.PROJECT_NAME, settings.VERSION)
