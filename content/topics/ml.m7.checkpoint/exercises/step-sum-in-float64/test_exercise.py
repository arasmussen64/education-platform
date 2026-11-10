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


def test_the_output():
    """Prints 0.1."""
    printed = run()
    assert printed == '0.1\n', f"Your program printed:\n{printed}"


def test_no_drift_and_no_loop():
    """Two hundred thousand tenths average to 0.1 within a millionth, three values average to 3, and no Python loop runs."""
    mean_loss = function("mean_loss")
    assert abs(mean_loss(np.full(200_000, 0.1, dtype=np.float32)) - 0.1) < 1e-6
    assert abs(mean_loss(np.array([1.0, 2.0, 6.0])) - 3.0) < 1e-12
    mean_loss(watched([0.5, 1.5, 2.5]))
    assert Watched.iterations == 0 and Watched.elements == 0
