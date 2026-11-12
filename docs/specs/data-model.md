# Data model

How content and learner data are stored, and how progress is computed.

- **Content** means lessons, exercises and the topic graph. It lives in git as files and is the same for every learner.
- **Learner data** lives in Postgres (Supabase) as a log of events that are never edited ([ADR-0008](../decisions/0008-event-log.md)).
- **Progress** (topic states and review schedules) is computed from those two and cached.

## Content files

### Layout

```text
content/
├── tracks/
│   ├── python-foundations.yaml
│   └── cloud-solutions-architect.yaml   generated from its spec by tools/outline_cloud_track.py
├── diagnostics/
│   └── math.yaml                 a ladder the placement test walks (ADR-0021)
└── topics/
    └── py.variables/
        ├── topic.yaml
        ├── lesson.mdx
        ├── recall/                   multiple-choice and predict-the-output items
        │   └── reassign-mcq.yaml
        └── exercises/
            └── fill-swap/
                ├── exercise.yaml
                ├── starter.py        empty for build; buggy for debug; with gaps for fill-in
                ├── solution.py       reference solution, never shown before the learner passes
                ├── test_exercise.py  the tests
                └── wrong/            known-wrong solutions; each one must fail
                    └── forgets-temp.py
```

### IDs and revisions

- Topic IDs look like `py.variables`. Item IDs are unique within their topic, so an item's full ID is `py.variables/fill-swap`.
- IDs never change once published, because events refer to them.
- Bump an item's `rev` when you change it meaningfully. Answers save the `rev` they were given (`item_rev`), so the versions can be told apart later, and answers to an earlier `rev` still count for progress and follow-ups ([ADR-0011](../decisions/0011-mistakes-come-back.md), amended 2026-11-11). To replace an item, add a new one and mark the old one `retired: true`.

### Track

```yaml
# content/tracks/python-foundations.yaml
id: python-foundations
title: Python Foundations
summary: From your first line of code to small, real programs you can build from a blank file.
order: 1 # where the track comes in the app, lowest first; each track has its own
modules:
  - id: py.m1
    title: First programs
    topics:
      [
        py.programs-and-print,
        py.values-and-types,
        py.variables,
        py.arithmetic,
        py.strings-and-input,
      ]
    checkpoint: py.m1.checkpoint
  # ...modules 2-6
```

A module may also name a **capstone**: a bigger checkpoint that ends a stage. It comes after the module's own checkpoint and builds on every module before it, so a ready capstone needs every earlier topic ready:

```yaml
- id: csa.m15
  title: Observability and operations
  topics: [csa.ops.telemetry, ...]
  checkpoint: csa.m15.checkpoint
  capstone: csa.capstone-1 # kind: checkpoint, like any checkpoint
```

The app shows the first track at `/map` and the others at `/map/<track id>`.

### Topic

```yaml
# content/topics/py.variables/topic.yaml
id: py.variables
kind: topic # topic | checkpoint
status: ready # planned (an outline on the map) | draft | ready (learners see it)
title: Variables
summary: Names that refer to values, and what assignment really does.
prerequisites: [py.values-and-types]
# packages: [numpy] # beyond the standard library; loaded on demand (ADR-0023)
estimated_minutes: 35
rev: 1
objectives:
  - Explain assignment using the "names refer to values" model.
  - Trace a sequence of assignments and predict each variable's value.
  - Swap the values of two variables.
resources: # the first is the main one, shown in the lesson
  - title: "CS50P Lecture 0: Functions, Variables"
    url: https://www.youtube.com/watch?v=VIDEO_ID
    type: video # video | reading | interactive
    use: embed # embed | link
    start: 1234 # seconds; videos only
    end: 1890
    license: CC BY-NC-SA 4.0
practice:
  [
    example-boxes-vs-labels,
    reassign-mcq,
    trace-three-assignments,
    fill-swap,
    write-rotate-three,
  ]
prove:
  build: build-swap-and-print
  debug: debug-lost-value
  explain:
    prompt: >
      What happens, step by step, when Python runs `b = a` and then `a = 5`?
      Why doesn't `b` change?
    rubric:
      - id: refers
        required: true
        description: Assignment makes a name refer to a value; it doesn't copy the value into a box.
      - id: rebinding
        required: true
        description: "`a = 5` points `a` at a new value; `b` still refers to the old one."
      - id: example
        required: false
        description: Uses a concrete example or a diagram.
    model_answer: >
      (used only by the grader; never shown to the learner)
review_pool: [reassign-mcq-2, trace-swap, review-swap-variant]
skills: # what the topic teaches (ADR-0011)
  - id: assignment
    description: "Explain assignment as names referring to values"
  - id: swap
    description: "Swap two values using a third name"
```

**Skills.** Every recall item and exercise lists the skills it mainly tests (`skills: [assignment]`); worked examples may leave it out, and any skills a worked example lists are ignored: it shows its answer as it goes, so it neither opens nor closes a follow-up ([ADR-0011](../decisions/0011-mistakes-come-back.md), amended 2026-11-11). A missed question comes back later as a _different_ question on the same skill ([ADR-0011](../decisions/0011-mistakes-come-back.md)). So in a ready topic, every skill needs at least 2 **follow-up candidates**: recall items, or fill-in, write and `review_code` exercises. Build and debug exercises name their skills too, but they're proof checks and never come back as follow-ups.

