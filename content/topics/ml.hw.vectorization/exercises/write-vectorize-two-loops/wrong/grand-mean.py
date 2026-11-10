import numpy as np


def relu_loop(x):
    out = np.empty_like(x)
    for i in range(len(x)):
        out[i] = x[i] if x[i] > 0 else 0.0
    return out


def standardize_loop(X):
    out = np.empty_like(X)
    for j in range(X.shape[1]):
        column = X[:, j]
        mean = sum(column) / len(column)
        spread = (sum((value - mean) ** 2 for value in column) / len(column)) ** 0.5
        for i in range(X.shape[0]):
            out[i, j] = (X[i, j] - mean) / spread
    return out


def relu(x):
    """x where positive, 0 elsewhere: one mask, one choice."""
    return np.where(x > 0, x, 0.0)


def standardize(X):
    """Each column minus its mean, divided by its standard deviation; broadcasting stretches the (3,) rows of means over the (4, 3) matrix."""
    return (X - X.mean()) / X.std()


x = np.array([-2.0, -0.5, 0.0, 1.5, 3.0])
X = np.arange(12, dtype=np.float64).reshape(4, 3) ** 2
print(relu(x), np.allclose(relu(x), relu_loop(x)))
print(np.round(standardize(X), 3))
print(np.allclose(standardize(X), standardize_loop(X)))
