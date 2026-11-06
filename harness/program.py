"""Run the learner's program for the Run button and report what happened."""

from __future__ import annotations

import io
import random
from typing import TypedDict

from checks import InputNeeded, execute
from errors import learner_traceback


class ProgramResult(TypedDict):
    output: str
    error: str | None
    waiting_for_input: bool


def run_program(stdin: str = "", seed: int | None = None) -> ProgramResult:
    """Run solution.py the way a terminal would.

    Prompts and the input typed after them appear in the output.

    When the program asks for more input than ``stdin`` holds, it stops there
    and ``waiting_for_input`` is true. The app then asks the learner for the
    next line and runs the program again from the start with it. Passing the
    same ``seed`` every time makes the random module repeat its choices, so
    each re-run behaves the same way up to the new input.

    If the program crashes, ``error`` holds the traceback, trimmed to the
    learner's file, and ``output`` holds whatever was printed before.
    """
    if seed is not None:
        random.seed(seed)
    output = io.StringIO()
    try:
        execute(stdin, output, echo_input=True, wait_for_input=True)
    except InputNeeded:
        return {"output": output.getvalue(), "error": None, "waiting_for_input": True}
    except Exception as exc:
        return {
            "output": output.getvalue(),
            "error": learner_traceback(exc),
            "waiting_for_input": False,
        }
    return {"output": output.getvalue(), "error": None, "waiting_for_input": False}
