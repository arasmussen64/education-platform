from pathlib import Path

from checks import function, run

REPORT = "north: 150.50\nsouth: 80.00\neast: 45.25\nRows: 6\nBad rows: 2\nTotal: 275.75\n"


def test_report_and_file():
    """report_lines formats money with two decimals and counts bad rows; write_report keeps every line."""
    rows = [{"region": "a", "amount": "1"}, {"region": "a", "amount": "bad"}]
    got = function("report_lines")(rows)
    assert got == ["a: 1.00", "Rows: 2", "Bad rows: 1", "Total: 1.00"], f"report_lines returned {got!r}"
    function("write_report")("sr.txt", ["one", "two"])
    function("write_report")("sr.txt", ["three", "four"])
    saved = Path("sr.txt").read_text(encoding="utf-8")
    assert saved == "three\nfour\n", f"after two calls the file contains {saved!r}"


def test_program():
    """Running the program prints the tests' message and the report, and report.txt holds the report."""
    got = run()
    assert got == "report: all checks passed\n" + REPORT, f"Your program printed:\n{got}"
    saved = Path("report.txt").read_text(encoding="utf-8")
    assert saved == REPORT, f"report.txt contains:\n{saved}"
