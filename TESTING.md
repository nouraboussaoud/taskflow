# Testing and evidence

Run commands from the repository root unless a `Set-Location` is shown. Local results below are observations from 2026-10-26, not a claim that GitHub Actions or a hosted environment has passed.

## Local checks (Windows PowerShell)

| Check | Command | Observed result |
| --- | --- | --- |
| Backend lint | `Set-Location backend; .\.venv\Scripts\ruff.exe check .` | Passed. |
| Backend unit/API tests | `Set-Location backend; .\.venv\Scripts\pytest.exe -q -p no:cacheprovider` | 10 passed; 2 third-party deprecation warnings on local Python 3.14. CI targets Python 3.12. |
| Frontend lint | `Set-Location frontend; npm.cmd run lint` | Passed after Phase 6 dependency update. |
| Frontend test | `Set-Location frontend; npm.cmd test -- --run` | 3 tests passed in 1 test file. |
| Frontend production build | `Set-Location frontend; npm.cmd run build` | Passed with Vite 8.3.5. |
| npm dependency audit | `Set-Location frontend; npm.cmd audit --audit-level=high` | 0 vulnerabilities reported after dependency update. |
| Frontend Docker build | `docker build -t taskflow-frontend:phase6 ./frontend` | Passed locally. |
| Compose config | `docker compose config --quiet` | Passed during Phase 5; staging override config also validated with example image variables. |
| Full local stack | `docker compose up -d --build; docker compose ps` | A previous Phase 5 run reported all three services healthy. The 2026-10-26 recheck could not access the local Windows Docker daemon (`//./pipe/docker_engine`: access denied), so it is not a fresh runtime confirmation. |
| API smoke | `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\smoke_test.ps1` | Phase 5 run passed health, registration, login, project, task. Re-run after restoring Docker-daemon access. |

For a clean host setup, create a Python 3.12 environment and install `backend/requirements-dev.txt`, then run backend commands from `backend`. Existing local `.venv` may use a different Python version; do not claim exact CI parity from a host-only run. The smoke test creates persistent test records in the Compose MySQL volume.

## Coverage map

- `backend/tests/test_security.py`: password hashing/verification and JWT signing shape.
- `backend/tests/test_auth_api.py`: register/login, duplicate email (409), invalid credentials/missing token (401), and CORS header on an unexpected 500.
- `backend/tests/test_projects_and_tasks_api.py`: project and task CRUD, task search/status filter, dashboard counts/overdue, invalid input (422), health, and six cross-user read/update/delete checks (404).
- `backend/tests/test_dashboard_service.py`: owner-scoped service aggregation.
- `frontend/src/test/Login.test.jsx`: sign-in route, token storage, and dashboard rendering with mocked fetch.
- `scripts/smoke_test.ps1` and `.sh`: real HTTP path through frontend Nginx to API and MySQL.

The pytest fixtures use in-memory SQLite for fast isolated behavior tests. They do **not** prove MySQL-specific behavior. The CI backend job starts MySQL 8 and applies Alembic migrations against it; the Compose smoke test exercises the actual MySQL-backed API. More direct MySQL API integration tests would strengthen coverage.

## CI and security checks to capture

The [CI workflow](.github/workflows/ci.yml) runs on pull requests and pushes to `develop`: backend lint/tests/MySQL migration/`pip-audit`, frontend lint/test/build/`npm audit`, both Docker builds with Trivy HIGH/CRITICAL gates, and Gitleaks. [release.yml](.github/workflows/release.yml) calls CI before GHCR publishing. [staging.yml](.github/workflows/staging.yml) is a manually triggered, disposable-runner smoke test of released images.

**Pending evidence:** save links to a successful PR CI run, tag release run, and staging simulation in the submission record once they actually exist. Trivy, Gitleaks, and `pip-audit` were not verified locally; local `pip-audit` installation stalled. An audit or scan failure is not a pass and should block release until investigated. Record finding ID, affected version, remediation, and a rerun in [SECURITY.md](SECURITY.md).

Useful local rerun sequence:

```powershell
Set-Location backend
.\.venv\Scripts\ruff.exe check .
.\.venv\Scripts\pytest.exe -q
Set-Location ..\frontend
npm.cmd ci
npm.cmd run lint
npm.cmd test
npm.cmd run build
npm.cmd audit --audit-level=high
Set-Location ..
docker compose up -d --build
docker compose ps
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\smoke_test.ps1
```

Test commands should be run in a fresh PowerShell session if `Set-Location` differs from the expected directory. Do not run the smoke script against a shared or production database without accepting that it adds test records.
