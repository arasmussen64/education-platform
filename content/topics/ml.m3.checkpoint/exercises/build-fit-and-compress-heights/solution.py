import numpy as np


def fit_plane(points):
    A = np.column_stack([points[:, 0], points[:, 1], np.ones(len(points))])
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
    [160.0, 30.0, 26.2],
    [170.0, 40.0, 32.8],
    [180.0, 25.0, 35.1],
    [165.0, 50.0, 32.4],
    [175.0, 35.0, 34.6],
    [185.0, 45.0, 41.3],
])
report(points)
