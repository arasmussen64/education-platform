# Devlog

A dated log of each working session: what changed, what was decided, what's next. Newest first.

## 2026-11-05: Python runs in the browser

**Done**

- Built the browser side of the Python runner:
  - Pyodide 314.0.7 runs in a Web Worker, loaded from the jsDelivr CDN.
  - `PythonRunner` queues requests and replaces the worker when code runs past 5 seconds.
  - A CodeMirror editor with Run and Check, on a temporary Playground page.
- The 14 harness scenarios now also run under real Pyodide (in Node) in the web tests. They match CPython exactly, tracebacks included.
- Checked the production build in a real browser:
  - Pyodide loaded in the background.
  - Run echoed input like a terminal.
  - Check failed, then passed after fixing the code.
  - An infinite loop was stopped after 5.1 seconds while the page stayed responsive.
  - The next run worked 0.1 seconds later.
  - No console errors.
- Made the Playground load on demand: the main bundle dropped from 786 KB to 320 KB.

**Fixed along the way**

- The status message now uses an `<output>` element, as the accessibility lint rule suggested.
- The summary now reads naturally for a single check ("The check passed!" instead of "All 1 checks passed!").
- Tests get their own TypeScript settings with Node types, so app code can't use Node APIs by accident.

**Next**

- The content pipeline and validator, then Module 1 content.
- Local Supabase once Docker Desktop is installed ([setup](setup.md)).

## 2026-11-05: Python test harness

**Done**

- Wrote the shared Python harness (`harness/`): `checks.run()` for tests, the Run and Check logic, and beginner-friendly error messages that only show the learner's own file.
- Added 14 scenarios with expected results I reviewed by hand, plus unit tests. A new CI job runs them with uv, pytest and ruff.
- Installed uv for this user, and Python 3.14 through it.

**Decided**

- Pyodide has a new version scheme (314.0.7 bundles Python 3.14), so the Python tooling targets 3.14.
- The content validator will use the harness's own test runner, not pytest. pytest rewrites `assert` statements in files named `test_*.py`, which changed the messages. Two scenarios that failed only under pytest exposed this.

**Next**

- The browser side: Pyodide in a Web Worker, the editor, Run and Check, and the same scenarios under Pyodide.

## 2026-11-05: Process and environment decisions

**Decided**

- The owner gave standing permission for Claude to merge its own pull requests once CI passes. Explain-it-back questions continue, but they never block merging.
- Supabase's second free project slot is already in use, so the platform gets one cloud project, for real learning only. Development runs a local Supabase in Docker Desktop ([ADR-0010](decisions/0010-environments.md)). The owner chose this over sharing the cloud project with a test account.

**Done**

- Merged the web app scaffold (PR #2).
- Wrote ADR-0010 and a [setup guide](setup.md) for the owner's computer and accounts.

**Next**

- The owner installs Docker Desktop, creates the Supabase project, and creates a Cloudflare account ([setup](setup.md)).
- The Python runner in the browser.

## 2026-11-05: Milestone A starts with the web app scaffold and CI

**Done**

- Merged the v1 spec (PR #1).
- Scaffolded the web app in `web/` with create-vite 9: Vite 8, React 19, TypeScript 7, React Router 8, Tailwind CSS 4, Vitest 5, Oxlint (with accessibility rules) and Prettier.
- Added placeholder pages (Today, the topic map, a topic, and "not found") inside a shared layout.
- The product name lives only in `web/src/config.ts`. A small Vite plugin puts it in the page title (ADR-0006).
- Wrote 5 route tests. Added CI on GitHub Actions: formatting, lint, type-check, tests and build.

**Notes**

- Several tools are newer than expected (React Router 8, Vitest 5, TypeScript 7), so I checked what they export before writing code against them.
- create-vite now defaults to Oxlint instead of ESLint. I kept the default.

**Next**

- The Python runner in the browser: Pyodide in a Web Worker, plus the `checks` test helper.
- The owner creates free Supabase and Cloudflare accounts.

## 2026-11-05: v1 spec

**Done**

- Wrote the [v1 spec](specs/v1.md): 16 features with acceptance criteria, four milestones (A–D), non-functional requirements, and a content definition of done.
- Wrote the [data model](specs/data-model.md): content file formats, the `checks` test helper, the Postgres tables, and the exact rules for topic states.
- Planned the [Python Foundations track](specs/python-foundations.md): 30 topics in 6 modules, each ending with a checkpoint, mostly built around CS50P lectures.
- Proposed ADR-0008 (append-only event log) and ADR-0009 (per-topic reviews, graded automatically).

**Decided** (the owner approved the spec pull request)

- The "prove it" checks, topic states and gating move from Phase 2 into Phase 1. They reuse the exercise engine, and v1 shouldn't call anything Learned without proof.
- ADR-0008 and ADR-0009 accepted.
- The topic list is approved as written.
- AI budget cap: $10 a month to start.

**Next**

- Milestone A: scaffold the app and CI, then the Python runner, the content pipeline, Supabase, the deploy, and Module 1 content.

## 2026-11-05: From idea to project setup

**Done**

- Researched Brilliant, roadmap.sh and Math Academy ([competitors](research/competitors.md)).
- Pinned down the concept through a Q&A ([vision](vision.md)):
  - Adaptive, from total beginner to principal engineer. First track: CS foundations → ML engineering.
  - Core promise: you can *apply* it, not just recognize it.
  - Mastery needs all four proofs: blank editor, explain it back, debug unfamiliar code, delayed review.
  - Gated, with test-out.
  - AI as hint-only tutor, reviewer, practice generator, and an "earn the AI" track.
  - Content: curated free resources plus AI-written supporting material; practice owned by the platform.
  - Free and personal-use first; free hosting; owner full time, learning in the mornings and building in the afternoons.
- Picked the working name **Switchback** (may change).
- Set up the repository: CLAUDE.md, README, CHANGELOG, ADR-0001 to ADR-0007, git config files.
- Backed it up to a private GitHub repo, `education-platform`.

**Decided:** ADR-0001 to ADR-0007 accepted, including the tech stack (ADR-0007): a TypeScript/React app on Cloudflare, Supabase, Pyodide, and Python for tooling and ML. It replaced the earlier "Python backend" idea because free Python hosting sleeps when idle.

**Next**

- Write the v1 spec: feature list, data model, the first 30 Python topics.
- Scaffold the app, CI and first deploy.
