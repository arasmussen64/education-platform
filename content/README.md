# Content

Everything learners see: tracks, topics, lessons and exercises, as plain files in git. The formats are defined in the [data model](../docs/specs/data-model.md#content-files). [`tools/validate_content.py`](../tools/validate_content.py) checks all of it on every pull request.

## Layout

```text
content/
├── tracks/python-foundations.yaml   modules, and which topics are in each
└── topics/<topic-id>/
    ├── topic.yaml                   metadata, prerequisites, resources, which items to use
    ├── lesson.mdx                   the AI-written intro and recap around the main resource
    ├── recall/<item>.yaml           multiple-choice and predict-the-output items
    └── exercises/<item>/
        ├── exercise.yaml
        ├── starter.py               fill-in and debug exercises (must fail the tests)
        ├── solution.py              the reference solution (must pass)
        ├── test_exercise.py         the tests
        └── wrong/*.py               known-wrong solutions (each must fail)
```

## A topic's life

| `status` | Meaning |
|---|---|
| `planned` | An outline: title, summary, prerequisites. It shows on the map, but there's nothing to learn yet. |
| `draft` | Being written. Whatever exists is checked, but the topic isn't shown to learners. |
| `ready` | Complete: learners see it. It must meet the content definition of done (below). |

## Writing a topic

1. Set `status: draft` and fill in `topic.yaml`: objectives, resources (each with its license, and whether we embed or link it), the explain prompt and rubric.
2. Write `lesson.mdx`: `<Intro>` (what to watch for), `<Resource index={0} />`, then `<Recap>`. The first resource in `topic.yaml` is the main one, shown in the lesson; any others are listed after the lesson as "More resources". Write your own explanations; never copy or paraphrase a resource's text.
3. Add the practice ladder: a worked example with labeled steps, then 2–3 recall items, a fill-in exercise, and a write exercise.
4. Add the proof: a build exercise (hidden tests, no starter), a debug exercise (a buggy starter), and the explain prompt.
5. Add a review pool: at least 3 items, at least one of them predict-the-output or a `review_code` exercise.
6. List the topic's **skills** in `topic.yaml`, and give every item `skills: [...]` with the skills it mainly tests. A missed question comes back later as a different question on the same skill ([ADR-0011](../docs/decisions/0011-mistakes-come-back.md)). So each skill needs at least 2 questions that can come back: recall items, or fill-in, write and `review_code` exercises. Aim for 3. Extra questions can go in the review pool.
7. Run the checker until it's clean, then go through the topic once as a learner. The dev server (`npm run dev` in `web/`) shows drafts, so you can try it at `http://localhost:5173/topic/<topic-id>`. Then set `status: ready`. While the owner is the only learner, a topic can go straight to `ready`: their first pass, on the live site, is the review ([v1 spec](../docs/specs/v1.md#content-definition-of-done)).

Tips for tests: give each test a one-line docstring, which is what the learner sees, and give `assert` a message when the default wouldn't be clear. See [harness/README.md](../harness/README.md).

When an exercise could be passed by typing the expected output in by hand, add a test with `run_with`, which reruns the program with other starting values. A swap must then swap *any* two values (see the Variables topic). Add the hand-typed version as a known-wrong solution, so the checker proves the test catches it.

The dev server watches `content/`, so new and changed files show up straight away.

To see the feedback a learner would get, copy an exercise's `test_exercise.py` and a starter or wrong answer (saved as `solution.py`) into an empty folder, then run `python -m uv run python harness/cli.py check <folder>`.

Tips for questions:

- Vary which choice is the right one, so its position is never a clue.
- Choices, prompts and explanations are Markdown, so code goes in backticks: `` `print("Hi")` ``.
- Write explanations that say why the answer is right, and why the tempting wrong one is wrong.
- Quote error messages exactly as Python 3.14 prints them. Run the code through the harness to see them.

## Checking

From the repository root:

```text
python -m uv run python tools/validate_content.py            everything, including running all the code
python -m uv run python tools/validate_content.py --no-run   formats and structure only (fast)
```

Item IDs never change once a topic is `ready`, because learners' answers refer to them. To change an item meaningfully, bump its `rev`.
