"""Writes the topic ml.nn.regularization (Module 8's fifth topic). Run from
the repository root under uv (python -m uv run python <this file>), so every
program's expected output is captured from CPython rather than typed in.
Overfitting is produced on purpose: sixty noisy points and a network of two
hidden layers of 64, trained full-batch with Adam for 300 epochs; the cures
are measured against it. Losses are printed rounded, the shape of each run is
also named in words, and the generator checks that a tenth-decimal nudge of
the data leaves every line unchanged. Files are written as bytes with LF
endings."""

import pathlib
import subprocess
import sys

ROOT = pathlib.Path("content/topics/ml.nn.regularization")


def write(relative: str, text: str) -> None:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


def out(program: str) -> str:
    result = subprocess.run([sys.executable, "-W", "error", "-c", program], capture_output=True, text=True, check=True)
    return result.stdout.replace("\r\n", "\n")


def differs(program: str, expected: str) -> bool:
    """True if the program fails or prints something other than expected: what a known-wrong must do."""
    result = subprocess.run([sys.executable, "-c", program], capture_output=True, text=True)
    return result.returncode != 0 or result.stdout.replace("\r\n", "\n") != expected


def block(text: str, indent: str = "  ") -> str:
    return "".join(indent + line + "\n" for line in text.rstrip("\n").splitlines())


def quoted(text: str) -> str:
    """A single-quoted YAML scalar: the one place where '' is an apostrophe."""
    return "'" + text.replace("'", "''") + "'"


def mcq(item_id: str, prompt: str, choices: list[str], answer: int, explanation: str, skills: list[str]) -> None:
    """An MCQ whose right answer is never the longest choice, with plain apostrophes in the block scalars."""
    lengths = [len(c) for c in choices]
    assert lengths[answer] < max(length for i, length in enumerate(lengths) if i != answer), (item_id, lengths)
    assert "''" not in prompt and "''" not in explanation, item_id
    write(
        f"recall/{item_id}.yaml",
        f"id: {item_id}\ntype: mcq\nrev: 1\nprompt: |\n{block(prompt)}choices:\n"
        + "".join(f"  - {quoted(c)}\n" for c in choices)
        + f"answer: {answer}\nexplanation: |\n{block(explanation)}skills: [{', '.join(skills)}]\n",
    )


# The module's classes with this topic's additions: Dropout, train and eval
# modes on Sequential, weight decay in the optimizers, early stopping in fit.
LAYERS = '''class Dense:
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
'''

LOOP = '''

def make_blobs(n_per_class, seed, spread=1.0):
    """Three clouds of points, one per class; a larger spread makes them overlap more."""
    rng = np.random.default_rng(seed)
    centres = np.array([[0.0, 0.0], [3.0, 3.0], [-3.0, 3.0]])
    X = np.vstack([centre + spread * rng.standard_normal((n_per_class, 2)) for centre in centres])
    return X, np.repeat(np.arange(3), n_per_class)


def evaluate(net, loss, X, y):
    net.eval()
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
'''

EXAMPLE_HEAD = "import numpy as np\n\n\n" + LAYERS + LOOP
EXAMPLE_TAIL = '''

X_train, y_train = make_blobs(20, seed=1, spread=1.8)
X_val, y_val = make_blobs(100, seed=2, spread=1.8)
loss = SoftmaxCrossEntropy()


def new_net(dropout=0.0):
    layers = [Dense(2, 64, seed=1, scale=1.0), ReLU()]
    if dropout:
        layers.append(Dropout(dropout, seed=5))
    layers += [Dense(64, 64, seed=2, scale=np.sqrt(2 / 64)), ReLU()]
    if dropout:
        layers.append(Dropout(dropout, seed=6))
    layers.append(Dense(64, 3, seed=3))
    return Sequential(layers)


def report(name, history):
    best = history["best_epoch"]
    print(f"{name}: train loss {history['train_loss'][-1]:.3f} | validation loss lowest {min(history['val_loss']):.3f} at epoch {best}, {history['val_loss'][-1]:.3f} at the end: {read_fit(history)} | validation accuracy {history['val_accuracy'][-1]:.2f}")


plain = fit(new_net(), loss, Adam(0.01), X_train, y_train, X_val, y_val, epochs=300)
print("60 training points, 300 held out, a network of two hidden layers of 64, 300 epochs of Adam:")
for epoch in (1, 10, 28, 50, 100, 200, 300):
    bar = "#" * int(round(plain["val_loss"][epoch - 1] * 10))
    print(f"epoch {epoch:3d} | train {plain['train_loss'][epoch - 1]:.3f} | validation {plain['val_loss'][epoch - 1]:.3f} {bar}")
report("plain", plain)
report("weight decay 0.03", fit(new_net(), loss, Adam(0.01, weight_decay=0.03), X_train, y_train, X_val, y_val, epochs=300))
report("dropout 0.5", fit(new_net(dropout=0.5), loss, Adam(0.01), X_train, y_train, X_val, y_val, epochs=300))
stopped = fit(new_net(), loss, Adam(0.01), X_train, y_train, X_val, y_val, epochs=300, patience=20)
print(f"early stopping, patience 20: stopped at epoch {stopped['stopped_at']}, kept the weights of epoch {stopped['best_epoch']}: validation loss {min(stopped['val_loss']):.3f}, accuracy {stopped['val_accuracy'][stopped['best_epoch'] - 1]:.2f}")
X_more, y_more = make_blobs(400, seed=3, spread=1.8)
report("twenty times the data", fit(new_net(), loss, Adam(0.01), X_more, y_more, X_val, y_val, epochs=300))
'''
EXAMPLE = EXAMPLE_HEAD + EXAMPLE_TAIL
EXAMPLE_OUT = out(EXAMPLE)
print("example:\n" + EXAMPLE_OUT)
EX = EXAMPLE_OUT.splitlines()
assert len(EX) == 13, EX
assert EX[8].startswith("plain:") and "overfitting" in EX[8], EX[8]
assert EX[9].startswith("weight decay 0.03:") and "holding" in EX[9], EX[9]
assert EX[10].startswith("dropout 0.5:") and "overfitting" not in EX[10], EX[10]
assert EX[11].startswith("early stopping, patience 20: stopped at epoch") and "kept the weights of epoch 28" in EX[11], EX[11]
assert EX[12].startswith("twenty times the data:") and "overfitting" not in EX[12], EX[12]
PLAIN_BEST = int(EX[8].split("at epoch ")[1].split(",")[0])
PLAIN_LOW = EX[8].split("lowest ")[1].split(" at")[0]
PLAIN_END = EX[8].split(", ")[1].split(" at the end")[0]
DECAY_END = EX[9].split(", ")[1].split(" at the end")[0]
DROPOUT_END = EX[10].split(", ")[1].split(" at the end")[0]
MORE_END = EX[12].split(", ")[1].split(" at the end")[0]
STOPPED_AT = int(EX[11].split("stopped at epoch ")[1].split(",")[0])
PLAIN_ACC = EX[8].split()[-1]
STOP_ACC = EX[11].split()[-1]
assert float(STOP_ACC) < float(PLAIN_ACC), (STOP_ACC, PLAIN_ACC)
NUDGED = EXAMPLE.replace("X_train, y_train = make_blobs(20, seed=1, spread=1.8)", "X_train, y_train = make_blobs(20, seed=1, spread=1.8)\nX_train[0, 0] += 1e-10")
assert out(NUDGED) == EXAMPLE_OUT, "a tenth-decimal nudge changed a printed line"
EXAMPLE_LINES = EXAMPLE.splitlines()


def ln(text: str, after: int = 0) -> int:
    return next(i + 1 for i, line in enumerate(EXAMPLE_LINES) if i + 1 > after and text in line)


# --- recall programs ----------------------------------------------------------------------------

PREDICT_DROPOUT = '''import numpy as np

X = np.array([[2.0, 4.0, 6.0, 8.0]])
keep = np.array([[1, 0, 1, 0]])
p = 0.5
print((X * keep / (1 - p)).tolist(), float(X.sum()), float((X * keep / (1 - p)).sum()))
print((X * np.array([[1, 1, 0, 1]]) / (1 - p)).sum(), X.tolist())
'''
PREDICT_DROPOUT_OUT = out(PREDICT_DROPOUT)
assert PREDICT_DROPOUT_OUT == "[[4.0, 0.0, 12.0, 0.0]] 20.0 16.0\n28.0 [[2.0, 4.0, 6.0, 8.0]]\n", PREDICT_DROPOUT_OUT

