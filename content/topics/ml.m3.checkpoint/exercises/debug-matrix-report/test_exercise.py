import numpy as np

from checks import function, printed, run

EXPECTED = 'plane [ 2.015 -1.035  3.024]\nlstsq agrees True\nvariance kept 0.9998\ncompression error 0.079\n'


def test_the_output():
    """Prints the plane, the lstsq check, the variance kept and the compression error."""
    out = run()
    assert out == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{out}"


def test_exact_plane():
    """On points exactly on a plane: the exact coefficients, all the variance kept, no error."""
    out = printed(function("report"), np.array([[0.0, 0.0, 3.0], [1.0, 0.0, 5.0], [0.0, 1.0, 2.0], [2.0, 3.0, 4.0], [3.0, 1.0, 8.0], [1.0, 2.0, 3.0]]))
    assert out == "plane [ 2. -1.  3.]\nlstsq agrees True\nvariance kept 1.0\ncompression error 0.0\n", (
        f"For points on the plane z = 2x - y + 3 it printed:\n{out}"
    )
