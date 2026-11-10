import numpy as np

X = np.array([[0.0, 0.0], [1.0, 0.0], [0.0, 1.0], [2.0, 3.0]])
z = np.array([3.0, 5.0, 2.0, 4.0])


def fit_plane(X, z):
    A = np.column_stack([X, np.ones(len(z))])
    return np.linalg.lstsq(A, z)[0]


print(np.round(fit_plane(X, z), 6) + 0.0)
