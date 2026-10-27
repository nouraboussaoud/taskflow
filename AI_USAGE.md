# AI Usage Disclosure

I used an AI assistant while building TaskFlow, as the assessment allows. This file says which tool I used and for what. The detailed, dated entries are in [AI_USAGE_LOG.md](AI_USAGE_LOG.md).

AI helped me work faster and learn, but I reviewed, tested and adapted what I kept, and I take responsibility for all the code in this repository. I can explain it, change it and debug it myself.

## Tool used

- **OpenAI Codex**: code review, debugging help, drafting documentation, Docker and CI troubleshooting, and explanations of concepts I wanted to understand.

## Where AI helped

- **Review:** checking my FastAPI, React/Vite, Docker Compose, GitHub Actions and documentation structure against the assessment requirements.
- **Debugging:** finding the cause of two Docker problems, a frontend lockfile mismatch and Windows line endings (CRLF) breaking a Linux shell script.
- **Documentation:** drafting and improving the Markdown files and the test checklist, plus a French study guide for my own revision.

## What I did myself

- Ran the application locally with Docker Compose and tested the full user workflow (register, log in, create projects and tasks).
- Read every suggestion before keeping it, and changed what did not fit my project or what I did not understand.
- Ran the commands listed in `TESTING.md` and recorded only the results I actually got.
- Investigated the CI failures and recorded the fixes and remaining work in `SECURITY.md` and `docs/ASSESSMENT_TODO.md`.

## Limits

- I did not knowingly share real credentials, tokens, database dumps or confidential data with the AI tool. My `.env` stays out of Git and out of prompts.
- AI suggestions were sometimes wrong or did not match my code, so I checked them against the running application and the tests.
- If I use AI significantly again before submitting, I will update this file and the log.
- In the follow-up review I will be able to explain the codebase and make a small change without AI.
