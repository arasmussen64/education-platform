from pathlib import Path

from checks import function, run

REPORT = "north: 150.50\nsouth: 80.00\neast: 45.25\nRows: 6\nBad rows: 2\nTotal: 275.75\n"


def test_read_and_clean():
    """read_rows gives dictionaries, amount_of gives None for abc and a blank, good_rows keeps the rest."""
    Path("rc.csv").write_text("date,region,amount\nd,a,1.5\nd,b,abc\nd,a,\n", encoding="utf-8")
    rows = function("read_rows")("rc.csv")
    assert rows == [
        {"date": "d", "region": "a", "amount": "1.5"},
        {"date": "d", "region": "b", "amount": "abc"},
        {"date": "d", "region": "a", "amount": ""},
    ], f"read_rows returned {rows!r}"
    amount_of = function("amount_of")
    assert amount_of(rows[0]) == 1.5, f"amount_of gave {amount_of(rows[0])!r} for 1.5"
    assert amount_of(rows[1]) is None, f"amount_of gave {amount_of(rows[1])!r} for abc"
    assert amount_of(rows[2]) is None, f"amount_of gave {amount_of(rows[2])!r} for a blank"
    assert function("good_rows")(rows) == [rows[0]], "good_rows should keep only the first row"


def test_program():
    """Running the program prints the tests' message and the report."""
    got = run()
    assert got == "report: all checks passed\n" + REPORT, f"Your program printed:\n{got}"