**Checkpoints** have no lesson, practice ladder, review pool or skills of their own. Instead, their tests name skills from the module's topics, and they have a way through for a learner who's stuck ([ADR-0012](../decisions/0012-checkpoint-support.md)):

```yaml
# content/topics/py.m1.checkpoint/topic.yaml (after the proof checks)
unstuck:
  example: example-shop-receipt # a solved sibling: a worked example in a different story
  steps: [step-read, step-work, step-print, step-outline] # the build in 3 or 4 fill-in steps, with hints
  versions: [build-split-bill, build-electricity] # at least 2 fresh versions of the build

# a checkpoint with further parts (ADR-0012, amended 2026-11-11): Checkpoint 2 as its plan has it, not yet written
prove:
  build: build-the-right-machine # part 1
  debug: debug-slow-vms # part 2
  more: # parts 3 on, each a build or debug of this checkpoint
    - id: build-stand-up-the-domain
      versions: [build-stand-up-the-domain-clinic] # a build part needs at least 1; a debug part may leave versions out
  explain: ...

# content/topics/py.m1.checkpoint/exercises/build-receipt/exercise.yaml (and every version, and the debug)
test_skills: # every test, by name: the skills it checks, as topic/skill
  test_subtotal: [py.strings-and-input/input-text, py.strings-and-input/convert]
  test_tip: [py.arithmetic/precedence, py.arithmetic/operators]
  test_two_decimals: [py.strings-and-input/fstrings]
```

A checkpoint's tests may name skills of its own module's topics and of earlier modules'.

Only checkpoints have `prove.more`. Its parts' tests name skills in `test_skills` like the build's, and no part or version may also be the build, the debug, the solved example, a step or a fresh version of the build.

### Recall items

````yaml
# content/topics/py.variables/recall/reassign-mcq.yaml
id: reassign-mcq
type: mcq # mcq | predict_output | parsons | predict_shell | estimate
rev: 1
prompt: |
  After this code runs, what is the value of `b`?
  ```python
  a = 3
  b = a
  a = 5
  ```
choices: ["3", "5", "It's an error"]
answer: 0
explanation: "`b = a` makes `b` refer to 3. Pointing `a` at 5 afterwards doesn't affect `b`."
skills: [assignment] # declared in topic.yaml
````

A `predict_output` item has `code` and `expected_output` instead of `choices` and `answer`. The validator runs the code and checks that the output matches exactly.

