# TaskFlow release and submission checklist

This is an execution checklist, not a record of a completed release. As checked locally on 2026-10-26: PR #1 and PR #2 are merged into `develop`; `main` still points to the initial MySQL foundation; no local `v*` tags exist; Phase 7 docs are uncommitted. Recheck GitHub before acting because remote state can change.

## 1. Finish and review the branches

- [ ] Restore or deliberately recreate `AI_USAGE.md` and `AI_USAGE_LOG.md` if they were removed intentionally; the assessment requires them and README currently links to them. Then commit the Phase 7 docs on `feature/docs` and push the branch. Keep the unrelated untracked `backend/app/schemas/errors.py` out of the commit unless you deliberately review and include it.
- [ ] Open a PR from `feature/ci` into `develop`. Review the first GitHub CI run: backend tests and MySQL migration, frontend checks, both image builds/Trivy scans, pip/npm audits, and Gitleaks. Fix findings; do not mark skipped or failed scans as passing.
- [ ] Open a PR from `feature/docs` into `develop` after CI changes are merged, or update that branch from `develop` first. Check rendered Markdown links and commands in GitHub.
- [ ] Confirm the earlier meaningful backend PRs (#1 and #2) and the new PR links in the submission. Ask for review where available; merge only when required checks pass. GitHub branch protection can require those checks on `develop` and `main` [if configured](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches).
- [ ] Open the final PR from `develop` into `main`. Review the full diff and a fresh CI result for the merge candidate. Do not push a release tag until `main` contains the intended source and workflows.

PowerShell checks before the final PR or tag:

```powershell
git status --short --branch
git fetch origin --prune --tags
git log --oneline --decorate -8 origin/develop
git log --oneline --decorate -8 origin/main
git tag --list 'v*'
git diff origin/main...origin/develop --stat
```

These commands inspect state only. The GitHub PR page is the source of truth for current review and check status; local refs may be stale until `git fetch`.

## 2. Verify the release candidate

- [ ] Confirm `.env` and any real credential files are ignored; inspect the staged diff before every commit. Do not paste secret values into screenshots, video, CI summaries, or email.
- [ ] Run the exact commands in [TESTING.md](../TESTING.md), including a Docker Compose health check and smoke test. Note that smoke tests create data in MySQL.
- [ ] Check the GitHub Actions CI run on the final PR. Record its URL and each job result in [TESTING.md](../TESTING.md). A local pass does not substitute for the remote MySQL migration, `pip-audit`, Trivy, or Gitleaks jobs.
- [ ] Resolve every security finding or document a justified, reviewed exception; do not change scan exit codes to make a release green.
- [ ] Confirm README setup, Swagger URL, `.env.example`, and deployment/rollback notes match the final code.
- [ ] Confirm the release tag is new and points to the reviewed `main` commit.

## 3. Tag and publish

`v0.1.0` is the requested first working backend+DB milestone. Select a real commit that demonstrated that state. `98a2c0f` is the local full-Compose/smoke commit, but tag it only after checking it is in the merged history and is the milestone you want to claim. Do **not** label the initial MySQL-only foundation as a working backend. An older tag may not contain the release workflow, so do not expect `v0.1.0` to publish GHCR images automatically.

```powershell
git fetch origin --tags
git merge-base --is-ancestor 98a2c0f origin/main
# Proceed only if the previous command exits 0 and you verified that commit.
git tag -a v0.1.0 98a2c0f -m "TaskFlow first working Compose milestone"
git push origin v0.1.0
```

If a squash merge changed commit identity, choose and verify the actual merged milestone commit instead. Do not force-move a published tag. For the final release, after the `develop` -> `main` PR is merged and the final commit is checked:

```powershell
git switch main
git pull --ff-only origin main
git status --short --branch
git tag --list v1.0.0
# Stop if v1.0.0 already exists or the worktree is not clean.
git tag -a v1.0.0 HEAD -m "TaskFlow 1.0.0"
git push origin v1.0.0
```

The tag triggers [release.yml](../.github/workflows/release.yml): reusable CI must pass before both GHCR images are pushed, then the GitHub Release is created. Check the Actions run, package pages for `taskflow-backend:v1.0.0` and `taskflow-frontend:v1.0.0`, and the [GitHub Releases page](https://github.com/nouraboussaoud/taskflow/releases). Do not manually create a duplicate Release or publish images if the gated workflow fails. GitHub also supports [creating a Release from an existing tag](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository), but use that only after investigating a failed automated release and retaining the required verification.

## 4. Simulate staging and record evidence

- [ ] After `staging.yml` is on the default branch (`main`), open **Actions → Staging simulation → Run workflow**, enter `v1.0.0`, and run it. GitHub requires a `workflow_dispatch` workflow to exist on the default branch before it can be manually triggered [per its docs](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow).
- [ ] Save the successful run URL and summary: pulled versioned images, Compose config valid, three healthy services, HTTP smoke test passed.
- [ ] If packages are private, confirm the workflow token has package read access. If pulling fails, fix permissions/visibility rather than adding credentials to the repo.
- [ ] Update [TESTING.md](../TESTING.md) and [SECURITY.md](../SECURITY.md) with actual results, findings, fixes, and links. Commit those evidence updates through a PR if the release record must include them.

The staging workflow runs on a temporary GitHub runner and does not deploy a server.

## 5. Rollback plan

If the release is faulty, stop promoting it. Make a corrective commit with `git revert <bad-commit>` on a new branch and PR it through checks. If a host was deployed manually, change both image references back to the previous verified version and restart with `docker compose ... up -d --no-build --wait`, then rerun health/smoke checks. Confirm database migration compatibility first; reverting images does **not** revert the schema or data. See [CLOUD_DEPLOYMENT.md](../CLOUD_DEPLOYMENT.md). Never use a force push or delete the MySQL volume as a rollback shortcut.

## 6. Submission email template

Recipient was not supplied; fill it in from the assessment instructions. Send only after checking every link and permission. Replace brackets with actual facts; omit unavailable links rather than claiming completion.

```text
To: [assessment recipient]
Subject: Qartis Tech assessment submission - TaskFlow - [your name]

Hello [name/team],

I am submitting TaskFlow for the Junior Cloud, DevOps & Full-Stack Engineer assessment.

Repository: https://github.com/nouraboussaoud/taskflow
Final PR (develop -> main): [PR URL]
Release v1.0.0: [Release URL, only after it exists]
CI run: [successful run URL]
Staging simulation: [successful run URL]
Demo video: [viewable video URL]

The README covers local startup. Architecture, testing evidence, security findings,
the Linux deployment plan, and AI usage are linked there. The application is a
local Docker Compose MVP; the staging workflow is a runner simulation, not a
hosted production deployment. [State any remaining scan or feature limitations.]

Thank you for reviewing my submission.
[Your name]
```

Before sending, test every URL in a private browser window, make the video accessible to the reviewer, and confirm there are no real credentials in the repo or recording.

## 7. Demo video script (about 4-5 minutes)

| Time | Show | Say |
| --- | --- | --- |
| 0:00-0:35 | Repo README and architecture diagram | “TaskFlow is a React/FastAPI/MySQL project manager. Compose runs three services; MySQL is private to the app network and persists in a named volume.” |
| 0:35-1:05 | `docker compose ps`, browser `/health`, Swagger `/docs` | “Health checks the database, and Swagger documents the `/api/v1` endpoints. The backend applies Alembic migrations at startup.” |
| 1:05-2:20 | Register/login, create a project and tasks, change status/priority, search/filter | “A user can manage their own projects and tasks. The API checks ownership on every protected resource.” Use only disposable demo credentials. |
| 2:20-2:50 | Dashboard and responsive browser width | “The dashboard counts statuses, priorities, and overdue work; the UI includes loading/error states.” |
| 2:50-3:35 | Test commands or recorded passing terminal output; CI PR run | “Pytest covers auth, CRUD, validation, and cross-user isolation. Frontend Vitest covers login. CI adds MySQL migration, audits, image scans, and secret scanning.” Show only results that actually passed. |
| 3:35-4:20 | GHCR Release and staging run, if successful; otherwise state pending | “A version tag triggers tests before publishing images. Staging pulls those images on a temporary runner and smoke-tests them; it is not a server deployment.” |
| 4:20-4:50 | Security/deployment docs and closing | “The docs record remaining risks: localStorage JWTs, no rate limiting or backups, and a manual Ubuntu/Nginx/TLS deployment plan.” |

Record a fresh demonstration after final fixes. Hide `.env`, tokens, browser storage, passwords, and any personal information. Do not display fabricated CI or release evidence.

## AI usage log row for this phase

Paste this into `AI_USAGE_LOG.md` after that file is restored, then replace the pending commit/PR field:

```markdown
| 2026-10-26 | OpenAI Codex; model ID not recorded | Release handoff (Phase 8) | Create PR/tag/Release checklist, submission email template, and demo script. | Adapted generated guidance | Cross-checked local branches/tags and workflow triggers; no release or email sent. | Commit/PR pending |
```
