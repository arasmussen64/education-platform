from checks import function, run

EXPECTED = "['load', 'clean', 'features', 'report', 'train', 'evaluate'] complete\n([], False)\n"


def test_the_output():
    """Prints the complete schedule and the stuck cycle."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_other_graphs():
    """A diamond is placed completely with its edges forward; a self-loop is stuck."""
    schedule = function("schedule")
    order, complete = schedule({"a": ["b", "c"], "b": ["d"], "c": ["d"], "d": []})
    assert complete and order.index("a") < order.index("b") < order.index("d") and order.index("c") < order.index("d")
    assert schedule({"a": ["a"]}) == ([], False)
