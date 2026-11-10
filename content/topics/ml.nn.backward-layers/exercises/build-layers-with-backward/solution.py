import numpy as np


class Dense:
    """A dense layer that remembers its input, so backward can compute the gradient for W."""

    def __init__(self, n_in, n_out, seed=0):
        rng = np.random.default_rng(seed)
        self.W = rng.standard_normal((n_in, n_out)) / np.sqrt(n_in)
        self.b = np.zeros(n_out)
        self.dW = np.zeros_like(self.W)
        self.db = np.zeros_like(self.b)

    def forward(self, X):
        self.X = X
        return X @ self.W + self.b

    def backward(self, grad_out):
        """grad_out is the loss's gradient with respect to this layer's output, one row per example."""
        self.dW = self.X.T @ grad_out
        self.db = grad_out.sum(axis=0)
        return grad_out @ self.W.T

    def parameters(self):
        return [self.W, self.b]

    def gradients(self):
        return [self.dW, self.db]


class ReLU:
    """Remembers which inputs were positive: the gradient passes through there and is zero elsewhere."""

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
    """Forward runs the layers in order; backward runs them in reverse, handing each the gradient from the one after it."""

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
    """Mean squared error over every entry; backward is its gradient with respect to the predictions."""

    def forward(self, pred, target):
        self.diff = pred - target
        return float(np.mean(self.diff ** 2))

    def backward(self):
        return 2 * self.diff / self.diff.size


class SoftmaxCrossEntropy:
    """Softmax over each row of logits, then the mean negative log probability of the true class; stable through log-sum-exp."""

    def forward(self, logits, labels):
        shifted = logits - logits.max(axis=1, keepdims=True)
        log_probs = shifted - np.log(np.exp(shifted).sum(axis=1, keepdims=True))
        self.probs = np.exp(log_probs)
        self.labels = labels
        return float(-log_probs[np.arange(len(labels)), labels].mean())

    def backward(self):
        grad = self.probs.copy()
        grad[np.arange(len(self.labels)), self.labels] -= 1
        return grad / len(self.labels)


def numeric_gradient(f, param, h=1e-6):
    """The central-difference gradient of f() with respect to every entry of param, which f reads."""
    grad = np.zeros_like(param)
    for index in np.ndindex(param.shape):
        old = param[index]
        param[index] = old + h
        up = f()
        param[index] = old - h
        down = f()
        param[index] = old
        grad[index] = (up - down) / (2 * h)
    return grad


def gradient_check(net, loss, X, y):
    """The largest gap between any parameter's backward gradient and its numeric one."""
    loss.forward(net.forward(X), y)
    net.backward(loss.backward())
    worst = 0.0
    for param, grad in zip(net.parameters(), net.gradients()):
        numeric = numeric_gradient(lambda: loss.forward(net.forward(X), y), param)
        worst = max(worst, float(np.abs(grad - numeric).max()))
    return worst


X = np.array([[1.0, 2.0, 0.5], [0.0, 1.0, -1.0], [2.0, -1.0, 0.0], [-1.0, 0.5, 1.5]])
y = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0], [0.0, 0.0]])
net = Sequential([Dense(3, 4, seed=1), ReLU(), Dense(4, 2, seed=2)])
loss = MSELoss()
print(round(loss.forward(net.forward(X), y), 4), net.backward(loss.backward()).shape, [g.shape for g in net.gradients()])
print(gradient_check(net, loss, X, y) < 1e-6)
ce = SoftmaxCrossEntropy()
logits = np.array([[2.0, 1.0, 0.1], [0.5, 2.5, 0.2]])
labels = np.array([0, 1])
print(round(ce.forward(logits, labels), 4), np.round(ce.backward(), 3).tolist())
classifier = Sequential([Dense(3, 5, seed=3), ReLU(), Dense(5, 3, seed=4)])
print(gradient_check(classifier, ce, X, np.array([0, 1, 2, 1])) < 1e-6, round(ce.forward(np.array([[1000.0, 1001.0]]), np.array([1])), 4))
