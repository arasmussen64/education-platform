import numpy as np

from checks import function, printed, run

EXPECTED = "[0. 0.]\n[0. 1.]\n[-1.  1.]\n[-1.  0.]\n"


def test_the_output():
    """Prints the four rotated corners."""
    out = run()
    assert out == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{out}"


def test_other_angle_and_points():
    """rotation(180) sends [1, 2] to [-1, -2] and [3, -1] to [-3, 1]."""
    rotation = function("rotation")
    corners_after = function("corners_after")
    out = printed(corners_after, rotation(180), np.array([[1.0, 2.0], [3.0, -1.0]]))
    assert out == "[-1. -2.]\n[-3.  1.]\n", f"For a half turn it printed:\n{out}"
