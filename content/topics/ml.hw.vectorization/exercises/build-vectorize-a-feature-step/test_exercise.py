import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


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
    """Prints the four lines."""
    assert run() == '[2.  3.5 5.  6.5]\n[[-1.342 -1.342 -1.342]\n [-0.447 -0.447 -0.447]\n [ 0.447  0.447  0.447]\n [ 1.342  1.342  1.342]]\n[0.  0.  2.5] [1. 3. 3. 5. 5.]\n[[0.    0.5   1.   ]\n [1.5   2.25  3.   ]\n [3.75  4.625 5.5  ]\n [6.375 7.312 8.25 ]]\n'


def test_against_loops():
    """Each function agrees with a plain loop on a 5 by 4 matrix."""
    predict = function("predict")
    standardize = function("standardize")
    relu = function("relu")
    running_max = function("running_max")
    ema = function("ema")
    X = (np.arange(20, dtype=np.float64).reshape(5, 4) * 1.5 - 7) ** 2 / 3
    w = np.array([0.5, -2.0, 1.0, 0.25])
    assert np.allclose(predict(X, w, -1.0), [sum(row[j] * w[j] for j in range(4)) - 1.0 for row in X])
    expected = np.empty_like(X)
    for j in range(4):
        column = X[:, j]
        expected[:, j] = (column - column.mean()) / column.std()
    assert np.allclose(standardize(X), expected)
    assert np.allclose(relu(X - 20), [[max(v - 20, 0.0) for v in row] for row in X])
    assert np.allclose(running_max(X[:, 1]), [max(X[: i + 1, 1]) for i in range(5)])
    state, rows = np.zeros(4), []
    for row in X:
        state = 0.3 * row + 0.7 * state
        rows.append(state.copy())
    assert np.allclose(ema(X, 0.3), rows)


def test_no_python_loops():
    """predict, standardize, relu and running_max never iterate in Python or read single elements; ema never reads single elements."""
    predict = function("predict")
    standardize = function("standardize")
    relu = function("relu")
    running_max = function("running_max")
    ema = function("ema")
    rows = [[1.0, 2.0, 3.0], [4.0, 6.0, 8.0], [0.0, -1.0, 5.0]]
    predict(watched(rows), np.array([1.0, 0.5, -1.0]), 0.0)
    assert Watched.iterations == 0 and Watched.elements == 0
    standardize(watched(rows))
    assert Watched.iterations == 0 and Watched.elements == 0
    relu(watched([-1.0, 2.0, -3.0]))
    assert Watched.iterations == 0 and Watched.elements == 0
    running_max(watched([1.0, 0.0, 2.0]))
    assert Watched.iterations == 0 and Watched.elements == 0
    ema(watched(rows), 0.5)
    assert Watched.elements == 0


def test_no_spread():
    """A constant column standardizes to zeros, not NaN, and the other columns are unaffected."""
    standardize = function("standardize")
    Z = standardize(np.array([[3.0, 1.0], [3.0, 2.0], [3.0, 6.0]]))
    assert not np.isnan(Z).any() and np.allclose(Z[:, 0], 0) and np.allclose(Z[:, 1].std(), 1)
