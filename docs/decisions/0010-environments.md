# ADR-0010: Local Supabase in Docker for development; one cloud project for real use

- **Status:** Accepted
- **Date:** 2026-11-05

## Context

- Supabase's free plan allows two active projects. The owner already uses one for something else, so this platform gets one cloud project.
- Learner events are append-only and are future ML training data (ADR-0008). Test data must never reach the real project, because it could never be removed.
- Database changes (tables, row-level security) need a safe place to be tried before they touch real data.
- The owner chose to run Supabase locally with Docker rather than the alternatives below.

## Decision

- **Production:** one Supabase cloud project, `education-platform`, used only for real learning.
- **Development:** the full Supabase stack (Postgres, Auth, Studio, Edge Functions) runs on the owner's PC in **Docker Desktop**, started with the Supabase CLI. The dev server talks to this local copy by default.
- **The CLI version is pinned:** the Supabase CLI is a dev dependency in the repo, so the PC and CI use the same version.
- **Schema changes are migrations:** SQL files in `supabase/migrations/`, never hand edits in the dashboard. They're replayed from scratch locally (`supabase db reset`) and in CI, together with database tests for row-level security and the append-only rules. They're applied to production only after merging.
- **Production stays separate:** never point a dev server, test or script at the production project.
- **Backups:** we don't rely on Supabase backups on the free plan. Use "Export my data" (F16) regularly until automated backups arrive in Phase 2.

## Alternatives considered

- **One cloud project plus a separate test account:** no installs, but test and real data would share a database, and schema changes could only be tried in CI.
- **Freeing a project slot:** the owner still needs their other project.

## Consequences

- One-time setup: Docker Desktop with WSL 2 (Windows Subsystem for Linux), using several GB of disk. Docker Desktop is free for personal use.
- Docker uses a few GB of memory while running, so quit it when you're not developing.
- CI gets a database job that starts Postgres in Docker on GitHub's machines. It takes a minute or two per run, within the free minutes.
- Once a migration has reached production it's never edited. Changes come as new migrations.
