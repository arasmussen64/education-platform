import numpy as np

from checks import function, run


def test_the_output():
    """Prints the row, the shape and the strided output."""
    printed = run()
    assert printed == '[0.0, -9.0, -4.0, 1.0]\n(6, 6) [[0.0, -4.0], [4.0, 0.0]]\n', f"Your program printed:\n{printed}"


def test_other_cases():
    """A 2-by-2 kernel by hand, padding that keeps the size, a stride of 3, and a 1-by-1 kernel that scales."""
    correlate2d = function("correlate2d")
    image = np.array([[1.0, 2.0, 0.0], [0.0, 1.0, 3.0], [2.0, 0.0, 1.0]])
    assert correlate2d(image, np.array([[1.0, 2.0], [0.0, -1.0]])).tolist() == [[4.0, -1.0], [2.0, 6.0]]
    box = np.ones((3, 3))
    padded = correlate2d(image, box, padding=1)
    assert padded.shape == (3, 3) and padded[1, 1] == image.sum() and padded[0, 0] == image[:2, :2].sum()
    strided = correlate2d(np.arange(49.0).reshape(7, 7), np.ones((1, 1)), stride=3)
    assert strided.tolist() == [[0.0, 3.0, 6.0], [21.0, 24.0, 27.0], [42.0, 45.0, 48.0]]
    assert np.array_equal(correlate2d(image, np.array([[2.0]])), 2 * image)
