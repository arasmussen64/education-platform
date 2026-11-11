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

- **Python Foundations** (`py.*`) was written by hand, topic by topic. All 36 of its topics are `ready`.
- **Machine Learning Foundations** (`ml.*`, [docs/specs/ml-foundations.md](../docs/specs/ml-foundations.md)) has Modules 1 to 8 `ready` and Module 9, transformers, outlined as `planned` topics; Module 10 is prose in the spec. Its topics build on Python Foundations topics by name (`prerequisites: [py.strings-and-input]`), so they unlock as the learner's Python does; the map reads those topics' progress along with the track's own. Its topics were not written file by file: all but one (`ml.math.vectors-and-matrices`) were first written by a generator, a script that holds a whole topic as text and writes the topic's files (from Module 4 on it also runs every program in the topic first, to capture its real output). Those scripts are archived in [tools/generators/](../tools/generators/README.md) as history. The files here in `content/topics/` are the source of truth: change a topic by editing them, never by re-running a generator, because most of the generators no longer match the content and would undo later fixes.
- **Cloud Solutions Architect** (`csa.*`) has Module 1, Linux and the command line, `ready`; the rest is an outline, where a topic is `planned` until it's written. The outlines are generated from the track's spec, [docs/specs/cloud-solutions-architect.md](../docs/specs/cloud-solutions-architect.md), by `tools/outline_cloud_track.py`. To change an outline, change the spec and run the script again (`python -m uv run python tools/outline_cloud_track.py`). Once a topic is being written, its `topic.yaml` loses the generated marker and the script leaves it alone from then on.

## A topic's life

| `status`  | Meaning                                                                                           |
| --------- | ------------------------------------------------------------------------------------------------- |
| `planned` | An outline: title, summary, prerequisites. It shows on the map, but there's nothing to learn yet. |
| `draft`   | Being written. Whatever exists is checked, but the topic isn't shown to learners.                 |
| `ready`   | Complete: learners see it. It must meet the content definition of done (below).                   |

## Writing a topic

1. Set `status: draft` and fill in `topic.yaml`: objectives, resources (each with its license, and whether we embed or link it), the explain prompt and rubric. If the topic's code imports a package beyond the standard library (NumPy, so far), list it under `packages:` ([ADR-0023](../docs/decisions/0023-packages-in-both-runtimes.md)); the browser loads it on first use, and the checker refuses an import the topic doesn't declare.

   Record each resource's license as its own source states it, read on the day you add it. Two licenses were recorded wrongly before, and one kind of link led to the wrong page. OpenStax books are CC BY-NC-SA 4.0: each book's preface says so, and the record reads `CC BY-NC-SA 4.0 (linked, not copied)`. Chapters of Python for Everybody are CC BY-NC-SA 3.0 by the book's copyright page, whatever the site's footer says. A 3Blue1Brown video is linked by its lesson page (`3blue1brown.com/lessons/...`), never by a series page (`/topics/...` redirects to the homepage), and each video gets a record of its own.

