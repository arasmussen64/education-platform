"""The validator must accept good content and catch each kind of mistake."""

from pathlib import Path

import pytest
from content_fixture import CHECKPOINT, MCQ, TOPIC, make_valid_tree, write
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
    # 6 reference solutions + 2 starters + 1 wrong solution + 1 predict item
    assert report.counts["runs"] == 10


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
