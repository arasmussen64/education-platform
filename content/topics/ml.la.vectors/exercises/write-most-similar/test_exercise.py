import numpy as np

from checks import function, run


def test_the_output():
    """Prints 0."""
    printed = run()
    assert printed == "0\n", f"Your program printed:\n{printed}"


def test_length_is_ignored():
    """A short row pointing the query's way beats a long row pointing elsewhere."""
    most_similar = function("most_similar")
    rows = np.array([[5.0, 0.0], [1.0, 3.0], [0.0, 0.5]])
    assert most_similar(np.array([0.0, 1.0]), rows) == 2
