## Alerting & Notification Platform (FastAPI)

A FastAPI-based service for creating, delivering, and tracking user alerts and notifications. It uses async SQLAlchemy with PostgreSQL, Alembic for migrations, and a clean layered architecture (API → services → repositories → models).

### Features
- **Alerts management**: create, update, list alerts
- **User inbox**: fetch, read/unread, snooze, visibility
- **Reminder jobs**: trigger reminders for pending alerts
- **Analytics**: simple summary endpoints
- **Extensible channels**: in-app channel with a pluggable base for future Email/SMS

---

## Getting Started

### Prerequisites
- Python 3.11+
- PostgreSQL 13+ running locally or accessible via network

### Setup (Windows PowerShell shown)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Configuration
The app reads settings from environment variables via `.env` if present.

Minimum required setting:
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/alerts
```

Defaults (if not overridden):
- `APP_NAME=alerts-platform`
- `ENVIRONMENT=dev`
- `API_PREFIX=/api`

You can keep these defaults unless you need to change them. See `app/core/config.py` for all options.

### Database Migrations (Alembic)
Initialize and apply the schema:
```powershell
alembic revision --autogenerate -m "init"
alembic upgrade head
```

If you later change models, create a new revision and upgrade again:
```powershell
alembic revision --autogenerate -m "your change"
alembic upgrade head
```

### Optional: Seed Sample Data
```powershell
python -m scripts.seed
```

### Run the API Server
```powershell
uvicorn app.main:app --reload
```

Once running:
- Swagger UI: `http://localhost:8000/docs`
- OpenAPI JSON: `http://localhost:8000/openapi.json`
- Health endpoint: `GET http://localhost:8000/health`

---

## API Overview
`API_PREFIX` defaults to `/api` (see config).

- Admin alerts:
  - `GET {API_PREFIX}/admin/alerts`
  - `POST {API_PREFIX}/admin/alerts`
  - `PUT {API_PREFIX}/admin/alerts/{id}`
- User alerts:
  - `GET {API_PREFIX}/user/alerts?user_id={id}`
  - `POST {API_PREFIX}/user/alerts/read`
  - `POST {API_PREFIX}/user/alerts/unread`
  - `POST {API_PREFIX}/user/alerts/snooze`
- Ops:
  - `POST {API_PREFIX}/ops/trigger-reminders`
- Analytics:
  - `GET {API_PREFIX}/analytics/summary`

Use Swagger UI for request/response schemas and try-it-out.

---

## Project Structure
```
app/
  api/           # FastAPI routers (admin, user, ops, analytics)
  channels/      # Delivery channels (base + in-app)
  core/          # Config, database
  db/            # SQLAlchemy Base
  models/        # ORM models
  repositories/  # Data access layer
  schemas/       # Pydantic schemas
  services/      # Business logic (alerts, reminders, user prefs)
migrations/      # Alembic environment and versions
scripts/         # Utilities like seed script
tests/           # Unit tests
```

---

## Testing
This repository includes tests in `tests/`. If you don't have `pytest` installed globally, install it into your virtualenv:
```powershell
python -m pip install pytest
pytest -q
```

Note: Tests may assume a reachable PostgreSQL database and an up-to-date schema (run migrations first).

---

## Development Tips
- Use an isolated virtual environment (`.venv`).
- Keep your database URL in `.env` during local development.
- Regenerate and apply Alembic migrations whenever models change.
- Explore and test endpoints via Swagger at `/docs`.

---

## Contributing

We welcome contributions! Use standard GitHub flow:

1. Fork the repository on GitHub.
2. Clone your fork:
   ```powershell
   git clone https://github.com/<your-username>/<your-fork>.git
   cd <your-fork>
   ```
3. Create a feature branch:
   ```powershell
   git checkout -b feat/<short-feature-name>
   ```
4. Set up your environment and run the app (see Getting Started).
5. Commit changes with clear messages:
   ```powershell
   git add -A
   git commit -m "feat: add <concise description>"
   ```
6. Push and open a Pull Request from your fork/branch to the upstream `main` branch.
7. Address review feedback and keep your branch up to date:
   ```powershell
   git fetch origin
   git rebase origin/main
   ```

Guidelines:
- Keep PRs focused and reasonably small.
- Add/adjust tests when changing behavior.
- Avoid breaking API changes unless discussed first.

---

## Configuration Reference
See `app/core/config.py` for the authoritative list. Common variables:

- `DATABASE_URL` (required): `postgresql+asyncpg://<user>:<pass>@<host>:<port>/<db>`
- `APP_NAME` (optional): Defaults to `alerts-platform`
- `ENVIRONMENT` (optional): `dev` by default
- `API_PREFIX` (optional): Defaults to `/api`

---

## Troubleshooting
- Alembic cannot connect: verify `DATABASE_URL` and that PostgreSQL is running.
- Import errors during migration autogenerate: ensure all models are imported in `migrations/env.py` (this repo already does it).
- Async driver missing: requirements include `asyncpg`; reinstall deps if needed.

---
