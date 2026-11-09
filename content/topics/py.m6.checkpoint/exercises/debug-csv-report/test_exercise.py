from pathlib import Path

from checks import function, run

REPORT = "north: 150.50\nsouth: 80.00\nRows: 4\nBad rows: 1\nTotal: 230.50\n"


def test_amount_of():
    """amount_of gives 12.5 for "12.5", and None, not a crash, for "abc" and for a blank."""
    amount_of = function("amount_of")
    assert amount_of({"amount": "12.5"}) == 12.5, 'amount_of should give 12.5 for "12.5"'
    for text in ("abc", ""):
        try:
            got = amount_of({"amount": text})
        except ValueError:
            raise AssertionError(f"amount_of crashed on {text!r} instead of returning None")
        assert got is None, f"amount_of returned {got!r} for {text!r}, not None"


def test_totals():
    """totals_by_region adds up a region's amounts: 1 and 2 for region a give 3.0."""
    rows = [
        {"region": "a", "amount": "1"},
        {"region": "a", "amount": "2"},
        {"region": "b", "amount": "x"},
    ]
    got = function("totals_by_region")(rows)
    assert got == {"a": 3.0}, f"totals_by_region returned {got!r}, not {{'a': 3.0}}"


def test_write_report():
    """write_report leaves every line in the file, not just the last."""
    function("write_report")("wr.txt", ["one", "two", "three"])
    got = Path("wr.txt").read_text(encoding="utf-8")
    assert got == "one\ntwo\nthree\n", f"the file contains {got!r}"


def test_program():
    """Prints the five report lines and writes them to report.txt."""
    got = run()
    assert got == REPORT, f"Your program printed:\n{got}"
    saved = Path("report.txt").read_text(encoding="utf-8")
    assert saved == REPORT, f"report.txt contains:\n{saved}"
