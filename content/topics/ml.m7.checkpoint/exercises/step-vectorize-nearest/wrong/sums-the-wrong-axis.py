import numpy as np


def nearest_centroid(X, centroids):
    """The index of the nearest centroid for every row, as one array operation: broadcasting makes every row-centroid difference at once."""
    squared = ((X[:, None, :] - centroids[None, :, :]) ** 2).sum(axis=0)
    return np.argmin(squared, axis=1).tolist()


X = np.array([[0.0, 0.0], [5.0, 5.0], [4.0, 6.0], [-1.0, 1.0]])
centroids = np.array([[0.0, 1.0], [5.0, 6.0]])
print(nearest_centroid(X, centroids))
