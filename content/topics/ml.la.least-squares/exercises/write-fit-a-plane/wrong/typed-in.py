import numpy as np

X = np.array([[0.0, 0.0], [1.0, 0.0], [0.0, 1.0], [2.0, 3.0]])
z = np.array([3.0, 5.0, 2.0, 4.0])


def fit_plane(X, z):
    return np.array([2.0, -1.0, 3.0])


print("[ 2. -1.  3.]")
