# Setup

What's needed on the owner's computer and in the cloud. Tick things off as they're done.

## On this computer

| Tool               | Why                                                                                          | Status                                                                         |
| ------------------ | -------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| Git and GitHub CLI | Version control and pull requests                                                            | ✅ Installed                                                                   |
| Node 24 and npm 11 | The web app                                                                                  | ✅ Installed                                                                   |
| Python 3.12        | Content tools and, later, ML                                                                 | ✅ Installed                                                                   |
| Docker Desktop     | Runs a private copy of Supabase for development ([ADR-0010](decisions/0010-environments.md)) | ✅ Installed                                                                   |
| uv                 | Python package manager; also installs Python 3.14                                            | ✅ Installed (`python -m pip install --user uv`; run it as `python -m uv`)     |
| Deno               | Runs and tests the AI proxy (an Edge Function)                                               | ✅ Comes with `npm install` at the repository root; nothing to install by hand |

### Install Docker Desktop

1. In PowerShell, run `winget install -e --id Docker.DockerDesktop`, or download the installer from docker.com.
2. Restart the PC if asked.
3. Open Docker Desktop and accept the terms. It runs on WSL 2 (Windows Subsystem for Linux); if it offers to install or update WSL, say yes.
4. Check that it works: `docker run --rm hello-world` should print "Hello from Docker!"

Docker Desktop uses a few GB of memory while it's running, so quit it when you're not developing. It's free for personal use.

## In the cloud

| Service           | Why                                                                                                                                                      | Status                                                                                                     |
| ----------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| GitHub            | Code, pull requests, CI                                                                                                                                  | ✅ Done                                                                                                    |
| GitHub OAuth app  | "Sign in with GitHub" on the live site                                                                                                                   | ✅ Created and connected to Supabase                                                                       |
| Supabase          | The real database and sign-in (one project, `education-platform`)                                                                                        | ✅ Linked; migrations applied                                                                              |
| Cloudflare        | Hosts the app                                                                                                                                            | ✅ Connected; deploys on every merge to `main`                                                             |
| Anthropic Console | The Claude API, for grading explanations and the tutor's hints                                                                                           | ✅ Key in the live project's secrets; both actions live; $10 monthly limit set in the Console (2026-11-09) |
| Docker Desktop    | The local Supabase, and the cloud track's labs (containers on this PC, run by `tools/labcheck.py`, [ADR-0018](decisions/0018-lab-checker-local-mode.md)) | ✅ Installed                                                                                               |

### Supabase

1. In your existing Supabase account, create a project named `education-platform` on the Free plan.
2. Save its database password in a password manager.
3. Choose the region closest to you.

This project is for real learning only. Development uses the local copy in Docker.

**Link it to the repo (one time).** In a terminal in the repository folder:

1. Run `npx supabase login`. It opens your browser to approve the CLI.
2. Run `npx supabase link --project-ref <ref>`. The ref is the code in your project's dashboard address: `supabase.com/dashboard/project/<ref>`. It asks for the database password.

After that, merged migrations are applied to the real database with `npx supabase db push --remote` (preview first with `--dry-run`). Without `--remote`, the CLI targets the local database.

### Cloudflare

1. Sign up at dash.cloudflare.com/sign-up and verify your email.
2. Skip any prompt to add a domain. We'll use Cloudflare's free address.

**Connect the repo (one time),** so every merge to `main` deploys automatically. Cloudflare's wording may differ slightly from this:

1. In the Cloudflare dashboard, open **Workers & Pages** and choose **Create**, then **Import a repository** (or "Connect to Git").
2. Connect GitHub. When GitHub asks which repositories Cloudflare may access, choose **only** `education-platform`.
3. Use these settings:

   | Setting                           | Value                                                  |
   | --------------------------------- | ------------------------------------------------------ |
   | Project name                      | `education-platform` (must match `web/wrangler.jsonc`) |
   | Build command                     | `npm run build`                                        |
   | Deploy command                    | `npx wrangler deploy`                                  |
   | **Path**, under Advanced settings | `/web` (it starts as `/`)                              |

   Leave everything else at its default. There's no production-branch field: Cloudflare uses the repository's default branch, `main`. You can check it later under **Settings → Build → Branch control**.

4. Save and deploy.
5. In the Worker's **Domains** tab, switch on the **workers.dev** address. A new Cloudflare account may start with it off. From then on, `web/wrangler.jsonc` keeps it on.

The app is live at **https://education-platform.arasmussen64.workers.dev**.

Pull requests also get their own preview builds.

### GitHub OAuth app (sign-in)

The live site's "Sign in with GitHub" uses an OAuth app named `education-platform`, under github.com/settings/developers → OAuth Apps.

| Field                   | Value                                                       |
| ----------------------- | ----------------------------------------------------------- |
| Homepage URL            | `https://education-platform.arasmussen64.workers.dev`       |
| Callback (redirect) URL | `https://fretenazxzmfakjxvtwd.supabase.co/auth/v1/callback` |

