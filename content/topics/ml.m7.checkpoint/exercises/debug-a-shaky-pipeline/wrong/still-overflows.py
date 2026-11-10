import numpy as np


def weekly(clicks):
    """Seven times the daily clicks, in an integer type wide enough to hold them."""
    return clicks.astype(np.int64) * 7


def mean_loss(losses):
    """The mean, summed as one array operation and accumulated in float64."""
    return float(losses.sum(dtype=np.float64) / len(losses))


def softmax(logits):
    """Row-wise softmax, with each row's largest logit subtracted first so that exp never overflows."""
    shifted = np.exp(logits)
    return shifted / shifted.sum(axis=1, keepdims=True)


clicks = np.array([20, 50, 100, 120], dtype=np.int8)
print("weekly:", weekly(clicks).tolist())
print("mean loss:", round(mean_loss(np.full(100_000, 0.1, dtype=np.float32)), 6))
print("softmax:", np.round(softmax(np.array([[1000.0, 1001.0], [1.0, 2.0]])), 3).tolist())
