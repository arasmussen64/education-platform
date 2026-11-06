"""Unit tests for checks.run(), the helper exercise tests use."""

import builtins
import io
import sys
from pathlib import Path

import checks
import pytest


@pytest.fixture
def solution(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Returns a function that writes solution.py into an empty working folder."""
    monkeypatch.chdir(tmp_path)

    def write(source: str) -> None:
        (tmp_path / checks.SOLUTION_FILE).write_text(source, encoding="utf-8")

    return write


def test_returns_printed_output_without_prompts(solution) -> None:
    solution('name = input("Name? ")\nprint("Hi", name)\n')
    assert checks.run("Ada\n") == "Hi Ada\n"


def test_feeds_input_one_line_per_call(solution) -> None:
    solution("a = int(input())\nb = int(input())\nprint(a + b)\n")
    assert checks.run("2\n3\n") == "5\n"


def test_raises_eof_when_input_runs_out(solution) -> None:
    solution("input()\ninput()\n")
    with pytest.raises(EOFError, match="more input than it was given"):
        checks.run("only one line\n")


def test_can_stop_and_wait_instead_of_failing(solution) -> None:
    solution('input("Name? ")\n')
    output = io.StringIO()
    with pytest.raises(checks.InputNeeded):
        checks.execute("", output, echo_input=True, wait_for_input=True)
    assert output.getvalue() == "Name? "


def test_waiting_is_not_an_ordinary_exception() -> None:
    # Otherwise a learner's `except Exception:` around input() would hide it.
    assert not issubclass(checks.InputNeeded, Exception)


def test_restores_input_and_stdin_after_a_crash(solution) -> None:
    real_input, real_stdin = builtins.input, sys.stdin
    solution("raise ValueError('boom')\n")
    with pytest.raises(ValueError):
        checks.run()
    assert builtins.input is real_input
    assert sys.stdin is real_stdin


def test_sys_exit_ends_the_program_quietly(solution) -> None:
    solution("import sys\nprint('a')\nsys.exit(1)\nprint('b')\n")
    assert checks.run() == "a\n"


def test_each_run_starts_fresh(solution) -> None:
    solution("try:\n    count += 1\nexcept NameError:\n    count = 1\nprint(count)\n")
    assert checks.run() == "1\n"
    assert checks.run() == "1\n"


def test_run_with_changes_starting_values(solution) -> None:
    solution("x = 3\ny = 5\nx, y = y, x\nprint(x, y)\n")
    assert checks.run_with({"x": "left", "y": "right"}) == "right left\n"


def test_run_with_changes_only_the_first_assignment(solution) -> None:
    solution("x = 1\nx = x + 1\nprint(x)\n")
    assert checks.run_with({"x": 10}) == "11\n"


def test_run_with_leaves_longer_names_alone(solution) -> None:
    solution("xs = 1\nx = 2\nprint(xs, x)\n")
    assert checks.run_with({"x": 7}) == "1 7\n"


def test_run_with_says_when_a_starting_line_is_missing(solution) -> None:
    solution("print(1)\n")
    with pytest.raises(AssertionError, match="Keep the line that gives x"):
        checks.run_with({"x": 3})
