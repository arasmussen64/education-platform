# ADR-0018: The lab checker's local mode

- **Status:** Accepted in principle by the owner on 2026-11-09 ("go" on the plan: local containers, GitHub's registry when needed, paste-first results); the details below are proposed until reviewed
- **Date:** 2026-11-09

## Context

Module 1 of the Cloud Solutions Architect track, Linux and the command line, has all fourteen topics drafted: lessons, explain prompts, skills and 228 recall items. What keeps them from `ready` is the hands-on half that every topic needs ([ADR-0002](0002-mastery-and-gating.md)): a worked example, a fill-in and a write exercise, and the build and debug proofs. For Python those are editor exercises checked in the browser. For Linux, [ADR-0017](0017-shell-in-the-browser.md) decided they run **in containers on the learner's own machine**, checked by the **lab checker** that [ADR-0014](0014-cloud-labs.md) describes for cloud labs: a local tool that only reads, and reports which checks passed.

ADR-0014 settled the checker's principles (least privilege, credentials stay local, checks name skills, CI verifies the checks) but left its first concrete form open: how a lab is written, how the checker runs it, how results reach the platform, and how CI proves a lab the way it proves a Python exercise (the reference solution passes, every known-wrong solution fails, [ADR-0004](0004-content-model.md)).

The owner's machine has Docker Desktop and Git Bash. GitHub's Ubuntu runners have Docker. The platform's hosting stays free ([ADR-0005](0005-free-hosting-first.md)).

## Decision

### 1. A lab is an exercise with `runtime: lab`

Labs live where Python exercises live, `content/topics/<topic>/exercises/<id>/`, with the same `exercise.yaml` (`id`, `stage`, `rev`, `title`, `prompt`, `hints`, `steps`, `skills`, `test_skills`) plus `runtime: lab`. The stages keep their meanings: a worked example is a guided lab with labelled steps, fill-in and write are practice, build and debug are proofs, and the module checkpoint is a lab with planted faults. Every rule the validator applies to a topic's ladder (one worked example, two recall items, a fill-in, a write, a build, a debug, review pool, skills) applies unchanged, so a topic with labs goes `ready` by the same definition of done.

Instead of `starter.py`, `solution.py` and `test_exercise.py`, a lab folder holds:

| File | Role | Python equivalent |
|---|---|---|
| `Dockerfile` | The lab image: a base image, a `learner` user with `sudo`, and the scenario (files, services, planted faults), built deterministically by a `seed.sh` the image runs once | the starter |
| `checks.yaml` | The checks: each an `id`, a `description` the learner sees, a `command` run inside the container, and what it must produce (exit status 0 by default; or `expect` with `equals`, `contains`, `matches`, `not_contains`, `exit`, or a numeric `lt`/`lte`/`gt`/`gte`) | `test_exercise.py` |
| `solution.sh` | The reference fix, as the learner would type it, run inside a fresh container as the `learner` user; shown after a pass as "compare with a reference solution" | `solution.py` |
| `wrong/*.sh` | Known-wrong fixes; each must leave at least one check failing | `wrong/*.py` |

Checks are **read-only by convention**: they inspect files, run the learner's scripts and read service state; they never change the container. A lab that needs `systemd` says `lab: { init: systemd }` and the checker starts it privileged with `/sbin/init`; the first labs don't.

### 2. The checker is `tools/labcheck.py`

A Python command-line tool in the repository, run with `python -m uv run python tools/labcheck.py …`, with the standard library plus PyYAML. It drives the `docker` command the learner already has:

- `start <topic> <exercise>` builds the image from the content folder (`lab-<topic>-<exercise>:r<rev>`), starts the container (`lab-<topic>-<exercise>`) and prints the command that opens a shell in it as the `learner` user.
- `check <topic> <exercise>` runs the checks with `docker exec`, prints each check's description and result, and prints the **result**: a short JSON object with the lab, its `rev`, the checker's version, the time, and which checks passed. `--json FILE` saves it too.
- `stop <topic> <exercise>` removes the container.
- `test <topic> <exercise>` (or `--all`) is the **contract** ADR-0004 asks for, run for real: the pristine container must not pass every check; a fresh container with `solution.sh` applied must pass every check; a fresh container with each `wrong/*.sh` applied must fail at least one. It prints a report and exits non-zero on a broken contract.
- `list` names every lab in the content tree.

Images are **built locally from the content folder**. Publishing them to a registry is deferred: the owner is the only learner and has the repository. When a second learner needs images without the repository, CI will push them to GitHub's container registry (`ghcr.io`), the owner's choice; publishing makes them public, so it waits for that need.

### 3. Results reach the platform by paste, as a `code_check` event

The learner copies the result JSON that `check` prints into the lab's box on the topic page. The page verifies it is for this lab and this `rev`, shows the checks, and records one event. The event's type is **`code_check`**, the same as a Check of a Python exercise, with `data.runtime = "lab"`, the checker's version, the counts and the failing check ids. Progress derivation already turns a correct `code_check` on a topic's build or debug exercise into that proof, so labs count toward Learned with no change to the derivation and no change to the database (the `events` table limits `type` to a fixed list, and adding one would mean a production migration for no gain).

Results are unsigned while the owner is the only learner, as ADR-0014 allows. Before any public launch, the checker signs results with a token the learner gets while signed in, and the paste becomes optional.

### 4. CI proves every lab, with Docker

A `Labs` job on GitHub's Ubuntu runners runs `labcheck test --all` on every pull request: it builds each lab's image and runs the contract against real containers. That is stronger than the recorded responses ADR-0014 planned for cloud labs, because here CI has the thing itself; recordings remain the plan for labs that need a cloud account. The validator checks a lab's structure without Docker (`exercise.yaml`, `checks.yaml` and its ids, `solution.sh`, that `test_skills` names real check ids) and, with `--labs`, runs the same contract locally.

### 5. The tutor is off in labs for now

The tutor reads the learner's code and their last Check; a lab has neither in the browser. Written hints work as before. Hints from the tutor about a lab, fed the check results, are a later addition.

## Alternatives considered

- **A new event type `lab_check`.** Cleaner names, but a production migration, a change to progress derivation and to every place that lists event types, for an event that means exactly what `code_check` means: the learner's work was checked and this many checks passed. The `data` field carries the difference.
- **Publishing images from the start.** Needed only for a learner without the repository; costs a public package and a build-and-push workflow now. Deferred, with the registry chosen.
- **Checks as Python functions** (ADR-0014's phrasing for cloud checks). For a container, a shell command with an expectation is simpler to write, to read and to run with `docker exec`, and the learner can read `checks.yaml` the way they can read a Python test. Cloud checks that call cloud APIs will be Python, as the ADR says.
- **Running the checks inside the container as a script.** It would let a lab tamper with its own checks and would couple the check runner to each image. The checker stays outside and only asks.
- **A shell in the browser (v86) instead of containers.** Still the later enhancement ADR-0017 named; the local mode is the base it builds on.

## Consequences

- The fourteen Module 1 topics can go `ready` as their labs are written, starting with Shell essentials; the checkpoint's broken server is a debug lab at module scale.
- New things to maintain: the checker, a Dockerfile per lab, and the `Labs` CI job, which adds a minute or two per lab to a pull request's checks. If that grows, the job runs only when `content/**` or the checker changes.
- Learners need Docker and Git (for the repository) on their machine; the setup guide says so.
- The topic page gains a lab view: the commands to run, the checks, the paste box, and the reference solution after a pass.
- Module 1's topics stop being outline-only in the app: they're bundled in like the Python track's, since the Today page and the follow-ups look only at bundled topics.