2. Write `lesson.mdx`: `<Intro>` (what to watch for), `<Resource index={0} />`, then `<Recap>`. The first resource in `topic.yaml` is the main one, shown in the lesson; any others are listed after the lesson as "More resources". Write your own explanations; never copy or paraphrase a resource's text.
3. Add the practice ladder: a worked example with labeled steps, then 2–3 recall items, a fill-in exercise, and a write exercise. Everything the build in step 4 needs appears here first: if the build uses a construct (`*args`, an attribute on a function, `argmin`), a practice item or the recap has already shown it.

   A Parsons problem (`type: parsons`: a short program's lines to put back in order, with a decoy or two) goes right after the worked example, where it does the most good. Write a prompt that says what the program prints, and make every line need the one before it, so there's exactly one right order. The validator proves it ([ADR-0016](../docs/decisions/0016-parsons-problems.md), amended): it tries the other orders of the lines (every order up to 7 lines; beyond that, every swap of two lines and every move of a run of lines) and each decoy in place of each line, and fails the item if any of them runs and prints the same output. Two shapes can always trade places, so avoid them: two set-up lines that don't use each other (join them, `a, b = ..., ...`, or build one from the other), and an import or a `def` beside a line that doesn't use it yet (make the line after an import use the module; a `def` whose own line doesn't use the import can always go above it, and two methods in one class can always trade places). An `assert` that passes can sit anywhere after the names it reads, so nothing may follow one in its block. If joining lines brings in syntax the learner hasn't met, the prompt says what it means.

   A fill-in's prompt may say "Until every `...` is replaced, Python can't run the program at all" only when that's true of every blank. A `...` in place of an operator, a keyword, a parameter or the name being assigned is a syntax error, which does stop Python before the program starts. A `...` where a value can stand (`len(...)`, `if ...:`, `x * ...`) is legal Python: the program runs, then stops with a `TypeError` that mentions `ellipsis`, or carries on and gives a wrong answer. Run the starter, and say in the prompt which blanks are which.

   A shell topic (the cloud track's Module 1) asks "what will it print?" with `predict_shell` items instead ([ADR-0017](../docs/decisions/0017-shell-in-the-browser.md)): a few small files, a command over them, and the output, which the validator proves by running the command in real bash. The command runs on Linux in CI and in Git Bash on the owner's PC, so keep it portable: no `jq` or `rev` (Git Bash has neither), no `ls -l`, `date`, `du`, `df` or `stat` (their output differs by machine), nothing that shows a path outside the folder, and `find` piped through `sort`. A command that writes to stderr fails the check; redirect an error you want shown with `2>&1`.

4. Add the proof: a build exercise (hidden tests, no starter), a debug exercise (a buggy starter), and the explain prompt. A debug's prompt gives what the program should do, the symptom the learner will see, and how many bugs there are. It never says what the bugs are or where they are: finding them is the exercise. This has been the rule since 2026-11-10. The earlier prompts that name their bugs are being rewritten to it a module at a time, cloud Module 1 first ([owner queue](../docs/owner-queue.md), "Decided for you").
5. Add a review pool: at least 3 items, at least one of them predict-the-output or a `review_code` exercise.
6. List the topic's **skills** in `topic.yaml`, and give every item `skills: [...]` with the skills it mainly tests. A missed question comes back later as a different question on the same skill ([ADR-0011](../docs/decisions/0011-mistakes-come-back.md)). So each skill needs at least 2 questions that can come back: recall items, or fill-in, write and `review_code` exercises. Aim for 3. Extra questions can go in the review pool.
7. Run the checker until it's clean, time the topic's Python exercises in the browser's Python (`npm run time:content -- <topic id>` in `web/`; see _Time limits_, below), then go through the topic once as a learner. The dev server (`npm run dev` in `web/`) shows drafts, so you can try it at `http://localhost:5173/topic/<topic-id>`. Then set `status: ready`. While the owner is the only learner, a topic can go straight to `ready`: their first pass, on the live site, is the review ([v1 spec](../docs/specs/v1.md#content-definition-of-done)).

**Topics that use NumPy** ([ADR-0023](../docs/decisions/0023-packages-in-both-runtimes.md)) declare `packages: [numpy]` in `topic.yaml`, and every printed result must be identical in the browser's Python and in CPython. The browser's NumPy is a 32-bit build, so don't print the `dtype` of a whole-number array (`int32` there, `int64` on a laptop). Trigonometry leaves `6e-17` where `0` was meant and sometimes `-0.`, so print `np.round(v, 6) + 0.0`. An eigenvector's sign and `eig`'s order differ between LAPACK builds, so use `eigh` for symmetric matrices (ascending, real), fix signs by hand before printing a vector, sort complex values, and otherwise print booleans from `np.allclose`. Pin every expected output by running the program under CPython before writing its test, and run every fill-in starter, as step 3 says.

A NumPy number inside a tuple, list or dictionary prints with its type around it, `np.float64(0.845)` (NumPy 2), which `ml.la.numpy-arrays` teaches once. When an exercise's expected output is a tuple or a list of numbers, the reference solution converts each one with `float()` (or `int()`, or `.tolist()` for a whole array), and the exercise carries a hint saying so. To check, run the solution with those conversions taken out and see what a learner who forgets them would be shown. Keep a whole-number NumPy number out of expected output in that form: it reads `np.int32(3)` in the browser and `np.int64(3)` on a laptop.

**Time limits.** The app stops a Run or a Check after an exercise's `time_limit_ms`: 5000 (5 seconds) when `exercise.yaml` doesn't set it, and 30000 at most. The validator can't tell you an exercise is too slow for the browser: it runs ordinary Python (CPython), which is faster than the browser's, and allows each program 20 seconds. So before marking a topic `ready`, run `npm run time:content -- <topic id>` in `web/` and keep every exercise under 40% of its limit. The start of an id works too (`ml.nn.` times every topic that begins that way), and the command marks each exercise that is over and ends with an error. Only Python exercises are timed. A lab runs in a container, not in the browser, so for a topic whose exercises are all labs (the cloud track's Module 1) the command says "No exercises found" and there is nothing to time. CI fails when a reference solution's Check, or a worked example's Run, takes more than 100% of the limit; the gap between 40% and 100% is the room a slower machine gets. The timing leaves out the first `import numpy` on a page, about half a second, which a learner's first Run or Check does pay inside the limit. The 40% margin covers it.

To bring a time down:

- If the solution does slow work as it loads (training a network, say), have the tests load it once per Check instead of calling `function()` in every test, which runs the file from the top each time. See `from_solution` in `content/topics/ml.nn.convolution/exercises/build-a-convolutional-layer/test_exercise.py`.
- Shrink the tests' data or step counts, then check that every known-wrong solution still fails.
- For a program that honestly needs longer, set `time_limit_ms` in its `exercise.yaml`, with a comment saying why.

If a prompt mentions the limit, it must state the real one.

## Writing a lab

A lab is an exercise that runs in a container on the learner's machine instead of in the browser ([ADR-0018](../docs/decisions/0018-lab-checker-local-mode.md)); the cloud track's Linux module uses them for every stage. Its `exercise.yaml` is the usual one plus `runtime: lab`, and its folder holds, instead of Python files:

- `Dockerfile`: start `FROM ubuntu:24.04`, add a `learner` user with passwordless `sudo`, copy in a `seed.sh` that builds the scenario deterministically (arithmetic on a loop counter, never randomness, so the checks can compute the truth from the data), run it, and end with `USER learner`, `WORKDIR /home/learner` and `CMD ["sleep", "infinity"]`. Keep the first `RUN` line (the packages and the users) identical across a topic's labs, so Docker builds that layer once for all of them.
- **A lab that needs systemd** (services, limits, boot) sets `lab: { init: systemd }` in `exercise.yaml`. The checker then starts the container privileged with `/sbin/init` and waits for the boot to finish. Its `Dockerfile` installs `systemd systemd-sysv dbus openssh-server` (D-Bus is what lets `systemctl` work for a user who isn't root; a real `sshd`, because every server has one and the permissions labs log in through it), puts the learner in the `adm` and `systemd-journal` groups so `journalctl` shows everything, as a cloud image's default user can, and ends with `CMD ["/sbin/init"]` and no `USER` line, since systemd must run as root; the learner's shell is opened as `learner` by `docker exec`. Every systemd lab starts from the same first `RUN` line, so Docker builds that layer once for all of them; when a topic needs another package, add it there and make the same edit in every systemd lab's `Dockerfile` (some seventy files), so the line stays identical in all of them. A tool only one topic needs (the triage labs' `sysstat` and `strace`) goes in a second `RUN` line that only that topic's labs carry, so the shared layer and the other labs don't change. These files were first put together from shared parts by a script, `tools/generators/cloud-labs/assemble.sh`. It is now an archive, one file behind the content, and must not be run against `content/`; [its README](../tools/generators/README.md#the-cloud-lab-parts) says what it would take to make it a tool again. Services and logs' labs are the pattern. Two things to know: a service that crashes at once and is restarted is "active" for a moment each time, so a check that a service runs should read `is-active` twice a couple of seconds apart with the same `MainPID`; and a `wrong/*.sh` that runs a `systemctl` command expected to fail must end that line with `|| true`, or the checker reports the script as broken rather than wrong.
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

1. Write the proof: the build (a small program, from a blank editor), the debug, and the explain prompt. On a checkpoint's page the explain check stays closed, prompt and all, until the build has passed ([ADR-0012](../docs/decisions/0012-checkpoint-support.md), amended 2026-11-10), so the prompt can't give the build away. Still, don't paste the build's solution into the prompt: one that leans less on the build's own code is better content. The debug's prompt follows the rule for any debug (_Writing a topic_, step 4): the symptom and the number of bugs, never what or where they are.
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

Tests that need a file (Module 6 on) create it first, with `Path("name.txt").write_text(...)`: nothing else is copied next to the learner's file, so a data file always comes from the test or from the program. `run()` leaves what the program wrote in place, so a test can `read_text` it afterwards. When a hidden test reads a file the program wrote, compare its lines (`read_text(...).splitlines()`), not the raw text, unless the final line break is the thing being tested: a missing last line break is invisible to the learner, and a hidden test gives no message. Where a missing line break is a real mistake (appending), make the test show it: append twice and compare the lines, as the notes-file build in `py.files` does.

Hidden tests (in build and `review_code` exercises) must fail with an `assert`, never crash. The page hides why a hidden test failed, but it shows a crash, because a crash is usually in the learner's own code. A crash inside the tests, like a `KeyError` from a missing line, would show how they work. The checker runs each hidden-test exercise on an empty program to catch this.

When an exercise could be passed by typing the expected output in by hand, add a test with `run_with`, which reruns the program with other starting values. A swap must then swap _any_ two values (see the Variables topic). Add the hand-typed version as a known-wrong solution, so the checker proves the test catches it.

The dev server watches `content/`, so new and changed files show up straight away.

To see the feedback a learner would get, copy an exercise's `test_exercise.py` and a starter or wrong answer (saved as `solution.py`) into an empty folder, then run `python -m uv run python harness/cli.py check <folder>`.

Tips for questions:

- The app shows a multiple-choice item's choices in a shuffled order, the same one each time the item comes back, so where the right answer sits in the file is never a clue. For the same reason, an explanation names a choice by what it says, never by where it sits ("the last choice"): the validator rejects a position.
- Choices, prompts and explanations are Markdown, so code goes in backticks: `` `print("Hi")` ``.
- Write explanations that say why the answer is right, and why the tempting wrong one is wrong.
- Quote error messages exactly as Python 3.14 prints them. Run the code through the harness to see them.

## Writing a diagnostic

A diagnostic ([ADR-0021](../docs/decisions/0021-placement-test.md)) is what the placement test walks when there's no track to walk yet: a ladder of levels, easiest first, each with a few original multiple-choice questions and a link to a free refresher. The shape is in the [data model](../docs/specs/data-model.md#diagnostics); `math.yaml` is the example.

- Three questions a level, each answerable in a minute without working on paper, each with distractors made from the common mistakes (adding the tops and bottoms of fractions; forgetting the chain rule). The test asks until two agree, so the third is a tie-breaker.
- The choices are shown shuffled, as in every multiple-choice item, so an explanation never names a choice by its position. The validator checks diagnostics for that too.
- The explanation is written for the result page of a future refresher, not for the test: the test shows nothing until the end.
- Levels are ordered so that being solid at one implies being solid at the ones before. The test depends on it: passing a level counts the levels below as known.

## Checking

From the repository root:

```text
python -m uv run python tools/validate_content.py            everything, including running all the code
python -m uv run python tools/validate_content.py --no-run   formats and structure only (fast)
```

And from `web/`, before a topic is marked `ready` (see _Time limits_, above):

```text
npm run time:content -- <topic id>                           the topic's exercises, timed in the browser's Python
```

Item IDs never change once a topic is `ready`, because learners' answers refer to them. To change an item meaningfully, bump its `rev`.
