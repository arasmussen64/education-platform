"""Writes the topic ml.nn.debugging-training (Module 8's seventh topic). Run
from the repository root under uv (python -m uv run python <this file>), so
every program's expected output is captured from CPython rather than typed
in. Every broken run is produced on purpose (a bias of -20, a rate of 30, a
starting scale of 1.0 through six layers, labels shuffled with a seed,
inputs times 1000) and read in words (converging, stalled, diverging; dead
counts; passes or fails), so the story holds on any machine; the generator
checks that a tenth-decimal nudge of the data leaves every line unchanged.
Files are written as bytes with LF endings."""

import pathlib
import subprocess
import sys

ROOT = pathlib.Path("content/topics/ml.nn.debugging-training")


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


# The module's classes and loop as they stand after the training-loop topic.
MODULE = '''class Dense:
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
'''

# This topic's additions: the diagnostic tools.
TOOLS = '''

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
'''

SPLIT = '''

def split(X, y, seed, held_out=0.2):
    """Shuffle the rows, inputs and labels together, and hold out a share for validation."""
    rng = np.random.default_rng(seed)
    order = rng.permutation(len(X))
    X, y = X[order], y[order]
    n_val = int(len(X) * held_out)
    return X[n_val:], y[n_val:], X[:n_val], y[:n_val]
'''

EXAMPLE_HEAD = "import numpy as np\n\n\n" + MODULE + TOOLS + SPLIT
EXAMPLE_TAIL = '''

X, y = make_blobs(100, seed=0)
X_train, y_train, X_val, y_val = split(X, y, seed=0)
loss = SoftmaxCrossEntropy()


def small_net(hidden=16, out_scale=0.01):
    """Two layers; the output layer starts small, so the first loss is what guessing gives."""
    return Sequential([Dense(2, hidden, seed=1), ReLU(), Dense(hidden, 3, seed=2, scale=out_scale)])


def run(net, rate, X_train=X_train, y_train=y_train, X_val=X_val, y_val=y_val, max_norm=None):
    return fit(net, loss, SGD(rate), X_train, y_train, X_val, y_val, epochs=30, max_norm=max_norm)


# 1. Is the first loss what guessing would give?
small_start = loss.forward(small_net().forward(X_train), y_train)
default_start = loss.forward(small_net(out_scale=None).forward(X_train), y_train)
print(f"1. loss at the start: {small_start:.2f} with a small output layer (guessing one of three: log 3 = {np.log(3):.2f}) | {default_start:.2f} with the default scale")

# 2. Can the code learn at all? 3. Are the gradients right?
first, last = overfit_one_batch(small_net(), loss, X_train[:8], y_train[:8])
print(f"2. overfit one batch of 8 rows: loss {first:.2f} -> {last:.2f} in 500 steps: {'passes' if last < 0.1 else 'fails'}")
print("3. gradient check:", "passes" if gradient_check(small_net(), loss, X_train[:8], y_train[:8]) < 1e-6 else "fails")

# 4. The learning rate, read from the curve.
parts = []
for rate in (0.0001, 0.05, 30.0):
    history = run(small_net(), rate)
    parts.append(f"{rate:g}: {history['train_loss'][0]:.2f} -> {history['train_loss'][-1]:.2f}, {read_curve(history['train_loss'])}")
print("4. learning rate |", " | ".join(parts))

# 5. Dead ReLUs: a bias that silences the hidden layer, and a rate that does.
silenced = small_net()
silenced.layers[0].b[:] = -20.0
silenced_history = run(silenced, 0.05)
hot = small_net()
hot_history = run(hot, 10.0)
healthy = small_net()
healthy_history = run(healthy, 0.05)
print(f"5. dead ReLUs | hidden bias -20: {dead_units(silenced, X_train)} of 16 dead, loss {silenced_history['train_loss'][0]:.2f} -> {silenced_history['train_loss'][-1]:.2f}, {read_curve(silenced_history['train_loss'])} | after a run at rate 10: {dead_units(hot, X_train)} of 16 dead, {read_curve(hot_history['train_loss'])} | the healthy run at 0.05: {dead_units(healthy, X_train)} of 16 dead, {read_curve(healthy_history['train_loss'])}, validation accuracy {healthy_history['val_accuracy'][-1]:.2f}")


# 6. Exploding gradients through six layers: a starting scale that is too big, a rate that is too high, and clipping.
def deep_net(scale):
    layers = [Dense(2, 32, seed=1, scale=scale)]
    for i in range(5):
        layers += [ReLU(), Dense(32, 32, seed=2 + i, scale=scale)]
    layers += [ReLU(), Dense(32, 3, seed=9, scale=0.01)]
    return Sequential(layers)


HE = np.sqrt(2 / 32)
big = run(deep_net(1.0), 0.05)
overflow_step = next(step for step, norm in enumerate(big["grad_norms"], start=1) if not np.isfinite(norm))
he = run(deep_net(HE), 0.05)
he_hot = run(deep_net(HE), 1.0)
clipped = run(deep_net(HE), 1.0, max_norm=1.0)
print(f"6. exploding gradients, six layers | scale 1.0, rate 0.05: gradient norm about 10^{int(np.log10(big['grad_norms'][0]))} at step 1, overflowed by step {overflow_step}: {read_curve(big['train_loss'])} | He scale, rate 0.05: {read_curve(he['train_loss'])}, {he['val_accuracy'][-1]:.2f} | He scale, rate 1.0: {read_curve(he_hot['train_loss'])} | He scale, rate 1.0, gradients clipped to 1: {read_curve(clipped['train_loss'])}, {clipped['val_accuracy'][-1]:.2f}")

# 7. The data: labels that don't match their rows, and inputs on the wrong scale.
y_shuffled = np.random.default_rng(4).permutation(y_train)
_, memorized = overfit_one_batch(small_net(), loss, X_train[:8], y_shuffled[:8])
shuffled = run(small_net(), 0.05, y_train=y_shuffled)
huge = run(small_net(), 0.05, X_train=X_train * 1000, X_val=X_val * 1000)
mean, std = (X_train * 1000).mean(axis=0), (X_train * 1000).std(axis=0)
rescaled = run(small_net(), 0.05, X_train=standardize(X_train * 1000, mean, std), X_val=standardize(X_val * 1000, mean, std))
print(f"7. data | labels shuffled: one batch of 8 still overfits ({memorized:.2f}), but 30 epochs go {shuffled['train_loss'][0]:.2f} -> {shuffled['train_loss'][-1]:.2f} and validation accuracy is {shuffled['val_accuracy'][-1]:.2f}: {diagnose(shuffled, 3)} | inputs times 1000: {read_curve(huge['train_loss'])} | standardized: {read_curve(rescaled['train_loss'])}, {rescaled['val_accuracy'][-1]:.2f}")
print("8. one word each, from diagnose:", ", ".join(diagnose(history, 3) for history in (healthy_history, silenced_history, big, shuffled)))
'''
EXAMPLE = EXAMPLE_HEAD + EXAMPLE_TAIL
EXAMPLE_OUT = out(EXAMPLE)
print("example:\n" + EXAMPLE_OUT)
EX = EXAMPLE_OUT.splitlines()
assert len(EX) == 8, EX
assert EX[0].startswith("1. loss at the start: 1.10 with a small output layer (guessing one of three: log 3 = 1.10) | 1.38"), EX[0]
assert EX[1].endswith("passes") and " 1.11 -> 0.02 " in EX[1], EX[1]
assert EX[2] == "3. gradient check: passes", EX[2]
assert "0.0001: 1.10 -> 1.03, stalled | 0.05: 1.10 -> 0.17, converging | 30: 1.10 -> nan, diverging" in EX[3], EX[3]
assert "hidden bias -20: 16 of 16 dead, loss 1.10 -> 1.10, stalled" in EX[4] and "after a run at rate 10: 12 of 16 dead, stalled" in EX[4] and "the healthy run at 0.05: 0 of 16 dead, converging, validation accuracy 0.90" in EX[4], EX[4]
assert "scale 1.0, rate 0.05: gradient norm about 10^3 at step 1, overflowed by step " in EX[5] and ": diverging | He scale, rate 0.05: converging, 0.93 | He scale, rate 1.0: diverging | He scale, rate 1.0, gradients clipped to 1: converging, 0.98" in EX[5], EX[5]
OVERFLOW_STEP = int(EX[5].split("overflowed by step ")[1].split(":")[0])
assert OVERFLOW_STEP <= 10, OVERFLOW_STEP
assert "labels shuffled: one batch of 8 still overfits (0.02), but 30 epochs go 1.10 -> 1.09 and validation accuracy is 0.35: stalled | inputs times 1000: diverging | standardized: converging, 0.93" in EX[6], EX[6]
assert EX[7] == "8. one word each, from diagnose: learning, stalled, diverging, stalled", EX[7]
NUDGED = EXAMPLE.replace("X_train, y_train, X_val, y_val = split(X, y, seed=0)", "X_train, y_train, X_val, y_val = split(X, y, seed=0)\nX_train[0, 0] += 1e-10")
assert out(NUDGED) == EXAMPLE_OUT, "a tenth-decimal nudge changed a printed line"
EXAMPLE_LINES = EXAMPLE.splitlines()


def ln(text: str, after: int = 0) -> int:
    return next(i + 1 for i, line in enumerate(EXAMPLE_LINES) if i + 1 > after and text in line)


# --- recall programs ----------------------------------------------------------------------------