PREDICT_DECAY = '''import numpy as np

W = np.array([2.0, -1.0, 0.5])
grad = np.array([0.0, 0.0, 0.0])
rate, decay = 0.1, 0.5
for step in range(3):
    W = W - rate * (grad + decay * W)
    print(np.round(W, 4).tolist())
'''
PREDICT_DECAY_OUT = out(PREDICT_DECAY)
assert PREDICT_DECAY_OUT == "[1.9, -0.95, 0.475]\n[1.805, -0.9025, 0.4512]\n[1.7148, -0.8574, 0.4287]\n", PREDICT_DECAY_OUT

PREDICT_STOP = '''def early_stopping(val_losses, patience):
    """The epoch (from 1) with the lowest loss so far, and the epoch at which training would stop."""
    best_epoch, best = 1, val_losses[0]
    for epoch, value in enumerate(val_losses, start=1):
        if value < best:
            best, best_epoch = value, epoch
        elif epoch - best_epoch >= patience:
            return best_epoch, epoch
    return best_epoch, len(val_losses)


print(early_stopping([0.9, 0.7, 0.6, 0.62, 0.61, 0.65, 0.7, 0.8], patience=3))
print(early_stopping([0.9, 0.7, 0.6, 0.5, 0.4], patience=3))
'''
PREDICT_STOP_OUT = out(PREDICT_STOP)
assert PREDICT_STOP_OUT == "(3, 6)\n(5, 5)\n", PREDICT_STOP_OUT

REVIEW_DECAY = '''import numpy as np

W = np.full(4, 1.0)
for steps, decay in ((10, 0.0), (10, 0.1), (100, 0.1)):
    w = W.copy()
    for _ in range(steps):
        w = w - 0.1 * (0.0 + decay * w)
    print(steps, decay, round(float(w[0]), 4))
'''
REVIEW_DECAY_OUT = out(REVIEW_DECAY)
assert REVIEW_DECAY_OUT == "10 0.0 1.0\n10 0.1 0.9044\n100 0.1 0.366\n", REVIEW_DECAY_OUT

PARSONS_LINES = [
    "val_losses = [0.9, 0.7, 0.6, 0.6, 0.61, 0.65, 0.7]",
    "best_epoch, best = 1, val_losses[0]",
    "for epoch, value in enumerate(val_losses, start=1):",
    "    if value < best:",
    "        best, best_epoch = value, epoch",
    "    elif epoch - best_epoch >= 3:",
    "        break",
    "print(best_epoch, epoch)",
]
PARSONS_OUT = out("\n".join(PARSONS_LINES) + "\n")
assert PARSONS_OUT == "3 6\n", PARSONS_OUT

# --- the fill-in --------------------------------------------------------------------------------

FILL_SOLUTION = '''import numpy as np


class Dropout:
    """Inverted dropout: in training, zero each value with probability p and scale the survivors by 1 / (1 - p), so the expected sum is unchanged and eval needs no correction."""

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


layer = Dropout(0.5, seed=0)
X = np.ones((1000, 20))
dropped = layer.forward(X)
print(round(float((dropped == 0).mean()), 1), round(float(dropped.mean()), 1), np.unique(dropped).tolist())
layer.training = False
print(bool((layer.forward(X) == X).all()))
'''
FILL_STARTER = FILL_SOLUTION.replace("        self.mask = (self.rng.random(X.shape) >= self.p) / (1 - self.p)", "        self.mask = (self.rng.random(X.shape) >= ...) / (1 - ...)")
FILL_WRONG = FILL_SOLUTION.replace("        self.mask = (self.rng.random(X.shape) >= self.p) / (1 - self.p)", "        self.mask = (self.rng.random(X.shape) >= self.p) * 1.0")
FILL_OUT = out(FILL_SOLUTION)
assert FILL_OUT == "0.5 1.0 [0.0, 2.0]\nTrue\n", FILL_OUT
assert differs(FILL_WRONG, FILL_OUT)

# --- the write ----------------------------------------------------------------------------------

WRITE_SOLUTION = '''def early_stopping(val_losses, patience):
    """Walk the validation losses epoch by epoch (from 1): return the epoch with the lowest loss so far and the epoch at which training stops, which is the first one that is `patience` epochs past the best, or the last epoch if that never happens."""
    best_epoch, best = 1, val_losses[0]
    for epoch, value in enumerate(val_losses, start=1):
        if value < best:
            best, best_epoch = value, epoch
        elif epoch - best_epoch >= patience:
            return best_epoch, epoch
    return best_epoch, len(val_losses)


print(early_stopping([1.0, 0.8, 0.75, 0.9, 0.85, 0.7, 0.72, 0.74, 0.8], patience=3))
print(early_stopping([0.6, 0.5, 0.45, 0.44], patience=2))
print(early_stopping([0.5, 0.5, 0.5, 0.5], patience=2))
'''
WRITE_TAIL = "print(early_stopping" + WRITE_SOLUTION.split("\n\n\nprint(early_stopping", 1)[1]
WRITE_OUT = out(WRITE_SOLUTION)
assert WRITE_OUT == "(6, 9)\n(4, 4)\n(1, 3)\n", WRITE_OUT
WRITE_NO_PATIENCE = WRITE_SOLUTION.replace("        elif epoch - best_epoch >= patience:", "        elif epoch - best_epoch >= 1:")
WRITE_TIES_IMPROVE = WRITE_SOLUTION.replace("        if value < best:", "        if value <= best:")
assert differs(WRITE_NO_PATIENCE, WRITE_OUT) and differs(WRITE_TIES_IMPROVE, WRITE_OUT)

# --- the build ----------------------------------------------------------------------------------

BUILD_TAIL = '''

X_train, y_train = make_blobs(20, seed=1, spread=1.8)
X_val, y_val = make_blobs(100, seed=2, spread=1.8)
loss = SoftmaxCrossEntropy()


def new_net(dropout=0.0):
    layers = [Dense(2, 64, seed=1, scale=1.0), ReLU()]
    if dropout:
        layers.append(Dropout(dropout, seed=5))
    layers += [Dense(64, 64, seed=2, scale=np.sqrt(2 / 64)), ReLU()]
    if dropout:
        layers.append(Dropout(dropout, seed=6))
    layers.append(Dense(64, 3, seed=3))
    return Sequential(layers)


plain = fit(new_net(), loss, Adam(0.01), X_train, y_train, X_val, y_val, epochs=300)
decayed = fit(new_net(), loss, Adam(0.01, weight_decay=0.03), X_train, y_train, X_val, y_val, epochs=300)
dropped = fit(new_net(dropout=0.5), loss, Adam(0.01), X_train, y_train, X_val, y_val, epochs=300)
stopped = fit(new_net(), loss, Adam(0.01), X_train, y_train, X_val, y_val, epochs=300, patience=20)
print(read_fit(plain), round(min(plain["val_loss"]), 3), round(plain["val_loss"][-1], 3))
print(read_fit(decayed), round(decayed["val_loss"][-1], 3), read_fit(dropped), round(dropped["val_loss"][-1], 3))
print(stopped["best_epoch"], stopped["stopped_at"], round(min(stopped["val_loss"]), 3), len(stopped["val_loss"]))
layer = Dropout(0.5, seed=0)
dropped_ones = layer.forward(np.ones((1000, 20)))
print(round(float((dropped_ones == 0).mean()), 1), round(float(dropped_ones.mean()), 1))
'''
BUILD_SOLUTION = "import numpy as np\n\n\n" + LAYERS + LOOP + BUILD_TAIL
BUILD_OUT = out(BUILD_SOLUTION)
print("build:\n" + BUILD_OUT)
BUILD_LINES = BUILD_OUT.splitlines()
assert BUILD_LINES[0].startswith("overfitting ") and BUILD_LINES[1].startswith("holding "), BUILD_OUT
assert BUILD_LINES[2].startswith("28 48 ") and BUILD_LINES[3] == "0.5 1.0", BUILD_OUT
assert out(BUILD_SOLUTION.replace("X_train, y_train = make_blobs(20, seed=1, spread=1.8)", "X_train, y_train = make_blobs(20, seed=1, spread=1.8)\nX_train[0, 0] += 1e-10")) == BUILD_OUT
DECAYED_PREFIX = BUILD_LINES[1].split(" ", 2)[0] + " " + BUILD_LINES[1].split(" ", 2)[1] + " "
assert DECAYED_PREFIX.startswith("holding "), DECAYED_PREFIX
BUILD_WRONGS = {
    "dropout-not-scaled": BUILD_SOLUTION.replace("        self.mask = (self.rng.random(X.shape) >= self.p) / (1 - self.p)", "        self.mask = (self.rng.random(X.shape) >= self.p) * 1.0"),
    "dropout-on-at-eval": BUILD_SOLUTION.replace("    net.eval()\n    logits = net.forward(X)", "    logits = net.forward(X)"),
    "decay-pushes-outwards": BUILD_SOLUTION.replace("            grad = grad + self.weight_decay * param", "            grad = grad - self.weight_decay * param"),
    "never-restores-the-best": BUILD_SOLUTION.replace("    if patience is not None and best_params is not None:\n        for param, best in zip(net.parameters(), best_params):\n            param[...] = best\n", ""),
}
for key, code in BUILD_WRONGS.items():
    assert code != BUILD_SOLUTION, key

