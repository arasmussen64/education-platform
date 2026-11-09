"""Find an exercise's tests, run them, and report the results as plain data.

Tests live in test_exercise.py. They are plain functions whose names start
with ``test_`` and that use ``assert``. The first line of a test's docstring
is the description the learner sees.
"""

from __future__ import annotations

import importlib
import inspect
import io
import sys
import traceback
from contextlib import redirect_stdout
from pathlib import Path
from types import FunctionType, ModuleType
from typing import Literal, TypedDict

from checks import SOLUTION_FILE
from errors import deepest_file, describe_error

TEST_MODULE = "test_exercise"
TEST_FILE = f"{TEST_MODULE}.py"

# Files are rewritten between runs, so never reuse cached bytecode.
sys.dont_write_bytecode = True

Outcome = Literal["pass", "fail", "error"]


class TestResult(TypedDict):
    name: str
    description: str
    outcome: Outcome
    message: str


class Report(TypedDict):
    status: Literal["ok", "error"]
    message: str
    passed: int
    total: int
    results: list[TestResult]


def run_tests() -> Report:
    """Run every test in test_exercise.py, in the order they're written."""
    _forget_learner_modules()
    try:
        # Loading the tests loads the learner's code too, if the tests import
        # it at the top; anything it prints then isn't part of the report.
        with redirect_stdout(io.StringIO()):
            module = importlib.import_module(TEST_MODULE)
    except Exception as exc:
        if deepest_file(exc) == TEST_FILE:
            message = (
                "The tests couldn't be loaded. This is a problem with the exercise."
            )
        else:
            message = "Your code couldn't be loaded."
        return {
            "status": "error",
            "message": f"{message} {describe_error(exc)}",
            "passed": 0,
            "total": 0,
            "results": [],
        }

    results = [_run_one(test) for test in _find_tests(module)]
    passed = sum(1 for result in results if result["outcome"] == "pass")
    return {
        "status": "ok",
        "message": "",
        "passed": passed,
        "total": len(results),
        "results": results,
    }


def _forget_learner_modules() -> None:
    """Make the next import read solution.py and the tests from disk again."""
    for name in ("solution", TEST_MODULE):
        sys.modules.pop(name, None)
    importlib.invalidate_caches()


def _find_tests(module: ModuleType) -> list[FunctionType]:
    return [
        value
        for name, value in vars(module).items()
        if name.startswith("test_")
        and isinstance(value, FunctionType)
        and value.__module__ == module.__name__
    ]


def _description(test: FunctionType) -> str:
    doc = inspect.getdoc(test)
    return doc.splitlines()[0] if doc else test.__name__


def _run_one(test: FunctionType) -> TestResult:
    outcome: Outcome
    try:
        # A test may call a function that prints; the Check button shows
        # the results, not that output, and the CLI needs a clean report.
        with redirect_stdout(io.StringIO()):
            test()
    except AssertionError as exc:
        if deepest_file(exc) == SOLUTION_FILE:
            # An assert in the learner's own code failed: that's their error.
            outcome, message = "error", describe_error(exc)
        else:
            outcome, message = "fail", _assertion_message(exc)
    except Exception as exc:
        outcome, message = "error", describe_error(exc)
    else:
        outcome, message = "pass", ""
    return {
        "name": test.__name__,
        "description": _description(test),
        "outcome": outcome,
        "message": message,
    }


def _assertion_message(exc: AssertionError) -> str:
    """The test's own message, or else the failing assert line."""
    if str(exc):
        return str(exc)
    for frame in reversed(traceback.extract_tb(exc.__traceback__)):
        if Path(frame.filename).name == TEST_FILE and frame.line:
            return f"Check failed: {frame.line}"
    return "Check failed."
