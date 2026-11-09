from pathlib import Path

from checks import function, run


def test_program():
    """Run directly, the tests pass, the report prints and attendance.txt holds it."""
    assert run() == (
        "attendance: all checks passed\nmath: 52\nart: 18\nRows: 4\nBad rows: 1\nTotal: 70\n"
    )
    assert Path("attendance.txt").read_text(encoding="utf-8") == (
        "math: 52\nart: 18\nRows: 4\nBad rows: 1\nTotal: 70\n"
    )


def test_pieces():
    """present_in gives None for bad values, and report_lines leaves the rows unchanged."""
    present_in = function("present_in")
    assert present_in({"present": "x"}) is None
    assert present_in({"present": ""}) is None
    assert present_in({"present": "7"}) == 7
    rows = [{"date": "d", "class": "art", "present": "3"}]
    function("report_lines")(rows)
    assert rows == [{"date": "d", "class": "art", "present": "3"}]
