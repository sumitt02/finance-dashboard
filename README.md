# Finance Dashboard API

A role-based finance dashboard backend built with **FastAPI**, **SQLAlchemy**, and **SQLite**.  
Designed as a clean, well-structured backend assessment submission.

---

## Tech Stack

| Layer       | Technology                          |
|-------------|-------------------------------------|
| Framework   | FastAPI                             |
| ORM         | SQLAlchemy 2.x                      |
| Database    | SQLite (via `better-sqlite3` style) |
| Validation  | Pydantic v2                         |
| Auth        | JWT (python-jose) + bcrypt          |

---

## Project Structure

```
finance-dashboard/
├── app/
│   ├── core/
│   │   ├── config.py          # Settings from .env
│   │   ├── database.py        # SQLAlchemy engine & session
│   │   ├── security.py        # JWT + bcrypt helpers
│   │   └── dependencies.py    # get_current_user, role_required
│   ├── models/
│   │   ├── user.py            # User ORM model
│   │   └── record.py          # FinancialRecord ORM model
│   ├── schemas/
│   │   ├── auth.py            # Register/Login/Token schemas
│   │   ├── user.py            # User response & update schemas
│   │   ├── record.py          # Record CRUD schemas
│   │   └── dashboard.py       # Summary response schemas
│   ├── routers/
│   │   ├── auth.py            # /auth/*
│   │   ├── users.py           # /users/*
│   │   ├── records.py         # /records/*
│   │   └── dashboard.py       # /dashboard/*
│   ├── services/
│   │   ├── auth_service.py    # Register & login logic
│   │   ├── user_service.py    # User management logic
│   │   ├── record_service.py  # CRUD + filtering logic
│   │   └── dashboard_service.py # Aggregation & summary logic
│   └── utils/
│       ├── enums.py           # Role, RecordType enums
│       └── exceptions.py      # Custom HTTP exceptions
├── main.py                    # App entry point
├── seed.py                    # Demo data seeder
├── requirements.txt
├── .env.example
└── README.md
```

---

## Setup & Run

### 1. Clone & create virtual environment

```bash
git clone <your-repo-url>
cd finance-dashboard

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env if needed (defaults work out of the box)
```

### 4. Seed the database

```bash
python seed.py
```

This creates 3 demo users and 25 sample financial records.

### 5. Start the server

```bash
uvicorn main:app --reload
```

API runs at: `http://127.0.0.1:8000`  
Swagger docs: `http://127.0.0.1:8000/docs`

---

## Demo Credentials

| Role    | Email              | Password    |
|---------|--------------------|-------------|
| admin   | admin@demo.com     | admin123    |
| analyst | analyst@demo.com   | analyst123  |
| viewer  | viewer@demo.com    | viewer123   |

---

## API Reference

### Auth

| Method | Endpoint         | Auth | Description              |
|--------|------------------|------|--------------------------|
| POST   | /auth/register   | ❌   | Register (role: viewer)  |
| POST   | /auth/login      | ❌   | Login, returns JWT token |

### Users *(Admin only)*

| Method | Endpoint               | Role  | Description           |
|--------|------------------------|-------|-----------------------|
| GET    | /users/                | Admin | List all users        |
| GET    | /users/{id}            | Admin | Get user by ID        |
| PATCH  | /users/{id}/role       | Admin | Update user role      |
| PATCH  | /users/{id}/status     | Admin | Activate/deactivate   |

### Records

| Method | Endpoint           | Role                    | Description                  |
|--------|--------------------|-------------------------|------------------------------|
| POST   | /records/          | Admin                   | Create a record              |
| GET    | /records/          | Viewer, Analyst, Admin  | List records (with filters)  |
| GET    | /records/{id}      | Viewer, Analyst, Admin  | Get record by ID             |
| PUT    | /records/{id}      | Admin                   | Update a record              |
| DELETE | /records/{id}      | Admin                   | Soft delete a record         |

**Available filters for GET /records/:**
- `type` — `income` or `expense`
- `category` — partial match (case-insensitive)
- `date_from` — ISO date (e.g. `2024-01-01`)
- `date_to` — ISO date
- `skip` — pagination offset (default: 0)
- `limit` — page size (default: 20, max: 100)

### Dashboard

| Method | Endpoint                    | Role                   | Description                        |
|--------|-----------------------------|------------------------|------------------------------------|
| GET    | /dashboard/summary          | Viewer, Analyst, Admin | Total income, expenses, net balance|
| GET    | /dashboard/by-category      | Analyst, Admin         | Totals grouped by category         |
| GET    | /dashboard/monthly-trends   | Analyst, Admin         | Last 6 months income vs expense    |
| GET    | /dashboard/recent           | Viewer, Analyst, Admin | Last 5 transactions                |

---

## Role Permissions

| Action                        | Viewer | Analyst | Admin |
|-------------------------------|--------|---------|-------|
| Login / Register              | ✅     | ✅      | ✅    |
| View records                  | ✅     | ✅      | ✅    |
| Filter records                | ✅     | ✅      | ✅    |
| View summary & recent         | ✅     | ✅      | ✅    |
| View category breakdown       | ❌     | ✅      | ✅    |
| View monthly trends           | ❌     | ✅      | ✅    |
| Create / Update / Delete records | ❌  | ❌      | ✅    |
| Manage users                  | ❌     | ❌      | ✅    |

---

## Environment Variables

| Variable                    | Default              | Description                      |
|-----------------------------|----------------------|----------------------------------|
| DATABASE_URL                | sqlite:///./finance.db | SQLAlchemy DB connection string |
| SECRET_KEY                  | (required)           | JWT signing secret               |
| ALGORITHM                   | HS256                | JWT algorithm                    |
| ACCESS_TOKEN_EXPIRE_MINUTES | 60                   | Token expiry in minutes          |

---

## Error Response Format

All errors return a consistent JSON shape:

```json
{
  "success": false,
  "message": "Descriptive error message",
  "details": null
}
```

Validation errors include a `details` array with field-level info.

---

## Design Decisions & Tradeoffs

### SQLite over PostgreSQL
Chosen for zero-config local setup. SQLAlchemy abstracts the DB layer, so switching to PostgreSQL only requires changing `DATABASE_URL`.

### Soft Deletes
Records are never physically removed — `is_deleted=True` is set instead. This preserves audit history and allows recovery.

### JWT in Authorization Header
Standard Bearer token approach. No refresh token implemented (out of scope for assessment), but expiry is configurable.

### Role Stored in DB (not only JWT)
Role is stored in the DB and re-fetched on every request. This ensures deactivated users or role changes take effect immediately without waiting for token expiry.

### Thin Routers, Fat Services
All business logic lives in `services/`. Routers only handle HTTP concerns (parsing, status codes, response models). This makes logic easy to test in isolation.

### Pydantic v2 Validators
Field-level validation (e.g. amount > 0, non-empty category) is enforced at the schema layer before any DB call is made.
