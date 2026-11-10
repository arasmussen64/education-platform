# ADR-0020: Nightly encrypted backups of the learning data

- **Status:** Accepted (the owner asked for Phase 2 to be built on 2026-11-09; this is its backups item)
- **Date:** 2026-11-09

## Context

- The learner's history (`events`, append-only, and the future training data of ADR-0008), their profile, the AI-call log and the problem reports live only in the one Supabase project. The free plan has no backups we can rely on ([ADR-0010](0010-environments.md)), and paying for them is ruled out ([ADR-0005](0005-free-hosting-first.md)).
- Until now the only copy has been "Export my data" ([F16](../specs/v1.md#f16-export-my-data)): a JSON download the owner has to remember to take, kept off this PC by hand.
- The repository is public since 2026-11-09, which gives GitHub Actions unlimited minutes, and which means nothing personal may ever land in it, in a workflow log or in anything a run keeps.
- The realistic risks are our own: a bad migration, an accidental delete, a project paused and lost on the free tier. Losing the provider entirely is the rarer case; the backup should survive both.

## Decision

1. **A scheduled workflow takes a data dump every night** (`.github/workflows/backup.yml`, 03:17 UTC, and on demand). It uses the pinned Supabase CLI (`db dump --remote=<url>`) against the real project's **session-pooler** connection string: data only, for the `public` and `auth` schemas. The schema itself isn't backed up, because the migrations are its source of truth (ADR-0010). `auth` is included so the learner keeps the same id on restore and the events stay theirs.
2. **The dump is encrypted before it leaves the runner,** with `gpg --symmetric` (AES-256) and a passphrase that exists only in a repository secret and the owner's password manager. The plain file is shredded. Nothing readable is ever uploaded anywhere.
3. **The archive is a private repository,** `education-platform-backups`, one commit a night under `dumps/YYYY-MM-DD.sql.gpg`. The dumps are small (one learner: kilobytes to megabytes a night), so a private Git repository is a free, versioned archive off the data's provider. The owner clones or pulls it onto another drive now and then; that's the copy that isn't on GitHub.
4. **Three secrets, which only the owner can add,** in the repository's Actions secrets: `SUPABASE_DB_URL` (the session-pooler string, which works from GitHub's IPv4 runners), `BACKUP_PASSPHRASE`, and `BACKUPS_REPO_TOKEN` (a fine-grained token that can write only to the backups repository). Until all three exist, the workflow says which are missing and stops green, so a schedule that's waiting for setup isn't a red X every morning.
5. **The restore path is rehearsed on every pull request.** CI's database job runs `tools/backup_restore_check.sh`: a learner with one event goes into the throwaway local database; the data is dumped with the same command; the dump is encrypted and decrypted with a throwaway passphrase; the database is reset to empty tables; the dump is restored with `psql`; the learner, their profile and the event must be back. The same script runs on the owner's PC. A backup nobody has restored isn't a backup.
6. **"Export my data" stays** as the learner's own copy and the ML capstone's input. The nightly dump is the platform's.

## Alternatives considered

- **Keep relying on the manual export.** It depends on remembering, and a learner's export is one learner's data; the dump is the whole database.
- **Supabase's paid daily backups or point-in-time recovery.** Against ADR-0005, and they live with the provider.
- **A Supabase Edge Function on a schedule writing to Supabase Storage.** Same provider as the data, so it doesn't cover a lost project; Deno has no `pg_dump`, so it would be a hand-written row copier that drifts from the schema.
- **Keeping the encrypted dump as the run's artifact.** Anyone with a GitHub account can download a public repository's artifacts. Encryption would make that safe, but it's a public footprint for no gain over the private repository, and artifacts expire after 90 days.
- **Committing the dumps to this repository.** Never: the repository is public, and a Git history can't unpublish.

## Consequences

- The owner has four one-time steps (create the private repository, make the passphrase, make the token, add the three secrets), written out in [docs/setup.md](../setup.md). Until then the workflow reports itself as waiting.
- The passphrase is the whole secret: losing it loses every backup. It goes in the password manager the day it's made.
- CI's database job gets about a minute more work (the rehearsal).
- The dump includes `auth` rows (hashed credentials, refresh tokens). It is encrypted everywhere it's kept and the backups repository is private, which is the right place for it and not a reason to leave `auth` out.
- Restoring into a _new_ project means running the migrations first, then the data; the steps are in the setup guide, and the rehearsal exercises the same order.
- GitHub switches off scheduled workflows in a repository with no commits for 60 days, after emailing the owner. Re-enabling it is one click on the Actions tab.
