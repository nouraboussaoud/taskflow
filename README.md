# TaskFlow

TaskFlow is a secure task and project management application built as a junior Cloud, DevOps, and Full-Stack engineering assessment.

## Phase 1: local database foundation

This phase starts MySQL 8 with persistent storage. Application services will be added in later phases.

### Prerequisites

- Docker Desktop running
- PowerShell 7+ (Windows PowerShell also works)

### Start MySQL

```powershell
Copy-Item .env.example .env
docker compose up -d
docker compose ps
docker compose logs db
```

The database intentionally has no published host port. Future backend containers will connect through Docker's internal `taskflow-internal` network using the hostname `db`.

### Stop MySQL

```powershell
docker compose down
```

`docker compose down` preserves the `mysql_data` volume. To remove all local database data deliberately, run `docker compose down -v`.

## Planned stack

- FastAPI, SQLAlchemy, Alembic, MySQL 8, JWT authentication
- React + Vite
- Docker Compose, GitHub Actions, GHCR

## Run the backend and frontend locally

Start Docker Desktop, then run from the repository root:

```powershell
docker compose up -d --build backend
docker compose ps
```

The backend applies Alembic migrations before serving. Check `http://localhost:8001/health` and open Swagger UI at `http://localhost:8001/docs`. MySQL remains on a private Docker network with no host port.

In a second PowerShell terminal, run:

```powershell
Set-Location frontend
npm.cmd ci
npm.cmd run dev
```

Open `http://localhost:5173`. The frontend calls `http://localhost:8001/api/v1` by default. If Vite was already running before you changed the API URL, restart it and refresh the browser. Use `docker compose down` to stop the containers without deleting MySQL data.

The backend reads `MYSQL_PASSWORD` from the repository-root `.env` as its database password. `DB_PASSWORD` is an optional override. A backend started directly on Windows cannot reach the default `DB_HOST=db` because that hostname exists only inside Docker.
