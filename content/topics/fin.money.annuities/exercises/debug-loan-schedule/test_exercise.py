from checks import run, run_with

EXPECTED = (
    "Payment: 828.23\n"
    "Month 1: interest 48.00, balance 4,019.77\n"
    "Month 2: interest 40.20, balance 3,231.73\n"
    "Month 3: interest 32.32, balance 2,435.82\n"
    "Month 4: interest 24.36, balance 1,631.94\n"
    "Month 5: interest 16.32, balance 820.03\n"
    "Month 6: interest 8.20, balance 0.00\n"
)


def tidy(printed):
    """A float leftover just below zero prints as -0.00, which counts as 0.00."""
    return printed.replace("-0.00", "0.00")


def test_the_schedule():
    """Prints the payment and six months, ending at a balance of 0.00."""
    printed = tidy(run())
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_another_loan():
    """Works for another loan: 12,000 at 6% a year over 3 months ends at 0.00."""
    expected = (
        "Payment: 4,040.07\n"
        "Month 1: interest 60.00, balance 8,019.93\n"
        "Month 2: interest 40.10, balance 4,019.97\n"
        "Month 3: interest 20.10, balance 0.00\n"
    )
    printed = tidy(run_with({"principal": 12000, "yearly_rate": 0.06, "months": 3}))
    assert printed == expected, (
        f"With principal = 12000, yearly_rate = 0.06 and months = 3 it should print:\n"
        f"{expected}\nIt printed:\n{printed}"
    )
