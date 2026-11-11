"""The answer-length rules for multiple-choice items, and their baseline."""

from pathlib import Path

import mcq_lengths
import pytest
from content_model import McqItem
from mcq_lengths import Baseline, Offenders


def mcq(item_id: str, right: int, *wrong: int) -> McqItem:
    """An item whose right answer has `right` characters and whose wrong
    choices have the lengths in `wrong`. Each choice is a different letter,
    repeated, so the choices are all different."""
    letters = "abcdefgh"
    lengths = [right, *wrong]
    return McqItem(
        id=item_id,
        type="mcq",
        rev=1,
        prompt="Which one?",
        choices=[letters[i] * n for i, n in enumerate(lengths)],
        answer=0,
        explanation="Because.",
    )


def test_length_counts_what_the_page_shows() -> None:
    assert mcq_lengths.length("a  folded\n  line ") == len("a folded line")


def test_a_right_answer_up_to_one_and_a_half_times_is_fine() -> None:
    assert mcq_lengths.item_problem(mcq("ok", 60, 40, 30)) is None
    assert mcq_lengths.item_problem(mcq("short", 20, 40, 30)) is None


def test_a_right_answer_over_one_and_a_half_times_is_a_problem() -> None:
    problem = mcq_lengths.item_problem(mcq("long", 61, 40, 30))
    assert problem is not None
    # The numbers, so the author can see how far off it is, and what to do.
    assert "61 characters and the longest wrong choice 40" in problem
    assert "move the detail" in problem
    assert "rather than padding" in problem


def test_the_longest_wrong_choice_is_the_one_compared() -> None:
    # 61 is over 1.5 times 40 but not 1.5 times 45.
    assert mcq_lengths.item_problem(mcq("ok", 61, 30, 45, 40)) is None


def test_the_right_answer_is_found_wherever_it_sits() -> None:
    item = McqItem(
        id="last",
        type="mcq",
        rev=1,
        prompt="Which one?",
        choices=["a" * 10, "b" * 12, "c" * 40],
        answer=2,
        explanation="Because.",
    )
    assert mcq_lengths.right_and_longest_wrong(item) == (40, 12)
    assert mcq_lengths.item_problem(item) is not None


def test_a_tie_for_longest_is_not_the_longest() -> None:
    assert mcq_lengths.is_longest(mcq("longer", 41, 40, 30))
    assert not mcq_lengths.is_longest(mcq("tie", 40, 40, 30))
    assert not mcq_lengths.is_longest(mcq("shorter", 39, 40, 30))


def test_a_topic_with_few_items_is_never_a_problem() -> None:
    items = [mcq(f"q{n}", 50, 40) for n in range(3)]
    assert mcq_lengths.topic_problem(items) is None


def test_half_the_items_longest_is_fine() -> None:
    items = [mcq("q1", 50, 40), mcq("q2", 50, 40), mcq("q3", 30, 40), mcq("q4", 40, 40)]
    assert mcq_lengths.topic_problem(items) is None


def test_more_than_half_the_items_longest_is_a_problem() -> None:
    items = [mcq("q1", 50, 40), mcq("q2", 50, 40), mcq("q3", 41, 40), mcq("q4", 30, 40)]
    problem = mcq_lengths.topic_problem(items)
    assert problem is not None
    assert "in 3 of the topic's 4 multiple-choice items (q1, q2, q3)" in problem
    assert "at most half" in problem


# --- The baseline ----------------------------------------------------------------


def found(*item_keys: str, topics: tuple[str, ...] = ()) -> Offenders:
    """Offenders with these names, each in a file named after it."""
    return Offenders(
        items={key: (Path(f"{key}.yaml"), f"{key} is too long") for key in item_keys},
        topics={key: (Path(key), f"{key} is mostly longest") for key in topics},
    )


FILE = Path("tools/mcq_length_baseline.yaml")


def test_an_offender_that_is_not_listed_is_reported() -> None:
    reported = mcq_lengths.problems(found("py.a/q1"), Baseline(), FILE)
    assert reported == [(Path("py.a/q1.yaml"), "py.a/q1 is too long")]


def test_listed_offenders_are_tolerated() -> None:
    baseline = Baseline(frozenset({"py.a/q1"}), frozenset({"py.a"}))
    assert (
        mcq_lengths.problems(found("py.a/q1", topics=("py.a",)), baseline, FILE) == []
    )