# --- the debug ----------------------------------------------------------------------------------

DEBUG_SOLUTION = "import numpy as np\n\n\n" + LAYERS + LOOP + '''

X_train, y_train = make_blobs(20, seed=1, spread=1.8)
X_val, y_val = make_blobs(100, seed=2, spread=1.8)
loss = SoftmaxCrossEntropy()
net = Sequential([Dense(2, 64, seed=1, scale=1.0), ReLU(), Dropout(0.5, seed=5), Dense(64, 3, seed=3)])
history = fit(net, loss, Adam(0.01, weight_decay=0.03), X_train, y_train, X_val, y_val, epochs=200)
again = evaluate(net, loss, X_val, y_val)
print("validation loss at the end:", round(history["val_loss"][-1], 3), "| evaluating twice gives the same answer:", again[0] == history["val_loss"][-1])
weights = net.layers[0].W
print("the first layer's weights shrank under decay:", bool(np.abs(weights).mean() < 0.5), "| validation accuracy:", round(history["val_accuracy"][-1], 2))
'''
BUG_NO_EVAL = ("    net.eval()\n    logits = net.forward(X)", "    logits = net.forward(X)")
BUG_DECAY_SIGN = ("            grad = grad + self.weight_decay * param", "            grad = grad - self.weight_decay * param")
DEBUG_STARTER = DEBUG_SOLUTION.replace(*BUG_NO_EVAL).replace(*BUG_DECAY_SIGN)
DEBUG_STILL_NO_EVAL = DEBUG_SOLUTION.replace(*BUG_NO_EVAL)
DEBUG_STILL_SIGN = DEBUG_SOLUTION.replace(*BUG_DECAY_SIGN)
DEBUG_OUT = out(DEBUG_SOLUTION)
STARTER_OUT = out(DEBUG_STARTER)
print("debug:\n" + DEBUG_OUT + "starter:\n" + STARTER_OUT)
assert DEBUG_OUT.splitlines()[0].endswith("evaluating twice gives the same answer: True") and DEBUG_OUT.splitlines()[1].startswith("the first layer's weights shrank under decay: True"), DEBUG_OUT
assert STARTER_OUT.splitlines()[0].endswith("False") and STARTER_OUT.splitlines()[1].startswith("the first layer's weights shrank under decay: False"), STARTER_OUT
assert out(DEBUG_STILL_NO_EVAL).splitlines()[0].endswith("False") and out(DEBUG_STILL_SIGN).splitlines()[1].startswith("the first layer's weights shrank under decay: False")
assert out(DEBUG_SOLUTION.replace("X_train, y_train = make_blobs(20, seed=1, spread=1.8)", "X_train, y_train = make_blobs(20, seed=1, spread=1.8)\nX_train[0, 0] += 1e-10")) == DEBUG_OUT

REVIEW_CODE_SOLUTION = '''def early_stopping(val_losses, patience):
    """The epoch (from 1) with the lowest loss so far, and the epoch at which training stops: patience epochs past the best, or the last."""
    best_epoch, best = 1, val_losses[0]
    for epoch, value in enumerate(val_losses, start=1):
        if value < best:
            best, best_epoch = value, epoch
        elif epoch - best_epoch >= patience:
            return best_epoch, epoch
    return best_epoch, len(val_losses)


print(early_stopping([1.0, 0.8, 0.7, 0.75, 0.74, 0.76, 0.77, 0.9], patience=4))
print(early_stopping([1.0, 0.9, 0.8], patience=4))
'''
REVIEW_CODE_OUT = out(REVIEW_CODE_SOLUTION)
assert REVIEW_CODE_OUT == "(3, 7)\n(3, 3)\n", REVIEW_CODE_OUT
REVIEW_CODE_WRONG = REVIEW_CODE_SOLUTION.replace("        elif epoch - best_epoch >= patience:", "        elif epoch - best_epoch > patience:")
assert differs(REVIEW_CODE_WRONG, REVIEW_CODE_OUT)

# =====================================================================================
# topic.yaml
# =====================================================================================

write(
    "topic.yaml",
    '''id: ml.nn.regularization
kind: topic
status: ready
title: "Regularization: learning what generalizes"
summary: "Overfitting seen as training loss falling while validation loss rises; weight decay; dropout with its train and eval modes; early stopping; and more data as the regularizer that always works."
prerequisites: [ml.nn.training-loop]
packages: [numpy]
estimated_minutes: 50
rev: 1
objectives:
  - "Produce and recognize overfitting from the training and validation curves."
  - "Implement weight decay as a term in the gradient, and inverted dropout as a layer with train and eval modes."
  - "Implement early stopping on validation loss with patience."
  - "Say what each regularizer assumes about the data and when it hurts."
# Linked, never copied or embedded: Wikipedia is CC BY-SA 4.0.
resources:
  - title: "Wikipedia: Overfitting (what it is, the picture of a model that fits the noise, and the Machine learning section)"
    url: https://en.wikipedia.org/wiki/Overfitting
    type: reading
    use: link
    license: CC BY-SA 4.0 (linked, not copied)
  - title: "Wikipedia: Dropout (neural networks) (the idea and where it came from; the training-time scaling and the eval switch are in this lesson)"
    url: https://en.wikipedia.org/wiki/Dilution_(neural_networks)
    type: reading
    use: link
    license: CC BY-SA 4.0 (linked, not copied)
  - title: "Wikipedia: Early stopping (the Validation-based early stopping section: stopping when the validation error rises and keeping the earlier weights; this lesson adds the patience)"
    url: https://en.wikipedia.org/wiki/Early_stopping
    type: reading
    use: link
    license: CC BY-SA 4.0 (linked, not copied)
practice:
  - example-overfitting-and-three-cures
  - mcq-reading-the-two-curves
  - predict-a-decay-step
  - mcq-what-weight-decay-assumes
  - predict-inverted-dropout
  - mcq-why-dropout-scales
  - predict-early-stopping
  - parsons-early-stopping
  - mcq-why-patience
  - mcq-when-regularizers-hurt
  - fill-dropout
  - write-early-stopping
prove:
  build: build-the-regularizers
  debug: debug-a-regularizer-that-backfired
  explain:
    prompt: |
      Three teammates. The first has a model at 100 percent training accuracy and 70 percent on held-out data and wants to train it longer. The second added dropout and saw the validation loss get worse, then found that their evaluation code never switches the network to eval mode. The third asks whether early stopping is cheating, since it looks at the validation set. In your own words: how to recognize overfitting from the two curves and what it means; what weight decay and dropout each change in training, what each assumes about a good model, and when each hurts; why dropout must be off at evaluation and what inverted dropout's scaling is for; and what early stopping does, why it has a patience, and whether it is cheating.
    rubric:
      - id: overfitting
        required: true
        description: "Training loss keeps falling while validation loss reaches a low and rises: the network is fitting the noise of the training rows, which a held-out set doesn't share. Training longer makes it worse; the fixes are regularization, stopping at the low, or more data, which is the one that always works because the noise doesn't repeat."
      - id: decay
        required: true
        description: "Weight decay adds decay times the weight to every gradient, a steady pull towards zero, so large weights have to earn their keep; it assumes a good model is a smooth one with small weights, and it hurts when the data needs sharp features or the network is already too small (underfitting)."
      - id: dropout
        required: true
        description: "Dropout zeroes each hidden value with probability p during training and scales the survivors by 1 / (1 - p), so no unit can rely on another and the expected activation is unchanged; at evaluation it passes everything through. Left on at evaluation it adds noise and the predictions get worse, which was the second teammate's bug. It assumes redundancy helps, and it hurts small layers, where dropping a share of the units is losing that share of the model."
      - id: early-stopping
        required: true
        description: "Early stopping watches the validation loss and stops once it hasn't improved for patience epochs, restoring the weights from the best epoch; the patience skips over the ordinary wobble of a curve. It uses the validation set to choose when to stop, which is what the validation set is for, so it is not cheating; the final test set, touched once, is what must stay unseen."
    model_answer: |
      Overfitting shows in the gap between the two curves. The training loss keeps falling, because the network has enough weights to fit every training row, noise included, while the validation loss falls to a low point and then rises, because the noise it memorized doesn't repeat in rows it hasn't seen. A model at 100 percent on training and 70 percent on held-out data is already there, and training longer only deepens the fit to the noise; the first teammate should stop earlier, regularize, or get more data. More data is the regularizer that always works, because noise doesn't repeat but structure does: the example's run on twenty times the data kept its validation loss near its low where the small run's more than quadrupled. Weight decay adds decay times the weight itself to every gradient, so each step shrinks every weight a little towards zero and a weight is only kept large if the data keeps pushing it back; it assumes that a good model is a smooth one with small weights, which is usually true, and it hurts when the data really needs sharp boundaries or the network is already too small to fit the training set, where it makes underfitting worse. Dropout zeroes each hidden value with probability p during every training step, a different random set each time, and scales the survivors by one over one minus p, so that no unit can depend on a particular other unit being there and the network learns redundant, spread-out features; the scaling keeps the expected value of each activation what it would have been, which is why nothing has to change at evaluation. At evaluation dropout is switched off and every unit passes through; the second teammate left it on, so their validation predictions were made by a randomly thinned network with extra noise, which is why they got worse, and evaluating twice gave two different answers. Dropout assumes redundancy helps, which it does in wide layers; it hurts small layers, where losing half the units is losing half the model, and it slows training, which is why it is paired with more epochs. Early stopping watches the validation loss after every epoch, remembers the weights of the best epoch, and stops once the loss hasn't improved for a set number of epochs, the patience, then restores the best weights. The patience exists because a validation curve wobbles from epoch to epoch and a single bad epoch shouldn't end the run; twenty epochs of no improvement is a trend. It isn't cheating: choosing when to stop is a decision about training, and the validation set is the set we keep aside for exactly such decisions, which is why it was separated from the training rows in the first place. What must stay unseen is the final test set, used once at the very end, because every decision made with the validation set makes its score a little optimistic, and that is the number we don't want to fool ourselves with.
review_pool:
  - review-predict-decay-shrinks
  - review-mcq-dropout-at-eval
  - review-mcq-more-data
  - review-early-stopping
# What this topic teaches. Each question names the skills it tests, so a
# missed question can come back as a different one on the same skill
# (ADR-0011).
skills:
  - id: overfitting
    description: "Produce and recognize overfitting from the training and validation curves, and say what it means"
  - id: decay
    description: "Implement weight decay as a term in the gradient, and say what it assumes and when it hurts"
  - id: dropout
    description: "Implement inverted dropout with train and eval modes, and say why the scaling and the switch matter"
  - id: early-stopping
    description: "Implement early stopping on validation loss with patience, restoring the best weights"
''',
)

