# Content

Everything learners see: tracks, topics, lessons and exercises, as plain files in git. The formats are defined in the [data model](../docs/specs/data-model.md#content-files). [`tools/validate_content.py`](../tools/validate_content.py) checks all of it on every pull request.

## Layout

```text
content/
├── tracks/<track-id>.yaml           modules, and which topics are in each; one file per track
├── diagnostics/<id>.yaml            a ladder the placement test walks, e.g. math (ADR-0021)
└── topics/<topic-id>/
    ├── topic.yaml                   metadata, prerequisites, resources, which items to use
    ├── lesson.mdx                   the AI-written intro and recap around the main resource
    ├── recall/<item>.yaml           multiple-choice, predict-the-output (Python or shell) and Parsons items
    └── exercises/<item>/
        ├── exercise.yaml
        ├── starter.py               fill-in and debug exercises (must fail the tests)
        ├── solution.py              the reference solution (must pass)
        ├── test_exercise.py         the tests
        └── wrong/*.py               known-wrong solutions (each must fail)
    └── exercises/<lab>/             a lab (runtime: lab in exercise.yaml, ADR-0018)
        ├── exercise.yaml
        ├── Dockerfile               the scenario: a base image, a learner user, seed.sh
        ├── checks.yaml              the checks: a command each, run inside the container
        ├── solution.sh              the reference fix (must pass every check)
        └── wrong/*.sh               known-wrong fixes (each must fail a check)
```

## Three tracks

- **Python Foundations** (`py.*`) is written by hand, topic by topic.
- **Machine Learning Foundations** (`ml.*`, [docs/specs/ml-foundations.md](../docs/specs/ml-foundations.md)) is written by hand too. Its topics build on Python Foundations topics by name (`prerequisites: [py.strings-and-input]`), so they unlock as the learner's Python does; the map reads those topics' progress along with the track's own. Its first two modules, the math refresher and intermediate Python, are outlined as `planned` topics in `content/topics/ml.*` and written one at a time; the later modules are prose in the spec until Phase 3.
- **Cloud Solutions Architect** (`csa.*`) is mostly an outline: a topic is `planned` until it's written, and Module 1's first topics are `draft` (lessons and recall now; the labs come when the lab checker's local mode exists, per [ADR-0017](../docs/decisions/0017-shell-in-the-browser.md)). The outlines are generated from the track's spec, [docs/specs/cloud-solutions-architect.md](../docs/specs/cloud-solutions-architect.md), by `tools/outline_cloud_track.py`. To change an outline, change the spec and run the script again (`python -m uv run python tools/outline_cloud_track.py`). Once a topic is being written, its `topic.yaml` loses the generated marker and the script leaves it alone from then on.

## A topic's life

| `status`  | Meaning                                                                                           |
| --------- | ------------------------------------------------------------------------------------------------- |
| `planned` | An outline: title, summary, prerequisites. It shows on the map, but there's nothing to learn yet. |
| `draft`   | Being written. Whatever exists is checked, but the topic isn't shown to learners.                 |
| `ready`   | Complete: learners see it. It must meet the content definition of done (below).                   |

## Writing a topic

1. Set `status: draft` and fill in `topic.yaml`: objectives, resources (each with its license, and whether we embed or link it), the explain prompt and rubric. If the topic's code imports a package beyond the standard library (NumPy, so far), list it under `packages:` ([ADR-0023](../docs/decisions/0023-packages-in-both-runtimes.md)); the browser loads it on first use, and the checker refuses an import the topic doesn't declare.
2. Write `lesson.mdx`: `<Intro>` (what to watch for), `<Resource index={0} />`, then `<Recap>`. The first resource in `topic.yaml` is the main one, shown in the lesson; any others are listed after the lesson as "More resources". Write your own explanations; never copy or paraphrase a resource's text.
3. Add the practice ladder: a worked example with labeled steps, then 2–3 recall items, a fill-in exercise, and a write exercise. A Parsons problem (`type: parsons`: a short program's lines to put back in order, with a decoy or two) goes right after the worked example, where it does the most good. Write a prompt that says what the program prints, so there's exactly one right order, and avoid lines that could swap places without changing the output; the validator runs the lines but can't spot an ambiguous order.

   A shell topic (the cloud track's Module 1) asks "what will it print?" with `predict_shell` items instead ([ADR-0017](../docs/decisions/0017-shell-in-the-browser.md)): a few small files, a command over them, and the output, which the validator proves by running the command in real bash. The command runs on Linux in CI and in Git Bash on the owner's PC, so keep it portable: no `jq` or `rev` (Git Bash has neither), no `ls -l`, `date`, `du`, `df` or `stat` (their output differs by machine), nothing that shows a path outside the folder, and `find` piped through `sort`. A command that writes to stderr fails the check; redirect an error you want shown with `2>&1`.

4. Add the proof: a build exercise (hidden tests, no starter), a debug exercise (a buggy starter), and the explain prompt.
5. Add a review pool: at least 3 items, at least one of them predict-the-output or a `review_code` exercise.
6. List the topic's **skills** in `topic.yaml`, and give every item `skills: [...]` with the skills it mainly tests. A missed question comes back later as a different question on the same skill ([ADR-0011](../docs/decisions/0011-mistakes-come-back.md)). So each skill needs at least 2 questions that can come back: recall items, or fill-in, write and `review_code` exercises. Aim for 3. Extra questions can go in the review pool.
7. Run the checker until it's clean, then go through the topic once as a learner. The dev server (`npm run dev` in `web/`) shows drafts, so you can try it at `http://localhost:5173/topic/<topic-id>`. Then set `status: ready`. While the owner is the only learner, a topic can go straight to `ready`: their first pass, on the live site, is the review ([v1 spec](../docs/specs/v1.md#content-definition-of-done)).

## Writing a lab

A lab is an exercise that runs in a container on the learner's machine instead of in the browser ([ADR-0018](../docs/decisions/0018-lab-checker-local-mode.md)); the cloud track's Linux module uses them for every stage. Its `exercise.yaml` is the usual one plus `runtime: lab`, and its folder holds, instead of Python files:

- `Dockerfile`: start `FROM ubuntu:24.04`, add a `learner` user with passwordless `sudo`, copy in a `seed.sh` that builds the scenario deterministically (arithmetic on a loop counter, never randomness, so the checks can compute the truth from the data), run it, and end with `USER learner`, `WORKDIR /home/learner` and `CMD ["sleep", "infinity"]`. Keep the first `RUN` line (the packages and the users) identical across a topic's labs, so Docker builds that layer once for all of them.
- **A lab that needs systemd** (services, limits, boot) sets `lab: { init: systemd }` in `exercise.yaml`. The checker then starts the container privileged with `/sbin/init` and waits for the boot to finish. Its `Dockerfile` installs `systemd systemd-sysv dbus openssh-server` (D-Bus is what lets `systemctl` work for a user who isn't root; a real `sshd`, because every server has one and the permissions labs log in through it), puts the learner in the `adm` and `systemd-journal` groups so `journalctl` shows everything, as a cloud image's default user can, and ends with `CMD ["/sbin/init"]` and no `USER` line, since systemd must run as root; the learner's shell is opened as `learner` by `docker exec`. Every systemd lab starts from the same first `RUN` line, so Docker builds that layer once for all of them; when a topic needs another package, add it there and regenerate every systemd lab's `Dockerfile`. A tool only one topic needs (the triage labs' `sysstat` and `strace`) goes in that topic's `tail-common` instead, so the shared layer and the other labs don't change. Services and logs' labs are the pattern. Two things to know: a service that crashes at once and is restarted is "active" for a moment each time, so a check that a service runs should read `is-active` twice a couple of seconds apart with the same `MainPID`; and a `wrong/*.sh` that runs a `systemctl` command expected to fail must end that line with `|| true`, or the checker reports the script as broken rather than wrong.
- **A lab that attaches things to Docker's machine** (the storage labs' disks are loop devices) puts a `teardown.sh` at `/usr/local/lib/lab/teardown.sh` that lets go of them (unmount, `losetup -d`); the checker runs it before removing the container, because removing a container leaves its loop devices attached. The storage labs' `disks.sh`, `teardown.sh` and `lab-grow` are the pattern: disks are image files attached at boot by a oneshot unit and labelled under `/dev/lab/`, so prompts and checks never depend on which loop number a disk got.
- **A lab with a network** (the networking labs) gets an "office" at boot: a network namespace joined to the lab machine by a veth pair, so `ip netns exec office COMMAND` (wrapped as `from-office`) is a connection from another machine arriving on `eth1`, and a firewall can be proved from outside without a second container. The lab machine runs its own name server (dnsmasq) and asks it, so names work on both sides; the container's `/etc/resolv.conf` is a mount Docker makes, which the boot script unmounts before writing its own. The networking labs' `network.sh`, `lab-network.service` and `from-office` are the pattern. A check that must tell _dropped_ from _refused_ times a `nc -z -w 2` attempt: a reset comes back in milliseconds, a drop takes the whole timeout.
- **A lab that stands in for a cloud instance** (the boot labs) runs cloud-init itself at the container's first boot, from a NoCloud seed under `/var/lib/cloud/seed/nocloud` that stands in for what a cloud's metadata service would hand over, with `ds-identify.cfg` set so cloud-init doesn't switch itself off as it does in a container. Three scripts stand in for the cloud console (`lab-launch` for a fresh instance, `lab-reboot` for the same one, `lab-imds-options` for the metadata options), and a small Python server (`lab-imds`) answers at `169.254.169.254`. The boot labs' `cloud.sh`, `lab-launch` and `lab-imds` are the pattern. Two things to know: the instance's own hostname must be in `/etc/hosts` or `sudo` and cloud-init stall for tens of seconds on a name lookup that can't succeed; and the console stand-ins must always exit 0, because whether an instance came up configured is for `cloud-init status` to report, not the wrapper's exit code (a `wrong/*.sh` that launches a still-broken config would otherwise be reported broken rather than wrong).
- **A plain lab** (`runtime: lab` with no `lab: { init: systemd }`) is the lighter kind: the checker runs the image's `sleep infinity` as the learner and execs the checks in, with no boot to wait for. The scripting labs are the pattern, and the first in the cloud track to use it: a small Ubuntu image with `shellcheck`, a `seed.sh` that lays down the scenery and the learner's starter or buggy script, and an identical first `RUN` across the five so Docker caches it. Their checks run `shellcheck` on the learner's script directly, so "run the linter" becomes something the contract enforces rather than advises.
- **A checkpoint's labs** (`csa.m1.checkpoint`) follow ADR-0012 in lab form: the build's and the debug's checks name the module skills they test in `test_skills` (check ids, not test functions); the solved sibling is a worked example in another story; each step is the build with the _other_ parts already done in the image, so the learner completes one part, and the last step is the whole build from an outline; the fresh versions are the build in other stories with their own images. The checks of the build, the steps and the versions are the same end state with the service and port swapped, so they're copies. Two things to know: a unit that's meant to fail on a bad config shouldn't carry `Restart=`, because a unit that can't exec only flaps between "activating" and a millisecond of "active" until systemd's start limit trips, which both hides the symptom and makes a plain `is-active` check racy (read it twice, a second apart); and a wrong fix should be an omission or a mistake (a part left out, a port missing, a file in the wrong folder), not a script of the shortcut the lab forbids.
- **Programs found by name** (`pgrep -x worker`, `ps -o comm`) need a direct shebang, `#!/bin/bash`: with `#!/usr/bin/env bash`, `env` runs bash a second time and the process is called `bash`, not `worker`. And a check that runs `pgrep -f some/path` matches its own command line, which contains that text; write the pattern as `some/pat[h]` so it doesn't.
- `checks.yaml`: a list of checks, each with an `id`, a `description` the learner sees, and a `command` run inside the container as root. Without an `expect`, exit status 0 is a pass; with one, compare the output (`equals`, `contains`, `not_contains`, `matches`, numeric `lt`/`lte`/`gt`/`gte`) or the exit status (`exit`). Checks only read. Where the right answer comes from the data, compute it in the check (`[ "$(cat the-learner's-file)" = "$(the pipeline over the data)" ]`) rather than hard-coding it.
- `solution.sh`: the reference fix, as the learner would type it, run by `labcheck test` as the learner in a fresh container. It's shown after a pass.
- `wrong/*.sh`: one file per likely mistake; each must leave at least one check failing. If a wrong fix passes, change the data until the mistake shows (the first lab's `uniq -c` without `sort` passed until `/home` stopped arriving in runs). When the number a check reads belongs to the whole machine rather than the container (`vmstat`'s columns, the load average, `free`: a container sees the host's), the data can't be changed and a busy CI runner will one day make the wrong column look right. Put a stand-in command with fixed numbers in the image and run the learner's script with that directory first in `PATH`, as the triage report's run-queue check does with `vmstat`.

Prove the contract with `python -m uv run python tools/labcheck.py test <topic> <lab>`: the pristine container must not pass, the solution must, every wrong fix must fail. CI's Labs workflow runs it for every lab, split by topic across four machines with four labs at a time on each (`test --all --jobs 4 --shard I/4`); the job named Labs is the one that must pass, and it does when every share did. A lab the checker gave up on in that crowd (a boot that didn't finish, a build that ran out of time) is retried once on its own afterwards; a check that fails or a wrong fix that passes never is. A check may wait a few seconds for something to happen (a line to reach the journal, a server to start listening) with a small retry loop, and it may start a throwaway process of its own when that's the only way to exercise the learner's script (a worker to stop, a runner to interrupt), cleaning up after itself; it must never change the learner's work. When what's being proved is how the learner's script behaves on a fresh state (a patch script on a fresh night), the first check may reset the scenario to that state before running it, as the Packages labs do, and must leave the machine as a correct script would. Then try it as a learner: `start`, open the shell it prints, do the work, `check`, paste the result into the lab's box on the dev server.

## Writing a checkpoint

A checkpoint ends a module: a bigger build, a debug with several bugs, and an explain that covers the whole module. It has no lesson, practice or review pool. Instead it has a way through for a learner who's stuck ([ADR-0012](../docs/decisions/0012-checkpoint-support.md)):

1. Write the proof: the build (a small program, from a blank editor), the debug, and the explain prompt.
2. In each build and debug, name the skills every test checks, as `topic/skill`, in `test_skills` (see the [data model](../docs/specs/data-model.md#topic)). A failed test brings those skills back on the learner's Today page. Write tests that each check one part of the program, so a failure points at the right skill.
3. Add `unstuck` to `topic.yaml`:
   - `example`: a **solved sibling**, a worked example of a similar program in a different story. Its labeled steps show how to break the problem into parts.
   - `steps`: the build itself, as **3 or 4 fill-in exercises with hints**. Each step gives the whole program except one part (read the inputs, work out the numbers, print the result); the last gives only an outline, as comments.
   - `versions`: **at least 2 fresh versions** of the build: the same skills in different stories, about as hard. Their tests name skills too.
4. A checkpoint can be `ready` only once every topic in its module is.

Tests that point at the right skill (see Checkpoint 1's builds):

- **Value tests** read the numbers whatever their format, and check them against the program's own earlier lines. Then one wrong number fails one test, not every test after it.
- **Inputs with decimals** go only in the test that reads them. Then `int()` where `float()` is needed fails only that test, not the arithmetic tests.
- **One test checks the format** (two decimal places), and **one the layout**: the words and spaces, with every number replaced.
- **Add a known-wrong answer for each likely mistake**, and check that it fails only the test for that mistake. When the function is random, the test must sample enough times that the mistake can't hide: ten dice rolls let a 0-to-6 range through one run in five; two hundred never do. Copy each wrong answer and the tests into an empty folder, then run `harness/cli.py check` (see below).

Tips for tests: give each test a one-line docstring, which is what the learner sees, and give `assert` a message when the default wouldn't be clear. See [harness/README.md](../harness/README.md).

Tests of functions (Module 4 on) load the learner's function with `function("name")` from `checks`, never with `from solution import name` at the top of the file: a missing function then fails one test with "Define a function called name", instead of stopping every test with an import error. `printed(f, *args)` captures what a call prints. A program whose functions are tested should call `main()` only under `if __name__ == "__main__":`, so loading it for the tests doesn't run it (and doesn't ask for input).

Tests that need a file (Module 6 on) create it first, with `Path("name.txt").write_text(...)`: nothing else is copied next to the learner's file, so a data file always comes from the test or from the program. `run()` leaves what the program wrote in place, so a test can `read_text` it afterwards.

Hidden tests (in build and `review_code` exercises) must fail with an `assert`, never crash. The page hides why a hidden test failed, but it shows a crash, because a crash is usually in the learner's own code. A crash inside the tests, like a `KeyError` from a missing line, would show how they work. The checker runs each hidden-test exercise on an empty program to catch this.

When an exercise could be passed by typing the expected output in by hand, add a test with `run_with`, which reruns the program with other starting values. A swap must then swap _any_ two values (see the Variables topic). Add the hand-typed version as a known-wrong solution, so the checker proves the test catches it.

The dev server watches `content/`, so new and changed files show up straight away.

To see the feedback a learner would get, copy an exercise's `test_exercise.py` and a starter or wrong answer (saved as `solution.py`) into an empty folder, then run `python -m uv run python harness/cli.py check <folder>`.

Tips for questions:

- Vary which choice is the right one, so its position is never a clue.
- Choices, prompts and explanations are Markdown, so code goes in backticks: `` `print("Hi")` ``.
- Write explanations that say why the answer is right, and why the tempting wrong one is wrong.
- Quote error messages exactly as Python 3.14 prints them. Run the code through the harness to see them.

## Writing a diagnostic

A diagnostic ([ADR-0021](../docs/decisions/0021-placement-test.md)) is what the placement test walks when there's no track to walk yet: a ladder of levels, easiest first, each with a few original multiple-choice questions and a link to a free refresher. The shape is in the [data model](../docs/specs/data-model.md#diagnostics); `math.yaml` is the example.

- Three questions a level, each answerable in a minute without working on paper, each with distractors made from the common mistakes (adding the tops and bottoms of fractions; forgetting the chain rule). The test asks until two agree, so the third is a tie-breaker.
- The choices are shown in the order written, so vary where the right answer sits.
- The explanation is written for the result page of a future refresher, not for the test: the test shows nothing until the end.
- Levels are ordered so that being solid at one implies being solid at the ones before. The test depends on it: passing a level counts the levels below as known.

## Checking

From the repository root:

```text
python -m uv run python tools/validate_content.py            everything, including running all the code
python -m uv run python tools/validate_content.py --no-run   formats and structure only (fast)
```

Item IDs never change once a topic is `ready`, because learners' answers refer to them. To change an item meaningfully, bump its `rev`.
