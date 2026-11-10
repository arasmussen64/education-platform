import numpy as np

from checks import function, run


def test_the_output():
    """Prints [0.707 0.707] 3.0."""
    printed = run()
    assert printed == "[0.707 0.707] 3.0\n", f"Your program printed:\n{printed}"


def test_another_matrix():
    """Finds the eigenvector for eigenvalue 3 of [[3, 1], [0, 2]], with length 1."""
    top_eigenvector = function("top_eigenvector")
    B = np.array([[3.0, 1.0], [0.0, 2.0]])
    x = top_eigenvector(B)
    assert abs(np.linalg.norm(x) - 1) < 1e-9
    assert np.allclose(B @ x, 3 * x, atol=1e-6)
