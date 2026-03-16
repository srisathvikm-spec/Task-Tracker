# Task Tracker Application

A production-grade Task Tracker built with **FastAPI**, **React + Vite + TypeScript**, **PostgreSQL**, and **Azure AD SSO**.

---

## 1. System Architecture

```
┌───────────────┐  HTTPS + Bearer Token  ┌──────────────────────┐  SQLAlchemy   ┌──────────┐
│  React SPA    │◄──────────────────────►│  FastAPI Backend     │◄────────────►│ Postgres │
│  Vite + TS    │                        │  Python 3.11         │              │          │
│  Ant Design   │                        │  Layered Arch        │              │          │
└───────┬───────┘                        └──────────┬───────────┘              └──────────┘
        │ MSAL popup                                │ Validate ID Token
        ▼                                           ▼
┌───────────────────────────────────────────────────────────────┐
│               Microsoft Entra ID (Azure AD)                   │
└───────────────────────────────────────────────────────────────┘
```

### Backend Layers

| Layer          | Files                           | Responsibility                           |
| -------------- | ------------------------------- | ---------------------------------------- |
| **Routers**    | `routers/*_router.py`           | HTTP handling, input validation, responses |
| **Services**   | `services/*_service.py`         | Business logic, RBAC enforcement          |
| **Repos**      | `repositories/*_repository.py`  | Database queries, pagination              |
| **Models**     | `models/*.py`                   | SQLAlchemy ORM (UUID PKs)                 |
| **Schemas**    | `schemas/*_schema.py`           | Pydantic validation                       |

---

## 2. Database ER Diagram

```
users (UUID PK)        roles (UUID PK)
├── name               ├── name
├── email (unique)     └────────┐
├── is_active                   │  user_roles (N:M)
├── created_at                  │  ├── user_id FK
│                               │  └── role_id FK
├──── owns ──► projects (UUID PK)
│              ├── name
│              ├── description
│              ├── start_date / end_date
│              ├── owner_id FK ──► users
│              └── created_at
│                    │
│                    │ 1:N
│                    ▼
└──── owns/assigned ──► tasks (UUID PK)
                        ├── title
                        ├── description
                        ├── status (enum)
                        ├── due_date
                        ├── owner_id FK ──► users
                        ├── project_id FK ► projects
                        ├── assigned_to FK ► users
                        ├── created_at
                        └── updated_at
```

---

## 3. RBAC Roles

| Action                            | Admin | Manager | Read Only User |
| --------------------------------- | :---: | :-----: | :------------: |
| Manage users & roles              |  ✅   |   ❌    |       ❌       |
| Create and edit projects          |  ✅   |   ✅    |       ❌       |
| Delete projects                   |  ✅   |   ❌    |       ❌       |
| Create tasks                      |  ✅   |   ✅    |       ❌       |
| Assign tasks                      |  ✅   |   ✅    |       ❌       |
| View tasks                        |  ✅   |   ✅    |  Assigned only |
| Update task status                |  ✅   |   ✅    | Assigned only (to completed) |

---

## 4. API Contract

All list endpoints return a structured envelope with pagination:

```json
{ "success": true, "message": "Success", "data": [...], "meta": { "total": 42, "page": 1 } }
```

| Method | Endpoint                     | Access             |
| ------ | ---------------------------- | ------------------ |
| GET    | `/api/v1/auth/me`            | Authenticated      |
| GET    | `/api/v1/users`              | Admin              |
| GET    | `/api/v1/users/{id}`         | Admin              |
| PATCH  | `/api/v1/users/{id}/role`    | Admin              |
| GET    | `/api/v1/users/roles/all`    | Admin              |
| POST   | `/api/v1/projects`           | Admin, Manager     |
| GET    | `/api/v1/projects`           | All                |
| GET    | `/api/v1/projects/{id}`      | All                |
| PUT    | `/api/v1/projects/{id}`      | Admin, Manager     |
| DELETE | `/api/v1/projects/{id}`      | Admin only         |
| POST   | `/api/v1/tasks`              | Admin, Manager     |
| GET    | `/api/v1/tasks`              | All (Read Only User sees assigned only) |
| GET    | `/api/v1/tasks/{id}`         | All (Read Only User assigned-only access) |
| PUT    | `/api/v1/tasks/{id}`         | RBAC rules         |
| DELETE | `/api/v1/tasks/{id}`         | Admin only         |
| PATCH  | `/api/v1/tasks/{id}/status`  | All (RBAC)         |
| PATCH  | `/api/v1/tasks/{id}/assign`  | Admin, Manager     |

**Filtering** (list endpoints): `?name=`, `?status=`, `?assigned_to=`, `?search=`, `?project_id=`

---

## 5. Environment Variables

| Variable           | Default                                           | Description                  |
| ------------------ | ------------------------------------------------- | ---------------------------- |
| `DATABASE_URL`     | `postgresql://admin:adminpassword@localhost:5432/task_tracker` | PostgreSQL connection |
| `AZURE_CLIENT_ID`  | *(empty)*                                         | Azure App Client ID          |
| `AZURE_TENANT_ID`  | *(empty)*                                         | Azure Tenant ID              |
| `SECRET_KEY`       | `super_secret_key_change_in_production`            | JWT signing secret           |
| `LOG_LEVEL`        | `INFO`                                            | Python log level             |

---

## 6. Local Development

### Docker Compose (recommended)

```bash
docker-compose up --build
```

Services: **postgres** (5432), **backend** (8000), **frontend** (5173)

Seed the database:
```bash
docker-compose exec backend python scripts/seed.py
```

### Manual

```bash
# Backend
cd backend
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

### Local Login (without Azure)

The login page provides a **Mock Login** input. Enter `admin@local.test` (or any seeded email) to bypass Azure SSO.

---

## 7. Seed Data

`python scripts/seed.py` creates:

| Entity   | Records                                               |
| -------- | ----------------------------------------------------- |
| Roles    | Admin, Manager, Read Only User                       |
| Users    | admin@local.test, manager@local.test, user@local.test |
| Projects | Includes Sample Team Project with role-based examples |
| Tasks    | Multiple sample tasks assigned across Admin/Manager/Read Only User |

---

## 8. Running Tests

```bash
cd backend
pytest tests/ -v
```

| Test File                | Coverage                                     |
| ------------------------ | -------------------------------------------- |
| `test_health.py`         | Liveness probe                               |
| `test_user_service.py`   | User CRUD, role assignment, duplicates       |
| `test_project_service.py`| Project CRUD, filtering, delete              |
| `test_task_service.py`   | RBAC: read-only user restrictions, admin override |

---

## 9. API Documentation

Once the backend is running:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