# =====================================================================================
# lesson.mdx
# =====================================================================================

write(
    "lesson.mdx",
    f'''<Intro>

A network with more weights than data points can fit the training rows perfectly, noise and all, and the loss curve that proves it is the one every practitioner learns to dread: training loss still falling, validation loss turning upwards. This topic makes that happen on purpose, sixty noisy points and a network of two hidden layers of 64, and then applies the three standard cures, **weight decay**, **dropout** and **early stopping**, measuring each against the plain run, before showing the one cure that always works: more data.

The main resource is **Wikipedia's _Overfitting_ page**, which has the picture of a curve fitting noise and the machine-learning section; about 10 minutes. The _Dropout_ page explains the training-time scaling and why nothing changes at test time, and the _Early stopping_ page covers patience and keeping the best weights. Watch for:

- **Generalization**: the gap between the training score and the held-out score.
- **The scaling in dropout**: why survivors are multiplied by 1 / (1 - p).
- **Patience**: why early stopping waits before it stops.

</Intro>

<Resource index={{0}} />

<Recap>

- **Overfitting** is the training loss falling while the validation loss, after a low point, rises: the network is fitting the noise of its training rows, which rows it hasn't seen don't share. In the example the plain run's training loss reached {EX[8].split("train loss ")[1].split(" |")[0]} while its validation loss fell to {PLAIN_LOW} at epoch {PLAIN_BEST} and climbed to {PLAIN_END} by epoch 300. Training longer makes it worse. The opposite failure, both losses high, is **underfitting**: a model too small or a run too short.
- **Weight decay** adds `decay * W` to every gradient (L2 regularization), a steady pull towards zero that each step applies: under plain gradient descent with no other gradient a weight shrinks by the factor `1 - rate * decay` per step (Adam rescales the pull as it does any gradient, but the direction is the same). Large weights have to earn their keep against the data. At 0.03 the example's validation loss ended at {DECAY_END}, holding near its low. It assumes a good model is a smooth one with small weights; it hurts when the data needs sharp boundaries or the network is already too small, and libraries usually leave biases out of it (this topic's `Adam` decays them too, for simplicity).
- **Dropout** zeroes each hidden value with probability `p` during training, a fresh random mask every step, and scales the survivors by `1 / (1 - p)` (**inverted dropout**) so that the expected activation is unchanged and nothing needs correcting at evaluation. No unit can rely on a particular other unit, so the network learns spread-out, redundant features. It is a layer with two modes: `Sequential.train()` turns dropping on, `Sequential.eval()` turns it off, and `fit` and `evaluate` must switch between them. At 0.5 the example's validation loss ended at {DROPOUT_END}: the rise is shrunk, not abolished. It hurts small layers and slows training.
- **Early stopping** watches the validation loss after every epoch, keeps a copy of the weights from the best epoch, and stops once the loss hasn't improved for `patience` epochs, then restores the best weights. The patience skips the ordinary wobble of a curve: on the plain run with a patience of 20, training stopped at epoch {STOPPED_AT} and kept the weights of epoch {PLAIN_BEST}, the low point. The accuracy there, {STOP_ACC}, is below the {PLAIN_ACC} of epoch 300: the loss climbed not because more points were missed but because the points still missed were missed with growing confidence, which the log-loss punishes and a count of right answers can't see. Loss moves smoothly and sees that overconfidence, which is why early stopping usually watches it. It is not cheating: choosing when to stop is what the validation set is for; the test set, touched once at the end, is what must stay unseen.
- **More data** is the regularizer that always works, because structure repeats and noise doesn't: twenty times the training rows kept the validation loss at {MORE_END} after 300 epochs where the small run's reached {PLAIN_END}. When more data can't be had, **data augmentation** (shifted, flipped, noised copies of what there is) is the next best thing, and the checkpoint's digits are drawn with random shifts and noise, the same idea.
- **What each assumes.** Weight decay: smooth is better. Dropout: redundancy is better. Early stopping: the validation low is the place to be. More data: the new rows come from the same distribution as the old. Each helps when its assumption holds and hurts when it doesn't, which is why the validation curve, not the training curve, is what decides.
- **This topic's `fit`** is The training loop's with three changes: it trains full-batch (sixty rows is one batch, so `batch_size` and `seed` are gone), it switches the network between train and eval modes, and it takes a `patience`; its history still starts after the first epoch.
- **In machine learning** (names you'll meet later): `weight_decay` is the optimizer argument (and **AdamW** applies it to the weights directly rather than through the gradient); `nn.Dropout`, `model.train()` and `model.eval()` are the two modes, and forgetting the switch is the classic evaluation bug; `EarlyStopping` callbacks and checkpoints that save the best weights are this topic's `fit`; and **batch normalization** regularizes a little as a side effect of the noise in its batch statistics.

</Recap>
''',
)

# =====================================================================================
# recall
# =====================================================================================

mcq(
    "mcq-reading-the-two-curves",
    "After 50 epochs a run's training loss has fallen from 1.1 to 0.05 and its validation loss has gone 1.0, 0.6, 0.5, 0.55, 0.7, 0.9. What is happening, and what helps?",
    [
        "Underfitting: the network is too small; add layers and train longer",
        "Overfitting: the network is fitting the training rows' noise, which held-out rows don't share; stop at the low, regularize, or get more data",
        "The learning rate is too high: the training loss would not have fallen so far otherwise",
        "Nothing: the validation loss on a few hundred held-out rows is noisy, so a rise from 0.5 to 0.9 is within the wobble and will come back down with more epochs",
    ],
    1,
    "A falling training loss beside a validation loss that bottoms out and rises is the signature of overfitting: the extra fit is to noise. Training longer deepens it. Early stopping at the low, weight decay, dropout, or more training rows are the fixes. Underfitting would show both losses high, and a too-high rate would show the training loss misbehaving too. A rise from 0.5 to 0.9 on a few hundred held-out rows is far beyond the wobble of a noisy curve.",
    ["overfitting"],
)

