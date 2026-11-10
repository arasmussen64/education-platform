import numpy as np


def weekly(clicks):
    """Seven times the daily clicks: widen the column to int64 before multiplying, whatever dtype it arrived in."""
    return clicks.astype(...) * 7


clicks = np.array([20, 50, 100, 120], dtype=np.int8)
print(weekly(clicks).tolist(), weekly(clicks).dtype)
