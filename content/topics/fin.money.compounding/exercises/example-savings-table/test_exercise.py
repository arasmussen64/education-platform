from checks import run

EXPECTED = (
    "Year 0: 1,000.00\n"
    "Year 1: 1,070.00\n"
    "Year 2: 1,144.90\n"
    "Year 3: 1,225.04\n"
    "Year 4: 1,310.80\n"
    "Year 5: 1,402.55\n"
    "Formula: 1,402.55\n"
    "Rule of 72: doubles in about 10.3 years\n"
    "Exactly: 10.2 years\n"
)


def test_the_table():
    """Prints the five-year table, the formula's answer and the doubling time."""
    assert run() == EXPECTED
