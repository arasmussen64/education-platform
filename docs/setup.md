# Setup

What's needed on the owner's computer and in the cloud. Tick things off as they're done.

## On this computer

| Tool | Why | Status |
|---|---|---|
| Git and GitHub CLI | Version control and pull requests | ✅ Installed |
| Node 24 and npm 11 | The web app | ✅ Installed |
| Python 3.12 | Content tools and, later, ML | ✅ Installed |
| Docker Desktop | Runs a private copy of Supabase for development ([ADR-0010](decisions/0010-environments.md)) | ✅ Installed |
| uv | Python package manager; also installs Python 3.14 | ✅ Installed (`python -m pip install --user uv`; run it as `python -m uv`) |

### Install Docker Desktop

1. In PowerShell, run `winget install -e --id Docker.DockerDesktop`, or download the installer from docker.com.
2. Restart the PC if asked.
3. Open Docker Desktop and accept the terms. It runs on WSL 2 (Windows Subsystem for Linux); if it offers to install or update WSL, say yes.
4. Check that it works: `docker run --rm hello-world` should print "Hello from Docker!"

Docker Desktop uses a few GB of memory while it's running, so quit it when you're not developing. It's free for personal use.

## In the cloud

| Service | Why | Status |
|---|---|---|
| GitHub | Code, pull requests, CI | ✅ Done |
| Supabase | The real database and sign-in (one project) | ✅ Project created; ☐ link it (`npx supabase login`) |
| Cloudflare | Hosts the app | ✅ Account created; ☐ connect the repo |
| Anthropic Console | The Claude API for the tutor and grading (week 2) | ☐ Later |

### Supabase

1. In your existing Supabase account, create a project named `education-platform` on the Free plan.
2. Save its database password in a password manager.
3. Choose the region closest to you.

This project is for real learning only. Development uses the local copy in Docker.

**Link it to the repo (one time).** In a terminal in the repository folder:

1. Run `npx supabase login`. It opens your browser to approve the CLI.
2. Run `npx supabase link --project-ref <ref>`. The ref is the code in your project's dashboard address: `supabase.com/dashboard/project/<ref>`. It asks for the database password.

After that, merged migrations are applied to the real database with `npx supabase db push`.

### Cloudflare

1. Sign up at dash.cloudflare.com/sign-up and verify your email.
2. Skip any prompt to add a domain. We'll use Cloudflare's free address.

**Connect the repo (one time),** so every merge to `main` deploys automatically. Cloudflare's wording may differ slightly from this:

1. In the Cloudflare dashboard, open **Workers & Pages** and choose **Create**, then **Import a repository** (or "Connect to Git").
2. Connect GitHub. When GitHub asks which repositories Cloudflare may access, choose **only** `education-platform`.
3. Use these settings:

   | Setting | Value |
   |---|---|
   | Project name | `education-platform` (must match `web/wrangler.jsonc`) |
   | Build command | `npm run build` |
   | Deploy command | `npx wrangler deploy` |
   | **Path**, under Advanced settings | `/web` (it starts as `/`) |

   Leave everything else at its default. There's no production-branch field: Cloudflare uses the repository's default branch, `main`. You can check it later under **Settings → Build → Branch control**.

4. Save and deploy. When the first build finishes, the app is live at `https://education-platform.<your-account>.workers.dev`.

Pull requests also get their own preview builds.

### Anthropic Console (week 2)

1. Create an account at console.anthropic.com and add billing.
2. Set a monthly spending limit of $10. This is on top of the app's own cap.
3. When we wire up the tutor, create an API key and store it only in Supabase's secret settings.

## Never commit or paste into chat

- database passwords
- Supabase secret or service-role keys
- the Claude API key
- Cloudflare API tokens

They belong in a password manager, in the service's own secret settings, or in a gitignored `.env` file. The Supabase project URL and its publishable key are safe to share; they're designed to be public.
