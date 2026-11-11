"""The validator must accept good content and catch each kind of mistake."""

import json
from pathlib import Path

import pytest
from content_fixture import (
    CHECKPOINT,
    CHECKPOINT_DIR,
    MCQ,
    READY_CHECKPOINT,
    TOPIC,
    TRACK,
    exercise_yaml,
    make_ready_checkpoint,
    make_valid_tree,
    write,
)
from validate_content import main, validate

TOPIC_DIR = "content/topics/t.hello"


@pytest.fixture
def tree(tmp_path: Path) -> Path:
    return make_valid_tree(tmp_path)


def problems(root: Path, run: bool = True) -> list[str]:
    return validate(root, run=run).problems


def assert_reported(root: Path, *fragments: str, run: bool = True) -> None:
    found = problems(root, run=run)
    for fragment in fragments:
        assert any(fragment in problem for problem in found), (
            f"expected a problem mentioning {fragment!r}, got: {found}"
        )


def test_good_content_has_no_problems(tree: Path) -> None:
    report = validate(tree)
    assert report.problems == []
    assert report.counts["ready"] == 1
    assert report.counts["exercises"] == 6
    # 6 reference solutions + 2 starters + 1 wrong solution + 1 predict item
    # + 1 Parsons item + 1 shell item, and an empty program for each of the 2
    # exercises with hidden tests; then the one other order of the Parsons
    # lines that runs to the end (it prints Hello without the !)
    assert report.counts["runs"] == 15
    # 5 other orders of the 3 lines, and the decoy in place of each line
    assert report.counts["arrangements"] == 8


def test_hidden_tests_fail_instead_of_crashing(tree: Path) -> None:
    # On an empty program, splitlines() is empty, so [0] crashes the test.
    write(
        tree,
        f"{TOPIC_DIR}/exercises/build-hello/test_exercise.py",
        "from checks import run\n\n\ndef test_says_hello():\n"
        '    """Prints Hello!"""\n'
        '    assert run().splitlines()[0] == "Hello!"\n',
    )
    assert_reported(tree, "test_says_hello crashes on an empty program (IndexError")


def test_unknown_fields_are_caught(tree: Path) -> None:
    write(
        tree, f"{TOPIC_DIR}/topic.yaml", TOPIC.replace("title: Hello", "titel: Hello")
    )
    assert_reported(tree, "titel: Extra inputs are not permitted", run=False)


def test_doubled_apostrophes_are_caught(tree: Path) -> None:
    # In a single-quoted scalar '' is an apostrophe; in a block scalar it isn't.
    write(
        tree,
        f"{TOPIC_DIR}/recall/mcq-print.yaml",
        MCQ.replace(
            "explanation: print shows its argument.",
            "explanation: |\n  print shows its argument; it doesn''t add quotes.",
        ),
    )
    assert_reported(
        tree, "keeps a doubled apostrophe", "it doesn''t add quotes", run=False
    )


def explain_mcq(tree: Path, explanation: str) -> None:
    """Give the fixture's multiple-choice item this explanation."""
    write(
        tree,
        f"{TOPIC_DIR}/recall/mcq-print.yaml",
        MCQ.replace("print shows its argument.", explanation),
    )


def test_explanations_never_name_a_choice_by_position(tree: Path) -> None:
    explain_mcq(tree, "print shows its argument. The last choice is a trap.")
    assert_reported(
        tree,
        "mcq-print.yaml: the explanation says 'last choice', but the app "
        "shuffles the choices, so a position points at the wrong one; name the "
        "choice by what it says",
        run=False,
    )


@pytest.mark.parametrize(
    ("explanation", "phrase"),
    [
        ("The second option only looks right.", "second option"),
        ("Not the First answer, which adds.", "First answer"),
        ("So the first and last choices are False.", "first and last choices"),
        ("The third\n  choice forgets the quotes.", "third choice"),
    ],
)
def test_every_way_of_naming_a_position_is_caught(
    tree: Path, explanation: str, phrase: str
) -> None:
    explain_mcq(tree, explanation)
    assert_reported(tree, f"the explanation says {phrase!r}, but", run=False)


@pytest.mark.parametrize(
    "explanation",
    [
        "The last line names the error, and the first one is where it started.",
        "Convert first, and the answer is then a number; the choice is yours.",
        "It removes the option to wait, the first response instead of the last.",
        "The other three choices each leave out the quotes.",
    ],
)
def test_everyday_uses_of_first_and_last_are_fine(tree: Path, explanation: str) -> None:
    explain_mcq(tree, explanation)
    assert problems(tree, run=False) == []


def test_ids_must_match_folders(tree: Path) -> None:
    write(tree, f"{TOPIC_DIR}/topic.yaml", TOPIC.replace("id: t.hello", "id: t.other"))
    assert_reported(tree, "must match its folder name", run=False)


