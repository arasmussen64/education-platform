"""Run the learner's program for the Run button and report what happened."""

from __future__ import annotations

import io
from typing import TypedDict

from checks import execute
from errors import learner_traceback


class ProgramResult(TypedDict):
    output: str
    error: str | None


def run_program(stdin: str = "") -> ProgramResult:
    """Run solution.py the way a terminal would.

    Prompts and the input typed after them appear in the output. If the
    program crashes, ``error`` holds the traceback, trimmed to the learner's
    file, and ``output`` holds whatever was printed before the crash.
    """
    output = io.StringIO()
    try:
        execute(stdin, output, echo_input=True)
    except Exception as exc:
        return {"output": output.getvalue(), "error": learner_traceback(exc)}
    return {"output": output.getvalue(), "error": None}
