"""A multiple-choice item's right answer must not stand out by its length.

Authors tend to write the right answer in full, with the reason attached, and
the wrong ones in a few words. The app shuffles where the choices sit but
shows their text as written, so "pick the long one" then passes the question
without knowing the topic. The 2026-11-10 audit found exactly that in 102 of
the cloud track's 108 questions. Two rules stop it coming back:

- an item fails when its right answer is more than 1.5 times as long as its
  longest wrong choice;
- a topic with four or more multiple-choice items fails when the right answer
  is the longest choice in more than half of them.

Items written before the rules are listed in mcq_length_baseline.yaml and
tolerated until someone rewrites them. That list can only shrink: an entry
that no longer breaks a rule is itself a problem until its line is removed,
and nothing from the cloud track (csa.*) may be on it at all, because that
track was rewritten when the rules arrived.

validate_content.py does the walking; this file holds the rules, the
messages and the baseline file. To write the baseline, or to drop its fixed
entries:

    python -m uv run python tools/validate_content.py --write-mcq-baseline
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from content_model import McqItem

# The right answer may be up to this many times as long as the longest wrong
# choice. Over it, the eye picks the right answer out without reading.
LONGEST_RATIO = 1.5
# With fewer items than this in a topic, "more than half" is two or three
# questions, which is chance rather than a habit.
FEWEST_ITEMS = 4
# Where the baseline lives, from the repository root.
BASELINE = Path("tools") / "mcq_length_baseline.yaml"
# Entries that start like this are never tolerated: the cloud track's items
# were all rewritten when the rules arrived (after the 2026-11-10 audit), so
# it has nothing old to excuse.
NEVER_LISTED = ("csa.",)
WRITE_COMMAND = "python -m uv run python tools/validate_content.py --write-mcq-baseline"


def length(choice: str) -> int:
    """How long a choice is on the page: its characters, with a run of spaces
    or a line break in the YAML counted as the one space the page shows."""
    return len(" ".join(choice.split()))


def right_and_longest_wrong(item: McqItem) -> tuple[int, int]:
    """The length of the right answer, and of the longest wrong choice."""
    lengths = [length(choice) for choice in item.choices]
    wrong = [n for index, n in enumerate(lengths) if index != item.answer]
    return lengths[item.answer], max(wrong)


def is_longest(item: McqItem) -> bool:
    """Whether the right answer is longer than every wrong choice. A tie is
    not "the longest": picking the long one doesn't single it out."""
    right, wrong = right_and_longest_wrong(item)
    return right > wrong


def item_problem(item: McqItem) -> str | None:
    """What's wrong, if the right answer is far longer than every wrong one."""
    right, wrong = right_and_longest_wrong(item)
    if right <= LONGEST_RATIO * wrong:
        return None
    return (
        f"the right answer is {right} characters and the longest wrong choice "
        f"{wrong}: more than {LONGEST_RATIO} times as long, so picking the long "
        "one finds it without knowing the topic. Cut the right answer down to "
        "the claim itself and move the detail (why, the command, the "
        "consequence) into the explanation; make each wrong choice as full and "
        "as confident, with a real, specific wrong claim rather than padding "
        "(for short answers like numbers, pick wrong ones of the same length)"
    )


def topic_problem(items: Iterable[McqItem]) -> str | None:
    """What's wrong, if the right answer is the longest choice in more than
    half of a topic's multiple-choice items."""
    items = list(items)
    if len(items) < FEWEST_ITEMS:
        return None
    longest = [item.id for item in items if is_longest(item)]
    if 2 * len(longest) <= len(items):
        return None
    return (
        f"the right answer is the longest choice in {len(longest)} of the "
        f"topic's {len(items)} multiple-choice items ({', '.join(longest)}): "
        "more than half, so picking the long one passes most of them. In some "
        "of those, shorten the right answer or give a wrong choice a longer, "
        "specific wrong claim, until the right answer is the longest in at "
        "most half"
    )


def item_key(topic_id: str, item_id: str) -> str:
    """How the baseline names a topic's item: py.loops/mcq-range."""
    return f"{topic_id}/{item_id}"


def diagnostic_key(diagnostic_id: str, item_id: str) -> str:
    """How the baseline names a diagnostic's item: diagnostics/math/add-1.
    A topic id has no slash in it, so the two kinds can't be confused."""
    return f"diagnostics/{diagnostic_id}/{item_id}"


def may_be_listed(key: str) -> bool:
    """Whether the baseline may name this item or topic at all."""
    return not key.startswith(NEVER_LISTED)