def test_prerequisites_must_exist(tree: Path) -> None:
    write(
        tree,
        f"{TOPIC_DIR}/topic.yaml",
        TOPIC.replace("prerequisites: []", "prerequisites: [t.missing]"),
    )
    assert_reported(tree, "prerequisite 't.missing' doesn't exist", run=False)


def test_prerequisites_cannot_go_in_a_circle(tree: Path) -> None:
    write(
        tree,
        f"{TOPIC_DIR}/topic.yaml",
        TOPIC.replace("prerequisites: []", "prerequisites: [t.m1.checkpoint]"),
    )
    assert_reported(tree, "prerequisites go in a circle", run=False)


def test_every_topic_must_be_in_a_track(tree: Path) -> None:
    write(
        tree,
        "content/topics/t.stray/topic.yaml",
        CHECKPOINT.replace("t.m1.checkpoint", "t.stray").replace(
            "kind: checkpoint", "kind: topic"
        ),
    )
    assert_reported(tree, "isn't in any track", run=False)


def test_tracks_each_have_their_own_order(tree: Path) -> None:
    second = TRACK.replace("test-track", "other-track").replace(
        "topics: [t.hello]", "topics: [t.other]"
    )
    second = second.replace("t.m1.checkpoint", "t.m2.checkpoint")
    write(tree, "content/tracks/other.yaml", second)
    write(
        tree,
        "content/topics/t.other/topic.yaml",
        "id: t.other\nkind: topic\nstatus: planned\ntitle: Other\n"
        "summary: Another topic.\nestimated_minutes: 30\nrev: 1\n"
        "objectives:\n  - Do another thing.\n",
    )
    write(
        tree,
        "content/topics/t.m2.checkpoint/topic.yaml",
        CHECKPOINT.replace("t.m1.checkpoint", "t.m2.checkpoint").replace(
            "[t.hello]", "[t.other]"
        ),
    )
    # Whichever file comes second gets the report.
    assert_reported(tree, "order 1 is also", run=False)
    write(tree, "content/tracks/other.yaml", second.replace("order: 1", "order: 2"))
    assert problems(tree, run=False) == []


def test_a_capstone_is_a_checkpoint_that_follows_its_module(tree: Path) -> None:
    write(
        tree,
        "content/tracks/test.yaml",
        TRACK.replace(
            "checkpoint: t.m1.checkpoint",
            "checkpoint: t.m1.checkpoint\n    capstone: t.capstone",
        ),
    )
    assert_reported(tree, "t.m1 lists 't.capstone', which doesn't exist", run=False)

    write(
        tree,
        "content/topics/t.capstone/topic.yaml",
        CHECKPOINT.replace("t.m1.checkpoint", "t.capstone").replace(
            "kind: checkpoint", "kind: topic"
        ),
    )
    assert_reported(tree, "'t.capstone' must have kind: checkpoint", run=False)

    write(
        tree,
        "content/topics/t.capstone/topic.yaml",
        CHECKPOINT.replace("t.m1.checkpoint", "t.capstone"),
    )
    assert problems(tree, run=False) == []


def test_ready_topics_need_every_part(tree: Path) -> None:
    write(tree, f"{TOPIC_DIR}/topic.yaml", TOPIC.replace("  debug: debug-hello\n", ""))
    assert_reported(tree, "prove.debug must name a debug exercise", run=False)


def test_ready_lessons_show_the_main_resource(tree: Path) -> None:
    write(tree, f"{TOPIC_DIR}/lesson.mdx", "<Intro>Hi.</Intro>\n")
    assert_reported(tree, "the lesson must show the main resource", run=False)


def test_lessons_place_only_the_main_resource(tree: Path) -> None:
    lesson = tree / TOPIC_DIR / "lesson.mdx"
    text = lesson.read_text(encoding="utf-8")
    write(tree, f"{TOPIC_DIR}/lesson.mdx", text + "\n<Resource index={1} />\n")
    assert_reported(
        tree, "only the main resource (index 0) goes in the lesson", run=False
    )


def test_named_items_must_exist(tree: Path) -> None:
    write(
        tree, f"{TOPIC_DIR}/topic.yaml", TOPIC.replace("review-hello]", "review-gone]")
    )
    assert_reported(tree, "names 'review-gone', which doesn't exist", run=False)


# --- Skills: a missed question comes back as another on the same skill -------


def test_items_can_only_name_declared_skills(tree: Path) -> None:
    write(
        tree,
        f"{TOPIC_DIR}/recall/mcq-print.yaml",
        MCQ.replace("[print-text]", "[print-txet]"),
    )
    assert_reported(
        tree, "names skill 'print-txet', which topic.yaml doesn't declare", run=False
    )


def test_ready_topics_declare_skills(tree: Path) -> None:
    topic = TOPIC.split("skills:")[0]
    write(tree, f"{TOPIC_DIR}/topic.yaml", topic)
    assert_reported(tree, "a ready topic needs skills", run=False)


