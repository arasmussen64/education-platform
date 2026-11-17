"""The tags a lesson.mdx may use, and the rules for each (ADR-0026).

A lesson is MDX: Markdown with a few components the app supplies
(web/src/components/LessonView.tsx). The app can only draw the ones it
knows, and MDX stops the whole page with an error at the first one it
doesn't, so this module reads every tag in a lesson and checks it before a
learner can open the page:

- <Intro>, <Resource index={0} /> and <Recap>, the lesson's frame (ADR-0004);
- <Check item="<item id>" />, one of the topic's practice quick questions,
  asked inside the lesson;
- <Puzzle question="…">answer</Puzzle>, first in the intro;
- <Story title="…" source="https://…" sourceTitle="…" license="…">…</Story>,
  a real incident in our own words.

Anything inside a code block or `inline code` is code, not a tag, so it's
blanked out before the tags are read, as MDX itself would treat it.

validate_content.py calls problems() for every topic's lesson.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# Every component a lesson may use. <Term> is never written by hand: the
# glossary step adds it while the app is built.
BLOCKS = ("Intro", "Resource", "Recap", "Check", "Puzzle", "Story")

# How long each kind of text may be, in words. A story is a page-turner, not
# a second lesson; a puzzle is a question and a short answer.
STORY_WORDS_MAX = 200
PUZZLE_QUESTION_WORDS_MAX = 50
PUZZLE_ANSWER_WORDS_MAX = 150

# The string attributes each block must have, and the only ones it may have.
REQUIRED = {
    "Check": ("item",),
    "Puzzle": ("question",),
    "Story": ("title", "source", "sourceTitle", "license"),
}
# Blocks that wrap text of their own, so they need a closing tag.
WRAPPERS = {"Intro", "Recap", "Puzzle", "Story"}
# Blocks the page draws as boxes. Written in the middle of a line of text,
# MDX would put the box inside a paragraph, which a page can't hold, so
# each of their tags goes on a line of its own.
OWN_LINE = {"Check", "Puzzle", "Story"}

FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
INLINE_CODE = re.compile(r"(`+)(?:(?!\n[ \t]*\n).)+?\1", re.DOTALL)
TAG_START = re.compile(r"<(/?)([A-Z][A-Za-z0-9.]*)")
ATTRIBUTE_NAME = re.compile(r"[A-Za-z_][\w:.-]*")
HTTPS_URL = re.compile(r"^https://[^\s\"'<>]+$")


@dataclass
class Tag:
    name: str
    closing: bool
    self_closing: bool
    # Each attribute's text, or None when its value is a {expression} or it
    # has no value at all.
    attributes: dict[str, str | None] = field(default_factory=dict)
    start: int = 0
    end: int = 0
    line: int = 0
    # Set when the tag couldn't be read to its end.
    broken: bool = False


def blank_code(text: str) -> str:
    """The lesson with every code block and inline code span turned into
    spaces, keeping each line where it was, so line numbers still match."""
    lines = text.split("\n")
    fence: str | None = None
    for number, line in enumerate(lines):
        match = FENCE.match(line)
        if fence is None and match:
            fence = match.group(1)[0] * len(match.group(1))
            lines[number] = " " * len(line)
        elif fence is not None:
            if match and match.group(1).startswith(fence):
                fence = None
            lines[number] = " " * len(line)
    blanked = "\n".join(lines)
    return INLINE_CODE.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), blanked)


def read_tag(text: str, start: int) -> Tag | None:
    """The tag that starts at `start` (just at its "<"), or None if there's
    no component tag there."""
    match = TAG_START.match(text, start)
    if not match:
        return None
    tag = Tag(
        name=match.group(2),
        closing=bool(match.group(1)),
        self_closing=False,
        start=start,
        line=text.count("\n", 0, start) + 1,
    )
    at = match.end()
    while at < len(text):
        while at < len(text) and text[at].isspace():
            at += 1
        if text.startswith("/>", at):
            tag.self_closing = True
            tag.end = at + 2
            return tag
        if text.startswith(">", at):
            tag.end = at + 1
            return tag
        name = ATTRIBUTE_NAME.match(text, at)
        if not name:
            break
        at = name.end()
        value: str | None = None
        if text.startswith("=", at):
            at += 1
            quote = text[at : at + 1]
            if quote in ('"', "'"):
                close = text.find(quote, at + 1)
                if close == -1:
                    break
                value = text[at + 1 : close]
                at = close + 1
            elif quote == "{":
                depth = 0
                while at < len(text):
                    depth += {"{": 1, "}": -1}.get(text[at], 0)
                    at += 1
                    if depth == 0:
                        break
            else:
                break
        tag.attributes[name.group(0)] = value
    tag.broken = True
    tag.end = at
    return tag


def tags_in(text: str) -> list[Tag]:
    """Every component tag in a lesson, opening and closing, in order."""
    blanked = blank_code(text)
    found: list[Tag] = []
    at = blanked.find("<")
    while at != -1:
        tag = read_tag(blanked, at)
        if tag is None:
            at = blanked.find("<", at + 1)
            continue
        found.append(tag)
        at = blanked.find("<", max(tag.end, at + 1))
    return found


def on_own_line(text: str, tag: Tag) -> bool:
    """Whether nothing but spaces shares a line with the tag."""
    line_start = text.rfind("\n", 0, tag.start) + 1
    line_end = text.find("\n", tag.end)
    after = text[tag.end :] if line_end == -1 else text[tag.end : line_end]
    return not text[line_start : tag.start].strip() and not after.strip()


def words(text: str) -> int:
    """How many words a piece of Markdown has (tags and code included)."""
    return len(re.findall(r"\S+", text))


def problems(
    text: str, quick_questions: set[str], exercises: set[str], practice: list[str]
) -> list[str]:
    """What's wrong with a lesson's tags, each starting with its line.

    `quick_questions` are the topic's recall items (any type, so a type added
    later works at once), `exercises` its exercises, and `practice` its
    practice ladder from topic.yaml.
    """
    found: list[str] = []
    tags = tags_in(text)
    # The blocks still open, innermost last, each with its opening tag.
    open_blocks: list[Tag] = []
    placed: set[str] = set()
    puzzles = 0
    # What follows the last <Intro>, so a puzzle can be checked to come first.
    intro_ends_at: int | None = None

    def add(tag: Tag, message: str) -> None:
        found.append(f"line {tag.line}: {message}")

    for tag in tags:
        if tag.broken:
            add(tag, f"<{tag.name}> isn't finished: check its quotes and its >")
            continue
        if tag.name in OWN_LINE and not on_own_line(text, tag):
            slash = "/" if tag.closing else ""
            add(tag, f"<{slash}{tag.name}> goes on a line of its own")
        if tag.name == "Term":
            add(
                tag,
                "<Term> is added by the glossary when the app is built; write "
                "the plain word, and list it in a topic's glossary.yaml",
            )
            continue
        if tag.name not in BLOCKS:
            add(
                tag,
                f"<{tag.name}> isn't a lesson building block; a lesson can use "
                f"{', '.join(f'<{name}>' for name in BLOCKS)} (content/README.md)",
            )
            continue

        if tag.closing:
            if open_blocks and open_blocks[-1].name == tag.name:
                opening = open_blocks.pop()
                body = text[opening.end : tag.start]
                check_body(opening, body, add)
            else:
                add(tag, f"</{tag.name}> closes a <{tag.name}> that isn't open")
            continue

        inside = open_blocks[-1].name if open_blocks else None
        if inside in ("Puzzle", "Story"):
            add(tag, f"<{tag.name}> can't go inside a <{inside}>")
        if tag.name in WRAPPERS and tag.self_closing:
            add(tag, f"<{tag.name}> wraps text, so it needs a closing </{tag.name}>")
        elif tag.name in WRAPPERS:
            open_blocks.append(tag)
        elif not tag.self_closing:
            add(tag, f"<{tag.name}> stands alone: write it <{tag.name} ... />")

        for name in REQUIRED.get(tag.name, ()):
            value = tag.attributes.get(name)
            if value is None:
                add(tag, f'<{tag.name}> needs {name}="..." (plain text in quotes)')
            elif not value.strip():
                add(tag, f"<{tag.name}>'s {name} is empty")
        allowed = set(REQUIRED.get(tag.name, ()))
        if tag.name == "Resource":
            allowed = {"index"}
        for name in tag.attributes:
            if name not in allowed:
                add(tag, f"<{tag.name}> has no {name}")

        if tag.name == "Intro":
            intro_ends_at = tag.end
        elif tag.name == "Check":
            check_check(tag, quick_questions, exercises, practice, placed, add)
        elif tag.name == "Puzzle":
            puzzles += 1
            if puzzles == 2:
                add(tag, "a lesson has one <Puzzle> at most")
            first_in_intro = (
                inside == "Intro"
                and intro_ends_at is not None
                and not text[intro_ends_at : tag.start].strip()
            )
            if not first_in_intro:
                add(tag, "<Puzzle> goes first inside <Intro>, before any text")
            question = tag.attributes.get("question") or ""
            if words(question) > PUZZLE_QUESTION_WORDS_MAX:
                add(
                    tag,
                    f"the puzzle's question has {words(question)} words; "
                    f"keep it to {PUZZLE_QUESTION_WORDS_MAX}",
                )
        elif tag.name == "Story":
            source = tag.attributes.get("source") or ""
            if source and not HTTPS_URL.match(source):
                add(tag, f"<Story>'s source must be an https:// link, not {source!r}")

    for tag in open_blocks:
        add(tag, f"<{tag.name}> is never closed with </{tag.name}>")
    return found


def check_check(
    tag: Tag,
    quick_questions: set[str],
    exercises: set[str],
    practice: list[str],
    placed: set[str],
    add,
) -> None:
    """A <Check item="…" />: a quick question of this topic's practice
    ladder, placed once."""
    item = tag.attributes.get("item")
    if not item:
        return
    if item in exercises:
        add(
            tag,
            f"<Check item={item!r}> is an exercise; only quick questions "
            "(multiple-choice, predict, Parsons, estimate and the like) go in "
            "the lesson",
        )
    elif item not in quick_questions:
        add(tag, f"<Check item={item!r}>: there's no such question in this topic")
    elif item not in practice:
        add(
            tag,
            f"<Check item={item!r}>: list it in topic.yaml's practice, where "
            "it counts like the rest of the ladder",
        )
    if item in placed:
        add(tag, f"<Check item={item!r}> is placed twice; a question goes in once")
    placed.add(item)


def check_body(opening: Tag, body: str, add) -> None:
    """The text a <Puzzle> or <Story> wraps: there, and short."""
    if opening.name not in ("Puzzle", "Story"):
        return
    if not body.strip():
        what = "the answer" if opening.name == "Puzzle" else "the story"
        add(opening, f"<{opening.name}> needs {what} between its tags")
        return
    limit = PUZZLE_ANSWER_WORDS_MAX if opening.name == "Puzzle" else STORY_WORDS_MAX
    count = words(body)
    if count > limit:
        what = "puzzle's answer" if opening.name == "Puzzle" else "story"
        add(opening, f"the {what} has {count} words; keep it to {limit}")
