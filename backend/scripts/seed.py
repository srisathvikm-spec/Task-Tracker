"""Seed script – populate roles, users, projects, and tasks.

Usage:
    python -m scripts.seed          (from backend/ directory)
    docker-compose exec backend python scripts/seed.py
"""

import os
import sys
import uuid
from datetime import date, timedelta
from typing import Dict

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database.base import Base
from app.database.session import engine, SessionLocal
from app.models.user import User
from app.models.role import Role
from app.models.project import Project
from app.models.task import Task


def seed() -> None:
    print("Creating tables …")
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    # Remove legacy roles that are no longer supported.
    for legacy_role_name in ["Task Creator", "User"]:
        legacy_role = db.query(Role).filter(Role.name == legacy_role_name).first()
        if legacy_role:
            db.delete(legacy_role)
            print(f"  ✔ Legacy role '{legacy_role_name}' removed")
    db.commit()

    # ── Roles ──────────────────────────────────────────────────────────
    role_names = ["Admin", "Manager", "Read Only User"]
    role_map: Dict[str, Role] = {}
    for name in role_names:
        existing = db.query(Role).filter(Role.name == name).first()
        if not existing:
            role = Role(name=name)
            db.add(role)
            db.flush()
            role_map[name] = role
            print(f"  ✔ Role '{name}' created")
        else:
            role_map[name] = existing
            print(f"  – Role '{name}' exists")
    db.commit()

    # ── Users ──────────────────────────────────────────────────────────
    users_spec = [
        ("Alice Admin", "admin@local.test", "Admin"),
        ("Bob Manager", "manager@local.test", "Manager"),
        ("Carol Read Only", "user@local.test", "Read Only User"),
        ("Sri Sathvik", "srisathvikm@gmail.com", "Admin"),
    ]
    user_map: Dict[str, User] = {}
    for name, email, role_name in users_spec:
        existing = db.query(User).filter(User.email == email).first()
        if not existing:
            u = User(name=name, email=email)
            u.roles.append(role_map[role_name])
            db.add(u)
            db.flush()
            user_map[email] = u
            print(f"  ✔ User '{name}' ({role_name})")
        else:
            expected_role = role_map[role_name]
            if expected_role not in existing.roles:
                existing.roles.append(expected_role)
                db.flush()
            user_map[email] = existing
            print(f"  – User '{name}' exists")
    db.commit()

    admin = user_map["admin@local.test"]
    manager = user_map["manager@local.test"]
    read_only_user = user_map["user@local.test"]
    sri = user_map["srisathvikm@gmail.com"]

    # ── Projects ───────────────────────────────────────────────────────
    projects_spec = [
        ("Website Redesign", "Overhaul the corporate website", admin.id),
        ("Mobile App MVP", "First version of the mobile app", manager.id),
        ("Infrastructure Upgrade", "Migrate to Kubernetes", admin.id),
        ("Q3 Marketing Campaign", "Launch new product campaign", manager.id),
        ("Security Audit", "Annual penetration testing", admin.id),
        ("Personal Workspace", "Track all my priority tasks", sri.id),
        ("Sample Team Project", "Example project with tasks assigned to each role", manager.id),
    ]
    proj_map: Dict[str, Project] = {}
    for name, desc, oid in projects_spec:
        existing = db.query(Project).filter(Project.name == name).first()
        if not existing:
            p = Project(name=name, description=desc, owner_id=oid,
                        start_date=date.today(), end_date=date.today() + timedelta(days=90))
            db.add(p)
            db.flush()
            proj_map[name] = p
            print(f"  ✔ Project '{name}'")
        else:
            proj_map[name] = existing
            print(f"  – Project '{name}' exists")
    db.commit()

    # ── Tasks ──────────────────────────────────────────────────────────
    tasks_spec = [
        ("Design mockups", "in_progress", proj_map["Website Redesign"].id, admin.id, manager.id),
        ("Setup CI/CD", "not_started", proj_map["Infrastructure Upgrade"].id, admin.id, read_only_user.id),
        ("Implement Login", "new", proj_map["Mobile App MVP"].id, manager.id, None),
        ("DB schema review", "completed", proj_map["Website Redesign"].id, admin.id, admin.id),
        ("Write API docs", "blocked", proj_map["Mobile App MVP"].id, manager.id, read_only_user.id),
        ("Draft press release", "new", proj_map["Q3 Marketing Campaign"].id, manager.id, read_only_user.id),
        ("Create social media assets", "in_progress", proj_map["Q3 Marketing Campaign"].id, manager.id, manager.id),
        ("Review vendor proposals", "new", proj_map["Security Audit"].id, admin.id, manager.id),
        ("Update firewall rules", "completed", proj_map["Security Audit"].id, admin.id, read_only_user.id),
        ("Code vulnerability scan", "in_progress", proj_map["Security Audit"].id, admin.id, read_only_user.id),
        ("Review UI updates", "new", proj_map["Personal Workspace"].id, sri.id, sri.id),
        ("Fix backend bugs", "in_progress", proj_map["Personal Workspace"].id, sri.id, sri.id),
        ("Prepare presentation", "not_started", proj_map["Personal Workspace"].id, sri.id, sri.id),
        ("Approve Q3 budget", "new", proj_map["Q3 Marketing Campaign"].id, manager.id, sri.id),
        ("Collect business requirements", "new", proj_map["Sample Team Project"].id, manager.id, read_only_user.id),
        ("Set up project board", "in_progress", proj_map["Sample Team Project"].id, manager.id, manager.id),
        ("Approve architecture proposal", "not_started", proj_map["Sample Team Project"].id, admin.id, admin.id),
    ]
    for title, status, pid, oid, aid in tasks_spec:
        existing = db.query(Task).filter(Task.title == title).first()
        if not existing:
            t = Task(title=title, status=status, project_id=pid, owner_id=oid,
                     assigned_to=aid, due_date=date.today() + timedelta(days=14))
            db.add(t)
            print(f"  ✔ Task '{title}'")
        else:
            print(f"  – Task '{title}' exists")
    db.commit()
    db.close()
    print("\n🎉  Seed completed!")


if __name__ == "__main__":
    seed()
