import cProfile
import pstats

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


def calls_to(function, name, *args):
    """How many times the function called name runs while function(*args) runs, read from a cProfile table: the hot loop, found by its call count."""
    profiler = cProfile.Profile()
    profiler.enable()
    function(*args)
    profiler.disable()
    return sum(row[1] for (file, line, func), row in pstats.Stats(profiler).stats.items() if func == name)


def distance_squared(a, b):
    return float(((a - b) ** 2).sum())


def nearest_centroid_loop(X, centroids):
    """The pipeline's hot loop as first written: every row against every centroid, one call each."""
    labels = []
    for row in X:
        best, best_d = -1, float("inf")
        for j, c in enumerate(centroids):
            d = distance_squared(row, c)
            if d < best_d:
                best, best_d = j, d
        labels.append(best)
    return labels


X = np.array([[5.0, 1.0], [7.0, 2.0], [60.0, 9.0], [55.0, 8.0], [6.0, 1.0], [58.0, 9.0]])
centroids = np.array([[-0.8, -0.8], [0.9, 0.9]])
Z = standardize(X)
print(np.round(Z, 3).tolist(), bool(np.allclose(Z.mean(axis=0), 0)))
print(nearest_centroid(Z, centroids))
print(calls_to(nearest_centroid_loop, "distance_squared", Z, centroids), calls_to(nearest_centroid, "distance_squared", Z, centroids), calls_to(nearest_centroid_loop, "distance_squared", np.vstack([Z, Z]), centroids))
print(weekly(np.array([10, 30, 90, 127], dtype=np.int8)).tolist())
print(round(mean_loss(np.full(50_000, 0.3, dtype=np.float32)), 6))
print(np.round(softmax(np.array([[-1500.0, -1499.0], [0.0, 0.0]])), 3).tolist())
print(model_cost([2, 32, 4], 600, 8, 2))
