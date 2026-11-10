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
        """Training mode: dropout drops."""
        for layer in self.layers:
            if hasattr(layer, "training"):
                layer.training = True

    def eval(self):
        """Evaluation mode: every layer passes everything through."""
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


class Adam:
    """Adam, with weight decay added to every gradient first: the pull towards zero that L2 regularization is."""

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
            grad = grad + self.weight_decay * param
            self.m[i] = self.beta1 * self.m[i] + (1 - self.beta1) * grad
            self.v[i] = self.beta2 * self.v[i] + (1 - self.beta2) * grad ** 2
            m_hat = self.m[i] / (1 - self.beta1 ** self.t)
            v_hat = self.v[i] / (1 - self.beta2 ** self.t)
            param -= self.rate * m_hat / (np.sqrt(v_hat) + self.eps)


def make_blobs(n_per_class, seed, spread=1.0):
    """Three clouds of points, one per class; a larger spread makes them overlap more."""
    rng = np.random.default_rng(seed)
    centres = np.array([[0.0, 0.0], [3.0, 3.0], [-3.0, 3.0]])
    X = np.vstack([centre + spread * rng.standard_normal((n_per_class, 2)) for centre in centres])
    return X, np.repeat(np.arange(3), n_per_class)


def evaluate(net, loss, X, y):
    logits = net.forward(X)
    return loss.forward(logits, y), float((logits.argmax(axis=1) == y).mean())


def fit(net, loss, optimizer, X_train, y_train, X_val, y_val, epochs, patience=None):
    """Full-batch training for some epochs; with a patience, stop once the validation loss hasn't improved for that many epochs and restore the best weights."""
    history = {"train_loss": [], "val_loss": [], "val_accuracy": [], "best_epoch": None, "stopped_at": None}
    best_loss, best_params, best_epoch = np.inf, None, 0
    for epoch in range(1, epochs + 1):
        net.train()
        loss.forward(net.forward(X_train), y_train)
        net.backward(loss.backward())
        optimizer.step(net.parameters(), net.gradients())
        train_loss, _ = evaluate(net, loss, X_train, y_train)
        val_loss, val_accuracy = evaluate(net, loss, X_val, y_val)
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["val_accuracy"].append(val_accuracy)
        if val_loss < best_loss:
            best_loss, best_epoch = val_loss, epoch
            best_params = [p.copy() for p in net.parameters()]
        elif patience is not None and epoch - best_epoch >= patience:
            break
    history["best_epoch"], history["stopped_at"] = best_epoch, epoch
    if patience is not None and best_params is not None:
        for param, best in zip(net.parameters(), best_params):
            param[...] = best
    return history


def read_fit(history):
    """What the validation curve did after its lowest point, in a word."""
    lowest = min(history["val_loss"])
    ratio = history["val_loss"][-1] / lowest
    if ratio > 2:
        return "overfitting"
    if ratio > 1.1:
        return "drifting up"
    return "holding"


X_train, y_train = make_blobs(20, seed=1, spread=1.8)
X_val, y_val = make_blobs(100, seed=2, spread=1.8)
loss = SoftmaxCrossEntropy()
net = Sequential([Dense(2, 64, seed=1, scale=1.0), ReLU(), Dropout(0.5, seed=5), Dense(64, 3, seed=3)])
history = fit(net, loss, Adam(0.01, weight_decay=0.03), X_train, y_train, X_val, y_val, epochs=200)
again = evaluate(net, loss, X_val, y_val)
print("validation loss at the end:", round(history["val_loss"][-1], 3), "| evaluating twice gives the same answer:", again[0] == history["val_loss"][-1])
weights = net.layers[0].W
print("the first layer's weights shrank under decay:", bool(np.abs(weights).mean() < 0.5), "| validation accuracy:", round(history["val_accuracy"][-1], 2))
