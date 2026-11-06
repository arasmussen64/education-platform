"""A tiny but complete content tree: one ready topic and one planned checkpoint.

make_valid_tree() writes it into a folder; each test then breaks one thing and
checks that the validator notices.
"""

from __future__ import annotations

from pathlib import Path

PASSING_TESTS = '''from checks import run


def test_says_hello():
    """Prints Hello!"""
    assert run() == "Hello!\\n"
'''

CORRECT = 'print("Hello!")\n'

TOPIC = """id: t.hello
kind: topic
status: ready
title: Hello
summary: Print a greeting.
prerequisites: []
estimated_minutes: 20
rev: 1
objectives:
  - Print text with print().
resources:
  - title: A video
    url: https://www.youtube.com/watch?v=abc
    type: video
    use: embed
    start: 10
    end: 20
    license: CC BY-NC-SA 4.0
practice: [example-hello, mcq-print, predict-print, fill-hello, write-hello]
prove:
  build: build-hello
  debug: debug-hello
  explain:
    prompt: What does print do?
    rubric:
      - id: shows
        required: true
        description: It shows text in the output.
    model_answer: It writes its arguments to the output.
review_pool: [mcq-print, predict-print, review-hello]
skills:
  - id: print-text
    description: Show text with print.
"""

CHECKPOINT = """id: t.m1.checkpoint
kind: checkpoint
status: planned
title: Checkpoint
summary: A small program.
prerequisites: [t.hello]
estimated_minutes: 60
rev: 1
objectives:
  - Build a small program.
"""

TRACK = """id: test-track
title: Test track
summary: A tiny track for tests.
modules:
  - id: t.m1
    title: Module one
    topics: [t.hello]
    checkpoint: t.m1.checkpoint
"""

MCQ = """id: mcq-print
type: mcq
rev: 1
prompt: What does print("Hi") show?
choices: ["Hi", "print", "Nothing"]
answer: 0
explanation: print shows its argument.
skills: [print-text]
"""

PREDICT = """id: predict-print
type: predict_output
rev: 1
prompt: What does this print?
code: |
  print("a")
  print("b")
expected_output: |
  a
  b
explanation: Each print starts a new line.
skills: [print-text]
"""

LESSON = """<Intro>Watch for print.</Intro>

<Resource index={0} />

<Recap>print shows text.</Recap>
"""


def exercise_yaml(item_id: str, stage: str) -> str:
    text = (
        f"id: {item_id}\nstage: {stage}\nrev: 1\n"
        "title: Say hello\nprompt: Print Hello!\n"
    )
    if stage == "worked_example":
        text += (
            "steps:\n  - label: Print it\n    lines: '1'\n    note: print shows text.\n"
        )
    else:
        text += "skills: [print-text]\n"
    return text


def write(root: Path, relative: str, text: str) -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    return path


def make_valid_tree(root: Path) -> Path:
    topic = "content/topics/t.hello"
    write(root, "content/tracks/test.yaml", TRACK)
    write(root, f"{topic}/topic.yaml", TOPIC)
    write(root, f"{topic}/lesson.mdx", LESSON)
    write(root, f"{topic}/recall/mcq-print.yaml", MCQ)
    write(root, f"{topic}/recall/predict-print.yaml", PREDICT)
    exercises = {
        "example-hello": "worked_example",
        "fill-hello": "fill_in",
        "write-hello": "write",
        "build-hello": "build",
        "debug-hello": "debug",
        "review-hello": "review_code",
    }
    for item_id, stage in exercises.items():
        folder = f"{topic}/exercises/{item_id}"
        write(root, f"{folder}/exercise.yaml", exercise_yaml(item_id, stage))
        write(root, f"{folder}/solution.py", CORRECT)
        write(root, f"{folder}/test_exercise.py", PASSING_TESTS)
    write(root, f"{topic}/exercises/fill-hello/starter.py", "print(...)\n")
    write(root, f"{topic}/exercises/debug-hello/starter.py", 'print("Helo!")\n')
    write(root, f"{topic}/exercises/build-hello/wrong/no-bang.py", 'print("Hello")\n')
    write(root, "content/topics/t.m1.checkpoint/topic.yaml", CHECKPOINT)
    return root
