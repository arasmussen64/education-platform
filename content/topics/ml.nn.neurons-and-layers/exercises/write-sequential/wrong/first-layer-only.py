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


net = Sequential([Dense(4, 8, seed=1), ReLU(), Dense(8, 2, seed=2)])
X = np.ones((6, 4))
print(net.forward(X).shape, [p.shape for p in net.parameters()], sum(p.size for p in net.parameters()))
by_hand = net.layers[2].forward(net.layers[1].forward(net.layers[0].forward(X)))
print(np.allclose(net.forward(X), by_hand))
