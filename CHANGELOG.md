# Changelog

All notable changes to this project are documented here.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versioning: [Semantic Versioning](https://semver.org/) once there's a release.

## [Unreleased]

### Added (deployment)

- Cloudflare deployment config (`web/wrangler.jsonc`): the built app is served as static files, with unknown addresses falling back to the app so its pages work. Wrangler's usage statistics are turned off.
- Setup steps for connecting the repo to Cloudflare and linking the Supabase project.

### Added (database)

- Local Supabase in Docker (`supabase/`), with the Supabase CLI pinned in a root `package.json` and `db:*` scripts.
- The first migration: learner profiles, created automatically at sign-up, and the append-only event log. Row-level security on both. Learners can only add and read their own events and can't grant themselves AI access; the database refuses to edit or delete events, even for admins.
- 18 database tests (pgTAP) and a **Database** CI job that starts a throwaway database, checks the SQL, and runs them.

### Changed

- Run now asks for input like a terminal. When a program calls `input()`, you type the answer right after the prompt and press Enter; there's no separate input box any more. Re-runs use the same random seed, so random choices stay put.

### Fixed

- No more console warning when the app first opens on a page that loads on demand (it now shows "Loading…").
- Password managers no longer pop up on the program-input field. It's now an editable piece of text (`role="textbox"`) instead of an `<input>`, because NordPass ignored the opt-out markers the first fix relied on.

### Added

- Python in the browser: Pyodide runs learner code in a background Web Worker, with a CodeMirror editor, Run and Check buttons, and a 5-second time limit. A temporary Playground page lets you try it.
- The 14 harness scenarios also run under real Pyodide in the web tests, so the browser and CI are checked to give identical results.
- The Python test harness (`harness/`), shared by the browser and CI. It has 14 scenarios that both runtimes must match, and a Python CI job (uv, ruff, pytest) on Python 3.14.
- ADR-0010: a local Supabase in Docker for development, and one cloud project for real use.
- A setup guide for the owner's computer and accounts (`docs/setup.md`).
- Web app scaffold in `web/`: Vite, React, TypeScript, Tailwind CSS and React Router, with placeholder Today, Map and Topic pages. The product name is kept in a single setting.
- CI on GitHub Actions: formatting, lint, type-check, tests and build on every pull request and every push to `main`.
- v1 spec, data model and Python Foundations track plan, in `docs/specs/`.
- ADR-0008 (append-only event log) and ADR-0009 (per-topic reviews, graded automatically), both accepted.
- Project documentation: vision, learning-science principles, roadmap, competitor research, devlog.
- Decision records ADR-0001 to ADR-0007: decision process, mastery and gating, AI roles, content model, free hosting, working name, tech stack.
- `CLAUDE.md` with the development process and the product rules that constrain code.
- Repository config: `.gitignore`, `.gitattributes` (LF line endings), `.editorconfig`.

### Changed

- Data model: the content validator uses the harness's own test runner instead of pytest.
- Process: Claude merges its own pull requests once CI passes, under standing permission from the owner.
- Roadmap: the "prove it" checks, topic states and gating move from Phase 2 into Phase 1.
