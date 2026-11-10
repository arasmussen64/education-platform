import numpy as np

from checks import function, run


class Watched(np.ndarray):
    """An array that counts how often Python iterates over it or reads single elements from it."""

    iterations = 0
    elements = 0

    def __iter__(self):
        Watched.iterations += 1
        return super().__iter__()

    def __getitem__(self, key):
        result = super().__getitem__(key)
        if np.ndim(result) == 0:
            Watched.elements += 1
        return result

    def tolist(self):
        Watched.elements += self.size
        return super().tolist()


def watched(a):
    """A counting view of a, with the counts reset."""
    Watched.iterations = 0
    Watched.elements = 0
    return np.asarray(a, dtype=np.float64).view(Watched)


def test_the_output():
    """Prints the standardized matrix and two Trues."""
    assert run() == '[[-1.069 -1.069]\n [-0.535 -0.535]\n [ 0.     0.   ]\n [ 1.604  1.604]]\nTrue True\n'


def test_no_python_loop():
    """standardize never iterates in Python or reads single elements, and handles a 3 by 3 matrix."""
    standardize = function("standardize")
    Z = standardize(watched([[1.0, 2.0, 0.0], [3.0, 5.0, 1.0], [5.0, 11.0, 8.0]]))
    assert Watched.iterations == 0 and Watched.elements == 0
    assert np.allclose(np.asarray(Z).mean(axis=0), 0) and np.allclose(np.asarray(Z).std(axis=0), 1)
