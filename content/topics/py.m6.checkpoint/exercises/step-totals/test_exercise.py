from checks import function, run

REPORT = "north: 150.50\nsouth: 80.00\neast: 45.25\nRows: 6\nBad rows: 2\nTotal: 275.75\n"


def test_totals():
    """totals_by_region adds a region's good amounts, skips bad rows, and keeps first-seen order."""
    rows = [
        {"region": "b", "amount": "1"},
        {"region": "a", "amount": "x"},
        {"region": "a", "amount": "2.5"},
        {"region": "b", "amount": "2"},
    ]
    got = function("totals_by_region")(rows)
    assert got == {"b": 3.0, "a": 2.5}, f"totals_by_region returned {got!r}"
    assert list(got) == ["b", "a"], f"regions came out in the order {list(got)!r}"


def test_program():
    """Running the program prints the tests' message and the report."""
    got = run()
    assert got == "report: all checks passed\n" + REPORT, f"Your program printed:\n{got}"
