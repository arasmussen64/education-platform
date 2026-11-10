import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


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
    """Prints the six lines."""
    assert run() == '[[-1.069, -1.069], [-0.535, -0.535], [0.0, 0.0], [1.604, 1.604]] True\n[0, 0, 0, 1]\n[140, 350, 700, 840]\n0.1\n[[0.269, 0.731], [0.269, 0.731]]\n(2565, 6156000, 54480)\n'


def test_standardize():
    """Every column ends at mean 0 and spread 1, a constant column becomes zeros, and no Python loop touches the array."""
    standardize = function("standardize")
    Z = standardize(np.array([[1.0, 100.0, 3.0], [2.0, 50.0, 3.0], [6.0, 0.0, 3.0], [7.0, 10.0, 3.0]]))
    assert np.allclose(Z[:, :2].mean(axis=0), 0) and np.allclose(Z[:, :2].std(axis=0), 1)
    assert not np.isnan(Z).any() and np.allclose(Z[:, 2], 0)
    standardize(watched([[1.0, 2.0], [3.0, 5.0], [5.0, 11.0]]))
    assert Watched.iterations == 0 and Watched.elements == 0


def test_nearest_centroid():
    """Agrees with a plain loop on 60 random rows and 4 centroids, keeps the first centroid on a tie, and never iterates in Python."""
    nearest_centroid = function("nearest_centroid")
    rng = np.random.default_rng(7)
    X = rng.standard_normal((60, 3))
    centroids = rng.standard_normal((4, 3)) * 2
    expected = []
    for row in X:
        distances = [float(((row - c) ** 2).sum()) for c in centroids]
        expected.append(distances.index(min(distances)))
    assert list(nearest_centroid(X, centroids)) == expected
    assert list(nearest_centroid(np.array([[0.0, 0.0]]), np.array([[1.0, 0.0], [-1.0, 0.0]]))) == [0]
    nearest_centroid(watched(X), centroids)
    assert Watched.iterations == 0 and Watched.elements == 0


def test_weekly():
    """An int8 column of 127 gives 889, a uint8 column of 255 gives 1785, and the result holds them."""
    weekly = function("weekly")
    assert list(weekly(np.array([127, 20], dtype=np.int8))) == [889, 140]
    assert list(weekly(np.array([255, 1], dtype=np.uint8))) == [1785, 7]
    assert weekly(np.array([1], dtype=np.int8)).dtype.itemsize >= 4


def test_mean_loss():
    """A hundred thousand float32 tenths average to 0.1 within a millionth, with no Python loop over them."""
    mean_loss = function("mean_loss")
    assert abs(mean_loss(np.full(100_000, 0.1, dtype=np.float32)) - 0.1) < 1e-6
    assert abs(mean_loss(np.array([1.0, 2.0, 6.0])) - 3.0) < 1e-12
    mean_loss(watched([0.5, 1.5, 2.5]))
    assert Watched.iterations == 0 and Watched.elements == 0


def test_softmax():
    """Logits of 5,000 and of -5,000 give finite rows that sum to 1 with the right ratios, and no Python loop runs."""
    softmax = function("softmax")
    P = softmax(np.array([[5000.0, 5001.0, 4999.0], [-5000.0, -5001.0, -5000.0], [0.0, 0.0, 0.0]]))
    assert not np.isnan(P).any() and np.allclose(P.sum(axis=1), 1)
    assert np.isclose(P[0, 1] / P[0, 0], np.e) and np.allclose(P[2], 1 / 3)
    softmax(watched([[1.0, 2.0], [3.0, 1.0]]))
    assert Watched.iterations == 0 and Watched.elements == 0


def test_model_cost():
    """[4, 3, 2] is 23 parameters; 10 examples cost 1,380 FLOPs; a batch of 2 in float16 needs 23 * 8 + 2 * 9 * 2 bytes."""
    model_cost = function("model_cost")
    assert tuple(model_cost([4, 3, 2], 10, 2, 2)) == (23, 1380, 23 * 8 + 2 * 9 * 2)
    assert tuple(model_cost([5, 1], 1, 1, 4)) == (6, 36, 6 * 16 + 6 * 4)
