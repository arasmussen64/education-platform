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


X = np.array([[1.0, 2.0, 0.5], [0.0, 1.0, -1.0], [2.0, -1.0, 0.0], [-1.0, 0.5, 1.5], [0.5, 0.5, 0.5], [-2.0, 1.0, 1.0]])
y = np.array([[1.0], [0.0], [1.0], [0.0], [1.0], [0.0]])


def train(net, steps=200, rate=0.1):
    loss = MSELoss()
    for _ in range(steps):
        loss.forward(net.forward(X), y)
        net.backward(loss.backward())
        for param, grad in zip(net.parameters(), net.gradients()):
            param -= rate * grad
    return round(loss.forward(net.forward(X), y), 3)


zeros = Sequential([Dense(3, 4, scale=0.0), ReLU(), Dense(4, 1, scale=0.0)])
clones = Sequential([Dense(3, 4, seed=1), ReLU(), Dense(4, 1, seed=2)])
clones.layers[0].W[:] = clones.layers[0].W[:, :1]
clones.layers[2].W[:] = clones.layers[2].W[0, 0]
random = Sequential([Dense(3, 4, seed=1), ReLU(), Dense(4, 1, seed=2)])
for name, net in (("all zeros", zeros), ("four copies of one unit", clones), ("random", random)):
    final = train(net)
    W1 = net.layers[0].W
    print(f"start {name}: loss after 200 steps {final} | hidden units identical: {bool(np.allclose(W1, W1[:, :1]))}")

rng = np.random.default_rng(0)
X_deep = rng.standard_normal((256, 100))


def through_depth(scale, activation, depth=10):
    """A 10-layer stack of 100-unit layers: the std of the activations after each layer, and the gradient reaching the input."""
    layers = []
    for i in range(depth):
        layers += [Dense(100, 100, seed=i, scale=scale), activation()]
    net = Sequential(layers)
    stds = []
    h = X_deep
    for layer in net.layers:
        h = layer.forward(h)
        if isinstance(layer, activation):
            stds.append(float(h.std()))
    grad_in = net.backward(np.random.default_rng(1).standard_normal(h.shape))
    return stds, float(grad_in.std())


for name, scale, activation in (("0.01 with tanh", 0.01, Tanh), ("1.0 with tanh", 1.0, Tanh), ("Xavier 0.1 with tanh", 0.1, Tanh), ("0.1 with ReLU", 0.1, ReLU), ("0.3 with ReLU", 0.3, ReLU), ("He 0.14 with ReLU", np.sqrt(2 / 100), ReLU)):
    stds, grad_std = through_depth(scale, activation)
    print(f"scale {name}: activations after layers 1, 5, 10 have std {stds[0]:.2f}, {stds[4]:.2f}, {stds[9]:.2f} ({describe(stds[9])}); the gradient reaching the input: {describe(grad_std)}")

big = Tanh()
big.forward(Dense(100, 100, seed=0, scale=1.0).forward(X_deep))
print("scale 1.0 with tanh: fraction of outputs beyond 0.99, where the slope is under 0.02:", round(float((np.abs(big.out) > 0.99).mean()), 2))
z = Dense(100, 100, seed=0, scale=1.0).forward(X_deep)
print("scale 1.0 with sigmoid: fraction of inputs beyond 4, where the slope is under 0.02:", round(float((np.abs(z) > 4).mean()), 2))
dead = Dense(100, 100, seed=3, scale=np.sqrt(2 / 100))
dead.b[:] = -5.0
h = ReLU().forward(dead.forward(X_deep))
print("He weights but a bias of -5: fraction of ReLU units that never fire on 256 inputs:", round(float((h.max(axis=0) == 0).mean()), 2))
print("rules of thumb: tanh or sigmoid -> Xavier, 1 / sqrt(n_in) = 0.10 for 100 inputs | ReLU -> He, sqrt(2 / n_in) = 0.14 | biases -> 0")
