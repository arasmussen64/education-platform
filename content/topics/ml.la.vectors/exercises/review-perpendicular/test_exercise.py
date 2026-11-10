import numpy as np

from checks import function, run


def test_the_output():
    """Prints True, then False."""
    assert run() == "True\nFalse\n"


def test_three_dimensions():
    """Two axes are perpendicular; a vector and a scaled copy of itself aren't."""
    is_perpendicular = function("is_perpendicular")
    assert is_perpendicular(np.array([1.0, 0.0, 0.0]), np.array([0.0, 5.0, 0.0])) is True
    assert is_perpendicular(np.array([1.0, 2.0, 3.0]), np.array([2.0, 4.0, 6.0])) is False