PREDICT_CURVE = '''import numpy as np


def read_curve(losses):
    first, last = losses[0], losses[-1]
    if not np.isfinite(last) or last > 1.5 * first:
        return "diverging"
    if last > 0.9 * first:
        return "stalled"
    return "converging"


print(read_curve([1.1, 0.9, 0.7, 0.5]), read_curve([1.1, 1.09, 1.08, 1.07]))
print(read_curve([1.1, 2.0, 7.0, 40.0]), read_curve([1.1, 0.8, 3.0, float("nan")]))
'''
PREDICT_CURVE_OUT = out(PREDICT_CURVE)
assert PREDICT_CURVE_OUT == "converging stalled\ndiverging diverging\n", PREDICT_CURVE_OUT

PREDICT_DEAD = '''import numpy as np

pre_activations = np.array([[-1.0, 2.0, -3.0, 0.5], [-2.0, 0.0, -1.0, -0.5], [-0.5, 1.0, -2.0, 1.5]])
mask = pre_activations > 0
print(mask.any(axis=0).tolist())
print(int((~mask.any(axis=0)).sum()), int((~mask.any(axis=1)).sum()))
'''
PREDICT_DEAD_OUT = out(PREDICT_DEAD)
assert PREDICT_DEAD_OUT == "[False, True, False, True]\n2 1\n", PREDICT_DEAD_OUT

PREDICT_CLIP = '''import numpy as np


def clip_gradients(grads, max_norm):
    norm = float(np.sqrt(sum(float((grad ** 2).sum()) for grad in grads)))
    if norm > max_norm:
        return [grad * (max_norm / norm) for grad in grads]
    return grads


grads = [np.array([3.0, 0.0]), np.array([[0.0, 4.0]])]
print([grad.tolist() for grad in clip_gradients(grads, 2.5)])
print([grad.tolist() for grad in clip_gradients(grads, 10.0)])
'''
PREDICT_CLIP_OUT = out(PREDICT_CLIP)
assert PREDICT_CLIP_OUT == "[[1.5, 0.0], [[0.0, 2.0]]]\n[[3.0, 0.0], [[0.0, 4.0]]]\n", PREDICT_CLIP_OUT

REVIEW_PREDICT = '''import numpy as np

hidden = np.array([[0.0, 3.0, 0.0], [0.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 2.5, 0.0]])
active = hidden > 0
print(int((~active.any(axis=0)).sum()), "dead of", hidden.shape[1])
print("rows with every unit silent:", int((~active.any(axis=1)).sum()))
'''
REVIEW_PREDICT_OUT = out(REVIEW_PREDICT)
assert REVIEW_PREDICT_OUT == "2 dead of 3\nrows with every unit silent: 1\n", REVIEW_PREDICT_OUT

PARSONS_LINES = [
    "import numpy as np",
    "X_train, X_val = np.array([[1.0, 100.0], [3.0, 300.0], [5.0, 500.0]]), np.array([[3.0, 100.0]])",
    "mean, std = X_train.mean(axis=0), X_train.std(axis=0)",
    "X_train, X_val = (X_train - mean) / std, (X_val - mean) / std",
    "print(X_train.round(3).tolist(), X_val.round(3).tolist())",
]
PARSONS_OUT = out("\n".join(PARSONS_LINES) + "\n")
assert PARSONS_OUT == "[[-1.225, -1.225], [0.0, 0.0], [1.225, 1.225]] [[0.0, -1.225]]\n", PARSONS_OUT

# --- the fill-in --------------------------------------------------------------------------------

FILL_SOLUTION = "import numpy as np\n\n\n" + MODULE.split("class SoftmaxCrossEntropy:")[0].rstrip("\n") + '''


def dead_units(net, X):
    """How many ReLU units output 0 on every row of X: no gradient reaches them, so they can never recover."""
    net.forward(X)
    return sum(int((~layer.mask.any(axis=0)).sum()) for layer in net.layers if isinstance(layer, ReLU))


rng = np.random.default_rng(0)
X = rng.standard_normal((50, 2))
net = Sequential([Dense(2, 16, seed=1), ReLU(), Dense(16, 16, seed=2), ReLU(), Dense(16, 3, seed=3)])
print(dead_units(net, X))
net.layers[0].b[:4] = -20.0
net.layers[2].b[:] = -20.0
print(dead_units(net, X))
'''
FILL_STARTER = FILL_SOLUTION.replace("    return sum(int((~layer.mask.any(axis=0)).sum()) for layer in net.layers if isinstance(layer, ReLU))", "    return sum(int((~layer.mask.any(axis=...)).sum()) for layer in net.layers if isinstance(layer, ...))")
assert FILL_STARTER.count("...") == 2
FILL_OUT = out(FILL_SOLUTION)
assert FILL_OUT == "0\n20\n", FILL_OUT
FILL_ROWS = FILL_SOLUTION.replace("    return sum(int((~layer.mask.any(axis=0)).sum()) for layer in net.layers if isinstance(layer, ReLU))", "    return sum(int((~layer.mask.any(axis=1)).sum()) for layer in net.layers if isinstance(layer, ReLU))")
FILL_ALL_LAYERS = FILL_SOLUTION.replace("    return sum(int((~layer.mask.any(axis=0)).sum()) for layer in net.layers if isinstance(layer, ReLU))", "    return sum(int((~(layer.forward(X) > 0).any(axis=0)).sum()) for layer in net.layers if isinstance(layer, Dense))")
assert differs(FILL_ROWS, FILL_OUT) and differs(FILL_ALL_LAYERS, FILL_OUT)

# --- the write ----------------------------------------------------------------------------------

WRITE_SOLUTION = '''import numpy as np


def gradient_norm(grads):
    """The length of all the gradients taken together, as one vector."""
    return float(np.sqrt(sum(float((grad ** 2).sum()) for grad in grads)))


def clip_gradients(grads, max_norm):
    """Scale every gradient by the same factor so their norm is at most max_norm; leave them alone if it already is."""
    norm = gradient_norm(grads)
    if norm > max_norm:
        return [grad * (max_norm / norm) for grad in grads]
    return grads


grads = [np.array([[3.0, 0.0], [0.0, 0.0]]), np.array([4.0]), np.array([12.0])]
print(gradient_norm(grads))
clipped = clip_gradients(grads, 6.5)
print([grad.tolist() for grad in clipped], gradient_norm(clipped))
print(clip_gradients(grads, 100.0) is grads)
'''
WRITE_TAIL = "grads = [" + WRITE_SOLUTION.split("\n\n\ngrads = [", 1)[1]
WRITE_OUT = out(WRITE_SOLUTION)
assert WRITE_OUT == "13.0\n[[[1.5, 0.0], [0.0, 0.0]], [2.0], [6.0]] 6.5\nTrue\n", WRITE_OUT
WRITE_EACH = WRITE_SOLUTION.replace("    norm = gradient_norm(grads)\n    if norm > max_norm:\n        return [grad * (max_norm / norm) for grad in grads]\n    return grads", "    return [grad * (max_norm / gradient_norm([grad])) if gradient_norm([grad]) > max_norm else grad for grad in grads]")
WRITE_ALWAYS = WRITE_SOLUTION.replace("    if norm > max_norm:\n        return [grad * (max_norm / norm) for grad in grads]\n    return grads", "    return [grad * (max_norm / norm) for grad in grads]")
assert differs(WRITE_EACH, WRITE_OUT) and differs(WRITE_ALWAYS, WRITE_OUT)

# --- the build ----------------------------------------------------------------------------------

BUILD_TAIL = '''

X, y = make_blobs(100, seed=0)
X_train, y_train, X_val, y_val = split(X, y, seed=0)
loss = SoftmaxCrossEntropy()


def small_net():
    return Sequential([Dense(2, 16, seed=1), ReLU(), Dense(16, 3, seed=2, scale=0.01)])


first, last = overfit_one_batch(small_net(), loss, X_train[:8], y_train[:8])
print(round(first, 2), round(last, 2), last < 0.1)
runs = [fit(small_net(), loss, SGD(rate), X_train, y_train, X_val, y_val, epochs=30) for rate in (0.05, 0.0001, 30.0)]
print(" | ".join(diagnose(history, 3) for history in runs), len(runs[0]["grad_norms"]))
silenced = small_net()
silenced.layers[0].b[:] = -20.0
fit(silenced, loss, SGD(0.05), X_train, y_train, X_val, y_val, epochs=30)
print(dead_units(silenced, X_train), dead_units(small_net(), X_train))
print([round(float(v), 2) for v in clip_gradients([np.array([3.0, 4.0])], 1.0)[0]], gradient_norm([np.array([3.0, 4.0]), np.array([12.0])]))
mean, std = X_train.mean(axis=0), X_train.std(axis=0)
Z = standardize(X_train, mean, std)
print(bool(np.abs(Z.mean(axis=0)).max() < 1e-12), Z.std(axis=0).round(6).tolist())
'''
BUILD_SOLUTION = "import numpy as np\n\n\n" + MODULE + TOOLS + SPLIT + BUILD_TAIL
BUILD_OUT = out(BUILD_SOLUTION)
print("build:\n" + BUILD_OUT)
assert BUILD_OUT == "1.11 0.02 True\nlearning | stalled | diverging 240\n16 0\n[0.6, 0.8] 13.0\nTrue [1.0, 1.0]\n", BUILD_OUT
assert out(BUILD_SOLUTION.replace("X_train, y_train, X_val, y_val = split(X, y, seed=0)", "X_train, y_train, X_val, y_val = split(X, y, seed=0)\nX_train[0, 0] += 1e-10")) == BUILD_OUT
BUILD_WRONGS = {
    "never-steps-on-one-batch": BUILD_SOLUTION.replace("            optimizer.step(net.parameters(), net.gradients())\n        return first, loss.forward(net.forward(X), y)", "        return first, loss.forward(net.forward(X), y)"),
    "diagnose-checks-chance-first": BUILD_SOLUTION.replace('''    verdict = read_curve(history["train_loss"])
    if verdict != "converging":
        return verdict
    if history["val_accuracy"][-1] < 1 / n_classes + 0.1:
        return "at chance"
    return "learning"''', '''    if history["val_accuracy"][-1] < 1 / n_classes + 0.1:
        return "at chance"
    verdict = read_curve(history["train_loss"])
    if verdict != "converging":
        return verdict
    return "learning"'''),
    "dead-units-counts-rows": BUILD_SOLUTION.replace("    return sum(int((~layer.mask.any(axis=0)).sum()) for layer in net.layers if isinstance(layer, ReLU))", "    return sum(int((~layer.mask.any(axis=1)).sum()) for layer in net.layers if isinstance(layer, ReLU))"),
    "norms-recorded-after-clipping": BUILD_SOLUTION.replace('''                grads = net.gradients()
                history["grad_norms"].append(gradient_norm(grads))
                if max_norm is not None:
                    grads = clip_gradients(grads, max_norm)''', '''                grads = net.gradients()
                if max_norm is not None:
                    grads = clip_gradients(grads, max_norm)
                history["grad_norms"].append(gradient_norm(grads))'''),
    "clips-every-gradient-alone": BUILD_SOLUTION.replace("    norm = gradient_norm(grads)\n    if norm > max_norm:\n        return [grad * (max_norm / norm) for grad in grads]\n    return grads", "    return [grad * (max_norm / gradient_norm([grad])) if gradient_norm([grad]) > max_norm else grad for grad in grads]"),
}
for key, code in BUILD_WRONGS.items():
    assert code != BUILD_SOLUTION, key

