from checks import run


def test_the_plan_and_the_fund():
    """Prints the six months of the savings plan, its totals, and the fund's best and worst month and running peaks."""
    assert run() == (
        "month 1: interest 0.00, balance 300.00\n"
        "month 2: interest 1.50, balance 601.50\n"
        "month 3: interest 3.01, balance 904.51\n"
        "month 4: interest 4.52, balance 1,209.03\n"
        "month 5: interest 6.05, balance 1,515.08\n"
        "month 6: interest 7.58, balance 1,822.65\n"
        "deposited 1,800.00\n"
        "total interest 22.65\n"
        "best month 5.5%, worst month -3.4%\n"
        "highest so far: [20.0, 20.6, 20.6, 21.0, 21.4]\n"
    )
