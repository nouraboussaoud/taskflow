# TaskFlow

TaskFlow is a small project and task manager built for a Cloud/DevOps/Full-Stack engineering assessment. Each signed-in user sees only their own projects and tasks.

## What it does

- Register, sign in, and manage projects and tasks (create, list, edit, delete).
- Set task status (`todo`, `in_progress`, `done`), priority (`low`, `medium`, `high`), and due date; search and filter tasks.
- See dashboard counts by status and priority, including overdue tasks.
- Use the API directly through Swagger UI with a Bearer token.

## Stack and choices

| Layer | Technology | Reason |
| --- | --- | --- |
| UI | React, Vite, React Router, plain CSS | Small responsive SPA with a quick local build. |
| API | Python 3.12, FastAPI, Pydantic | Typed REST endpoints and generated OpenAPI docs. |
| Data | MySQL 8, SQLAlchemy, Alembic | Required persistent database with versioned schema migrations. |
| Runtime | Docker Compose, unprivileged Nginx/frontend and API images | Reproducible three-service local stack. |
| Delivery | GitHub Actions, GHCR | Free-to-start build, scan, and versioned-image workflows; no deployed server is assumed. |

## Local setup (Windows PowerShell)

Prerequisites: Docker Desktop with Linux containers and PowerShell. Node.js 22 and Python 3.12 are needed only for running frontend/backend tools directly on the host.

```powershell
git clone https://github.com/nouraboussaoud/taskflow.git
Set-Location taskflow
Copy-Item .env.example .env
# Edit .env: replace both MySQL passwords and JWT_SECRET_KEY with unique random values.
# For the Docker-served UI, set FRONTEND_ORIGIN=http://localhost:8080.
docker compose up -d --build
docker compose ps
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\smoke_test.ps1
```

The app is at <http://localhost:8080>; the API's Swagger UI is at <http://localhost:8001/docs> and its OpenAPI schema at <http://localhost:8001/openapi.json>. For Swagger, register or log in, copy the returned `access_token`, then click **Authorize** and enter the token. The backend runs `alembic upgrade head` before serving. `/health` reports API-to-MySQL connectivity.

The smoke script creates a unique local test user, project, and task; it does not remove them. On Linux, use `bash scripts/smoke_test.sh`. Run `docker compose down` to stop services without deleting data. **Do not use `docker compose down -v` unless you intend to delete the MySQL volume.** MySQL has no host port.

### Configuration

Copy [.env.example](.env.example) to an ignored `.env`; never commit real values. The root file supplies Docker services. [frontend/.env.example](frontend/.env.example) is an optional Vite development example.

| Variable | Purpose |
| --- | --- |
| `MYSQL_DATABASE`, `MYSQL_USER` | Database and least-privilege application username. |
| `MYSQL_PASSWORD`, `MYSQL_ROOT_PASSWORD` | Distinct database passwords; replace examples. |
| `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER` | API database connection; `DB_HOST=db` inside Compose. |
| `DB_PASSWORD` | Optional API password override when not using `MYSQL_PASSWORD`. |
| `JWT_SECRET_KEY` | Random JWT signing key; changing it invalidates existing tokens. |
| `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES` | Token algorithm and lifetime. |
| `FRONTEND_ORIGIN` | Exact origin allowed by API CORS; `http://localhost:8080` for Docker UI, `http://localhost:5173` for Vite dev. |
| `VITE_API_URL` | Optional frontend-dev API URL; Docker builds use same-origin `/api/v1`. |

### Frontend development mode

```powershell
docker compose up -d --build backend
Set-Location frontend
npm.cmd ci
npm.cmd run dev
```

Open <http://localhost:5173>; the dev UI calls `http://localhost:8001/api/v1` by default. Set `FRONTEND_ORIGIN=http://localhost:5173` in the root `.env` and recreate the backend if you changed it. A host-run backend cannot resolve Docker's `db` hostname without separate database networking.

## Delivery and project notes

The [CI workflow](.github/workflows/ci.yml) checks lint, tests, MySQL migrations, dependency audits, Docker image scans, and secrets. A `vX.Y.Z` tag triggers [release.yml](.github/workflows/release.yml) only after CI passes; [staging.yml](.github/workflows/staging.yml) can smoke-test published images on a temporary GitHub runner. A workflow file is not proof of a successful GitHub run or a deployed server.

- [Architecture](ARCHITECTURE.md) — components, trust boundaries, and request/data flow.
- [Testing](TESTING.md) — commands, observed results, and pending checks.
- [Security](SECURITY.md) — controls, scan status, and remaining risks.
- [Cloud deployment plan](CLOUD_DEPLOYMENT.md) — hypothetical Ubuntu host setup, HTTPS, updates, and rollback.
- [AI assistance disclosure](AI_USAGE.md) and [usage log](AI_USAGE_LOG.md).
- [Release and submission checklist](docs/RELEASE_CHECKLIST.md) — PRs, tags, evidence, rollback, email, and demo script.

This is an assessment MVP, not a production service. It has no hosted environment, automated backups, monitoring/alerts, rate limiting, or password reset. GitHub-hosted runner minutes, GHCR storage/bandwidth, and any future server/domain have plan-specific limits or costs; check current terms before relying on free capacity. Do not treat the staging simulation as production deployment.
