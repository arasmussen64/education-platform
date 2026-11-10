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
    def __init__(self, rate):
        self.rate = rate

    def step(self, params, grads):
        for param, grad in zip(params, grads):
            param -= self.rate * grad


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


def make_blobs(n_per_class, seed, spread=1.0):
    """Three clouds of points, one per class."""
    rng = np.random.default_rng(seed)
    centres = np.array([[0.0, 0.0], [3.0, 3.0], [-3.0, 3.0]])
    X = np.vstack([centre + spread * rng.standard_normal((n_per_class, 2)) for centre in centres])
    return X, np.repeat(np.arange(3), n_per_class)


def batches(n, batch_size, rng):
    """Shuffled index arrays covering every row once."""
    order = rng.permutation(n)
    for start in range(0, n, batch_size):
        yield order[start : start + batch_size]


def evaluate(net, loss, X, y):
    logits = net.forward(X)
    return loss.forward(logits, y), float((logits.argmax(axis=1) == y).mean())


def read_curve(losses):
    """A training curve in a word: diverging if the last loss is NaN or rose by half, stalled if it fell by less than a tenth, else converging."""
    first, last = losses[0], losses[-1]
    if not np.isfinite(last) or last > 1.5 * first:
        return "diverging"
    if last > 0.9 * first:
        return "stalled"
    return "converging"


def gradient_norm(grads):
    """The length of all the gradients taken together, as one vector."""
    return float(np.sqrt(sum(float((grad ** 2).sum()) for grad in grads)))


def clip_gradients(grads, max_norm):
    """Scale the gradients down, all by the same factor, so their norm is at most max_norm; leave them alone if it already is."""
    norm = gradient_norm(grads)
    if norm > max_norm:
        return [grad * (max_norm / norm) for grad in grads]
    return grads


def fit(net, loss, optimizer, X_train, y_train, X_val, y_val, epochs, batch_size=32, seed=0, max_norm=None):
    """Mini-batch training whose history starts with the losses before any training (entry 0) and adds one entry per epoch, records the gradient norm at every step (before any clipping), and can clip; overflow is a symptom to read, not a crash."""
    rng = np.random.default_rng(seed)
    history = {"train_loss": [], "val_loss": [], "val_accuracy": [], "grad_norms": []}

    def record():
        train_loss, _ = evaluate(net, loss, X_train, y_train)
        val_loss, val_accuracy = evaluate(net, loss, X_val, y_val)
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["val_accuracy"].append(val_accuracy)

    with np.errstate(all="ignore"):
        record()
        for epoch in range(epochs):
            for index in batches(len(X_train), batch_size, rng):
                loss.forward(net.forward(X_train[index]), y_train[index])
                net.backward(loss.backward())
                grads = net.gradients()
                history["grad_norms"].append(gradient_norm(grads))
                if max_norm is not None:
                    grads = clip_gradients(grads, max_norm)
                optimizer.step(net.parameters(), grads)
            record()
    return history


def dead_units(net, X):
    """How many ReLU units output 0 on every row of X: no gradient reaches them, so they can never recover."""
    net.forward(X)
    return sum(int((~layer.mask.any(axis=0)).sum()) for layer in net.layers if isinstance(layer, ReLU))


def overfit_one_batch(net, loss, X, y, steps=500, rate=0.1):
    """Train on a handful of rows, the whole handful every step: a working network drives the loss to nearly zero. Returns the first and the last loss."""
    optimizer = SGD(rate)
    first = loss.forward(net.forward(X), y)
    with np.errstate(all="ignore"):
        for step in range(steps):
            loss.forward(net.forward(X), y)
            net.backward(loss.backward())
            optimizer.step(net.parameters(), net.gradients())
        return first, loss.forward(net.forward(X), y)


def standardize(X, mean, std):
    """Columns to mean 0 and spread 1, with a mean and spread measured on the training rows only."""
    return (X - mean) / std


def diagnose(history, n_classes):
    """One phrase for a run: diverging (the loss is NaN or rose by half), stalled (it fell by less than a tenth), at chance (the validation accuracy is within a tenth of guessing), else learning."""
    verdict = read_curve(history["train_loss"])
    if verdict != "converging":
        return verdict
    if history["val_accuracy"][-1] < 1 / n_classes + 0.1:
        return "at chance"
    return "learning"


def split(X, y, seed, held_out=0.2):
    """Shuffle the rows, inputs and labels together, and hold out a share for validation."""
    rng = np.random.default_rng(seed)
    order = rng.permutation(len(X))
    X, y = X[order], y[order]
    n_val = int(len(X) * held_out)
    return X[n_val:], y[n_val:], X[:n_val], y[:n_val]


X, y = make_blobs(100, seed=0)
X_train, y_train, X_val, y_val = split(X, y, seed=0)
loss = SoftmaxCrossEntropy()
rate = 50.0
net = Sequential([Dense(2, 16, seed=1), ReLU(), Dense(16, 3, seed=2, scale=0.01)])
history = fit(net, loss, SGD(rate), X_train, y_train, X_val, y_val, epochs=30)
print(f"loss {history['train_loss'][0]:.2f} -> {history['train_loss'][-1]:.2f}: {diagnose(history, 3)} | validation accuracy {history['val_accuracy'][-1]:.2f}")
fresh = Sequential([Dense(2, 16, seed=1), ReLU(), Dense(16, 3, seed=2, scale=0.01)])
_, last = overfit_one_batch(fresh, loss, X_train[:8], y_train[:8], rate=rate)
print(f"one batch of 8 overfits: {bool(last < 0.1)} | dead units after training: {dead_units(net, X_train)} of 16")
