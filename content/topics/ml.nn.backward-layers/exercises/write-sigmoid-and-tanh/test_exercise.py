import numpy as np

from checks import function, run


def test_the_output():
    """Prints each layer's first row and a passing check."""
    printed = run()
    assert printed == 'Sigmoid [0.5, 0.731, 0.119] True\nTanh [0.0, 0.762, -0.964] True\n', f"Your program printed:\n{printed}"


def test_values_and_gradients():
    """Sigmoid of 0 is 0.5 with slope 0.25; tanh of 0 is 0 with slope 1; both backward passes scale an arbitrary gradient."""
    Sigmoid = function("Sigmoid")
    Tanh = function("Tanh")
    X = np.array([[0.0, 2.0], [-3.0, 0.5]])
    s, t = Sigmoid(), Tanh()
    assert np.allclose(s.forward(X)[0, 0], 0.5) and np.allclose(t.forward(X)[0, 0], 0.0)
    g = np.array([[2.0, -1.0], [0.5, 4.0]])
    assert np.allclose(s.backward(g)[0, 0], 0.5) and np.allclose(t.backward(g)[0, 0], 2.0)
    out = s.forward(X)
    assert np.allclose(s.backward(g), g * out * (1 - out))
    out = t.forward(X)
    assert np.allclose(t.backward(g), g * (1 - out ** 2))
