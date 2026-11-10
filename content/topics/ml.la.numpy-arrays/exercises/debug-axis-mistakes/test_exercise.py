import numpy as np

from checks import function, printed, run

EXPECTED = "daily averages: [20. 30. 50.]\nabove average:\n[[-5. -5.  5.]\n [ 5.  5. -5.]]\nbest day: 3\n"


def test_the_output():
    """Prints the daily averages, the differences and the best day."""
    out = run()
    assert out == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{out}"


def test_other_grid():
    """Works for two shops and two days."""
    out = printed(function("report"), np.array([[1, 2], [3, 8]]))
    assert out == "daily averages: [2. 5.]\nabove average:\n[[-1. -3.]\n [ 1.  3.]]\nbest day: 2\n", (
        f"For [[1, 2], [3, 8]] it printed:\n{out}"
    )
