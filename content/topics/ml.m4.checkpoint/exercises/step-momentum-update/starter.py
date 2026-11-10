import numpy as np

g = np.array([-1.5, -0.5, 0.5, 1.5])
X = np.array([[a, b] for a in g for b in g])
y = (X[:, 0] ** 2 + X[:, 1] ** 2 < 1).astype(float)
params = {
    "W1": np.array([[0.2, -0.4, -0.3, -2.0], [1.4, 0.9, -0.3, 0.6]]),
    "b1": np.array([0.1, -0.2, 0.25, -0.15]),
    "W2": np.array([-0.3, -0.6, 0.4, -0.1]),
    "b2": np.array(0.0),
}


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
            vel[key] = ... * vel[key] + grads[key]
            params[key] = params[key] - ... * vel[key]
    return losses


losses = train(X, y, params, 0.1, 0.9, 300)
print(round(losses[0], 3), round(losses[-1], 3))
print(np.round(params["W2"], 3))
