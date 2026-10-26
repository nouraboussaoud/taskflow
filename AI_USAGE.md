# AI usage disclosure

## Declaration

AI-assisted tooling was used while building TaskFlow. The author reviewed, adapted, tested, and remains responsible for every submitted change. AI assistance did not replace the author's responsibility to understand, explain, modify, and debug the application.

## Tools used

- OpenAI Codex: code review guidance, debugging guidance, documentation drafting, Docker and CI troubleshooting, and learning support.

## Areas where assistance was used

- Reviewing the FastAPI, React/Vite, Docker Compose, GitHub Actions, and documentation structure against the assessment requirements.
- Explaining the architecture, authentication/authorization flow, Docker networking, and framework choices in terms the author can defend in a technical review.
- Diagnosing Docker build/startup problems, including the frontend lockfile mismatch and Linux shell-script line-ending issue.
- Drafting or improving documentation templates, test/checklist guidance, and the French study guide.

## Verification performed by the author

- Ran the application locally with Docker Compose and verified the user workflow.
- Reviewed generated code and configuration before retaining it.
- Reviewed the verification commands in `TESTING.md`; the author must run every required command and record only the results actually observed before submission.
- Reviewed CI failures and recorded the required remediation work in `SECURITY.md` and `docs/ASSESSMENT_TODO.md`.

## Important limits

- No real credentials, tokens, database dumps, or confidential information were intentionally shared with AI tools.
- This disclosure must be updated if additional significant AI assistance is used before submission.
- The author will be able to explain the final codebase and perform a small code change without AI during the follow-up review.
