"""The validator proves a typed item (ADR-0027): read the way the page reads
them, its accepted answers differ, its known mistakes are wrong answers the
page can tell apart, and its prompt doesn't give the answer away. Each test
breaks the item below in one way."""

from pathlib import Path

import pytest
from content_fixture import TOPIC, make_valid_tree, write
from validate_content import validate

TOPIC_DIR = "content/topics/t.hello"
TYPED_FILE = f"{TOPIC_DIR}/recall/typed-command.yaml"

TYPED = """id: typed-command
type: typed
rev: 1
prompt: |
  Which Docker command lists only the containers that are running now?
kind: command
answers:
  - docker ps
  - docker container ls
mistakes:
  - id: every-container
    answers: [docker ps -a, docker ps --all]
    why: "`-a` lists every container, stopped ones too."
explanation: "`docker ps` lists running containers; `-a` adds the stopped ones."
skills: [print-text]
"""


@pytest.fixture
def tree(tmp_path: Path) -> Path:
    """The fixture's tree, with the typed item in the topic's practice."""
    root = make_valid_tree(tmp_path)
    topic = TOPIC.replace("estimate-cost,", "estimate-cost, typed-command,")
    write(root, f"{TOPIC_DIR}/topic.yaml", topic)
    write(root, TYPED_FILE, TYPED)
    return root


def typed_with(tree: Path, *changes: tuple[str, str]) -> list[str]:
    """The problems found once the typed item has these changes."""
    text = TYPED
    for old, new in changes:
        assert old in text, f"{old!r} isn't in the typed item"
        text = text.replace(old, new)
    write(tree, TYPED_FILE, text)
    return validate(tree, run=False).problems


def assert_one_problem(found: list[str], fragment: str) -> None:
    assert len(found) == 1, found
    assert "typed-command.yaml" in found[0]
    assert fragment in found[0], found


def assert_refused(found: list[str], fragment: str) -> None:
    """The item doesn't load, for this reason."""
    assert any("typed-command.yaml" in p and fragment in p for p in found), found


def test_a_good_typed_item_passes_and_counts_as_a_recall_item(tree: Path) -> None:
    report = validate(tree, run=False)
    assert report.problems == []
    assert report.counts["recall items"] == 6


def test_a_text_item_passes_too(tree: Path) -> None:
    found = typed_with(
        tree,
        ("kind: command", "kind: text"),
        ("Which Docker command lists", "What do you call the list of"),
    )
    assert found == []


def test_answers_that_read_the_same_are_refused(tree: Path) -> None:
    found = typed_with(tree, ("  - docker container ls", "  - $ docker  ps"))
    assert_one_problem(found, "'docker ps' and '$ docker  ps' are the same")


def test_a_commands_case_counts_unless_the_item_says_otherwise(tree: Path) -> None:
    assert typed_with(tree, ("  - docker container ls", "  - Docker PS")) == []
    found = typed_with(
        tree,
        ("  - docker container ls", "  - Docker PS"),
        ("kind: command", "kind: command\ncase: insensitive"),
    )
    assert_one_problem(found, "are the same once they're read")
    assert "case ignored" in found[0]


def test_a_mistake_that_is_also_an_answer_is_refused(tree: Path) -> None:
    found = typed_with(tree, ("docker ps --all]", "docker container ls]"))
    assert_one_problem(found, "is also an accepted answer")


def test_a_mistake_that_reads_like_an_answer_is_refused(tree: Path) -> None:
    found = typed_with(tree, ("docker ps --all]", "'`docker ps`']"))
    assert_one_problem(found, "is also an accepted answer")


def test_two_mistakes_with_the_same_answer_are_refused(tree: Path) -> None:
    found = typed_with(
        tree,
        (
            "explanation:",
            "  - id: all-again\n    answers: [docker ps -a]\n"
            "    why: The same.\nexplanation:",
        ),
    )
    assert_one_problem(found, "is already in mistake 'every-container'")


def test_mistake_ids_must_differ(tree: Path) -> None:
    found = typed_with(
        tree,
        (
            "explanation:",
            "  - id: every-container\n    answers: [docker ls]\n"
            "    why: No such command.\nexplanation:",
        ),
    )
    assert_refused(found, "mistake ids must all be different")


def test_an_answer_that_reads_as_nothing_is_refused(tree: Path) -> None:
    found = typed_with(
        tree, ("kind: command", "kind: text"), ("  - docker container ls", '  - "."')
    )
    assert_one_problem(found, "is empty once it's read")


def test_a_prompt_that_says_the_answer_is_refused(tree: Path) -> None:
    found = typed_with(
        tree,
        ("running now?", "running now? (Hint: it starts `docker container ls`.)"),
    )
    assert_one_problem(found, "the prompt gives away the answer 'docker container ls'")


def test_a_prompt_may_show_a_longer_command(tree: Path) -> None:
    # "docker ps -a" contains "docker ps" but isn't it.
    found = typed_with(
        tree,
        ("running now?", "running now? Not `docker ps -a`, which shows all."),
    )
    assert found == []


def test_a_command_in_a_code_block_gives_it_away(tree: Path) -> None:
    found = typed_with(
        tree,
        ("running now?\n", "running now?\n  ```bash\n  $ docker ps\n  ```\n"),
    )
    assert_one_problem(found, "gives away the answer 'docker ps'")


def test_a_term_is_given_away_as_a_whole_word_if_long_enough(tree: Path) -> None:
    as_text = [("kind: command", "kind: text"), ("  - docker container ls", "  - ls")]
    found = typed_with(
        tree, *as_text, ("running now?", "running now? Docker PS is wrong.")
    )
    assert_one_problem(found, "gives away the answer 'docker ps'")
    # "ls" is too short to look for: it would be found in "lists" or "ls -a".
    found = typed_with(tree, *as_text, ("running now?", "running now? Not ls."))
    assert found == []


@pytest.mark.parametrize("answer", ["22", "yes", "1.5"])
def test_an_answer_yaml_would_read_as_a_number_or_true_must_be_quoted(
    tree: Path, answer: str
) -> None:
    found = typed_with(tree, ("  - docker container ls", f"  - {answer}"))
    assert_refused(found, "valid string")
    assert typed_with(tree, ("  - docker container ls", f'  - "{answer}"')) == []


def test_an_answer_is_one_short_line(tree: Path) -> None:
    found = typed_with(tree, ("  - docker container ls", '  - "docker\\nps"'))
    assert_refused(found, "should match pattern")
    found = typed_with(tree, ("  - docker container ls", f"  - {'x' * 121}"))
    assert_refused(found, "at most 120 characters")


def test_a_typed_item_can_stand_for_a_produced_answer_in_the_review_pool(
    tree: Path,
) -> None:
    # The review pool needs an item whose answer is produced, not picked
    # (ADR-0009): a typed answer is produced from memory.
    topic = TOPIC.replace("estimate-cost,", "estimate-cost, typed-command,").replace(
        "review_pool: [mcq-print, predict-print, review-hello]",
        "review_pool: [mcq-print, typed-command, parsons-order]",
    )
    write(tree, f"{TOPIC_DIR}/topic.yaml", topic)
    assert validate(tree, run=False).problems == []
    no_produced = topic.replace("typed-command, parsons-order]", "mcq-print]")
    write(tree, f"{TOPIC_DIR}/topic.yaml", no_produced)
    assert any("review pool needs" in p for p in validate(tree, run=False).problems)
