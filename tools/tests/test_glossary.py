"""The glossary (ADR-0026): the validator accepts a topic's glossary.yaml
written as content/README.md says, and catches each kind of mistake."""

from pathlib import Path

import pytest
from content_fixture import TOPIC, make_valid_tree, write
from validate_content import uses_word, validate

TOPIC_DIR = "content/topics/t.hello"
# The fixture's lesson: "Watch for print." ... "print shows text."
GOOD = """- term: print
  aliases: [print function]
  definition: The function that shows text in the output, followed by a new line.
"""


@pytest.fixture
def tree(tmp_path: Path) -> Path:
    return make_valid_tree(tmp_path)


def problems(root: Path) -> list[str]:
    return validate(root, run=False).problems


def assert_reported(root: Path, fragment: str) -> None:
    found = problems(root)
    assert any(fragment in problem for problem in found), (
        f"expected a problem mentioning {fragment!r}, got: {found}"
    )


def second_topic(root: Path, glossary: str, status: str = "planned") -> None:
    """Another topic, an outline in the same module, with a glossary."""
    folder = "content/topics/t.other"
    write(
        root,
        f"{folder}/topic.yaml",
        f"id: t.other\nkind: topic\nstatus: {status}\ntitle: Other\n"
        "summary: Another topic.\nprerequisites: []\nestimated_minutes: 10\n"
        "rev: 1\nobjectives:\n  - Something else.\n",
    )
    write(root, f"{folder}/glossary.yaml", glossary)
    track = root / "content/tracks/test.yaml"
    track.write_text(
        track.read_text("utf-8").replace("[t.hello]", "[t.hello, t.other]"),
        encoding="utf-8",
        newline="\n",
    )


def test_a_good_glossary_passes(tree: Path) -> None:
    write(tree, f"{TOPIC_DIR}/glossary.yaml", GOOD)
    report = validate(tree, run=False)
    assert report.problems == []
    assert report.counts["glossary terms"] == 1


@pytest.mark.parametrize(
    ("glossary", "fragment"),
    [
        ("[]\n", "at least 1 item"),
        ("- term: print\n", "definition: Field required"),
        ("- term: print\n  definition: x\n  extra: 1\n", "extra: Extra inputs"),
        ("- term: '`print`'\n  definition: x\n", "String should match pattern"),
        (
            "- term: print\n  aliases: [Print]\n  definition: x\n",
            "the term and its aliases must all be different",
        ),
        (
            f"- term: print\n  definition: {'word ' * 41}\n",
            "the definition has 41 words; keep it to 40",
        ),
        (
            "- term: print\n  definition: |\n    one line\n    and another\n",
            "the definition is one line",
        ),
    ],
)
def test_badly_written_glossaries_are_caught(
    tree: Path, glossary: str, fragment: str
) -> None:
    write(tree, f"{TOPIC_DIR}/glossary.yaml", glossary)
    assert_reported(tree, fragment)


def test_a_term_belongs_to_one_topic_only(tree: Path) -> None:
    write(tree, f"{TOPIC_DIR}/glossary.yaml", GOOD)
    # Ignoring case, and an alias counts as much as a term.
    second_topic(tree, "- term: Print Function\n  definition: Another meaning.\n")
    assert_reported(
        tree,
        "'Print Function' is already defined in t.hello (as 'print function')",
    )


def test_a_term_twice_in_one_topic_is_caught(tree: Path) -> None:
    write(
        tree,
        f"{TOPIC_DIR}/glossary.yaml",
        GOOD + "- term: Print\n  definition: Said again.\n",
    )
    assert_reported(tree, "'Print' is already defined in this topic")


def test_a_ready_topic_defines_only_what_its_lesson_uses(tree: Path) -> None:
    write(
        tree,
        f"{TOPIC_DIR}/glossary.yaml",
        GOOD + "- term: interpreter\n  definition: Runs Python.\n",
    )
    assert_reported(tree, "'interpreter' isn't in this topic's lesson")


def test_an_outline_may_list_terms_before_its_lesson(tree: Path) -> None:
    second_topic(tree, "- term: loop\n  definition: Code that runs again.\n")
    assert problems(tree) == []


def test_a_checkpoint_teaches_no_terms(tree: Path) -> None:
    write(tree, "content/topics/t.m1.checkpoint/glossary.yaml", GOOD)
    assert_reported(tree, "a checkpoint teaches no terms of its own")


def test_whole_words_with_plurals_count_as_used() -> None:
    assert uses_word("Two NATs and a gateway.", "NAT")
    assert uses_word("the Page cache.", "page cache")
    assert uses_word("several processes", "process")
    assert not uses_word("NATIVE code", "NAT")
    assert not uses_word("a pre-NAT step", "NAT")


def test_the_fixture_topic_is_ready() -> None:
    # The lesson rule above applies to ready topics; the fixture's is.
    assert "status: ready" in TOPIC
