import numpy as np


def standardize(X):
    """Each column minus its mean, over its standard deviation; a column with no spread becomes zeros."""
    spread = X.std(axis=0)
    return (X - X.mean(axis=0)) / np.where(spread == 0, 1.0, spread)


def nearest_centroid(X, centroids):
    """The index of the nearest centroid for every row, by squared distance, the first on a tie: one array operation, no Python loop."""
    labels = []
    for row in X:
        best, best_d = -1, float("inf")
        for j, c in enumerate(centroids):
            d = float(((row - c) ** 2).sum())
            if d < best_d:
                best, best_d = j, d
        labels.append(best)
    return labels


def weekly(clicks):
    """Seven times the daily clicks, in an integer type wide enough to hold them whatever the column's dtype."""
    return clicks.astype(np.int64) * 7


def mean_loss(losses):
    """The mean, summed as one array operation and accumulated in float64, so a hundred thousand small values don't drift."""
    return float(losses.sum(dtype=np.float64) / len(losses))


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


X = np.array([[18.0, 40.0], [19.0, 42.0], [21.0, 45.0], [30.0, 80.0], [31.0, 85.0]])
Z = standardize(X)
print(np.round(Z, 3).tolist(), bool(np.allclose(Z.std(axis=0), 1)))
print(nearest_centroid(Z, np.array([[-0.5, -0.5], [1.5, 1.5]])))
print(weekly(np.array([24, 48, 96, 120], dtype=np.int8)).tolist())
print(round(mean_loss(np.full(100_000, 0.1, dtype=np.float32)), 6))
print(np.round(softmax(np.array([[2000.0, 2000.0, 2001.0]])), 3).tolist())
print(model_cost([2, 16, 8, 3], 500, 16, 4))
