# Security notes

This is a transparent assessment-level security record, not a claim of a production security audit.

## Implemented measures

- Passwords are stored as bcrypt hashes, not plaintext. Authentication uses expiring signed JWTs; protected endpoints require a Bearer token.
- ORM queries scope projects and tasks to the authenticated owner. Another user's resource returns 404; cross-user read/update/delete cases are tested.
- Pydantic validates inputs; API error responses use an `error` object, while `/health` avoids exposing database connection details. SQLAlchemy constructs database queries without string-built SQL.
- CORS allows only `FRONTEND_ORIGIN`. The frontend container proxies API calls under the same origin in Docker. Unexpected 500 responses preserve a CORS header for that configured origin, so browser users see the real error.
- `.env` is ignored by Git; `.env.example` contains placeholders. MySQL has no published port. Frontend and backend host ports bind to loopback. The backend and frontend images run as non-root users.
- CI definitions include `pip-audit`, `npm audit`, Trivy image scans with HIGH/CRITICAL exit failure, and Gitleaks secret scanning. The release job depends on the CI workflow. The final CI and release runs passed on 2026-10-26; linked evidence appears below.

## Findings and verification status

| Finding/check | Status on 2026-10-26 | Action |
| --- | --- | --- |
| Old frontend package audit reported 10 findings, including high/critical React Router/Vitest-chain issues | Remediated locally by updating React Router, Vite, Vitest, plugin, and lockfile; `npm audit --audit-level=high` then reported 0 vulnerabilities. | Confirm CI on a clean runner; continue routine updates. |
| Backend Trivy scan | Failed on CI before release. It reported HIGH/CRITICAL findings in `python-jose`/its dependency chain, old Starlette, and the Debian base image. | On branch `fix/security-dependencies`, replace `python-jose` with PyJWT, update FastAPI/Starlette, use the Bookworm Python slim base, and apply available runtime OS updates. Require a clean CI rerun before merge. |
| Backend Python dependency audit | Passed in the [final release PR CI run](https://github.com/nouraboussaoud/taskflow/actions/runs/40392702732). | Re-run on every release; remediate any future fixable finding before release. |
| Trivy backend/frontend image scan after remediation | Passed in the [final release PR CI run](https://github.com/nouraboussaoud/taskflow/actions/runs/40392702732) and again in the [v1.0.0 release workflow](https://github.com/nouraboussaoud/taskflow/actions/runs/40393130519). The gate fails HIGH/CRITICAL vulnerabilities when a vendor fix exists; it skips only upstream findings with no available fix. | Review every release run and document any remaining upstream operating-system risk. |
| Gitleaks repository history scan | Passed in the [final release PR CI run](https://github.com/nouraboussaoud/taskflow/actions/runs/40392702732), which checks out full Git history (`fetch-depth: 0`). | Rotate a real secret immediately if a future scan detects one. |
| Hosted TLS/firewall/backup checks | Not applicable yet; no server deployment verified. | Follow [CLOUD_DEPLOYMENT.md](CLOUD_DEPLOYMENT.md) before any real exposure. |

The initial npm advisories were identified by `npm audit`; the post-update 0-vulnerability result is only a point-in-time registry report, not proof that the code is vulnerability-free. Security check failures must not be bypassed merely to publish. The Trivy `ignore-unfixed` setting does not disable the severity gate: it prevents release from being blocked only by upstream findings for which no vendor patch exists. All fixable HIGH/CRITICAL findings still fail the workflow.

## Remaining risks and next steps

- The SPA stores its JWT in `localStorage`. An XSS bug could expose it. Before production, add a strict Content Security Policy, review third-party scripts, and consider a secure HttpOnly cookie-based session with CSRF protection. Keep token expiry short.
- No API rate limiting, account lockout, password reset, email verification, or MFA exists. Registration/login could be abused; add abuse controls and monitoring before public exposure.
- No automated off-host MySQL backup/restore test or high-availability plan exists. The named volume protects data across normal container restarts, not host failure or accidental deletion.
- The app has no centralized alerting or audit trail. JSON logging avoids intentionally logging request bodies/passwords, but logs and error paths still need operational review.
- Compose image tags and action version tags are not immutable digests. Pin and review supply-chain dependencies for a higher-assurance deployment.
- The CI MySQL service maps port 3306 on its isolated runner for migrations; the application Compose file does **not** publish MySQL. Treat these as separate environments.
- Swagger is reachable through the local API port. A public host plan keeps it behind an SSH tunnel by default.

If a secret is committed, rotate it first; removing it in a later commit does not erase history. Never publish `.env`, database dumps, tokens, or unredacted logs. Report vulnerabilities privately to the repository owner rather than opening a public issue containing exploit details.
