import numpy as np

from checks import function, printed, run

EXPECTED = "similarities: [1.    0.707 0.   ]\nmost similar: row 0\n"


def test_the_output():
    """Prints the three similarities and the most similar row."""
    out = run()
    assert out == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{out}"


def test_two_rows():
    """Works for two rows of three: one along the query, one perpendicular to it."""
    out = printed(function("report"), np.array([0.0, 1.0, 0.0]), np.array([[0.0, 2.0, 0.0], [3.0, 0.0, 4.0]]))
    assert out == "similarities: [1. 0.]\nmost similar: row 0\n", f"For those rows it printed:\n{out}"
