from checks import run, run_with


def test_this_bill():
    """Prints Total with tip: 99.71, then Each pays: 33.24."""
    printed = run()
    assert printed == "Total with tip: 99.71\nEach pays: 33.24\n", (
        f"Your program printed:\n{printed}"
    )


def test_any_bill():
    """Works for any bill, tip and number of people."""
    printed = run_with({"bill": 60, "tip_percent": 20, "people": 4})
    assert printed == "Total with tip: 72.00\nEach pays: 18.00\n", (
        "With a bill of 60, a 20% tip and 4 people it should print "
        f"Total with tip: 72.00, then Each pays: 18.00. It printed:\n{printed}"
    )
