"""The other ways to arrange a Parsons problem's lines (ADR-0016).

The app marks a Parsons answer right only when the learner's lines are exactly
the author's lines in the author's order. So if some other arrangement also
runs and prints the same output, a learner who builds it has a working program
and is told it's wrong.

This file lists the arrangements worth trying and says each one in plain
words. It runs nothing: validate_content.py runs them (check_parsons_orders).

Two kinds of arrangement are listed:

- another order of the real lines, with the decoys left out;
- the author's order with a decoy in place of one real line.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass

# Up to this many lines, every order is tried: 7 lines have 5,040 orders, and
# 8 would have 40,320. Longer programs get the orders a learner is most likely
# to build instead: two lines swapped, or a run of lines moved somewhere else.
EVERY_ORDER_UP_TO = 7


@dataclass(frozen=True)
class Arrangement:
    """One program a learner could build, and how it differs from the author's."""

    lines: tuple[str, ...]
    # For the validator's message, like "lines 2 and 3 can swap places".
    description: str
    uses_decoy: bool = False

    @property
    def program(self) -> str:
        return "\n".join(self.lines) + "\n"


def quoted(line: str) -> str:
    """A line as the message shows it: without its indentation, in quotes."""
    return repr(line.strip())


def swaps(lines: list[str]) -> dict[tuple[int, ...], str]:
    """Every order made by swapping two lines, with its description."""
    found: dict[tuple[int, ...], str] = {}
    for i, j in itertools.combinations(range(len(lines)), 2):
        order = list(range(len(lines)))
        order[i], order[j] = order[j], order[i]
        found[tuple(order)] = (
            f"lines {i + 1} and {j + 1} can swap places "
            f"({quoted(lines[i])} and {quoted(lines[j])})"
        )
    return found


def block_moves(lines: list[str]) -> dict[tuple[int, ...], str]:
    """Every order made by lifting out a run of lines and putting it back
    somewhere else, with its description. Short runs come first, so an order
    that can be reached two ways is described the simpler way."""
    found: dict[tuple[int, ...], str] = {}
    count = len(lines)
    unmoved = tuple(range(count))
    for length in range(1, count):
        for start in range(count - length + 1):
            block = unmoved[start : start + length]
            rest = unmoved[:start] + unmoved[start + length :]
            for gap in range(len(rest) + 1):
                order = rest[:gap] + block + rest[gap:]
                if order == unmoved or order in found:
                    continue
                if length == 1:
                    what = f"line {start + 1} ({quoted(lines[start])})"
                else:
                    what = f"lines {start + 1} to {start + length}"
                where = f"before line {rest[gap] + 1}" if gap < len(rest) else "last"
                found[order] = f"{what} can go {where}"
    return found


def other_orders(lines: list[str]) -> list[Arrangement]:
    """The other orders of the real lines to try, the simplest changes first."""
    described = swaps(lines)
    for order, description in block_moves(lines).items():
        described.setdefault(order, description)
    if len(lines) <= EVERY_ORDER_UP_TO:
        for order in itertools.permutations(range(len(lines))):
            if order != tuple(range(len(lines))):
                numbers = ", ".join(str(index + 1) for index in order)
                described.setdefault(order, f"the lines can go in the order {numbers}")
    return [
        Arrangement(tuple(lines[index] for index in order), description)
        for order, description in described.items()
    ]


def decoy_swaps(lines: list[str], decoys: list[str]) -> list[Arrangement]:
    """The author's order with one decoy in place of one real line."""
    found: list[Arrangement] = []
    for decoy in decoys:
        for index, line in enumerate(lines):
            changed = (*lines[:index], decoy, *lines[index + 1 :])
            description = (
                f"the decoy {quoted(decoy)} can take the place of line "
                f"{index + 1} ({quoted(line)})"
            )
            found.append(Arrangement(changed, description, uses_decoy=True))
    return found


def arrangements(lines: list[str], decoys: list[str]) -> list[Arrangement]:
    """Everything to try for one Parsons item."""
    return [*other_orders(lines), *decoy_swaps(lines, decoys)]