def test_an_entry_that_no_longer_offends_is_a_problem() -> None:
    baseline = Baseline(frozenset({"py.a/q1", "py.a/fixed"}), frozenset({"py.a"}))
    reported = mcq_lengths.problems(found("py.a/q1"), baseline, FILE)
    assert [path for path, _ in reported] == [FILE, FILE]
    assert "lists the item 'py.a/fixed', which no longer breaks" in reported[0][1]
    assert "--write-mcq-baseline" in reported[0][1]
    assert "lists the topic 'py.a', which no longer breaks" in reported[1][1]


def test_the_cloud_track_is_never_tolerated() -> None:
    baseline = Baseline(frozenset({"csa.linux.shell/q1"}), frozenset({"csa.linux.cpu"}))
    offenders = found("csa.linux.shell/q1", topics=("csa.linux.cpu",))
    reported = mcq_lengths.problems(offenders, baseline, FILE)
    messages = [message for _, message in reported]
    # Each is reported as if it weren't listed, and the listing is a problem too.
    assert "csa.linux.shell/q1 is too long" in messages
    assert "csa.linux.cpu is mostly longest" in messages
    listed = [message for path, message in reported if path == FILE]
    assert len(listed) == 2
    assert all("nothing from the cloud track (csa.*)" in each for each in listed)


def test_a_missing_baseline_is_an_empty_one(tmp_path: Path) -> None:
    assert mcq_lengths.read_baseline(tmp_path / "none.yaml") == Baseline()


@pytest.mark.parametrize(
    ("text", "complaint"),
    [
        ("items: [unclosed", "isn't valid YAML"),
        ("- py.a/q1\n", "two lists and nothing else"),
        ("items: []\nextra: []\n", "two lists and nothing else"),
        ("items: py.a/q1\n", "items must be a list of names"),
        ("topics: [1, 2]\n", "topics must be a list of names"),
    ],
)
def test_a_baseline_that_cannot_be_read_says_why(
    tmp_path: Path, text: str, complaint: str
) -> None:
    path = tmp_path / "baseline.yaml"
    path.write_text(text, encoding="utf-8")
    with pytest.raises(mcq_lengths.BadBaseline, match=complaint):
        mcq_lengths.read_baseline(path)


def test_the_first_write_lists_every_offender_but_the_cloud_tracks(
    tmp_path: Path,
) -> None:
    path = tmp_path / "tools" / "baseline.yaml"
    offenders = found(
        "py.b/q2", "py.a/q1", "csa.linux.shell/q1", topics=("py.a", "csa.linux.cpu")
    )
    said = mcq_lengths.write_baseline(path, offenders)
    assert "listed what breaks a rule today" in said
    assert "2 items and 1 topics" in said
    assert mcq_lengths.read_baseline(path) == Baseline(
        frozenset({"py.a/q1", "py.b/q2"}), frozenset({"py.a"})
    )
    text = path.read_text(encoding="utf-8")
    # Sorted, one entry a line, under a header that names the command.
    assert text.endswith("items:\n  - py.a/q1\n  - py.b/q2\ntopics:\n  - py.a\n")
    assert mcq_lengths.WRITE_COMMAND in text


def test_a_later_write_only_removes_entries(tmp_path: Path) -> None:
    path = tmp_path / "baseline.yaml"
    mcq_lengths.write_baseline(path, found("py.a/q1", "py.a/q2", topics=("py.a",)))
    # q2 and the topic were fixed; q3 is a new offender.
    said = mcq_lengths.write_baseline(path, found("py.a/q1", "py.a/q3"))
    assert "removed 2 entries" in said
    assert mcq_lengths.read_baseline(path) == Baseline(frozenset({"py.a/q1"}))
    assert path.read_text(encoding="utf-8").endswith(
        "items:\n  - py.a/q1\ntopics: []\n"
    )


def test_the_repository_baseline_is_as_the_command_writes_it() -> None:
    # Hand edits other than deleting a line would show up here.
    path = Path(__file__).resolve().parents[2] / mcq_lengths.BASELINE
    baseline = mcq_lengths.read_baseline(path)
    assert path.read_text(encoding="utf-8") == mcq_lengths.render(
        baseline.items, baseline.topics
    )
    assert all(mcq_lengths.may_be_listed(key) for key in baseline.items)
    assert all(mcq_lengths.may_be_listed(key) for key in baseline.topics)