@dataclass
class Offenders:
    """Everything that breaks a rule right now, on the baseline or not.

    Each maps the baseline's name for the item or topic to the file it's in
    and the message an author would get.
    """

    items: dict[str, tuple[Path, str]] = field(default_factory=dict)
    topics: dict[str, tuple[Path, str]] = field(default_factory=dict)


@dataclass(frozen=True)
class Baseline:
    """The offenders the validator tolerates."""

    items: frozenset[str] = frozenset()
    topics: frozenset[str] = frozenset()


class BadBaseline(Exception):
    """The baseline file can't be read as two lists of names."""


def read_baseline(path: Path) -> Baseline:
    """The baseline in `path`; an empty one if there's no such file."""
    if not path.exists():
        return Baseline()
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise BadBaseline(f"isn't valid YAML: {exc}") from exc
    if not isinstance(data, dict) or set(data) - {"items", "topics"}:
        raise BadBaseline("must hold two lists and nothing else: items and topics")
    lists: dict[str, frozenset[str]] = {}
    for name in ("items", "topics"):
        entries = data.get(name) or []
        if not isinstance(entries, list) or not all(
            isinstance(entry, str) for entry in entries
        ):
            raise BadBaseline(f"{name} must be a list of names")
        lists[name] = frozenset(entries)
    return Baseline(lists["items"], lists["topics"])


def problems(
    found: Offenders, baseline: Baseline, baseline_file: Path
) -> list[tuple[Path, str]]:
    """The problems to report: each offender the baseline doesn't cover, and
    each baseline entry that shouldn't be there."""
    reported: list[tuple[Path, str]] = []
    kinds = (
        ("item", found.items, baseline.items),
        ("topic", found.topics, baseline.topics),
    )
    for kind, offending, listed in kinds:
        for key, (path, message) in offending.items():
            if key not in listed or not may_be_listed(key):
                reported.append((path, message))
        for key in sorted(listed):
            if not may_be_listed(key):
                reported.append(
                    (
                        baseline_file,
                        f"lists {key!r}, but nothing from the cloud track (csa.*) "
                        "may be on the baseline: remove the line and fix the "
                        f"{kind} instead",
                    )
                )
            elif key not in offending:
                reported.append(
                    (
                        baseline_file,
                        f"lists the {kind} {key!r}, which no longer breaks the "
                        "answer-length rule (or no longer exists). The list only "
                        f"shrinks, so remove its line, or run: {WRITE_COMMAND}",
                    )
                )
    return reported


HEADER = f"""\
# Multiple-choice items written before the answer-length rules, which the
# validator tolerates until they are rewritten. The rules are in
# tools/mcq_lengths.py:
# - items: the right answer is more than {LONGEST_RATIO} times as long as the longest
#   wrong choice;
# - topics: of {FEWEST_ITEMS} or more items, the right answer is the longest choice in
#   more than half.
#
# Don't add to this file by hand. It was written by
#     {WRITE_COMMAND}
# and that command now only removes entries. When you fix an item or a topic,
# run it again (or delete the line yourself): the validator fails while a
# fixed entry is still listed, so this list can only shrink.
"""


def render(items: Iterable[str], topics: Iterable[str]) -> str:
    """The baseline file's text: the header, then the two lists, sorted."""

    def as_list(name: str, entries: Iterable[str]) -> str:
        entries = sorted(entries)
        if not entries:
            return f"{name}: []\n"
        return f"{name}:\n" + "".join(f"  - {entry}\n" for entry in entries)

    return HEADER + as_list("items", items) + as_list("topics", topics)


def write_baseline(path: Path, found: Offenders) -> str:
    """Write the baseline, and return a line saying what was done.

    The first time, it lists everything that offends now (never the cloud
    track's). Once the file exists it only drops the entries that no longer
    offend: a new offender is never added, so it stays a problem to fix.
    """
    if path.exists():
        old = read_baseline(path)
        items = {key for key in old.items if key in found.items}
        topics = {key for key in old.topics if key in found.topics}
    else:
        old = None
        items, topics = set(found.items), set(found.topics)
    items = {key for key in items if may_be_listed(key)}
    topics = {key for key in topics if may_be_listed(key)}
    if old is None:
        did = "listed what breaks a rule today"
    else:
        dropped = len(old.items) + len(old.topics) - len(items) - len(topics)
        did = f"removed {dropped} entries that no longer belong on it"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render(items, topics), encoding="utf-8", newline="\n")
    return (
        f"{path.name}: {did}. It now lists {len(items)} items and {len(topics)} topics."
    )
