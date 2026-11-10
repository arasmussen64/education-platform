"""Unit tests for tracer.trace_program(), behind the Step through button."""

from pathlib import Path

import checks
import pytest
import tracer


@pytest.fixture
def solution(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Returns a function that writes solution.py into an empty working folder."""
    monkeypatch.chdir(tmp_path)

    def write(source: str) -> None:
        (tmp_path / checks.SOLUTION_FILE).write_text(source, encoding="utf-8")

    return write


def events(result: tracer.TraceResult) -> list[tuple[str, int]]:
    return [(step["event"], step["line"]) for step in result["steps"]]


def test_records_each_line_before_it_runs_with_the_variables_so_far(solution) -> None:
    solution("x = 1\ny = x + 1\nprint(x, y)\n")
    result = tracer.trace_program()
    assert events(result) == [("line", 1), ("line", 2), ("line", 3), ("return", 3)]
    first, second, third, last = result["steps"]
    assert first["frames"] == [
        {"name": "program", "line": 1, "vars": [], "returns": None}
    ]
    assert second["frames"][0]["vars"] == [["x", "1"]]
    assert third["frames"][0]["vars"] == [["x", "1"], ["y", "2"]]
    # Output is recorded as it grows: nothing yet at line 3, everything after.
    assert third["out_len"] == 0
    assert last["out_len"] == len("1 2\n")
    assert result["output"] == "1 2\n"
    assert result["error"] is None
    assert result["truncated"] is False


def test_shows_each_call_as_its_own_frame(solution) -> None:
    solution("def double(n):\n    return n * 2\n\nresult = double(4)\n")
    result = tracer.trace_program()
    assert events(result) == [
        ("line", 1),
        ("line", 4),
        ("call", 1),
        ("line", 2),
        ("return", 2),
        ("return", 4),
    ]
    call = result["steps"][2]
    assert [frame["name"] for frame in call["frames"]] == ["program", "double"]
    assert call["frames"][1]["vars"] == [["n", "4"]]
    returning = result["steps"][4]
    assert returning["frames"][1]["returns"] == "8"
    # Back in the program, the function shows as a function, not a repr.
    assert result["steps"][5]["frames"][0]["vars"] == [
        ["double", "function double"],
        ["result", "8"],
    ]


def test_stops_where_an_error_happens(solution) -> None:
    solution("print('before')\ntotal = 10 / 0\nprint('after')\n")
    result = tracer.trace_program()
    assert events(result)[-1] == ("exception", 2)
    assert result["output"] == "before\n"
    assert result["error"] is not None
    assert "ZeroDivisionError" in result["error"]


def test_stops_and_waits_when_the_program_wants_input(solution) -> None:
    solution('name = input("Name? ")\nprint("Hi", name)\n')
    waiting = tracer.trace_program()
    assert waiting["waiting_for_input"] is True
    assert waiting["output"] == "Name? "
    assert events(waiting) == [("line", 1)]
    done = tracer.trace_program("Ada\n")
    assert done["waiting_for_input"] is False
    assert done["output"] == "Name? Ada\nHi Ada\n"
    assert done["steps"][1]["frames"][0]["vars"] == [["name", "'Ada'"]]


def test_stops_recording_after_the_step_limit(solution) -> None:
    solution("i = 0\nwhile True:\n    i = i + 1\n")
    result = tracer.trace_program(max_steps=20)
    assert len(result["steps"]) == 20
    assert result["truncated"] is True
    assert result["error"] is None


def test_shortens_long_values_and_names_kinds(solution) -> None:
    solution(
        "import math\nitems = list(range(100))\nclass Pet: pass\nprint(len(items))\n"
    )
    result = tracer.trace_program()
    final = result["steps"][-1]["frames"][0]["vars"]
    names = [name for name, _ in final]
    # Modules aren't shown; classes are named, not repr'd.
    assert "math" not in names
    assert ["Pet", "class Pet"] in final
    items = dict(final)["items"]
    assert items.endswith("…")
    assert len(items) == tracer.MAX_VALUE_CHARS + 1


def test_repeats_random_choices_with_a_seed(solution) -> None:
    solution("import random\nn = random.randint(1, 1000)\n")
    first = tracer.trace_program(seed=7)
    second = tracer.trace_program(seed=7)
    assert (
        first["steps"][-1]["frames"][0]["vars"]
        == second["steps"][-1]["frames"][0]["vars"]
    )
