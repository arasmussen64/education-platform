from checks import run, run_with

EXPECTED = "Without the fee: $34,242.38\nWith the fee: $23,467.65\nThe fee takes 31.5%\n"


def test_the_report():
    """Prints both final amounts and the share the fee takes: 31.5%."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_other_numbers():
    """Works for any numbers: $1,000 growing 10% with a 1% fee for 2 years loses 2.0%."""
    expected = "Without the fee: $1,210.00\nWith the fee: $1,185.92\nThe fee takes 2.0%\n"
    printed = run_with({"start": 1000, "growth": 0.1, "fee": 0.01, "years": 2})
    assert printed == expected, f"With those numbers it should print:\n{expected}\nIt printed:\n{printed}"
