"""Tools that exercise tests use to run the learner's code.

This file runs in two places and must behave the same in both:

- in the browser, inside Pyodide, when a learner presses Run or Check;
- on GitHub, under CPython, when exercises are validated.

The learner's code is always in a file named solution.py in the current
working directory. Tests either import functions from it
(``from solution import rotate``) or run it as a whole program with run().
"""

from __future__ import annotations

import builtins
import importlib
import io
import re
import sys
from collections.abc import Callable
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any

SOLUTION_FILE = "solution.py"

NOT_ENOUGH_INPUT = "The program asked for more input than it was given."


class InputNeeded(BaseException):
    """The program (in Run mode) wants input it hasn't been given yet.

    It's a BaseException, like SystemExit, so a learner's ``except Exception``
    around input() can't accidentally swallow it.
    """


def run(stdin: str = "") -> str:
    """Run the learner's program as a script and return everything it printed.

    ``stdin`` is what the program receives from input(), one line per call.
    Prompts passed to input() are left out of the result, so a test doesn't
    break because a prompt is worded differently.

    If the program asks for more input than ``stdin`` holds, it gets an
    EOFError, just as a real program reading from an empty input would.
    """
    output = io.StringIO()
    execute(stdin, output, echo_input=False)
    return output.getvalue()


ASKED_FOR_INPUT = (
    "Your program asked for input while its functions were being loaded. "
    "Put the input() calls inside main(), and call main() only under "
    'if __name__ == "__main__":'
)


def function(name: str) -> Callable[..., Any]:
    """The function called ``name`` in the learner's solution.py.

    Loading the file runs its top-level code, so anything it prints there is
    swallowed, and a program that asks for input at that point fails with a
    plain message instead of hanging or crashing. A missing function fails
    the test with "Define a function called ...", which a hidden test can
    show, rather than crashing on an import.
    """
    sys.modules.pop("solution", None)
    importlib.invalidate_caches()
    try:
        with redirect_stdout(io.StringIO()):
            module = importlib.import_module("solution")
    except EOFError:
        raise AssertionError(ASKED_FOR_INPUT) from None
    found = getattr(module, name, None)
    if not callable(found):
        raise AssertionError(f"Define a function called {name}.")
    return found


def printed(call: Callable[..., Any], *args: Any) -> str:
    """Everything ``call(*args)`` prints, for testing a function that prints."""
    output = io.StringIO()
    with redirect_stdout(output):
        call(*args)
    return output.getvalue()


def run_with(starting_values: dict[str, object], stdin: str = "") -> str:
    """Run the learner's program as if some names started with other values.

    Each name's first assignment, like ``x = 3``, is replaced with the value
    given here, and the program runs as run() would. Tests use it to check that
    code really works with its names: that a swap swaps any two values, say,
    not just the two it was written with.

    If a name's starting line is missing, the check fails and says so.
    """
    source = Path(SOLUTION_FILE).read_text(encoding="utf-8")
    for name, value in starting_values.items():
        source, found = re.subn(
            rf"^{re.escape(name)}[ \t]*=(?!=).*$",
            f"{name} = {value!r}",
            source,
            count=1,
            flags=re.MULTILINE,
        )
        if not found:
            raise AssertionError(f"Keep the line that gives {name} its starting value.")
    output = io.StringIO()
    execute(stdin, output, echo_input=False, source=source)
    return output.getvalue()


def execute(
    stdin: str,
    output: io.StringIO,
    *,
    echo_input: bool,
    wait_for_input: bool = False,
    source: str | None = None,
) -> None:
    """Run solution.py with ``stdin`` as its input, printing into ``output``.

    With ``echo_input``, prompts and the input typed after them are written to
    ``output`` too, so it reads like a terminal session (the Run button).

    When the program asks for more input than ``stdin`` holds, it gets an
    EOFError, or, with ``wait_for_input``, the run stops with InputNeeded so
    the app can ask the learner.

    Exceptions raised by the learner's code are passed on to the caller.
    sys.exit() simply ends the program early.
    """
    if source is None:
        source = Path(SOLUTION_FILE).read_text(encoding="utf-8")
    code = compile(source, SOLUTION_FILE, "exec")
    stdin_stream = io.StringIO(stdin)

    def fake_input(prompt: object = "") -> str:
        if echo_input:
            output.write(str(prompt))
        line = stdin_stream.readline()
        if not line:
            if wait_for_input:
                raise InputNeeded
            raise EOFError(NOT_ENOUGH_INPUT)
        text = line.removesuffix("\n")
        if echo_input:
            output.write(text + "\n")
        return text

    namespace = {"__name__": "__main__", "__file__": SOLUTION_FILE}
    saved_input, saved_stdin = builtins.input, sys.stdin
    builtins.input = fake_input
    sys.stdin = stdin_stream
    try:
        with redirect_stdout(output):
            exec(code, namespace)
    except SystemExit:
        pass
    finally:
        builtins.input = saved_input
        sys.stdin = saved_stdin
