# Changelog

All notable changes to this project are documented here.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versioning: [Semantic Versioning](https://semver.org/) once there's a release.

## [Unreleased]

### Added (topic pages)

- The app reads `content/` while it's built: YAML becomes data, lessons are MDX, and exercise code is loaded as text. A topic's lesson and exercises download only when its page opens.
- **Topic pages**, in three parts:
  - **Learn:** objectives, then the lesson's intro, the main resource (a privacy-enhanced YouTube embed, cut to its start and end times, or a link) and the recap, with the source and license. Other resources are listed after it.
  - **Practice**, in order: a worked example with labeled steps to run; multiple-choice and predict-the-output questions with instant feedback; fill-in and write exercises with hints one at a time. The reference solution appears only after a pass.
  - **Prove it:** the build and debug exercises (hidden test details, no hints) and the explain prompt. Grading the explanation, and counting the proof toward mastery, arrive in Milestone B.
- Topics that aren't written yet show their outline and say so. `draft` topics show only on the dev server.
- **The map** lists every module and topic, each marked Ready, Draft or Coming soon, with an icon and a word.
- Exercises can set their own time limit (`time_limit_ms`).
- If a page fails to load, an error page with a Reload button appears inside the layout. The usual cause is the app being updated while it's open.
- The content checker requires a ready lesson to place its main resource (`<Resource index={0} />`), and no other.

### Added (content)

- `content/`: the Python Foundations track and all 36 topics from the approved list as `planned` outlines, with their prerequisites. A `status` field (`planned`, `draft`, `ready`) tracks each topic's progress.
- The content validator (`tools/validate_content.py`). It checks file formats, the topic map (tracks, prerequisites, no cycles), and the definition of done for `ready` topics. It runs every exercise through the shared harness: reference solutions must pass, starters and known-wrong solutions must fail, and predict-the-output items must print what they claim. 14 tests prove it catches each kind of mistake.
- `harness/cli.py`: runs one folder through the harness in a fresh process. Used by the validator and the scenario tests.
- A **Content** CI job.

### Added (sign-in)

- Sign-in with GitHub on the live site, and email links in local development (they land in the local test inbox). The header shows who's signed in, with Sign out.
- The Supabase client, with settings for local and production, and TypeScript types generated from the database (`npm run db:types`).

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

- Cloudflare's pull-request preview builds now deploy: `wrangler preview` needed a `previews` block in `web/wrangler.jsonc`.
- Cloudflare builds no longer spend about 6 minutes installing Python. The Python version is pinned in `pyproject.toml` instead of a `.python-version` file, which Cloudflare's build reacted to.
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
