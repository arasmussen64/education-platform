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
│   └── python-foundations.yaml
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
- Bump an item's `rev` when you change it meaningfully. To replace an item, add a new one and mark the old one `retired: true`.

### Track

```yaml
# content/tracks/python-foundations.yaml
id: python-foundations
title: Python Foundations
modules:
  - id: py.m1
    title: First programs
    topics: [py.programs-and-print, py.values-and-types, py.variables, py.arithmetic, py.strings-and-input]
    checkpoint: py.m1.checkpoint
  # ...modules 2-6
```

### Topic

```yaml
# content/topics/py.variables/topic.yaml
id: py.variables
kind: topic                     # topic | checkpoint
status: ready                   # planned (an outline on the map) | draft | ready (learners see it)
title: Variables
summary: Names that refer to values, and what assignment really does.
prerequisites: [py.values-and-types]
estimated_minutes: 35
rev: 1
objectives:
  - Explain assignment using the "names refer to values" model.
  - Trace a sequence of assignments and predict each variable's value.
  - Swap the values of two variables.
resources:                      # the first is the main one, shown in the lesson
  - title: "CS50P Lecture 0: Functions, Variables"
    url: https://www.youtube.com/watch?v=VIDEO_ID
    type: video                 # video | reading | interactive
    use: embed                  # embed | link
    start: 1234                 # seconds; videos only
    end: 1890
    license: CC BY-NC-SA 4.0
practice: [example-boxes-vs-labels, reassign-mcq, trace-three-assignments, fill-swap, write-rotate-three]
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
skills:                         # what the topic teaches (ADR-0011)
  - id: assignment
    description: "Explain assignment as names referring to values"
  - id: swap
    description: "Swap two values using a third name"
```

**Skills.** Every recall item and exercise lists the skills it mainly tests (`skills: [assignment]`); worked examples may leave it out. A missed question comes back later as a *different* question on the same skill ([ADR-0011](../decisions/0011-mistakes-come-back.md)). So in a ready topic, every skill needs at least 2 **follow-up candidates**: recall items, or fill-in, write and `review_code` exercises. Build and debug exercises name their skills too, but they're proof checks and never come back as follow-ups.

**Checkpoints** have no lesson, practice ladder, review pool or skills of their own. Instead, their tests name skills from the module's topics, and they have a way through for a learner who's stuck ([ADR-0012](../decisions/0012-checkpoint-support.md)):

```yaml
# content/topics/py.m1.checkpoint/topic.yaml (after the proof checks)
unstuck:
  example: example-shop-receipt           # a solved sibling: a worked example in a different story
  steps: [step-read, step-work, step-print, step-outline]  # the build in 3 or 4 fill-in steps, with hints
  versions: [build-split-bill, build-electricity]          # at least 2 fresh versions of the build

# content/topics/py.m1.checkpoint/exercises/build-receipt/exercise.yaml (and every version, and the debug)
test_skills:                              # every test, by name: the skills it checks, as topic/skill
  test_subtotal: [py.strings-and-input/input-text, py.strings-and-input/convert]
  test_tip: [py.arithmetic/precedence, py.arithmetic/operators]
  test_two_decimals: [py.strings-and-input/fstrings]
```

A checkpoint's tests may name skills of its own module's topics and of earlier modules'.

### Recall items

```yaml
# content/topics/py.variables/recall/reassign-mcq.yaml
id: reassign-mcq
type: mcq                       # mcq | predict_output
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
skills: [assignment]            # declared in topic.yaml
```

A `predict_output` item has `code` and `expected_output` instead of `choices` and `answer`. The validator runs the code and checks that the output matches exactly.

### Exercises

```yaml
# content/topics/py.variables/exercises/fill-swap/exercise.yaml
id: fill-swap
stage: fill_in        # worked_example | fill_in | write | build | debug | review_code
rev: 1
title: Swap two values
prompt: |
  Finish the program so it swaps `x` and `y`, then prints them.
time_limit_ms: 5000
hints:                # written by the author; the tutor uses them as a guide
  - What happens to the original value of x when you assign to x?
  - You need somewhere to keep one value safe.
# steps:              # worked_example only: [{label, lines: "1-2", note}], labeled by purpose
```

How each stage behaves:

