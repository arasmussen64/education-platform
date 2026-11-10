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


class SGD:
    """Plain gradient descent: every parameter steps against its gradient by the learning rate."""

    def __init__(self, rate):
        self.rate = rate

    def step(self, params, grads):
        for param, grad in zip(params, grads):
            param -= self.rate * grad


class Adam:
    """Adam from Module 4: a running average of each gradient and of its square, with the step scaled by their ratio."""

    def __init__(self, rate, beta1=0.9, beta2=0.999, eps=1e-8):
        self.rate, self.beta1, self.beta2, self.eps = rate, beta1, beta2, eps
        self.m, self.v, self.t = None, None, 0

    def step(self, params, grads):
        if self.m is None:
            self.m = [np.zeros_like(p) for p in params]
            self.v = [np.zeros_like(p) for p in params]
        self.t += 1
        for i, (param, grad) in enumerate(zip(params, grads)):
            self.m[i] = self.beta1 * self.m[i] + (1 - self.beta1) * grad
            self.v[i] = self.beta2 * self.v[i] + (1 - self.beta2) * grad ** 2
            m_hat = self.m[i] / (1 - self.beta1 ** self.t)
            v_hat = self.v[i] / (1 - self.beta2 ** self.t)
            param -= self.rate * m_hat / (np.sqrt(v_hat) + self.eps)


def make_blobs(n_per_class=100, seed=0):
    """Three clouds of points in the plane, one per class, overlapping a little."""
    rng = np.random.default_rng(seed)
    centres = np.array([[0.0, 0.0], [3.0, 3.0], [-3.0, 3.0]])
    X = np.vstack([centre + rng.standard_normal((n_per_class, 2)) for centre in centres])
    y = np.repeat(np.arange(3), n_per_class)
    return X, y


def split(X, y, train_fraction=0.8, seed=0):
    """Shuffle once, then cut: the validation rows are never trained on."""
    order = np.random.default_rng(seed).permutation(len(X))
    cut = int(train_fraction * len(X))
    train, val = order[:cut], order[cut:]
    return X[train], y[train], X[val], y[val]


def batches(n, batch_size, rng):
    """Index arrays covering 0..n-1 once, in a fresh random order, batch_size at a time (the last batch may be short)."""
    order = rng.permutation(n)
    for start in range(0, n, batch_size):
        yield order[start : start + batch_size]


def accuracy(logits, labels):
    """The share of rows whose largest logit is the true class."""
    return float((logits.argmax(axis=1) == labels).mean())


def evaluate(net, loss, X, y):
    """Loss and accuracy on a whole set, with no training."""
    logits = net.forward(X)
    return loss.forward(logits, y), accuracy(logits, y)


def fit(net, loss, optimizer, X_train, y_train, X_val, y_val, epochs, batch_size, seed=0):
    """Train for some epochs of shuffled mini-batches; after each epoch, record the losses and the validation accuracy."""
    rng = np.random.default_rng(seed)
    history = {"train_loss": [], "val_loss": [], "val_accuracy": []}
    for epoch in range(epochs):
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


def read_curve(losses):
    """Converging, stalled or diverging, from the first and last values."""
    first, last = losses[0], losses[-1]
    if not np.isfinite(last) or last > 1.5 * first:
        return "diverging"
    if (first - last) / first < 0.1:
        return "stalled"
    return "converging"


X, y = make_blobs()
X_train, y_train, X_val, y_val = split(X, y)
print("rows:", len(X_train), "to train on,", len(X_val), "held out | classes in the validation set:", np.bincount(y_val).tolist())


def new_net(seed=0):
    return Sequential([Dense(2, 16, seed=seed, scale=np.sqrt(2 / 2)), ReLU(), Dense(16, 3, seed=seed + 1)])


loss = SoftmaxCrossEntropy()
history = fit(new_net(), loss, SGD(0.05), X_train, y_train, X_val, y_val, epochs=30, batch_size=32)
for epoch in (0, 4, 9, 19, 29):
    train_loss, val_loss, val_accuracy = history["train_loss"][epoch], history["val_loss"][epoch], history["val_accuracy"][epoch]
    print(f"epoch {epoch + 1:2d} | train loss {train_loss:.3f} {'#' * int(round(train_loss * 20))} | val loss {val_loss:.3f} | val accuracy {val_accuracy:.2f}")
print("the curve is", read_curve(history["train_loss"]), "| steps taken:", 30 * -(-len(X_train) // 32))

for rate in (0.00005, 0.05, 30.0):
    with np.errstate(over="ignore", invalid="ignore"):
        history = fit(new_net(), loss, SGD(rate), X_train, y_train, X_val, y_val, epochs=30, batch_size=32)
    print(f"learning rate {rate}: the training loss goes from {history['train_loss'][0]:.3g} to {history['train_loss'][-1]:.3g}: {read_curve(history['train_loss'])}")

for batch_size in (8, 240):
    history = fit(new_net(), loss, SGD(0.05), X_train, y_train, X_val, y_val, epochs=30, batch_size=batch_size)
    steps = 30 * -(-len(X_train) // batch_size)
    print(f"batch size {batch_size}: {steps} steps in 30 epochs, final validation accuracy {history['val_accuracy'][-1]:.2f}")

history = fit(new_net(), loss, Adam(0.01), X_train, y_train, X_val, y_val, epochs=30, batch_size=32)
print(f"Adam at 0.01, batch 32: final train loss {history['train_loss'][-1]:.3f}, validation accuracy {history['val_accuracy'][-1]:.2f}")