# --- the debug ----------------------------------------------------------------------------------

DEBUG_SOLUTION = "import numpy as np\n\n\n" + MODULE + TOOLS + SPLIT + '''

X, y = make_blobs(100, seed=0)
X_train, y_train, X_val, y_val = split(X, y, seed=0)
loss = SoftmaxCrossEntropy()
rate = 0.05
net = Sequential([Dense(2, 16, seed=1), ReLU(), Dense(16, 3, seed=2, scale=0.01)])
history = fit(net, loss, SGD(rate), X_train, y_train, X_val, y_val, epochs=30)
print(f"loss {history['train_loss'][0]:.2f} -> {history['train_loss'][-1]:.2f}: {diagnose(history, 3)} | validation accuracy {history['val_accuracy'][-1]:.2f}")
fresh = Sequential([Dense(2, 16, seed=1), ReLU(), Dense(16, 3, seed=2, scale=0.01)])
_, last = overfit_one_batch(fresh, loss, X_train[:8], y_train[:8], rate=rate)
print(f"one batch of 8 overfits: {bool(last < 0.1)} | dead units after training: {dead_units(net, X_train)} of 16")
'''
BUG_RATE = ("rate = 0.05\n", "rate = 50.0\n")
BUG_SPLIT = ("    order = rng.permutation(len(X))\n    X, y = X[order], y[order]\n", "    X = X[rng.permutation(len(X))]\n    y = y[rng.permutation(len(y))]\n")
DEBUG_STARTER = DEBUG_SOLUTION.replace(*BUG_RATE).replace(*BUG_SPLIT)
DEBUG_STILL_RATE = DEBUG_SOLUTION.replace(*BUG_RATE)
DEBUG_STILL_SPLIT = DEBUG_SOLUTION.replace(*BUG_SPLIT)
assert DEBUG_STARTER != DEBUG_STILL_RATE != DEBUG_SOLUTION != DEBUG_STILL_SPLIT
DEBUG_OUT = out(DEBUG_SOLUTION)
STARTER_OUT = out(DEBUG_STARTER)
STILL_SPLIT_OUT = out(DEBUG_STILL_SPLIT)
print("debug:\n" + DEBUG_OUT + "starter:\n" + STARTER_OUT + "rate fixed:\n" + STILL_SPLIT_OUT)
assert DEBUG_OUT.startswith("loss 1.10 -> 0.17: learning | validation accuracy 0.90\none batch of 8 overfits: True | dead units after training: 0 of 16\n"), DEBUG_OUT
assert "-> nan: diverging" in STARTER_OUT.splitlines()[0] and "dead units after training: 16 of 16" in STARTER_OUT, STARTER_OUT
assert ": stalled | validation accuracy 0." in STILL_SPLIT_OUT and "one batch of 8 overfits: True | dead units after training: 0 of 16" in STILL_SPLIT_OUT, STILL_SPLIT_OUT
assert 0.2 <= float(STILL_SPLIT_OUT.split("validation accuracy ")[1].split("\n")[0]) <= 0.5, STILL_SPLIT_OUT
assert "diverging" in out(DEBUG_STILL_RATE)
assert out(DEBUG_SOLUTION.replace("X_train, y_train, X_val, y_val = split(X, y, seed=0)", "X_train, y_train, X_val, y_val = split(X, y, seed=0)\nX_train[0, 0] += 1e-10")) == DEBUG_OUT
STILL_SPLIT_ACC = STILL_SPLIT_OUT.split("validation accuracy ")[1].split("\n")[0]

REVIEW_CODE_SOLUTION = '''import numpy as np


def clip_gradients(grads, max_norm):
    """Scale every gradient by the same factor so that their norm, all together, is at most max_norm; unchanged if it already is."""
    norm = float(np.sqrt(sum(float((grad ** 2).sum()) for grad in grads)))
    if norm > max_norm:
        return [grad * (max_norm / norm) for grad in grads]
    return grads


grads = [np.array([6.0, 0.0]), np.array([[8.0]])]
print([grad.tolist() for grad in clip_gradients(grads, 5.0)])
print([grad.tolist() for grad in clip_gradients(grads, 20.0)])
'''
REVIEW_CODE_OUT = out(REVIEW_CODE_SOLUTION)
assert REVIEW_CODE_OUT == "[[3.0, 0.0], [[4.0]]]\n[[6.0, 0.0], [[8.0]]]\n", REVIEW_CODE_OUT
REVIEW_CODE_WRONG = REVIEW_CODE_SOLUTION.replace("    if norm > max_norm:\n        return [grad * (max_norm / norm) for grad in grads]\n    return grads", "    return [grad * (max_norm / norm) for grad in grads]")
assert differs(REVIEW_CODE_WRONG, REVIEW_CODE_OUT)

# =====================================================================================
# topic.yaml
# =====================================================================================

