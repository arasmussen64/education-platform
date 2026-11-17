"""How a typed answer is read before it's compared (ADR-0027).

A typed item's accepted answers, its known mistakes and what the learner
types all go through `normalise` first, so "Docker PS", " docker  ps " and
"$ docker ps" can be compared with the answer as the item's rules say.

The browser does exactly the same in web/src/content/typed.ts. Both are
tested against the same cases, tools/tests/typed_cases.json, so the two
can't drift apart: an answer the validator proved distinct is distinct on
the page too.
"""

from __future__ import annotations

import unicodedata
from typing import Literal

Kind = Literal["text", "command"]
Case = Literal["sensitive", "insensitive"]

# What a phone's "smart punctuation" types in place of plain quotes.
CURLY_QUOTES = str.maketrans(
    {
        "“": '"',
        "”": '"',
        "„": '"',
        "‘": "'",
        "’": "'",
        "‚": "'",
    }
)
# Hyphens and a minus sign that look like "-" but aren't.
SHORT_DASHES = "‐‑‒−"
# What a phone or a Mac types for "--": an en dash or an em dash. In a
# command they stand for "--" (docker ps --all); in text, for a hyphen.
LONG_DASHES = "–—―"
# A shell prompt copied in front of a command: "$ ", "> " or "PS> ".
PROMPTS = ("$", ">", "PS>")
# Surrounding marks a learner may put round a term: "VNet", 'VNet', `VNet`.
WRAPPERS = "\"'`"
# An answer this short is never forgiven a slip: one letter is a large part
# of it, and short answers are often codes (NTFS, NFS) where it matters.
SHORTEST_FORGIVEN = 5


def default_case(kind: Kind) -> Case:
    """A command's case matters (ls and LS are different commands); a
    term's doesn't (VNet and vnet are the same word)."""
    return "sensitive" if kind == "command" else "insensitive"


def _dashes(text: str, kind: Kind) -> str:
    long_dash = "--" if kind == "command" else "-"
    for dash in SHORT_DASHES:
        text = text.replace(dash, "-")
    for dash in LONG_DASHES:
        text = text.replace(dash, long_dash)
    return text


def _unwrap(text: str, marks: str) -> str:
    """Takes one pair of matching marks off the ends: "VNet" is VNet."""
    if len(text) >= 2 and text[0] == text[-1] and text[0] in marks:
        return text[1:-1].strip()
    return text


def _without_prompt(text: str) -> str:
    """Takes a copied shell prompt off the front: "$ ls" is ls. Only a
    prompt followed by a space, so "$HOME" and ">file" stay as they are."""
    for prompt in PROMPTS:
        rest = text[len(prompt) :]
        if text.startswith(prompt) and rest[:1].isspace():
            return rest.strip()
    return text


def _without_full_stop(text: str) -> str:
    return text[:-1].rstrip() if text.endswith(".") else text


def normalise(text: str, kind: Kind, case: Case) -> str:
    """The standard form of a typed answer, in this order:

    1. Unicode's compatibility form (NFKC): a non-breaking space becomes a
       space, and full-width letters become ordinary ones.
    2. Curly quotes become straight ones, and look-alike dashes become "-";
       an en or em dash becomes "--" in a command, "-" in text.
    3. Spaces, tabs and line breaks: any run of them is one space, and none
       at either end.
    4. For a command: one pair of backticks round it, then a copied prompt
       ("$ ", "> " or "PS> ") in front, are taken off.
       For text: a full stop at the end, one pair of quotes or backticks
       round it, then a full stop at the end again, are taken off.
    5. Lower case, when the item's case is insensitive.
    """
    text = unicodedata.normalize("NFKC", text).translate(CURLY_QUOTES)
    text = " ".join(_dashes(text, kind).split())
    if kind == "command":
        text = _without_prompt(_unwrap(text, "`"))
    else:
        text = _without_full_stop(_unwrap(_without_full_stop(text), WRAPPERS))
    return text.lower() if case == "insensitive" else text


def is_slip(typed: str, answer: str) -> bool:
    """Whether `typed` is `answer` with one slip of the fingers among its
    letters: one letter changed, added or left out, or two neighbouring
    letters swapped. Both are already normalised. A slip involving a digit,
    a space or a symbol isn't one (RAID 5 and RAID 6 are different
    answers), nor is a letter in the other case (an item whose case matters
    means it), and an answer shorter than five characters is never forgiven
    one. Text items only: the page never forgives a command."""
    if len(answer) < SHORTEST_FORGIVEN or typed == answer:
        return False
    if len(typed) == len(answer):
        pairs = enumerate(zip(typed, answer, strict=True))
        differ = [i for i, (a, b) in pairs if a != b]
        if len(differ) == 1:
            a, b = typed[differ[0]], answer[differ[0]]
            return a.isalpha() and b.isalpha() and a.lower() != b.lower()
        if len(differ) == 2 and differ[1] == differ[0] + 1:
            i, j = differ
            swapped = typed[i] == answer[j] and typed[j] == answer[i]
            return swapped and typed[i].isalpha() and typed[j].isalpha()
        return False
    shorter, longer = sorted((typed, answer), key=len)
    if len(longer) - len(shorter) != 1:
        return False
    for i, letter in enumerate(longer):
        if longer[:i] + longer[i + 1 :] == shorter:
            return letter.isalpha()
    return False
