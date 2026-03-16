"""Pytest conftest – shared fixtures for all backend tests.

Uses a **separate PostgreSQL test database** to match production behaviour.
Set TEST_DATABASE_URL env var or it defaults to task_tracker_test on localhost.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.models.user import User
from app.models.role import Role
from app.models.project import Project
from app.models.task import Task
from app.core.security import get_db
from app.main import app

from fastapi.testclient import TestClient

# PostgreSQL test database – override via TEST_DATABASE_URL env var
import os

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://postgres:9411@localhost:5432/task_tracker_test",
)

engine = create_engine(TEST_DATABASE_URL)
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function", autouse=True)
def db():
    """Create tables fresh for each test and teardown afterwards."""
    Base.metadata.create_all(bind=engine)
    session = TestSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db):
    """TestClient that overrides the DB dependency."""
    def _override():
        try:
            yield db
        finally:
            pass
    app.dependency_overrides[get_db] = _override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ── Convenience fixtures ──────────────────────────────────────────────────

@pytest.fixture
def admin_role(db):
    r = Role(name="Admin")
    db.add(r); db.commit(); db.refresh(r)
    return r

@pytest.fixture
def creator_role(db):
    r = Role(name="Manager")
    db.add(r); db.commit(); db.refresh(r)
    return r

@pytest.fixture
def readonly_role(db):
    r = Role(name="Read Only User")
    db.add(r); db.commit(); db.refresh(r)
    return r


@pytest.fixture
def admin_user(db, admin_role):
    u = User(name="Admin User", email="admin@test.com")
    u.roles.append(admin_role)
    db.add(u); db.commit(); db.refresh(u)
    return u


@pytest.fixture
def creator_user(db, creator_role):
    u = User(name="Creator User", email="creator@test.com")
    u.roles.append(creator_role)
    db.add(u); db.commit(); db.refresh(u)
    return u


@pytest.fixture
def readonly_user(db, readonly_role):
    u = User(name="Readonly User", email="readonly@test.com")
    u.roles.append(readonly_role)
    db.add(u); db.commit(); db.refresh(u)
    return u


@pytest.fixture
def sample_project(db, admin_user):
    p = Project(name="Test Project", owner_id=admin_user.id)
    db.add(p); db.commit(); db.refresh(p)
    return p


@pytest.fixture
def sample_task(db, sample_project, admin_user, readonly_user):
    t = Task(
        title="Test Task",
        status="new",
        project_id=sample_project.id,
        owner_id=admin_user.id,
        assigned_to=readonly_user.id,
    )
    db.add(t); db.commit(); db.refresh(t)
    return t
