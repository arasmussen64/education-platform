from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).

EXPECTED = "1 a year: 21.00%\n2 a year: 22.10%\n4 a year: 22.71%\n12 a year: 23.14%\n365 a year: 23.36%\n"


def test_the_table():
    """Prints the effective rate of 21% APR at 1, 2, 4, 12 and 365 times a year."""
    assert run() == EXPECTED


def test_other_rates():
    """effective_annual_rate(0.08, 4) is about 0.0824, and (0.36, 12) about 0.4258."""
    effective_annual_rate = function("effective_annual_rate")
    assert abs(effective_annual_rate(0.08, 4) - 0.08243216) < 1e-6
    assert abs(effective_annual_rate(0.36, 12) - 0.42576089) < 1e-6


def test_once_a_year():
    """Compounded once a year, the effective rate is the APR itself: effective_annual_rate(0.07, 1) is 0.07."""
    effective_annual_rate = function("effective_annual_rate")
    assert abs(effective_annual_rate(0.07, 1) - 0.07) < 1e-9