def test_every_graded_item_names_a_skill(tree: Path) -> None:
    write(
        tree,
        f"{TOPIC_DIR}/recall/mcq-print.yaml",
        MCQ.replace("skills: [print-text]\n", ""),
    )
    assert_reported(tree, "mcq-print.yaml: needs at least one skill", run=False)


def test_each_skill_has_two_questions_that_can_come_back(tree: Path) -> None:
    # A second skill, tested only by the build exercise, which is a proof
    # check and so can never come back as a follow-up.
    write(
        tree,
        f"{TOPIC_DIR}/topic.yaml",
        TOPIC + "  - id: banners\n    description: Print a banner.\n",
    )
    exercise = tree / TOPIC_DIR / "exercises/build-hello/exercise.yaml"
    text = exercise.read_text(encoding="utf-8")
    write(
        tree,
        f"{TOPIC_DIR}/exercises/build-hello/exercise.yaml",
        text.replace("[print-text]", "[print-text, banners]"),
    )
    assert_reported(
        tree, "skill 'banners' needs at least 2 questions that can come back", run=False
    )


def test_reference_solutions_must_pass(tree: Path) -> None:
    write(tree, f"{TOPIC_DIR}/exercises/write-hello/solution.py", 'print("Bye")\n')
    assert_reported(tree, "the reference solution must pass every test")


def test_starters_must_fail(tree: Path) -> None:
    write(tree, f"{TOPIC_DIR}/exercises/debug-hello/starter.py", 'print("Hello!")\n')
    assert_reported(tree, "the starter must fail the tests, but it passes")


def test_known_wrong_solutions_must_fail(tree: Path) -> None:
    write(
        tree, f"{TOPIC_DIR}/exercises/build-hello/wrong/no-bang.py", 'print("Hello!")\n'
    )
    assert_reported(tree, "a known-wrong solution must fail a test, but it passes")


def test_predicted_output_must_be_what_the_code_prints(tree: Path) -> None:
    item = f"{TOPIC_DIR}/recall/predict-print.yaml"
    text = (tree / item).read_text(encoding="utf-8")
    write(tree, item, text.replace("  a\n  b\n", "  a\n  c\n"))
    assert_reported(
        tree, "expected_output is 'a\\nc\\n', but the code prints 'a\\nb\\n'"
    )


def test_parsons_lines_must_run_in_order(tree: Path) -> None:
    item = f"{TOPIC_DIR}/recall/parsons-order.yaml"
    text = (tree / item).read_text(encoding="utf-8")
    write(tree, item, text.replace("  - 'print(greeting)'", "  - 'print(greting)'"))
    assert_reported(tree, "the lines in order crash")


def test_parsons_decoys_must_differ_from_the_lines(tree: Path) -> None:
    item = f"{TOPIC_DIR}/recall/parsons-order.yaml"
    text = (tree / item).read_text(encoding="utf-8")
    write(tree, item, text.replace("  - 'print(Greeting)'", "  - 'print(greeting)'"))
    assert_reported(tree, "different from every line", run=False)


# --- Parsons items: only the author's order may work (ADR-0016) ------------------

PARSONS_ITEM = f"{TOPIC_DIR}/recall/parsons-order.yaml"


def parsons_yaml(lines: list[str], decoys: list[str]) -> str:
    """A Parsons item for the fixture topic with these lines and decoys."""

    def as_list(entries: list[str]) -> str:
        return "".join(f"  - {entry!r}\n" for entry in entries)

    return (
        "id: parsons-order\ntype: parsons\nrev: 1\n"
        "prompt: Put the lines in order.\n"
        f"lines:\n{as_list(lines)}distractors:\n{as_list(decoys)}"
        "explanation: A name must exist before it's used.\nskills: [print-text]\n"
    )


def test_parsons_lines_work_in_one_order_only(tree: Path) -> None:
    # Neither of the first two lines needs the other, so they can swap.
    lines = ["first = 'Hel'", "second = 'lo!'", "print(first + second)"]
    write(tree, PARSONS_ITEM, parsons_yaml(lines, ["print(First + second)"]))
    assert_reported(
        tree,
        "parsons-order.yaml: another order of the lines runs and prints the same "
        "output, so a learner who builds it would be marked wrong: lines 1 and 2 "
        "can swap places (\"first = 'Hel'\" and \"second = 'lo!'\"). Make each "
        "line need the one before it, or join the lines that don't depend on "
        "each other",
    )


def test_parsons_problems_name_the_simplest_other_order(tree: Path) -> None:
    # The import can go anywhere before the line that uses it: two other orders.
    lines = ["import math", "low = 2.5", "high = low + 1", "print(math.floor(high))"]
    write(tree, PARSONS_ITEM, parsons_yaml(lines, ["print(math.floor(High))"]))
    assert_reported(
        tree,
        "marked wrong: lines 1 and 2 can swap places ('import math' and "
        "'low = 2.5'); 1 more order works too. Make each line",
    )


