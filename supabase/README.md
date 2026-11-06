# Database (Supabase)

Postgres, sign-in and server functions, through [Supabase](https://supabase.com). Development uses a private copy that runs in Docker on your PC; the cloud project is for real learning only ([ADR-0010](../docs/decisions/0010-environments.md)).

## Folder

| Path | What it is |
|---|---|
| `config.toml` | Settings for the local copy (ports, auth, which services run) |
| `migrations/` | The database's history: SQL files, applied in order. They're the only way the schema changes. |
| `tests/database/` | Database tests (pgTAP): who can read and write what, and the append-only rules |
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
| `npx supabase migration new <name>` | Creates a new, empty migration file. |

Local Studio, a web UI for browsing the database, runs at http://127.0.0.1:54323 while the local Supabase is up.

## Rules

- **Change the schema only with a new migration.** Never edit tables in a dashboard, and never edit a migration that has reached production.
- **Every table gets row-level security** in the same migration that creates it, and tests that prove who can and can't see each row.
- **Events are append-only** (ADR-0008). The database blocks updates and deletes even for admins, except when deliberately deleting a whole account (see the migration).
- **Migrations reach production only after merging,** once they've passed locally and in CI.