write(
    "topic.yaml",
    '''id: ml.nn.debugging-training
kind: topic
status: ready
title: "When training goes wrong"
summary: "A checklist for a network that won't learn: check the first loss, overfit one batch, check the gradients, read the curve for the learning rate, count dead ReLUs, watch the gradient norm for an explosion, suspect the data, and change one thing at a time."
prerequisites: [ml.nn.training-loop, ml.nn.initialization-and-activations]
packages: [numpy]
estimated_minutes: 50
rev: 1
objectives:
  - "Diagnose a learning rate that is too high or too low from the loss curve, and fix it."
  - "Use the overfit-one-batch test and the gradient check to tell a bug from a hard problem."
  - "Detect dead ReLUs and exploding gradients from activation and gradient statistics, and apply the standard fixes."
  - "Find a data bug (shuffled labels, unscaled inputs) from what training does, and say why each one fools a network."
# Linked, never copied or embedded: the recipe is a personal blog post;
# Wikipedia is CC BY-SA 4.0.
resources:
  - title: "Andrej Karpathy: A Recipe for Training Neural Networks (the checklist this topic follows: verify the loss at init, overfit one batch, change one thing at a time)"
    url: https://karpathy.github.io/2019/04/25/recipe/
    type: reading
    use: link
    license: No licence stated (default copyright; linked, not copied)
  - title: "Wikipedia: Rectified linear unit (the Potential problems section: the dying ReLU problem)"
    url: https://en.wikipedia.org/wiki/Rectifier_(neural_networks)
    type: reading
    use: link
    license: CC BY-SA 4.0 (linked, not copied)
  - title: "Wikipedia: Vanishing gradient problem (which covers exploding gradients too, and the fixes: initialization, clipping, normalization)"
    url: https://en.wikipedia.org/wiki/Vanishing_gradient_problem
    type: reading
    use: link
    license: CC BY-SA 4.0 (linked, not copied)
practice:
  - example-a-checklist-for-a-network-that-will-not-learn
  - predict-read-the-curve
  - mcq-too-high-or-too-low
  - mcq-overfit-one-batch
  - mcq-what-the-gradient-check-rules-out
  - predict-dead-units
  - mcq-the-signs-of-dead-relus
  - predict-clip-gradients
  - mcq-the-signs-of-exploding-gradients
  - mcq-labels-that-do-not-match
  - mcq-inputs-on-the-wrong-scale
  - parsons-standardize
  - mcq-one-thing-at-a-time
  - fill-dead-units
  - write-clip-gradients
prove:
  build: build-the-diagnostics
  debug: debug-a-run-that-will-not-learn
  explain:
    prompt: |
      A teammate's network isn't learning and they are about to try a bigger model, a different optimizer and more epochs, all at once. Walk them through the checklist in order and say what each step rules in or out: what the first loss should be and why; what overfitting one batch and the gradient check each prove; how to read the loss curve for the learning rate, including the case where a rate that is too high stalls rather than diverges; what dead ReLUs and exploding gradients look like in the numbers and what fixes each; what shuffled labels and unscaled inputs do to a run and why; and why to change one thing at a time with the seed fixed.
    rubric:
      - id: order
        required: true
        description: "First cheap checks that separate a bug from a hard problem: the first loss should be about log(number of classes) with a small output layer (far off means the output scale or the data is wrong); a working network drives the loss on eight rows to nearly zero, and if it can't the code is broken; the gradient check compares backward with central differences and a failure is a bug in backward. Only then touch the learning rate, the model or the data."
      - id: rate-and-curve
        required: true
        description: "Stalled (fell by less than a tenth) usually means the rate is too low; diverging (NaN or rising) means too high; but a too-high rate can also stall by killing the hidden units, so a stalled run gets the dead-unit count before the rate is raised. The fix is the rate by a factor of ten, then look again."
      - id: dead-and-exploding
        required: true
        description: "A dead ReLU outputs zero on every row, so no gradient reaches its weights and it never recovers; a large negative bias or one oversized step makes them, and the count is read from the activations. Exploding gradients show as a gradient norm that grows step over step until it overflows, from a starting scale that is too big or a rate too high; the fixes are He-scaled starts, a lower rate and clipping the gradient norm."
      - id: data
        required: true
        description: "Labels that don't match their rows let one batch be memorized but leave the full run stalled and the validation accuracy at chance, because there is no pattern to learn; inputs on the wrong scale make the first steps enormous and the run diverge, because the gradient scales with the inputs. Standardize with the training set's mean and spread, applied to the validation set too."
      - id: one-thing
        required: true
        description: "Change one thing at a time with the seed fixed, so that a difference in the result has one cause; changing three things at once leaves no way to know which one mattered, and without a fixed seed two runs differ anyway."
    model_answer: |
      Before touching anything, check what is cheap to check. With the output layer started small, the first loss should be about log 3 for three classes, 1.10, because the network is guessing evenly; a first loss far from that means the output scale, the loss or the labels are not what you think. Then take eight rows and train on them alone for a few hundred steps: a network whose code works will drive that loss to nearly zero, because eight points are trivial to memorize, and if it cannot, the bug is in the code, not in the data or the hyperparameters. The gradient check settles whether backward is right: compare every gradient with a central difference of the loss, and a gap above a millionth is a bug in a backward method. These three pass, so what is left is the training setup. Read the loss curve: falling and levelling off is converging; falling by less than a tenth in thirty epochs is stalled, which usually means the learning rate is too low; NaN or rising is diverging, which means too high. But a rate that is too high does not always diverge. One huge step can push a hidden unit's bias so far negative that it outputs zero on every row, and a ReLU that outputs zero passes no gradient back, so it never recovers: in the example a rate of 10 left twelve of sixteen units dead and the run stalled, looking exactly like a rate that was too low. So count the dead units before raising the rate; the count is the number of units whose activation is zero on every row. Dead units also come from a large negative bias at the start; the fixes are zero biases with He-scaled weights, a smaller rate, and, in libraries, a leaky ReLU, whose gradient is never zero. Exploding gradients show in the gradient norm, the length of all the gradients taken together: it grows step over step until it overflows to infinity and the loss becomes NaN. A starting scale that is too big through several layers does it from the first step; a rate that is too high does it after a few. He-scaled starts fix the first, a lower rate fixes the second, and clipping the gradient norm to a limit lets a run survive either, since the step is bounded. If all of that is in order and the run still stalls, suspect the data. Labels that do not match their rows, from shuffling inputs and labels separately, give a run that can still memorize eight rows but has no pattern to learn across the training set: the loss barely moves and the validation accuracy sits at chance. Inputs on the wrong scale, say in the thousands, make the first logits and so the first gradients enormous, because the gradient of a dense layer scales with its input, and the run diverges at a rate that was fine before; standardizing each column with the training set's mean and spread, applied to the validation set with the same numbers, fixes it. Through all of this, change one thing at a time with the seed fixed. If the bigger model, the new optimizer and the extra epochs go in together and the run improves, nothing says which one did it, and if it gets worse, nothing says which one to take out; with the seed fixed, two runs that differ in one setting differ for one reason.
review_pool:
  - review-predict-dead-units
  - review-mcq-cannot-overfit-one-batch
  - review-mcq-which-fix
  - review-clip-gradients
# What this topic teaches. Each question names the skills it tests, so a
# missed question can come back as a different one on the same skill
# (ADR-0011).
skills:
  - id: learning-rate
    description: "Diagnose a learning rate that is too high or too low from the loss curve, and fix it"
  - id: bug-or-hard
    description: "Use the first loss, the overfit-one-batch test and the gradient check to tell a bug from a hard problem, and change one thing at a time"
  - id: dead-and-exploding
    description: "Detect dead ReLUs and exploding gradients from activation and gradient statistics, and apply the standard fixes"
  - id: data-bugs
    description: "Find a data bug (shuffled labels, unscaled inputs) from what training does, and say why each one fools a network"
''',
)

# =====================================================================================
# lesson.mdx
# =====================================================================================

write(
    "lesson.mdx",
    f'''<Intro>

Every network that fails to learn fails quietly: the loss sits still, or climbs, or turns to NaN, and nothing says why. The temptation is to change the model, the optimizer and the epochs at once. This topic is the checklist that practitioners use instead, each step cheap and each one ruling something in or out: the first loss, one batch, the gradient check, the curve, the dead units, the gradient norm, the data, and one change at a time. Every failure in it is produced on purpose so that the signs are seen before they're met.

The main resource is **Andrej Karpathy's _A Recipe for Training Neural Networks_** (a blog post, about 20 minutes), the checklist this topic follows; read step 2 of the recipe (the tips "verify loss @ init" and "overfit one batch") and its advice to add complexity one thing at a time. Wikipedia's _Rectified linear unit_ page has the dying-ReLU problem under _Potential problems_, and its _Vanishing gradient problem_ page covers exploding gradients and the fixes. Watch for:

- **The loss at init**: what the first loss should be before any training.
- **Overfit one batch**: the test that separates a broken network from a hard problem.
- **Gradient clipping**: bounding the step when the gradient blows up.

</Intro>

<Resource index={{0}} />

<Recap>

- **The first loss.** With the output layer started small, the network guesses evenly and the loss is `log(classes)`: 1.10 for three classes, which the example prints. A first loss far from that means the output scale, the loss or the labels aren't what you think. The default output scale gave 1.38: already a hint that the start matters.
- **Overfit one batch.** Train on eight rows, the whole eight every step, for a few hundred steps: a working network drives the loss to nearly zero (1.11 to 0.02 in 500 steps), because eight points are trivial to memorize. If it can't, at a sensible rate and start (zero biases, He-scaled weights), the bug is almost certainly in the code, and no hyperparameter (a setting chosen by hand, like the rate) will fix it. `overfit_one_batch` returns the first and last loss.
- **The gradient check** compares every backward gradient with a central difference of the loss; a gap above a millionth is a bug in a backward method. It passes here, so what is left is the setup and the data.
- **The learning rate, from the curve.** `read_curve` says **stalled** when the loss fell by less than a tenth (0.0001: 1.10 to 1.03), **converging** when it fell (0.05), **diverging** when it is NaN or rose by half (30). Stalled usually means too low and diverging too high; the fix is a factor of ten, then look again. But a rate that is too high can also stall: see the next point.
- **Dead ReLUs.** A ReLU unit whose input is negative on every row outputs 0 everywhere, passes no gradient back, and never recovers. `dead_units` counts them from the masks. A hidden bias of -20 killed all 16 and the loss sat at 1.10; a rate of 10 killed 12 of 16 in a run that stalled rather than diverged, so a stalled run gets its dead count before its rate is raised. Fixes: zero biases with He-scaled weights, a lower rate, and in libraries a leaky ReLU, whose gradient is never zero.
- **Exploding gradients.** `gradient_norm` is the length of all the gradients as one vector; `fit` records it at every step. Through six layers at a starting scale of 1.0, the norm was about 10^3 at the first step and overflowed by step {OVERFLOW_STEP}: diverging. He-scaled starts at a rate of 0.05 converge (93%). The He start at a rate of 1.0 diverges; the same run with **gradient clipping** (`clip_gradients` scales all the gradients down together when their norm passes 1) converges to 98%, because the step is bounded whatever the gradient does.
- **Data bugs.** Labels shuffled apart from their rows: one batch of 8 still memorizes (0.02) but 30 epochs go 1.10 to 1.09 and the validation accuracy is 0.35, chance, because there is no pattern to learn. Inputs times 1000: diverging at a rate that was fine, because a dense layer's gradient scales with its input and the first steps are enormous. `standardize` the columns with the training set's mean and spread, applied to the validation set with the same two numbers, and the run converges (93%).
- **One thing at a time.** `diagnose` gives one phrase per run (diverging, stalled, at chance, learning); the checklist tells the stalled ones apart. Change one setting per run with the seed fixed, so that a difference has one cause; changing three at once leaves no way to know which mattered, and without a fixed seed two runs differ anyway.
- **This topic's `fit`** is The training loop's, not Regularization's: mini-batches, no patience and no modes, plus a `max_norm` for clipping and a history that starts before training (entry 0), so `read_curve` reads every run from its real start; `evaluate` is the training loop's too.
- **In machine learning** (names you'll meet later): `torch.nn.utils.clip_grad_norm_` is `clip_gradients`; a **learning-rate finder** sweeps the rate on a log scale and reads the curve; **leaky ReLU**, **GELU** and **batch normalization** are the library answers to dead units and bad scales; **`torch.autograd.gradcheck`** is the gradient check; and the loss-at-init rule, the one-batch test and the one-change rule are the first three items in every recipe for training a network.

</Recap>
''',
)

# =====================================================================================
# recall
# =====================================================================================

