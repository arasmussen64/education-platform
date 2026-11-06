# Web app

The React app for the learning platform. The [v1 spec](../docs/specs/v1.md) describes what it does, and [ADR-0007](../docs/decisions/0007-tech-stack.md) explains why it's built this way.

## Commands

Run these inside `web/`.

| Command              | What it does                                                            |
| -------------------- | ----------------------------------------------------------------------- |
| `npm install`        | Installs dependencies. Run it the first time and after pulling changes. |
| `npm run dev`        | Starts the app at http://localhost:5173 and reloads it as you edit.     |
| `npm test`           | Runs the tests once.                                                    |
| `npm run test:watch` | Re-runs the tests every time you save.                                  |
| `npm run lint`       | Checks for common mistakes (Oxlint).                                    |
| `npm run typecheck`  | Checks types (TypeScript).                                              |
| `npm run format`     | Formats the code (Prettier). `npm run format:check` only reports.       |
| `npm run build`      | Builds the production version into `dist/`.                             |

CI runs `format:check`, `lint`, `typecheck`, `test` and `build` on every pull request.

**Deploying** happens automatically: Cloudflare builds and deploys every merge to `main` using `wrangler.jsonc`. `npx wrangler deploy --dry-run`, run after `npm run build`, checks the config without uploading anything. `.nvmrc` tells Cloudflare's build which Node version to use; keep it the same as the one at the repository root.

**Restart the dev server** (Ctrl+C, then `npm run dev`) after pulling changes to `vite.config.ts` or `package.json`. A running server tries to reload itself, but it can end up half-updated: for example, serving pages with no styles at all.

## Layout

```text
src/
├── config.ts        app-wide settings, including the product name (ADR-0006)
├── main.tsx         starts the app
├── routes.tsx       every page and its address
├── auth/            who's signed in (see "Sign-in" below)
├── components/      shared pieces, such as the page layout, the code runner and exercises
├── content/         loading the lessons and exercises from ../content (see below)
├── events/          saving what the learner does (see "Saving progress")
├── followups/       mistakes coming back as fresh questions (ADR-0011)
├── pages/           one file per page
├── python/          running learner Python in the browser (see below)
├── supabase/        the Supabase client, its settings, and generated database types
└── test/            test setup and helpers (fake sign-in, fake Python, a sample topic)
```

Tests live next to the code they test, named `*.test.ts` or `*.test.tsx`. They may use Node APIs (`tsconfig.test.json`); app code may not (`tsconfig.app.json`).

## Content

The lessons and exercises live in [`../content`](../content/README.md), as files. The app reads them while it's being built, so there's no content server or database:

