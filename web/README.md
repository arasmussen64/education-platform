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

**Restart the dev server** (Ctrl+C, then `npm run dev`) after pulling changes to `vite.config.ts` or `package.json`. A running server tries to reload itself, but it can end up half-updated: for example, serving pages with no styles at all.

## Layout

```text
src/
├── config.ts        app-wide settings, including the product name (ADR-0006)
├── main.tsx         starts the app
├── routes.tsx       every page and its address
├── components/      shared pieces, such as the page layout and the code runner
├── pages/           one file per page
├── python/          running learner Python in the browser (see below)
└── test/setup.ts    runs before the tests
```

Tests live next to the code they test, named `*.test.ts` or `*.test.tsx`. They may use Node APIs (`tsconfig.test.json`); app code may not (`tsconfig.app.json`).

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

**Typing input, like a terminal.** When a program calls `input()`, the Run output shows the prompt with a text field after it. Behind the scenes, the program stops at that `input()`. When the learner presses Enter, it runs again from the start with every line typed so far. Every re-run uses the same random seed, so a guessing game's secret number doesn't change. The field is deliberately not inside a `<form>`, so password managers don't offer to "save" what's typed.