write(
    "recall/predict-read-the-curve.yaml",
    f'''id: predict-read-the-curve
type: predict_output
rev: 1
prompt: |
  `read_curve` names a loss curve from its first and last value: diverging if the last is NaN or rose by half, stalled if it fell by less than a tenth, else converging. What does the program print for the four curves?
code: |
{block(PREDICT_CURVE)}expected_output: |
{block(PREDICT_CURVE_OUT)}explanation: |
  1.1 to 0.5 fell by more than a tenth: converging. 1.1 to 1.07 fell by less than a tenth: stalled. 1.1 to 40 rose by far more than half: diverging. A last value of NaN fails `isfinite`, so it reads diverging whatever came before: a loss that reached NaN has overflowed, which only a run that blew up does.
skills: [learning-rate]
''',
)

mcq(
    "mcq-too-high-or-too-low",
    "Run A's loss goes 1.10 to 1.08 in 30 epochs. Run B's loss is NaN by epoch 2. Run C's loss goes 1.10 to 1.07 and 12 of its 16 hidden units are dead. What is wrong in each?",
    [
        "A: the rate is too low; B: too high; C: too high as well, since one big step killed the units, though the curve looks like A's",
        "A and C: the rate is too low, since both stalled; B: the data is unscaled",
        "A: the rate is too high; B: the rate is too low, since the loss overflowed before it had a chance to fall; C: the network is too small for the data, since a bigger one would keep more units alive",
        "All three need more epochs, since none of them has converged yet",
    ],
    0,
    "A stalled curve is the usual sign of a rate too low, and NaN of a rate too high. C stalled too, but its dead units give it away: a rate that is too high can push the hidden biases so far negative in one step that the units output zero everywhere and stop learning, after which the loss sits still. Raising C's rate would make it worse, which is why the dead count comes before the rate.",
    ["learning-rate", "dead-and-exploding"],
)

mcq(
    "mcq-overfit-one-batch",
    "A network with zero biases and He-scaled weights, trained on eight rows for 500 steps at a rate that converged on this data last week, ends with a loss of 1.05, down from 1.10. What does that prove, and what is the next step?",
    [
        "The data is too hard for this network; collect more rows",
        "The code is broken, since a working network memorizes eight rows easily; find the bug before touching any hyperparameter",
        "The learning rate is too low, since the loss moved a little; raise it by a factor of ten and train on the full set",
        "Nothing yet: eight rows are too few to say anything about a network, so train on the full set for more epochs and judge from that curve instead",
    ],
    1,
    "Eight points are trivial to memorize: a network with a working forward, backward and update drives their loss to nearly zero. One that cannot has a bug, in the loss, in a backward pass, in the update or in how the data is fed, and the full set, more rows and a different rate won't fix it; the rate and the start are known good here, which is what lets the test point at the code. The test is cheap, so it comes first.",
    ["bug-or-hard"],
)

mcq(
    "mcq-what-the-gradient-check-rules-out",
    "The gradient check passes, one batch overfits, and the full run still stalls. Where is the problem not, and where might it be?",
    [
        "Not in backward or the update; look at the rate, the dead units and the data",
        "Not in the learning rate, since the gradient check would have caught a bad one",
        "Not in the data, since the batch that overfit came from it and so the data is fine, which means the fault must be in the loss function itself",
        "Nowhere: a run that passes both checks is correct and only needs more epochs",
    ],
    0,
    "The gradient check proves that backward matches the loss; the one-batch test proves that the whole loop can learn. Together they clear the code. A stalled full run with working code is a setup or data problem: a rate too low, units that died, labels that don't match their rows. The checks say nothing about the rate, and a batch that memorizes shuffled labels is still shuffled.",
    ["bug-or-hard"],
)

write(
    "recall/predict-dead-units.yaml",
    f'''id: predict-dead-units
type: predict_output
rev: 1
prompt: |
  Three rows of pre-activations for four hidden units. A unit is dead if its pre-activation is not positive on any row. What does the program print?
code: |
{block(PREDICT_DEAD)}expected_output: |
{block(PREDICT_DEAD_OUT)}explanation: |
  `mask.any(axis=0)` asks, column by column, whether any row is positive: units 1 and 3 fire somewhere, units 0 and 2 never do, so two are dead. Along `axis=1` the question is per row: the second row has no positive entry (0.0 is not above zero), so one row gets nothing through the layer.
skills: [dead-and-exploding]
''',
)

mcq(
    "mcq-the-signs-of-dead-relus",
    "What does a dead ReLU unit look like in the numbers, why doesn't it recover, and what prevents it?",
    [
        "Its output is 0 on every row, so its weights get no gradient and can't change; zero biases with He-scaled starts, a lower rate, or a leaky ReLU",
        "Its output is the same positive number on every row, so it carries no information; more hidden units",
        "Its weights have grown huge, so its output saturates at the maximum value the ReLU can give, and nothing short of starting over with a smaller network brings it back",
        "Its gradient is NaN; gradient clipping",
    ],
    0,
    "ReLU passes the gradient only where its input was positive. A unit whose input is negative on every row outputs zero everywhere and its weights receive exactly zero gradient, so nothing moves it back: it is dead for good. A large negative bias or one oversized step makes them. Keeping the biases at zero, scaling the weights for ReLU, stepping smaller, or using a leaky ReLU that passes a little gradient below zero are the standard answers. ReLU has no maximum and a dead unit's gradient is zero, not NaN.",
    ["dead-and-exploding"],
)

write(
    "recall/predict-clip-gradients.yaml",
    f'''id: predict-clip-gradients
type: predict_output
rev: 1
prompt: |
  `clip_gradients` scales all the gradients down by one factor when their combined norm passes `max_norm`, and leaves them alone otherwise. What does the program print?
code: |
{block(PREDICT_CLIP)}expected_output: |
{block(PREDICT_CLIP_OUT)}explanation: |
  Together the gradients are the vector (3, 0, 0, 4), with norm 5. Clipping to 2.5 multiplies every entry by a half (2.5 over 5), so the direction is unchanged and the norm is now 2.5. Clipping to 10 changes nothing, since 5 is under the limit: clipping only ever shrinks.
skills: [dead-and-exploding]
''',
)

mcq(
    "mcq-the-signs-of-exploding-gradients",
    "The gradient norm recorded at each step reads 0.9, 1.1, 3, 40, 2,000, then inf and NaN. What is happening, what causes it, and what fixes it?",
    [
        "The learning rate is too low and the gradients are piling up; raise the rate",
        "Exploding gradients: each step overshoots and makes the next gradient larger until the numbers overflow; a start too big or a rate too high causes it; He starts, a lower rate or clipping fix it",
        "Dead ReLUs: the units are dying one by one and the gradient that each dead unit would have received is being added onto the survivors, which is what makes the norm grow; a leaky ReLU, which keeps every unit alive, fixes it",
        "Normal: the gradient norm always grows as the network learns, and NaN just means it has finished learning",
    ],
    1,
    "A norm that grows step over step is the signature: the weights grow, the activations grow, the gradients grow, and float64 runs out of room. Through several layers a starting scale that is too large does it from the first step, and a rate that is too high does it after a few. Fix the start, lower the rate, or clip the norm so the step is bounded whatever the gradient does. Dead units give zero, not infinity, and a healthy norm usually shrinks as the loss falls.",
    ["dead-and-exploding"],
)

mcq(
    "mcq-labels-that-do-not-match",
    "A run's gradient check passes, eight rows overfit to a loss of 0.02, the rate is one that converged last week, and yet 30 epochs go 1.10 to 1.09 with validation accuracy 0.35. What happened?",
    [
        "The validation set is too small",
        "The labels don't match their rows: inputs and labels were shuffled apart, so there is no pattern; eight rows can be memorized, the full set can't, and held-out accuracy is chance",
        "The network is too small for the data, since the loss moved a little but not enough to matter; add a hidden layer, double its width, and train for ten times as many epochs before deciding anything",
        "The learning rate is too low after all",
    ],
    1,
    "Everything in the code checks out and the rate is known good, so the data is what is left. With random labels the network can memorize a handful of rows, which is why the one-batch test passes, but across 240 rows there is nothing consistent to fit, so the loss barely moves and the held-out accuracy is a third for three classes. The classic cause is a shuffle applied to X and not to y.",
    ["data-bugs"],
)

mcq(
    "mcq-inputs-on-the-wrong-scale",
    "The same network and rate that converged on inputs around 1 diverges on the same data multiplied by 1,000. Why, and what is the fix?",
    [
        "Big numbers overflow NumPy's integers; use float64",
        "A dense layer's gradient is its input times the output gradient, so inputs a thousand times larger give gradients a thousand times larger and the first steps are enormous; standardize each column with the training set's mean and spread",
        "The network needs more hidden units to represent large numbers",
        "The loss function can't handle large logits, since the exponentials inside softmax overflow for anything above a few hundred, so the only option is to switch the loss to mean squared error, which has no exponential in it and so never overflows, and to keep the rate",
    ],
    1,
    "`dW = X.T @ grad_out`: scale X by 1,000 and dW scales with it, so a rate that was right is now a thousand times too high. Standardizing (subtract the mean, divide by the spread, both measured on the training rows) puts every column near 1. The validation set must get the training set's numbers, not its own, so the two are on the same footing. The arrays are already float64, and the loss is fine.",
    ["data-bugs"],
)

write(
    "recall/parsons-standardize.yaml",
    "id: parsons-standardize\ntype: parsons\nrev: 1\nprompt: |\n"
    + block("Put the lines in order to standardize two columns with the training set's mean and spread, apply the same numbers to a validation row, and print both. One line is a decoy that doesn't belong.")
    + "lines:\n"
    + "".join(f"  - {quoted(line)}\n" for line in PARSONS_LINES)
    + "distractors:\n  - "
    + quoted("mean, std = X_val.mean(axis=0), X_val.std(axis=0)")
    + "\nexplanation: |\n"
    + block("The mean and spread come from the training rows, then both sets are shifted and scaled by those same two numbers, then printed. The decoy measures them on the validation set, which has one row: its spread is zero, the division gives NaN, and even with more rows the two sets would be on different footings.")
    + "skills: [data-bugs]\n",
)

