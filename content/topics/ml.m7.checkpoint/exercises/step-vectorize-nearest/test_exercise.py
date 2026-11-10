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
    """Prints the four labels."""
    printed = run()
    assert printed == '[0, 1, 1, 0]\n', f"Your program printed:\n{printed}"


def test_agrees_with_a_loop():
    """Matches a plain loop on 40 random rows and 3 centroids, and never iterates over the rows in Python."""
    nearest_centroid = function("nearest_centroid")
    rng = np.random.default_rng(3)
    X = rng.standard_normal((40, 2))
    centroids = rng.standard_normal((3, 2)) * 2
    expected = []
    for row in X:
        distances = [float(((row - c) ** 2).sum()) for c in centroids]
        expected.append(distances.index(min(distances)))
    assert list(nearest_centroid(X, centroids)) == expected
    nearest_centroid(watched(X), centroids)
    assert Watched.iterations == 0 and Watched.elements == 0
