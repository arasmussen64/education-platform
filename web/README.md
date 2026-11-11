# Web app

The React app for the learning platform. The [v1 spec](../docs/specs/v1.md) describes what it does, and [ADR-0007](../docs/decisions/0007-tech-stack.md) explains why it's built this way.

## Commands

Run these inside `web/`.

| Command                | What it does                                                            |
| ---------------------- | ----------------------------------------------------------------------- |
| `npm install`          | Installs dependencies. Run it the first time and after pulling changes. |
| `npm run dev`          | Starts the app at http://localhost:5173 and reloads it as you edit.     |
| `npm test`             | Runs the tests once.                                                    |
| `npm run test:watch`   | Re-runs the tests every time you save.                                  |
| `npm run lint`         | Checks for common mistakes (Oxlint).                                    |
| `npm run typecheck`    | Checks types (TypeScript).                                              |
| `npm run format`       | Formats the code (Prettier). `npm run format:check` only reports.       |
| `npm run build`        | Builds the production version into `dist/`.                             |
| `npm run time:content` | Times exercises' reference solutions in the browser's Python (below).   |

CI runs `format:check`, `lint`, `typecheck`, `test` and `build` on every pull request.

**Timing content.** `npm run time:content` times each exercise's reference solution in Pyodide (the browser's Python), the way the Run and Check buttons run it, and shows what share of its time limit it uses. Add the starts of topic ids to time only some: `npm run time:content -- ml.nn. py.loops`. Rows over 40% are marked and the command exits with an error; an author keeps every exercise under that before a topic is marked `ready` ([content/README.md](../content/README.md)). Close other programs first, because a busy machine reads high. NumPy is imported before timing starts, so on a NumPy topic the first Run or Check on a real page is about half a second slower than the figure shown.

**Deploying** happens automatically: Cloudflare builds and deploys every merge to `main` using `wrangler.jsonc`. `npx wrangler deploy --dry-run`, run after `npm run build`, checks the config without uploading anything. `.nvmrc` tells Cloudflare's build which Node version to use; keep it the same as the one at the repository root.

**Restart the dev server** (Ctrl+C, then `npm run dev`) after pulling changes to `vite.config.ts` or `package.json`. A running server tries to reload itself, but it can end up half-updated: for example, serving pages with no styles at all.

## Layout

```text
src/
├── config.ts        app-wide settings, including the product name (ADR-0006)
├── days.ts          calendar days in the learner's own time zone
├── main.tsx         starts the app
├── routes.tsx       every page and its address
├── auth/            who's signed in (see "Sign-in" below)
├── checkpoints/     a checkpoint's way through for a stuck learner (ADR-0012)
├── components/      shared pieces, such as the page layout, exercises, and the code runner
│                    with Run, Check and Step through (ADR-0022)
├── content/         loading the lessons and exercises from ../content (see below)
├── drafts/          what the learner has typed, kept on this device until the item passes (see below)
├── events/          saving what the learner does (see "Saving progress")
├── explain/         the explain-it-back check, graded through the AI proxy (ADR-0013)
├── export/          "Export my data": everything the learner has done, as one file (see below)
├── followups/       mistakes coming back as fresh questions (ADR-0011)
├── labs/            reading the result a learner pastes from the lab checker (ADR-0018)
├── pages/           one file per page
├── place/           where the learner is on a topic page, and the place remembered for next time
├── placement/       the placement test: finding where to start, without ticking anything off (ADR-0021)
├── practice/        the question from an earlier topic in each practice ladder (v1 spec, F5)
├── progress/        each topic's progress toward Learned (see below), and practice hours
├── python/          running learner Python in the browser (see below)
├── reports/         "Report a problem" (v1 spec, F15)
├── reviews/         reviews of Learned topics: the scheduler and the review session (ADR-0009)
├── supabase/        the Supabase client, its settings, and generated database types
├── test/            test setup and helpers (fake sign-in, fake Python, a sample topic)
├── tooling/         helpers for the build itself, used by vite.config.ts (not part of the app)
└── tutor/           the hint-only tutor, asked through the AI proxy (ADR-0015)
```

Tests live next to the code they test, named `*.test.ts` or `*.test.tsx`. They may use Node APIs (`tsconfig.test.json`); app code may not (`tsconfig.app.json`).

## Content

The lessons and exercises live in [`../content`](../content/README.md), as files. The app reads them while it's being built, so there's no content server or database:

- **YAML** files (topics, questions, exercises, a lab's `checks.yaml`) become plain data, through a small plugin in `vite.config.ts`.
- A **lab** (an exercise with `runtime: lab`, [ADR-0018](../docs/decisions/0018-lab-checker-local-mode.md)) runs in a container on the learner's machine, not in the browser. The page shows the `tools/labcheck.py` commands, the checks, and a box for the checker's printed result, which `web/src/labs/result.ts` validates and `PracticeItem` saves as a `code_check` event marked `runtime: lab`.
- **Lessons** (`lesson.mdx`) are [MDX](https://mdxjs.com): Markdown that can use components. `<Intro>`, `<Resource index={0} />` and `<Recap>` are drawn by `components/LessonView.tsx`.
- **Python files** (starter code, solutions, tests) are loaded as text, with Vite's `?raw`. There are about 1,800 of them. While building, a second small plugin in `vite.config.ts` reads them 32 at a time: Vite's own loader opens them all at once, which is more open files than Cloudflare's build machine allows one program (the live site's build failed that way on 2026-11-11, "EMFILE: too many open files"). CI builds under the same low limit (`ulimit -n 1024` in the Build step), so a build that would fail on Cloudflare fails on the pull request first.
- A **skill index** (`virtual:skill-index`, from another small plugin in `vite.config.ts`) gathers every question's and exercise's skills, stage and test skills into one file of its own, about 22 kB compressed, which downloads once a learner is signed in. With it the app works out the mistakes to revisit, and so whether a topic is Mastered, without downloading whole topics. `followups/skillIndex.test.ts` checks it against the full content.

`content/content.ts` finds the files with `import.meta.glob`. The tracks, and the topic outlines of the Python and machine-learning tracks, are bundled into the app, because the map and the Today page need them at once. The cloud track's outline-only topics are left out, and download as one piece the first time its map is shown or one of its topics opens: see `LAZY_TRACKS` in `content.ts`, and `content/outlines/`. Its Module 1 (`csa.linux.*`), which has real content, is bundled in like those tracks' topics, because the Today page and the follow-ups only look at bundled topics. A topic's lesson, questions and exercises download only when its page opens.

The dev server also shows `draft` topics, marked as drafts, so they can be tried while being written. The live site only shows `ready` ones.

`content/types.ts` mirrors the Python models in `tools/content_model.py`, which check the files in CI. Change both together.

## Python in the browser

Learner code runs in [Pyodide](https://pyodide.org) (Python compiled to WebAssembly) inside a Web Worker, so it never freezes the page.

| File                  | What it does                                                                                                                                                                            |
| --------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `python/runner.ts`    | The app's side: sends code to the worker one request at a time, and replaces the worker if code runs past its time limit (5 seconds, unless the exercise sets its own `time_limit_ms`). |
| `python/worker.ts`    | The worker: loads Pyodide from the jsDelivr CDN and answers Run and Check requests.                                                                                                     |
| `python/session.ts`   | Drives Pyodide with the shared harness ([`../harness`](../harness/README.md)). The worker and the tests both use it.                                                                    |
| `python/protocol.ts`  | The messages and results passed between the two.                                                                                                                                        |
| `python/constants.ts` | The Pyodide version, its CDN address, the default time limit for learner code, and the limit for loading a topic's packages.                                                            |

The Pyodide version is pinned in two places: `python/constants.ts`, which is what the browser loads, and `package.json`, which the tests use. `session.pyodide.test.ts` fails if they differ. It also runs every harness scenario in real Pyodide and checks that the results exactly match CPython's. `content/content.pyodide.test.ts` goes further: it runs every ready exercise's reference solution against its tests in Pyodide, so an exercise that passes in CI but not in the browser can't reach a learner. Only the reference solutions run there, because a known-wrong solution may loop forever on purpose and Pyodide in Node can't be interrupted; the validator proves those fail under CPython. It also times every Check, and every worked example's Run, against the exercise's `time_limit_ms`, fails when one is over, and prints the ten times closest to their limits. The app would stop a correct answer that ran longer, and the validator can't see that, because CPython is faster than Pyodide.

The app starts loading Pyodide (about 10 MB, cached after the first visit) in the background as soon as it opens.

**Typing input, like a terminal.** When a program calls `input()`, the Run output shows the prompt with a text field after it. Behind the scenes, the program stops at that `input()`. When the learner presses Enter, it runs again from the start with every line typed so far. Every re-run uses the same random seed, so a guessing game's secret number doesn't change.

The field is an editable `<span role="textbox">`, not an `<input>`. Password managers only look at real form fields, and a field after "What's your name?" looks like a contact form to them. NordPass, for one, gives pages no way to opt out.

## Saving progress

Everything a learner does on a topic page becomes an event in the append-only `events` table ([ADR-0008](../docs/decisions/0008-event-log.md)): viewing a lesson, answering, running and checking code, showing a hint. The `data` each event saves is listed in the [data model](../docs/specs/data-model.md#events-append-only).

| File                        | What it does                                                                                                                                                                                                                                                                                                                                                                          |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `events/eventLog.ts`        | Turns what happened into a complete row (ID, learner, session, time, commit) and decides when to send. Retries wait 5 s, 10 s, 20 s… up to 5 minutes. Every row's `data` also gets the learner's own calendar day and time zone (`local_day`, `utc_offset_minutes`). An event the browser's storage won't take waits in a second outbox in the page's memory, and is sent from there. |
| `events/outbox.ts`          | Keeps unsent events in `localStorage`, so a reload or a lost connection loses nothing. Holds a second list for events the server refused, each with the reason, the time of the last attempt and the number of attempts. `memoryStore` gives the same outbox a place in memory, for when `localStorage` is full or switched off.                                                      |
| `events/checkGrade.ts`      | Whether a Check counts as right, as wrong, or not at all. One that couldn't run (Python didn't start, a package didn't load, the exercise's own tests couldn't load, or it has no tests) is saved with no verdict. `savedCheckCouldNotRun` applies the same rule to Checks already saved, so the history reader can leave out the ones saved as wrong before 2026-11-11.              |
| `events/sync.ts`            | Sends the outbox in batches. An event the server refuses is moved to the refused list (kept in `localStorage`) so it can't block the rest. `retryRefused` sends each refused event again, one at a time, once 12 hours have passed since its last attempt; none is ever dropped.                                                                                                      |
| `events/refusedText.ts`     | The words the header and the account page use for refused events, in one place.                                                                                                                                                                                                                                                                                                       |
| `events/supabaseEvents.ts`  | Sends to Supabase as an upsert that ignores duplicates, so retrying is always safe.                                                                                                                                                                                                                                                                                                   |
| `events/EventsProvider.tsx` | Connects the log to sign-in, and tries again when the browser comes back online or the tab is shown again.                                                                                                                                                                                                                                                                            |
| `components/SaveStatus.tsx` | The "Not saved yet" badge in the header, shown while work is waiting on this device, or "Not saved yet: this device can't keep it if the page closes" while some of it is only in the page's memory. Also shows a link to the account page while the learner has refused events.                                                                                                      |

Components record events with `useRecordEvent()`. Only a signed-in learner's events are kept. Events recorded while sign-in is still loading wait in memory, then go to whoever turns out to be signed in.

## Drafts

Code typed in an exercise, and the text in the explain-it-back box, are kept as a **draft** on this device until the item passes, so a reload, a link or "Prove it now" doesn't throw them away. A draft is never sent to the server and never counts as an answer: only a Check or a graded explanation does.

| File                        | What it does                                                                                                                                                                                                                                                                                                                                                        |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `drafts/drafts.ts`          | Keeps the drafts in `localStorage`, one per topic and item, with the item's `rev`: a draft saved for an older `rev` isn't brought back. They keep to 250,000 characters in all, measured as saved, and the oldest go first, so they can't crowd out the event outbox, which shares that storage. A browser that blocks storage works the same, just without drafts. |
| `drafts/useDraft.ts`        | Brings a draft back when the editor opens, saves half a second after typing pauses (and straight away when the page closes, the tab is hidden or the editor goes away), and forgets the draft once the item passes.                                                                                                                                                 |
| `components/CodeRunner.tsx` | Says "This is your code from last time, kept on this device" when a draft is brought back, and, once the code has changed, Start over, which asks first and then brings back the starting code.                                                                                                                                                                     |

Reviews, the placement test and worked examples keep no drafts, so they always start fresh: reviews and the placement test measure what the learner remembers.

## Mistakes to revisit

The Today page brings missed skills back as fresh questions until they're relearned ([ADR-0011](../docs/decisions/0011-mistakes-come-back.md)).

| File                            | What it does                                                                                                                                                                                                                         |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `followups/followUps.ts`        | The rules, as pure functions: which skills are open and when they're due, what counts towards relearning one (a right day on or after its due day, on another question, never a worked example), and which question to ask for each. |
| `followups/skillIndex.ts`       | Reads the skill index (every item's skills, stage and test skills), which `vite.config.ts` builds from `../content` as `virtual:skill-index`, so working out follow-ups needs no topic content.                                      |
| `followups/history.ts`          | Reads the learner's graded attempts from Supabase, 1,000 rows per request, with the day each event recorded. Checks saved as wrong before 2026-11-11 that couldn't run are left out.                                                 |
| `followups/useTopicContents.ts` | Downloads the full content of the topics the Today page shows (its reviews and today's questions), with a failed state and Try again.                                                                                                |
| `pages/TodayPage.tsx`           | "Mistakes to revisit" and "Coming back later".                                                                                                                                                                                       |

Nothing is stored for follow-ups: they're recalculated from the event log on every visit, so older misses count too. `progress/useProgress.ts` works them out together with the progress (below), so every page that shows a topic's state knows which of its skills are being relearned.

## Progress

Each topic's progress toward Learned (v1 spec, F8), by the rules in the [data model](../docs/specs/data-model.md#derived-progress).

| File                         | What it does                                                                                                                                                                                                                                              |
| ---------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `progress/progress.ts`       | The rules, as pure functions: when each proof check first passed (`progressOf`), which skills are being relearned (`withOpenFollowUps`), and each topic's state (`stateOf`).                                                                              |
| `progress/useProgress.ts`    | Reads the learner's history, the skill index and the times they opened a checkpoint's steps, once; adds the events on this device; works out the follow-ups; and recalculates after each event.                                                           |
| `checkpoints/stepsOpened.ts` | Saves and reads the times the learner opened a checkpoint's steps (a `hint` event with `source: "steps"`). After the first opening, only a fresh version proves the build ([ADR-0012](../docs/decisions/0012-checkpoint-support.md), amended 2026-11-11). |
| `pages/MapPage.tsx`          | Marks the topics the learner has started, and which proof checks they've passed there.                                                                                                                                                                    |
| `pages/TopicPage.tsx`        | "Your proof so far": each check, passed (and when) or not yet.                                                                                                                                                                                            |

Like follow-ups, nothing is stored: progress is recalculated from the event log, so passes from before this existed count too. States and gating have been on since 2026-11-08, when explanations began to be graded.

**Your place in a topic.** A topic page can be long (Shell essentials has 24 practice items), so every topic page has an outline beside the content (above it on a narrow screen): the lesson's parts, every practice item with whether it's done, the three proof checks, and "Continue where you left off".

| File                          | What it does                                                                                                                                                                                                         |
| ----------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `progress/itemStates.ts`      | Each practice item's state from the learner's graded attempts: done after one correct answer or Check, tried after only wrong ones. A learner can't tick an item off themselves. Placement-test answers don't count. |
| `components/TopicOutline.tsx` | The outline. Items and sections are links to places on the page; the current one is marked; done items carry a mark as well as a color.                                                                              |
| `place/useCurrentPlace.ts`    | Which place is at the top of the screen (an IntersectionObserver over every `data-place` element: the lesson's paragraphs, each item card, the proof checks), remembered as you go.                                  |
| `place/placeMemory.ts`        | The remembered place, in `localStorage`, per device. A convenience: the page works the same without it.                                                                                                              |
| `components/PracticeItem.tsx` | Shows an item's state in its position line, and folds away an item that was already done when the page opened ("Show it again" brings it back).                                                                      |

## Export my data

The account page (`/account`, opened from the learner's name in the header) downloads everything they've done as one JSON file, for backups and the ML capstone (v1 spec, F16). The file's layout is in the [data model](../docs/specs/data-model.md#the-export-file).

| File                    | What it does                                                                                                                                                                                                                                    |
| ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `export/exportData.ts`  | Reads the outbox and the refused list, then the profile and every event from Supabase, and joins them, each event once. Refused events go under their own key, `refused_events`. It reads 1,000 rows per request until a page comes back empty. |
| `export/download.ts`    | Saves the file through the browser's normal download. The browser makes the file itself; nothing is uploaded.                                                                                                                                   |
| `pages/AccountPage.tsx` | How many events the server has refused and what that means; "Download my data"; and a message saying how many events the file holds, how many came from this browser's outbox, and how many refused ones it lists.                              |

The outbox is read first, then the server. An event sent in between is on the server by then, and one sent later is in the copy of the outbox, so none can fall through the gap.

## Sign-in

`src/auth/` keeps track of who's signed in (`AuthProvider` and `useAuth`), using Supabase Auth with the PKCE flow. `src/supabase/` holds the client, its settings, and the generated database types.

- **The live site:** "Sign in with GitHub". Supabase sends the learner to GitHub and back.
- **The dev server:** email links. The local Supabase has no GitHub app, so the sign-in page shows an email form, and the email lands in the local test inbox at http://127.0.0.1:54324. Start the local Supabase first (`npm run db:start` at the repository root).

The Supabase address and publishable key are in `src/supabase/config.ts`: the local ones for `npm run dev`, the real project's for builds. They're public by design; row-level security protects the data.

`src/supabase/database.types.ts` is generated: after a migration, run `npm run db:types` at the repository root.
