"""SQLAlchemy engine and session factory."""

from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import sessionmaker

from app.config.settings import settings


def _build_connect_args() -> dict:
    """Build DB driver connection args with cloud-safe SSL handling."""
    url = make_url(settings.DATABASE_URL)
    if not (url.drivername.startswith("postgresql") and url.host):
        return {}

    # Supabase Postgres requires TLS.
    if settings.DATABASE_SSLMODE:
        return {"sslmode": settings.DATABASE_SSLMODE}
    if "supabase.co" in url.host and "sslmode=" not in settings.DATABASE_URL:
        return {"sslmode": "require"}
    return {}


engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    connect_args=_build_connect_args(),
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """FastAPI dependency that yields a DB session and closes it afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
