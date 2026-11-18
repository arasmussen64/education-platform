from checks import run, run_with

EXPECTED = (
    "Year 1: 15.00%\n"
    "Year 2: -25.00%\n"
    "Year 3: 25.00%\n"
    "Year 4: 8.99%\n"
    "Growth per year: 4.11%\n"
    "$10,000 at that rate for 4 years: $11,750.00\n"
    "$10,000 in the fund itself: $11,750.00\n"
)


def test_yearly_returns():
    """Prints the four yearly returns: 15.00%, -25.00%, 25.00% and 8.99%."""
    got = run().splitlines()[:4]
    want = EXPECTED.splitlines()[:4]
    assert got == want, "Expected the yearly returns:\n" + "\n".join(want) + "\nYour program printed:\n" + "\n".join(got)


def test_growth_matches_the_fund():
    """Growth per year is 4.11%, and $10,000 at that rate ends where the fund itself does."""
    got = run().splitlines()[4:]
    want = EXPECTED.splitlines()[4:]
    assert got == want, "Expected:\n" + "\n".join(want) + "\nYour program printed:\n" + "\n".join(got)


def test_other_prices():
    """Works for other prices: 50, 60, 45, 63 grow 8.01% a year, to $12,600.00."""
    printed = run_with({"prices": [50.0, 60.0, 45.0, 63.0]})
    expected = (
        "Year 1: 20.00%\n"
        "Year 2: -25.00%\n"
        "Year 3: 40.00%\n"
        "Growth per year: 8.01%\n"
        "$10,000 at that rate for 3 years: $12,600.00\n"
        "$10,000 in the fund itself: $12,600.00\n"
    )
    assert printed == expected, (
        f"With prices = [50.0, 60.0, 45.0, 63.0] it should print:\n{expected}\nIt printed:\n{printed}"
    )