def test_parsons_problems_count_the_other_orders(tree: Path) -> None:
    # None of the first three lines needs another, so all 6 orders of them
    # work: the author's, the one that is named, and 4 more.
    lines = ["a = 1", "b = 2", "c = 3", "print(a + b + c)"]
    write(tree, PARSONS_ITEM, parsons_yaml(lines, ["print(a + b + C)"]))
    assert_reported(
        tree,
        "marked wrong: lines 1 and 2 can swap places ('a = 1' and 'b = 2'); "
        "4 more orders work too. Make each line",
    )


def test_a_parsons_decoy_must_not_work_in_place_of_a_line(tree: Path) -> None:
    lines = ["greeting = 'Hello'", "greeting = greeting + '!'", "print(greeting)"]
    write(tree, PARSONS_ITEM, parsons_yaml(lines, ["print(greeting.strip())"]))
    assert_reported(
        tree,
        "parsons-order.yaml: the decoy 'print(greeting.strip())' can take the "
        "place of line 3 ('print(greeting)') and the program still runs and "
        "prints the same output, so a learner who uses the decoy would be "
        "marked wrong. Change the decoy so the program crashes or prints "
        "something else",
    )


def test_parsons_orders_are_compared_in_a_process_of_their_own(tree: Path) -> None:
    # Run alone, the order import, print, start prints False. In a process
    # where an earlier program left tracing switched on it would print True,
    # like the author's order, and be reported by mistake.
    lines = [
        "import tracemalloc",
        "tracemalloc.start()",
        "print(tracemalloc.is_tracing())",
    ]
    write(tree, PARSONS_ITEM, parsons_yaml(lines, ["print(tracemalloc.tracing())"]))
    assert problems(tree) == []


def test_a_parsons_order_that_never_ends_is_not_a_working_order(tree: Path) -> None:
    # With the last two lines before the second, the loop never ends. The
    # check must give up on that order quickly, not wait for it.
    lines = ["n = 3", "n = n - 1", "while n > 2:", "    print(n)"]
    write(tree, PARSONS_ITEM, parsons_yaml(lines, ["n = N - 1"]))
    assert problems(tree) == []


def test_parsons_orders_that_affect_each_other_all_run_alone(tree: Path) -> None:
    # This program crashes the second time it runs in the same process, so
    # the quick first pass can't be trusted, and every one of the 5 other
    # orders and 3 uses of the decoy is run in a process of its own.
    lines = [
        "import builtins",
        "builtins.runs = getattr(builtins, 'runs', 0) + 1",
        "print(1 // (builtins.runs == 1))",
    ]
    write(tree, PARSONS_ITEM, parsons_yaml(lines, ["print(builtins.run)"]))
    report = validate(tree)
    assert report.problems == []
    # The 13 runs that aren't Parsons runs, the author's order, and the 8.
    assert report.counts["runs"] == 13 + 1 + 8


# --- Labs: exercises in containers (ADR-0018) -----------------------------------

LAB_DIR = f"{TOPIC_DIR}/exercises/lab-report"
LAB_EXERCISE = (
    "id: lab-report\nstage: write\nruntime: lab\nrev: 1\n"
    "title: A report\nprompt: Make a report.\nskills: [print-text]\n"
)
LAB_CHECKS = (
    "checks:\n  - id: report-exists\n    description: The report exists.\n"
    "    command: test -f /home/learner/report.txt\n"
)


def add_lab(tree: Path) -> None:
    write(tree, f"{LAB_DIR}/exercise.yaml", LAB_EXERCISE)
    write(tree, f"{LAB_DIR}/Dockerfile", "FROM ubuntu:24.04\n")
    write(tree, f"{LAB_DIR}/checks.yaml", LAB_CHECKS)
    write(tree, f"{LAB_DIR}/solution.sh", "echo done > ~/report.txt\n")


def test_a_lab_needs_its_image_checks_and_solution(tree: Path) -> None:
    add_lab(tree)
    assert problems(tree, run=False) == []
    (tree / LAB_DIR / "checks.yaml").unlink()
    (tree / LAB_DIR / "solution.sh").unlink()
    assert_reported(
        tree, "a lab needs checks.yaml", "a lab needs solution.sh", run=False
    )


def test_a_lab_has_no_python_exercise_files(tree: Path) -> None:
    add_lab(tree)
    # A program that's part of the scenario is fine...
    write(tree, f"{LAB_DIR}/server.py", "print(1)\n")
    assert problems(tree, run=False) == []
    # ...a Python exercise's files are not.
    write(tree, f"{LAB_DIR}/solution.py", "print(1)\n")
    assert_reported(tree, "a lab has no solution.py", run=False)


