# Setup

What's needed on the owner's computer and in the cloud. Tick things off as they're done.

## On this computer

| Tool | Why | Status |
|---|---|---|
| Git and GitHub CLI | Version control and pull requests | ✅ Installed |
| Node 24 and npm 11 | The web app | ✅ Installed |
| Python 3.12 | Content tools and, later, ML | ✅ Installed |
| Docker Desktop | Runs a private copy of Supabase for development ([ADR-0010](decisions/0010-environments.md)) | ☐ To do |
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
| Supabase | The real database and sign-in (one project) | ☐ Create the project |
| Cloudflare | Hosts the app | ☐ Create an account |
| Anthropic Console | The Claude API for the tutor and grading (week 2) | ☐ Later |

### Supabase

1. In your existing Supabase account, create a project named `education-platform` on the Free plan.
2. Save its database password in a password manager.
3. Choose the region closest to you.

This project is for real learning only. Development uses the local copy in Docker.

### Cloudflare

1. Sign up at dash.cloudflare.com/sign-up and verify your email.
2. Skip any prompt to add a domain. We'll use Cloudflare's free address.

Later, Cloudflare gets connected to the GitHub repo so every merge to `main` deploys automatically.

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
