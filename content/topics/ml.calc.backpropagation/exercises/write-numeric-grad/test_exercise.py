import numpy as np

from checks import function, run


def test_the_output():
    """Prints 2M and True."""
    printed = run()
    assert printed == '[[ 2. -4.]\n [ 1.  6.]]\nTrue\n', f"Your program printed:\n{printed}"


def test_other_shapes_and_functions():
    """Works for a 2-by-3 matrix with f = sum of cubes (gradient 3W²) and for a vector with f = a dot product."""
    numeric_grad = function("numeric_grad")
    W = np.array([[1.0, 2.0, -1.0], [0.5, 0.0, 3.0]])
    assert np.allclose(numeric_grad(lambda W: np.sum(W**3), W), 3 * W**2, atol=1e-5)
    v = np.array([1.0, -2.0, 0.5])
    a = np.array([3.0, 1.0, 2.0])
    assert np.allclose(numeric_grad(lambda v: v @ a, v), a, atol=1e-6)