| Stage | Starter code | Tests shown | Tutor |
|---|---|---|---|
| `worked_example` | none: `solution.py` is shown, with its labeled steps | yes | on |
| `fill_in` | the solution with gaps (`...`); must fail | yes | on |
| `write` | empty, or a function signature | yes | on |
| `build` | empty | descriptions only | off |
| `debug` | buggy code; must fail | yes | off |
| `review_code` | empty, or a function signature | descriptions only | off |

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
- `run_with({"x": "left", "y": "right"})` runs the program as if those names started with other values. It replaces each name's first assignment, like `x = 3`. Use it to check that code really works with its names, so retyping the expected values can't pass: for example, that a swap swaps *any* two values. If a starting line is missing, the check fails with "Keep the line that gives x its starting value."
- Function exercises import from the learner's code: `from solution import rotate`. They must not read input or print at the top level.
- Give `assert` a message when the default would be unclear: `assert got == 4, f"double(2) should be 4, but it returned {got}"`. Without one, the learner sees the failing `assert` line.

In CI, the validator copies the reference solution (and then each wrong solution) to `solution.py` and runs the same test runner the browser uses (`harness/testrunner.py`), in a fresh Python process. It uses the same Python minor version as the pinned Pyodide release. It does not use pytest, because pytest rewrites `assert` statements and would change the messages.

### Lessons

`lesson.mdx` holds the AI-written intro and recap around the main resource. They're written ahead of time and reviewed like any other content.

```mdx
<Intro>
What to watch for: ...
</Intro>

<Resource index={0} />

<Recap>
- ...
</Recap>
```

## Learner data (Postgres)

Every table has row-level security: a learner can only read and write their own rows.

### `profiles`

| Column | Type | Notes |
|---|---|---|
| `id` | uuid, primary key | same as `auth.users.id` |
| `display_name` | text | |
| `allowed` | boolean | default false; gates AI use while sign-ups are closed |
| `settings` | jsonb | e.g. the daily review limit |
| `created_at` | timestamptz | |

### `events` (append-only)

| Column | Type | Notes |
|---|---|---|
| `id` | uuid, primary key | created in the browser, so a retried upload can't duplicate it |
| `user_id` | uuid | |
| `type` | text | see the event types below |
| `topic_id` | text | |
| `item_id` | text, nullable | the item's ID within its topic |
| `context` | text | `learn`, `practice`, `prove` or `review` |
| `correct` | boolean, nullable | for graded events |
| `duration_ms` | integer, nullable | |
| `hints_used` | integer | default 0 |
| `item_rev` | integer, nullable | the item's `rev` when it was answered |
| `content_build` | text | the git commit the content was built from |
| `session_id` | uuid | groups one study session |
| `occurred_at` | timestamptz | browser time |
| `received_at` | timestamptz | server time, default `now()` |
| `data` | jsonb | details for that event type, at most 16 KB |

Policies allow **insert** and **select** only. There is no update or delete policy.

| Event type | When | `data` holds |
|---|---|---|
| `lesson_view` | a topic's lesson is opened | `resource`: the main resource's URL |
| `answer` | a multiple-choice or predict-the-output item is answered | `choice` and `choice_text`, or `prediction` |
| `code_run` | the learner presses Run | `code`; `outcome` (`done`, `timeout` or `failed`); `output`, `error` and `waiting_for_input` (or `message`) |
| `code_check` | tests are run | `code`; `outcome`; `status`; `passed` and `total`; `failing` (test names); `message` if the tests couldn't run |
| `explain_submit` | an explanation is graded | the text; the verdict; rubric results; `ai_call_id` |
| `hint` | a hint is shown | `level`; `source` (`author` for the written hints, until the tutor exists); later `ai_call_id` |
| `review` | a topic's review session ends | item IDs; results; the rating |

How the browser fills in the other columns:

- **`duration_ms`** (graded events): from the learner's first click or focus inside the item, or from their previous attempt at it, to this attempt. Time spent reading the lesson above doesn't count.
- **`hints_used`**: how many hints were showing at the time.
- **`session_id`**: a new study session starts when the app opens, and after 30 minutes without any events.
- **`content_build`**: the git commit the app was built from.
- **`occurred_at`**: the browser's clock when it happened. An event saved after time offline keeps its original time; `received_at` shows when it arrived.

Code and output are cut to 6,000 and 2,000 characters, so every event fits the 16 KB limit. Signed-out visitors' events aren't recorded at all.

### `topic_progress` (derived cache)

One row per learner and topic. It can be deleted and rebuilt from `events` at any time.