mcq(
    "mcq-one-thing-at-a-time",
    "A run is stalled. A teammate proposes doubling the hidden layer, switching to Adam and tripling the epochs in one go. What is wrong with that?",
    [
        "Doubling the hidden layer is enough on its own, since a stalled run means the network is too small",
        "Nothing, as long as the seed is also changed, so the run gets a fresh start",
        "If the run improves nothing says which change did it, and if it gets worse nothing says which to undo; change one thing per run with the seed fixed, and start with the cheap checks",
        "Tripling the epochs is enough on its own, since a stalled run just needs more time to get going, and the other two changes can wait until the longer run has been given a fair chance to show what it does",
    ],
    2,
    "Three changes at once give one data point with three explanations. One change with the seed fixed gives a comparison in which only one thing differs, so the result can be attributed. And a stalled run might be a bug, dead units or bad data, none of which the three changes address; the checklist's cheap checks come first. Changing the seed as well adds a fourth difference.",
    ["bug-or-hard"],
)

write(
    "recall/review-predict-dead-units.yaml",
    f'''id: review-predict-dead-units
type: predict_output
rev: 1
prompt: |
  Hidden activations after a ReLU, four rows by three units. A dead unit is one that is zero on every row. What does the program print?
code: |
{block(REVIEW_PREDICT)}expected_output: |
{block(REVIEW_PREDICT_OUT)}explanation: |
  Only the middle unit is ever positive, so the other two are dead: two of three. The second row is zero in every unit, so one row passes nothing through the layer; for that row the layers above see nothing and learn nothing.
skills: [dead-and-exploding]
''',
)

mcq(
    "review-mcq-cannot-overfit-one-batch",
    "A network can't drive the loss on eight rows below 1.0 in 500 steps, and its gradient check fails on the second layer's weights. Where is the bug?",
    [
        "In the data: the eight rows must be mislabelled",
        "In the second layer's backward pass, which is the one thing both symptoms point at; the data and the hyperparameters are not yet in question",
        "In the learning rate, since eight rows need a much smaller rate than the full set, and the gradient check is only approximate, so a failure on one layer is normal",
        "In the optimizer, which must be stepping uphill",
    ],
    1,
    "A gradient check compares a backward gradient with central differences; a failure on one layer's weights means that layer's backward is wrong, and a network with a wrong gradient can't learn even eight rows. The data isn't in question until the code checks out, and an optimizer stepping uphill would fail the one-batch test but not the gradient check.",
    ["bug-or-hard"],
)

mcq(
    "review-mcq-which-fix",
    "Match the symptom to the first thing to try: (a) the loss is NaN at step 3 with inputs in the thousands; (b) the loss sits at 1.10 and all hidden units are dead; (c) the gradient norm grows a hundredfold a step with a good starting scale.",
    [
        "(a) standardize the inputs; (b) restart with zero biases and He-scaled weights at a lower rate; (c) lower the rate or clip the norm",
        "(a) lower the rate; (b) raise the rate; (c) add more layers",
        "(a) use mean squared error, which has no exponential to overflow; (b) add dropout, so the dead units are dropped anyway; (c) raise the rate, since a growing norm means the network is finally learning something",
        "(a), (b) and (c): train for more epochs",
    ],
    0,
    "Inputs on the wrong scale make the gradients enormous, so the fix is the scale, not the rate. Dead units can't recover, so the run restarts with a start that doesn't kill them and steps that won't. A norm growing step over step with a good start is a rate too high: lower it, or bound the step by clipping. None of the three is cured by patience.",
    ["learning-rate", "data-bugs"],
)

# =====================================================================================
# exercises
# =====================================================================================

write(
    "exercises/example-a-checklist-for-a-network-that-will-not-learn/exercise.yaml",
    f'''id: example-a-checklist-for-a-network-that-will-not-learn
stage: worked_example
rev: 1
title: "A checklist for a network that won't learn"
prompt: |
  Eight checks on the three clouds of points, each failure produced on purpose: the first loss, one batch, the gradient check, three learning rates, two ways to kill ReLUs, two ways to explode the gradient and two to stop it, two data bugs, and one word per run. Press **Run**, then read how each part works.
steps:
  - label: "The tools"
    lines: "{ln('def gradient_norm')}-{ln('return "learning"')}"
    note: "`gradient_norm` treats all the gradients as one vector and takes its length; `clip_gradients` scales them all down by the same factor when that length passes a limit. `fit` is The training loop's loop with three additions: its history starts with the losses before any training (entry 0, so every curve is read from its real start), it records the gradient norm at every step (before clipping) and can clip, and it runs under `errstate` so that overflow is read rather than crashed on. `dead_units` counts ReLU units that fire on no row; `overfit_one_batch` trains on a handful of rows; `standardize` applies a training-set mean and spread; `diagnose` gives a run one phrase."
  - label: "1 to 3: the cheap checks"
    lines: "{ln('# 1. Is the first loss')}-{ln('3. gradient check')}"
    note: "With the output layer started at scale 0.01 the first loss is log 3, 1.10: the network is guessing evenly. The default scale gives 1.38, higher than guessing, a start that already has opinions. Eight rows trained alone go from 1.11 to 0.02: the code can learn. The gradient check passes: backward is right. Whatever goes wrong below is not a bug in the layers."
  - label: "4: the learning rate"
    lines: "{ln('# 4. The learning rate')}-{ln('4. learning rate |')}"
    note: "Thirty epochs at three rates. At 0.0001 the loss moves from 1.10 to 1.03: stalled. At 0.05 it converges. At 30 it is NaN: diverging. The fix for the first two is the rate by a factor of ten, and the curve read again."
  - label: "5: dead ReLUs"
    lines: "{ln('# 5. Dead ReLUs')}-{ln('5. dead ReLUs |')}"
    note: "A hidden bias of -20 makes every unit's input negative on every row, so all 16 output 0, pass no gradient back, and the loss sits at 1.10 for thirty epochs: a stall that no learning rate would cure. A rate of 10 does the same by brute force: one huge step kills 12 of 16, and that run stalls rather than diverges, reading exactly like a rate that was too low. The healthy run at 0.05 has no dead units and reaches 0.90."
  - label: "6: exploding gradients"
    lines: "{ln('# 6. Exploding gradients')}-{ln('6. exploding gradients')}"
    note: "Six layers started at scale 1.0 (the right scale for 32 inputs is about 0.25): the gradient norm is about 10^3 at the very first step and overflows by step {OVERFLOW_STEP}. The He scale at a rate of 0.05 converges to 0.93. The He scale at a rate of 1.0 diverges, each step overshooting; the same run with the gradients clipped to a norm of 1 converges to 0.98, because the step can never be larger than the rate however large the gradient is."
  - label: "7 and 8: the data, and one word each"
    lines: "{ln('# 7. The data')}-{ln('8. one word each')}"
    note: "With the training labels shuffled apart from their rows, eight rows still memorize (0.02) but the full run goes 1.10 to 1.09 and held-out accuracy is 0.35, a third: there was no pattern to learn, and `diagnose` says stalled, the same word as a low rate. Inputs times 1000 diverge at the rate that was fine, because the first gradients are a thousand times larger; standardized with the training set's mean and spread they converge to 0.93. The last line is `diagnose` on four runs: learning, stalled, diverging, stalled."
''',
)
write("exercises/example-a-checklist-for-a-network-that-will-not-learn/solution.py", EXAMPLE)
write(
    "exercises/example-a-checklist-for-a-network-that-will-not-learn/test_exercise.py",
    f'''from checks import run


def test_the_walkthrough():
    """Prints the eight checks."""
    assert run() == {EXAMPLE_OUT!r}
''',
)