def test_lab_checks_need_distinct_ids_and_a_condition(tree: Path) -> None:
    add_lab(tree)
    write(tree, f"{LAB_DIR}/checks.yaml", LAB_CHECKS + LAB_CHECKS[8:])
    assert_reported(tree, "check ids must all be different", run=False)
    write(
        tree,
        f"{LAB_DIR}/checks.yaml",
        LAB_CHECKS.replace("    command: test", "    expect: {}\n    command: test"),
    )
    assert_reported(tree, "expect needs at least one condition", run=False)


def test_lab_options_only_for_labs(tree: Path) -> None:
    add_lab(tree)
    write(
        tree,
        f"{TOPIC_DIR}/exercises/write-hello/exercise.yaml",
        exercise_yaml("write-hello", "write") + "lab:\n  init: systemd\n",
    )
    assert_reported(tree, "lab options are only for runtime: lab", run=False)


def test_checkpoint_lab_test_skills_name_check_ids(checkpoint: Path) -> None:
    folder = f"{CHECKPOINT_DIR}/exercises/debug-card"
    for name in ("solution.py", "starter.py", "test_exercise.py"):
        (checkpoint / folder / name).unlink()
    write(
        checkpoint,
        f"{folder}/exercise.yaml",
        "id: debug-card\nstage: debug\nruntime: lab\nrev: 1\ntitle: A card\n"
        "prompt: Fix it.\ntest_skills:\n  report-exists: [t.hello/print-text]\n"
        "  report-gone: [t.hello/print-text]\n",
    )
    write(checkpoint, f"{folder}/Dockerfile", "FROM ubuntu:24.04\n")
    write(checkpoint, f"{folder}/checks.yaml", LAB_CHECKS)
    write(checkpoint, f"{folder}/solution.sh", "echo done > ~/report.txt\n")
    assert_reported(
        checkpoint,
        "test_skills names 'report-gone', which isn't a test in checks.yaml",
        run=False,
    )
    write(
        checkpoint,
        f"{folder}/exercise.yaml",
        "id: debug-card\nstage: debug\nruntime: lab\nrev: 1\ntitle: A card\n"
        "prompt: Fix it.\ntest_skills:\n  test_says_hello: [t.hello/print-text]\n",
    )
    assert_reported(checkpoint, "isn't a check id", run=False)


# --- Shell items run in real bash (ADR-0017) ----------------------------------

SHELL_ITEM = f"{TOPIC_DIR}/recall/shell-count.yaml"


def test_shell_output_must_be_what_the_command_prints(tree: Path) -> None:
    text = (tree / SHELL_ITEM).read_text(encoding="utf-8")
    write(tree, SHELL_ITEM, text.replace("  2\n  ok\n", "  3\n  ok\n"))
    assert_reported(
        tree,
        "expected_output is '3\\nok\\nok\\n', but the command prints '2\\nok\\nok\\n'",
    )


def test_shell_commands_must_not_write_to_stderr(tree: Path) -> None:
    text = (tree / SHELL_ITEM).read_text(encoding="utf-8")
    write(
        tree, SHELL_ITEM, text.replace("grep -c ada names.txt", "grep -c ada nope.txt")
    )
    assert_reported(tree, "writes to stderr", "nope.txt")


def test_shell_files_stay_inside_their_folder(tree: Path) -> None:
    text = (tree / SHELL_ITEM).read_text(encoding="utf-8")
    write(tree, SHELL_ITEM, text.replace("  logs/app.log: |", "  ../app.log: |"))
    assert_reported(tree, "must not have . or .. parts", run=False)
    write(tree, SHELL_ITEM, text.replace("  logs/app.log: |", "  /tmp/app.log: |"))
    assert_reported(tree, "String should match pattern", run=False)


