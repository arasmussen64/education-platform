import numpy as np


def pca(X, k):
    mean = X.mean(axis=0)
    centered = X - mean
    C = centered.T @ centered / (len(X) - 1)
    values, vectors = np.linalg.eigh(C)
    components = vectors[:, :k]
    components = components * np.sign(components[0])
    return centered @ components, components, values / values.sum()


def reconstruct(scores, components, mean):
    return scores @ components.T + mean


X = np.array([[2.0, 1.0], [3.0, 2.0], [4.0, 2.0], [5.0, 4.0], [6.0, 4.0], [7.0, 5.0]])
scores, components, explained = pca(X, 1)
print(np.round(explained, 3))
rebuilt = reconstruct(scores, components, X.mean(axis=0))
print(round(float(np.linalg.norm(X - rebuilt)), 3))
