import numpy as np


def fit_plane(points):
    A = np.column_stack([points[:, 0], points[:, 1], np.ones(2)])
    return np.linalg.solve(A @ A.T, A.T @ points[:, 2])


def compress(points, k):
    mean = points.mean(axis=0)
    centered = points - mean
    C = points.T @ points / (len(points) - 1)
    values, vectors = np.linalg.eigh(C)
    order = np.argsort(values)[::-1]
    values = values[order]
    components = vectors[:, order[:k]]
    rebuilt = (centered @ components) @ components.T + mean
    return values / values.sum(), rebuilt


def report(points):
    coef = fit_plane(points)
    A = np.column_stack([points[:, 0], points[:, 1], np.ones(len(points))])
    print("plane", np.round(coef, 3))
    print("lstsq agrees", np.allclose(coef, np.linalg.lstsq(A, points[:, 2])[0]))
    shares, rebuilt = compress(points, 2)
    print("variance kept", round(float(shares[:2].sum()), 4))
    print("compression error", round(float(np.linalg.norm(points - rebuilt)), 3))


points = np.array([
    [0.0, 0.0, 3.1],
    [1.0, 0.0, 4.9],
    [0.0, 1.0, 2.05],
    [2.0, 3.0, 3.95],
    [3.0, 1.0, 8.1],
    [1.0, 2.0, 2.9],
])
report(points)
