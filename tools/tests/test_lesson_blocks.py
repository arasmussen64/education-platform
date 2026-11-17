"""The lesson building blocks (ADR-0026): the validator accepts each one
written as content/README.md says, and catches each kind of mistake."""

from pathlib import Path

import pytest
from content_fixture import make_valid_tree, write
from lesson_blocks import blank_code, problems, tags_in
from validate_content import validate

TOPIC_DIR = "content/topics/t.hello"

QUICK = {"mcq-print", "predict-print", "parsons-order"}
EXERCISES = {"fill-hello", "write-hello"}
PRACTICE = ["mcq-print", "predict-print", "fill-hello", "write-hello"]

STORY = (
    '<Story title="The day the printer said nothing" '
    'source="https://example.com/postmortem" sourceTitle="Our printer postmortem" '
    'license="linked, not copied">\n\nA print job went missing for an hour.\n\n'
    "</Story>"
)


def lesson(intro: str = "Watch for print.", after: str = "") -> str:
    return (
        f"<Intro>\n\n{intro}\n\n</Intro>\n\n<Resource index={{0}} />\n\n{after}\n\n"
        "<Recap>\n\nprint shows text.\n\n</Recap>\n"
    )


def found(text: str) -> list[str]:
    return problems(text, QUICK, EXERCISES, PRACTICE)


def assert_found(text: str, fragment: str) -> None:
    got = found(text)
    assert any(fragment in problem for problem in got), (
        f"expected a problem mentioning {fragment!r}, got: {got}"
    )


# --- Reading the tags -------------------------------------------------------


def test_tags_inside_code_are_not_tags() -> None:
    text = (
        'Run `<Foo>` here.\n\n```text\n<Bar baz>\n```\n\n<Check item="mcq-print" />\n'
    )
    assert [tag.name for tag in tags_in(text)] == ["Check"]
    # Code is blanked, not removed, so positions and lines still match.
    assert len(blank_code(text)) == len(text)
    assert tags_in(text)[0].line == 7


def test_attributes_are_read_in_either_quote_and_as_expressions() -> None:
    (tag,) = tags_in(
        """<Story title='He said "hi"' source="https://a.example/x" n={1 + {2}} on />"""
    )
    assert tag.attributes == {
        "title": 'He said "hi"',
        "source": "https://a.example/x",
        "n": None,
        "on": None,
    }
    assert tag.self_closing


# --- Good lessons -------------------------------------------------------------


def test_every_block_written_as_the_readme_says_passes() -> None:
    text = lesson(
        intro=(
            '<Puzzle question="Why does `print` add a new line?">\n\n'
            "Because its `end` is `\\n` unless you say otherwise.\n\n</Puzzle>\n\n"
            'Watch for print.\n\n<Check item="mcq-print" />\n\nMore.'
        ),
        after=f'{STORY}\n\n<Check item="predict-print" />',
    )
    assert found(text) == []


def test_the_lessons_in_content_all_pass() -> None:
    # The real lessons were written before the blocks; none may break a rule.
    root = Path(__file__).resolve().parents[2]
    report = validate(root, run=False)
    assert [p for p in report.problems if "lesson.mdx" in p] == []


# --- Mistakes the validator catches -----------------------------------------


def test_an_unknown_tag_is_caught() -> None:
    assert_found(lesson(intro="<Callout>Hi</Callout>"), "<Callout> isn't a lesson")


def test_a_hand_written_term_is_caught() -> None:
    assert_found(lesson(intro="<Term>NAT</Term>"), "added by the glossary")


@pytest.mark.parametrize(
    ("check", "fragment"),
    [
        ('<Check item="nope" />', "no such question in this topic"),
        ('<Check item="fill-hello" />', "is an exercise"),
        ('<Check item="parsons-order" />', "list it in topic.yaml's practice"),
        ("<Check item={'mcq-print'} />", 'needs item="..."'),
        ("<Check />", 'needs item="..."'),
        ('<Check item="mcq-print" extra="1" />', "<Check> has no extra"),
        ('<Check item="mcq-print">', "stands alone"),
        ('<Check item="mcq-print />', "isn't finished"),
    ],
)
def test_check_mistakes_are_caught(check: str, fragment: str) -> None:
    assert_found(lesson(after=check), fragment)


