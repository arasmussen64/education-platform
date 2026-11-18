from checks import run


def test_both_comparisons():
    """Prints the later offer in today's money, the gap, and the offer now in two years."""
    assert run() == (
        "The later offer, today: 9,789.96\n"
        "Money now wins by: 210.04\n"
        "The offer now, in 2 years: 11,236.00\n"
    )