write(
    "recall/predict-a-decay-step.yaml",
    f'''id: predict-a-decay-step
type: predict_output
rev: 1
prompt: |
  Three steps of weight decay with no other gradient: each step subtracts the learning rate times the decay times the weight itself. What does the program print?
code: |
{block(PREDICT_DECAY)}expected_output: |
{block(PREDICT_DECAY_OUT)}explanation: |
  With the data's gradient at zero, the only pull is the decay's: each step multiplies every weight by `1 - rate * decay`, here 0.95, towards zero from either side. Signs are kept, and the weights shrink by five percent a step however large they are; a weight is kept large only if the data keeps pushing it back out.
skills: [decay]
''',
)

mcq(
    "mcq-what-weight-decay-assumes",
    "Weight decay adds `decay * W` to the gradient of every weight. What does that assume about a good model, and when does it hurt?",
    [
        "It assumes the weights should all end up equal; it hurts when the inputs have different scales",
        "It assumes a good model is a smooth one with small weights; it hurts when the data needs sharp boundaries or the network is already too small, where it deepens underfitting",
        "It assumes the training set is noisy and shrinks the weights to average the noise out; it hurts whenever the data is clean, where there is no noise to average and the shrinking only loses fit",
        "It assumes a large learning rate; it hurts with Adam, which already scales the steps",
    ],
    1,
    "The pull towards zero means a weight stays large only if the data keeps pushing it back, so the fitted function is smoother and less able to chase single points. That is what most data wants and what noisy data needs, but a network that can't yet fit the training set is made worse by it, and so is a problem whose true boundary really is sharp. It is used with Adam constantly; the inputs' scales are a separate matter, and clean data doesn't make decay hurt; too little capacity does.",
    ["decay"],
)

write(
    "recall/predict-inverted-dropout.yaml",
    f'''id: predict-inverted-dropout
type: predict_output
rev: 1
prompt: |
  Inverted dropout by hand: a row of four values, a keep mask that drops two of them, and the scaling by `1 / (1 - p)` with `p = 0.5`; then another mask. What does the program print?
code: |
{block(PREDICT_DROPOUT)}expected_output: |
{block(PREDICT_DROPOUT_OUT)}explanation: |
  The dropped values become 0 and the survivors are doubled, so the mask that keeps the first and third values (2 and 6, doubled to 4 and 12) sums to 16 and one that keeps three sums to 28, against the original 20: each mask's sum is off, but the average over many masks is the original, which is what the scaling is for. The input itself is never changed.
skills: [dropout]
''',
)

mcq(
    "mcq-why-dropout-scales",
    "Inverted dropout multiplies the values it keeps by `1 / (1 - p)`. Why?",
    [
        "So each activation's expected value is unchanged and the network needs no correction at evaluation, when nothing is dropped",
        "To make the kept values larger than the dropped ones, so the next layer can tell which units survived this step and which were dropped, and route its gradient to the survivors",
        "Because the gradient would otherwise be zero for the kept values",
        "To keep the weights from growing, like weight decay",
    ],
    0,
    "If half the values are zeroed and the rest left alone, the layer's output is about half its usual size during training and full size at evaluation, and the next layer sees two different scales. Doubling the survivors keeps the training-time average equal to the evaluation-time value, so the same weights work in both modes. The dropped values carry no gradient either way, and the weights are untouched.",
    ["dropout"],
)

write(
    "recall/predict-early-stopping.yaml",
    f'''id: predict-early-stopping
type: predict_output
rev: 1
prompt: |
  `early_stopping` walks a list of validation losses, one per epoch, and returns the epoch with the lowest loss and the epoch at which training stops: the first epoch that is `patience` epochs past the best, or the last epoch. What does the program print for the two lists?
code: |
{block(PREDICT_STOP)}expected_output: |
{block(PREDICT_STOP_OUT)}explanation: |
  In the first list the loss is lowest at epoch 3 (0.6); epochs 4 and 5 don't beat it, and epoch 6 is three epochs past the best, so training stops there and the weights of epoch 3 are the ones to keep. In the second list every epoch improves on the last, so the run goes to the end and the best epoch is the last.
skills: [early-stopping]
''',
)

write(
    "recall/parsons-early-stopping.yaml",
    "id: parsons-early-stopping\ntype: parsons\nrev: 1\nprompt: |\n"
    + block("Put the lines in order to walk a list of validation losses, remember the best epoch, stop three epochs after it, and print `3 6` (the best epoch and the one that stopped). One line is a decoy that doesn't belong.")
    + "lines:\n"
    + "".join(f"  - {quoted(line)}\n" for line in PARSONS_LINES)
    + "distractors:\n  - "
    + quoted("    if value <= best:")
    + "\nexplanation: |\n"
    + block("The best starts as the first loss; each epoch either beats it and becomes the new best, or counts against the patience, and the loop breaks at the third epoch past the best. The decoy treats an equal loss as an improvement: on this list it would move the best to epoch 4 and stop at 7, printing `4 7`, and on a flat stretch it would keep resetting the patience.")
    + "skills: [early-stopping]\n",
)

mcq(
    "mcq-why-patience",
    "Early stopping waits for `patience` epochs without improvement before it stops, and then restores the best weights. Why both?",
    [
        "The validation loss wobbles, so one bad epoch isn't a trend; and by the time the patience runs out the network has moved past its best, so the saved copy is the one to keep",
        "Because the optimizer needs a few extra epochs to flush its momentum, and the weights at the stopping epoch are the ones the momentum has settled on, so they are the ones to keep",
        "Because stopping on the first rise would always stop at epoch 2",
        "Because the training loss must also have stopped improving",
    ],
    0,
    "A curve measured on a few hundred held-out rows is noisy, so improvement is judged over a window; twenty epochs of nothing better is a trend where one is a wobble. By the time the window has run out the network has moved on from its best point, so the saved copy from the best epoch is what is kept. Momentum and the training loss don't enter into it, and stopping on the first rise would not always stop at epoch 2, but it would stop on the first wobble.",
    ["early-stopping"],
)

mcq(
    "mcq-when-regularizers-hurt",
    "A small network underfits: training and validation loss are both high and still falling slowly. A teammate adds weight decay and dropout. What happens?",
    [
        "Both losses fall faster, since regularizers always help",
        "Both get worse: decay and dropout limit what the network can fit, and this network can't fit the training set as it is; it needs more capacity or more epochs, not less",
        "The validation loss falls and the training loss rises until the two curves meet, since regularizers exist to close the gap between them whichever way it runs, so the fit improves",
        "Nothing changes, since regularizers only act once the training loss is near zero",
    ],
    1,
    "Regularizers trade fitting power for generalization. That is the right trade when the network has power to spare, which overfitting shows; when it hasn't, as both losses high show, taking power away makes the fit worse on both sets. The signal to read is the gap between the curves: a gap calls for regularizing, two high curves call for a bigger model or a longer run.",
    ["overfitting"],
)

write(
    "recall/review-predict-decay-shrinks.yaml",
    f'''id: review-predict-decay-shrinks
type: predict_output
rev: 1
prompt: |
  Weights of 1 under a learning rate of 0.1 with no data gradient: ten steps without decay, ten with decay 0.1, and a hundred with decay 0.1. What does the program print?
code: |
{block(REVIEW_DECAY)}expected_output: |
{block(REVIEW_DECAY_OUT)}explanation: |
  Without decay nothing moves. With decay each step multiplies the weight by 1 minus 0.1 times 0.1, which is 0.99: ten steps leave 0.904 and a hundred leave 0.366. A weight the data doesn't defend fades away at a rate set by the learning rate times the decay.
skills: [decay]
''',
)

