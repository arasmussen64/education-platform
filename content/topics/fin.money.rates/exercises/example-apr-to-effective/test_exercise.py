from checks import run

EXPECTED = (
    "Charged each month: 2.00%\n"
    "$1,000 after a year: $1,268.24\n"
    "Effective annual rate: 26.82%\n"
    "By the formula: 26.82%\n"
)


def test_a_year_of_card_interest():
    """Prints the monthly rate, the balance after a year and the effective rate both ways."""
    assert run() == EXPECTED
