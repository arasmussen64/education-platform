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
    dz1 = dh * h
    dW1 = X @ dz1
    db1 = dz1.sum(axis=0)
    return dW1, db1, dW2, db2


for step in range(1000):
    z1, h, p = forward(X, W1, b1, W2, b2)
    if step == 0:
        print("start", round(loss(p, y), 3))
    dW1, db1, dW2, db2 = backward(X, y, W2, z1, h, p)
    W1 = W1 - 0.5 * dW1
    b1 = b1 - 0.5 * db1
    W2 = W2 - 0.5 * dW2
    b2 = b2 - 0.5 * db2
z1, h, p = forward(X, W1, b1, W2, b2)
print("end", round(loss(p, y), 3))
print("predictions", np.round(p, 2))
