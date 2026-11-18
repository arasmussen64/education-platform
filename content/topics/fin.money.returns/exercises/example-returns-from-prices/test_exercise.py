from checks import run

EXPECTED = (
    "10.00%\n"
    "-10.00%\n"
    "10.00%\n"
    "Chained: 8.90%\n"
    "Last over first: 8.90%\n"
    "Added up: 10.00%\n"
)


def test_returns_and_totals():
    """Prints the three returns, the chained total, the last-over-first total and the sum."""
    assert run() == EXPECTED
