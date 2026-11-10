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

    def train(self):
        for layer in self.layers:
            if hasattr(layer, "training"):
                layer.training = True

    def eval(self):
        for layer in self.layers:
            if hasattr(layer, "training"):
                layer.training = False


class Conv2D:
    """n_kernels square kernels of size k over single-channel images (N, H, W): one feature map per kernel, (N, n_kernels, H - k + 1, W - k + 1)."""

    def __init__(self, n_kernels, k, seed=0, scale=None):
        rng = np.random.default_rng(seed)
        self.scale = 1 / k if scale is None else scale
        self.W = rng.standard_normal((n_kernels, k, k)) * self.scale
        self.b = np.zeros(n_kernels)
        self.dW = np.zeros_like(self.W)
        self.db = np.zeros_like(self.b)

    def forward(self, X):
        self.X = X
        n, h, w = X.shape
        k = self.W.shape[1]
        h_out, w_out = h - k + 1, w - k + 1
        out = np.zeros((n, len(self.W), h_out, w_out))
        for i in range(k):
            for j in range(k):
                patch = X[:, i : i + h_out, j : j + w_out]
                out += patch[:, None] * self.W[None, :, i, j, None, None]
        return out + self.b[None, :, None, None]

    def backward(self, grad_out):
        k = self.W.shape[1]
        h_out, w_out = grad_out.shape[2:]
        self.dW = np.zeros_like(self.W)
        self.db = grad_out.sum(axis=(0, 2, 3))
        grad_in = np.zeros_like(self.X)
        for i in range(k):
            for j in range(k):
                patch = self.X[:, i : i + h_out, j : j + w_out]
                self.dW[:, i, j] = (grad_out * patch[:, None]).sum(axis=(0, 2, 3))
                grad_in[:, i : i + h_out, j : j + w_out] += (grad_out * self.W[None, :, j, i, None, None]).sum(axis=1)
        return grad_in

    def parameters(self):
        return [self.W, self.b]

    def gradients(self):
        return [self.dW, self.db]


class MaxPool2D:
    def __init__(self, size=2):
        self.size = size

    def forward(self, X):
        n, c, h, w = X.shape
        s = self.size
        windows = X.reshape(n, c, h // s, s, w // s, s)
        out = windows.max(axis=(3, 5))
        self.mask = windows == out[:, :, :, None, :, None]
        return out

    def backward(self, grad_out):
        n, c, h_out, w_out = grad_out.shape
        s = self.size
        spread = self.mask * grad_out[:, :, :, None, :, None]
        return spread.reshape(n, c, h_out * s, w_out * s)

    def parameters(self):
        return []

    def gradients(self):
        return []


class Flatten:
    def forward(self, X):
        self.shape = X.shape
        return X.reshape(len(X), -1)

    def backward(self, grad_out):
        return grad_out.reshape(self.shape)

    def parameters(self):
        return []

    def gradients(self):
        return []


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
X = rng.standard_normal((3, 8, 8))
y = rng.integers(0, 4, size=3)
net = Sequential([Conv2D(2, 3, seed=1), ReLU(), MaxPool2D(2), Flatten(), Dense(18, 4, seed=2)])
loss = SoftmaxCrossEntropy()
print(net.forward(X).shape, "| gradient check:", "passes" if gradient_check(net, loss, X, y) < 1e-6 else "fails")
loss.forward(net.forward(X), y)
grad_in = net.backward(loss.backward())
numeric = numeric_gradient(lambda: loss.forward(net.forward(X), y), X)
print("input gradient:", "passes" if np.abs(grad_in - numeric).max() < 1e-6 else "fails")
