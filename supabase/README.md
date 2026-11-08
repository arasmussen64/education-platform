# Database (Supabase)

Postgres, sign-in and server functions, through [Supabase](https://supabase.com). Development uses a private copy that runs in Docker on your PC; the cloud project is for real learning only ([ADR-0010](../docs/decisions/0010-environments.md)).

## Folder

| Path | What it is |
|---|---|
| `config.toml` | Settings for the local copy (ports, auth, which services run) |
| `migrations/` | The database's history: SQL files, applied in order. They're the only way the schema changes. |
| `tests/database/` | Database tests (pgTAP): who can read and write what, and the append-only rules |
| `functions/ai/` | The AI proxy, an Edge Function: the one place the Claude API key exists ([ADR-0013](../docs/decisions/0013-explain-grading.md)) |
| `functions/.env.example` | The proxy's settings for your PC. Copy it to `functions/.env`, which git ignores. |
| `seed.sql` | Sample data for the local copy only |

## Commands

Run these from the repository root. Docker Desktop must be running.

| Command | What it does |
|---|---|
| `npm run db:start` | Starts the local Supabase. The first time, it downloads a few GB of images. |
| `npm run db:status` | Shows the local addresses and keys. |
| `npm run db:reset` | Rebuilds the local database from scratch: every migration, then `seed.sql`. |
| `npm run db:test` | Runs the database tests. |
| `npm run db:lint` | Checks the SQL in migrations for mistakes. |
| `npm run db:stop` | Stops the local Supabase. Your local data is kept for next time. |
| `npm run db:types` | Regenerates `web/src/supabase/database.types.ts` from the local database. Run it after every migration. |
| `npx supabase migration new <name>` | Creates a new, empty migration file. |
| `npx supabase db push --remote --dry-run` | Shows which merged migrations the real project is missing. Without `--dry-run` (and with `--yes`), it applies them. Without `--remote`, it targets the local database. |
| `npx supabase migration list --remote` | Compares migration history on your PC with the real project. |

Local Studio, a web UI for browsing the database, runs at http://127.0.0.1:54323 while the local Supabase is up.

## The AI proxy (Edge Function)

`functions/ai/` grades explanations with Claude ([ADR-0013](../docs/decisions/0013-explain-grading.md)). An Edge Function is a small program Supabase runs on its servers, on Deno, a JavaScript and TypeScript runtime. The browser can call it but can't see inside it, so the API key is safe there.

| File | What it does |
|---|---|
| `handler.ts` | The checks, in order: signed in, `allowed`, under the month's $10 cap, a key exists. Then it grades and logs the call in `ai_calls`. |
| `grading.ts` | What Claude is asked, and how its answer is read. A pass means every required rubric item is met. |
| `cost.ts` | Anthropic's prices, and what a call cost. Update the prices when Anthropic's change. |
| `index.ts` | Connects the handler to the real Supabase and Claude. |

| Command | What it does |
|---|---|
| `npm run fn:serve` | Serves the functions on your PC, at http://127.0.0.1:54321/functions/v1/ai. Needs the local Supabase running. |
| `npm run fn:test` | Type-checks the proxy and runs its tests, with Deno. No test calls the real Claude API. |

Deno comes with `npm install` at the repository root, so there's nothing else to install.

## Rules

- **Change the schema only with a new migration.** Never edit tables in a dashboard, and never edit a migration that has reached production.
- **Every table gets row-level security** in the same migration that creates it, and tests that prove who can and can't see each row.
- **Events are append-only** (ADR-0008). The database blocks updates and deletes even for admins, except when deliberately deleting a whole account (see the migration).
- **Migrations reach production only after merging,** once they've passed locally and in CI.