write(
    "exercises/fill-dead-units/exercise.yaml",
    f'''id: fill-dead-units
stage: fill_in
rev: 1
title: "Counting dead units"
prompt: |
  `dead_units(net, X)` should run a forward pass and count, over every `ReLU` layer, the units whose input was positive on no row of `X`: each `ReLU` keeps a `mask` of shape (rows, units) that is `True` where the input was positive. Replace each `...` so the program prints the count for a fresh network and again after four units of the first hidden layer and all sixteen of the second have their biases set to -20:

  ```
{block(FILL_OUT)}  ```

  The program fails until every `...` is replaced.
hints:
  - "`mask.any(axis=0)` collapses the rows and asks, unit by unit, whether any row fired."
  - "Only the ReLU layers have masks; `isinstance(layer, ReLU)` picks them out of `net.layers`."
skills: [dead-and-exploding]
''',
)
write("exercises/fill-dead-units/starter.py", FILL_STARTER)
write("exercises/fill-dead-units/solution.py", FILL_SOLUTION)
write(
    "exercises/fill-dead-units/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints 0 and then 20."""
    printed = run()
    assert printed == {FILL_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_other_cases():
    """A single killed unit counts as one; a network with no ReLU has none; a unit that fires on one row is alive."""
    # One import for everything, so the ReLU class dead_units looks for is the one the network was built with.
    dead_units = function("dead_units")
    Dense, ReLU, Sequential = (dead_units.__globals__[name] for name in ("Dense", "ReLU", "Sequential"))
    X = np.random.default_rng(1).standard_normal((40, 3))
    net = Sequential([Dense(3, 8, seed=2), ReLU(), Dense(8, 2, seed=3)])
    net.layers[0].b[5] = -50.0
    assert dead_units(net, X) == 1
    assert dead_units(Sequential([Dense(3, 2, seed=1)]), X) == 0
    net.layers[0].W[:, 5] = 0.0
    net.layers[0].b[5] = 0.0
    assert dead_units(net, X) == 1
    net.layers[0].b[5] = 1e-9
    assert dead_units(net, X) == 0
''',
)
write("exercises/fill-dead-units/wrong/counts-rows.py", FILL_ROWS)
write("exercises/fill-dead-units/wrong/counts-dense-layers.py", FILL_ALL_LAYERS)
write(
    "exercises/fill-dead-units/wrong/typed-in.py",
    "import numpy as np\n\n\nclass Dense:\n    def __init__(self, n_in, n_out, seed=0, scale=None):\n        self.W = np.zeros((n_in, n_out))\n        self.b = np.zeros(n_out)\n\n\nclass ReLU:\n    pass\n\n\nclass Sequential:\n    def __init__(self, layers):\n        self.layers = layers\n\n\ndef dead_units(net, X):\n    return 0\n\n\n" + "".join(f"print({line!r})\n" for line in FILL_OUT.splitlines()),
)

write(
    "exercises/write-clip-gradients/exercise.yaml",
    f'''id: write-clip-gradients
stage: write
rev: 1
title: "Gradient clipping"
prompt: |
  Write `gradient_norm(grads)`, the length of a list of gradient arrays taken together as one vector (the square root of the sum of all their squared entries, as a float), and `clip_gradients(grads, max_norm)`, which returns the same list scaled down by one factor so that its norm is exactly `max_norm` when it was above it, and returns `grads` itself, unchanged, when it was not. Called on the gradients in the starter, the program prints:

  ```
{block(WRITE_OUT)}  ```
hints:
  - "Sum `(grad ** 2).sum()` over the arrays, then take the square root: that is the norm of all of them together."
  - "The factor is `max_norm / norm`, applied to every array alike, so the direction of the step is unchanged."
skills: [dead-and-exploding]
''',
)
write("exercises/write-clip-gradients/starter.py", "import numpy as np\n\n\n# Write gradient_norm and clip_gradients here, above the data.\n\n\n" + WRITE_TAIL)
write("exercises/write-clip-gradients/solution.py", WRITE_SOLUTION)
write(
    "exercises/write-clip-gradients/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints the norm, the clipped list with its norm, and True."""
    printed = run()
    assert printed == {WRITE_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_other_cases():
    """Random gradients clip to the limit with their direction kept; small ones come back untouched; the originals are never changed."""
    gradient_norm = function("gradient_norm")
    clip_gradients = function("clip_gradients")
    rng = np.random.default_rng(2)
    grads = [rng.standard_normal((3, 4)), rng.standard_normal(5)]
    before = [grad.copy() for grad in grads]
    norm = gradient_norm(grads)
    assert isinstance(norm, float) and abs(norm - np.sqrt(sum((g ** 2).sum() for g in grads))) < 1e-12
    clipped = clip_gradients(grads, 0.5)
    assert abs(gradient_norm(clipped) - 0.5) < 1e-12
    assert np.allclose(clipped[0] / grads[0], clipped[1][0] / grads[1][0])
    assert clip_gradients(grads, norm + 1) is grads
    assert all(np.array_equal(a, b) for a, b in zip(grads, before))
    assert gradient_norm([np.zeros(3)]) == 0.0
''',
)
write("exercises/write-clip-gradients/wrong/clips-each-alone.py", WRITE_EACH)
write("exercises/write-clip-gradients/wrong/always-scales.py", WRITE_ALWAYS)
write(
    "exercises/write-clip-gradients/wrong/typed-in.py",
    "import numpy as np\n\n\ndef gradient_norm(grads):\n    return 13.0\n\n\ndef clip_gradients(grads, max_norm):\n    return grads\n\n\n" + "".join(f"print({line!r})\n" for line in WRITE_OUT.splitlines()),
)

# --- the proof -----------------------------------------------------------------------------------

write(
    "exercises/build-the-diagnostics/exercise.yaml",
    f'''id: build-the-diagnostics
stage: build
rev: 1
title: "The diagnostics"
prompt: |
  Starting from a blank editor, paste the module's `Dense` (with its `scale` argument, as Starting weights and activation functions left it), `ReLU`, `Sequential`, `SoftmaxCrossEntropy`, `SGD`, `numeric_gradient`, `gradient_check`, `make_blobs`, `batches`, `evaluate` and `read_curve` as The training loop left them, and this topic's `split`, which holds out the first rows of a seeded shuffle:

  ```python
{block(SPLIT.strip(), "  ")}  ```

  Then write:

  - `gradient_norm(grads)`: the length of the gradients taken together, as a float.
  - `clip_gradients(grads, max_norm)`: all scaled down by one factor to norm `max_norm` when above it; `grads` itself otherwise.
  - `fit(net, loss, optimizer, X_train, y_train, X_val, y_val, epochs, batch_size=32, seed=0, max_norm=None)`: the training loop (shuffled batches from `batches`, one `optimizer.step` per batch), whose history (`train_loss`, `val_loss`, `val_accuracy` from `evaluate`) starts with the values **before any training** and adds one entry per epoch, and also holds `grad_norms`, the norm at every step **before** any clipping; with `max_norm` the step uses the clipped gradients. Run the loop under `np.errstate(all="ignore")` so a run that overflows is recorded, not crashed.
  - `dead_units(net, X)`: a forward pass, then the number of ReLU units whose mask is `False` on every row, over all ReLU layers.
  - `overfit_one_batch(net, loss, X, y, steps=500, rate=0.1)`: train on exactly these rows, all of them every step, with `SGD(rate)`; return the loss before and after.
  - `standardize(X, mean, std)`: `(X - mean) / std`.
  - `diagnose(history, n_classes)`: `read_curve` of the training loss if it isn't `"converging"`; else `"at chance"` if the last validation accuracy is below `1 / n_classes + 0.1`; else `"learning"`.

  Then print:

  ```python
  X, y = make_blobs(100, seed=0)
  X_train, y_train, X_val, y_val = split(X, y, seed=0)
  loss = SoftmaxCrossEntropy()


  def small_net():
      return Sequential([Dense(2, 16, seed=1), ReLU(), Dense(16, 3, seed=2, scale=0.01)])


  first, last = overfit_one_batch(small_net(), loss, X_train[:8], y_train[:8])
  print(round(first, 2), round(last, 2), last < 0.1)
  runs = [fit(small_net(), loss, SGD(rate), X_train, y_train, X_val, y_val, epochs=30) for rate in (0.05, 0.0001, 30.0)]
  print(" | ".join(diagnose(history, 3) for history in runs), len(runs[0]["grad_norms"]))
  silenced = small_net()
  silenced.layers[0].b[:] = -20.0
  fit(silenced, loss, SGD(0.05), X_train, y_train, X_val, y_val, epochs=30)
  print(dead_units(silenced, X_train), dead_units(small_net(), X_train))
  print([round(float(v), 2) for v in clip_gradients([np.array([3.0, 4.0])], 1.0)[0]], gradient_norm([np.array([3.0, 4.0]), np.array([12.0])]))
  mean, std = X_train.mean(axis=0), X_train.std(axis=0)
  Z = standardize(X_train, mean, std)
  print(bool(np.abs(Z.mean(axis=0)).max() < 1e-12), Z.std(axis=0).round(6).tolist())
  ```

  ```
{block(BUILD_OUT)}  ```

  The checks test the norm and the clipping on random gradients, that `fit` starts its history before training, records one norm per step before clipping and that clipping bounds the step, `diagnose` on hand-made histories, `dead_units` and `overfit_one_batch` on small cases, `standardize` with the training set's numbers, and that the same seeds give the same history.
skills: [learning-rate, bug-or-hard, dead-and-exploding, data-bugs]
''',
)
write("exercises/build-the-diagnostics/starter.py", "")
write("exercises/build-the-diagnostics/solution.py", BUILD_SOLUTION)
write(
    "exercises/build-the-diagnostics/test_exercise.py",
    f'''import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def module():
    """Everything from one import of the solution, so its training runs once per test."""
    return function("fit").__globals__


def small_net(m):
    return m["Sequential"]([m["Dense"](2, 16, seed=1), m["ReLU"](), m["Dense"](16, 3, seed=2, scale=0.01)])


def data(m):
    X, y = m["make_blobs"](100, seed=0)
    return m["split"](X, y, seed=0)


def test_the_output():
    """Prints the five lines."""
    assert run() == {BUILD_OUT!r}


def test_norm_and_clip():
    """The norm is the length of everything together; clipping keeps the direction, lands on the limit, and leaves small gradients as they are."""
    m = module()
    gradient_norm, clip_gradients = m["gradient_norm"], m["clip_gradients"]
    rng = np.random.default_rng(2)
    grads = [rng.standard_normal((3, 4)), rng.standard_normal(5)]
    norm = gradient_norm(grads)
    assert isinstance(norm, float) and abs(norm - np.sqrt(sum((g ** 2).sum() for g in grads))) < 1e-12
    clipped = clip_gradients(grads, 0.5)
    assert abs(gradient_norm(clipped) - 0.5) < 1e-12 and np.allclose(clipped[0] / grads[0], clipped[1][0] / grads[1][0])
    assert clip_gradients(grads, norm + 1) is grads


def test_fit_records_and_clips():
    """One norm per step, recorded before clipping; entry 0 is the loss before training; a tiny limit keeps the weights almost where they started; the same seeds repeat exactly."""
    m = module()
    fit, SGD, SoftmaxCrossEntropy = m["fit"], m["SGD"], m["SoftmaxCrossEntropy"]
    X_train, y_train, X_val, y_val = data(m)
    loss = SoftmaxCrossEntropy()
    plain = fit(small_net(m), loss, SGD(0.05), X_train, y_train, X_val, y_val, epochs=3)
    assert len(plain["grad_norms"]) == 24 and len(plain["train_loss"]) == len(plain["val_loss"]) == len(plain["val_accuracy"]) == 4
    assert abs(plain["train_loss"][0] - 1.10) < 0.02
    clipped = fit(small_net(m), loss, SGD(0.05), X_train, y_train, X_val, y_val, epochs=3, max_norm=0.01)
    assert abs(clipped["grad_norms"][0] - plain["grad_norms"][0]) < 1e-12 and plain["grad_norms"][0] > 0.01
    net = small_net(m)
    before = [p.copy() for p in net.parameters()]
    fit(net, loss, SGD(0.05), X_train, y_train, X_val, y_val, epochs=1, max_norm=1e-6)
    assert all(np.abs(p - b).max() < 1e-5 for p, b in zip(net.parameters(), before))
    again = fit(small_net(m), loss, SGD(0.05), X_train, y_train, X_val, y_val, epochs=3)
    assert again["train_loss"] == plain["train_loss"] and again["grad_norms"] == plain["grad_norms"]


def test_diagnose():
    """Diverging, stalled, at chance and learning, from hand-made histories."""
    diagnose = function("diagnose")
    assert diagnose({{"train_loss": [1.1, 0.5, float("nan")], "val_accuracy": [0.3, 0.3, 0.3]}}, 3) == "diverging"
    assert diagnose({{"train_loss": [1.1, 1.05, 1.0], "val_accuracy": [0.3, 0.3, 0.3]}}, 3) == "stalled"
    assert diagnose({{"train_loss": [1.1, 0.8, 0.5], "val_accuracy": [0.3, 0.3, 0.4]}}, 3) == "at chance"
    assert diagnose({{"train_loss": [1.1, 0.8, 0.5], "val_accuracy": [0.3, 0.6, 0.9]}}, 3) == "learning"
    assert diagnose({{"train_loss": [0.7, 0.3], "val_accuracy": [0.5, 0.58]}}, 2) == "at chance"


def test_dead_and_overfit():
    """Three silenced units count as three; eight rows overfit to below a tenth and the network is left trained."""
    # One import for everything here, so the ReLU class dead_units looks for is the one the network was built with.
    dead_units = function("dead_units")
    overfit_one_batch, SoftmaxCrossEntropy, Dense, ReLU, Sequential, make_blobs, split = (dead_units.__globals__[name] for name in ("overfit_one_batch", "SoftmaxCrossEntropy", "Dense", "ReLU", "Sequential", "make_blobs", "split"))

    def net():
        return Sequential([Dense(2, 16, seed=1), ReLU(), Dense(16, 3, seed=2, scale=0.01)])

    X, y = make_blobs(100, seed=0)
    X_train, y_train, _, _ = split(X, y, seed=0)
    silenced = net()
    silenced.layers[0].b[:3] = -50.0
    assert dead_units(silenced, X_train) == 3 and dead_units(net(), X_train) == 0
    net = net()
    loss = SoftmaxCrossEntropy()
    first, last = overfit_one_batch(net, loss, X_train[:8], y_train[:8])
    assert abs(first - 1.11) < 0.02 and last < 0.1 and loss.forward(net.forward(X_train[:8]), y_train[:8]) < 0.1


def test_standardize():
    """Columns to mean 0 and spread 1 with the training set's numbers; the validation set gets the same numbers."""
    standardize = function("standardize")
    rng = np.random.default_rng(5)
    X_train = rng.normal(100.0, 20.0, size=(50, 2)) * np.array([1.0, 1000.0])
    X_val = rng.normal(100.0, 20.0, size=(10, 2)) * np.array([1.0, 1000.0])
    mean, std = X_train.mean(axis=0), X_train.std(axis=0)
    Z = standardize(X_train, mean, std)
    assert np.allclose(Z.mean(axis=0), 0.0) and np.allclose(Z.std(axis=0), 1.0)
    assert np.allclose(standardize(X_val, mean, std), (X_val - mean) / std)
''',
)
for key, code in BUILD_WRONGS.items():
    write(f"exercises/build-the-diagnostics/wrong/{key}.py", code)
write(
    "exercises/build-the-diagnostics/wrong/typed-in.py",
    "import numpy as np\n\n\ndef gradient_norm(grads):\n    return 13.0\n\n\ndef clip_gradients(grads, max_norm):\n    return grads\n\n\ndef fit(*args, **kwargs):\n    return {'train_loss': [], 'val_loss': [], 'val_accuracy': [], 'grad_norms': []}\n\n\ndef dead_units(net, X):\n    return 0\n\n\ndef overfit_one_batch(net, loss, X, y, steps=500, rate=0.1):\n    return 1.11, 0.02\n\n\ndef standardize(X, mean, std):\n    return X\n\n\ndef diagnose(history, n_classes):\n    return 'learning'\n\n\n"
    + "".join(f"print({line!r})\n" for line in BUILD_OUT.splitlines()),
)

write(
    "exercises/debug-a-run-that-will-not-learn/exercise.yaml",
    f'''id: debug-a-run-that-will-not-learn
stage: debug
rev: 1
title: "A run that won't learn"
prompt: |
  A training script with the module's loop and this topic's tools. It should print:

  ```
{block(DEBUG_OUT)}  ```

  It has two bugs. Run it: the loss is NaN by the end, diverging, and the dead count reads 16 of 16 only because the weights have overflowed to NaN (NaN is not greater than zero): `rate` is 50, a thousand times the 0.05 that converges. Fix that, and the run reads **stalled**, from 1.10 to 1.0-something, with validation accuracy {STILL_SPLIT_ACC}, chance; yet one batch still overfits and no units are dead, so the code can learn and the rate is known good. The data is what's left: `split` shuffles `X` and `y` with two different permutations, so the labels no longer belong to their rows; one permutation, applied to both, keeps them together.
skills: [learning-rate, data-bugs]
''',
)
write("exercises/debug-a-run-that-will-not-learn/starter.py", DEBUG_STARTER)
write("exercises/debug-a-run-that-will-not-learn/solution.py", DEBUG_SOLUTION)
write(
    "exercises/debug-a-run-that-will-not-learn/test_exercise.py",
    f'''import numpy as np

from checks import function, run

EXPECTED = {DEBUG_OUT!r}


def test_the_output():
    """Prints a learning run and a batch that overfits."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\\n{{EXPECTED}}\\nYour program printed:\\n{{printed}}"


def test_the_pieces():
    """split keeps every label with its row, and a fresh network overfits eight rows at the script's rate."""
    split = function("split")
    X = np.arange(20.0).reshape(10, 2)
    y = np.arange(10)
    X_train, y_train, X_val, y_val = split(X, y, seed=3)
    assert np.array_equal(X_train[:, 0] / 2, y_train) and np.array_equal(X_val[:, 0] / 2, y_val)
    assert len(X_train) == 8 and sorted(y_train.tolist() + y_val.tolist()) == list(range(10))
    assert not np.array_equal(X_train, X[2:]), "split must shuffle"
''',
)
write("exercises/debug-a-run-that-will-not-learn/wrong/still-a-rate-of-50.py", DEBUG_STILL_RATE)
write("exercises/debug-a-run-that-will-not-learn/wrong/still-shuffling-x-alone.py", DEBUG_STILL_SPLIT)
write(
    "exercises/debug-a-run-that-will-not-learn/wrong/typed-in.py",
    "import numpy as np\n\n\ndef split(X, y, seed, held_out=0.2):\n    n_val = int(len(X) * held_out)\n    return X[n_val:], y[n_val:], X[:n_val], y[:n_val]\n\n\n" + "".join(f"print({line!r})\n" for line in DEBUG_OUT.splitlines()),
)

write(
    "exercises/review-clip-gradients/exercise.yaml",
    f'''id: review-clip-gradients
stage: review_code
rev: 1
title: "Gradient clipping, from memory"
prompt: |
  Write `clip_gradients(grads, max_norm)`: scale every array in the list by the same factor so that their norm, all together, is at most `max_norm`, and return the list unchanged if it already is. Print it for `[np.array([6.0, 0.0]), np.array([[8.0]])]` clipped to 5, then to 20:

  ```
{block(REVIEW_CODE_OUT)}  ```
skills: [dead-and-exploding]
''',
)
write("exercises/review-clip-gradients/starter.py", "")
write("exercises/review-clip-gradients/solution.py", REVIEW_CODE_SOLUTION)
write(
    "exercises/review-clip-gradients/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints the clipped and the untouched list."""
    assert run() == {REVIEW_CODE_OUT!r}


def test_other_cases():
    """A random list lands on the limit with its direction kept; a small one is returned as is."""
    clip_gradients = function("clip_gradients")
    rng = np.random.default_rng(3)
    grads = [rng.standard_normal(4), rng.standard_normal((2, 2))]
    norm = float(np.sqrt(sum((g ** 2).sum() for g in grads)))
    clipped = clip_gradients(grads, 0.25)
    assert abs(float(np.sqrt(sum((g ** 2).sum() for g in clipped))) - 0.25) < 1e-12
    assert np.allclose(clipped[0] / grads[0], clipped[1][0, 0] / grads[1][0, 0])
    assert clip_gradients(grads, norm * 2) is grads
''',
)
write("exercises/review-clip-gradients/wrong/always-scales.py", REVIEW_CODE_WRONG)
write(
    "exercises/review-clip-gradients/wrong/typed-in.py",
    "import numpy as np\n\n\ndef clip_gradients(grads, max_norm):\n    return grads\n\n\n" + "".join(f"print({line!r})\n" for line in REVIEW_CODE_OUT.splitlines()),
)

print("ml.nn.debugging-training written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
