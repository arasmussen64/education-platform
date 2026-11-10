import numpy as np


class Dense:
    def __init__(self, n_in, n_out, seed=0, scale=None):
        rng = np.random.default_rng(seed)
        self.scale = 1 / np.sqrt(n_in) if scale is None else scale
        self.W = rng.standard_normal((n_in, n_out)) * self.scale
        self.b = np.zeros(n_out)
        self.dW = np.zeros_like(self.W)
        self.db = np.zeros_like(self.b)

    def forward(self, X):
        self.X = X
        return X @ self.W + self.b

    def backward(self, grad_out):
        self.dW = self.X.T @ grad_out
        self.db = grad_out.sum(axis=0)
        return grad_out @ self.W.T

    def parameters(self):
        return [self.W, self.b]

    def gradients(self):
        return [self.dW, self.db]


class ReLU:
    def forward(self, X):
        self.mask = X > 0
        return np.maximum(X, 0.0)

    def backward(self, grad_out):
        return grad_out * self.mask

    def parameters(self):
        return []

    def gradients(self):
        return []


class Sequential:
    def __init__(self, layers):
        self.layers = layers

    def forward(self, X):
        for layer in self.layers:
            X = layer.forward(X)
        return X

    def backward(self, grad):
        for layer in reversed(self.layers):
            grad = layer.backward(grad)
        return grad

    def parameters(self):
        return [p for layer in self.layers for p in layer.parameters()]

    def gradients(self):
        return [g for layer in self.layers for g in layer.gradients()]


def dead_units(net, X):
    """How many ReLU units output 0 on every row of X: no gradient reaches them, so they can never recover."""
    net.forward(X)
    return sum(int((~layer.mask.any(axis=0)).sum()) for layer in net.layers if isinstance(layer, ReLU))


rng = np.random.default_rng(0)
X = rng.standard_normal((50, 2))
net = Sequential([Dense(2, 16, seed=1), ReLU(), Dense(16, 16, seed=2), ReLU(), Dense(16, 3, seed=3)])
print(dead_units(net, X))
net.layers[0].b[:4] = -20.0
net.layers[2].b[:] = -20.0
print(dead_units(net, X))
