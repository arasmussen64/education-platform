import numpy as np

from checks import function, run


class Watched(np.ndarray):
    """An array that counts how often Python iterates over it, reads single elements from it, or turns a matrix into lists."""

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
        if self.ndim >= 2:
            Watched.elements += self.size
        return super().tolist()


def watched(a, dtype=np.float64):
    """A counting view of a, with the counts reset."""
    Watched.iterations = 0
    Watched.elements = 0
    return np.asarray(a, dtype=dtype).view(Watched)

EXPECTED = 'weekly: [140, 350, 700, 840]\nmean loss: 0.1\nsoftmax: [[0.269, 0.731], [0.269, 0.731]]\n'


def test_the_output():
    """Prints the weekly clicks, a mean of 0.1 and two finite softmax rows."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_weekly_widens():
    """An int8 127 gives 889 and a uint8 255 gives 1785."""
    weekly = function("weekly")
    assert list(weekly(np.array([127, 3], dtype=np.int8))) == [889, 21]
    assert list(weekly(np.array([255], dtype=np.uint8))) == [1785]


def test_mean_does_not_drift():
    """Two hundred thousand float32 tenths average to 0.1 within a millionth, with no Python loop over the array."""
    mean_loss = function("mean_loss")
    assert abs(mean_loss(np.full(200_000, 0.1, dtype=np.float32)) - 0.1) < 1e-6
    mean_loss(watched([0.5, 1.5, 2.5]))
    assert Watched.iterations == 0 and Watched.elements == 0


def test_softmax_stays_finite():
    """Logits of 5,000 and of -5,000 give finite rows that sum to 1."""
    softmax = function("softmax")
    P = softmax(np.array([[5000.0, 5001.0], [-5000.0, -5001.0]]))
    assert not np.isnan(P).any() and np.allclose(P.sum(axis=1), 1) and np.isclose(P[0, 1] / P[0, 0], np.e)
