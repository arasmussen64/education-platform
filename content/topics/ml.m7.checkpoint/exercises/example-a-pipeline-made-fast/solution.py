import cProfile
import pstats

import numpy as np


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


def nearest_centroid(X, centroids):
    """The same labels as one array operation: broadcasting makes every row-centroid difference at once."""
    squared = ((X[:, None, :] - centroids[None, :, :]) ** 2).sum(axis=2)
    return np.argmin(squared, axis=1).tolist()


def profile(function, *args):
    profiler = cProfile.Profile()
    profiler.enable()
    result = function(*args)
    profiler.disable()
    return result, pstats.Stats(profiler)


def calls(stats, name):
    return sum(row[1] for (file, line, func), row in stats.stats.items() if func == name)


rng = np.random.default_rng(0)
X = rng.standard_normal((400, 4))
centroids = np.array([[2.0, 2.0, 2.0, 2.0], [-2.0, -2.0, -2.0, -2.0], [2.0, -2.0, 2.0, -2.0], [-2.0, 2.0, -2.0, 2.0], [0.0, 0.0, 0.0, 0.0]])
slow, stats = profile(nearest_centroid_loop, X, centroids)
fast, fast_stats = profile(nearest_centroid, X, centroids)
print(f"the loop: {calls(stats, 'distance_squared'):,} calls to distance_squared for 400 rows | vectorized: {calls(fast_stats, 'distance_squared')} calls, same labels: {slow == fast}")
_, doubled = profile(nearest_centroid_loop, np.vstack([X, X]), centroids)
print(f"doubling the rows: {calls(doubled, 'distance_squared'):,} calls, {calls(doubled, 'distance_squared') / calls(stats, 'distance_squared'):.1f} times as many: linear in the rows either way; vectorizing changes the constant, not the order")

clicks = np.array([20, 50, 100, 120], dtype=np.int8)
print("weekly clicks from an int8 column:", (clicks * 7).tolist(), "| widened to int64 first:", (clicks.astype(np.int64) * 7).tolist())

losses = np.full(100_000, 0.1, dtype=np.float32)
total = np.float32(0)
for loss in losses:
    total += loss
print(f"mean loss from a float32 running total: {float(total) / len(losses):.6f} | summed in float64: {float(losses.sum(dtype=np.float64)) / len(losses):.6f}")

logits = np.array([[1000.0, 1001.0], [1.0, 2.0]])
with np.errstate(over="ignore", invalid="ignore"):
    naive = np.exp(logits) / np.exp(logits).sum(axis=1, keepdims=True)
shifted = np.exp(logits - logits.max(axis=1, keepdims=True))
stable = shifted / shifted.sum(axis=1, keepdims=True)
print("softmax of a logit of 1,000: naive has NaN:", bool(np.isnan(naive).any()), "| stable rows sum to 1:", bool(np.allclose(stable.sum(axis=1), 1)), "| first row:", np.round(stable[0], 3).tolist())

LAYERS = [4, 64, 32, 5]
params = sum(i * o + o for i, o in zip(LAYERS, LAYERS[1:]))
print(f"the model the pipeline feeds, layers {LAYERS}: {params:,} parameters, {6 * params * 400:,} FLOPs to train on the 400 rows, {params * 16 + sum(LAYERS) * 32 * 4:,} bytes of state and activations at a batch of 32")
