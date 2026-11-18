from checks import function, run

EXPECTED = (
    "Month 0: $20.00, drawdown 0.0%\n"
    "Month 1: $22.00, drawdown 0.0%\n"
    "Month 2: $19.80, drawdown -10.0%\n"
    "Month 3: $23.00, drawdown 0.0%\n"
    "Month 4: $18.40, drawdown -20.0%\n"
    "Month 5: $20.70, drawdown -10.0%\n"
    "Month 6: $24.00, drawdown 0.0%\n"
)


def test_the_table():
    """Prints each month's price and its drawdown from the running peak."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_other_prices():
    """drawdowns([10, 8, 12, 9, 6]) is [0, -0.2, 0, -0.25, -0.5]."""
    drawdowns = function("drawdowns")
    got = drawdowns([10, 8, 12, 9, 6])
    want = [0.0, -0.2, 0.0, -0.25, -0.5]
    assert isinstance(got, list) and len(got) == len(want), (
        f"drawdowns([10, 8, 12, 9, 6]) returned {got}; expected a list of 5 drawdowns."
    )
    for g, w in zip(got, want):
        assert abs(g - w) < 1e-9, f"drawdowns([10, 8, 12, 9, 6]) returned {got}; expected {want}."