mcq(
    "review-mcq-dropout-at-eval",
    "A network with dropout gives a different validation loss every time it is evaluated, and a worse one than expected. What is the most likely cause?",
    [
        "The validation set is being reshuffled between evaluations, and the loss is computed on whichever rows come first, so the rows measured differ each time",
        "Dropout is still on: the network was never switched to eval mode, so each evaluation runs a randomly thinned network with extra noise",
        "Weight decay is too strong, which makes the outputs random",
        "The learning rate is too high for a dropout network",
    ],
    1,
    "In training mode dropout draws a fresh mask on every forward pass, so two evaluations differ and both are noisier than the full network. `eval()` turns the dropping off; `fit` and `evaluate` must call it before measuring, and `train()` before each training step. Evaluation itself doesn't shuffle, and neither decay nor the rate makes a fixed network give two different answers.",
    ["dropout"],
)

mcq(
    "review-mcq-more-data",
    "Why is more training data called the regularizer that always works, when weight decay and dropout sometimes hurt?",
    [
        "Because more data makes the network bigger",
        "Because structure repeats across new rows while noise doesn't, so there is less noise to fit and more signal to learn, with no assumption about what a good model looks like",
        "Because more data lets the learning rate be larger and the batches be bigger, so each epoch takes more and surer steps, which is what keeps the validation loss from rising at the end",
        "Because it makes the validation set unnecessary",
    ],
    1,
    "Decay assumes small weights are better and dropout assumes redundancy is better; each helps when its assumption holds. More rows from the same source change the problem itself: the noise in any one row is diluted and the patterns are confirmed. The network's size, the rate and the validation set are all unchanged. When more data can't be had, augmented copies are the next best thing.",
    ["overfitting"],
)

# =====================================================================================
# exercises
# =====================================================================================

write(
    "exercises/example-overfitting-and-three-cures/exercise.yaml",
    f'''id: example-overfitting-and-three-cures
stage: worked_example
rev: 1
title: "Overfitting, and three cures"
prompt: |
  Sixty noisy points, a network of two hidden layers of 64, and 300 epochs of Adam: the validation loss turns upwards while the training loss keeps falling. Then the same run with weight decay, with dropout, with early stopping, and with twenty times the data. Press **Run**, then read how each part works.
steps:
  - label: "Dropout, two modes, and decay in the optimizer"
    lines: "{ln('class Dropout:')}-{ln('param -= self.rate * m_hat')}"
    note: "`Dropout` keeps a mask of which values survived and the scaling `1 / (1 - p)`; in eval mode it passes everything through and its backward does too. `Sequential.train()` and `eval()` flip the mode of every layer that has one. `Adam` adds `weight_decay * param` to each gradient before anything else: the pull towards zero."
  - label: "fit with early stopping, and reading the curve"
    lines: "{ln('def make_blobs')}-{ln('return "holding"')}"
    note: "`fit` trains full-batch (sixty rows is one batch), switching to train mode before the step and eval mode before measuring; it remembers the epoch with the lowest validation loss and a copy of the weights from it, and with a `patience` it stops once that many epochs have passed without a new low and restores the copy. `read_fit` names what the validation loss did after its low: more than doubled is overfitting, up by a tenth is drifting, else holding."
  - label: "The plain run"
    lines: "{ln('X_train, y_train = make_blobs(20')}-{ln('report("plain", plain)')}"
    note: "Twenty noisy points per class to train on and a hundred per class held out, from clouds that overlap. The training loss falls all the way to {EX[8].split("train loss ")[1].split(" |")[0]}; the validation loss falls to {PLAIN_LOW} at epoch {PLAIN_BEST} and then climbs to {PLAIN_END}, the bars lengthening again: the network is fitting the noise in its sixty points."
  - label: "Weight decay and dropout"
    lines: "{ln('report("weight decay 0.03"')}-{ln('report("dropout 0.5"')}"
    note: "With decay 0.03 the validation loss ends at {DECAY_END}, holding near its low, because weights that only fit noise are pulled back towards zero. With dropout 0.5 on both hidden layers it ends at {DROPOUT_END}: the rise is shrunk, not abolished, and the training loss stays higher, since the network trains thinned."
  - label: "Early stopping"
    lines: "{ln('stopped = fit(new_net()')}-{ln('early stopping, patience 20')}"
    note: "The plain run again, with a patience of 20: training stops at epoch {STOPPED_AT}, twenty epochs after the low at epoch {PLAIN_BEST}, and the weights from epoch {PLAIN_BEST} are restored, so the network is left at its best validation loss instead of its worst. Its accuracy there, {STOP_ACC}, is lower than the plain run's {PLAIN_ACC} at epoch 300: the loss rose because the points still missed were missed ever more confidently, each costing a large log-loss, not because more were missed. Loss, which moves smoothly, is what early stopping watches; accuracy moves in steps of one row."
  - label: "Twenty times the data"
    lines: "{ln('X_more, y_more = make_blobs(400')}-{ln('report("twenty times the data"')}"
    note: "Four hundred points per class and the same network for the same 300 epochs: the validation loss ends at {MORE_END}. Structure repeats across new rows and noise doesn't, so there is less noise to fit; more data is the regularizer that needs no assumption."
''',
)
write("exercises/example-overfitting-and-three-cures/solution.py", EXAMPLE)
write(
    "exercises/example-overfitting-and-three-cures/test_exercise.py",
    f'''from checks import run


def test_the_walkthrough():
    """Prints the plain run's curve and the five reports."""
    assert run() == {EXAMPLE_OUT!r}
''',
)

