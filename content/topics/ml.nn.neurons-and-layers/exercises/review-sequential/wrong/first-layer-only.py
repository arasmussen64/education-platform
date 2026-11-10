import numpy as np


class Dense:
    def __init__(self, n_in, n_out, seed=0):
        rng = np.random.default_rng(seed)
        self.W = rng.standard_normal((n_in, n_out)) / np.sqrt(n_in)
        self.b = np.zeros(n_out)

    def forward(self, X):
        return X @ self.W + self.b

    def parameters(self):
        return [self.W, self.b]


class ReLU:
    def forward(self, X):
        return np.maximum(X, 0.0)

    def parameters(self):
        return []


class Sequential:
    """Layers run one after another; the output of each is the input of the next."""

    def __init__(self, layers):
        self.layers = layers

    def forward(self, X):
        for layer in self.layers:
            X = layer.forward(X)
        return X

    def parameters(self):
        return self.layers[0].parameters()


net = Sequential([Dense(3, 5, seed=3), ReLU(), Dense(5, 1, seed=4)])
print(net.forward(np.zeros((7, 3))).shape, sum(p.size for p in net.parameters()))
