"""Quickly find which arrangements of a Parsons problem's lines run at all.

validate_content.py starts this file in a fresh Python process, once per
Parsons item, in an empty temporary folder:

    python -I tools/parsons_screen.py

It reads JSON from standard input, {"authored": program, "programs": [...]},
runs every program the way the Run button does (the harness's execute), and
prints one line of JSON:

    {"finished": [0, 7], "carried_over": false}

"finished" lists the programs, by position, that ran to the end without an
error.

Why this file exists: an item of 7 lines has 5,040 orders, and starting a new
Python process for each would take minutes. Nearly all of them crash on their
first or second line, so they are weeded out here, thousands a second, in one
process.

Why its answer is only a first pass: programs that share a process can affect
each other. One program switches something on (memory tracing, say) and the
next finds it already on, so it may print something it wouldn't print in a
process of its own. So this file never compares output. It only says which
programs finished, and the validator runs each of those again in a process of
its own before it believes anything. Files a program writes are deleted
before the next one runs. As a last check the author's order is run once more
at the end: if it no longer finishes, something was carried over from one
program to the next ("carried_over"), and the validator then runs every
program in a process of its own instead.
"""

from __future__ import annotations

import io
import json
import shutil
import sys
from pathlib import Path
from types import FrameType
from typing import Any

HARNESS = Path(__file__).resolve().parents[1] / "harness"
# The same two places the harness's own cli.py lets a program import from.
sys.path[:0] = [str(HARNESS), "."]

from checks import SOLUTION_FILE, execute  # noqa: E402


class TooManySteps(BaseException):
    """Raised inside a program that runs far longer than the author's order
    does: a loop that never ends. A BaseException, so that the program's own
    ``except Exception`` can't swallow it. (A bare ``except:`` still could.
    Then the program would run on, and the validator's time limit for this
    whole file would stop it and report the item.)"""


def finishes(program: str, step_limit: int | None = None) -> tuple[bool, int]:
    """Run one program. Returns whether it ran to the end without an error,
    and how many lines it ran.

    Lines are counted with Python's tracing hook, and only the program's own
    lines count: the libraries it imports run uncounted, at full speed.
    """
    steps = 0

    def count_line(frame: FrameType, event: str, arg: object) -> Any:
        nonlocal steps
        if event == "line":
            steps += 1
            if step_limit is not None and steps > step_limit:
                raise TooManySteps
        return count_line

    def on_call(frame: FrameType, event: str, arg: object) -> Any:
        # Python asks this once per function call: count its lines or not?
        is_the_program = frame.f_code.co_filename == SOLUTION_FILE
        return count_line if is_the_program else None

    sys.settrace(on_call)
    try:
        execute("", io.StringIO(), echo_input=True, wait_for_input=True, source=program)
    except BaseException:
        # Any error, a loop that never ends, or a program that asks for input.
        return False, steps
    finally:
        sys.settrace(None)
    return True, steps


def empty_the_folder() -> None:
    """Delete whatever the last program wrote, so the next one starts clean."""
    for entry in Path.cwd().iterdir():
        if entry.is_dir():
            shutil.rmtree(entry, ignore_errors=True)
        else:
            entry.unlink(missing_ok=True)


def main() -> None:
    job = json.load(sys.stdin)
    authored_steps = finishes(job["authored"])[1]
    empty_the_folder()
    # Another order of the same lines does about the same amount of work, so
    # one that runs ten times as many lines is stuck in a loop.
    step_limit = authored_steps * 10 + 1000

    finished: list[int] = []
    for position, program in enumerate(job["programs"]):
        if finishes(program, step_limit)[0]:
            finished.append(position)
        empty_the_folder()

    carried_over = not finishes(job["authored"])[0]
    # Everything the programs printed was captured, so this line is the only
    # output.
    print(json.dumps({"finished": finished, "carried_over": carried_over}))


if __name__ == "__main__":
    main()
