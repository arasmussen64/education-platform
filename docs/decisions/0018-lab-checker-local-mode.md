# ADR-0018: The lab checker's local mode

- **Status:** Accepted by the owner on 2026-11-09 (the plan first, as "go" on local containers, GitHub's registry when needed and paste-first results; then the details below, once built and reviewed)
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

Checks are **read-only by convention**: they inspect files, run the learner's scripts and read service state; they never change the container. A lab that needs `systemd` says `lab: { init: systemd }` and the checker starts it privileged with `/sbin/init`. Most labs do: 69 of Module 1's 79 (this sentence first ended "the first labs don't", which was true of the first ten only; what privileged means is in the amendment of 2026-11-11).

### 2. The checker is `tools/labcheck.py`

A Python command-line tool in the repository, run with `python -m uv run python tools/labcheck.py …`, with the standard library plus PyYAML. It drives the `docker` command the learner already has:

- `start <topic> <exercise>` builds the image from the content folder (`lab-<topic>-<exercise>:r<rev>`), starts the container (`lab-<topic>-<exercise>`) and prints the command that opens a shell in it as the `learner` user.
- `check <topic> <exercise>` runs the checks with `docker exec`, prints each check's description and result, and prints the **result**: a short JSON object with the lab, its `rev`, the checker's version, the time, and which checks passed. `--json FILE` saves it too.
- `stop <topic> <exercise>` removes the container.
- Since the amendment of 2026-11-11: `shell <topic> <exercise>` opens the shell (`start` no longer prints a command to paste), `start` keeps a lab in progress unless given `--fresh`, and `status` and `stop --all` list and remove the labs it started.
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

## Amendment (2026-11-11): a shell command, a start that keeps the work, and what privileged means

- **Status:** Proposed. It is built as described here, for the owner to accept or change.

The decision had `start` print "the command that opens a shell", and said nothing about running `start` twice, about labs left running, or about what a privileged container may touch. An audit on 2026-11-10 found four things wrong with that. Each was then tried for real on the owner's PC before anything was changed:

- **The printed command failed in Git Bash.** It was `docker exec -it -u learner -w /home/learner <container> bash`. Git Bash rewrites an argument that looks like a path when it hands it to a Windows program, so `docker.exe` received `C:/Program Files/Git/home/learner` and answered `OCI runtime exec failed: exec failed: Cwd must be an absolute path`. The first step of the first lab failed, and nothing had ever run that command: CI and `test` don't use it.
- **`start` removed a lab in progress,** without a word, because it always began by removing the container of that name. Worse, `check` on a container that had stopped (as every container does when Docker Desktop or the computer restarts) said to run `start`. The tool's own advice destroyed the work.
- **"The first labs don't" need privileged containers** was true of the first ten labs only. 69 of the 79 boot systemd and so run privileged, and no document said what that means. In a storage lab, `lsblk` lists the disks of Docker's own Linux machine (`sda` to `sde`) beside the lab's disk.
- **The paste box recorded a pass for any result with one passing check,** whatever the check was called.

What is true now:

1. **`shell <topic> <exercise>` opens the lab's shell, as the learner, in their home.** The tool runs `docker exec` itself and hands Docker the arguments as a list, with no shell in between to rewrite a path. `start`, `check` and the lab page name this command; nothing tells the learner to type a `docker` command any more. What it does depends on what standard input is:
   - _A real console_ (PowerShell, Windows Terminal, and Git Bash's window in current versions of Git for Windows, which put a console behind it): an interactive shell with a prompt. On Windows the test is the one Docker applies, "does this handle have a console mode", because the usual test (`isatty`) also says yes to the `nul` device.
   - _A pipe or a file:_ the commands sent in are run, and nothing else is printed. This is what lets the shell be tested without a person.
   - _A Git Bash window with no console behind it_ (older versions of Git for Windows, or `MSYS=disable_pcon`): Docker would answer "the input device is not a TTY". The tool recognises the window by the name of its pipe (`\msys-…-pty0-from-master`) and says to run the same command in PowerShell or Windows Terminal, without asking Docker at all.

   Proven for real against Docker on the owner's PC: commands on standard input from Git Bash and from PowerShell (`whoami` gave `learner`, `pwd` gave `/home/learner`); an interactive session driven through a Windows pseudo console, which is what Windows Terminal and current Git Bash give a program (a prompt `learner@lab:~$`, `tty` gave `/dev/pts/0`, typed commands ran, `exit` came back); the prompt appearing inside a hidden Git Bash window as this PC has it installed; and the message inside a hidden Git Bash window started with `MSYS=disable_pcon`. Not proven: a person typing in a window on screen, and the older console window that PowerShell uses outside Windows Terminal.

2. **`start` never removes work by surprise.** A lab that is running is left alone. A lab that has stopped is started again with `docker start`, which keeps every file in it, and a lab that boots is waited for as on its first start. A paused lab is unpaused. Only `start --fresh` removes a container, and only once the new image has been built, so a build that fails costs nothing. A container that was started from another revision of the lab is refused, not removed, since the checks are for the new revision: the message says to use `--fresh`. `check` and `shell` on a stopped lab now say how to start it again and that the work is kept. One case does remove a container unasked: a brand-new lab that fails to come up (a boot that never finishes) is removed again, because it has no work in it and would otherwise be found by the next `start` and called running.

   Whether a restarted lab comes back healthy was tried on all 79 labs: the solution applied, the checks passed, the container killed (the hard case of a restart), started again, and the checks run again. Every lab booted again: 77 within seven seconds, and two storage labs after a minute and a half, because systemd waits that long for a disk named in `/etc/fstab`. 67 labs still passed every check. The other 12 had lost what a server loses in a reboot, and nothing on disk: a process started by hand, a control group, a mount (the storage labs need `sudo mount -a`), files on a memory-backed filesystem (the checkpoint's debug lab fills its data area again at boot, so that one fault comes back). So `start` says it this way: the lab came back like a server from a reboot, files and settings are as they were, what was only running or mounted may need doing again, and the checks show where you stand.

3. **The tool can find and stop every lab it started.** Each container carries two labels (a label is a name and value Docker stores with a container): `labcheck.lab`, the lab, and `labcheck.role`, which is `learner` for `start` and `test` for a contract run's throwaway container. `status` lists them with their state. `stop --all` removes the ones `start` made and leaves a test run's alone (`stop --all --tests` takes those too). Because it goes by label, it cannot touch a container this tool didn't start. `check` ends by saying the lab is still running and how to stop it; some labs are busy on purpose, and nothing else would stop a forgotten one.

   **Disks that dead labs left attached are let go of.** A storage lab's disks are image files attached to Docker's machine as loop devices (a loop device makes a file behave like a disk). They outlive a container that goes away without its teardown script: one removed from the Docker Desktop window, or one stopped by a restart and started again, which then has two of each disk. A later lab can then mount the dead lab's disk in place of its own. Before a lab with disks boots (one that ships a `teardown.sh`), `start` now runs a short-lived helper container that sees the whole of Docker's machine and detaches a lab disk only when the filesystem its image file is on is no longer mounted anywhere. That filesystem was a container's own, so the container is gone or stopped and nothing can reach the file again; a running lab's disks never qualify, whatever its container is called. The helper holds each device open while it decides, and the kernel will not detach or reuse a device that is held open, so a disk cannot change hands between the look and the letting go. It gives up without touching anything if it cannot see the machine's processes or if files do not report their filesystem's device. Tried on Docker Desktop while other containers were running: a running lab's disk was reported in use and left alone; a stopped lab's and a removed lab's were detached; a held-open device stayed attached when asked to detach and refused a second file. With `--fresh` it runs once the old container has been removed: a paused container can't run its teardown script (Docker refuses to run anything in it), so its disks only count as stale after it is gone. It runs only for `start` and for `stop` of a lab that had already stopped, never in `test`, so CI and parallel contract runs are untouched.

4. **The lab page says the same things.** It lists the commands as four steps (start, shell, check, stop), says that running `start` again keeps the work and that `--fresh` begins again, and shows `status` and `stop --all`. It also carries one sentence about what the lab's container may touch. For a lab that boots systemd: the container is privileged, which means Docker lets it reach the disks and settings of the machine Docker runs on, not only its own files; change only what the lab asks for; stop it with the `stop` command, not from the Docker Desktop window. For the other ten: an ordinary container, which cannot change files on the rest of the computer. The page reads `lab: { init: systemd }` from the lab's own `exercise.yaml`.

5. **A pasted result counts only when its checks are exactly the lab's own checks,** each once, in any order. Anything else records nothing and says to run `check` again, which is the right advice for the likely cause: a result made before the lab's checks changed. This is not a trust fix. Results are still unsigned, and someone who can type a result can type the right check names; signing before any second learner stays as section 3 says. What the rule does buy: a stale or partial result can no longer read as a pass, and the ticks on the page always belong to real checks.

6. **CI proves every lab once a week as well,** on `main`, with every image built from nothing. Section 4's pull-request run only happens when a pull request touches the labs or the checker, and every image is built from `ubuntu:24.04` and whatever packages `apt` serves that day, so a lab could break with nobody looking.

**What privileged means, and what it costs.** A privileged container has every permission the kernel can give and sees every device of the machine Docker runs on. With Docker Desktop that machine is a small Linux system Docker Desktop keeps running inside the computer, not Windows itself; on a Linux computer it is the computer. systemd is the reason the labs need it today: it wants to be the first process, to own a tree of control groups and to mount filesystems, and the storage and networking labs attach disks and build networks on top. The cost is that a mistyped command on the wrong device (`/dev/sdb` where `/dev/lab/data1` was meant) could damage Docker's own data. The page now says so in plain words. Running systemd with a short list of permissions in place of all of them has not been tried; it would be the next step if a second learner arrives.

**Alternatives considered.**

- _Printing the old command with `MSYS_NO_PATHCONV=1` in front._ That does keep the path intact in Git Bash, but it is one more thing to explain, it is wrong in PowerShell, and it still fails in a Git Bash window that has no console.
- _Asking "remove it? (y/n)" when `start` finds a lab in progress._ A prompt that destroys work on one keystroke is the same trap with a pause. Keeping is the default, and removing has a name.
- _Running `mount -a` for the learner after a restart._ The checker only reads (the Context above); it never changes a lab. And after a real reboot the learner would find out the same way.
- _Finding lab containers by name (`lab-…`) for `stop --all`._ It would also match a container somebody else named that way. Labels cannot.
- _Detaching every loop device whose file sits under the labs' folder._ That would pull a disk out from under a running lab; only "its filesystem is mounted nowhere" proves a disk is dead.
- _Detaching stale disks in `test` as well._ CI's machines start clean and a contract run always runs the teardown, so there is nothing to gain there and a shared Docker to disturb.

**Still open.** A container started by the tool before this change carries no label, so `status` and `stop --all` don't see it; `start`, `shell`, `check` and `stop` find it by name as before. `start` used to rebuild the image every time, so a lab whose files changed without a new revision was picked up by the next `start`; now the old container is kept until `--fresh`, which is one more reason to bump `rev` when a lab's meaning changes. The lab images are still built from an unpinned base image and unpinned packages; the weekly run notices a break, and pinning would prevent one. Results are still unsigned.
