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


X = np.array([[1.0, 2.0, 0.5], [0.0, 1.0, -1.0], [2.0, -1.0, 0.0], [-1.0, 0.5, 1.5], [0.5, 0.5, 0.5], [-2.0, 1.0, 1.0]])
y = np.array([[1.0], [0.0], [1.0], [0.0], [1.0], [0.0]])
hidden = Dense(3, 8, seed=1, scale=np.sqrt(2 / 3))
hidden.b[:] = -5.0
net = Sequential([hidden, ReLU(), Dense(8, 1, seed=2)])
loss = MSELoss()
first = loss.forward(net.forward(X), y)
for step in range(300):
    loss.forward(net.forward(X), y)
    net.backward(loss.backward())
    for param, grad in zip(net.parameters(), net.gradients()):
        param -= 0.05 * grad
last = loss.forward(net.forward(X), y)
h = net.layers[1].forward(hidden.forward(X))
print("loss", round(first, 4), "->", round(last, 4), "| the loss fell by more than half:", last < first / 2)
print("hidden units identical:", bool(np.allclose(hidden.W, hidden.W[:, :1])), "| dead hidden units:", int((h.max(axis=0) == 0).sum()), "of 8")
