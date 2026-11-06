from checks import run, run_with


def test_prints_swapped():
    """Prints the two values swapped: 5 3."""
    printed = run()
    assert printed == "5 3\n", f"Expected 5 3. Your program printed:\n{printed}"


def test_swaps_any_values():
    """Swaps any two values, not just 3 and 5."""
    printed = run_with({"x": "left", "y": "right"})
    assert printed == "right left\n", (
        "Starting with x as left and y as right, it should print right left. "
        f"It printed:\n{printed}\nSwap using the names, not by typing values."
    )
