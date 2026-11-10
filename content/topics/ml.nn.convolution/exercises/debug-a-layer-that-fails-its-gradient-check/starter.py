import numpy as np


class Dense:
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
    """The largest gap between any parameter's backward gradient and its numeric one."""
    loss.forward(net.forward(X), y)
    net.backward(loss.backward())
    worst = 0.0
    for param, grad in zip(net.parameters(), net.gradients()):
        numeric = numeric_gradient(lambda: loss.forward(net.forward(X), y), param)
        worst = max(worst, float(np.abs(grad - numeric).max()))
    return worst


def input_gradient_check(net, loss, X, y):
    """The largest gap between the gradient backward hands back for X and the numeric one."""
    loss.forward(net.forward(X), y)
    grad = net.backward(loss.backward())
    numeric = numeric_gradient(lambda: loss.forward(net.forward(X), y), X)
    return float(np.abs(grad - numeric).max())


def correlate2d(image, kernel, padding=0, stride=1):
    """Slide the kernel over the image (padded with zeros on every side), moving stride pixels at a time; each output cell is the sum of the kernel times the patch under it. Libraries call this a convolution."""
    if padding:
        image = np.pad(image, padding)
    k = kernel.shape[0]
    h_out = (image.shape[0] - k) // stride + 1
    w_out = (image.shape[1] - k) // stride + 1
    out = np.zeros((h_out, w_out))
    for y in range(h_out):
        for x in range(w_out):
            patch = image[y * stride : y * stride + k, x * stride : x * stride + k]
            out[y, x] = (patch * kernel).sum()
    return out


class Conv2D:
    """n_kernels square kernels of size k slid over single-channel images (N, H, W), giving (N, n_kernels, H - k + 1, W - k + 1): one feature map per kernel."""

    def __init__(self, n_kernels, k, seed=0):
        rng = np.random.default_rng(seed)
        self.W = rng.standard_normal((n_kernels, k, k)) / np.sqrt(k * k)
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
                # Every output cell times weight (i, j) sees the input shifted by (i, j).
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
                # Weight (i, j) was used at every position: its gradient sums them all.
                self.dW[:, i, j] = (grad_out * patch[:, None]).sum(axis=(0, 2, 3))
                # Each output gradient flows back to the input cells it read, through weight (i, j).
                grad_in[:, i : i + h_out, j : j + w_out] += (grad_out * self.W[None, :, j, i, None, None]).sum(axis=1)
        return grad_in

    def parameters(self):
        return [self.W, self.b]

    def gradients(self):
        return [self.dW, self.db]


class MaxPool2D:
    """Keep the largest value in each size-by-size window of every feature map (N, C, H, W), dividing height and width by size."""

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
        # Only the cell that won its window affected the output, so only it gets the gradient.
        spread = grad_out[:, :, :, None, :, None] * np.ones((1, 1, 1, s, 1, s))
        return spread.reshape(n, c, h_out * s, w_out * s)

    def parameters(self):
        return []

    def gradients(self):
        return []


class Flatten:
    """Feature maps (N, C, H, W) to rows (N, C * H * W), so a Dense layer can follow."""

    def forward(self, X):
        self.shape = X.shape
        return X.reshape(len(X), -1)

    def backward(self, grad_out):
        return grad_out.reshape(self.shape)

    def parameters(self):
        return []

    def gradients(self):
        return []


def make_bars(n, seed):
    """n noisy 8x8 images: the first half with a horizontal bar, the second half with a vertical one, each at a random position."""
    rng = np.random.default_rng(seed)
    X = rng.normal(0.0, 0.3, size=(n, 8, 8))
    y = np.repeat([0, 1], n // 2)
    for image, label in zip(X, y):
        at = rng.integers(1, 7)
        if label == 0:
            image[at, :] += 1.0
        else:
            image[:, at] += 1.0
    return X, y


block = np.array([[[[1.0, 2.0, 5.0, 6.0], [3.0, 4.0, 7.0, 8.0], [9.0, 10.0, 13.0, 14.0], [11.0, 12.0, 15.0, 16.0]]]])
pool = MaxPool2D(2)
pooled = pool.forward(block)
print("pooling a 4x4:", pooled[0, 0].tolist(), "| cells that get gradient:", int((pool.backward(np.ones((1, 1, 2, 2))) != 0).sum()))
rng = np.random.default_rng(0)
images = rng.standard_normal((5, 8, 8))
labels = rng.integers(0, 3, size=5)
net = Sequential([Conv2D(4, 3, seed=1), ReLU(), MaxPool2D(2), Flatten(), Dense(36, 3, seed=2)])
loss = SoftmaxCrossEntropy()
print("gradient check of the parameters:", "passes" if gradient_check(net, loss, images, labels) < 1e-6 else "fails", "| of the input:", "passes" if input_gradient_check(net, loss, images, labels) < 1e-6 else "fails")
