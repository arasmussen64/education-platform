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
    """Prints the two agreements and the standardized matrix."""
    printed = run()
    assert printed == '[0.  0.  0.  1.5 3. ] True\n[[-1.    -1.066 -1.112]\n [-0.714 -0.671 -0.64 ]\n [ 0.143  0.197  0.236]\n [ 1.571  1.54   1.516]]\nTrue\n', f"Your program printed:\n{printed}"


def test_no_python_loop():
    """Neither function iterates over its array in Python or reads it one element at a time."""
    relu = function("relu")
    standardize = function("standardize")
    relu(watched([-1.0, 2.0, -3.0, 4.0]))
    assert Watched.iterations == 0 and Watched.elements == 0, "relu loops in Python"
    standardize(watched([[1.0, 2.0], [3.0, 5.0], [5.0, 11.0]]))
    assert Watched.iterations == 0 and Watched.elements == 0, "standardize loops in Python"


def test_other_shapes():
    """relu on a matrix, and standardize gives every column a mean of 0 and a spread of 1."""
    relu = function("relu")
    standardize = function("standardize")
    assert relu(np.array([[-1.0, 0.5], [2.0, -2.0]])).tolist() == [[0.0, 0.5], [2.0, 0.0]]
    Z = standardize(np.array([[1.0, 100.0, -3.0], [2.0, 50.0, 0.0], [6.0, 0.0, 3.0]]))
    assert np.allclose(Z.mean(axis=0), 0) and np.allclose(Z.std(axis=0), 1)
