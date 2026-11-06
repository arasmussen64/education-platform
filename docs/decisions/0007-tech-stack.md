# ADR-0007: Tech stack

- **Status:** Accepted
- **Date:** 2026-11-05

## Context

- Free hosting only (ADR-0005). Always-on servers are the hardest thing to get for free; static files and code that runs in the browser are the easiest.
- Learners write and run Python. Running it in their own browser costs nothing and avoids running untrusted code on a server.
- The owner is learning Python first and will build v1 mostly with AI help, taking over more of the code over time.
- Answer and review logs are precious (they're the training data for the owner's ML capstone), so they must be stored durably, not just in one browser.
- It should work across devices and be ready for more users later.

## Decision

| Part | Choice | Why |
|---|---|---|
| Web app | **TypeScript + React + Vite** (single-page app), Tailwind CSS | Mainstream and well documented; deploys as static files anywhere |
| Code editor | **CodeMirror 6** | Lightweight and works on mobile |
| Lessons | **MDX** (Markdown plus interactive components) in `content/` | Lessons are files in git; interactive pieces drop right in |
| Running Python | **Pyodide** (Python compiled to WebAssembly) in a **Web Worker** | Free, runs in the learner's browser, sandboxed |
| Database and login | **Supabase** free tier: Postgres, Auth, Row Level Security | Real SQL, login included, works across devices; it's plain Postgres, so it's portable |
| AI proxy | **Supabase Edge Function** calling the **Claude API** | Keeps the key secret; enforces the tutor rules and a spending cap |
| Review scheduling | **FSRS** via the open-source `ts-fsrs` library | Proven algorithm; the owner later fits personal parameters in Python |
| Hosting | **Cloudflare Workers with static assets** (Cloudflare now recommends this over Pages for new projects) | Static requests are free and unmetered |
| Python tooling | `tools/`: a content validator that runs reference solutions against tests in CI, using **uv**, **pytest** and **ruff** | Real Python work for the owner from week one |
| ML work (later) | `ml/`: Python notebooks and scripts, trained offline on exported logs | The standard industry split: train in Python, ship the resulting parameters to the app |
| Tests and CI | **Vitest** (web), **pytest** (Python), **Playwright** (later); **GitHub Actions** | Free at this scale |

### Proposed repository layout

```text
education-platform/
├── CLAUDE.md, README.md, CHANGELOG.md
├── docs/        vision, learning science, roadmap, decisions, research, devlog
├── web/         the React app
├── content/     topic graph, lessons, exercises and their tests
├── tools/       Python content validator and generators
├── supabase/    database migrations and edge functions
└── ml/          later: scheduler fitting, knowledge tracing
```

## Alternatives considered

- **Python backend (FastAPI or Django).** This was the first suggestion, because it would keep the whole app in the language the owner is learning. Set aside for now: free Python hosting either sleeps when idle (it can take up to a minute to wake) or is very limited. Worth revisiting once hosting has a budget.
- **Next.js on Vercel.** Popular, but Vercel's free Hobby plan is for personal, non-commercial use only, and Next.js's split between server and browser code is harder for a beginner to reason about.
- **Browser-only storage (IndexedDB).** Costs nothing, but data is tied to one browser and easy to lose. That's unacceptable for the review logs.

## Consequences

- The owner will pick up some TypeScript. Daily Python practice comes from the exercises, the content tooling and, later, all the ML work.
- Infinite loops in learner code are handled by killing and restarting the Web Worker. This avoids the special cross-origin headers that Pyodide's interrupt feature needs, which can break embedded YouTube videos.
- Hidden tests are shipped to the browser, so a determined learner could read them. That's acceptable for personal use; revisit before a public launch.
- Supabase's free tier pauses a project after a week without activity. That's fine with daily use, but a backup and export routine is still needed.
- Free-tier numbers, checked 2026-11-05 through third-party summaries (confirm on the official pricing pages before relying on them):
  - Supabase: 500 MB database, 2 active projects, 50,000 monthly active users.
  - Cloudflare: unmetered static requests; Workers allows 100,000 requests a day.
- Check Cloudflare's free-plan terms on commercial use before any paid launch.
