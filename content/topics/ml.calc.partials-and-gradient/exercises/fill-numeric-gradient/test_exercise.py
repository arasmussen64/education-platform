import numpy as np

from checks import function, run


def test_the_output():
    """Prints the three gradients."""
    printed = run()
    assert printed == '[2. 6.]\n[3. 2.]\n[4. 4. 1.]\n', f"Your program printed:\n{printed}"


def test_another_function():
    """For f = x y² + exp(z) at (1, 2, 0) the gradient is [4, 4, 1], to six decimals."""
    numeric_gradient = function("numeric_gradient")
    g = numeric_gradient(lambda p: p[0] * p[1] ** 2 + np.exp(p[2]), np.array([1.0, 2.0, 0.0]))
    assert np.abs(g - [4.0, 4.0, 1.0]).max() < 1e-6
