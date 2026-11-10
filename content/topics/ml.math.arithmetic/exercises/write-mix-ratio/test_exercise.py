from checks import run, run_with


def test_one_and_a_half_litres():
    """Prints Juice: 0.60 litres, then Water: 0.90 litres."""
    printed = run()
    assert printed == "Juice: 0.60 litres\nWater: 0.90 litres\n", (
        f"Your program printed:\n{printed}"
    )


def test_any_total():
    """Works for any total: 2.0 litres gives 0.80 and 1.20."""
    printed = run_with({"total": 2.0})
    assert printed == "Juice: 0.80 litres\nWater: 1.20 litres\n", (
        f"With total = 2.0 it should print Juice: 0.80 litres, then Water: 1.20 litres. It printed:\n{printed}"
    )
