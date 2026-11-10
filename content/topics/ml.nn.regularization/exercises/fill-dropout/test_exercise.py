import numpy as np

from checks import function, run


def test_the_output():
    """Prints the fraction, the mean, the two values and True."""
    printed = run()
    assert printed == '0.5 1.0 [0.0, 2.0]\nTrue\n', f"Your program printed:\n{printed}"


def test_other_rates():
    """At p = 0.2 about a fifth is dropped and survivors are 1.25; backward passes the same mask; eval changes nothing."""
    Dropout = function("Dropout")
    layer = Dropout(0.2, seed=3)
    X = np.ones((2000, 10))
    out = layer.forward(X)
    assert 0.17 < (out == 0).mean() < 0.23 and np.allclose(out[out > 0], 1.25) and 0.95 < out.mean() < 1.05
    grad = layer.backward(np.ones_like(X))
    assert np.array_equal(grad == 0, out == 0) and np.allclose(grad[grad > 0], 1.25)
    layer.training = False
    assert np.array_equal(layer.forward(X), X) and np.array_equal(layer.backward(X), X)
