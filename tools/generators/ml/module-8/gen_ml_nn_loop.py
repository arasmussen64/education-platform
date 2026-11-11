"""Writes the topic ml.nn.training-loop (Module 8's fourth topic). Run from
the repository root under uv (python -m uv run python <this file>), so every
program's expected output is captured from CPython rather than typed in.
Training runs on a seeded three-blob dataset; losses are printed rounded,
curves are also read in words, and the generator checks that a tenth-decimal
nudge of the data leaves every line unchanged. Files are written as bytes
with LF endings."""

import pathlib
import subprocess
import sys

ROOT = pathlib.Path("content/topics/ml.nn.training-loop")


def write(relative: str, text: str) -> None:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


def out(program: str) -> str:
    result = subprocess.run([sys.executable, "-W", "error", "-c", program], capture_output=True, text=True, check=True)
    return result.stdout.replace("\r\n", "\n")


def out_loose(program: str) -> str:
    """Run as the browser would: a known-wrong solution may warn on its way to a wrong answer."""
    result = subprocess.run([sys.executable, "-c", program], capture_output=True, text=True, check=True)
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


# The module's classes as they stand, plus the two optimizers this topic adds.
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
    """Adam from Module 4: a running average of each gradient and of its square, with each step the average gradient divided by the square root of the average squared gradient."""

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
'''

LOOP = '''

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
'''

# --- the worked example ----------------------------------------------------------------------

EXAMPLE_HEAD = "import numpy as np\n\n\n" + LAYERS + LOOP
EXAMPLE_TAIL = '''

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
    first = history['train_loss'][0]
    shown = f"{first:.3g}" if first < 1000 else "over a thousand"
    print(f"learning rate {rate}: the training loss goes from {shown} to {history['train_loss'][-1]:.3g}: {read_curve(history['train_loss'])}")

