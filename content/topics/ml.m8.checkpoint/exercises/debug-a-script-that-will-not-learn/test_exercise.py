import numpy as np

from checks import function, run

EXPECTED = 'loss 1.97 -> 0.06 | held-out accuracy 0.95 | at least 0.9: True\nevaluating twice gives the same answer: True\n'


def test_the_output():
    """Prints a run that clears the bar and a double evaluation that agrees."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_the_pieces():
    """start_weights is random and scaled by the fan-in, RATE is 0.01, and evaluate leaves dropout off."""
    fit = function("fit")
    m = fit.__globals__
    W = m["start_weights"](np.random.default_rng(1), (400, 50), 400)
    assert W.shape == (400, 50) and 0.04 < W.std() < 0.06 and not np.allclose(W[:, 0], W[:, 1])
    assert m["RATE"] == 0.01
    layer = m["Dropout"](0.5, seed=1)
    net = m["Sequential"]([layer])
    X = np.ones((50, 4))
    first = m["evaluate"](net, m["SoftmaxCrossEntropy"](), X, np.zeros(50, dtype=int))
    assert layer.training is False and first == m["evaluate"](net, m["SoftmaxCrossEntropy"](), X, np.zeros(50, dtype=int))
