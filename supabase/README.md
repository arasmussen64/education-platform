# Database (Supabase)

Postgres, sign-in and server functions, through [Supabase](https://supabase.com). Development uses a private copy that runs in Docker on your PC; the cloud project is for real learning only ([ADR-0010](../docs/decisions/0010-environments.md)).

## Folder

| Path                     | What it is                                                                                                                      |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------- |
| `config.toml`            | Settings for the local copy (ports, auth, which services run)                                                                   |
| `migrations/`            | The database's history: SQL files, applied in order. They're the only way the schema changes.                                   |
| `tests/database/`        | Database tests (pgTAP): who can read and write what, and the append-only rules                                                  |
| `functions/ai/`          | The AI proxy, an Edge Function: the one place the Claude API key exists ([ADR-0013](../docs/decisions/0013-explain-grading.md)) |
| `functions/.env.example` | The proxy's settings for your PC. Copy it to `functions/.env`, which git ignores.                                               |
| `seed.sql`               | Sample data for the local copy only                                                                                             |

## Commands

Run these from the repository root. Docker Desktop must be running.

| Command                                   | What it does                                                                                                                                                                                                                                                                                                                       |
| ----------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `npm run db:start`                        | Starts the local Supabase. The first time, it downloads a few GB of images.                                                                                                                                                                                                                                                        |
| `npm run db:status`                       | Shows the local addresses and keys.                                                                                                                                                                                                                                                                                                |
| `npm run db:reset`                        | Rebuilds the local database from scratch: every migration, then `seed.sql`.                                                                                                                                                                                                                                                        |
| `npm run db:test`                         | Runs the database tests.                                                                                                                                                                                                                                                                                                           |
| `npm run db:lint`                         | Checks the SQL in migrations for mistakes.                                                                                                                                                                                                                                                                                         |
| `npm run db:stop`                         | Stops the local Supabase. Your local data is kept for next time.                                                                                                                                                                                                                                                                   |
| `npm run db:types`                        | Regenerates `web/src/supabase/database.types.ts` from the local database. Run it after every migration. If `npm run db:start` said "Starting database from backup", run `npm run db:reset` first: the backup may predate your newest migration, and the generated file would silently lose that table (it happened on 2026-11-09). |
| `npx supabase migration new <name>`       | Creates a new, empty migration file.                                                                                                                                                                                                                                                                                               |
| `npx supabase db push --remote --dry-run` | Shows which merged migrations the real project is missing. Without `--dry-run` (and with `--yes`), it applies them. Without `--remote`, it targets the local database.                                                                                                                                                             |
| `npx supabase migration list --remote`    | Compares migration history on your PC with the real project.                                                                                                                                                                                                                                                                       |

Local Studio, a web UI for browsing the database, runs at http://127.0.0.1:54323 while the local Supabase is up.

## The AI proxy (Edge Function)

`functions/ai/` grades explanations and gives the tutor's hints with Claude ([ADR-0013](../docs/decisions/0013-explain-grading.md), [ADR-0015](../docs/decisions/0015-hint-only-tutor.md)). An Edge Function is a small program Supabase runs on its servers, on Deno, a JavaScript and TypeScript runtime. The browser can call it but can't see inside it, so the API key is safe there.

| File                       | What it does                                                                                                                                                        |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `handler.ts`               | The checks, in order: signed in, `allowed`, under the month's $10 cap, a key exists. Then it asks Claude (a grading or a hint) and logs the call in `ai_calls`.     |
| `grading.ts`               | What Claude is asked to grade an explanation, and how its answer is read. A pass means every required rubric item is met.                                           |
| `tutor.ts`                 | What Claude is asked for a hint, the rungs of the hint ladder, and the safety filter that replaces a reply giving too much away.                                    |
| `cost.ts`                  | Anthropic's prices, and what a call cost. Update the prices when Anthropic's change.                                                                                |
| `index.ts`                 | Connects the handler to the real Supabase and Claude.                                                                                                               |
| `test-set/`                | Sample explanations with the verdict each should get, one file per topic. They choose the grading model.                                                            |
| `tutor-test-set/`          | Conversations with learners trying to get the answer out of the tutor, one file per exercise, with what each reply must not contain. They choose the tutor's model. |
| `eval.ts`, `tutor-eval.ts` | Run a test set against Claude, with the same request the proxy sends.                                                                                               |

| Command                                     | What it does                                                                                                                                                                                                                                                                                                       |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `npm run fn:serve`                          | Serves the functions on your PC, at http://127.0.0.1:54321/functions/v1/ai. Needs the local Supabase running.                                                                                                                                                                                                      |
| `npm run fn:test`                           | Type-checks the proxy and runs its tests, with Deno. No test calls the real Claude API.                                                                                                                                                                                                                            |
| `npm run fn:eval -- [model] [effort]`       | Runs the grading test set against the real Claude API, using the key in `functions/.env`. **It costs money** (about $0.02 for the set on Claude Haiku 5.5, $0.80 on Claude Opus 5.5), so the owner approves each run.                                                                                              |
| `npm run fn:eval:tutor -- [model] [effort]` | Runs the tutor test set the same way and prints every reply to read. **It costs money** (about half a cent on Claude Haiku 5.5, measured on 2026-11-09; about $0.10 on Claude Sonnet 5.5), so the owner approves each run. A reply that is replaced by the safety filter, or contains a forbidden line, is a miss. |

Deno comes with `npm install` at the repository root, so there's nothing else to install.

### Putting it live

Merging deploys the web app, but not the function. A change to `functions/ai/` reaches the live project only when it's deployed by hand, with the owner's go-ahead. Once the change is merged, run these from the repository root, in this order:

1. `npx supabase db push --remote --dry-run` lists the migrations the live database is missing. If the change has one, apply it: run the same command with `--yes` in place of `--dry-run`.
2. `npx supabase functions deploy ai --no-verify-jwt --yes` deploys the function. `--no-verify-jwt` matches `config.toml`: the function checks sign-in itself.
3. Check it without calling Claude. This request should get a 401 and `{"error":"Sign in first."}`:

   ```sh
   curl -s -X POST https://<ref>.supabase.co/functions/v1/ai -H "apikey: <publishable key>"
   ```

The key is set once, and again only when it changes: `npx supabase secrets set --env-file supabase/functions/.env --yes`.

**Why `--yes`:** the CLI asks before it changes the live project. Inside Claude Code it can't ask, so it refuses unless the command includes `--yes`. That flag goes in only once the owner has agreed.

## Problem reports

"Report a problem" on the site (v1 spec, F15) adds a row to `problem_reports`: who, when, the topic, the item and its `rev`, and the message. To read them, open the live project's dashboard, **Table Editor**, `problem_reports`, and filter on `status = open`. Once the content is fixed (and merged), set that row's `status` to `resolved`. Learners can't change a report themselves. The same table is in the local database, so a report made on a dev server lands in local Studio (http://127.0.0.1:54323).

## Backups

A workflow takes an encrypted data dump of the real project every night and commits it to a private backups repository ([ADR-0020](../docs/decisions/0020-automated-backups.md)); the owner's one-time setup is in [docs/setup.md](../docs/setup.md), under "Back up your learning data". CI's database job rehearses the restore on every pull request with `tools/backup_restore_check.sh`, which you can also run yourself against the local database (it resets it, then restores everything that was in it).

## Rules

- **Change the schema only with a new migration.** Never edit tables in a dashboard, and never edit a migration that has reached production.
- **Every table gets row-level security** in the same migration that creates it, and tests that prove who can and can't see each row.
- **Events are append-only** (ADR-0008). The database blocks updates and deletes even for admins, except when deliberately deleting a whole account (see the migration).
- **Migrations reach production only after merging,** once they've passed locally and in CI.
