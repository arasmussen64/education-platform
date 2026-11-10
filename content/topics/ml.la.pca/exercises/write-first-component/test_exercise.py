import numpy as np

from checks import function, run


def test_the_output():
    """Prints the component, then the scores."""
    printed = run()
    assert printed == "[0.772 0.635]\n[-3.201 -1.794 -1.021  1.021  1.794  3.201]\n", f"Your program printed:\n{printed}"


def test_collinear_points():
    """Points on the line y = x give the component [0.707, 0.707] and scores spaced by the square root of 2."""
    first_component = function("first_component")
    scores = function("scores")
    X = np.array([[1.0, 1.0], [2.0, 2.0], [3.0, 3.0], [4.0, 4.0]])
    assert np.allclose(first_component(X), [2**-0.5, 2**-0.5])
    assert np.allclose(scores(X), np.array([-1.5, -0.5, 0.5, 1.5]) * 2**0.5)
