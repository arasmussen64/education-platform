from checks import function, run, run_with

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7). A balance that is a float leftover
# just below zero prints as -0.00, which counts as 0.00.

SCHEDULE = (
    "Payment: 1,026.41\n"
    "Month 1: interest 45.00, paid down 981.41, balance 5,018.59\n"
    "Month 2: interest 37.64, paid down 988.77, balance 4,029.81\n"
    "Month 3: interest 30.22, paid down 996.19, balance 3,033.62\n"
    "Month 4: interest 22.75, paid down 1,003.66, balance 2,029.96\n"
    "Month 5: interest 15.22, paid down 1,011.19, balance 1,018.77\n"
    "Month 6: interest 7.64, paid down 1,018.77, balance 0.00\n"
    "Total paid: 6,158.48\n"
    "Total interest: 158.48\n"
)


def tidy(printed):
    return printed.replace("-0.00", "0.00")


def test_the_payment():
    """payment(6000, 0.0075, 6) is 1,026.41, and 1,000 over 2 periods at 10% is 576.19."""
    payment = function("payment")
    assert abs(payment(6000, 0.0075, 6) - 1026.41) < 0.005
    assert abs(payment(1000, 0.1, 2) - 576.19) < 0.005


def test_the_schedule():
    """Prints the payment, the six months and the totals."""
    assert tidy(run()) == SCHEDULE


def test_another_loan():
    """Works for another loan: 12,000 at 6% a year over 3 months."""
    expected = (
        "Payment: 4,040.07\n"
        "Month 1: interest 60.00, paid down 3,980.07, balance 8,019.93\n"
        "Month 2: interest 40.10, paid down 3,999.97, balance 4,019.97\n"
        "Month 3: interest 20.10, paid down 4,019.97, balance 0.00\n"
        "Total paid: 12,120.20\n"
        "Total interest: 120.20\n"
    )
    printed = run_with({"principal": 12000, "yearly_rate": 0.06, "months": 3})
    assert tidy(printed) == expected