Its client ID and secret are stored only in Supabase (**Authentication → Sign In / Providers → GitHub**). In Supabase **Authentication → URL Configuration**, the Site URL is the live address, and `https://education-platform.arasmussen64.workers.dev/**` is an allowed redirect.

**Sign-ups are closed** (v1 spec, F1). The owner's account was created by signing in with GitHub on 2026-11-06. Then **Authentication → Sign In / Providers → "Allow new users to sign up"** was switched off. Existing accounts can still sign in. To check from anywhere, run `curl -s https://fretenazxzmfakjxvtwd.supabase.co/auth/v1/settings -H "apikey: <publishable key>"`; it should show `"disable_signup": true`. To let another learner in later, switch it back on briefly, or invite them from **Authentication → Users**.

Local development doesn't use this app. The local Supabase signs in with email links, which land in its test inbox at http://127.0.0.1:54324.

### Anthropic Console (the Claude API)

1. Create an account at console.anthropic.com and add billing.
2. Set a monthly spending limit of $10. This is on top of the app's own cap.
3. Create an API key. It's kept in two places only:
   - `supabase/functions/.env` on your PC (gitignored), for local testing, `npm run fn:eval` and `npm run fn:eval:tutor`;
   - the live project's secrets, as `ANTHROPIC_API_KEY`. It was put there on 2026-11-08 with `npx supabase secrets set --env-file supabase/functions/.env --yes`. That command reads the file, so the key never appears on screen.

**To change the key:**

1. Put the new key in the `.env` file.
2. Run that command again.
3. Delete the old key in the Console.

**Who can use it.** Explanations are graded only for accounts with `allowed` switched on, a column in `profiles`. The owner's account was switched on on 2026-11-08, in the dashboard's SQL editor, with:

```sql
update public.profiles set allowed = true
where id = (select id from auth.users order by created_at limit 1)
returning display_name, allowed;
```

It picks the oldest account, which is the owner's. For another learner, use their id from **Authentication → Users** instead.

## Back up your learning data

Your learning history lives only in the Supabase project, and we don't rely on the free plan's backups ([ADR-0010](decisions/0010-environments.md)). A workflow takes an encrypted copy every night ([ADR-0020](decisions/0020-automated-backups.md)); it needs four one-time steps from you, because every one of them is a credential:

1. **Create the private backups repository.** On GitHub, a new repository called `education-platform-backups`, **private**, with a README so it has a first commit. The nightly dumps are committed there under `dumps/`.
2. **Make a passphrase.** A long random one from your password manager, saved there as "education-platform backups". The dumps are AES-256 encrypted with it; without it they're unreadable, you included.
3. **Make a token for the backups repository.** GitHub, Settings, Developer settings, Fine-grained personal access tokens: one token, access to only `education-platform-backups`, repository permission **Contents: Read and write**, nothing else, expiry one year (put a reminder in your calendar).
4. **Add the three secrets** to this repository: Settings, Secrets and variables, Actions, "New repository secret":
   - `SUPABASE_DB_URL`: in the Supabase dashboard, your project, **Connect**, choose **Session pooler**, copy the connection string and put your database password in place of `[YOUR-PASSWORD]`. (The session pooler works from GitHub's machines; the direct connection doesn't.) If the password has anything in it besides letters and digits, the string needs those characters escaped; the simpler fix is to reset the database password (Project Settings, Database) to letters and digits only, then run `npx supabase link` again.
   - `BACKUP_PASSPHRASE`: the passphrase from step 2.
   - `BACKUPS_REPO_TOKEN`: the token from step 3.

Then run the **Backup** workflow once by hand (Actions, Backup, "Run workflow") and check that a file appeared in the backups repository. Until the secrets are set, the nightly run says which are missing and stops without a red X. Two things to know: GitHub switches a schedule off in a repository with no commits for 60 days (it emails you first; one click on the Actions tab turns it back on), and every few months you should clone or pull the backups repository onto a drive that isn't this PC, which is the copy that isn't on GitHub.

**Restoring,** should you ever need to: download a dump (`dumps/YYYY-MM-DD.sql.gpg`), then `gpg -d YYYY-MM-DD.sql.gpg > restore.sql`. The target must have the schema and empty tables: a new project after `npx supabase link` and `npx supabase db push --remote`, or this one after its data was lost. Then `psql "<session pooler URL>" -v ON_ERROR_STOP=1 --single-transaction -f restore.sql`. This PC has no `psql` of its own; the one inside the local database's container works (`docker exec -i supabase_db_education-platform psql "<url>" ...`), which is how the rehearsal does it. Every pull request's CI rehearses this order on a throwaway database (`tools/backup_restore_check.sh`), so the day you need it, it's known to work.

**"Download my data"** on the live site (your name in the header) is still yours to take whenever you like; keep that file off this PC too, and never commit it: the repository is public.

## Never commit or paste into chat

- database passwords
- Supabase secret or service-role keys
- the Claude API key
- Cloudflare API tokens

They belong in a password manager, in the service's own secret settings, or in a gitignored `.env` file. The Supabase project URL and its publishable key are safe to share; they're designed to be public.
