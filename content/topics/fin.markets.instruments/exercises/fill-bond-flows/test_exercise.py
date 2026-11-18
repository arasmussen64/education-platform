from checks import run, run_with


def test_the_price():
    """Prints Price: $466.88."""
    printed = run()
    assert printed == "Price: $466.88\n", f"Your program printed:\n{printed}"


def test_another_bond():
    """Works for any bond: $1,000 paying 5% for 2 years, at a market rate of 4%, is $1,018.86."""
    printed = run_with({"face": 1000, "coupon_rate": 0.05, "years": 2, "market_rate": 0.04})
    assert printed == "Price: $1,018.86\n", (
        f"For that bond it should print Price: $1,018.86. It printed:\n{printed}"
    )
