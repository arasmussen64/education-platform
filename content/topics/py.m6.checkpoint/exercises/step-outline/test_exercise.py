from pathlib import Path

from checks import function, run

REPORT = "north: 150.50\nsouth: 80.00\neast: 45.25\nRows: 6\nBad rows: 2\nTotal: 275.75\n"


def test_program():
    """Running the program prints the tests' message and the report, and report.txt holds the report."""
    got = run()
    assert got == "report: all checks passed\n" + REPORT, f"Your program printed:\n{got}"
    saved = Path("report.txt").read_text(encoding="utf-8")
    assert saved == REPORT, f"report.txt contains:\n{saved}"


def test_functions():
    """The pieces work on other data too: a bad row gives None, totals add up, the rows stay unchanged."""
    rows = [
        {"date": "d", "region": "a", "amount": "1"},
        {"date": "d", "region": "a", "amount": "nope"},
        {"date": "d", "region": "a", "amount": "2"},
    ]
    assert function("amount_of")(rows[1]) is None, "amount_of should give None for nope"
    got = function("totals_by_region")(rows)
    assert got == {"a": 3.0}, f"totals_by_region returned {got!r}"
    got = function("report_lines")(rows)
    assert got == ["a: 3.00", "Rows: 3", "Bad rows: 1", "Total: 3.00"], f"report_lines returned {got!r}"
    assert rows[1] == {"date": "d", "region": "a", "amount": "nope"} and len(rows) == 3, (
        "the rows list should be unchanged"
    )


def test_docstrings():
    """Every function has a docstring."""
    for name in ("read_rows", "amount_of", "good_rows", "totals_by_region", "report_lines", "write_report", "main"):
        assert (function(name).__doc__ or "").strip() != "", f"{name} needs a docstring"
