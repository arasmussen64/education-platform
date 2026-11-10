import numpy as np

from checks import function, printed, run

EXPECTED = "first component explains 0.984\ndirection [0.772 0.635]\n"


def test_the_output():
    """Prints the share and the direction."""
    out = run()
    assert out == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{out}"


def test_rectangle():
    """For the corners of a 2-by-1 rectangle: 0.8 along the x direction."""
    out = printed(function("report"), np.array([[0.0, 0.0], [2.0, 0.0], [0.0, 1.0], [2.0, 1.0]]))
    assert out == "first component explains 0.8\ndirection [1. 0.]\n", f"For the rectangle it printed:\n{out}"
