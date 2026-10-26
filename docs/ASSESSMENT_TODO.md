# Assessment completion checklist

Use this checklist as the source of truth before submitting. Do not mark an item complete until there is evidence: a command result, a GitHub URL, a screenshot, or a commit/PR link.

## Immediate blocker: security CI

- [x] Create branch `fix/security-dependencies` from updated `develop`.
- [x] Apply the code/dependency remediation: replace the vulnerable JWT dependency, update compatible API dependencies, and update the backend image base.
- [ ] Rebuild, scan, and verify the remediation in GitHub Actions before declaring it resolved.
- [ ] Keep the security gate enabled. If an upstream OS vulnerability has no vendor fix, document the risk and configure the scanner to ignore **only unfixed** findings; do not suppress fixable HIGH/CRITICAL findings.
- [ ] Update `SECURITY.md` with finding IDs, affected versions, remediation, remaining risks, date, and the successful rerun result.
- [ ] Open a PR to `develop`, ensure CI is green, merge it, and save the workflow URL.

## Application and Docker evidence

- [ ] Run `docker compose up -d --build` from a clean local state.
- [ ] Capture `docker compose ps` showing healthy database, backend, and frontend services.
- [ ] Demonstrate registration, login, project CRUD, task CRUD, status/priority, search/filter, dashboard statistics, loading/error states, and responsive UI.
- [ ] Demonstrate persistence: create a task, restart the stack without `-v`, and show that the task remains.
- [ ] Capture Swagger at `http://localhost:8001/docs`; authorize with a JWT and call protected endpoints.
- [ ] Run `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\smoke_test.ps1` and retain its result.

## Test and quality evidence

- [ ] Run backend lint and tests: `backend\.venv\Scripts\python.exe -m ruff check backend` and `backend\.venv\Scripts\python.exe -m pytest backend\tests -q`.
- [ ] Run frontend checks: `npm ci`, `npm run lint`, `npm run test`, and `npm run build` from `frontend`.
- [ ] Update `TESTING.md` with actual dates and results, not planned results.
- [ ] Verify the CI workflow passes lint, tests, MySQL migrations, `pip-audit`, `npm audit`, Trivy, and Gitleaks.

## Required documentation

- [x] `README.md`
- [x] `ARCHITECTURE.md`
- [x] `CLOUD_DEPLOYMENT.md`
- [x] `TESTING.md`
- [x] `SECURITY.md`
- [x] `.env.example`
- [x] `AI_USAGE.md`
- [x] `AI_USAGE_LOG.md`
- [ ] Review every document for accurate, current evidence before release.
- [ ] Ensure no `.env`, secrets, screenshots with credentials, or database dumps are committed.

## Git, CI/CD, and release

- [ ] Confirm `main`, `develop`, and feature branches exist in GitHub.
- [ ] Confirm at least two meaningful pull requests are visible in GitHub history.
- [ ] Push the final `develop` changes and save a successful CI workflow URL.
- [ ] Create and merge a final PR from `develop` to `main` only after checks pass.
- [ ] Create tags `v0.1.0` and `v1.0.0` on the final `main` commit.
- [ ] Confirm the release workflow publishes versioned backend and frontend images to GHCR.
- [ ] Confirm a GitHub `v1.0.0` Release exists.
- [ ] Run the manually triggered staging workflow with `v1.0.0`; save its successful URL.
- [ ] Verify the rollback procedure in `docs/RELEASE_CHECKLIST.md` can be explained.

## Final submission package

- [ ] Record a 5-10 minute demo: app features, Swagger, MySQL persistence, tests, Docker, Git history/PRs, CI/CD, security, deployment plan, rollback.
- [ ] Collect URLs: repository, `v1.0.0` GitHub Release, GHCR backend/frontend images, CI run, staging run, and optional live app.
- [ ] Reply to the recruitment email before the deadline with those URLs.
- [ ] Rehearse a short technical defense: request flow, JWT authorization, data isolation, migrations, Docker networking, FastAPI choice, React/Vite choice, CI gates, and rollback.
