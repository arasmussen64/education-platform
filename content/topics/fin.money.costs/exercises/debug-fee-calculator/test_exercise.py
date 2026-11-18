from checks import run, run_with

EXPECTED = (
    "Without the fee: $135,454.20\n"
    "With the fee: $100,165.02\n"
    "The fee takes 26.1% of what you'd have had\n"
)


def test_the_report():
    """Prints $135,454.20 without the fee, $100,165.02 with it, and 26.1%."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_other_numbers():
    """Works for other numbers: a 2% fee over 10 years takes 18.3%."""
    expected = (
        "Without the fee: $65,155.79\n"
        "With the fee: $53,237.02\n"
        "The fee takes 18.3% of what you'd have had\n"
    )
    printed = run_with({"fee": 0.02, "years": 10})
    assert printed == expected, f"With a 2% fee over 10 years it should print:\n{expected}\nIt printed:\n{printed}"
