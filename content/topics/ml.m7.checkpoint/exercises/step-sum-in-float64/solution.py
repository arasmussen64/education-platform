import numpy as np


def mean_loss(losses):
    """Sum as one array operation, accumulating in float64, then divide: no running total, no drift."""
    return float(losses.sum(dtype=np.float64) / len(losses))


losses = np.full(100_000, 0.1, dtype=np.float32)
print(round(mean_loss(losses), 6))
