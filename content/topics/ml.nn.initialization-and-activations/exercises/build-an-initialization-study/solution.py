import numpy as np


class Dense:
    """A dense layer whose starting weights are standard normals times a scale (1 / sqrt(n_in) unless told otherwise)."""

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


class Tanh:
    def forward(self, X):
        self.out = np.tanh(X)
        return self.out

    def backward(self, grad_out):
        return grad_out * (1 - self.out ** 2)

    def parameters(self):
        return []

    def gradients(self):
        return []


class Sigmoid:
    def forward(self, X):
        self.out = 1 / (1 + np.exp(-X))
        return self.out

    def backward(self, grad_out):
        return grad_out * self.out * (1 - self.out)

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


class MSELoss:
    def forward(self, pred, target):
        self.diff = pred - target
        return float(np.mean(self.diff ** 2))

    def backward(self):
        return 2 * self.diff / self.diff.size


def describe(std):
    """A size in words: the words are the same on every machine even when the last digits aren't."""
    if std < 1e-3:
        return "vanished"
    if std > 1e3:
        return "exploded"
    if 0.1 <= std <= 10:
        return "stable"
    return "drifting"


def xavier_scale(n_in):
    """The starting scale that keeps a tanh or sigmoid layer's signal the same size: 1 / sqrt(n_in)."""
    return float(np.sqrt(1 / n_in))


def he_scale(n_in):
    """The starting scale that keeps a ReLU layer's signal the same size, since ReLU zeroes half: sqrt(2 / n_in)."""
    return float(np.sqrt(2 / n_in))


def activation_stds(net, X):
    """The std of the batch after each layer of the network, in order."""
    stds = []
    for layer in net.layers:
        X = layer.forward(X)
        stds.append(float(X.std()))
    return stds


def input_gradient_std(net, X):
    """Run forward, push a unit-size gradient (standard normals, seed 1) back through the network, and return the std of what reaches the input."""
    out = net.forward(X)
    grad_in = net.backward(np.random.default_rng(1).standard_normal(out.shape))
    return float(grad_in.std())


def dead_fraction(H):
    """The share of ReLU units (columns) that are zero for every input in the batch."""
    return float((H.max(axis=0) == 0).mean())


def saturated_fraction(Z, threshold=4.0):
    """The share of pre-activations beyond the threshold in size."""
    return float((np.abs(Z) > threshold).mean())


def units_identical(W):
    """Whether every column of W is the same column: the symmetry that zero or copied starting weights never break."""
    return bool(np.allclose(W, W[:, :1]))


rng = np.random.default_rng(0)
X = rng.standard_normal((256, 100))


def stack(scale, activation, depth=8):
    return Sequential([piece for i in range(depth) for piece in (Dense(100, 100, seed=i, scale=scale), activation())])


print(xavier_scale(100), he_scale(100), he_scale(50))
for name, scale, activation in (("0.01 tanh", 0.01, Tanh), ("Xavier tanh", xavier_scale(100), Tanh), ("0.1 ReLU", 0.1, ReLU), ("He ReLU", he_scale(100), ReLU)):
    net = stack(scale, activation)
    stds = activation_stds(net, X)
    print(name, describe(stds[-1]), describe(input_gradient_std(net, X)))
layer = Dense(100, 100, seed=3, scale=he_scale(100))
layer.b[:] = -5.0
print(round(dead_fraction(ReLU().forward(layer.forward(X))), 2), round(saturated_fraction(Dense(100, 100, seed=0, scale=1.0).forward(X)), 2))
print(units_identical(np.zeros((3, 4))), units_identical(np.tile(np.array([[1.0], [2.0]]), (1, 5))), units_identical(Dense(3, 4, seed=1).W))
