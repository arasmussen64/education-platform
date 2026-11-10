import numpy as np

from checks import function, run


def test_the_output():
    """Prints 0.984."""
    assert run() == "0.984\n"


def test_rectangle():
    """The 2-by-1 rectangle's corners give 0.8."""
    top_share = function("top_share")
    assert top_share(np.array([[0.0, 0.0], [2.0, 0.0], [0.0, 1.0], [2.0, 1.0]])) == 0.8
