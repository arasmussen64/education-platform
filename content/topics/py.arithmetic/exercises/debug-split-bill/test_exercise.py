from checks import run, run_with

EXPECTED = "Total: 72\nEach pays: 18.0\n"


def test_the_bill():
    """Prints Total: 72, then Each pays: 18.0."""
    printed = run()
    assert printed == EXPECTED, (
        f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"
    )


def test_any_bill():
    """Works for any bill, not just this one."""
    printed = run_with({"food": 30, "drinks": 10, "people": 4})
    assert printed == "Total: 40\nEach pays: 10.0\n", (
        "With food 30, drinks 10 and 4 people it should print Total: 40, "
        f"then Each pays: 10.0. It printed:\n{printed}"
    )
