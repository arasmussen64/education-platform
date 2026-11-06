# Changelog

All notable changes to this project are documented here.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versioning: [Semantic Versioning](https://semver.org/) once there's a release.

## [Unreleased]

### Added (mistakes come back)

- **Mistakes to revisit** on the Today page ([ADR-0011](docs/decisions/0011-mistakes-come-back.md), now accepted). The owner asked for this after missing a question in their first lesson:
  - a skill you missed comes back the next day, as a *different* question on the same skill;
  - after a right answer it returns 3 days later, and right answers on 2 different days relearn it;
  - "Coming back later" lists what's due on other days.
- It's worked out from the event log, so misses from before this feature count too.
- Answers on Today are saved as reviews, with hints off.
- Code exercises count as missed only if they never passed that day. Failing Checks while working something out aren't mistakes.
- The Today page now loads only when visited, like the topic pages.

### Added (the second lesson)

- **Values and types** (`py.values-and-types`), ready to learn:
  - **Learn:** CS50P Lecture 0 from 59:32 to 1:07:58: what an integer is, and why a calculator prints "12" for 1 + 2. A float clip and the Python tutorial are linked as more resources.
  - **Practice:** a worked example with `type()`, three questions (one mixes in topic 1: `print` hides quotes), a fill-in and a write exercise.
  - **Prove it:** a type report (its hidden tests also check that `type()` is used), a receipt with one crashing and one silent type bug, and explaining the calculator bug.
  - **Review pool:** three items. Two skills: `identify-types` and `plus-by-type`.
- The loading test now checks every ready topic automatically.

### Added (skills)

- [ADR-0011](docs/decisions/0011-mistakes-come-back.md) (proposed): a missed question will come back as a different question on the same skill, until it's right on 2 different days. The owner asked for it, and chose fresh questions over repeats.
- Topics declare their **skills**, and every question and exercise names the skills it tests. The content checker requires every graded item to name a skill, and every skill to have at least 2 questions that can come back after a miss. Unknown skill names are caught as typos.
- Programs and print is labeled with 4 skills, and has a new review question on printing with commas.

### Fixed

- A video clip looked as long as the whole lecture, because YouTube's player always shows the full video's length (a 9-minute clip read as 1 hour 45 minutes). The page now says above the video which part to watch, how long it is, and that it stops by itself. The topic's time estimate now says it covers the whole topic. Reported by the owner.

### Added (the first lesson)

- **Programs and print** (`py.programs-and-print`), the first real topic, ready to learn:
  - **Learn:** a 9.5-minute segment of CS50P Lecture 0 (CC BY-NC-SA 4.0), with an intro on what to watch for and a recap.
  - **Practice:** a worked example, three questions (one on reading an error), a fill-in exercise and a write exercise.
  - **Prove it:** build a banner from scratch, fix a program with two bugs, and explain why an error happened.
  - **Review pool:** three items for later reviews.
  The checker runs 22 programs for it, including 12 known-wrong answers that must fail.
- A practice-hours tracker idea is on the roadmap (Phase 2).

### Changed

- Multiple-choice answers are Markdown, so they can show code.
- Code and output boxes stand out from their cards in dark mode.
- The content definition of done: while the owner is the only learner, their first pass happens on the live site.

### Added (saving progress)

- Everything a signed-in learner does on a topic page is saved to the append-only event log (F6): lesson views, answers, runs, checks and hints. Each event records the item's revision, how long the attempt took, the hints used, the study session, and the commit the app was built from.
- Events go into an outbox on the device first, then to the server in batches. Retries are always safe, because the server ignores an event it already has. Offline, nothing is lost: the app retries with growing waits and again as soon as the browser is back online.
- An event the server refuses is set aside on the device, so it can't block the others.
- A "Not saved yet" badge in the header while work is waiting on this device.
- Topic pages tell signed-out visitors that their answers won't be saved.

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
