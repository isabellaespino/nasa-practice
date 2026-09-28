# Workflow

Work in this loop. Never skip a step.

- **study**: write a timestamped markdown doc in doc/study/ analyzing a request. Feasibility and tradeoffs. No code.
- **plan**: write a timestamped markdown checklist in doc/plan/ of concrete steps to achieve an outcome. Usually derived from a study.
- **execute plan**: carry out an existing plan doc. Do this on a Git branch off main.
- **rendezvous**: merge the branch back to main and confirm the codebase runs.
- **sync docs**: update doc/wiki/, the living manual of the codebase, to match reality.

# Rules

- Scope every change to one conventional commit (feat: fix: chore: build:).
- Stack: Django, SQLite, Django built-in auth and admin, server-rendered templates. No frontend framework.
- Do not add dependencies without saying why in a study first.
- Declare every dependency in requirements.txt.
- Maintain a .gitignore. Never commit db.sqlite3, .venv, or .env.
- Secrets and API keys live in .env only. Keep a committed .env.example listing required variables with no values.
- Never reset or reseed db.sqlite3. Verify with Django's test framework or a throwaway test database.
- Anyone cloning this repo must be able to set it up from the files alone: README with setup steps, and seed data via a fixture or management command so the app is not empty.
- Every page must be reachable through navigation links, not only by typing URLs.
- When running the server, bind to 0.0.0.0.
