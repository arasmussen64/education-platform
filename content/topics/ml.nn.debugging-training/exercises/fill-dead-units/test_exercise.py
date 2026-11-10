import numpy as np

from checks import function, run


def test_the_output():
    """Prints 0 and then 20."""
    printed = run()
    assert printed == '0\n20\n', f"Your program printed:\n{printed}"


def test_other_cases():
    """A single killed unit counts as one; a network with no ReLU has none; a unit that fires on one row is alive."""
    # One import for everything, so the ReLU class dead_units looks for is the one the network was built with.
    dead_units = function("dead_units")
    Dense, ReLU, Sequential = (dead_units.__globals__[name] for name in ("Dense", "ReLU", "Sequential"))
    X = np.random.default_rng(1).standard_normal((40, 3))
    net = Sequential([Dense(3, 8, seed=2), ReLU(), Dense(8, 2, seed=3)])
    net.layers[0].b[5] = -50.0
    assert dead_units(net, X) == 1
    assert dead_units(Sequential([Dense(3, 2, seed=1)]), X) == 0
    net.layers[0].W[:, 5] = 0.0
    net.layers[0].b[5] = 0.0
    assert dead_units(net, X) == 1
    net.layers[0].b[5] = 1e-9
    assert dead_units(net, X) == 0