write(
    "exercises/fill-dropout/exercise.yaml",
    f'''id: fill-dropout
stage: fill_in
rev: 1
title: "Inverted dropout"
prompt: |
  In training mode, `Dropout.forward` should zero each value with probability `p` and scale the survivors by `1 / (1 - p)`; in eval mode it passes everything through. The mask is built from uniform random numbers: a value survives when its number is at least `p`. Replace each `...` so the program prints the dropped fraction and the mean of a thousand rows of ones (rounded to one decimal), the values that appear, and `True` for eval mode:

  ```
{block(FILL_OUT)}  ```

  The program fails until every `...` is replaced.
hints:
  - "A uniform number is at least `p` with probability `1 - p`, so the comparison against `p` keeps the right share."
  - "Dividing the kept ones by `1 - p` makes each survivor 2 at `p = 0.5`, so the mean over many values stays 1."
skills: [dropout]
''',
)
write("exercises/fill-dropout/starter.py", FILL_STARTER)
write("exercises/fill-dropout/solution.py", FILL_SOLUTION)
write(
    "exercises/fill-dropout/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints the fraction, the mean, the two values and True."""
    printed = run()
    assert printed == {FILL_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_other_rates():
    """At p = 0.2 about a fifth is dropped and survivors are 1.25; backward passes the same mask; eval changes nothing."""
    Dropout = function("Dropout")
    layer = Dropout(0.2, seed=3)
    X = np.ones((2000, 10))
    out = layer.forward(X)
    assert 0.17 < (out == 0).mean() < 0.23 and np.allclose(out[out > 0], 1.25) and 0.95 < out.mean() < 1.05
    grad = layer.backward(np.ones_like(X))
    assert np.array_equal(grad == 0, out == 0) and np.allclose(grad[grad > 0], 1.25)
    layer.training = False
    assert np.array_equal(layer.forward(X), X) and np.array_equal(layer.backward(X), X)
''',
)
write("exercises/fill-dropout/wrong/never-scaled.py", FILL_WRONG)
write(
    "exercises/fill-dropout/wrong/typed-in.py",
    "import numpy as np\n\n\nclass Dropout:\n    def __init__(self, p, seed=0):\n        self.p = p\n        self.training = True\n\n    def forward(self, X):\n        return X\n\n    def backward(self, grad_out):\n        return grad_out\n\n\n" + "".join(f"print({line!r})\n" for line in FILL_OUT.splitlines()),
)

write(
    "exercises/write-early-stopping/exercise.yaml",
    f'''id: write-early-stopping
stage: write
rev: 1
title: "Early stopping, as a rule on a curve"
prompt: |
  Write `early_stopping(val_losses, patience)`: walk the validation losses epoch by epoch (epochs count from 1), track the epoch with the lowest loss so far (a strict improvement; an equal loss doesn't count), and return the tuple `(best_epoch, stop_epoch)`, where `stop_epoch` is the first epoch that is `patience` epochs past the best, or the last epoch if the run never stalls that long. Called on the three lists in the starter, the program prints:

  ```
{block(WRITE_OUT)}  ```
hints:
  - "Keep `best` and `best_epoch`; on each epoch either update them or test `epoch - best_epoch >= patience`."
  - "A flat curve never improves after epoch 1, so with a patience of 2 it stops at epoch 3."
skills: [early-stopping]
''',
)
write("exercises/write-early-stopping/starter.py", "# Write early_stopping here, above the calls.\n\n\n" + WRITE_TAIL)
write("exercises/write-early-stopping/solution.py", WRITE_SOLUTION)
write(
    "exercises/write-early-stopping/test_exercise.py",
    f'''from checks import function, run


def test_the_output():
    """Prints the three pairs."""
    printed = run()
    assert printed == {WRITE_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_other_curves():
    """A late recovery after a wobble resets the patience; a single epoch stops at 1; patience 1 stops at the first non-improvement."""
    early_stopping = function("early_stopping")
    assert early_stopping([1.0, 0.9, 0.95, 0.85, 0.9, 0.9, 0.9, 0.9], patience=3) == (4, 7)
    assert early_stopping([0.3], patience=5) == (1, 1)
    assert early_stopping([0.5, 0.4, 0.45, 0.3], patience=1) == (2, 3)
''',
)
write("exercises/write-early-stopping/wrong/no-patience.py", WRITE_NO_PATIENCE)
write("exercises/write-early-stopping/wrong/ties-count-as-better.py", WRITE_TIES_IMPROVE)
write(
    "exercises/write-early-stopping/wrong/typed-in.py",
    "def early_stopping(val_losses, patience):\n    return (3, 6)\n\n\n" + "".join(f"print({line!r})\n" for line in WRITE_OUT.splitlines()),
)

# --- the proof -----------------------------------------------------------------------------------

write(
    "exercises/build-the-regularizers/exercise.yaml",
    f'''id: build-the-regularizers
stage: build
rev: 1
title: "The regularizers"
prompt: |
  Starting from a blank editor, paste the module's `Dense`, `ReLU`, `Sequential` and `SoftmaxCrossEntropy` as they stand, then write:

  - `Dropout(p, seed=0)`: a layer with a `training` flag; in training, `forward` zeroes each value with probability `p` (a `np.random.default_rng(seed)` made once in `__init__` draws `rng.random(X.shape)` on every forward pass, and a value is dropped where its number is below `p`) and scales the rest by `1 / (1 - p)`, keeping the mask; `backward` applies the same mask; in eval mode both pass everything through. `parameters()` and `gradients()` are empty.
  - `Sequential.train()` and `Sequential.eval()`: set `training` on every layer that has it.
  - `Adam(rate, weight_decay=0.0, ...)`: the Adam of The training loop (an object with `step(params, grads)`), with `weight_decay * param` added to each gradient before the moments are updated.
  - `make_blobs(n_per_class, seed, spread=1.0)`: the three clouds, with the noise multiplied by `spread`.
  - `evaluate(net, loss, X, y)`: eval mode, then the loss and accuracy on the whole set.
  - `fit(net, loss, optimizer, X_train, y_train, X_val, y_val, epochs, patience=None)`: full-batch training, train mode before each step; a history with `train_loss`, `val_loss`, `val_accuracy`, `best_epoch` and `stopped_at`; with a `patience`, stop once the validation loss hasn't improved (strictly) for that many epochs and restore the weights of the best epoch.
  - `read_fit(history)`: `"overfitting"` if the last validation loss is more than twice the lowest, `"drifting up"` if more than 1.1 times, else `"holding"`.

  Then print:

  ```python
  X_train, y_train = make_blobs(20, seed=1, spread=1.8)
  X_val, y_val = make_blobs(100, seed=2, spread=1.8)
  loss = SoftmaxCrossEntropy()


  def new_net(dropout=0.0):
      layers = [Dense(2, 64, seed=1, scale=1.0), ReLU()]
      if dropout:
          layers.append(Dropout(dropout, seed=5))
      layers += [Dense(64, 64, seed=2, scale=np.sqrt(2 / 64)), ReLU()]
      if dropout:
          layers.append(Dropout(dropout, seed=6))
      layers.append(Dense(64, 3, seed=3))
      return Sequential(layers)


  plain = fit(new_net(), loss, Adam(0.01), X_train, y_train, X_val, y_val, epochs=300)
  decayed = fit(new_net(), loss, Adam(0.01, weight_decay=0.03), X_train, y_train, X_val, y_val, epochs=300)
  dropped = fit(new_net(dropout=0.5), loss, Adam(0.01), X_train, y_train, X_val, y_val, epochs=300)
  stopped = fit(new_net(), loss, Adam(0.01), X_train, y_train, X_val, y_val, epochs=300, patience=20)
  print(read_fit(plain), round(min(plain["val_loss"]), 3), round(plain["val_loss"][-1], 3))
  print(read_fit(decayed), round(decayed["val_loss"][-1], 3), read_fit(dropped), round(dropped["val_loss"][-1], 3))
  print(stopped["best_epoch"], stopped["stopped_at"], round(min(stopped["val_loss"]), 3), len(stopped["val_loss"]))
  layer = Dropout(0.5, seed=0)
  dropped_ones = layer.forward(np.ones((1000, 20)))
  print(round(float((dropped_ones == 0).mean()), 1), round(float(dropped_ones.mean()), 1))
  ```

  ```
{block(BUILD_OUT)}  ```

  The checks test dropout's two modes and its backward, decay's shrinking of an undefended weight, early stopping's stop epoch and restored weights, that the plain run overfits while the decayed one holds, and that the same seeds give the same numbers.
skills: [overfitting, decay, dropout, early-stopping]
''',
)
write("exercises/build-the-regularizers/starter.py", "")
write("exercises/build-the-regularizers/solution.py", BUILD_SOLUTION)
write(
    "exercises/build-the-regularizers/test_exercise.py",
    f'''import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7). Each test imports the solution
# once (its training runs on import) and takes what it needs from that one
# import.


def test_the_output():
    """Prints the four lines (the dropout run's last number may differ with how its mask is drawn; the plain and decayed runs may not)."""
    printed = run().splitlines()
    expected = {BUILD_OUT!r}.splitlines()
    assert len(printed) == 4 and printed[0] == expected[0] and printed[2] == expected[2] and printed[3] == expected[3]
    assert printed[1].startswith({DECAYED_PREFIX!r}) and printed[1].split()[2] in ("holding", "drifting")


def test_dropout_modes():
    """Training drops about p and scales survivors by 1 / (1 - p), backward uses the same mask, eval passes everything through, Sequential flips the modes, and evaluate measures with dropout off, giving the same answer twice."""
    fit = function("fit")
    Dropout, Sequential = (fit.__globals__[name] for name in ("Dropout", "Sequential"))
    layer = Dropout(0.25, seed=2)
    X = np.ones((2000, 8))
    out = layer.forward(X)
    assert 0.22 < (out == 0).mean() < 0.28 and np.allclose(out[out > 0], 4 / 3)
    assert np.array_equal(layer.backward(np.ones_like(X)) == 0, out == 0)
    net = Sequential([layer])
    net.eval()
    assert layer.training is False and np.array_equal(net.forward(X), X)
    net.train()
    assert layer.training is True
    evaluate, loss = fit.__globals__["evaluate"], fit.__globals__["SoftmaxCrossEntropy"]()
    rows = np.random.default_rng(3).standard_normal((40, 8))
    labels = np.random.default_rng(4).integers(0, 8, size=40)
    first = evaluate(net, loss, rows, labels)
    assert layer.training is False and first == evaluate(net, loss, rows, labels)


def test_weight_decay_shrinks():
    """With a zero data gradient, Adam with decay pulls a weight towards zero; without decay it stays."""
    Adam = function("fit").__globals__["Adam"]
    still = np.array([1.0, -2.0])
    Adam(0.01).step([still], [np.zeros(2)])
    assert np.allclose(still, [1.0, -2.0])
    pulled = np.array([1.0, -2.0])
    optimizer = Adam(0.01, weight_decay=0.1)
    for _ in range(50):
        optimizer.step([pulled], [np.zeros(2)])
    assert np.abs(pulled).max() < 1.9 and np.sign(pulled).tolist() == [1.0, -1.0]


def test_early_stopping_restores():
    """With a patience of 10 the run stops 10 epochs after its best, the history is that long, and the restored weights give the best validation loss."""
    fit = function("fit")
    Dense, ReLU, Sequential, SoftmaxCrossEntropy, Adam, make_blobs, evaluate = (fit.__globals__[name] for name in ("Dense", "ReLU", "Sequential", "SoftmaxCrossEntropy", "Adam", "make_blobs", "evaluate"))
    X_train, y_train = make_blobs(20, seed=1, spread=1.8)
    X_val, y_val = make_blobs(100, seed=2, spread=1.8)
    net = Sequential([Dense(2, 64, seed=1, scale=1.0), ReLU(), Dense(64, 64, seed=2, scale=np.sqrt(2 / 64)), ReLU(), Dense(64, 3, seed=3)])
    loss = SoftmaxCrossEntropy()
    history = fit(net, loss, Adam(0.01), X_train, y_train, X_val, y_val, epochs=300, patience=10)
    assert history["stopped_at"] == history["best_epoch"] + 10 and len(history["val_loss"]) == history["stopped_at"]
    assert abs(evaluate(net, loss, X_val, y_val)[0] - min(history["val_loss"])) < 1e-9


def test_overfitting_and_a_cure():
    """The plain run's validation loss more than doubles from its low; with decay 0.03 it holds; the same seeds repeat exactly."""
    fit = function("fit")
    Dense, ReLU, Sequential, SoftmaxCrossEntropy, Adam, make_blobs, read_fit = (fit.__globals__[name] for name in ("Dense", "ReLU", "Sequential", "SoftmaxCrossEntropy", "Adam", "make_blobs", "read_fit"))
    X_train, y_train = make_blobs(20, seed=1, spread=1.8)
    X_val, y_val = make_blobs(100, seed=2, spread=1.8)

    def net():
        return Sequential([Dense(2, 64, seed=1, scale=1.0), ReLU(), Dense(64, 64, seed=2, scale=np.sqrt(2 / 64)), ReLU(), Dense(64, 3, seed=3)])

    plain = fit(net(), SoftmaxCrossEntropy(), Adam(0.01), X_train, y_train, X_val, y_val, epochs=200)
    assert read_fit(plain) == "overfitting" and plain["train_loss"][-1] < 0.1
    decayed = fit(net(), SoftmaxCrossEntropy(), Adam(0.01, weight_decay=0.03), X_train, y_train, X_val, y_val, epochs=200)
    assert read_fit(decayed) == "holding" and decayed["val_loss"][-1] < plain["val_loss"][-1]
    again = fit(net(), SoftmaxCrossEntropy(), Adam(0.01), X_train, y_train, X_val, y_val, epochs=200)
    assert again["val_loss"] == plain["val_loss"]
    assert read_fit({{"val_loss": [1.0, 0.5, 0.55]}}) == "holding" and read_fit({{"val_loss": [1.0, 0.5, 0.6]}}) == "drifting up" and read_fit({{"val_loss": [1.0, 0.5, 1.2]}}) == "overfitting"
''',
)
for key, code in BUILD_WRONGS.items():
    write(f"exercises/build-the-regularizers/wrong/{key}.py", code)
write(
    "exercises/build-the-regularizers/wrong/typed-in.py",
    "import numpy as np\n\n\nclass Dropout:\n    def __init__(self, p, seed=0):\n        self.p = p\n        self.training = True\n\n    def forward(self, X):\n        return X\n\n    def backward(self, grad_out):\n        return grad_out\n\n\nclass Adam:\n    def __init__(self, rate, weight_decay=0.0):\n        self.rate = rate\n\n    def step(self, params, grads):\n        pass\n\n\ndef make_blobs(n_per_class, seed, spread=1.0):\n    return np.zeros((3 * n_per_class, 2)), np.repeat(np.arange(3), n_per_class)\n\n\ndef evaluate(net, loss, X, y):\n    return 0.0, 0.0\n\n\ndef fit(*args, **kwargs):\n    return {}\n\n\ndef read_fit(history):\n    return 'holding'\n\n\n"
    + "".join(f"print({line!r})\n" for line in BUILD_OUT.splitlines()),
)

write(
    "exercises/debug-a-regularizer-that-backfired/exercise.yaml",
    f'''id: debug-a-regularizer-that-backfired
stage: debug
rev: 1
title: "Two regularizers that backfired"
prompt: |
  A one-hidden-layer network with dropout, trained with Adam and weight decay for 200 epochs. It should print:

  ```
{block(DEBUG_OUT)}  ```

  It has two bugs. Run it: evaluating the same network twice gives two different validation losses, because `evaluate` never switches the network to **eval mode**, so dropout is still drawing masks while the network is being measured; `evaluate` must call `net.eval()` before its forward pass (and `fit` already calls `net.train()` before each step). Fix that, and the first layer's weights have **grown** under decay instead of shrinking: `Adam.step` subtracts `weight_decay * param` from the gradient, pushing weights outwards. Weight decay adds it, a pull towards zero.
skills: [dropout, decay]
''',
)
write("exercises/debug-a-regularizer-that-backfired/starter.py", DEBUG_STARTER)
write("exercises/debug-a-regularizer-that-backfired/solution.py", DEBUG_SOLUTION)
write(
    "exercises/debug-a-regularizer-that-backfired/test_exercise.py",
    f'''import numpy as np

from checks import function, run

EXPECTED = {DEBUG_OUT!r}


def test_the_output():
    """Prints a repeatable validation loss and shrunken weights."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\\n{{EXPECTED}}\\nYour program printed:\\n{{printed}}"


def test_the_pieces():
    """evaluate switches dropout off, and Adam's decay pulls an undefended weight towards zero."""
    Dropout = function("Dropout")
    Sequential = function("Sequential")
    Adam = function("Adam")
    evaluate = function("evaluate")

    class Plain:
        def forward(self, logits, labels):
            return float(logits.sum())

    layer = Dropout(0.5, seed=1)
    net = Sequential([layer])
    X = np.ones((50, 4))
    first = evaluate(net, Plain(), X, np.zeros(50, dtype=int))[0]
    assert first == 200.0 and layer.training is False
    pulled = np.array([1.0, -1.0])
    optimizer = Adam(0.01, weight_decay=0.1)
    for _ in range(30):
        optimizer.step([pulled], [np.zeros(2)])
    assert np.abs(pulled).max() < 1.0
''',
)
write("exercises/debug-a-regularizer-that-backfired/wrong/still-no-eval.py", DEBUG_STILL_NO_EVAL)
write("exercises/debug-a-regularizer-that-backfired/wrong/still-the-wrong-sign.py", DEBUG_STILL_SIGN)
write(
    "exercises/debug-a-regularizer-that-backfired/wrong/typed-in.py",
    "import numpy as np\n\n\nclass Dropout:\n    def __init__(self, p, seed=0):\n        self.training = True\n\n\nclass Sequential:\n    def __init__(self, layers):\n        self.layers = layers\n\n\nclass Adam:\n    def __init__(self, rate, weight_decay=0.0):\n        pass\n\n    def step(self, params, grads):\n        pass\n\n\ndef evaluate(net, loss, X, y):\n    return 0.0, 0.0\n\n\n" + "".join(f"print({line!r})\n" for line in DEBUG_OUT.splitlines()),
)

write(
    "exercises/review-early-stopping/exercise.yaml",
    f'''id: review-early-stopping
stage: review_code
rev: 1
title: "Early stopping, from memory"
prompt: |
  Write `early_stopping(val_losses, patience)`: the epoch (from 1) with the lowest loss so far and the epoch at which training stops, which is the first epoch `patience` epochs past the best, or the last epoch. Print it for `[1.0, 0.8, 0.7, 0.75, 0.74, 0.76, 0.77, 0.9]` with a patience of 4, and for `[1.0, 0.9, 0.8]` with a patience of 4:

  ```
{block(REVIEW_CODE_OUT)}  ```
skills: [early-stopping]
''',
)
write("exercises/review-early-stopping/starter.py", "")
write("exercises/review-early-stopping/solution.py", REVIEW_CODE_SOLUTION)
write(
    "exercises/review-early-stopping/test_exercise.py",
    f'''from checks import function, run


def test_the_output():
    """Prints the two pairs."""
    assert run() == {REVIEW_CODE_OUT!r}


def test_other_curves():
    """A flat curve stops at 1 + patience; an improving one runs to the end."""
    early_stopping = function("early_stopping")
    assert early_stopping([0.5] * 10, patience=3) == (1, 4)
    assert early_stopping([0.9, 0.8, 0.7, 0.6], patience=2) == (4, 4)
''',
)
write("exercises/review-early-stopping/wrong/off-by-one.py", REVIEW_CODE_WRONG)
write(
    "exercises/review-early-stopping/wrong/typed-in.py",
    "def early_stopping(val_losses, patience):\n    return (3, 7)\n\n\n" + "".join(f"print({line!r})\n" for line in REVIEW_CODE_OUT.splitlines()),
)

print("ml.nn.regularization written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