- **YAML** files (topics, questions, exercises) become plain data, through a small plugin in `vite.config.ts`.
- **Lessons** (`lesson.mdx`) are [MDX](https://mdxjs.com): Markdown that can use components. `<Intro>`, `<Resource index={0} />` and `<Recap>` are drawn by `components/LessonView.tsx`.
- **Python files** (starter code, solutions, tests) are loaded as text, with Vite's `?raw`.

`content/content.ts` finds the files with `import.meta.glob`. Topic outlines are bundled into the app, because the map needs them all. A topic's lesson, questions and exercises download only when its page opens.

The dev server also shows `draft` topics, marked as drafts, so they can be tried while being written. The live site only shows `ready` ones.

`content/types.ts` mirrors the Python models in `tools/content_model.py`, which check the files in CI. Change both together.

## Python in the browser

Learner code runs in [Pyodide](https://pyodide.org) (Python compiled to WebAssembly) inside a Web Worker, so it never freezes the page.

| File                  | What it does                                                                                                                          |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `python/runner.ts`    | The app's side: sends code to the worker one request at a time, and replaces the worker if code runs past its time limit (5 seconds). |
| `python/worker.ts`    | The worker: loads Pyodide from the jsDelivr CDN and answers Run and Check requests.                                                   |
| `python/session.ts`   | Drives Pyodide with the shared harness ([`../harness`](../harness/README.md)). The worker and the tests both use it.                  |
| `python/protocol.ts`  | The messages and results passed between the two.                                                                                      |
| `python/constants.ts` | The Pyodide version, its CDN address, and the time limit.                                                                             |

The Pyodide version is pinned in two places: `python/constants.ts`, which is what the browser loads, and `package.json`, which the tests use. `session.pyodide.test.ts` fails if they differ. It also runs every harness scenario in real Pyodide and checks that the results exactly match CPython's.

The app starts loading Pyodide (about 10 MB, cached after the first visit) in the background as soon as it opens.

**Typing input, like a terminal.** When a program calls `input()`, the Run output shows the prompt with a text field after it. Behind the scenes, the program stops at that `input()`. When the learner presses Enter, it runs again from the start with every line typed so far. Every re-run uses the same random seed, so a guessing game's secret number doesn't change.

The field is an editable `<span role="textbox">`, not an `<input>`. Password managers only look at real form fields, and a field after "What's your name?" looks like a contact form to them. NordPass, for one, gives pages no way to opt out.

## Saving progress

Everything a learner does on a topic page becomes an event in the append-only `events` table ([ADR-0008](../docs/decisions/0008-event-log.md)): viewing a lesson, answering, running and checking code, showing a hint. The `data` each event saves is listed in the [data model](../docs/specs/data-model.md#events-append-only).

| File                        | What it does                                                                                                                                          |
| --------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `events/eventLog.ts`        | Turns what happened into a complete row (ID, learner, session, time, commit) and decides when to send. Retries wait 5 s, 10 s, 20 s… up to 5 minutes. |
| `events/outbox.ts`          | Keeps unsent events in `localStorage`, so a reload or a lost connection loses nothing.                                                                |
| `events/sync.ts`            | Sends the outbox in batches. An event the server refuses is set aside (kept in `localStorage`) so it can't block the rest.                            |
| `events/supabaseEvents.ts`  | Sends to Supabase as an upsert that ignores duplicates, so retrying is always safe.                                                                   |
| `events/EventsProvider.tsx` | Connects the log to sign-in, and tries again when the browser comes back online or the tab is shown again.                                            |
| `components/SaveStatus.tsx` | The "Not saved yet" badge in the header, shown while work is waiting on this device.                                                                  |

Components record events with `useRecordEvent()`. Only a signed-in learner's events are kept. Events recorded while sign-in is still loading wait in memory, then go to whoever turns out to be signed in.

## Mistakes to revisit

The Today page brings missed skills back as fresh questions until they're relearned ([ADR-0011](../docs/decisions/0011-mistakes-come-back.md)).

| File                        | What it does                                                                                                         |
| --------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `followups/followUps.ts`    | The rules, as pure functions: which skills are open and when they're due, and which question to ask for each.        |
| `followups/history.ts`      | Reads the learner's graded attempts from Supabase, 1,000 rows per request.                                           |
| `followups/useFollowUps.ts` | Joins that history with the events on this device, loads the topics with misses, and recalculates after each answer. |
| `pages/TodayPage.tsx`       | "Mistakes to revisit" and "Coming back later".                                                                       |

Nothing is stored for follow-ups: they're recalculated from the event log on every visit, so older misses count too.

## Sign-in

`src/auth/` keeps track of who's signed in (`AuthProvider` and `useAuth`), using Supabase Auth with the PKCE flow. `src/supabase/` holds the client, its settings, and the generated database types.

- **The live site:** "Sign in with GitHub". Supabase sends the learner to GitHub and back.
- **The dev server:** email links. The local Supabase has no GitHub app, so the sign-in page shows an email form, and the email lands in the local test inbox at http://127.0.0.1:54324. Start the local Supabase first (`npm run db:start` at the repository root).

The Supabase address and publishable key are in `src/supabase/config.ts`: the local ones for `npm run dev`, the real project's for builds. They're public by design; row-level security protects the data.

`src/supabase/database.types.ts` is generated: after a migration, run `npm run db:types` at the repository root.
