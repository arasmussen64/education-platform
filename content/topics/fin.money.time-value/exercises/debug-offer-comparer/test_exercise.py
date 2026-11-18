from checks import run, run_with

EXPECTED = "Offer A: 8,349.79\nOffer B: 8,161.87\nTake offer A\n"


def test_the_two_offers():
    """Values offer A at 8,349.79 and offer B at 8,161.87 today, and takes offer A."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_other_offers():
    """Works for other offers: [1000, 1000] against [0, 2420] at 10% takes offer B."""
    expected = "Offer A: 1,909.09\nOffer B: 2,200.00\nTake offer B\n"
    printed = run_with({"offer_a": [1000, 1000], "offer_b": [0, 2420], "rate": 0.1})
    assert printed == expected, (
        f"With offer_a = [1000, 1000], offer_b = [0, 2420] and rate = 0.1 it should "
        f"print:\n{expected}\nIt printed:\n{printed}"
    )