for batch_size in (8, 240):
    history = fit(new_net(), loss, SGD(0.05), X_train, y_train, X_val, y_val, epochs=30, batch_size=batch_size)
    steps = 30 * -(-len(X_train) // batch_size)
    print(f"batch size {batch_size}: {steps} steps in 30 epochs, final validation accuracy {history['val_accuracy'][-1]:.2f}")

history = fit(new_net(), loss, Adam(0.01), X_train, y_train, X_val, y_val, epochs=30, batch_size=32)
print(f"Adam at 0.01, batch 32: final train loss {history['train_loss'][-1]:.3f}, validation accuracy {history['val_accuracy'][-1]:.2f}")
'''
EXAMPLE = EXAMPLE_HEAD + EXAMPLE_TAIL
EXAMPLE_OUT = out(EXAMPLE)
print("example:\n" + EXAMPLE_OUT)
EX = EXAMPLE_OUT.splitlines()
assert len(EX) == 13, EX
assert EX[0].startswith("rows: 240 to train on, 60 held out"), EX[0]
assert EX[6] == "the curve is converging | steps taken: 240", EX[6]
assert EX[7].endswith("stalled") and EX[8].endswith("converging") and EX[9].endswith("diverging"), EX[7:10]
FINAL_ACC = float(EX[5].split()[-1])
assert FINAL_ACC >= 0.85, FINAL_ACC
assert EX[10].startswith("batch size 8: 900 steps") and EX[11].startswith("batch size 240: 30 steps"), EX[10:12]
BATCH_8_ACC = float(EX[10].split()[-1])
BATCH_240_ACC = float(EX[11].split()[-1])
assert BATCH_240_ACC < BATCH_8_ACC, (BATCH_8_ACC, BATCH_240_ACC)
assert EX[12].startswith("Adam at 0.01, batch 32:"), EX[12]
ADAM_ACC = float(EX[12].split()[-1])
NUDGED = EXAMPLE.replace("X, y = make_blobs()", "X, y = make_blobs()\nX[0, 0] += 1e-10")
assert out(NUDGED) == EXAMPLE_OUT, "a tenth-decimal nudge changed a printed line"
EXAMPLE_LINES = EXAMPLE.splitlines()


def ln(text: str, after: int = 0) -> int:
    return next(i + 1 for i, line in enumerate(EXAMPLE_LINES) if i + 1 > after and text in line)


# --- recall programs ----------------------------------------------------------------------------

PREDICT_BATCHES = '''import numpy as np


def batches(n, batch_size, rng):
    order = rng.permutation(n)
    for start in range(0, n, batch_size):
        yield order[start : start + batch_size]


rng = np.random.default_rng(0)
sizes = [len(index) for index in batches(100, 32, rng)]
print(len(sizes), sizes, sum(sizes))
first = np.concatenate(list(batches(10, 4, np.random.default_rng(1))))
second = np.concatenate(list(batches(10, 4, np.random.default_rng(1))))
print(sorted(first.tolist()) == list(range(10)), bool((first == second).all()))
'''
PREDICT_BATCHES_OUT = out(PREDICT_BATCHES)
assert PREDICT_BATCHES_OUT == "4 [32, 32, 32, 4] 100\nTrue True\n", PREDICT_BATCHES_OUT

PREDICT_SPLIT = '''import numpy as np

order = np.random.default_rng(0).permutation(50)
cut = int(0.8 * 50)
train, val = order[:cut], order[cut:]
print(len(train), len(val), len(set(train.tolist()) & set(val.tolist())))
print(sorted(train.tolist() + val.tolist()) == list(range(50)))
'''
PREDICT_SPLIT_OUT = out(PREDICT_SPLIT)
assert PREDICT_SPLIT_OUT == "40 10 0\nTrue\n", PREDICT_SPLIT_OUT

REVIEW_STEPS = '''n_train = 1000
for batch_size in (1, 32, 250, 1000):
    steps_per_epoch = -(-n_train // batch_size)
    print(batch_size, steps_per_epoch, steps_per_epoch * 10)
'''
REVIEW_STEPS_OUT = out(REVIEW_STEPS)
assert REVIEW_STEPS_OUT == "1 1000 10000\n32 32 320\n250 4 40\n1000 1 10\n", REVIEW_STEPS_OUT

PARSONS_LINES = [
    "import numpy as np",
    "X = np.array([[1.0, 2.0], [3.0, 4.0]])",
    "W = np.zeros((X.shape[1], 1))",
    "pred = X @ W",
    "grad = X.T @ (2 * (pred - np.array([[1.0], [2.0]])) / 2)",
    "W = W - 0.1 * grad",
    "print(W.round(2).tolist())",
]
PARSONS_OUT = out("\n".join(PARSONS_LINES) + "\n")
assert PARSONS_OUT == "[[0.7], [1.0]]\n", PARSONS_OUT

# --- the fill-in --------------------------------------------------------------------------------

FILL_SOLUTION = '''import numpy as np


def batches(n, batch_size, rng):
    """Index arrays covering 0..n-1 once, in a fresh random order, batch_size at a time; the last batch may be short."""
    order = rng.permutation(n)
    for start in range(0, n, batch_size):
        yield order[start : start + batch_size]


rng = np.random.default_rng(0)
epoch_one = list(batches(10, 4, rng))
epoch_two = list(batches(10, 4, rng))
print([len(index) for index in epoch_one], sorted(np.concatenate(epoch_one).tolist()))
print(bool((np.concatenate(epoch_one) == np.concatenate(epoch_two)).all()))
'''
FILL_STARTER = FILL_SOLUTION.replace("    order = rng.permutation(n)\n    for start in range(0, n, batch_size):\n        yield order[start : start + batch_size]", "    order = rng.permutation(...)\n    for start in range(0, n, ...):\n        yield order[start : start + ...]")
FILL_WRONG = FILL_SOLUTION.replace("    order = rng.permutation(n)", "    order = np.arange(n)")
FILL_OUT = out(FILL_SOLUTION)
assert FILL_OUT == "[4, 4, 2] [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]\nFalse\n", FILL_OUT
assert differs(FILL_WRONG, FILL_OUT)

# --- the write ----------------------------------------------------------------------------------

WRITE_SOLUTION = '''import numpy as np


def accuracy(logits, labels):
    """The share of rows whose largest logit is the true class."""
    return float((logits.argmax(axis=1) == labels).mean())


def evaluate(net, loss, X, y):
    """Loss and accuracy on a whole set, with no training step."""
    logits = net.forward(X)
    return loss.forward(logits, y), accuracy(logits, y)


class Constant:
    """A stand-in network that always returns the same logits."""

    def __init__(self, logits):
        self.logits = logits

    def forward(self, X):
        return self.logits


class ZeroOneLoss:
    """A stand-in loss: the share of rows whose largest logit is not the true class."""

    def forward(self, logits, labels):
        return float((logits.argmax(axis=1) != labels).mean())


logits = np.array([[2.0, 1.0, 0.0], [0.1, 0.2, 0.7], [1.0, 3.0, 2.0], [0.5, 0.4, 0.3]])
labels = np.array([0, 2, 2, 1])
print(accuracy(logits, labels))
print(evaluate(Constant(logits), ZeroOneLoss(), np.zeros((4, 2)), labels))
'''
WRITE_OUT = out(WRITE_SOLUTION)
assert WRITE_OUT == "0.5\n(0.5, 0.5)\n", WRITE_OUT
WRITE_WRONG_AXIS = WRITE_SOLUTION.replace("    return float((logits.argmax(axis=1) == labels).mean())", "    return float((logits.argmax(axis=0) == labels).mean())")
WRITE_COUNTS = WRITE_SOLUTION.replace("    return float((logits.argmax(axis=1) == labels).mean())", "    return float((logits.argmax(axis=1) == labels).sum())")
assert differs(WRITE_WRONG_AXIS, WRITE_OUT) and differs(WRITE_COUNTS, WRITE_OUT)

# --- the build ----------------------------------------------------------------------------------

BUILD_HEAD = "import numpy as np\n\n\n" + LAYERS
BUILD_TAIL = '''

X, y = make_blobs()
X_train, y_train, X_val, y_val = split(X, y)
net = Sequential([Dense(2, 16, seed=0, scale=np.sqrt(2 / 2)), ReLU(), Dense(16, 3, seed=1)])
loss = SoftmaxCrossEntropy()
history = fit(net, loss, SGD(0.05), X_train, y_train, X_val, y_val, epochs=30, batch_size=32)
print(len(X_train), len(X_val), [len(history[key]) for key in ("train_loss", "val_loss", "val_accuracy")])
print(round(history["train_loss"][0], 3), round(history["train_loss"][-1], 3), round(history["val_accuracy"][-1], 2), read_curve(history["train_loss"]))
print([len(index) for index in batches(10, 4, np.random.default_rng(0))], accuracy(np.array([[2.0, 1.0], [0.0, 1.0], [3.0, 1.0]]), np.array([0, 1, 1])))
'''
BUILD_SOLUTION = BUILD_HEAD + LOOP + BUILD_TAIL
BUILD_OUT = out(BUILD_SOLUTION)
print("build:\n" + BUILD_OUT)
BUILD_LINES = BUILD_OUT.splitlines()
assert BUILD_LINES[0] == "240 60 [30, 30, 30]" and BUILD_LINES[1].endswith("converging") and BUILD_LINES[2] == "[4, 4, 2] 0.6666666666666666", BUILD_OUT
assert float(BUILD_LINES[1].split()[2]) >= 0.85, BUILD_OUT
assert out(BUILD_SOLUTION.replace("X, y = make_blobs()", "X, y = make_blobs()\nX[0, 0] += 1e-10")) == BUILD_OUT
BUILD_WRONGS = {
    "no-shuffle": BUILD_SOLUTION.replace("    order = rng.permutation(n)\n    for start in range(0, n, batch_size):", "    order = np.arange(n)\n    for start in range(0, n, batch_size):"),
    "validates-on-training-rows": BUILD_SOLUTION.replace("        val_loss, val_accuracy = evaluate(net, loss, X_val, y_val)", "        val_loss, val_accuracy = evaluate(net, loss, X_train, y_train)"),
    "steps-uphill": BUILD_SOLUTION.replace("            param -= self.rate * grad", "            param += self.rate * grad"),
    "one-batch-per-epoch": BUILD_SOLUTION.replace("        for index in batches(len(X_train), batch_size, rng):\n            loss.forward", "        for index in list(batches(len(X_train), batch_size, rng))[:1]:\n            loss.forward"),
}
for key, code in BUILD_WRONGS.items():
    assert code != BUILD_SOLUTION, key

# --- the debug ----------------------------------------------------------------------------------

DEBUG_SOLUTION = BUILD_HEAD + LOOP + '''

X, y = make_blobs()
X_train, y_train, X_val, y_val = split(X, y)
net = Sequential([Dense(2, 16, seed=0, scale=np.sqrt(2 / 2)), ReLU(), Dense(16, 3, seed=1)])
loss = SoftmaxCrossEntropy()
history = fit(net, loss, SGD(0.05), X_train, y_train, X_val, y_val, epochs=20, batch_size=32)
print("training loss:", round(history["train_loss"][0], 3), "->", round(history["train_loss"][-1], 3), "|", read_curve(history["train_loss"]))
print("validation accuracy after 20 epochs:", round(history["val_accuracy"][-1], 2), "| above 0.6:", history["val_accuracy"][-1] > 0.6)
'''
BUG_UPHILL = ("            param -= self.rate * grad", "            param += self.rate * grad")
BUG_AXIS = ("    return float((logits.argmax(axis=1) == labels).mean())", "    return float((logits.argmax(axis=0) == labels).mean())")
DEBUG_STARTER = DEBUG_SOLUTION.replace(*BUG_UPHILL).replace(*BUG_AXIS)
DEBUG_STILL_UPHILL = DEBUG_SOLUTION.replace(*BUG_UPHILL)
DEBUG_STILL_AXIS = DEBUG_SOLUTION.replace(*BUG_AXIS)
DEBUG_OUT = out(DEBUG_SOLUTION)
print("debug:\n" + DEBUG_OUT)
assert DEBUG_OUT.splitlines()[0].endswith("| converging") and DEBUG_OUT.splitlines()[1].endswith("True"), DEBUG_OUT
STARTER_RESULT = subprocess.run([sys.executable, "-c", DEBUG_STARTER], capture_output=True, text=True)
assert STARTER_RESULT.returncode != 0 or "diverging" in STARTER_RESULT.stdout, STARTER_RESULT.stdout + STARTER_RESULT.stderr
assert differs(DEBUG_STILL_UPHILL, DEBUG_OUT) and differs(DEBUG_STILL_AXIS, DEBUG_OUT)
assert "diverging" in out_loose(DEBUG_STILL_UPHILL), out_loose(DEBUG_STILL_UPHILL)
assert out(DEBUG_SOLUTION.replace("X, y = make_blobs()", "X, y = make_blobs()\nX[0, 0] += 1e-10")) == DEBUG_OUT

REVIEW_CODE_SOLUTION = '''import numpy as np


def batches(n, batch_size, rng):
    """Index arrays covering 0..n-1 once in a fresh random order, batch_size at a time; the last may be short."""
    order = rng.permutation(n)
    for start in range(0, n, batch_size):
        yield order[start : start + batch_size]


rng = np.random.default_rng(3)
first = list(batches(23, 5, rng))
second = list(batches(23, 5, rng))
print([len(index) for index in first], sorted(np.concatenate(first).tolist()) == list(range(23)))
print(bool((np.concatenate(first) == np.concatenate(second)).all()))
'''
REVIEW_CODE_OUT = out(REVIEW_CODE_SOLUTION)
assert REVIEW_CODE_OUT == "[5, 5, 5, 5, 3] True\nFalse\n", REVIEW_CODE_OUT
REVIEW_CODE_WRONG = REVIEW_CODE_SOLUTION.replace("    order = rng.permutation(n)", "    order = np.arange(n)")
assert differs(REVIEW_CODE_WRONG, REVIEW_CODE_OUT)

# =====================================================================================
# topic.yaml
# =====================================================================================

write(
    "topic.yaml",
    '''id: ml.nn.training-loop
kind: topic
status: ready
title: "The training loop"
summary: "Epochs, mini-batches and shuffling; a fit function that trains a network with an optimizer and records the loss; evaluating on data the network hasn't seen; accuracy and a loss curve read from text; and what the batch size and the learning rate change."
prerequisites: [ml.nn.backward-layers]
packages: [numpy]
estimated_minutes: 55
rev: 1
objectives:
  - "Write a training loop over epochs and shuffled mini-batches, with a stochastic gradient descent or Adam step per batch."
  - "Split data into training and validation sets, and evaluate loss and accuracy on the validation set every epoch."
  - "Read a loss curve: converging, diverging, stalled."
  - "Say what the batch size trades (noise against speed) and how the learning rate interacts with it."
# Linked, never copied or embedded: Wikipedia is CC BY-SA 4.0; Nielsen's book
# is CC BY-NC 3.0.
resources:
  - title: "Wikipedia: Stochastic gradient descent (the Background and Iterative method sections: why a mini-batch's gradient stands in for the whole set's)"
    url: https://en.wikipedia.org/wiki/Stochastic_gradient_descent
    type: reading
    use: link
    license: CC BY-SA 4.0 (linked, not copied)
  - title: "Wikipedia: Training, validation, and test data sets (what each set is for, and why the validation set is never trained on)"
    url: https://en.wikipedia.org/wiki/Training,_validation,_and_test_data_sets
    type: reading
    use: link
    license: CC BY-SA 4.0 (linked, not copied)
  - title: "Neural Networks and Deep Learning, chapter 1 (Michael Nielsen), the sections Learning with gradient descent and Implementing our network to classify digits: the mini-batch loop in code"
    url: https://neuralnetworksanddeeplearning.com/chap1.html
    type: reading
    use: link
    license: CC BY-NC 3.0 (linked, not copied)
practice:
  - example-a-training-loop
  - predict-batches
  - mcq-epoch-and-step
  - predict-a-split
  - mcq-why-shuffle
  - parsons-one-step
  - mcq-why-a-validation-set
  - mcq-reading-the-curve
  - mcq-the-batch-size-trade
  - fill-batches
  - write-accuracy-and-evaluate
prove:
  build: build-fit
  debug: debug-a-loop-that-does-not-learn
  explain:
    prompt: |
      A teammate who has only ever called a library's `fit` asks four things about yours. "What is an epoch, what is a step, and why do you shuffle the rows every epoch?" "Why hold rows back in a validation set when more training rows would help?" "My training loss went 1.1, 1.0, 1.1, 1.3, 2.0, 7.4: what is that curve telling me, and what if it had gone 1.10, 1.09, 1.09, 1.08 instead?" "Is a batch size of 1 or of the whole set better, and does the learning rate have to change with it?" In your own words, answer all four.
    rubric:
      - id: loop
        required: true
        description: "An epoch is one pass over every training row; a step is one forward, loss, backward and update on one mini-batch, so an epoch has rows over batch size steps. The rows are shuffled every epoch so that each batch is a fresh sample, no batch is always the same rows, and an ordering in the data can't leak into the gradient."
      - id: validation
        required: true
        description: "Training loss and accuracy measure what the network has memorized as much as what it has learned; rows it never trained on measure what generalizes. The validation set is cut once, before training, and used only to evaluate (and later to choose hyperparameters and when to stop); the price of a few fewer training rows buys the only honest number."
      - id: curves
        required: true
        description: "A loss that rises and keeps rising is diverging: the learning rate is too high (or something is wrong with the data or the gradients) and each step overshoots. A loss that barely moves is stalled: the learning rate is too low, or the starting weights or the data are broken, which the next topics' checks tell apart. Converging is a fall that levels off."
      - id: batch
        required: true
        description: "A smaller batch gives more steps per epoch and a noisier gradient, and uses less memory; a larger batch gives a smoother gradient and fewer steps, so it needs more epochs or a larger learning rate to cover the same ground, and uses the hardware better (Parallelism and what a GPU is good at). Batch size 1 is pure stochastic descent; the whole set is plain gradient descent; 32 to 256 is the usual middle."
    model_answer: |
      An epoch is one pass through every training row. A step is what happens on one mini-batch: a forward pass, the loss, a backward pass and one update of every parameter, so an epoch of 240 rows in batches of 32 is 8 steps, and 30 epochs is 240 steps. I shuffle the rows at the start of every epoch so that each batch is a fresh random sample of the data rather than the same 32 rows in the same order every time; without the shuffle the last, short batch would always hold the same rows, any ordering in the file, such as the classes being stored in blocks, would leak into every gradient, and the loss would move in a pattern that has nothing to do with learning. The validation rows are held back because the training loss can't tell learning from memorizing: a network that has seen a row can get it right by remembering it. Rows it has never trained on measure what generalizes, which is the only number that matters when the model meets new data. The set is cut once, before training, with a seeded shuffle so the cut is reproducible, and it is used only to evaluate after each epoch; later it also decides when to stop and which settings to keep. A few fewer training rows is a cheap price for an honest score. The curve 1.1, 1.0, 1.1, 1.3, 2.0, 7.4 is diverging: after a small improvement the loss rises and then runs away, which means each step is overshooting, and the usual cause is a learning rate that is too high, with a broken gradient or unscaled inputs as the other suspects. The fix is to lower the rate, by a factor of ten to start, and watch again. The curve 1.10, 1.09, 1.09, 1.08 is stalled: it is moving in the right direction but so slowly that something is off, usually a learning rate that is too low, sometimes weights that started at zero or too small, or data that isn't what the code thinks it is. Converging looks like neither: a clear fall that levels off. A batch of 1 is stochastic gradient descent in its purest form, one update per row, the most steps per epoch and the noisiest gradient, which can be good for escaping flat regions but wastes the hardware; a batch of the whole set is plain gradient descent, one smooth step per epoch, so it needs many more epochs or a larger learning rate to travel the same distance. The example's batch of 8 took 900 steps in 30 epochs and the full batch of 240 took 30, and the full batch finished less accurate at the same rate. The learning rate does interact with it: a larger batch has a less noisy gradient and can usually take a larger step, and a smaller batch needs a smaller one, which is why changing the batch size means re-tuning the rate. The usual middle is 32 to 256, a size the hardware handles in one go, with Adam adjusting the step per parameter on top.
review_pool:
  - review-predict-steps-per-epoch
  - review-mcq-a-flat-curve
  - review-mcq-batch-and-rate
  - review-batches
# What this topic teaches. Each question names the skills it tests, so a
# missed question can come back as a different one on the same skill
# (ADR-0011).
skills:
  - id: loop
    description: "Write a training loop over epochs and shuffled mini-batches, one forward, loss, backward and update per batch"
  - id: validation
    description: "Split data into training and validation sets and evaluate loss and accuracy on the held-out rows"
  - id: curves
    description: "Read a loss curve as converging, stalled or diverging, and say what each means"
  - id: batch
    description: "Say what the batch size trades and how the learning rate interacts with it"
''',
)

# =====================================================================================
# lesson.mdx
# =====================================================================================

write(
    "lesson.mdx",
    f'''<Intro>

Layers that carry their gradient gave every layer a `backward` and every loss a gradient; this one turns "forward, loss, backward, update" into the loop every library calls `fit`. The loop walks the training rows in shuffled **mini-batches**, takes one optimizer step per batch, and after each pass over the data (an **epoch**) measures the loss and the accuracy on rows it has never trained on. The topic ends by reading the curve that loop produces, converging, stalled or diverging, and by changing the two knobs that shape it, the learning rate and the batch size.

The main resource is **Wikipedia's _Stochastic gradient descent_ page**, whose Background and Iterative method sections say why one mini-batch's gradient is a fair stand-in for the whole set's; about 15 minutes. The _Training, validation, and test data sets_ page explains the split, and Nielsen's chapter 1 has the same mini-batch loop written out in code. Watch for:

- **Stochastic**: a random subset's gradient points roughly the right way, far more cheaply.
- **Held-out rows**: why the validation set is never trained on.
- **The learning rate** in the update rule, and what happens on either side of the right value.

</Intro>

<Resource index={{0}} />

<Recap>

- **The loop.** For each **epoch** (one pass over the training rows), shuffle the row indices, cut them into **mini-batches** of `batch_size`, and for each batch take one **step**: forward, loss, backward, update. 240 rows in batches of 32 is 8 steps per epoch (the last batch has 16); 30 epochs is 240 steps. `fit` wraps this and returns a **history**: training loss, validation loss and validation accuracy after every epoch.
- **Shuffling** every epoch makes each batch a fresh random sample: no batch is always the same rows, the short last batch rotates, and an ordering in the data (classes stored in blocks, rows sorted by date) can't leak into the gradient. `rng.permutation(n)` with a seeded generator makes the shuffle reproducible.
- **Optimizers as objects.** `SGD(rate).step(params, grads)` does `param -= rate * grad` for every pair; `Adam(rate)` keeps a running average of each gradient and of its square and divides the average gradient by the square root of the average squared gradient to size each parameter's step, as Optimizers beyond plain gradient descent derived. The loop doesn't care which: it asks the network for `parameters()` and `gradients()` and hands them over.
- **The split.** Cut the rows once, before training, with a seeded shuffle: 80 percent to train on, 20 percent held out as the **validation set**, which is only ever evaluated. Training loss measures what the network has memorized as much as what it has learned; the held-out rows measure what **generalizes**. Later topics use the validation curve to catch overfitting and to decide when to stop; a final **test set**, touched once at the very end, is the convention when the validation set has been used to make choices.
- **Reading the curve.** The example's loss falls steadily from its first epoch and levels off (guessing a third for every class would sit at `log 3`, 1.099; after one epoch the loss is already well below that): **converging**, with validation accuracy {FINAL_ACC:.0%}. At a learning rate of 0.00005 it moves by a few hundredths in 30 epochs: **stalled**, usually a rate that is too low, sometimes dead starting weights or broken data. At 30 the loss is over a thousand after the first epoch and NaN by the end: **diverging**, a rate that is too high, each step overshooting. The first fix for either is the rate, by a factor of ten; When training goes wrong adds the checks that tell a bad rate from a bug.
- **The batch size trades noise against speed.** Batch 8 took 900 steps in 30 epochs and reached {BATCH_8_ACC:.0%}; the full batch of 240 took 30 smooth steps and reached {BATCH_240_ACC:.0%} at the same rate: fewer, smoother steps cover less ground per epoch, so a large batch needs more epochs or a larger learning rate (and uses the hardware better, as Parallelism and what a GPU is good at showed). Batch 1 is pure stochastic descent; the whole set is plain gradient descent; 32 to 256 is the usual middle. **Changing the batch size means re-tuning the rate.**
- **Accuracy** is the share of rows whose largest logit is the true class, `(logits.argmax(axis=1) == labels).mean()`; the axis matters, since `argmax(axis=0)` picks rows instead of classes. **Evaluation never updates**: forward and loss only, on the whole set at once.
- **In machine learning** (names you'll meet later): a `DataLoader` is `batches` with the shuffle and the slicing built in; `model.train()` and `model.eval()` switch layers such as dropout between the two modes Regularization: learning what generalizes introduces; a **learning-rate schedule** lowers the rate as training goes on; **early stopping** watches the validation curve; and the loss curve in a dashboard is `history` plotted.

</Recap>
''',
)

# =====================================================================================
# recall
# =====================================================================================

write(
    "recall/predict-batches.yaml",
    f'''id: predict-batches
type: predict_output
rev: 1
prompt: |
  `batches` shuffles the row indices and hands them out `batch_size` at a time. For 100 rows in batches of 32, and then twice for 10 rows with the same seed. What does the program print?
code: |
{block(PREDICT_BATCHES)}expected_output: |
{block(PREDICT_BATCHES_OUT)}explanation: |
  100 rows make three full batches of 32 and a last one of 4, covering every row once. Two generators with the same seed produce the same permutation, so the two runs hand out the same indices in the same order, and every index from 0 to 9 appears exactly once.
skills: [loop]
''',
)

mcq(
    "mcq-epoch-and-step",
    "A training set of 1,000 rows is trained for 5 epochs in batches of 50. How many steps is that, and what is one step?",
    [
        "5 steps: one update per epoch, using the average gradient over all 1,000 rows, which is what an epoch means",
        "100 steps: 20 batches per epoch times 5 epochs, each one forward, loss, backward and update on 50 rows",
        "5,000 steps: one update per row per epoch",
        "50 steps: one per batch size, however many epochs",
    ],
    1,
    "An epoch is one pass over the training rows; a step is one mini-batch through forward, loss, backward and update. 1,000 rows in batches of 50 is 20 steps per epoch, so 100 in all. One update per epoch would be full-batch gradient descent and one per row would be a batch size of 1; both are choices, not what batches of 50 mean.",
    ["loop"],
)

write(
    "recall/predict-a-split.yaml",
    f'''id: predict-a-split
type: predict_output
rev: 1
prompt: |
  Fifty rows split 80/20 by a seeded shuffle: the sizes, how many indices the two parts share, and whether together they cover every row. What does the program print?
code: |
{block(PREDICT_SPLIT)}expected_output: |
{block(PREDICT_SPLIT_OUT)}explanation: |
  The permutation is every index once in a random order; cutting it at 40 gives 40 training indices and 10 validation ones with nothing in common, and together they are all 50. That is what makes the validation rows honest: none of them is trained on.
skills: [validation]
''',
)

mcq(
    "mcq-why-shuffle",
    "Why does `fit` reshuffle the training rows at the start of every epoch, rather than once?",
    [
        "So that the validation set changes every epoch and the accuracy reported at the end is an average over many different held-out sets rather than one",
        "Because NumPy requires a new permutation before it can slice an array",
        "So that each batch is a fresh random sample: no batch is always the same rows, and an ordering in the data can't leak into the gradients",
        "To make the loss curve smoother, since shuffled rows have smaller gradients",
    ],
    2,
    "Without a fresh shuffle the same 32 rows would form the same batch in the same position every epoch, the last short batch would always hold the same leftovers, and any structure in that one order would repeat into every epoch's steps. The validation set is cut once and never changes; shuffling makes the gradients noisier, not smaller.",
    ["loop"],
)

write(
    "recall/parsons-one-step.yaml",
    "id: parsons-one-step\ntype: parsons\nrev: 1\nprompt: |\n"
    + block("Put the lines in order to take one gradient-descent step of a one-layer network in plain arrays (forward, the mean-squared-error gradient, the weight gradient, the update) and print the new weights, `[[0.7], [1.0]]`. One line is a decoy that doesn't belong.")
    + "lines:\n"
    + "".join(f"  - {quoted(line)}\n" for line in PARSONS_LINES)
    + "distractors:\n  - "
    + quoted("W = W + 0.1 * grad")
    + "\nexplanation: |\n"
    + block("The forward pass needs X and W, the loss's gradient needs the prediction, the weight gradient is X transposed times that, and the update subtracts the learning rate times the gradient: each line depends on the one before, which is the order of every training step. With zero weights the predictions are 0, the differences are -1 and -2, and the gradient is [-7, -10], so the new weights are 0.7 and 1.0. The decoy adds the gradient instead of subtracting it, which steps uphill.")
    + "skills: [loop]\n",
)

mcq(
    "mcq-why-a-validation-set",
    "Why hold 20 percent of the rows back from training, when training on all of them would make the network better?",
    [
        "Because the optimizer needs a second set to compute the learning rate, which it reads from the gap between the two sets' losses after every epoch",
        "Because a network trained on every row would have no rows left to shuffle into batches",
        "Because training loss measures what the network memorized as much as what it learned; rows it never saw measure what generalizes",
        "Because the held-out rows are used to initialize the weights",
    ],
    2,
    "A network that has seen a row can get it right by remembering it, so the training score can keep improving while the model gets worse on anything new. The held-out rows are never trained on, so their loss and accuracy are an honest estimate; the cost of a few fewer training rows is small beside that. Nothing about optimization or initialization uses them.",
    ["validation"],
)

mcq(
    "mcq-reading-the-curve",
    "Two training runs. In the first the loss goes 1.10, 1.08, 1.15, 1.40, 2.9, 31. In the second it goes 1.100, 1.098, 1.097, 1.095 over the same epochs. What is each curve saying?",
    [
        "The first is converging quickly and the second slowly; both are fine",
        "The first is diverging: the rate is too high and each step overshoots. The second is stalled: the rate is too low, or the weights or data are broken",
        "The first has found the minimum and is exploring around it, which is what a large loss after a small one means; the second has overfitted the training rows",
        "Both show a batch size that is too small",
    ],
    1,
    "A loss that rises and runs away means the steps are overshooting: lower the learning rate by a factor of ten first. A loss that moves by a thousandth per epoch is barely training: raise the rate, and if that does nothing, suspect the starting weights or the data. Converging looks like a clear fall that levels off, and overfitting shows in the gap between training and validation curves, not in the training curve alone.",
    ["curves"],
)

mcq(
    "mcq-the-batch-size-trade",
    "At the same learning rate and number of epochs, what changes when the batch size goes from 8 to the whole training set?",
    [
        "Nothing: the same rows are seen the same number of times either way",
        "The gradients become exact and training finishes in one epoch",
        "Far fewer, smoother steps per epoch: the gradient is less noisy but covers less ground, so it needs more epochs or a larger rate",
        "The validation set gets larger, so the accuracy is measured more precisely and the curve looks smoother than it did with small batches",
    ],
    2,
    "The step count is rows over batch size per epoch: 30 steps for the full batch against 900 for batches of 8 in the example, and each full-batch step is one average gradient rather than many noisy ones. Fewer steps of the same size travel less, which is why the full batch finished less accurate at the same rate. The batch size never touches the validation set, and an exact gradient does not mean a one-step solution.",
    ["batch"],
)

write(
    "recall/review-predict-steps-per-epoch.yaml",
    f'''id: review-predict-steps-per-epoch
type: predict_output
rev: 1
prompt: |
  Steps per epoch and steps in 10 epochs for 1,000 training rows at four batch sizes. What does the program print?
code: |
{block(REVIEW_STEPS)}expected_output: |
{block(REVIEW_STEPS_OUT)}explanation: |
  Steps per epoch is the rows divided by the batch size, rounded up for a short last batch: a batch of 1 is one step per row, 32 gives 32 (the last batch has 8 rows), 250 gives 4, and the whole set gives 1. Ten epochs multiply each by ten; the batch size decides how many updates a pass over the data buys.
skills: [batch]
''',
)

mcq(
    "review-mcq-a-flat-curve",
    "A training loss sits at 1.0986 for 30 epochs, to four decimals, on a three-class problem. What is the most likely story?",
    [
        "The network has converged to the best possible loss for this data, which three overlapping classes can't improve on however long it trains, so the run is finished",
        "Nothing is learned: 1.0986 is log 3, guessing a third for every class; the gradient isn't reaching the weights, the rate is zero, or the labels are misaligned",
        "The batch size is too large, so each epoch has too few steps for the loss to move",
        "The validation set is too small",
    ],
    1,
    "The natural logarithm of 3 is 1.0986: exactly the loss of a softmax that assigns a third to every class. A loss parked there isn't slow, it is stuck, and the suspects are a learning rate of zero, starting weights that give no gradient, a bug in backward, or labels that don't match the rows. A converged network on this data sits far lower, and batch size and validation size don't pin a loss to a constant.",
    ["curves"],
)

mcq(
    "review-mcq-batch-and-rate",
    "A model trains well at batch size 32 and learning rate 0.05. A teammate switches to batch size 1,024 to use the GPU better and keeps the rate. What should they expect, and what helps?",
    [
        "Faster convergence per epoch, since each step now uses an almost exact gradient and so can be trusted to point straight at the minimum from the first step",
        "Slower progress per epoch: 32 times fewer steps of the same size; raise the learning rate or train for more epochs to make up the ground",
        "Divergence, since large batches make the gradient too large",
        "No change, since the batch size only affects memory",
    ],
    1,
    "Each epoch now takes 32 times fewer steps, and a step of the same size covers the same distance whatever the batch, so the model travels a thirty-second as far per epoch. The larger batch's gradient is less noisy, which is exactly what lets it take a larger step: scaling the rate up with the batch, or training longer, recovers the progress. A bigger batch averages the gradient, it doesn't enlarge it.",
    ["batch"],
)

# =====================================================================================
# exercises
# =====================================================================================

write(
    "exercises/example-a-training-loop/exercise.yaml",
    f'''id: example-a-training-loop
stage: worked_example
rev: 1
title: "A training loop"
prompt: |
  Three overlapping clouds of points to classify, split into training and validation rows; `fit` over 30 epochs of shuffled mini-batches with the history printed as text bars; the same loop at a learning rate that stalls and one that diverges; batch sizes of 8 and of the whole set; and Adam. Press **Run**, then read how each part works.
steps:
  - label: "The classes and the optimizers"
    lines: "{ln('class Dense:')}-{ln('param -= self.rate * m_hat')}"
    note: "The module's layers and the softmax cross-entropy as they stand after the last topics, plus two optimizers as objects: `SGD.step` subtracts the learning rate times the gradient from every parameter, and `Adam.step` keeps running averages of each gradient and of its square and divides the average gradient by the square root of the average squared gradient to size each parameter's step, as Module 4 derived. The loop asks the network for `parameters()` and `gradients()` and hands them to whichever optimizer it was given."
  - label: "Data, the split, batches and evaluation"
    lines: "{ln('def make_blobs')}-{ln('return loss.forward(logits, y), accuracy(logits, y)')}"
    note: "`make_blobs` draws 100 points around each of three centres with a seed. `split` shuffles once and cuts 80/20: the validation rows are never trained on. `batches` shuffles the training indices afresh and yields them `batch_size` at a time, the last batch short. `accuracy` is the share of rows whose largest logit is the true class; `evaluate` runs forward and the loss on a whole set with no update."
  - label: "fit, and reading a curve"
    lines: "{ln('def fit(')}-{ln('converging')}"
    note: "For each epoch, for each batch: forward, loss, backward, step. After the epoch, the training and validation losses and the validation accuracy go into the history. `read_curve` names a curve from its first and last values: diverging if the loss grew by half or stopped being a number, stalled if it fell by less than a tenth, converging otherwise."
  - label: "Thirty epochs, printed"
    lines: "{ln('X, y = make_blobs()')}-{ln('the curve is')}"
    note: "240 training rows and 60 held out (the split is random, so the classes aren't exactly 20 each). Guessing a third for every class would sit at log 3, 1.099; after one epoch the loss is already well below that and it falls steadily; the bars shrink; the validation accuracy climbs to {FINAL_ACC:.0%}. Eight batches an epoch for thirty epochs is 240 steps."
  - label: "A rate that stalls and one that diverges"
    lines: "{ln('for rate in (0.00005, 0.05, 30.0)')}-{ln('the training loss goes from')}"
    note: "At 0.00005 (printed as 5e-05) the loss moves by a few hundredths in thirty epochs: stalled. At 0.05 it converges. At 30 every step overshoots so badly that the loss is already over a thousand after the first epoch (in the quadrillions, in fact) and NaN by the end: diverging (the `errstate` only silences NumPy's overflow warnings so the run can finish). The first fix for either is the learning rate, by a factor of ten."
  - label: "Batch size, and Adam"
    lines: "{ln('for batch_size in (8, 240)')}-{ln('Adam at 0.01')}"
    note: "Batches of 8 take 900 steps in thirty epochs and reach {BATCH_8_ACC:.0%}; the whole set as one batch takes 30 smooth steps and reaches {BATCH_240_ACC:.0%} at the same rate, because fewer steps of the same size cover less ground. Adam at 0.01 on batches of 32 reaches {ADAM_ACC:.0%}, adjusting each parameter's step on its own."
''',
)
write("exercises/example-a-training-loop/solution.py", EXAMPLE)
write(
    "exercises/example-a-training-loop/test_exercise.py",
    f'''from checks import run


def test_the_walkthrough():
    """Prints the split, five epochs of history, the curve, three learning rates, two batch sizes and Adam."""
    assert run() == {EXAMPLE_OUT!r}
''',
)

write(
    "exercises/fill-batches/exercise.yaml",
    f'''id: fill-batches
stage: fill_in
rev: 1
title: "Shuffled mini-batches"
prompt: |
  `batches(n, batch_size, rng)` should yield index arrays that cover the rows `0` to `n - 1` exactly once, in a fresh random order each time it is called, `batch_size` at a time, with a short last batch if the rows don't divide evenly. Replace each `...` so the program prints:

  ```
{block(FILL_OUT)}  ```

  The program fails until every `...` is replaced.
hints:
  - "`rng.permutation(n)` is every index once in a random order; slicing it in steps of the batch size gives the batches."
  - "The second epoch draws a new permutation from the same generator, so its order differs from the first."
skills: [loop]
''',
)
write("exercises/fill-batches/starter.py", FILL_STARTER)
write("exercises/fill-batches/solution.py", FILL_SOLUTION)
write(
    "exercises/fill-batches/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints the batch sizes, the covered indices and False for a repeated order."""
    printed = run()
    assert printed == {FILL_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_other_sizes():
    """Every index appears once per epoch, the last batch is short when needed, and two epochs differ."""
    batches = function("batches")
    rng = np.random.default_rng(5)
    one = list(batches(23, 5, rng))
    two = list(batches(23, 5, rng))
    assert [len(index) for index in one] == [5, 5, 5, 5, 3]
    assert sorted(np.concatenate(one).tolist()) == list(range(23))
    assert not np.array_equal(np.concatenate(one), np.concatenate(two))
    assert [len(index) for index in batches(8, 4, rng)] == [4, 4]
''',
)
write("exercises/fill-batches/wrong/never-shuffles.py", FILL_WRONG)
write(
    "exercises/fill-batches/wrong/typed-in.py",
    "def batches(n, batch_size, rng):\n    return []\n\n\n" + "".join(f"print({line!r})\n" for line in FILL_OUT.splitlines()),
)

write(
    "exercises/write-accuracy-and-evaluate/exercise.yaml",
    f'''id: write-accuracy-and-evaluate
stage: write
rev: 1
title: "Accuracy, and evaluating without training"
prompt: |
  Write `accuracy(logits, labels)`, the share of rows (as a float) whose largest logit is the true class, and `evaluate(net, loss, X, y)`, which runs the network forward on the whole set, and returns the tuple `(loss.forward(logits, y), accuracy(logits, y))` with no training step. The starter gives a stand-in network that returns fixed logits and a stand-in loss, so the program prints:

  ```
{block(WRITE_OUT)}  ```
hints:
  - "The largest logit per row is `argmax(axis=1)`: one class index per row; `axis=0` would pick a row per class, which is the classic bug."
  - "Evaluation is forward and loss only; nothing calls backward or an optimizer."
skills: [validation]
''',
)
write("exercises/write-accuracy-and-evaluate/starter.py", WRITE_SOLUTION.split("def accuracy")[0] + "class Constant" + WRITE_SOLUTION.split("class Constant", 1)[1])
write("exercises/write-accuracy-and-evaluate/solution.py", WRITE_SOLUTION)
write(
    "exercises/write-accuracy-and-evaluate/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints the accuracy and the evaluation tuple."""
    printed = run()
    assert printed == {WRITE_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_other_logits():
    """Accuracy is a fraction of rows, not a count; a perfect and an all-wrong set give 1 and 0; evaluate returns the loss first."""
    accuracy = function("accuracy")
    evaluate = function("evaluate")
    logits = np.array([[0.1, 0.9], [0.8, 0.2], [0.3, 0.7], [0.6, 0.4], [0.5, 0.5001]])
    assert accuracy(logits, np.array([1, 0, 1, 0, 1])) == 1.0 and accuracy(logits, np.array([0, 1, 0, 1, 0])) == 0.0
    assert accuracy(logits, np.array([1, 0, 0, 0, 0])) == 0.6

    class Net:
        def forward(self, X):
            return logits

    class Loss:
        def forward(self, logits, labels):
            return 0.25

    assert evaluate(Net(), Loss(), np.zeros((5, 1)), np.array([1, 0, 1, 0, 1])) == (0.25, 1.0)
''',
)
write("exercises/write-accuracy-and-evaluate/wrong/wrong-axis.py", WRITE_WRONG_AXIS)
write("exercises/write-accuracy-and-evaluate/wrong/counts-not-fraction.py", WRITE_COUNTS)
write(
    "exercises/write-accuracy-and-evaluate/wrong/typed-in.py",
    "def accuracy(logits, labels):\n    return 0.5\n\n\ndef evaluate(net, loss, X, y):\n    return (0.5, 0.5)\n\n\n" + "".join(f"print({line!r})\n" for line in WRITE_OUT.splitlines()),
)

# --- the proof -----------------------------------------------------------------------------------

write(
    "exercises/build-fit/exercise.yaml",
    f'''id: build-fit
stage: build
rev: 1
title: "fit"
prompt: |
  Starting from a blank editor, paste the module's classes as they stand (`Dense` with its `scale`, `ReLU`, `Sequential`, `SoftmaxCrossEntropy`, `SGD` and `Adam` from the worked example), then write the loop:

  - `make_blobs(n_per_class=100, seed=0)`: 100 points around each of the centres `(0, 0)`, `(3, 3)` and `(-3, 3)` plus standard-normal noise from `np.random.default_rng(seed)`, drawn centre by centre, with labels 0, 1, 2; returns `(X, y)`.
  - `split(X, y, train_fraction=0.8, seed=0)`: one seeded permutation, cut at `int(train_fraction * n)`; returns `(X_train, y_train, X_val, y_val)`.
  - `batches(n, batch_size, rng)`: yields index arrays covering `0..n-1` once in a fresh random order, `batch_size` at a time, the last short.
  - `accuracy(logits, labels)`: the share of rows whose largest logit sits at the label; `evaluate(net, loss, X, y)`: a forward pass and the loss, returning `(loss, accuracy)`, with no update.
  - `fit(net, loss, optimizer, X_train, y_train, X_val, y_val, epochs, batch_size, seed=0)`: for each epoch, for each batch from `batches` (one generator for the whole run, seeded), one step: forward, loss, backward, `optimizer.step(net.parameters(), net.gradients())`; after each epoch, append the training loss, the validation loss and the validation accuracy to a history dictionary with those three keys (`train_loss`, `val_loss`, `val_accuracy`); return the history.
  - `read_curve(losses)`: `"diverging"` if the last loss is not finite or more than 1.5 times the first, `"stalled"` if it fell by less than a tenth, else `"converging"`.

  Then print:

  ```python
  X, y = make_blobs()
  X_train, y_train, X_val, y_val = split(X, y)
  net = Sequential([Dense(2, 16, seed=0, scale=np.sqrt(2 / 2)), ReLU(), Dense(16, 3, seed=1)])
  loss = SoftmaxCrossEntropy()
  history = fit(net, loss, SGD(0.05), X_train, y_train, X_val, y_val, epochs=30, batch_size=32)
  print(len(X_train), len(X_val), [len(history[key]) for key in ("train_loss", "val_loss", "val_accuracy")])
  print(round(history["train_loss"][0], 3), round(history["train_loss"][-1], 3), round(history["val_accuracy"][-1], 2), read_curve(history["train_loss"]))
  print([len(index) for index in batches(10, 4, np.random.default_rng(0))], accuracy(np.array([[2.0, 1.0], [0.0, 1.0], [3.0, 1.0]]), np.array([0, 1, 1])))
  ```

  ```
{block(BUILD_OUT)}  ```

  The checks cover every index once per epoch with a different order the next epoch, keep the split disjoint and complete, evaluate without changing the weights, hold the trained network to at least 85 percent validation accuracy, confirm that a run with a different seed differs and one with the same seed repeats, and read three hand-made curves.
skills: [loop, validation, curves, batch]
''',
)
write("exercises/build-fit/starter.py", "")
write("exercises/build-fit/solution.py", BUILD_SOLUTION)
write(
    "exercises/build-fit/test_exercise.py",
    f'''import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints the three lines."""
    assert run() == {BUILD_OUT!r}


def test_batches_and_split():
    """Batches cover every index once and reshuffle between epochs; the split is disjoint, complete and seeded."""
    batches = function("batches")
    split = function("split")
    make_blobs = function("make_blobs")
    rng = np.random.default_rng(2)
    one, two = list(batches(23, 5, rng)), list(batches(23, 5, rng))
    assert [len(index) for index in one] == [5, 5, 5, 5, 3] and sorted(np.concatenate(one).tolist()) == list(range(23))
    assert not np.array_equal(np.concatenate(one), np.concatenate(two))
    X, y = make_blobs(50, seed=3)
    assert X.shape == (150, 2) and np.bincount(y).tolist() == [50, 50, 50]
    X_train, y_train, X_val, y_val = split(X, y, seed=4)
    assert len(X_train) == 120 and len(X_val) == 30
    rows = {{tuple(row) for row in X_train}} | {{tuple(row) for row in X_val}}
    assert len(rows) == 150 and not ({{tuple(row) for row in X_train}} & {{tuple(row) for row in X_val}})
    again = split(X, y, seed=4)
    assert np.array_equal(again[0], X_train) and not np.array_equal(split(X, y, seed=5)[0], X_train)


def test_evaluate_does_not_train():
    """evaluate returns the loss and the accuracy and leaves every weight exactly as it was."""
    Dense = function("Dense")
    ReLU = function("ReLU")
    Sequential = function("Sequential")
    SoftmaxCrossEntropy = function("SoftmaxCrossEntropy")
    evaluate = function("evaluate")
    make_blobs = function("make_blobs")
    X, y = make_blobs(20, seed=1)
    net = Sequential([Dense(2, 8, seed=1), ReLU(), Dense(8, 3, seed=2)])
    before = [p.copy() for p in net.parameters()]
    value, acc = evaluate(net, SoftmaxCrossEntropy(), X, y)
    assert 0 <= acc <= 1 and value > 0
    assert all(np.array_equal(a, b) for a, b in zip(before, net.parameters()))


def test_fit_learns_and_repeats():
    """fit reaches 85 percent validation accuracy within 30 epochs, repeats exactly with the same seed, and differs with another."""
    Dense = function("Dense")
    ReLU = function("ReLU")
    Sequential = function("Sequential")
    SoftmaxCrossEntropy = function("SoftmaxCrossEntropy")
    SGD = function("SGD")
    fit = function("fit")
    make_blobs = function("make_blobs")
    split = function("split")
    X, y = make_blobs(80, seed=7)
    X_train, y_train, X_val, y_val = split(X, y, seed=7)

    def run_once(seed):
        net = Sequential([Dense(2, 16, seed=3, scale=1.0), ReLU(), Dense(16, 3, seed=4)])
        return fit(net, SoftmaxCrossEntropy(), SGD(0.05), X_train, y_train, X_val, y_val, epochs=30, batch_size=16, seed=seed)

    first = run_once(1)
    assert len(first["train_loss"]) == 30 and first["val_accuracy"][-1] >= 0.85
    assert first["train_loss"][-1] < first["train_loss"][0]
    assert run_once(1)["train_loss"] == first["train_loss"]
    assert run_once(2)["train_loss"] != first["train_loss"]


def test_read_curve():
    """A falling curve converges, a flat one stalls, a rising or NaN one diverges."""
    read_curve = function("read_curve")
    assert read_curve([1.1, 0.8, 0.5, 0.3]) == "converging"
    assert read_curve([1.10, 1.09, 1.09, 1.08]) == "stalled"
    assert read_curve([1.1, 1.3, 2.0, 7.4]) == "diverging" and read_curve([1.1, 2.0, float("nan")]) == "diverging"
''',
)
for key, code in BUILD_WRONGS.items():
    write(f"exercises/build-fit/wrong/{key}.py", code)
write(
    "exercises/build-fit/wrong/typed-in.py",
    "import numpy as np\n\n\ndef make_blobs(n_per_class=100, seed=0):\n    return np.zeros((300, 2)), np.zeros(300, dtype=int)\n\n\ndef split(X, y, train_fraction=0.8, seed=0):\n    return X[:240], y[:240], X[240:], y[240:]\n\n\ndef batches(n, batch_size, rng):\n    return []\n\n\ndef accuracy(logits, labels):\n    return 0.0\n\n\ndef evaluate(net, loss, X, y):\n    return 0.0, 0.0\n\n\ndef fit(*args, **kwargs):\n    return {}\n\n\ndef read_curve(losses):\n    return 'converging'\n\n\n"
    + "".join(f"print({line!r})\n" for line in BUILD_OUT.splitlines()),
)

write(
    "exercises/debug-a-loop-that-does-not-learn/exercise.yaml",
    f'''id: debug-a-loop-that-does-not-learn
stage: debug
rev: 1
title: "A loop that doesn't learn"
prompt: |
  The module's loop on the three blobs for 20 epochs. It should print:

  ```
{block(DEBUG_OUT)}  ```

  It has two bugs. Run it: it crashes inside `accuracy` with a broadcasting error (shapes `(3,)` and `(240,)`), because `accuracy` takes `argmax(axis=0)`, which picks a row for each of the 3 classes instead of a class for each of the 240 rows; the largest logit per row is `argmax(axis=1)`. Fix that, and the program runs, but the training loss climbs and the curve reads diverging, because `SGD.step` **adds** the learning rate times the gradient, stepping uphill; gradient descent subtracts it.
skills: [loop, validation]
''',
)
write("exercises/debug-a-loop-that-does-not-learn/starter.py", DEBUG_STARTER)
write("exercises/debug-a-loop-that-does-not-learn/solution.py", DEBUG_SOLUTION)
write(
    "exercises/debug-a-loop-that-does-not-learn/test_exercise.py",
    f'''import numpy as np

from checks import function, run

EXPECTED = {DEBUG_OUT!r}


def test_the_output():
    """Prints a converging loss and a validation accuracy well above a third."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\\n{{EXPECTED}}\\nYour program printed:\\n{{printed}}"


def test_the_pieces():
    """SGD steps against the gradient by the rate, and accuracy picks the largest logit per row."""
    SGD = function("SGD")
    accuracy = function("accuracy")
    param = np.array([1.0, 2.0])
    SGD(0.5).step([param], [np.array([2.0, -2.0])])
    assert param.tolist() == [0.0, 3.0]
    assert accuracy(np.array([[0.2, 0.8], [0.9, 0.1], [0.4, 0.6]]), np.array([1, 0, 0])) == 2 / 3
''',
)
write("exercises/debug-a-loop-that-does-not-learn/wrong/still-uphill.py", DEBUG_STILL_UPHILL)
write("exercises/debug-a-loop-that-does-not-learn/wrong/still-the-wrong-axis.py", DEBUG_STILL_AXIS)
write(
    "exercises/debug-a-loop-that-does-not-learn/wrong/typed-in.py",
    "import numpy as np\n\n\nclass SGD:\n    def __init__(self, rate):\n        self.rate = rate\n\n    def step(self, params, grads):\n        pass\n\n\ndef accuracy(logits, labels):\n    return 1.0\n\n\n" + "".join(f"print({line!r})\n" for line in DEBUG_OUT.splitlines()),
)

write(
    "exercises/review-batches/exercise.yaml",
    f'''id: review-batches
stage: review_code
rev: 1
title: "Mini-batches, from memory"
prompt: |
  Write `batches(n, batch_size, rng)`: a generator of index arrays that cover `0..n-1` once in a fresh random order from `rng`, `batch_size` at a time, the last batch short if needed. With `rng = np.random.default_rng(3)`, draw two epochs of 23 rows in batches of 5 and print the first epoch's batch sizes with whether it covers every index, then whether the second epoch repeated the first's order:

  ```
{block(REVIEW_CODE_OUT)}  ```
skills: [loop]
''',
)
write("exercises/review-batches/starter.py", "")
write("exercises/review-batches/solution.py", REVIEW_CODE_SOLUTION)
write(
    "exercises/review-batches/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints the sizes, the coverage and False."""
    assert run() == {REVIEW_CODE_OUT!r}


def test_other_sizes():
    """Twelve rows in batches of 4 give three full batches covering every row; two epochs differ."""
    batches = function("batches")
    rng = np.random.default_rng(9)
    one, two = list(batches(12, 4, rng)), list(batches(12, 4, rng))
    assert [len(index) for index in one] == [4, 4, 4] and sorted(np.concatenate(one).tolist()) == list(range(12))
    assert not np.array_equal(np.concatenate(one), np.concatenate(two))
''',
)
write("exercises/review-batches/wrong/never-shuffles.py", REVIEW_CODE_WRONG)
write(
    "exercises/review-batches/wrong/typed-in.py",
    "def batches(n, batch_size, rng):\n    return []\n\n\n" + "".join(f"print({line!r})\n" for line in REVIEW_CODE_OUT.splitlines()),
)

print("ml.nn.training-loop written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
