"""The Step through button (ADR-0022): run the learner's program under
Python's tracing hook and record what each line did, so the app can play it
back one step at a time, like Python Tutor.

Runs in the browser (Pyodide) and in CI (CPython), and must behave the same
in both: harness/scenarios has trace scenarios both runtimes must match.
"""

from __future__ import annotations

import io
import random
import sys
import types
from typing import Any, TypedDict

from checks import SOLUTION_FILE, InputNeeded, execute
from errors import learner_traceback

# Enough to follow a short program through a loop or two. Past this, the
# program keeps running without being recorded, up to the usual time limit.
MAX_STEPS = 300
# Long values are cut short: the point is to see what changed, not every item.
MAX_VALUE_CHARS = 60


class Frame(TypedDict):
    """One function call that's running (the program itself is the first)."""

    name: str
    line: int
    # Name and value (shown as text), in the order the names were made.
    vars: list[list[str]]
    # The value being returned, on a return step.
    returns: str | None


class Step(TypedDict):
    # Which line the step is about.
    line: int
    # "line": about to run the line. "call": a function was just called.
    # "return": it's returning. "exception": an error was raised here.
    event: str
    # The calls that are running, the program first, the innermost last.
    frames: list[Frame]
    # How much of `output` had been printed by then.
    out_len: int


class TraceResult(TypedDict):
    steps: list[Step]
    output: str
    error: str | None
    waiting_for_input: bool
    # True when the recording stopped at MAX_STEPS.
    truncated: bool


class StepLimit(BaseException):
    """Raised inside the program once enough steps are recorded, to stop it.

    A BaseException, so a learner's ``except Exception`` can't swallow it.
    """


def show(value: object) -> str:
    """A value as text, short, and friendlier than repr for a few kinds."""
    if isinstance(value, types.FunctionType):
        return f"function {value.__name__}"
    if isinstance(value, type):
        return f"class {value.__name__}"
    if isinstance(value, types.ModuleType):
        return f"module {value.__name__}"
    try:
        text = repr(value)
    except Exception:
        return "<a value that can't be shown>"
    if len(text) > MAX_VALUE_CHARS:
        text = text[:MAX_VALUE_CHARS] + "…"
    return text


def _is_learner_frame(frame: types.FrameType) -> bool:
    return frame.f_code.co_filename == SOLUTION_FILE


def _snapshot(
    frame: types.FrameType, returns: object = None, returning: bool = False
) -> Frame:
    names = [
        name
        for name, value in frame.f_locals.items()
        if not name.startswith("__") and not isinstance(value, types.ModuleType)
    ]
    return {
        "name": "program"
        if frame.f_code.co_name == "<module>"
        else frame.f_code.co_name,
        "line": frame.f_lineno,
        "vars": [[name, show(frame.f_locals[name])] for name in names],
        "returns": show(returns) if returning else None,
    }


def trace_program(
    stdin: str = "", seed: int | None = None, max_steps: int = MAX_STEPS
) -> TraceResult:
    """Run solution.py like the Run button does, recording a step for each
    line about to run, each call, each return and each error, with every
    running call's variables at that moment.

    Input, random seeds and errors work exactly as in ``program.run_program``:
    a program that wants more input than ``stdin`` holds stops with
    ``waiting_for_input`` true, and a crash leaves its traceback in ``error``.
    """
    if seed is not None:
        random.seed(seed)
    output = io.StringIO()
    steps: list[Step] = []
    truncated = False

    def stack(
        frame: types.FrameType, returns: object = None, returning: bool = False
    ) -> list[Frame]:
        frames: list[Frame] = []
        current: types.FrameType | None = frame
        innermost = True
        while current is not None:
            if _is_learner_frame(current):
                frames.append(_snapshot(current, returns, returning and innermost))
                innermost = False
            current = current.f_back
        frames.reverse()
        return frames

    def record(frame: types.FrameType, event: str, arg: object) -> None:
        nonlocal truncated
        if len(steps) >= max_steps:
            truncated = True
            raise StepLimit
        returning = event == "return"
        steps.append(
            {
                "line": frame.f_lineno,
                "event": event,
                "frames": stack(frame, arg, returning),
                "out_len": len(output.getvalue()),
            }
        )

    def tracer(frame: types.FrameType, event: str, arg: object) -> Any:
        if not _is_learner_frame(frame):
            return None
        # The program itself starting isn't a call the learner made.
        if event == "call" and frame.f_code.co_name == "<module>":
            return tracer
        # An exception step shows where the error was raised; a return step
        # right after an exception is the frame unwinding, which is noise.
        if event == "exception":
            record(frame, "exception", arg)
            return tracer
        if event == "return" and steps and steps[-1]["event"] == "exception":
            return tracer
        record(frame, event, arg)
        return tracer

    error: str | None = None
    waiting = False
    saved = sys.gettrace()
    sys.settrace(tracer)
    try:
        execute(stdin, output, echo_input=True, wait_for_input=True)
    except InputNeeded:
        waiting = True
    except StepLimit:
        pass
    except Exception as exc:
        error = learner_traceback(exc)
    finally:
        sys.settrace(saved)

    if waiting and steps and steps[-1]["event"] == "exception":
        # The stop for input isn't an error the learner made: drop it.
        steps.pop()
    return {
        "steps": steps,
        "output": output.getvalue(),
        "error": error,
        "waiting_for_input": waiting,
        "truncated": truncated,
    }
