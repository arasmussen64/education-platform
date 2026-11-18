from checks import run, run_with

# Hidden tests: the learner sees each docstring and whether it passed.


def test_the_report():
    """Prints both funds' final amounts and the difference as a share of the better one: 20.2%."""
    assert run() == (
        "Fund A: $151,293.10\n"
        "Fund B: $189,693.11\n"
        "Difference: 20.2% of the better fund's amount\n"
    )


def test_other_fees():
    """Works when fund A is the cheaper one: fees of 0.2% and 1.2% give 26.1%."""
    assert run_with({"fee_a": 0.002, "fee_b": 0.012}) == (
        "Fund A: $186,864.04\n"
        "Fund B: $138,139.48\n"
        "Difference: 26.1% of the better fund's amount\n"
    )
