import numpy as np


def max_pool(X, size=2):
    """Pool every image in X (n, h, w) over size-by-size windows: the pooled array (n, h // size, w // size) and a boolean mask of where each window's maximum sat."""
    n, h, w = X.shape
    windows = X.reshape(n, h // size, size, w // size, size)
    pooled = windows.mean(axis=(2, 4))
    mask = windows == pooled[:, :, None, :, None]
    return pooled, mask


def max_pool_backward(mask, grad_out):
    """Send each pooled cell's gradient back to the cell that won its window; every other cell gets zero."""
    n, h_out, size, w_out, _ = mask.shape
    return (mask * grad_out[:, :, None, :, None]).reshape(n, h_out * size, w_out * size)


X = np.array([[[2.0, 7.0, 1.0, 0.0], [4.0, 3.0, 5.0, 8.0], [0.0, 1.0, 9.0, 2.0], [6.0, 0.0, 3.0, 3.0]]])
pooled, mask = max_pool(X)
print(pooled[0].tolist())
print(max_pool_backward(mask, np.array([[[1.0, 2.0], [3.0, 4.0]]]))[0].tolist())
