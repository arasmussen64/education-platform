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


class Dropout:
    """In training, zero each value with probability p and scale the rest by 1 / (1 - p); in eval, pass everything through."""

    def __init__(self, p, seed=0):
        self.p = p
        self.rng = np.random.default_rng(seed)
        self.training = True

    def forward(self, X):
        if not self.training or self.p == 0:
            self.mask = None
            return X
        self.mask = (self.rng.random(X.shape) >= self.p) / (1 - self.p)
        return X * self.mask

    def backward(self, grad_out):
        return grad_out if self.mask is None else grad_out * self.mask

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
                grad_in[:, i : i + h_out, j : j + w_out] += (grad_out * self.W[None, :, i, j, None, None]).sum(axis=1)
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


class Adam:
    """Adam, with weight decay added to every gradient first."""

    def __init__(self, rate, weight_decay=0.0, beta1=0.9, beta2=0.999, eps=1e-8):
        self.rate, self.weight_decay = rate, weight_decay
        self.beta1, self.beta2, self.eps = beta1, beta2, eps
        self.m, self.v, self.t = None, None, 0

    def step(self, params, grads):
        if self.m is None:
            self.m = [np.zeros_like(p) for p in params]
            self.v = [np.zeros_like(p) for p in params]
        self.t += 1
        for i, (param, grad) in enumerate(zip(params, grads)):
            grad = grad - self.weight_decay * param
            self.m[i] = self.beta1 * self.m[i] + (1 - self.beta1) * grad
            self.v[i] = self.beta2 * self.v[i] + (1 - self.beta2) * grad ** 2
            m_hat = self.m[i] / (1 - self.beta1 ** self.t)
            v_hat = self.v[i] / (1 - self.beta2 ** self.t)
            param -= self.rate * m_hat / (np.sqrt(v_hat) + self.eps)


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


def batches(n, batch_size, rng):
    """Shuffled index arrays covering every row once."""
    order = rng.permutation(n)
    for start in range(0, n, batch_size):
        yield order[start : start + batch_size]


def evaluate(net, loss, X, y):
    """The loss and the accuracy on a set, with dropout off and no update."""
    net.eval()
    logits = net.forward(X)
    return loss.forward(logits, y), float((logits.argmax(axis=1) == y).mean())


def fit(net, loss, optimizer, X_train, y_train, X_val, y_val, epochs, batch_size=32, seed=0):
    """Mini-batch training: train mode before each step, eval mode to measure, one history entry per epoch."""
    rng = np.random.default_rng(seed)
    history = {"train_loss": [], "val_loss": [], "val_accuracy": []}
    for epoch in range(epochs):
        net.train()
        for index in batches(len(X_train), batch_size, rng):
            loss.forward(net.forward(X_train[index]), y_train[index])
            net.backward(loss.backward())
            optimizer.step(net.parameters(), net.gradients())
        train_loss, _ = evaluate(net, loss, X_train, y_train)
        val_loss, val_accuracy = evaluate(net, loss, X_val, y_val)
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["val_accuracy"].append(val_accuracy)
    return history


def make_images(glyphs, n_per_class, seed, size=10, max_shift=1, noise=0.2):
    """n_per_class images per glyph: Gaussian noise, with the glyph drawn at its centre shifted by up to max_shift pixels each way; labels in font order."""
    rng = np.random.default_rng(seed)
    names = list(glyphs)
    X = rng.normal(0.0, noise, size=(n_per_class * len(names), size, size))
    y = np.repeat(np.arange(len(names)), n_per_class)
    for image, label in zip(X, y):
        rows = glyphs[names[label]]
        top = (size - len(rows)) // 2 + rng.integers(-max_shift, max_shift + 1)
        left = (size - len(rows[0])) // 2 + rng.integers(-max_shift, max_shift + 1)
        for r, row in enumerate(rows):
            for c, char in enumerate(row):
                if char == "#":
                    image[top + r, left + c] += 1.0
    return X, y


LETTERS = {
    'A': ['.###.', '#...#', '#...#', '#####', '#...#', '#...#', '#...#'],
    'C': ['.###.', '#...#', '#....', '#....', '#....', '#...#', '.###.'],
    'E': ['#####', '#....', '#....', '####.', '#....', '#....', '#####'],
    'F': ['#####', '#....', '#....', '####.', '#....', '#....', '#....'],
    'H': ['#...#', '#...#', '#...#', '#####', '#...#', '#...#', '#...#'],
    'L': ['#....', '#....', '#....', '#....', '#....', '#....', '#####'],
    'T': ['#####', '..#..', '..#..', '..#..', '..#..', '..#..', '..#..'],
    'U': ['#...#', '#...#', '#...#', '#...#', '#...#', '#...#', '.###.'],
}


def make_letters(n_per_class, seed):
    """n_per_class noisy, shifted images of each letter, with labels in font order."""
    return make_images(LETTERS, n_per_class, seed)


X_train, y_train = make_letters(60, seed=1)
X_val, y_val = make_letters(20, seed=2)
loss = SoftmaxCrossEntropy()
print(X_train.shape, X_val.shape, np.bincount(y_val).tolist())
tiny = Sequential([Conv2D(2, 3, seed=1), ReLU(), MaxPool2D(2), Flatten(), Dense(32, 8, seed=2)])
print("gradient check:", "passes" if gradient_check(tiny, loss, X_train[:4], y_train[:4]) < 1e-6 else "fails")
net = Sequential([Conv2D(6, 3, seed=1), ReLU(), MaxPool2D(2), Flatten(), Dropout(0.2, seed=5), Dense(96, 8, seed=2)])
history = fit(net, loss, Adam(0.01, weight_decay=1e-4), X_train, y_train, X_val, y_val, epochs=20)
accuracy = history["val_accuracy"][-1]
print(f"loss {history['train_loss'][0]:.2f} -> {history['train_loss'][-1]:.2f} | held-out accuracy {accuracy:.2f} | at least 0.9: {accuracy >= 0.9} | {sum(p.size for p in net.parameters())} parameters")
print("evaluating twice gives the same answer:", evaluate(net, loss, X_val, y_val)[0] == evaluate(net, loss, X_val, y_val)[0])
names = list(LETTERS)
net.eval()
print("the first held-out image of each letter reads:", " ".join(names[i] for i in net.forward(X_val[::20]).argmax(axis=1)))
