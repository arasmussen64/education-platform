from checks import function, run


def test_the_output():
    """Prints the two counts for both networks."""
    printed = run()
    assert printed == '235146 84510720000\n23 1080\n', f"Your program printed:\n{printed}"


def test_edge_cases():
    """A single layer, a network with no layers, and the FLOPs of one example."""
    parameter_count = function("parameter_count")
    training_flops = function("training_flops")
    assert parameter_count([5, 1]) == 6 and parameter_count([7]) == 0
    assert training_flops([5, 1], 1) == 30 and training_flops([10, 10, 10], 100) == 3 * 400 * 100
