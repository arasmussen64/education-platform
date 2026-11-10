import numpy as np


def sigmoid(z):
    return 1 / (1 + np.exp(-z))


X = np.array([[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]])
y = np.array([0.0, 1.0, 1.0, 0.0])
W1 = np.array([[0.3, 0.8, 0.3, -1.3], [0.9, 0.4, -0.5, 0.6]])
b1 = np.array([0.2, 0.1, 0.1, 0.3])
W2 = np.array([-0.7, -0.2, -0.5, 0.6])
b2 = 0.0


def forward(X, W1, b1, W2, b2):
    z1 = X @ W1 + b1
    h = np.maximum(z1, 0.0)
    p = sigmoid(h @ W2 + b2)
    return z1, h, p


def loss(p, y):
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


def backward(X, y, W2, z1, h, p):
    dz2 = (p - y) / len(y)
    dW2 = h.T @ dz2
    db2 = dz2.sum()
    dh = np.outer(dz2, W2)
    dz1 = dh * (z1 > 0)
    dW1 = X.T @ dz1
    db1 = dz1.sum(axis=0)
    return dW1, db1, dW2, db2


def numeric_dW1():
    grad = np.zeros_like(W1)
    for i in range(2):
        for j in range(4):
            step = np.zeros_like(W1)
            step[i, j] = 1e-6
            up = loss(forward(X, W1 + step, b1, W2, b2)[2], y)
            down = loss(forward(X, W1 - step, b1, W2, b2)[2], y)
            grad[i, j] = (up - down) / 2e-6
    return grad


z1, h, p = forward(X, W1, b1, W2, b2)
dW1, db1, dW2, db2 = backward(X, y, W2, z1, h, p)
print(np.round(dW2, 3))
print(np.round(dW1, 3))
print(np.allclose(dW1, numeric_dW1(), atol=1e-6))
