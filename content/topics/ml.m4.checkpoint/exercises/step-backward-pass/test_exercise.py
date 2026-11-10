import numpy as np

from checks import function, run


def test_the_output():
    """Prints the shapes and True."""
    printed = run()
    assert printed == "{'W1': (2, 4), 'b1': (4,), 'W2': (4,), 'b2': ()}\nTrue\n", f"Your program printed:\n{printed}"


def test_a_unit_that_is_off():
    """A hidden unit that is off for every example gets a zero gradient."""
    backward = function("backward")
    params = {"W1": np.zeros((2, 3)), "b1": np.zeros(3), "W2": np.array([0.5, -0.5, 1.0]), "b2": np.array(0.0)}
    X = np.array([[1.0, 0.0], [0.0, 1.0]])
    z1 = np.array([[1.0, -1.0, 2.0], [0.5, -2.0, 1.0]])
    grads = backward(X, np.array([1.0, 0.0]), params, z1, np.maximum(z1, 0.0), np.array([0.7, 0.4]))
    assert np.abs(grads["W1"][:, 1]).max() == 0 and grads["b1"][1] == 0
    assert np.abs(grads["W1"][:, 0]).max() > 0 and np.abs(grads["W2"]).max() > 0
