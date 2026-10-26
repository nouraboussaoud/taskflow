# AI usage log

This log records significant AI-assisted work. It contains summaries only and intentionally excludes credentials, tokens, passwords, personal data, and confidential information.

| Date | Tool/model | Task | Prompt summary | Use of output | Verification | Associated change |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-10-26 | OpenAI Codex | Assessment review | Compare the repository against the technical assessment and identify missing deliverables. | Guidance and checklist adapted by the author. | Repository files, Git history, and local commands were reviewed. | Documentation and planning updates. |
| 2026-10-26 | OpenAI Codex | Docker troubleshooting | Diagnose frontend dependency-lock mismatch and backend container startup failure. | Guidance and configuration/code changes adapted by the author. | Frontend Docker build and Docker Compose startup were inspected; final verification is tracked in `TESTING.md`. | `frontend/package-lock.json`, `.gitattributes`, and `backend/entrypoint.sh` review/fix. |
| 2026-10-26 | OpenAI Codex | Learning material | Explain TaskFlow architecture and prepare a French study guide. | Documentation/learning guidance adapted by the author. | The author reviewed the guide against the codebase. | `docs/Guide_comprehension_TaskFlow_FR.pdf`. |
| 2026-10-26 | OpenAI Codex | CI security triage | Interpret the Trivy failure and outline safe remediation steps. | Guidance only; security remediation still requires author implementation and verification. | CI log reviewed; no security finding is marked resolved without a successful rerun. | `SECURITY.md`, `docs/ASSESSMENT_TODO.md`. |
| 2026-10-26 | OpenAI Codex | Security remediation | Replace the vulnerable JWT package, upgrade compatible API dependencies, update the base image, and retain a meaningful CI gate. | Code/configuration changes adapted by the author. | Backend tests, Ruff, and `pip check` passed locally; CI audit and Trivy rerun remain required before merge. | `backend/requirements.txt`, `backend/app/core/security.py`, `backend/app/api/deps.py`, `backend/Dockerfile`, `.github/workflows/ci.yml`. |


