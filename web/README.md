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

## Layout

```text
src/
├── config.ts        app-wide settings, including the product name (ADR-0006)
├── main.tsx         starts the app
├── routes.tsx       every page and its address
├── components/      shared pieces, such as the page layout
├── pages/           one file per page
└── test/setup.ts    runs before the tests
```

Tests live next to the code they test, named `*.test.tsx`.