def test_a_question_placed_twice_is_caught() -> None:
    text = lesson(
        intro='<Check item="mcq-print" />', after='<Check item="mcq-print" />'
    )
    assert_found(text, "placed twice")


@pytest.mark.parametrize(
    ("text", "fragment"),
    [
        (
            lesson(
                intro='Text first.\n\n<Puzzle question="Why?">\n\nBecause.\n\n</Puzzle>'
            ),
            "goes first inside <Intro>",
        ),
        (
            lesson(after='<Puzzle question="Why?">\n\nBecause.\n\n</Puzzle>'),
            "goes first inside <Intro>",
        ),
        (lesson(intro='<Puzzle question="Why?" />'), "needs a closing"),
        (lesson(intro='<Puzzle question="Why?">\n\n</Puzzle>'), "needs the answer"),
        (lesson(intro="<Puzzle>\n\nBecause.\n\n</Puzzle>"), 'needs question="..."'),
        (
            lesson(intro=f'<Puzzle question="{"why " * 51}">\n\nBecause.\n\n</Puzzle>'),
            "the puzzle's question has 51 words",
        ),
        (
            lesson(intro=f'<Puzzle question="Why?">\n\n{"so " * 151}\n\n</Puzzle>'),
            "the puzzle's answer has 151 words",
        ),
        (
            lesson(
                intro='<Puzzle question="Why?">\n\nA.\n\n</Puzzle>',
                after='<Puzzle question="And?">\n\nB.\n\n</Puzzle>',
            ),
            "one <Puzzle> at most",
        ),
        (
            lesson(
                intro='<Puzzle question="Why?">\n\n<Check item="mcq-print" />\n'
                "\n</Puzzle>"
            ),
            "<Check> can't go inside a <Puzzle>",
        ),
        (lesson(intro='<Puzzle question="Why?">\n\nBecause.'), "never closed"),
    ],
)
def test_puzzle_mistakes_are_caught(text: str, fragment: str) -> None:
    assert_found(text, fragment)


@pytest.mark.parametrize(
    ("story", "fragment"),
    [
        (STORY.replace("https://", "http://"), "must be an https:// link"),
        (
            STORY.replace('title="The day the printer said nothing" ', ""),
            'needs title="..."',
        ),
        (STORY.replace(' license="linked, not copied"', ""), 'needs license="..."'),
        (
            STORY.replace('sourceTitle="Our printer postmortem"', 'sourceTitle=""'),
            "sourceTitle is empty",
        ),
        (STORY.replace("A print job went missing for an hour.", ""), "needs the story"),
        (
            STORY.replace("A print job went missing for an hour.", "word " * 201),
            "the story has 201 words; keep it to 200",
        ),
    ],
)
def test_story_mistakes_are_caught(story: str, fragment: str) -> None:
    assert_found(lesson(after=story), fragment)


@pytest.mark.parametrize(
    "text",
    [
        lesson(after='Try this: <Check item="mcq-print" />'),
        lesson(after='<Check item="mcq-print" /> and then read on.'),
        lesson(after=STORY.replace("\n\n</Story>", " The end.</Story>")),
    ],
)
def test_a_block_in_the_middle_of_a_line_is_caught(text: str) -> None:
    # MDX would draw the box inside a paragraph.
    assert_found(text, "goes on a line of its own")


def test_a_tag_written_over_several_lines_is_on_its_own_line() -> None:
    story = STORY.replace(" source=", "\n  source=")
    assert found(lesson(after=story)) == []


def test_a_stray_closing_tag_is_caught() -> None:
    assert_found(lesson(after="</Story>"), "isn't open")


def test_the_validator_reports_lesson_problems_with_their_line(tmp_path: Path) -> None:
    tree = make_valid_tree(tmp_path)
    write(tree, f"{TOPIC_DIR}/lesson.mdx", lesson(after='<Check item="nope" />'))
    report = validate(tree, run=False)
    assert any(
        p.startswith(f"{TOPIC_DIR}/lesson.mdx: line 9: <Check item='nope'>")
        for p in report.problems
    ), report.problems