A `parsons` item ([ADR-0016](../decisions/0016-parsons-problems.md)) has `lines`, the program's lines in the right order with their indentation, and optional `distractors`, lines that don't belong. The app scrambles them and the learner puts them back; the answer is right when the lines are exactly the solution's, in order, with no decoy. The prompt must say what the program prints, so there's one right order. The validator runs the lines in order: the program must run without an error and without asking for input, the lines must be distinct, and no distractor may equal a line. It then tries other orders of the lines (every one, for an item of up to 7 lines), and each distractor in place of each line, and fails the item if any of them runs and prints the same output, because the app would mark that working program wrong (the ADR's amendment of 2026-11-10).

A `predict_shell` item ([ADR-0017](../decisions/0017-shell-in-the-browser.md)) is the same question for the command line. It has `files`, a few small text files by path (a plain name, or a path like `logs/app.log`; never absolute, never `..`; 4,000 characters in all at most), `command`, one line of bash or a few, and `expected_output`. The browser runs nothing: the page shows the files and the command and asks what it prints. The validator runs the command in real bash (Linux in CI, Git Bash on Windows) in a temporary folder holding just those files, with `LC_ALL=C`, an empty `HOME` and nothing on stdin, and checks that stdout is exactly `expected_output` and that stderr is empty. So an item must behave the same on both (no `jq` or `rev`, which Git Bash lacks; nothing that prints dates, sizes, user names or the folder's path), and an error it wants to show is redirected with `2>&1`.

An `estimate` item ([ADR-0024](../decisions/0024-estimate-questions.md)) asks for a number the learner works out and types. It has `unit` (shown after the box), `answer`, `tolerance` (exactly one of `absolute`, within that much either side, 0 meaning exactly, or `percent`, above 0 and at most 30, which needs an answer that isn't 0), `given` (the numbers the prompt states, by name; at least one), `working` (the sum over them that gives the answer), `mistakes` (at least one: `id`, `value`, `working`, `why`), and optionally `prices_as_of` and `prices_source` (both or neither, and both when the prompt holds an amount of money, which the validator recognises by a currency sign or code beside a number). Numbers must be YAML numbers written as plain digits; a `working` is text, so one that is a bare number is quoted. A given may not take the name of a function a working can call or a word Python keeps for itself (`in`, `if`). The validator works the sums out with exact fractions (`tools/arithmetic.py`, never `eval`), refusing any number of more than about 300 digits. It checks that the working, rounded to the answer's decimals, gives the answer and that its exact value lies inside the tolerance; that each mistake's working gives its value and that neither lies inside the tolerance (edges count as inside); that mistake values differ; and that every given number appears in the prompt. The page reads what is typed forgivingly (spaces, a sign, a currency sign in front, commas between groups of three, a % after a percentage). Anything else gets a note and isn't counted. A wrong answer within 0.5% of a mistake's value is shown that mistake's `why`. In review sessions and in the review-pool rule an estimate counts as code or predict.

### Diagnostics

A diagnostic ([ADR-0021](../decisions/0021-placement-test.md)) is a ladder the placement test walks the way it walks a track: a few questions from the middle level, and the answers rule out half of what's left. There's one so far, `math`, for the math the machine-learning track leans on.

```yaml
# content/diagnostics/math.yaml
id: math # must match the file name
title: Math for machine learning
summary: Where your math is solid and where to refresh it before the machine-learning track.
levels: # easiest first; at least 2
  - id: arithmetic
    title: Arithmetic, fractions and percentages
    summary: Fractions, decimals, percentages, negative numbers and the order of operations.
    refresh: # a free refresher, as a link; recorded like any resource (ADR-0004)
      title: "Khan Academy: Arithmetic"
      url: https://www.khanacademy.org/math/arithmetic
      type: interactive
      use: link
      license: CC BY-NC-SA 3.0 US (linked, not copied)
    items: # multiple-choice items, at least 2, no skills (there's no topic to relearn)
      - id: arithmetic-fractions
        type: mcq
        rev: 1
        prompt: What is 3/4 + 1/8?
        choices: ["4/12", "7/8", "5/8", "1/2"]
        answer: 1
        explanation: "..."
```

Item ids are unique across the whole diagnostic. As with every multiple-choice item, the app shows the choices in a repeatable shuffled order seeded from the item's id, so where the answer sits in the file doesn't matter; `choice` in the event is still the author's index. Events about a diagnostic use `diagnostic.<id>` as their `topic_id`.

### Exercises

```yaml
# content/topics/py.variables/exercises/fill-swap/exercise.yaml
id: fill-swap
stage: fill_in # worked_example | fill_in | write | build | debug | review_code
# runtime: python     # python (the default) | lab, a container on the learner's machine (below)
rev: 1
title: Swap two values
prompt: |
  Finish the program so it swaps `x` and `y`, then prints them.
time_limit_ms: 5000 # optional; 5000 is the default (see below)
hints: # written by the author; the tutor uses them as a guide
  - What happens to the original value of x when you assign to x?
  - You need somewhere to keep one value safe.
# steps:              # worked_example only: [{label, lines: "1-2", note}], labeled by purpose
```

`time_limit_ms` is how long the app lets a Run or a Check of the exercise take before it stops the program. Left out, it's 5000 (5 seconds). The content model allows up to 30000, for an exercise whose correct answer honestly needs longer, such as one that trains a network. CI times every ready exercise's reference solution in the browser's Python and fails when one runs past its limit ([content/README.md](../../content/README.md), _Time limits_).

How each stage behaves:

| Stage            | Starter code                                         | Tests shown       | Tutor |
| ---------------- | ---------------------------------------------------- | ----------------- | ----- |
| `worked_example` | none: `solution.py` is shown, with its labeled steps | yes               | on    |
| `fill_in`        | the solution with gaps (`...`); must fail            | yes               | on    |
| `write`          | empty, or a function signature                       | yes               | on    |
| `build`          | empty                                                | descriptions only | off   |
| `debug`          | buggy code; must fail                                | yes               | off   |
| `review_code`    | empty, or a function signature                       | descriptions only | off   |

### Labs

An exercise with `runtime: lab` ([ADR-0018](../decisions/0018-lab-checker-local-mode.md)) runs in a container on the learner's machine, started and checked by `tools/labcheck.py`. Its folder holds a `Dockerfile` (the scenario), `checks.yaml`, `solution.sh` and `wrong/*.sh` in place of the Python files; `lab: { init: systemd }` marks a lab whose container must boot systemd: the checker starts it privileged, in its own cgroup namespace, with `/sbin/init`, and waits for the boot to finish before running anything, and `restart_trial: true` beside it makes `labcheck test` restart the container once the solution passes and run every check again (ADR-0018, third amendment). A lab's `Dockerfile` may start `FROM lab-base-<name>`, a shared base in `content/lab-bases/<name>/` that the checker builds first. `checks.yaml`:

```yaml
checks:
  - id: failed-count # unique; what test_skills names in a checkpoint lab
    description: "failed-count.txt holds the number of 5xx requests."
    command: | # run inside the container as root; read-only
      [ "$(cat /home/learner/report/failed-count.txt)" = "$(awk '$3 ~ /^5/' /var/log/shop/access.log | wc -l)" ]
    # expect:                   # optional; without it, exit status 0 passes
    #   equals: "36"            # or contains, not_contains, matches, exit, lt, lte, gt, gte
    # timeout: 120              # optional; whole seconds from 1 to 300, default 30; a lab's checks 600 in all
```

The checker's result is a small JSON object the learner pastes into the lab's box: the lab (`topic/exercise`), its `rev`, the checker's version, the time, and which checks passed. The page records it as a `code_check` event with `data.runtime = "lab"`, so progress derivation treats a passed lab build or debug exactly like a passed Python one.

### Tests and the `checks` helper

Tests are plain Python functions named `test_…` that use `assert`. The first line of each test's docstring is what the learner sees.

```python
# test_exercise.py
from checks import run


def test_swaps():
    """Prints the swapped values."""
    assert run() == "5\n3\n"
```

The `checks` module lives in [`harness/`](../../harness/), which the browser and CI share, so tests behave the same everywhere:

- `run(stdin="")` runs the learner's program as a script, feeding it `stdin`, and returns what it printed. Prompts passed to `input()` are left out, so tests don't break over prompt wording. If the program wants more input than it was given, it gets an `EOFError`.
- `run_with({"x": "left", "y": "right"})` runs the program as if those names started with other values. It replaces each name's first assignment, like `x = 3`. Use it to check that code really works with its names, so retyping the expected values can't pass: for example, that a swap swaps _any_ two values. If a starting line is missing, the check fails with "Keep the line that gives x its starting value."
- Function exercises import from the learner's code: `from solution import rotate`. They must not read input or print at the top level.
- Give `assert` a message when the default would be unclear: `assert got == 4, f"double(2) should be 4, but it returned {got}"`. Without one, the learner sees the failing `assert` line.

In CI, the validator copies the reference solution (and then each wrong solution) to `solution.py` and runs the same test runner the browser uses (`harness/testrunner.py`), in a fresh Python process. It uses the same Python minor version as the pinned Pyodide release. It does not use pytest, because pytest rewrites `assert` statements and would change the messages.

### Lessons

`lesson.mdx` holds the AI-written intro and recap around the main resource. They're written ahead of time and reviewed like any other content.

```mdx
<Intro>What to watch for: ...</Intro>

<Resource index={0} />

<Recap>- ...</Recap>
```

## Learner data (Postgres)

Every table has row-level security: a learner can only read and write their own rows.

### `profiles`

| Column         | Type              | Notes                                                 |
| -------------- | ----------------- | ----------------------------------------------------- |
| `id`           | uuid, primary key | same as `auth.users.id`                               |
| `display_name` | text              |                                                       |
| `allowed`      | boolean           | default false; gates AI use while sign-ups are closed |
| `settings`     | jsonb             | e.g. the daily review limit                           |
| `created_at`   | timestamptz       |                                                       |

### `events` (append-only)

| Column          | Type              | Notes                                                                                                                                                  |
| --------------- | ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `id`            | uuid, primary key | created in the browser, so a retried upload can't duplicate it                                                                                         |
| `user_id`       | uuid              |                                                                                                                                                        |
| `type`          | text              | see the event types below                                                                                                                              |
| `topic_id`      | text              |                                                                                                                                                        |
| `item_id`       | text, nullable    | the item's ID within its topic                                                                                                                         |
| `context`       | text              | `learn`, `practice`, `prove`, `review`, or `placement` for an answer given during the placement test ([ADR-0021](../decisions/0021-placement-test.md)) |
| `correct`       | boolean, nullable | for graded events                                                                                                                                      |
| `duration_ms`   | integer, nullable |                                                                                                                                                        |
| `hints_used`    | integer           | default 0                                                                                                                                              |
| `item_rev`      | integer, nullable | the item's `rev` when it was answered                                                                                                                  |
| `content_build` | text              | the git commit the content was built from                                                                                                              |
| `session_id`    | uuid              | groups one study session                                                                                                                               |
| `occurred_at`   | timestamptz       | browser time (UTC); the learner's own day and time zone are in `data`                                                                                  |
| `received_at`   | timestamptz       | server time, default `now()`                                                                                                                           |
| `data`          | jsonb             | details for that event type, at most 128 KB (131,072 bytes, since migration `20261111164541`; 16 KB before)                                            |

Policies allow **insert** and **select** only. There is no update or delete policy.

| Event type                    | When                                                                                               | `data` holds                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| ----------------------------- | -------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `lesson_view`                 | a topic's lesson is opened                                                                         | `resource`: the main resource's URL                                                                                                                                                                                                                                                                                                                                                                                                           |
| `answer`                      | a multiple-choice, predict-the-output, Parsons or estimate item is answered                        | `choice` and `choice_text`, or `prediction`, or `program` (the lines in the order the learner left them), or for an estimate `typed` (what the learner typed), `number` (what it was read as), `relative_error` (how far off, as a signed share of the answer: 0.22 for 22% high; null when the answer is 0) and `mistake` (the id of the known mistake a wrong answer matched, or null). Text that can't be read as a number records nothing |
| `code_run`                    | the learner presses Run, or Step through ([ADR-0022](../decisions/0022-step-through.md))           | `code`; `outcome` (`done`, `timeout` or `failed`); `output`, `error` and `waiting_for_input` (or `message`). From Step through, also `stepped: true`, `steps` (how many were recorded) and `truncated`                                                                                                                                                                                                                                        |
| `code_check`                  | tests are run                                                                                      | `code`; `outcome`; `status`; `passed` and `total`; `failing` (test names); `message` if the tests couldn't run                                                                                                                                                                                                                                                                                                                                |
| `explain_submit`              | an explanation is sent to be checked (item `explain`)                                              | the text and `status`; when graded, the `verdict`, each rubric item's result, the `questions`, `ai_call_id` and `model`. `correct` is set only when graded ([ADR-0013](../decisions/0013-explain-grading.md))                                                                                                                                                                                                                                 |
| `hint`                        | a hint is shown, or a checkpoint's steps are opened (see below the table)                          | `level` (how many hints of that source so far); `source` (`author` for a written hint, `tutor` for one from the AI tutor). For the tutor ([ADR-0015](../decisions/0015-hint-only-tutor.md)): `rung` (`nudge`, `concept`, `specific` or `step`), `replaced` (whether the proxy swapped Claude's reply for a safer hint), the learner's `question`, `ai_call_id` and `model`                                                                    |
| `review`                      | a review session's items all have a first answer, from this visit or earlier ones (item `review`)  | `rating` (`good`, `hard` or `again`) and `items`: each item's ID and whether its first attempt was correct. `correct` is whether the rating was Good ([ADR-0009](../decisions/0009-reviews.md))                                                                                                                                                                                                                                               |
| `review`                      | a topic's review session ends                                                                      | item IDs; results; the rating                                                                                                                                                                                                                                                                                                                                                                                                                 |
| `answer`, context `placement` | a question is answered during the placement test ([ADR-0021](../decisions/0021-placement-test.md)) | the usual answer data, plus `run`, the run's id; for a diagnostic, `level` too; `dont_know: true` with a null `choice`, `prediction` or `program` (for an estimate, null `typed`, `number`, `relative_error` and `mistake`) when the learner chose "I don't know this" (counted as wrong). `topic_id` is the probed topic, or `diagnostic.<id>`                                                                                               |
| `placement`                   | a placement run ends (item `placement`, context `placement`)                                       | `run`; `kind` (`track` or `diagnostic`); `known`, the topics or levels in order that count as known; `next`, where to start, or null; `asked`, `correct`; `probes`, each topic or level probed with its questions and results. `topic_id` is the track's id or `diagnostic.<id>`; `correct` is null                                                                                                                                           |

**A Check that couldn't run** is saved with `correct` null and counts nowhere ([ADR-0008](../decisions/0008-event-log.md), amendment of 2026-11-11). That's when its `outcome` is `failed` (Python didn't start, a package didn't load, the worker crashed), or its `status` is `error` because the exercise's own tests couldn't be loaded, or it ran no tests (`status` `ok` and `total` 0). Code that runs past its time limit (`outcome` `timeout`) still counts as wrong. The rule is `checkCorrect` in `web/src/events/checkGrade.ts`, and `savedCheckCouldNotRun` in the same file applies it to Checks already saved.

**Opening a checkpoint's steps** is saved as a `hint` event with `source: "steps"` and no `level` ([ADR-0012](../decisions/0012-checkpoint-support.md), amended 2026-11-11). Its item is the checkpoint's build, and its context `prove`. It's saved the first time the steps open on each visit.

How the browser fills in the other columns:

- **`duration_ms`** (graded events): from the learner's first click or focus inside the item, or from their previous attempt at it, to this attempt. Time spent reading the lesson above doesn't count. The practice-hours tracker on the Today page adds these up, counting at most 30 minutes per attempt. A Check that couldn't run saves none, and its time carries on to the next attempt.
- **`hints_used`**: how many hints were showing at the time.
- **`session_id`**: a new study session starts when the app opens, and after 30 minutes without any events.
- **`content_build`**: the git commit the app was built from.
- **`occurred_at`**: the browser's clock when it happened. An event saved after time offline keeps its original time; `received_at` shows when it arrived.
- **`data.local_day` and `data.utc_offset_minutes`** (every event since 2026-11-11, [ADR-0008](../decisions/0008-event-log.md), amended): the learner's calendar day when it happened, like `"2026-11-06"`, and how many minutes their clock was ahead of UTC (`-480` in Los Angeles in winter, `330` in India). An event's day is its `local_day` when it has one that could be right (the UTC day or one either side of it). Older events have neither, and their day is the day on the viewing device's clock (`dayOf` in `web/src/days.ts`).

Code is kept whole up to 20,000 characters, and output, errors and messages up to 2,000, each cut with a marker that counts towards the limit (`web/src/events/payloads.ts`). A character takes up to three bytes, so even the worst event (about 72 KB) fits the 128 KB limit; the limit was 16 KB, with code cut at 6,000 characters, until migration `20261111164541_raise_event_data_limit.sql` (2026-11-11). Signed-out visitors' events aren't recorded at all.

#### Events the server refuses

Every event waits in the browser's outbox (a list in `localStorage`) until the server confirms it. If the browser won't let the page write to `localStorage` (it's full, or site data is switched off), the event waits in a second outbox in the page's memory instead and is sent from there in the same way. While any are unsent, the header says "Not saved yet: this device can't keep it if the page closes", because closing the page would lose them ([ADR-0008](../decisions/0008-event-log.md), amendment of 2026-11-11).

A send can fail in two ways:

- **A passing problem:** no connection, an expired sign-in, a busy or broken server (HTTP status 0, 401, 408, 429 or 5xx). The event stays in the outbox and is sent again after 5 seconds, then 10, and so on up to every 5 minutes.
- **A refusal:** any other status, which means the server wouldn't take the data itself. The usual cause is that the app is ahead of the database: it records a new kind of event before the migration that allows it has reached the server.

A refused event is never dropped. It moves from the outbox to a second list in `localStorage`, so that it can't hold up the events behind it, and it's kept there with the server's reason, the time of the last attempt, and the number of attempts.

The browser tries refused events again. After any save that goes through, it sends each of the signed-in learner's refused events whose last attempt was more than 12 hours ago, one at a time:

- **Accepted:** the event is on the server, so it leaves the refused list. Sending an event the server already has is harmless, because the server ignores an `id` it has seen.
- **Refused again:** it stays, with the new reason and time, and one more attempt counted.
- **A passing problem:** the browser stops and leaves the rest untouched until the next save.

Another learner's refused events on the same device are never sent, and never removed.

While a learner has refused events, the header says so ("3 pieces of your work couldn't be saved yet") and the account page explains it: the work exists only in that browser until it's saved, so it isn't on other devices and clearing the browser's site data would erase it. ["Download my data"](#the-export-file) includes it.

### `topic_progress` (derived cache)

One row per learner and topic. It can be deleted and rebuilt from `events` at any time.

| Column                                                    | Notes                                                                                    |
| --------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| `user_id`, `topic_id`                                     | primary key                                                                              |
| `build_passed_at`, `debug_passed_at`, `explain_passed_at` | first pass of each proof check                                                           |
| `learned_at`                                              | when the last of the three passed                                                        |
| `mastered_at`                                             | the first time it became Mastered                                                        |
| `last_review_at`, `last_review_rating`                    |                                                                                          |
| `card`                                                    | jsonb: the FSRS card (due date, stability, difficulty, reps, lapses, state, last review) |
| `updated_at`                                              |                                                                                          |

### `ai_calls` (append-only)

`id`, `user_id`, `created_at`, `action` (`tutor_hint` or `grade_explanation`), `model`, `input_tokens`, `output_tokens`, `cost_usd`, `request`, `response`.

Only the AI proxy writes to it, with the service role. A learner can read their own rows. Like `events`, rows are never updated or deleted, except when deliberately deleting a whole account. It's used to enforce the budget cap and to review the grader's and tutor's quality ([ADR-0013](../decisions/0013-explain-grading.md)).

- For `grade_explanation`, `request` holds the topic, the explanation and the prompt version. The rubric and model answer can be found from the topic. `response` holds the grading: the verdict, each rubric item, and the questions. Or, when Claude's answer couldn't be used, the problem.
- For `tutor_hint` ([ADR-0015](../decisions/0015-hint-only-tutor.md)), `request` holds the topic, the item, the rung (`level`), how many tutor hints came before (`hints_so_far`), the learner's question and code, and the prompt version. `response` holds the hint's text, its rung, and whether it was `replaced` by a safer hint (and why). Or the problem.
- `request` keeps to its column's 16 KB: the proxy cuts the logged code by bytes, not characters, so the whole request stays within 15,360 bytes. Every program in the track today is logged whole.
- When the database refuses a full row, the proxy writes a row with the spend alone (who, the action, the model, the tokens and the cost), so the budget cap still counts the call. If even that fails, no further call reaches Claude until it has been written ([ADR-0015](../decisions/0015-hint-only-tutor.md), amendment of 2026-11-11).
- `public.ai_spend_this_month()` adds up `cost_usd` since the start of this calendar month (UTC), across everyone. Only the proxy may call it.

### `problem_reports`

`id`, `user_id`, `created_at`, `topic_id`, `item_id`, `item_rev`, `message`, `status` (`open` or `resolved`).

A learner's note that something on a lesson, exercise or question is wrong ([F15](v1.md#f15-report-a-problem)). `item_id` is the item's ID within the topic, `lesson` or `explain` for the parts of a topic that aren't items, or null for the topic as a whole; `item_rev` is the item's `rev` at the time, so a report about an old version can be told apart from one about the current one. `message` is 1 to 2,000 characters.

Learners insert and read their own reports, and nothing else: `status` isn't in their insert grant, so every report starts `open`, and only the owner changes it, in the dashboard, once the content is fixed.

### The export file

"Export my data" ([F16](v1.md#f16-export-my-data)) downloads everything a learner has done as one JSON file, for backups and the ML capstone. The browser builds it: it reads the learner's profile and events from Supabase (row-level security returns only their own), and adds the events still waiting in the outbox. It reads the outbox first, so an event sent in between is on the server by then. It also lists the events the server has refused ([above](#events-the-server-refuses)), under a key of their own.

```json
{
  "format": 1,
  "exported_at": "2026-11-07T09:15:00.000Z",
  "content_build": "8c5f1ed",
  "user_id": "0b6e…",
  "profile": {
    "id": "0b6e…",
    "display_name": null,
    "allowed": false,
    "settings": {},
    "created_at": "2026-11-06T10:25:41.123456+00:00"
  },
  "events": [
    {
      "id": "8d1e…",
      "user_id": "0b6e…",
      "type": "answer",
      "topic_id": "py.programs-and-print",
      "item_id": "predict-four-lines",
      "context": "practice",
      "correct": false,
      "duration_ms": 41200,
      "hints_used": 0,
      "item_rev": 1,
      "content_build": "2fc7cce",
      "session_id": "5a90…",
      "occurred_at": "2026-11-06T10:42:13.123+00:00",
      "received_at": "2026-11-06T10:42:13.201456+00:00",
      "data": { "prediction": "Hello world" }
    }
  ],
  "refused_events": [
    {
      "reason": "400 23514: new row for relation \"events\" violates check constraint \"events_context_check\"",
      "last_tried_at": "2026-11-10T08:30:00.000Z",
      "attempts": 2,
      "event": {
        "id": "c41f…",
        "user_id": "0b6e…",
        "type": "answer",
        "topic_id": "py.variables",
        "item_id": "mcq-rebinding",
        "context": "placement",
        "correct": true,
        "duration_ms": 9300,
        "hints_used": 0,
        "item_rev": 1,
        "content_build": "8c5f1ed",
        "session_id": "77b2…",
        "occurred_at": "2026-11-09T20:14:02.511Z",
        "data": { "choice": 2, "run": "e09a…" }
      }
    }
  ]
}
```

- **`format`** is the layout's version. Adding a field doesn't change it. It changes when an existing field changes meaning, so scripts reading older files can tell them apart.
- **`events`** holds every column of the `events` table, oldest first. An event that was still in the outbox has `"received_at": null`.
- **`refused_events`** holds the events the server has refused, which only the browser that made the file has. Each entry gives the server's `reason` (the HTTP status, the database's error code and its message), `last_tried_at`, `attempts` (how many times it has been refused), and the `event` as it was sent, which has no `received_at`. They're kept out of `events` because they aren't part of the saved history yet: a script that rebuilds progress should read `events` alone. An event leaves this list, and appears in `events`, once a later try saves it. The list is empty in the normal case.
- **Times** are ISO 8601, in UTC, exactly as stored: the server writes `+00:00`, the browser `Z`.
- **Not in the file:** progress. It's left out on purpose: the app recalculates it from the events on every visit, so it can always be rebuilt from the events in this file ([F16](v1.md#f16-export-my-data)).

## Derived progress

Pure functions in `web/src/progress/progress.ts` compute progress from the topic outlines and the learner's graded events. `progressOf` finds when each proof check first passed, `withOpenFollowUps` notes which of each topic's skills are being relearned (see [Mistakes to revisit](#mistakes-to-revisit)), and `stateOf` gives a topic's state.

- A proof check passes with a passing Check of the topic's build or debug, or with an `explain_submit` event whose `correct` is true. A pass on any of a checkpoint's fresh versions counts as its build, and a pass of a further part (`prove.more`) or of any of that part's fresh versions counts as that part; `progressOf` records each part's first pass in `partsPassed`, only for checkpoints that have parts.
- Once the learner has opened a checkpoint's steps, a pass of its main build from after the first opening doesn't count; a fresh version's does. A checkpoint with no fresh version keeps counting its main build ([ADR-0012](../decisions/0012-checkpoint-support.md), amended 2026-11-11). The openings are `hint` events with `source: "steps"`, read alongside the graded events (`web/src/checkpoints/stepsOpened.ts`); only the earliest matters. History from before 2026-11-11 has none, so all its passes count.
- A Check with no verdict (one that couldn't run) isn't a graded event, so it counts for nothing here. Checks saved as wrong before 2026-11-11 that couldn't run are left out when the history is read (`savedCheckCouldNotRun` in `web/src/events/checkGrade.ts`, used by `web/src/followups/history.ts`); the stored rows don't change.
- Answers in the `placement` context are skipped: the placement test asks about topics the learner hasn't opened, and its answers must not make a topic In progress ([ADR-0021](../decisions/0021-placement-test.md)). The follow-ups skip them too, and so do the practice questions' Done and Tried marks on topic pages (`web/src/progress/itemStates.ts`). Practice hours count them.
- The result doesn't depend on the order of the events, so an event that arrives late, say from another device's outbox, changes only what it adds. Tests check this; it's what lets the app update progress as events arrive instead of rebuilding it.
- The app recalculates progress from the history each visit, like the follow-ups. The `topic_progress` cache comes when that gets slow.

### Regular topics

```text
learned  = build passed AND debug passed AND explain passed   (any order, any time)
fresh_at = the later of learned_at and the most recent review rated Again
mastered = learned
           AND a review rated Good happened at least 7 days after fresh_at
           AND the most recent review was not rated Again
           AND none of the topic's skills has an open follow-up

state =
  if not learned:
      Locked        if any prerequisite is not learned
      In progress   if the topic has any practice or proof attempt
      Available     otherwise
  else:
      Relearning    if the most recent review was rated Again
      Fading        if the review card is due
      Mastered      if mastered
      Learned       otherwise
```

- "In progress" and "Relearning" are finer-grained versions of ADR-0002's Available and Fading states, shown to help the learner.
- For gating, a prerequisite counts as learned in every learned state (Learned, Mastered, Fading, Relearning). A failed review never re-locks the topics built on it ([ADR-0002](../decisions/0002-mastery-and-gating.md)).
- A failed review (rated Again) starts Mastered's week over; Hard doesn't ([ADR-0002](../decisions/0002-mastery-and-gating.md), amended 2026-11-11). A question a Hard review got wrong does open a follow-up, which holds Mastered back by itself; a code item opens one only if no Check of it passed that day, as for any code under [Mistakes to revisit](#mistakes-to-revisit). The open follow-ups come from the same history, with the skill index described there. `useProgress` (`web/src/progress/useProgress.ts`) notes them on each topic's progress with `withOpenFollowUps`, and `stateOf` then shows such a topic as Learned rather than Mastered. A topic page reads only the history of the topic and its prerequisites, so a follow-up that a checkpoint's test opened, restarted or moved on can leave it showing a different state from the map and the Today page, which read the whole history.

### Checkpoints

Locked → Available → In progress → Passed, once all three proof checks pass and, on a checkpoint with further parts, every part in `prove.more` has passed too ([ADR-0012](../decisions/0012-checkpoint-support.md), amended 2026-11-11). A pass on any fresh version of the build counts as passing the build ([ADR-0012](../decisions/0012-checkpoint-support.md)). Once its steps have been opened, a pass of the main build no longer counts, only a fresh version's (the same ADR, amended 2026-11-11; see above). That rule is the main build's alone: a further part counts whenever it passed, since the steps don't show its program. The page opens a checkpoint's explain check only after its build has passed (the same ADR, amended 2026-11-10); its further parts don't hold it back; the calculation itself doesn't depend on the order. Checkpoints have no reviews.

### Mistakes to revisit

Details are in [ADR-0011](../decisions/0011-mistakes-come-back.md). They're worked out by `web/src/followups/followUps.ts`, from the learner's `answer` and `code_check` events and the `skills` of each item, so nothing is stored for them:

- Each item's outcome is judged per day. A question is missed if any answer to it that day was wrong. A code exercise is correct if any Check that day passed.
- An event's day is the learner's own recorded day where the event has one (`local_day`, since 2026-11-11), else the day on the viewing device's clock.
- A checkpoint's tests count for the skills they name ([ADR-0012](../decisions/0012-checkpoint-support.md)), in those skills' own topics. Each test is judged per day like code: missed if it failed in a Check and no Check that day passed it. The names of each Check's failing tests are in its event's `data.failing`. A Check whose tests couldn't run (`data.status` isn't `ok`) counts for none of them.
- Worked examples are no evidence either way: a lab walkthrough's Check neither opens nor closes a follow-up ([ADR-0011](../decisions/0011-mistakes-come-back.md), amended 2026-11-11).
- For each skill, day by day:
  - a missed day opens the follow-up (due the next day) and clears earlier progress;
  - a right day counts only if it's on or after the day the follow-up is due, and one of its right answers is on an item other than those missed when it last opened. A missed item counts only when every follow-up candidate on the skill was missed. A counted day makes it due again 3 days later, then 7; a right day that doesn't count changes nothing;
  - 3 counted days close it.
- Answers to an item's earlier `rev` count like any other, misses included.
- Each item's skills, stage and test skills come from the skill index built with the app (`virtual:skill-index`: `web/vite.config.ts` builds it from `content/`, and `web/src/followups/skillIndex.ts` reads it), so working out the follow-ups needs no topic content. Only items of topics that can be opened count. On the Today page, only the topics of the questions it shows download in full.

### Reviews

Details are in [ADR-0009](../decisions/0009-reviews.md). The scheduler is `web/src/reviews/fsrs.ts`: the FSRS-4.5 formulas and default parameters, a 90% target retention, and intervals capped at 365 days. It follows FSRS-4.5 exactly, with the two limits of FSRS-4.5's own code (a lapse never raises stability, and stability stays between 0.01 and 36,500 days), and its tests check it against py-fsrs 2.5.1, the Python package's FSRS-4.5 release (the ADR's amendment of 2026-11-11). The formulas are the platform's own code so they can be fitted to the owner's history in the ML capstone.

- A topic's card is replayed from its events each visit, like everything else here: it starts when the topic becomes Learned, which counts as a first review rated Good, and each `review` event after that updates it. Checkpoints have no cards.
- The card holds a **stability** (days until the chance of remembering drops to 90%) and a **difficulty** (1 to 10). The next review is due `stability` days after the last one, rounded, at least 1.
- Each review session rates the card from the **first** answer to each of its items: all correct is Good; some correct is Hard; none is Again. Every answer to an item of the topic's review pool saved with the context `review` since the topic fell due counts, whether it was given in a review session or as a mistakes-to-revisit question on Today, so a session left half-way still counts. The next visit shows those items as answered on an earlier visit and asks the rest; if earlier visits answered every item, the session is saved as soon as it shows. Earlier answers never make up a session without a code or predict-the-output item when the pool has one. Practice answers don't count.
- States after Learned, in this order: **Relearning** if the most recent review was Again; **Fading** if the review is due; **Mastered** if a review rated Good happened at least 7 days after the later of `learned_at` and the most recent review rated Again, and none of the topic's skills has an open follow-up; otherwise **Learned**.
- Today lists the topics whose review is due, the most forgotten first (lowest chance of remembering), up to 20 a day. The review sessions already finished that day, on the learner's own calendar day, count against the 20 (`reviewsLeftToday` in `web/src/reviews/reviews.ts`). When they're used up while topics are still due, Today says the day's reviews are done, and the rest wait for the next day. A session asks 2 items from the topic's review pool, at least one of them code, predict-the-output, Parsons or an estimate, the ones answered longest ago first, so sessions rotate through the pool.