def test_shell_items_say_when_there_is_no_bash(
    tree: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import validate_content

    monkeypatch.setattr(validate_content, "find_bash", lambda: None)
    assert_reported(tree, "needs bash to run the command")


def test_shell_commands_that_never_stop_are_reported(
    tree: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import validate_content

    monkeypatch.setattr(validate_content, "SHELL_TIMEOUT_SECONDS", 2)
    text = (tree / SHELL_ITEM).read_text(encoding="utf-8")
    write(tree, SHELL_ITEM, text.replace("grep -c ada names.txt", "sleep 30"))
    assert_reported(tree, "ran for over 2s")


def test_code_that_never_stops_is_reported(
    tree: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import validate_content

    monkeypatch.setattr(validate_content, "RUN_TIMEOUT_SECONDS", 2)
    write(
        tree,
        f"{TOPIC_DIR}/exercises/write-hello/solution.py",
        "while True:\n    pass\n",
    )
    assert_reported(tree, "a loop that never ends")


def test_no_run_skips_running_code(tree: Path) -> None:
    write(tree, f"{TOPIC_DIR}/exercises/write-hello/solution.py", 'print("Bye")\n')
    assert problems(tree, run=False) == []


# --- Checkpoints: a way through for a learner who's stuck (ADR-0012) ---------


@pytest.fixture
def checkpoint(tree: Path) -> Path:
    return make_ready_checkpoint(tree)


def replace_in(root: Path, relative: str, old: str, new: str) -> None:
    text = (root / relative).read_text(encoding="utf-8")
    assert old in text, f"{old!r} isn't in {relative}"
    write(root, relative, text.replace(old, new))


def test_a_complete_checkpoint_has_no_problems(checkpoint: Path) -> None:
    report = validate(checkpoint)
    assert report.problems == []
    assert report.counts["ready"] == 2


def test_ready_checkpoints_need_a_way_through(checkpoint: Path) -> None:
    topic = READY_CHECKPOINT.split("unstuck:")[0]
    write(checkpoint, f"{CHECKPOINT_DIR}/topic.yaml", topic)
    assert_reported(checkpoint, "a ready checkpoint needs unstuck", run=False)


def test_each_part_of_the_way_through_is_the_right_kind(checkpoint: Path) -> None:
    topic = (
        READY_CHECKPOINT.replace("example: example-other", "example: step-read")
        .replace("step-outline]", "build-card-b]")
        .replace("[build-card-b, build-card-c]", "[build-card, build-card-c]")
    )
    write(checkpoint, f"{CHECKPOINT_DIR}/topic.yaml", topic)
    assert_reported(
        checkpoint,
        "unstuck.example must name a worked example",
        "unstuck step 'build-card-b' must be a fill-in exercise",
        "unstuck version 'build-card' is the build itself",
        run=False,
    )


def test_there_are_enough_steps_and_versions(checkpoint: Path) -> None:
    topic = READY_CHECKPOINT.replace(", step-outline]", "]").replace(
        ", build-card-c]", "]"
    )
    write(checkpoint, f"{CHECKPOINT_DIR}/topic.yaml", topic)
    replace_in(
        checkpoint,
        f"{CHECKPOINT_DIR}/exercises/step-read/exercise.yaml",
        "hints:\n  - Use print.\n",
        "",
    )
    assert_reported(
        checkpoint,
        "unstuck.steps needs at least 3 steps",
        "unstuck.versions needs at least 2 fresh versions",
        "unstuck step 'step-read' needs hints",
        run=False,
    )


def test_every_checkpoint_test_names_its_skills(checkpoint: Path) -> None:
    replace_in(
        checkpoint,
        f"{CHECKPOINT_DIR}/exercises/debug-card/exercise.yaml",
        "test_skills:\n  test_says_hello: [t.hello/print-text]\n",
        "",
    )
    assert_reported(
        checkpoint,
        "debug-card/exercise.yaml: every test needs the skills it checks",
        "these have none: test_says_hello",
        run=False,
    )


def test_checkpoint_tests_name_real_tests_and_skills(checkpoint: Path) -> None:
    replace_in(
        checkpoint,
        f"{CHECKPOINT_DIR}/exercises/build-card/exercise.yaml",
        "  test_says_hello: [t.hello/print-text]\n",
        "  test_says_hello: [t.hello/print-txet, t.gone/print-text]\n"
        "  test_says_bye: [t.hello/print-text]\n",
    )
    assert_reported(
        checkpoint,
        "test_says_hello: t.hello doesn't declare skill 'print-txet'",
        "test_says_hello: topic 't.gone' doesn't exist",
        "test_skills names 'test_says_bye', which isn't a test",
        run=False,
    )


def test_checkpoint_tests_name_skills_taught_before_them(checkpoint: Path) -> None:
    replace_in(
        checkpoint,
        "content/tracks/test.yaml",
        "checkpoint: t.m1.checkpoint\n",
        "checkpoint: t.m1.checkpoint\n"
        "  - id: t.m2\n    title: Module two\n"
        "    topics: [t.later]\n    checkpoint: t.m2.checkpoint\n",
    )
    later = (
        CHECKPOINT.replace("t.m1.checkpoint", "t.later")
        .replace("kind: checkpoint", "kind: topic")
        .replace("prerequisites: [t.hello]", "prerequisites: [t.m1.checkpoint]")
    )
    write(
        checkpoint,
        "content/topics/t.later/topic.yaml",
        later + "skills:\n  - id: loops\n    description: Repeat things.\n",
    )
    write(
        checkpoint,
        "content/topics/t.m2.checkpoint/topic.yaml",
        CHECKPOINT.replace("t.m1", "t.m2").replace("[t.hello]", "[t.later]"),
    )
    replace_in(
        checkpoint,
        f"{CHECKPOINT_DIR}/exercises/build-card/exercise.yaml",
        "[t.hello/print-text]",
        "[t.later/loops]",
    )
    assert_reported(checkpoint, "'t.later' comes after this checkpoint", run=False)


def test_only_checkpoints_name_skills_per_test(tree: Path) -> None:
    replace_in(
        tree,
        f"{TOPIC_DIR}/exercises/build-hello/exercise.yaml",
        "skills: [print-text]\n",
        "skills: [print-text]\ntest_skills:\n  test_says_hello: [t.hello/print-text]\n",
    )
    assert_reported(tree, "only checkpoint exercises have test_skills", run=False)


def test_ready_checkpoints_need_their_module_ready(checkpoint: Path) -> None:
    write(
        checkpoint,
        f"{TOPIC_DIR}/topic.yaml",
        TOPIC.replace("status: ready", "status: draft"),
    )
    assert_reported(
        checkpoint,
        "needs every topic of its module ready, but 't.hello' is draft",
        run=False,
    )


def test_topics_and_checkpoints_keep_to_their_own_fields(checkpoint: Path) -> None:
    write(
        checkpoint,
        f"{CHECKPOINT_DIR}/topic.yaml",
        READY_CHECKPOINT + "skills:\n  - id: cards\n    description: Make cards.\n",
    )
    write(
        checkpoint,
        f"{TOPIC_DIR}/topic.yaml",
        TOPIC + "unstuck:\n  example: example-hello\n",
    )
    assert_reported(
        checkpoint,
        "checkpoints don't declare skills",
        "only checkpoints have unstuck",
        run=False,
    )


DIAGNOSTIC = """id: math
title: Math
summary: Where your math stops.
levels:
  - id: counting
    title: Counting
    summary: Counting things.
    refresh:
      title: Counting, refreshed
      url: https://example.com/counting
      type: reading
      use: link
      license: CC BY 4.0
    items:
      - id: count-1
        type: mcq
        rev: 1
        prompt: "2 + 2?"
        choices: ["3", "4"]
        answer: 1
        explanation: Four.
      - id: count-2
        type: mcq
        rev: 1
        prompt: "3 + 3?"
        choices: ["6", "9"]
        answer: 0
        explanation: Six.
  - id: adding
    title: Adding
    summary: Adding things.
    refresh:
      title: Adding, refreshed
      url: https://example.com/adding
      type: reading
      use: link
      license: CC BY 4.0
    items:
      - id: add-1
        type: mcq
        rev: 1
        prompt: "10 + 5?"
        choices: ["15", "50"]
        answer: 0
        explanation: Fifteen.
      - id: add-2
        type: mcq
        rev: 1
        prompt: "7 + 8?"
        choices: ["14", "15"]
        answer: 1
        explanation: Fifteen.
"""


def test_a_diagnostic_is_checked(tree: Path) -> None:
    write(tree, "content/diagnostics/math.yaml", DIAGNOSTIC)
    report = validate(tree, run=False)
    assert report.problems == []
    assert report.counts["diagnostics"] == 1


def test_diagnostic_mistakes_are_caught(tree: Path) -> None:
    write(tree, "content/diagnostics/maths.yaml", DIAGNOSTIC)
    assert_reported(tree, "doesn't match the file name", run=False)
    write(
        tree,
        "content/diagnostics/math.yaml",
        DIAGNOSTIC.replace("answer: 1\n", "answer: 5\n", 1),
    )
    assert_reported(tree, "answer must be the index", run=False)
    write(
        tree,
        "content/diagnostics/math.yaml",
        DIAGNOSTIC.replace("id: add-2", "id: count-1"),
    )
    assert_reported(tree, "item ids must all be different", run=False)
    write(
        tree,
        "content/diagnostics/math.yaml",
        DIAGNOSTIC.replace(
            "    title: Adding\n", "    title: Adding\n    topic: t.nowhere\n"
        ),
    )
    assert_reported(tree, "names a topic that doesn't exist", run=False)
    write(
        tree,
        "content/diagnostics/math.yaml",
        DIAGNOSTIC.replace("explanation: Six.", "explanation: The first answer."),
    )
    assert_reported(
        tree, "item 'count-2': the explanation says 'first answer'", run=False
    )


# --- Multiple-choice answer lengths (mcq_lengths.py) --------------------------

BASELINE = "tools/mcq_length_baseline.yaml"


def write_mcq(tree: Path, item_id: str, right: str, *wrong: str) -> None:
    """Add a multiple-choice item to the fixture's topic. The right answer is
    written first; the validator doesn't care where it sits."""
    write(
        tree,
        f"{TOPIC_DIR}/recall/{item_id}.yaml",
        f"id: {item_id}\ntype: mcq\nrev: 1\nprompt: What does print do?\n"
        f"choices: {json.dumps([right, *wrong])}\nanswer: 0\n"
        "explanation: print shows its argument.\nskills: [print-text]\n",
    )


def test_a_right_answer_far_longer_than_the_wrong_ones_is_caught(tree: Path) -> None:
    write_mcq(tree, "mcq-print", "It shows its argument on the screen", "Nothing", "x")
    assert_reported(
        tree,
        "recall/mcq-print.yaml: the right answer is 35 characters and the "
        "longest wrong choice 7: more than 1.5 times as long",
        "Cut the right answer down to the claim itself",
        run=False,
    )


def test_a_right_answer_a_little_longer_is_fine(tree: Path) -> None:
    write_mcq(tree, "mcq-print", "It shows its argument", "It returns a string")
    assert problems(tree, run=False) == []


def test_a_topic_where_the_long_one_is_usually_right_is_caught(tree: Path) -> None:
    # With the fixture's own item, whose right answer is its shortest choice,
    # two more long right answers make two of three: too few items to judge.
    write_mcq(tree, "mcq-long-1", "It shows the text", "It hides text")
    write_mcq(tree, "mcq-long-2", "It shows the text", "It hides text")
    assert problems(tree, run=False) == []
    # A third makes three of four, which is more than half.
    write_mcq(tree, "mcq-long-3", "It shows the text", "It hides text")
    assert_reported(
        tree,
        "t.hello/topic.yaml: the right answer is the longest choice in 3 of the "
        "topic's 4 multiple-choice items (mcq-long-1, mcq-long-2, mcq-long-3)",
        run=False,
    )
    # Half is allowed: make one of them the shorter choice.
    write_mcq(tree, "mcq-long-3", "It shows text", "It hides the text")
    assert problems(tree, run=False) == []


def test_the_baseline_tolerates_what_it_lists(tree: Path) -> None:
    write_mcq(tree, "mcq-print", "It shows its argument on the screen", "Nothing")
    for n in (1, 2, 3):
        write_mcq(tree, f"mcq-long-{n}", "It shows the text", "It hides text")
    assert len(problems(tree, run=False)) == 2
    write(tree, BASELINE, "items:\n  - t.hello/mcq-print\ntopics:\n  - t.hello\n")
    assert problems(tree, run=False) == []


def test_a_fixed_baseline_entry_must_be_removed(tree: Path) -> None:
    # The fixture's item doesn't break the rule, so listing it is a mistake.
    write(tree, BASELINE, "items:\n  - t.hello/mcq-print\ntopics:\n  - t.hello\n")
    assert_reported(
        tree,
        f"{BASELINE}: lists the item 't.hello/mcq-print', which no longer breaks",
        f"{BASELINE}: lists the topic 't.hello', which no longer breaks",
        "remove its line, or run: python -m uv run python "
        "tools/validate_content.py --write-mcq-baseline",
        run=False,
    )


def test_the_baseline_never_covers_the_cloud_track(tree: Path) -> None:
    write(tree, BASELINE, "items:\n  - csa.linux.shell/mcq-pipes\n")
    assert_reported(
        tree,
        f"{BASELINE}: lists 'csa.linux.shell/mcq-pipes', but nothing from the "
        "cloud track (csa.*) may be on the baseline",
        run=False,
    )


def test_a_baseline_that_cannot_be_read_is_reported(tree: Path) -> None:
    write(tree, BASELINE, "items: t.hello/mcq-print\n")
    assert_reported(tree, f"{BASELINE}: items must be a list of names", run=False)


def test_diagnostic_items_follow_the_length_rule_too(tree: Path) -> None:
    write(
        tree,
        "content/diagnostics/math.yaml",
        DIAGNOSTIC.replace('choices: ["3", "4"]', 'choices: ["3", "4, two twos"]'),
    )
    assert_reported(
        tree,
        "diagnostics/math.yaml: item 'count-1': the right answer is 11 "
        "characters and the longest wrong choice 1",
        run=False,
    )
    write(tree, BASELINE, "items:\n  - diagnostics/math/count-1\n")
    assert problems(tree, run=False) == []


def test_the_baseline_command_writes_the_list_and_then_only_shrinks_it(
    tree: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    write_mcq(tree, "mcq-print", "It shows its argument on the screen", "Nothing")
    assert len(problems(tree, run=False)) == 1

    assert main(["--root", str(tree), "--write-mcq-baseline"]) == 0
    assert "It now lists 1 items and 0 topics." in capsys.readouterr().out
    assert "  - t.hello/mcq-print\n" in (tree / BASELINE).read_text(encoding="utf-8")
    assert problems(tree, run=False) == []

    # The item is fixed and another one goes wrong. The fixed one comes off
    # the list; the new one is never added, so it stays a problem.
    write_mcq(tree, "mcq-print", "It shows its argument", "It returns a string")
    write_mcq(tree, "mcq-new", "It shows its argument on the screen", "Nothing")
    assert len(problems(tree, run=False)) == 2
    assert main(["--root", str(tree), "--write-mcq-baseline"]) == 0
    said = capsys.readouterr().out
    assert "removed 1 entries" in said
    assert "1 items or topics break a rule and aren't on the list" in said
    assert (
        (tree / BASELINE)
        .read_text(encoding="utf-8")
        .endswith("items: []\ntopics: []\n")
    )
    assert_reported(tree, "recall/mcq-new.yaml: the right answer is", run=False)
