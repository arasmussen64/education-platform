from checks import run

EXPECTED = (
    "Mean monthly return: 0.83%\n"
    "Monthly volatility: 3.31%\n"
    "statistics.stdev agrees: 3.31%\n"
    "Dividing by n instead: 3.02%\n"
    "Annual volatility: 11.47%\n"
)


def test_volatility():
    """Prints the mean, the monthly volatility both ways, the n version and the annual volatility."""
    assert run() == EXPECTED
