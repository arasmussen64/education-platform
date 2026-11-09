from pathlib import Path

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7). Each test checks one part of the
# program, so a failure points at the skill behind it (test_skills in
# exercise.yaml, ADR-0012).


def count_asserts():
    source = Path("solution.py").read_text(encoding="utf-8")
    return sum(1 for line in source.splitlines() if line.strip().startswith("assert "))


def test_hours_started():
    """hours_started: 0 for 0 minutes, 1 for 1 and 60, 2 for 61 and 120, 3 for 121."""
    hours_started = function("hours_started")
    for minutes, expected in [(0, 0), (1, 1), (60, 1), (61, 2), (120, 2), (121, 3)]:
        assert hours_started(minutes) == expected, minutes


def test_fee():
    """fee: 0.00 for 0 minutes, 2.00 up to an hour, 1.50 per started hour after, 12.00 at most."""
    fee = function("fee")
    cases = [
        (0, 0.0),
        (1, 2.0),
        (30, 2.0),
        (60, 2.0),
        (61, 3.5),
        (120, 3.5),
        (121, 5.0),
        (420, 11.0),
        (421, 12.0),
        (600, 12.0),
        (1440, 12.0),
    ]
    for minutes, expected in cases:
        assert fee(minutes) == expected, minutes


def test_report_lines():
    """report_lines gives a line per stay with two decimals, then the total; [] gives just Total: 0.00."""
    report_lines = function("report_lines")
    assert report_lines([30, 90]) == ["30 min: 2.00", "90 min: 3.50", "Total: 5.50"]
    assert report_lines([0]) == ["0 min: 0.00", "Total: 0.00"]
    assert report_lines([]) == ["Total: 0.00"]


def test_leaves_data_alone():
    """report_lines leaves the list of stays unchanged."""
    stays = [30, 90, 61]
    function("report_lines")(stays)
    assert stays == [30, 90, 61]


def test_docstrings():
    """Every function has a docstring."""
    for name in ("hours_started", "fee", "report_lines", "main"):
        assert (function(name).__doc__ or "").strip() != "", name


def test_tests():
    """test_parking has 4 or more asserts, passes, and fails when fee always says 2.00."""
    assert count_asserts() >= 4
    test = function("test_parking")
    test()
    import solution

    original = solution.fee
    solution.fee = lambda minutes: 2.0
    caught = False
    try:
        test()
    except AssertionError:
        caught = True
    finally:
        solution.fee = original
    assert caught


def test_program():
    """Run directly, the file prints the tests' message and the report."""
    assert run() == (
        "parking: all checks passed\n"
        "30 min: 2.00\n90 min: 3.50\n61 min: 3.50\n600 min: 12.00\n0 min: 0.00\n"
        "Total: 21.00\n"
    )
