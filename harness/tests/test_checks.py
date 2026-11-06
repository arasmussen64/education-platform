"""Unit tests for checks.run(), the helper exercise tests use."""

import builtins
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
