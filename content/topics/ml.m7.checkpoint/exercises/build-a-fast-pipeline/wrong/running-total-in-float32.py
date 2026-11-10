import numpy as np


def standardize(X):
    """Each column minus its mean, over its standard deviation; a column with no spread becomes zeros."""
    spread = X.std(axis=0)
    return (X - X.mean(axis=0)) / np.where(spread == 0, 1.0, spread)


def nearest_centroid(X, centroids):
    """The index of the nearest centroid for every row, by squared distance, the first on a tie: one array operation, no Python loop."""
    squared = ((X[:, None, :] - centroids[None, :, :]) ** 2).sum(axis=2)
    return np.argmin(squared, axis=1).tolist()


def weekly(clicks):
    """Seven times the daily clicks, in an integer type wide enough to hold them whatever the column's dtype."""
    return clicks.astype(np.int64) * 7


def mean_loss(losses):
    """The mean, summed as one array operation and accumulated in float64, so a hundred thousand small values don't drift."""
    total = np.float32(0)
    for loss in losses:
        total += loss
    return float(total / len(losses))


def softmax(logits):
    """Row-wise softmax with the largest logit of each row subtracted first, so exp never overflows and no row becomes NaN."""
    shifted = np.exp(logits - logits.max(axis=1, keepdims=True))
    return shifted / shifted.sum(axis=1, keepdims=True)


def model_cost(layers, examples, batch, itemsize):
    """(parameters, training FLOPs, bytes): weights and biases per dense layer; 6 FLOPs per parameter per example; four copies of the parameters plus one batch of activations."""
    params = sum(i * o + o for i, o in zip(layers, layers[1:]))
    flops = 6 * params * examples
    bytes_needed = params * 4 * itemsize + batch * sum(layers) * itemsize
    return params, flops, bytes_needed


X = np.array([[1.0, 10.0], [2.0, 20.0], [3.0, 30.0], [6.0, 60.0]])
Z = standardize(X)
print(np.round(Z, 3).tolist(), bool(np.allclose(Z.mean(axis=0), 0)))
print(nearest_centroid(Z, np.array([[-1.0, -1.0], [1.5, 1.5]])))
print(weekly(np.array([20, 50, 100, 120], dtype=np.int8)).tolist())
print(round(mean_loss(np.full(100_000, 0.1, dtype=np.float32)), 6))
print(np.round(softmax(np.array([[1000.0, 1001.0], [1.0, 2.0]])), 3).tolist())
print(model_cost([4, 64, 32, 5], 400, 32, 4))
