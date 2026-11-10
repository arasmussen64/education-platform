from checks import function, run


def test_the_output():
    """Prints the two cost tuples."""
    printed = run()
    assert printed == '(2565, 6156000, 54480)\n(23, 1380, 220)\n', f"Your program printed:\n{printed}"


def test_another_network():
    """A single layer from 5 to 1, one example, a batch of 1 in float32: 6 parameters, 36 FLOPs, 6 * 16 + 6 * 4 bytes."""
    model_cost = function("model_cost")
    assert tuple(model_cost([5, 1], 1, 1, 4)) == (6, 36, 6 * 16 + 6 * 4)
