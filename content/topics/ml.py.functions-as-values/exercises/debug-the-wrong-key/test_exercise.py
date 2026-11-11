from checks import run, run_with

EXPECTED = "[('tea', 2.5), ('cake', 4.0), ('jam', 6.5)]\njam\n"


def test_the_output():
    """Prints the products cheapest first, then jam."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_other_products():
    """Works when the alphabetical order and the price order disagree."""
    printed = run_with({"products": [("zebra", 1.0), ("apple", 9.0), ("mango", 3.0)]})
    assert printed == "[('zebra', 1.0), ('mango', 3.0), ('apple', 9.0)]\napple\n", (
        f"It should list them cheapest first, then name the most expensive. It printed:\n{printed}"
    )