| Column | Notes |
|---|---|
| `user_id`, `topic_id` | primary key |
| `build_passed_at`, `debug_passed_at`, `explain_passed_at` | first pass of each proof check |
| `learned_at` | when the last of the three passed |
| `mastered_at` | the first time it became Mastered |
| `last_review_at`, `last_review_rating` | |
| `card` | jsonb: the FSRS card (due date, stability, difficulty, reps, lapses, state, last review) |
| `updated_at` | |

### `ai_calls` (append-only)

`id`, `user_id`, `created_at`, `action` (`tutor_hint` or `grade_explanation`), `model`, `input_tokens`, `output_tokens`, `cost_usd`, `request`, `response`.

Only the AI proxy writes to it, with the service role. A learner can read their own rows. Like `events`, rows are never updated or deleted, except when deliberately deleting a whole account. It's used to enforce the budget cap and to review the grader's and tutor's quality ([ADR-0013](../decisions/0013-explain-grading.md)).

- `request` holds the topic, the explanation and the prompt version. The rubric and model answer can be found from the topic.
- `response` holds the grading: the verdict, each rubric item, and the questions. Or, when Claude's answer couldn't be used, the problem.
- `public.ai_spend_this_month()` adds up `cost_usd` since the start of this calendar month (UTC), across everyone. Only the proxy may call it.

### `problem_reports`

`id`, `user_id`, `created_at`, `topic_id`, `item_id`, `item_rev`, `message`, `status` (`open` or `resolved`).

### The export file

"Export my data" ([F16](v1.md#f16-export-my-data)) downloads everything a learner has done as one JSON file, for backups and the ML capstone. The browser builds it: it reads the learner's profile and events from Supabase (row-level security returns only their own), and adds the events still waiting in the outbox. It reads the outbox first, so an event sent in between is on the server by then.

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
  ]
}
```

- **`format`** is the layout's version. Adding a field doesn't change it. It changes when an existing field changes meaning, so scripts reading older files can tell them apart.
- **`events`** holds every column of the `events` table, oldest first. An event that was still in the outbox has `"received_at": null`.
- **Times** are ISO 8601, in UTC, exactly as stored: the server writes `+00:00`, the browser `Z`.
- **Not in the file yet:** progress, until Milestone B computes it (it can always be rebuilt from the events); and events the server refused, which stay in the browser for investigation.

## Derived progress

Pure functions in `web/src/progress/progress.ts` compute progress from the topic outlines and the learner's graded events. `progressOf` finds when each proof check first passed, and `stateOf` gives a topic's state.

- A proof check passes with a passing Check of the topic's build or debug, or with an `explain_submit` event whose `correct` is true. A pass on any of a checkpoint's fresh versions counts as its build.
- The result doesn't depend on the order of the events, so an event that arrives late, say from another device's outbox, changes only what it adds. Tests check this; it's what lets the app update progress as events arrive instead of rebuilding it.
- The app recalculates progress from the history each visit, like the follow-ups. The `topic_progress` cache comes when that gets slow.

### Regular topics

```text
learned  = build passed AND debug passed AND explain passed   (any order, any time)
mastered = learned
           AND a review rated Good happened at least 7 days after learned_at
           AND the most recent review was not rated Again

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

### Checkpoints

Locked → Available → In progress → Passed, once all three proof checks pass. A pass on any fresh version of the build counts as passing the build ([ADR-0012](../decisions/0012-checkpoint-support.md)). Checkpoints have no reviews.

### Mistakes to revisit

Details are in [ADR-0011](../decisions/0011-mistakes-come-back.md). They're worked out by `web/src/followups/followUps.ts`, from the learner's `answer` and `code_check` events and the `skills` of each item, so nothing is stored for them:

- Each item's outcome is judged per day. A question is missed if any answer to it that day was wrong. A code exercise is correct if any Check that day passed.
- A checkpoint's tests count for the skills they name ([ADR-0012](../decisions/0012-checkpoint-support.md)), in those skills' own topics. Each test is judged per day like code: missed if it failed in a Check and no Check that day passed it. The names of each Check's failing tests are in its event's `data.failing`. A Check whose tests couldn't run (`data.status` isn't `ok`) counts for none of them.
- For each skill, day by day:
  - a missed day opens the follow-up (due the next day) and clears earlier progress;
  - each correct day after it counts (due again 3 days later, then 7);
  - 3 correct days close it.

### Reviews

Details are in [ADR-0009](../decisions/0009-reviews.md).

- The FSRS card is created when a topic becomes Learned. That counts as a first review rated Good.
- Each review session rates the card: all items correct is Good; some correct is Hard; none is Again.
