"""The validator must accept good content and catch each kind of mistake."""

from pathlib import Path

import pytest
from content_fixture import (
    CHECKPOINT,
    CHECKPOINT_DIR,
    MCQ,
    READY_CHECKPOINT,
    TOPIC,
    make_ready_checkpoint,
    make_valid_tree,
    write,
)
from validate_content import validate

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
    # 6 reference solutions + 2 starters + 1 wrong solution + 1 predict item,
    # and an empty program for each of the 2 exercises with hidden tests
    assert report.counts["runs"] == 12


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
