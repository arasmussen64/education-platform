import numpy as np

from checks import function, run


def test_the_output():
    """Prints the two outputs."""
    assert run() == '[[-2.0, -2.0, -2.0], [-2.0, -2.0, -2.0]]\n[[24.0, 28.0]]\n'


def test_other_cases():
    """A 2-by-2 kernel by hand, and a 1-by-1 kernel that scales."""
    correlate2d = function("correlate2d")
    image = np.array([[1.0, 2.0, 0.0], [0.0, 1.0, 3.0], [2.0, 0.0, 1.0]])
    assert correlate2d(image, np.array([[1.0, 2.0], [0.0, -1.0]])).tolist() == [[4.0, -1.0], [2.0, 6.0]]
    assert np.array_equal(correlate2d(image, np.array([[3.0]])), 3 * image)
