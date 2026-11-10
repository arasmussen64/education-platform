import numpy as np


def sigmoid(z):
    return 1 / (1 + np.exp(-z))


def forward(X, params):
    z1 = X @ params["W1"] + params["b1"]
    h = np.maximum(z1, 0.0)
    p = sigmoid(h @ params["W2"] + params["b2"])
    return z1, h, p


def loss(p, y):
    p = np.clip(p, 1e-12, 1 - 1e-12)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


def backward(X, y, params, z1, h, p):
    dz2 = (p - y) / len(y)
    dh = np.outer(dz2, params["W2"])
    dz1 = dh * (z1 > 0)
    return {"W1": X.T @ dz1, "b1": dz1.sum(axis=0), "W2": h.T @ dz2, "b2": dz2.sum()}


def train(X, y, params, rate, beta, steps):
    vel = {key: np.zeros_like(value) for key, value in params.items()}
    losses = []
    for step in range(steps):
        z1, h, p = forward(X, params)
        losses.append(loss(p, y))
        grads = backward(X, y, params, z1, h, p)
        for key in params:
            vel[key] = beta * vel[key] + grads[key]
            params[key] = params[key] - rate * vel[key]
    return losses


X = np.array([[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]])
y = np.array([0.0, 1.0, 1.0, 0.0])
params = {
    "W1": np.array([[0.3, 0.8, 0.3, -1.3], [0.9, 0.4, -0.5, 0.6]]),
    "b1": np.array([0.2, 0.1, 0.1, 0.3]),
    "W2": np.array([-0.7, -0.2, -0.5, 0.6]),
    "b2": np.array(0.0),
}
losses = train(X, y, params, 0.1, 0.9, 500)
print("loss", round(losses[0], 3), round(losses[100], 3), round(losses[-1], 3))
p = forward(X, params)[2]
print("accuracy", np.mean((p > 0.5) == (y == 1)))
print("classes", (p > 0.5).astype(int))
