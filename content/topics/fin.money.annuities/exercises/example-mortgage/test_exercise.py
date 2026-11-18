from checks import run


def test_the_mortgage():
    """Prints the payment, the first two months and the total interest."""
    assert run() == (
        "Payment: 1,798.65\n"
        "Month 1: interest 1,500.00, paid down 298.65\n"
        "  balance 299,701.35\n"
        "Month 2: interest 1,498.51, paid down 300.14\n"
        "  balance 299,401.20\n"
        "Total interest: 347,514.57\n"
    )
