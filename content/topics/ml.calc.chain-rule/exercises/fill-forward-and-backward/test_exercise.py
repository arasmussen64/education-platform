import numpy as np

from checks import function, run


def test_the_output():
    """Prints the four values, the derivative and True."""
    printed = run()
    assert printed == '[ 0.5       2.5      12.182494  0.082085]\n-0.246255\nTrue\n', f"Your program printed:\n{printed}"


def test_at_another_point():
    """At x = 0 the values are [0, 1, e, 1/e] and the derivative is -3/e."""
    forward = function("forward")
    backward = function("backward")
    values = forward(0.0)
    assert np.allclose(values, [0.0, 1.0, np.e, 1 / np.e])
    assert abs(backward(values) + 3 / np.e) < 1e-9
