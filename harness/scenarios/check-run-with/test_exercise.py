from checks import run_with


def test_swaps_other_values():
    """Swaps any two values."""
    assert run_with({"x": "left", "y": "right"}) == "right left\n"


def test_missing_starting_line():
    """Needs a starting line for each name."""
    run_with({"z": 1})
