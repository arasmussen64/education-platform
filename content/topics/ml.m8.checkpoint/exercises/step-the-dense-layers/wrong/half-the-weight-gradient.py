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
        self.dW = (grad_out.T @ self.X).T * 0.5
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

    def train(self):
        for layer in self.layers:
            if hasattr(layer, "training"):
                layer.training = True

    def eval(self):
        for layer in self.layers:
            if hasattr(layer, "training"):
                layer.training = False


class SoftmaxCrossEntropy:
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
    """The largest gap between any parameter's backward gradient and its numeric one, with the network in eval mode so dropout can't change the function between evaluations."""
    net.eval()
    loss.forward(net.forward(X), y)
    net.backward(loss.backward())
    worst = 0.0
    for param, grad in zip(net.parameters(), net.gradients()):
        numeric = numeric_gradient(lambda: loss.forward(net.forward(X), y), param)
        worst = max(worst, float(np.abs(grad - numeric).max()))
    return worst


rng = np.random.default_rng(0)
X = rng.standard_normal((6, 5))
y = rng.integers(0, 3, size=6)
net = Sequential([Dense(5, 8, seed=1), ReLU(), Dense(8, 3, seed=2)])
loss = SoftmaxCrossEntropy()
print("gradient check:", "passes" if gradient_check(net, loss, X, y) < 1e-6 else "fails")
print(sum(p.size for p in net.parameters()), net.forward(X).shape)
