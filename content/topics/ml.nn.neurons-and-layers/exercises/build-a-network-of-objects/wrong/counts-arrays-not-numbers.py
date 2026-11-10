import numpy as np


class Dense:
    """A layer of neurons: every output is a weighted sum of every input plus a bias. W is (inputs, outputs)."""

    def __init__(self, n_in, n_out, seed=0):
        rng = np.random.default_rng(seed)
        self.W = rng.standard_normal((n_in, n_out)) / np.sqrt(n_in)
        self.b = np.zeros(n_out)

    def forward(self, X):
        return X @ self.W + self.b

    def parameters(self):
        return [self.W, self.b]


class ReLU:
    """Keeps the positive part of every value and zeroes the rest; it has nothing to learn."""

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
        return [p for layer in self.layers for p in layer.parameters()]


def count_parameters(net):
    """How many numbers the network can learn."""
    return len(net.parameters())


def shapes_through(net, X):
    """The shape of the batch after each layer, in order."""
    shapes = []
    for layer in net.layers:
        X = layer.forward(X)
        shapes.append(X.shape)
    return shapes


net = Sequential([Dense(35, 16, seed=1), ReLU(), Dense(16, 10, seed=2)])
X = np.random.default_rng(0).standard_normal((8, 35))
print(shapes_through(net, X), count_parameters(net))
hand = Dense(2, 3)
hand.W, hand.b = np.array([[0.5, -1.0, 0.2], [-0.25, 0.5, 0.4]]), np.array([0.1, -0.3, -0.5])
tiny = Sequential([hand, ReLU()])
print(np.round(tiny.forward(np.array([[1.0, 2.0], [-1.0, 1.0]])), 2).tolist())
first, second = Dense(35, 16, seed=1), Dense(16, 10, seed=2)
merged = Dense(35, 10)
merged.W, merged.b = first.W @ second.W, first.b @ second.W + second.b
print(np.allclose(Sequential([first, second]).forward(X), merged.forward(X)), np.allclose(net.forward(X), merged.forward(X)))
