# CLAUDE.md

Guidance for Claude Code in this repository. Keep this file short; details live in `docs/`.

## What this is

**Switchback** (working name, may change) is an adaptive computer-science learning platform covering CS from total beginner to principal engineer. Learners can't tick topics off themselves: every topic is taught, must be *proven* by building with it, and is kept fresh with spaced review. First learning track: CS foundations → ML engineering.

- Concept: [docs/vision.md](docs/vision.md)
- Plan and current phase: [docs/roadmap.md](docs/roadmap.md)
- v1 spec: [docs/specs/v1.md](docs/specs/v1.md), with the [data model](docs/specs/data-model.md) and the [first track](docs/specs/python-foundations.md)
- Decisions (ADRs): [docs/decisions/](docs/decisions/)
- Methods behind the features: [docs/learning-science.md](docs/learning-science.md)
- Session history: [docs/devlog.md](docs/devlog.md)
- Owner's machine and accounts: [docs/setup.md](docs/setup.md)

**Current phase:** 1, Milestone A (walking skeleton). The web app lives in `web/`.

**Stack** ([ADR-0007](docs/decisions/0007-tech-stack.md)): TypeScript + React + Vite web app served as static files from Cloudflare; Supabase (Postgres, Auth, Edge Functions as the Claude API proxy); learners' Python runs in the browser via Pyodide in a Web Worker; Python (uv, pytest, ruff) for content tooling and ML; GitHub Actions for CI.

**At the start of a session,** read the latest devlog entry and the roadmap's current phase.

## Working with the owner

- The owner is early in their coding journey and is the platform's first learner. Building the platform is part of how they learn.
- Explain what you're doing and why, in plain language. Define jargon the first time you use it.
- Prefer simple, readable code over clever code: small files, clear names, comments that explain *why*.
- Teach as you go. When a task would make a good exercise, offer to let the owner write it (with hints) instead of writing it yourself.
- Keep the owner able to explain the code. Every pull request includes a short plain-language summary, and you offer an occasional explain-it-back question. These never block merging.
- Ask before anything hard to undo or that costs money: paid services, deleting data, force-pushing, making things public.
- The owner may have a dev server running. After changing `vite.config.ts` or installing packages, tell them to restart it (Ctrl+C, then `npm run dev`), because a running server can get stuck half-updated. Never stop a process you didn't start.

## Development process

- **Plan first.** Check the roadmap and relevant ADRs before non-trivial work. Significant or hard-to-reverse choices get an ADR in `docs/decisions/` (status *Proposed* until the owner accepts it).
- **Branches.** `main` must always work. Make each change on a short-lived branch (`feat/…`, `fix/…`, `docs/…`, `chore/…`) and merge it into `main` through a pull request.
- **Merging.** The owner gave standing permission (2026-11-05) for Claude to merge its own pull requests once CI passes. Use squash merges and delete the branch. Everything in "Ask before" above still needs the owner.
- **Environments** ([ADR-0010](docs/decisions/0010-environments.md)). Development and tests use a local Supabase running in Docker. The single cloud Supabase project is for real learning only: never point a dev server, test or script at it. Database changes reach it only as migrations, after they've passed locally and in CI.
- **Commits.** [Conventional Commits](https://www.conventionalcommits.org/): `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`. Small and focused.
- **Definition of done** for every change:
  - tests added or updated, and passing (once code exists)
  - `CHANGELOG.md` updated under *Unreleased*
  - docs updated if behavior, setup or a decision changed
  - a `docs/devlog.md` entry for the session: what changed, what was decided, what's next
- **Secrets never get committed.** Keys go in `.env` (gitignored); keep `.env.example` with placeholder names.
- **Free tiers only** ([ADR-0005](docs/decisions/0005-free-hosting-first.md)). Never add a service that bills without asking. The one paid exception is the Claude API, capped at $10 a month to start (v1 spec).

## Product rules that constrain code

- The product name lives in **one** config constant. Never hard-code "Switchback" in components, URLs, package names or database names ([ADR-0006](docs/decisions/0006-working-name.md)).
- Mastery = blank-editor challenge + explain it back + debug unfamiliar code + survives a delayed review ([ADR-0002](docs/decisions/0002-mastery-and-gating.md)). Don't weaken this without a new ADR.
- The AI tutor gives hints, never full solutions, and is switched off during "prove it" checks ([ADR-0003](docs/decisions/0003-ai-roles-and-guardrails.md)).
- Every exercise must be machine-verifiable: its reference solution passes the tests and known-wrong solutions fail ([ADR-0004](docs/decisions/0004-content-model.md)).
- Record every external resource's license. Never copy text from sources that don't allow it ([ADR-0004](docs/decisions/0004-content-model.md)).
- The Python harness (`harness/`) runs learner code in both the browser and CI. Its scenario results are a contract both runtimes must match; read [harness/README.md](harness/README.md) before changing it.
- Learner answer and review logs are future ML training data. Append only: never delete or rewrite them.
- For Claude API work, look up current model IDs and pricing in the official docs instead of relying on memory.

## Commands

Web app: run these inside `web/`. Details are in [web/README.md](web/README.md).

- `npm install` installs dependencies.
- `npm run dev` starts the app at http://localhost:5173.
- `npm run format:check`, `npm run lint`, `npm run typecheck`, `npm test` and `npm run build` are the checks CI runs on every pull request. Run all of them before pushing.

Python: run these from the repository root. uv manages Python 3.14 and the tools.

- `python -m uv sync` installs the Python tools.
- `python -m uv run pytest` runs the harness tests.
- `python -m uv run ruff format` and `python -m uv run ruff check` format and lint Python code.

Database: run these from the repository root, with Docker Desktop running. Details are in [supabase/README.md](supabase/README.md).

- `npm install` installs the Supabase CLI. `npm run db:start` and `npm run db:stop` start and stop the local Supabase.
- `npm run db:reset` rebuilds the local database from the migrations.
- `npm run db:test` and `npm run db:lint` run the database tests and check the SQL.
- `npx supabase migration new <name>` starts a schema change. Never edit a migration that has reached production. After a migration, run `npm run db:types`.
- Signing in locally: the dev server uses email links. They land in the local test inbox (Mailpit) at http://127.0.0.1:54324. The live site uses GitHub.

Content: run this from the repository root. Details are in [content/README.md](content/README.md).

- `python -m uv run python tools/validate_content.py` checks every topic and runs every exercise (`--no-run` skips running code). CI runs it on every pull request, and content must pass it before being marked `ready`.

## Environment

Windows 11 (Git Bash or PowerShell), Node 24, npm 11, Python 3.12, git, GitHub CLI. `.gitattributes` normalizes line endings to LF.
