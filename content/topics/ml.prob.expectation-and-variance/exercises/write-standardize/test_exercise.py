import numpy as np

from checks import function, run


def test_the_output():
    """Prints the two test scores' z-scores and the three heights'."""
    printed = run()
    assert printed == '1.5 0.5\n[-2.   0.   2.5]\n', f"Your program printed:\n{printed}"


def test_properties():
    """The mean standardizes to 0, a value one spread above to 1, and an array keeps its shape."""
    standardize = function("standardize")
    assert standardize(70, 70, 8) == 0 and standardize(78, 70, 8) == 1
    z = standardize(np.array([[1.0, 2.0], [3.0, 4.0]]), 2.5, 0.5)
    assert z.shape == (2, 2) and z.tolist() == [[-3.0, -1.0], [1.0, 3.0]]
