import numpy as np


def fit_plane(points):
    A = np.column_stack([points[:, 0], points[:, 1]])
    return np.linalg.solve(A.T @ A, A.T @ points[:, 2])


def compress(points, k):
    mean = points.mean(axis=0)
    centered = points - mean
    C = centered.T @ centered / (len(points) - 1)
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
    [1.0, 2.0, 4.6],
    [2.0, 1.0, 5.4],
    [3.0, 4.0, 8.4],
    [4.0, 2.0, 9.1],
    [5.0, 5.0, 11.9],
    [6.0, 3.0, 12.6],
])
report(points)
