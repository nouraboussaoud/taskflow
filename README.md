# TaskFlow

TaskFlow is a secure task and project management application built as a junior Cloud, DevOps, and Full-Stack engineering assessment.

## Local setup

### Prerequisites

- Docker Desktop running
- PowerShell 7+ (Windows PowerShell also works)

### Start all three services

```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
# Edit .env and replace the example passwords and JWT secret first.
docker compose up -d --build
docker compose ps
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\smoke_test.ps1
```

Open the app at `http://localhost:8080` and Swagger UI at `http://localhost:8001/docs`. Nginx proxies `/api/v1` and `/health` to the backend. The backend applies Alembic migrations before serving. MySQL uses the persistent `mysql_data` volume and has no published host port.

The smoke script creates a unique test user, project, and task in the local database. On Linux, run `bash scripts/smoke_test.sh` instead.

### Stop the stack

```powershell
docker compose down
```

`docker compose down` preserves `mysql_data`. Running `docker compose down -v` deletes that volume and all local TaskFlow data.

## Stack

- FastAPI, SQLAlchemy, Alembic, MySQL 8, JWT authentication
- React + Vite
- Docker Compose, GitHub Actions, GHCR

## Frontend development mode

Start Docker Desktop, then run from the repository root:

```powershell
docker compose up -d --build backend
docker compose ps
```

Check `http://localhost:8001/health` and open Swagger UI at `http://localhost:8001/docs`.

In a second PowerShell terminal, run:

```powershell
Set-Location frontend
npm.cmd ci
npm.cmd run dev
```

Open `http://localhost:5173`. The frontend calls `http://localhost:8001/api/v1` by default. If Vite was already running before you changed the API URL, restart it and refresh the browser. Use `docker compose down` to stop the containers without deleting MySQL data.

The backend reads `MYSQL_PASSWORD` from the repository-root `.env` as its database password. `DB_PASSWORD` is an optional override. A backend started directly on Windows cannot reach the default `DB_HOST=db` because that hostname exists only inside Docker.
