from checks import run


def test_the_quote_and_the_buy():
    """Prints the quote, the two fills, the average price and the cost above the middle."""
    assert run() == (
        "bid 99.95, ask 100.05, spread 0.10, middle 100.00\n"
        "bought 200 at 100.05\n"
        "bought 300 at 100.10\n"
        "paid 50,040.00, an average of 100.08 a share\n"
        "above the middle: 40.00\n"
    )
