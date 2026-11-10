import numpy as np

X = np.array([[1.0, 2.0]])
W1 = np.array([[1.0, -1.0], [0.0, 1.0]])
b1 = np.array([0.0, -1.0])
W2 = np.array([2.0, -1.0])
b2 = 0.5


def forward(X, W1, b1, W2, b2):
    h = X @ W1 + b1
    return 1 / (1 + np.exp(-(h @ W2 + b2)))


print(np.round(forward(X, W1, b1, W2, b2), 3))
