from checks import function, run, run_with

EXPECTED = "day 0: 100.00\nday 1: 102.00\nday 2: 105.92\n"


def test_the_index():
    """Prints the index level for each day, starting at 100.00."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_market_value():
    """market_value adds up price times shares: 30 x 40 + 100 x 5 + 8 x 125 is 2700."""
    market_value = function("market_value")
    got = market_value({"North": 30.0, "South": 100.0, "West": 8.0})
    assert got == 2700, f"market_value of those prices returned {got}"


def test_other_shares():
    """With other share counts the weights change: 10, 20 and 100 million give 100.00, 97.52, 96.19."""
    printed = run_with({"shares": {"North": 10, "South": 20, "West": 100}})
    expected = "day 0: 100.00\nday 1: 97.52\nday 2: 96.19\n"
    assert printed == expected, f"With those shares it should print:\n{expected}\nIt printed:\n{printed}"
