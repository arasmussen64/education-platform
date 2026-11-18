from checks import run


def test_the_prices():
    """Prints the bond's cash flows and its price at market rates of 3%, 5% and 7%."""
    assert run() == (
        "Cash flows: [0, 50.0, 50.0, 1050.0]\n"
        "Market rate 3%: $1,056.57\n"
        "Market rate 5%: $1,000.00\n"
        "Market rate 7%: $947.51\n"
    )
