import numpy as np


class Dense:
    """W is (inputs, outputs), so a batch of shape (rows, inputs) times W is (rows, outputs)."""

    def __init__(self, n_in, n_out, seed=0):
        rng = np.random.default_rng(seed)
        self.W = rng.standard_normal((n_in, n_out)) / np.sqrt(n_in)
        self.b = np.zeros(n_out)

    def forward(self, X):
        return X @ self.W + self.b


class ReLU:
    """Zero below zero, unchanged above."""

    def forward(self, X):
        return np.maximum(X, 0.0)


class Sequential:
    def __init__(self, layers):
        self.layers = layers

    def forward(self, X):
        for layer in self.layers:
            X = layer.forward(X)
        return X


net = Sequential([Dense(3, 4, seed=1), ReLU(), Dense(4, 2, seed=2)])
X = np.array([[1.0, -2.0, 0.5], [0.0, 1.0, 1.0]])
print("output shape:", net.forward(X).shape)
hidden = net.layers[1].forward(net.layers[0].forward(X))
print("hidden values are never negative:", bool((hidden >= 0).all()), "| some are zero:", bool((hidden == 0).any()))
