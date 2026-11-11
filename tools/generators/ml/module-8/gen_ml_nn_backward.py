"""Writes the topic ml.nn.backward-layers (Module 8's second topic). Run from
the repository root under uv (python -m uv run python <this file>), so every
program's expected output is captured from CPython rather than typed in.
Every gradient is checked numerically and printed as a boolean; losses are
printed rounded and the generator checks that a tenth-decimal nudge of a
starting weight leaves every printed line unchanged. Files are written as
bytes with LF endings."""

import pathlib
import subprocess
import sys

ROOT = pathlib.Path("content/topics/ml.nn.backward-layers")


def write(relative: str, text: str) -> None:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


def out(program: str) -> str:
    result = subprocess.run([sys.executable, "-W", "error", "-c", program], capture_output=True, text=True, check=True)
    return result.stdout.replace("\r\n", "\n")


def differs(program: str, expected: str) -> bool:
    """True if the program fails or prints something other than expected: what a known-wrong must do."""
    result = subprocess.run([sys.executable, "-W", "error", "-c", program], capture_output=True, text=True)
    return result.returncode != 0 or result.stdout.replace("\r\n", "\n") != expected


def fails(program: str) -> str:
    result = subprocess.run([sys.executable, "-W", "error", "-c", program], capture_output=True, text=True)
    assert result.returncode != 0, "expected the program to fail"
    return result.stderr


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


# The module's classes, now with backward. Later topics add to them.
LAYERS = '''class Dense:
    """A dense layer that remembers its input, so backward can compute the gradient for W."""

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
        """grad_out is the loss's gradient with respect to this layer's output, one row per example."""
        self.dW = self.X.T @ grad_out
        self.db = grad_out.sum(axis=0)
        return grad_out @ self.W.T

    def parameters(self):
        return [self.W, self.b]

    def gradients(self):
        return [self.dW, self.db]


class ReLU:
    """Remembers which inputs were positive: the gradient passes through there and is zero elsewhere."""

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
    """Forward runs the layers in order; backward runs them in reverse, handing each the gradient from the one after it."""

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


class MSELoss:
    """Mean squared error over every entry; backward is its gradient with respect to the predictions."""

    def forward(self, pred, target):
        self.diff = pred - target
        return float(np.mean(self.diff ** 2))

    def backward(self):
        return 2 * self.diff / self.diff.size


class SoftmaxCrossEntropy:
    """Softmax over each row of logits, then the mean negative log probability of the true class; stable through log-sum-exp."""

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
'''

# --- the worked example ----------------------------------------------------------------------

EXAMPLE_HEAD = "import numpy as np\n\n\n" + LAYERS
EXAMPLE_TAIL = '''

X = np.array([[1.0, 2.0, 0.5], [0.0, 1.0, -1.0], [2.0, -1.0, 0.0], [-1.0, 0.5, 1.5], [0.5, 0.5, 0.5]])
y = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0], [0.0, 0.0], [0.5, 0.5]])
net = Sequential([Dense(3, 4, seed=1), ReLU(), Dense(4, 2, seed=2)])
loss = MSELoss()
value = loss.forward(net.forward(X), y)
grad_in = net.backward(loss.backward())
print("loss", round(value, 4), "| gradient shapes:", [g.shape for g in net.gradients()], "| gradient for the input:", grad_in.shape)
print("every gradient matches its numeric check:", gradient_check(net, loss, X, y) < 1e-6)

first = net.layers[0]
loss.forward(net.forward(X), y)
grad_out = net.layers[1].backward(net.layers[2].backward(loss.backward()))
print("dW[0, 0] is the sum over the batch of input 0 times the gradient at output 0:", bool(np.isclose(first.dW[0, 0], (first.X[:, 0] * grad_out[:, 0]).sum())))
print("a Dense layer does 1 matrix multiply forward and 2 backward:", "X.T @ grad_out ->", first.dW.shape, "and grad_out @ W.T ->", (grad_out @ first.W.T).shape)

logits = np.array([[2.0, 1.0, 0.1], [0.5, 2.5, 0.2]])
labels = np.array([0, 1])
ce = SoftmaxCrossEntropy()
print("softmax cross-entropy:", round(ce.forward(logits, labels), 4), "| probabilities:", np.round(ce.probs, 3).tolist())
print("its gradient is (p - onehot) / n:", np.round(ce.backward(), 3).tolist(), "| numeric check:", bool(np.abs(ce.backward() - numeric_gradient(lambda: ce.forward(logits, labels), logits)).max() < 1e-6))
big = SoftmaxCrossEntropy()
print("logits of 1,000 stay finite:", round(big.forward(np.array([[1000.0, 1001.0]]), np.array([1])), 4))

for step in range(60):
    value = loss.forward(net.forward(X), y)
    net.backward(loss.backward())
    for param, grad in zip(net.parameters(), net.gradients()):
        param -= 0.1 * grad
    if step in (0, 30, 59):
        print("step", step, "loss", round(value, 3))
'''
EXAMPLE = EXAMPLE_HEAD + EXAMPLE_TAIL
EXAMPLE_OUT = out(EXAMPLE)
print("example:\n" + EXAMPLE_OUT)
EX = EXAMPLE_OUT.splitlines()
assert len(EX) == 10, EX
assert EX[0].startswith("loss ") and "gradient shapes: [(3, 4), (4,), (4, 2), (2,)] | gradient for the input: (5, 3)" in EX[0], EX[0]
assert EX[1] == "every gradient matches its numeric check: True", EX[1]
assert EX[2].endswith("True") and EX[3].endswith("(3, 4) and grad_out @ W.T -> (5, 3)"), EX[2:4]
assert EX[4].startswith("softmax cross-entropy: 0.") and EX[5].endswith("numeric check: True"), EX[4:6]
assert EX[6] == "logits of 1,000 stay finite: 0.3133", EX[6]
losses = [float(line.split()[-1]) for line in EX[7:10]]
assert losses[0] > losses[1] > losses[2], losses
NUDGED = EXAMPLE.replace("net = Sequential([Dense(3, 4, seed=1), ReLU(), Dense(4, 2, seed=2)])", "net = Sequential([Dense(3, 4, seed=1), ReLU(), Dense(4, 2, seed=2)])\nnet.layers[0].W[0, 0] += 1e-10")
assert out(NUDGED) == EXAMPLE_OUT, "a tenth-decimal nudge changed a printed line"
EXAMPLE_LINES = EXAMPLE.splitlines()


def ln(text: str, after: int = 0) -> int:
    return next(i + 1 for i, line in enumerate(EXAMPLE_LINES) if i + 1 > after and text in line)


# --- recall programs ----------------------------------------------------------------------------

PREDICT_RELU = '''import numpy as np

X = np.array([[2.0, -1.0, 0.0], [-0.5, 3.0, 1.0]])
mask = X > 0
grad_out = np.array([[1.0, 1.0, 1.0], [0.5, -2.0, 4.0]])
print(mask.astype(int).tolist())
print((grad_out * mask).tolist())
'''
PREDICT_RELU_OUT = out(PREDICT_RELU)
assert PREDICT_RELU_OUT == "[[1, 0, 0], [0, 1, 1]]\n[[1.0, 0.0, 0.0], [0.0, -2.0, 4.0]]\n", PREDICT_RELU_OUT

PREDICT_DENSE_SHAPES = '''import numpy as np

X = np.ones((4, 3))
W = np.ones((3, 2))
grad_out = np.array([[1.0, 0.0], [1.0, 0.0], [0.0, 1.0], [0.0, 1.0]])
dW = X.T @ grad_out
db = grad_out.sum(axis=0)
grad_in = grad_out @ W.T
print(dW.shape, db.shape, grad_in.shape)
print(dW.tolist(), db.tolist(), grad_in[0].tolist())
'''
PREDICT_DENSE_SHAPES_OUT = out(PREDICT_DENSE_SHAPES)
assert PREDICT_DENSE_SHAPES_OUT == "(3, 2) (2,) (4, 3)\n[[2.0, 2.0], [2.0, 2.0], [2.0, 2.0]] [2.0, 2.0] [1.0, 1.0, 1.0]\n", PREDICT_DENSE_SHAPES_OUT

REVIEW_SOFTMAX_GRAD = '''import numpy as np

probs = np.array([[0.7, 0.2, 0.1], [0.1, 0.1, 0.8]])
labels = np.array([0, 2])
grad = probs.copy()
grad[np.arange(2), labels] -= 1
print(np.round(grad / 2, 2).tolist())
print(round(float(-np.log(probs[np.arange(2), labels]).mean()), 4))
'''
REVIEW_SOFTMAX_GRAD_OUT = out(REVIEW_SOFTMAX_GRAD)
assert REVIEW_SOFTMAX_GRAD_OUT == "[[-0.15, 0.1, 0.05], [0.05, 0.05, -0.1]]\n0.2899\n", REVIEW_SOFTMAX_GRAD_OUT

PARSONS_LINES = [
    "import numpy as np",
    "X = np.array([[1.0, 2.0], [0.0, -1.0]])",
    "W1 = np.full((X.shape[1], 3), 0.5)",
    "h = np.maximum(X @ W1, 0.0)",
    "grad_h = np.ones((2, 3)) * (h > 0)",
    "dW1 = X.T @ grad_h",
    "print(dW1.tolist())",
]
PARSONS_OUT = out("\n".join(PARSONS_LINES) + "\n")
assert PARSONS_OUT == "[[1.0, 1.0, 1.0], [2.0, 2.0, 2.0]]\n", PARSONS_OUT

# --- the fill-in --------------------------------------------------------------------------------

FILL_SOLUTION = '''import numpy as np


class Dense:
    """A dense layer that remembers its input, so backward can compute the gradient for W."""

    def __init__(self, W, b):
        self.W = W
        self.b = b

    def forward(self, X):
        self.X = X
        return X @ self.W + self.b

    def backward(self, grad_out):
        self.dW = self.X.T @ grad_out
        self.db = grad_out.sum(axis=0)
        return grad_out @ self.W.T


layer = Dense(np.array([[1.0, -1.0], [0.0, 2.0], [0.5, 0.5]]), np.array([-0.5, 0.0]))
X = np.array([[1.0, 1.0, 1.0], [2.0, 0.0, -2.0]])
layer.forward(X)
grad_in = layer.backward(np.array([[1.0, 0.5], [0.0, 1.0]]))
print(layer.dW.tolist(), layer.db.tolist())
print(grad_in.tolist())
'''
FILL_STARTER = FILL_SOLUTION.replace("        self.dW = self.X.T @ grad_out\n        self.db = grad_out.sum(axis=0)\n        return grad_out @ self.W.T", "        self.dW = ... @ grad_out\n        self.db = grad_out.sum(axis=...)\n        return grad_out @ ...")
FILL_WRONG = FILL_SOLUTION.replace("        self.db = grad_out.sum(axis=0)", "        self.db = grad_out.sum(axis=1)")
FILL_OUT = out(FILL_SOLUTION)
assert FILL_OUT == "[[1.0, 2.5], [1.0, 0.5], [1.0, -1.5]] [1.0, 1.5]\n[[0.5, 1.0, 0.75], [-1.0, 2.0, 0.5]]\n", FILL_OUT
assert differs(FILL_WRONG, FILL_OUT)

# --- the write ----------------------------------------------------------------------------------

WRITE_HEAD = '''import numpy as np


def numeric_gradient(f, param, h=1e-6):
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
'''
WRITE_BODY = '''

class Sigmoid:
    """Squashes to (0, 1); the gradient is out * (1 - out), so the output is what backward needs."""

    def forward(self, X):
        self.out = 1 / (1 + np.exp(-X))
        return self.out

    def backward(self, grad_out):
        return grad_out * self.out * (1 - self.out)


class Tanh:
    """Squashes to (-1, 1); the gradient is 1 - out squared."""

    def forward(self, X):
        self.out = np.tanh(X)
        return self.out

    def backward(self, grad_out):
        return grad_out * (1 - self.out ** 2)
'''
WRITE_TAIL = '''

X = np.array([[0.0, 1.0, -2.0], [0.5, -0.5, 3.0]])
for layer in (Sigmoid(), Tanh()):
    out = layer.forward(X)
    analytic = layer.backward(np.ones_like(X))
    numeric = numeric_gradient(lambda: float(layer.forward(X).sum()), X)
    print(type(layer).__name__, np.round(out[0], 3).tolist(), bool(np.abs(analytic - numeric).max() < 1e-6))
'''
WRITE_SOLUTION = WRITE_HEAD + WRITE_BODY + WRITE_TAIL
WRITE_STARTER = WRITE_HEAD + WRITE_TAIL
WRITE_OUT = out(WRITE_SOLUTION)
assert WRITE_OUT == "Sigmoid [0.5, 0.731, 0.119] True\nTanh [0.0, 0.762, -0.964] True\n", WRITE_OUT
WRITE_SIGMOID_WRONG = WRITE_SOLUTION.replace("        return grad_out * self.out * (1 - self.out)", "        return grad_out * self.out")
WRITE_TANH_WRONG = WRITE_SOLUTION.replace("        return grad_out * (1 - self.out ** 2)", "        return grad_out * (1 - self.out)")
assert differs(WRITE_SIGMOID_WRONG, WRITE_OUT) and differs(WRITE_TANH_WRONG, WRITE_OUT)

# --- the build ----------------------------------------------------------------------------------

BUILD_TAIL = '''

X = np.array([[1.0, 2.0, 0.5], [0.0, 1.0, -1.0], [2.0, -1.0, 0.0], [-1.0, 0.5, 1.5]])
y = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0], [0.0, 0.0]])
net = Sequential([Dense(3, 4, seed=1), ReLU(), Dense(4, 2, seed=2)])
loss = MSELoss()
print(round(loss.forward(net.forward(X), y), 4), net.backward(loss.backward()).shape, [g.shape for g in net.gradients()])
print(gradient_check(net, loss, X, y) < 1e-6)
ce = SoftmaxCrossEntropy()
logits = np.array([[2.0, 1.0, 0.1], [0.5, 2.5, 0.2]])
labels = np.array([0, 1])
print(round(ce.forward(logits, labels), 4), np.round(ce.backward(), 3).tolist())
classifier = Sequential([Dense(3, 5, seed=3), ReLU(), Dense(5, 3, seed=4)])
print(gradient_check(classifier, ce, X, np.array([0, 1, 2, 1])) < 1e-6, round(ce.forward(np.array([[1000.0, 1001.0]]), np.array([1])), 4))
'''
BUILD_SOLUTION = "import numpy as np\n\n\n" + LAYERS + BUILD_TAIL
BUILD_OUT = out(BUILD_SOLUTION)
print("build:\n" + BUILD_OUT)
BUILD_LINES = BUILD_OUT.splitlines()
assert len(BUILD_LINES) == 4 and BUILD_LINES[1] == "True" and BUILD_LINES[3] == "True 0.3133", BUILD_OUT
assert BUILD_LINES[0].endswith("(4, 3) [(3, 4), (4,), (4, 2), (2,)]"), BUILD_OUT
assert out(BUILD_SOLUTION.replace("net = Sequential([Dense(3, 4, seed=1), ReLU(), Dense(4, 2, seed=2)])", "net = Sequential([Dense(3, 4, seed=1), ReLU(), Dense(4, 2, seed=2)])\nnet.layers[0].W[0, 0] += 1e-10")) == BUILD_OUT
BUILD_WRONGS = {
    "dw-not-summed-over-the-batch": BUILD_SOLUTION.replace("        self.dW = self.X.T @ grad_out\n", "        self.dW = (self.X[:1].T @ grad_out[:1]) * len(self.X)\n"),
    "relu-passes-everything": BUILD_SOLUTION.replace("        return grad_out * self.mask\n", "        return grad_out\n"),
    "backward-in-forward-order": BUILD_SOLUTION.replace("        for layer in reversed(self.layers):\n            grad = layer.backward(grad)", "        for layer in self.layers:\n            grad = layer.backward(grad)"),
    "mse-forgets-the-two": BUILD_SOLUTION.replace("        return 2 * self.diff / self.diff.size", "        return self.diff / self.diff.size"),
    "softmax-without-the-shift": BUILD_SOLUTION.replace("        shifted = logits - logits.max(axis=1, keepdims=True)\n", "        shifted = logits\n"),
}
for key, code in BUILD_WRONGS.items():
    assert code != BUILD_SOLUTION and differs(code, BUILD_OUT), key

# --- the debug ----------------------------------------------------------------------------------

DEBUG_SOLUTION = "import numpy as np\n\n\n" + LAYERS + '''

X = np.array([[1.0, 2.0, 0.5], [0.0, 1.0, -1.0], [2.0, -1.0, 0.0]])
y = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
net = Sequential([Dense(3, 4, seed=1), ReLU(), Dense(4, 2, seed=2)])
loss = MSELoss()
print("gradient shapes match the parameters:", [g.shape for g in net.gradients()] == [p.shape for p in net.parameters()] or net.gradients() == [], end=" | ")
worst = gradient_check(net, loss, X, y)
print("worst gap:", "under 1e-6" if worst < 1e-6 else "too big")
'''
BUG_DW = ("        self.dW = self.X.T @ grad_out\n", "        self.dW = grad_out.T @ self.X\n")
BUG_MASK = ("        self.mask = X > 0\n        return X * self.mask", "        self.mask = X >= 0\n        return np.maximum(X, 0.0)")
DEBUG_STARTER = DEBUG_SOLUTION.replace(*BUG_DW).replace("        return grad_out * self.mask\n", "        return grad_out * (grad_out > 0)\n")
DEBUG_STILL_DW = DEBUG_SOLUTION.replace(*BUG_DW)
DEBUG_STILL_MASK = DEBUG_SOLUTION.replace("        return grad_out * self.mask\n", "        return grad_out * (grad_out > 0)\n")
DEBUG_OUT = out(DEBUG_SOLUTION)
print("debug:\n" + DEBUG_OUT)
assert DEBUG_OUT == "gradient shapes match the parameters: True | worst gap: under 1e-6\n", DEBUG_OUT
STARTER_ERROR = fails(DEBUG_STARTER)
assert "operands could not be broadcast" in STARTER_ERROR or "ValueError" in STARTER_ERROR, STARTER_ERROR
assert out(DEBUG_STILL_MASK) == "gradient shapes match the parameters: True | worst gap: too big\n"

REVIEW_CODE_SOLUTION = '''import numpy as np


class ReLU:
    """Remembers where the input was positive; the gradient passes through there and is zero elsewhere."""

    def forward(self, X):
        self.mask = X > 0
        return np.maximum(X, 0.0)

    def backward(self, grad_out):
        return grad_out * self.mask


layer = ReLU()
print(layer.forward(np.array([[2.0, -1.0, 0.0], [-0.5, 3.0, 1.0]])).tolist())
print(layer.backward(np.array([[1.0, 1.0, 1.0], [0.5, -2.0, 4.0]])).tolist())
'''
REVIEW_CODE_OUT = out(REVIEW_CODE_SOLUTION)
assert REVIEW_CODE_OUT == "[[2.0, 0.0, 0.0], [0.0, 3.0, 1.0]]\n[[1.0, 0.0, 0.0], [0.0, -2.0, 4.0]]\n", REVIEW_CODE_OUT
REVIEW_CODE_WRONG = REVIEW_CODE_SOLUTION.replace("        return grad_out * self.mask", "        return grad_out * (grad_out > 0)")
assert differs(REVIEW_CODE_WRONG, REVIEW_CODE_OUT)

# =====================================================================================
# topic.yaml
# =====================================================================================

write(
    "topic.yaml",
    '''id: ml.nn.backward-layers
kind: topic
status: ready
title: "Layers that carry their gradient"
summary: "Each layer keeps what it needs from the forward pass and implements backward, the gradient of the loss with respect to its input and its parameters; loss layers for mean squared error and softmax cross-entropy; a Sequential that runs the chain rule for you; and a gradient check on every piece."
prerequisites: [ml.nn.neurons-and-layers]
packages: [numpy]
estimated_minutes: 60
rev: 1
objectives:
  - "Implement backward for a dense layer and for ReLU, sigmoid and tanh, caching what the forward pass needs."
  - "Implement mean squared error and softmax cross-entropy as loss layers with their gradients."
  - "Chain the layers' backward calls in reverse to get every parameter's gradient, and check each against a numeric derivative."
  - "Say what the chain rule does at each layer boundary and why the backward pass costs about twice the forward."
# Linked, never copied or embedded: 3Blue1Brown's videos are under the
# standard YouTube licence; Nielsen's book is CC BY-NC 3.0; Wikipedia is
# CC BY-SA 4.0.
resources:
  - title: "3Blue1Brown: Neural networks (Grant Sanderson), chapters 3 and 4: What is backpropagation really doing? and Backpropagation calculus"
    url: https://www.3blue1brown.com/lessons/backpropagation
    type: video
    use: link
    license: Standard YouTube licence (linked, not copied)
  - title: "Neural Networks and Deep Learning, chapter 2: How the backpropagation algorithm works (Michael Nielsen), the four fundamental equations and the algorithm"
    url: https://neuralnetworksanddeeplearning.com/chap2.html
    type: reading
    use: link
    license: CC BY-NC 3.0 (linked, not copied)
  - title: "Wikipedia: Backpropagation (the Overview and the Matrix multiplication section)"
    url: https://en.wikipedia.org/wiki/Backpropagation
    type: reading
    use: link
    license: CC BY-SA 4.0 (linked, not copied)
practice:
  - example-backward-through-a-stack
  - predict-relu-backward
  - mcq-what-backward-returns
  - predict-dense-backward-shapes
  - mcq-why-dw-sums-over-the-batch
  - parsons-the-backward-loop
  - mcq-why-cache-the-input
  - mcq-the-softmax-gradient
  - mcq-what-the-check-proves
  - fill-dense-backward
  - write-sigmoid-and-tanh
prove:
  build: build-layers-with-backward
  debug: debug-a-gradient-that-fails-its-check
  explain:
    prompt: |
      A reviewer reads your layers and asks four things. "What does a layer's `backward` take in and give back, and why does `Sequential` call them in reverse?" "Where does `dW = X.T @ grad_out` come from, and why does `forward` have to keep `X`?" "Why is the softmax cross-entropy gradient just `(p - onehot) / n`, when the loss has a log and an exp in it?" "You say the numeric check passes; what does that prove, and what doesn't it prove?" In your own words, answer all four.
    rubric:
      - id: layer-backward
        required: true
        description: "backward takes the loss's gradient with respect to the layer's output (one row per example) and returns the gradient with respect to its input, storing the gradients for its own parameters on the way; that is the chain rule applied at the layer boundary, and the reverse order is because each layer's input gradient is the next-earlier layer's output gradient. dW = X.T @ grad_out because output k of row i is sum_j X[i, j] W[j, k], so the gradient for W[j, k] is X[i, j] times grad_out[i, k], summed over the rows; the layer keeps X because backward needs it."
      - id: loss-layers
        required: true
        description: "The log and the exp cancel in the derivative: the loss is minus the log of the softmax, and the softmax's own derivative with respect to a logit is p times (indicator minus p), so the gradient of the loss per example is p minus the one-hot target, divided by n for the mean. MSE's gradient is 2 (pred - target) over the number of entries."
      - id: chain
        required: true
        description: "Sequential's backward hands each layer the gradient from the layer after it, in reverse, so every parameter's gradient appears without any layer knowing about the others; the numeric check compares each backward gradient with a central difference of the loss, nudging one parameter at a time."
      - id: why
        required: true
        description: "A passing check proves the implementation computes the derivative of the loss the code actually implements, within rounding; it doesn't prove the loss or the architecture is right for the task, or that training will go well. The backward pass costs about twice the forward because a dense layer does one matrix multiply forward and two backward, for the input gradient and for dW."
    model_answer: |
      A layer's `backward` takes the gradient of the loss with respect to the layer's own output, one row per example and one column per output, and gives back the gradient with respect to the layer's input, in the shape of the input; on the way it stores the gradients for its own parameters. That is the chain rule applied at the boundary of the layer: how the loss changes with the input is how it changes with the output times how the output changes with the input. `Sequential` calls the layers in reverse because the gradient a layer needs is the one the layer after it produces; the loss supplies the first, the last layer turns it into the gradient for its input, which is the second-to-last layer's output, and so on back to the data. `dW = X.T @ grad_out` comes from writing out one output: output `k` of row `i` is the sum over `j` of `X[i, j] * W[j, k]` plus `b[k]`, so the derivative of that output with respect to `W[j, k]` is `X[i, j]`, and by the chain rule the loss's gradient for `W[j, k]` is `X[i, j] * grad_out[i, k]`, summed over every row of the batch because every example used the same weight. Written for all `j` and `k` at once that sum is exactly `X.T @ grad_out`, and the bias gradient is the column sums of `grad_out` for the same reason. `forward` has to keep `X` because `backward` runs later and needs it; the layer carries its own memory. The softmax gradient is simple because the log and the exp undo each other. The loss for one example is minus the log of the softmax probability of the true class; the derivative of a log-softmax entry with respect to logit `k` is the indicator that `k` is the true class minus `p[k]`, so the derivative of the loss is `p[k]` minus the indicator, which over the batch is `p - onehot`, and dividing by `n` is the derivative of the mean. The example checks it numerically and the gap is under a millionth. What the numeric check proves is that my `backward` computes the derivative of the loss my code actually computes, to within rounding, nudging one parameter at a time and comparing the slope of the loss with the stored gradient; a wrong transpose, a dropped factor of two or a ReLU mask taken from the wrong array all show up as a gap of order one. What it doesn't prove is that the loss, the architecture or the learning rate are right for the task, that training will converge, or that the gradients are large enough to learn from; the check is about the implementation matching the math, not about the math being a good idea. The cost is about twice the forward pass because a dense layer does one matrix multiply forward and two backward, one for the gradient of its input and one for `dW`, each the same size as the forward one.
review_pool:
  - review-predict-the-softmax-gradient
  - review-mcq-why-reverse
  - review-mcq-twice-the-forward
  - review-relu-with-backward
# What this topic teaches. Each question names the skills it tests, so a
# missed question can come back as a different one on the same skill
# (ADR-0011).
skills:
  - id: layer-backward
    description: "Implement backward for a dense layer and for activation layers, caching what the forward pass needs"
  - id: loss-layers
    description: "Implement mean squared error and softmax cross-entropy as loss layers with their gradients"
  - id: chain
    description: "Chain the layers' backward calls in reverse and check every gradient numerically"
  - id: why
    description: "Say what the chain rule does at a layer boundary, what the numeric check proves, and why backward costs about twice forward"
''',
)

# =====================================================================================
# lesson.mdx
# =====================================================================================

write(
    "lesson.mdx",
    '''<Intro>

Module 4 derived backpropagation for one small network, with every gradient written out by hand. This topic packages it so that it never has to be written out again: each layer gets a `backward` that turns the gradient at its output into the gradient at its input and stores the gradients for its own parameters, a loss becomes a layer with a `backward` of its own, and `Sequential` runs the chain rule by calling the layers in reverse. The price of the convenience is discipline: every `backward` is checked against a numeric derivative before it is trusted, and the topic ends with the first training steps taken by the new machinery.

The main resource is **3Blue1Brown's chapters 3 and 4** on backpropagation, the intuition and then the calculus, about 25 minutes together. Nielsen's chapter 2 states the same thing as four equations and an algorithm, which is what the classes below implement, and Wikipedia's _Backpropagation_ page has the matrix form. Watch for:

- **The gradient at a layer's output** becoming the gradient at its input: the chain rule as a hand-off.
- **Summing over the batch**: why a weight's gradient adds up contributions from every example.
- **The four equations**: error at the output, error passed back, bias gradient, weight gradient.

</Intro>

<Resource index={0} />

<Recap>

- **The contract.** `forward(X)` computes the layer's output and remembers whatever `backward` will need. `backward(grad_out)` takes the loss's gradient with respect to the layer's output (one row per example, one column per output), stores the gradients for the layer's own parameters, and returns the gradient with respect to the layer's input, in the input's shape. `parameters()` and `gradients()` line up one to one, which is all an optimizer needs.
- **Dense.** Output `k` of row `i` is `sum_j X[i, j] * W[j, k] + b[k]`. So `dW = X.T @ grad_out` (each weight's gradient is its input times the gradient at its output, **summed over the batch**, because every example used the same weight), `db = grad_out.sum(axis=0)`, and the gradient for the input is `grad_out @ W.T`. The layer keeps `X` in `forward` because `backward` needs it. One matrix multiply forward, two backward: that is why **backward costs about twice the forward**.
- **Activations.** ReLU keeps the mask `X > 0` and returns `grad_out * mask`: the gradient passes where the unit was active and is zero where it wasn't. Sigmoid keeps its output and returns `grad_out * out * (1 - out)`; tanh (`np.tanh`, an S-curve from -1 to 1: a sigmoid centred on zero) returns `grad_out * (1 - out ** 2)`, since its slope is `1 - tanh(x) ** 2`. ReLU's and the sigmoid's derivatives are Module 4's; each is applied elementwise to the incoming gradient.
- **Loss layers.** `MSELoss.forward(pred, target)` is the mean of the squared differences over every entry; its `backward()` is `2 * (pred - target) / size`. `SoftmaxCrossEntropy.forward(logits, labels)` computes log-softmax through the shift and log-sum-exp from Floating point, so logits of 1,000 stay finite, and returns the mean negative log probability of the true class; its `backward()` is `(p - onehot) / n`: the log and the exp cancel in the derivative, which is why the gradient is so simple.
- **Sequential.** `backward(grad)` calls each layer's `backward` **in reverse**, feeding each the gradient the layer after it returned, so every parameter's gradient appears without any layer knowing about the others; `gradients()` gathers them in the same order as `parameters()`. The loss layer's `backward()` supplies the first gradient.
- **The gradient check** nudges one parameter entry at a time by `h = 1e-6`, up and down, recomputes the loss, and compares `(up - down) / 2h` with the stored gradient; over a whole network the worst gap should be under about `1e-6` in float64. It proves that `backward` computes the derivative of the loss the code actually implements. It doesn't prove that the loss or the architecture is right for the task, that training will work, or that the gradients are big enough to learn from. Run it once per new layer and whenever a loss curve looks wrong (When training goes wrong).
- **A training step** with the new pieces: `loss.forward(net.forward(X), y)`, `net.backward(loss.backward())`, then `param -= rate * grad` for each parameter and gradient pair. Sixty such steps on the example's five rows bring the loss down steadily; The training loop makes this a function with batches, epochs and a validation set.
- **In machine learning** (names you'll meet later): `loss.backward()` in PyTorch does what `Sequential.backward` does here, by recording the forward pass as a graph (**autograd**) instead of asking each layer; `.grad` on a parameter is `dW`; `torch.autograd.gradcheck` is the numeric check; and the reason frameworks default to float32 but check gradients in float64 is the rounding this topic's `h` has to live with.

</Recap>
''',
)

# =====================================================================================
# recall
# =====================================================================================

write(
    "recall/predict-relu-backward.yaml",
    f'''id: predict-relu-backward
type: predict_output
rev: 1
prompt: |
  A ReLU's mask on a two-row input, and the gradient it passes back. What does the program print?
code: |
{block(PREDICT_RELU)}expected_output: |
{block(PREDICT_RELU_OUT)}explanation: |
  The mask is 1 where the input was positive and 0 where it was zero or negative; an input of exactly 0 is on the flat side, so its gradient is 0. The gradient coming back is kept where the mask is 1 and dropped where it is 0, whatever its sign or size.
skills: [layer-backward]
''',
)

mcq(
    "mcq-what-backward-returns",
    "A layer's `backward(grad_out)` is called with the loss's gradient with respect to the layer's output. What does it return, and what does it store?",
    [
        "It returns the updated weights and stores the learning rate",
        "It returns the loss value for this layer and stores the gradient with respect to the output, for the optimizer to read later",
        "It returns `grad_out` unchanged and stores a copy; only the loss layer computes gradients",
        "The gradient with respect to the layer's input, in the input's shape; it stores its own parameters' gradients",
    ],
    3,
    "The chain rule at a layer boundary: how the loss changes with the input is how it changes with the output times how the output changes with the input. The layer computes that and hands it to the layer before it, which is why Sequential calls backward in reverse; its own parameter gradients it keeps for the optimizer. Layers never see the learning rate or update themselves, and no layer but the loss has a loss value.",
    ["layer-backward"],
)

write(
    "recall/predict-dense-backward-shapes.yaml",
    f'''id: predict-dense-backward-shapes
type: predict_output
rev: 1
prompt: |
  A dense layer's three backward products on a batch of four rows of ones, with weights of ones and a gradient that is a one-hot per row. What does the program print?
code: |
{block(PREDICT_DENSE_SHAPES)}expected_output: |
{block(PREDICT_DENSE_SHAPES_OUT)}explanation: |
  `X.T @ grad_out` is `(3, 4) @ (4, 2)`, the shape of `W`: each entry sums input times gradient over the four rows, and with inputs of 1 and two rows pointing at each output, every entry is 2. `db` sums the gradient down the rows, 2 per output. `grad_out @ W.T` is `(4, 2) @ (2, 3)`, the shape of `X`: the first row's single 1 picks up the first column of `W` transposed, all ones.
skills: [layer-backward]
''',
)

mcq(
    "mcq-why-dw-sums-over-the-batch",
    "Why is a dense layer's weight gradient `X.T @ grad_out`, a sum over the rows of the batch, rather than one gradient per example?",
    [
        "Because every example used the same `W`: the loss's dependence on `W[j, k]` is the sum over examples of input `j` times the gradient at output `k`",
        "Because NumPy can only multiply matrices, so the per-example gradients get summed by accident",
        "Because the gradient of the first example is all that matters; the others are averaged out by the learning rate over many steps, so summing them changes nothing",
        "Because `X.T @ grad_out` is cheaper to compute than the per-example gradients",
    ],
    0,
    "Output `k` of row `i` is `sum_j X[i, j] * W[j, k] + b[k]`, so the derivative of that output with respect to `W[j, k]` is `X[i, j]`, and the loss's gradient for `W[j, k]` is `X[i, j] * grad_out[i, k]` summed over `i`, since the same weight touched every row. `X.T @ grad_out` computes exactly that for every `j` and `k`. Averaging over the batch is already inside `grad_out` when the loss is a mean.",
    ["layer-backward"],
)

write(
    "recall/parsons-the-backward-loop.yaml",
    "id: parsons-the-backward-loop\ntype: parsons\nrev: 1\nprompt: |\n"
    + block("Put the lines in order to push a gradient of ones back through a ReLU and into a dense layer's weight gradient, in plain arrays, and print `[[1.0, 1.0, 1.0], [2.0, 2.0, 2.0]]`. One line is a decoy that doesn't belong.")
    + "lines:\n"
    + "".join(f"  - {quoted(line)}\n" for line in PARSONS_LINES)
    + "distractors:\n  - "
    + quoted("grad_h = np.ones((2, 3))")
    + "\nexplanation: |\n"
    + block("The forward pass comes first, because the ReLU's mask comes from it: the second row's sums are negative, so the mask zeroes that row's gradient. The chain then runs backwards: the gradient at the ReLU's output passes through the mask to become the gradient at the dense layer's output, and `X.T @ grad_h` turns it into the weight gradient, where the first row alone contributes 1 for the first input and 2 for the second. The decoy skips the mask, so the second row's gradient leaks through and its input of -1 pulls the second entries down to 1.")
    + "skills: [chain]\n",
)

mcq(
    "mcq-why-cache-the-input",
    "Why does `Dense.forward` store `self.X = X` before returning `X @ self.W + self.b`?",
    [
        "So that `forward` can be called again without passing `X`, which saves copying the batch on every call",
        "So that `backward` can rerun the forward pass whenever the gradient check asks for the loss again",
        "Because `backward` runs later and needs `X` for `dW = X.T @ grad_out`",
        "To check in `backward` that the batch hasn't changed",
    ],
    2,
    "The weight gradient is input times output gradient summed over the batch, so backward can't be computed without the input that forward saw. Every layer that needs something from its forward pass keeps it: Dense keeps X, ReLU keeps its mask, Sigmoid keeps its output. The memory those caches take, for every layer and every example in the batch, is the activation memory Counting a model's cost measured.",
    ["layer-backward"],
)

mcq(
    "mcq-the-softmax-gradient",
    "The softmax cross-entropy loss has a log and an exp in it, yet its gradient with respect to the logits is `(p - onehot) / n`. Why so simple?",
    [
        "Because the loss is approximated by its first-order Taylor expansion around the current logits, which drops the log and the exp and leaves a linear term",
        "Because NumPy simplifies the expression symbolically before computing it",
        "Because the log and the exp cancel in the derivative: d(log-softmax_k)/d(logit_j) is `(j == k) - p[j]`, so each example's gradient is `p - onehot`",
        "Because the gradient is defined that way by convention, and the loss is chosen to match",
    ],
    2,
    "Write the loss for one example as `log(sum(exp(logits))) - logits[label]`; the derivative of the first term with respect to logit `j` is `exp(logits[j]) / sum(exp(logits))`, which is `p[j]`, and the second term contributes `-1` at the true class. No approximation, no symbolic algebra: the exponential's derivative is itself and the log's derivative divides it away. The numeric check in the worked example confirms it to a millionth.",
    ["loss-layers"],
)

mcq(
    "mcq-what-the-check-proves",
    "Your network passes the gradient check with a worst gap of 3e-9. What has been shown, and what hasn't?",
    [
        "That the network will train well on this data, since its gradients are exact",
        "That `backward` computes the derivative of the loss the code implements, to within rounding; not that the loss or the architecture suit the task",
        "That the loss function is the right one for the task, since its gradient agrees with the numeric slope",
        "Nothing, since the numeric check has its own rounding error of about the same size as the gap it reports, so it can't tell a right gradient from a wrong one unless the gap is exactly zero",
    ],
    1,
    "The check compares backward with a brute-force slope of the same loss function, so a tiny gap means the two agree: the implementation matches the math. It says nothing about whether that math is a good idea; a wrong loss, a network too small for the task, or a learning rate that diverges all pass the check. The numeric slope's own rounding error is around 1e-10 to 1e-8 in float64 with h = 1e-6, far below the gaps a bug makes, which are of order 1.",
    ["why"],
)

write(
    "recall/review-predict-the-softmax-gradient.yaml",
    f'''id: review-predict-the-softmax-gradient
type: predict_output
rev: 1
prompt: |
  Two rows of softmax probabilities with their true classes: the gradient of the mean cross-entropy with respect to the logits, and the loss itself. What does the program print?
code: |
{block(REVIEW_SOFTMAX_GRAD)}expected_output: |
{block(REVIEW_SOFTMAX_GRAD_OUT)}explanation: |
  The gradient per example is the probabilities with 1 subtracted at the true class, so the true class gets a negative entry (push its logit up) and the others positive ones (push them down), then divided by the two examples. The loss is the mean of minus the log of the true-class probabilities, 0.7 and 0.8.
skills: [loss-layers]
''',
)

mcq(
    "review-mcq-why-reverse",
    "Why does `Sequential.backward` loop over the layers in reverse?",
    [
        "Because the last layer's parameters are the most important and should be updated first, before the earlier layers see the gradient",
        "Because reversing the list makes the matrix multiplies cheaper",
        "It doesn't have to; forward order works too, as long as every layer is visited",
        "Because each layer's backward needs the gradient at its output, which the layer after it returns; the loss supplies the first",
    ],
    3,
    "The chain rule hands gradients backwards: the gradient at a layer's output is the gradient at the next layer's input, which that next layer computes. Starting from the loss and walking to the data is the only order in which every layer has what it needs when its turn comes. Forward order would give the first layer a gradient shaped for the last and fail. Nothing is updated during backward; that is the optimizer's job afterwards.",
    ["chain"],
)

mcq(
    "review-mcq-twice-the-forward",
    "Why does the backward pass cost about twice the forward pass?",
    [
        "Because backward runs in Python and forward in NumPy",
        "Because a dense layer does one matrix multiply forward and two backward, for the input gradient and for `dW`, each the size of the forward one",
        "Because backward has to repeat the forward pass before it can start, since the activations were not kept, so it does the forward work again and then its own",
        "Because the gradients are computed in float64 and the forward pass in float32",
    ],
    1,
    "Forward is `X @ W`; backward is `grad_out @ W.T` for the input gradient and `X.T @ grad_out` for the weight gradient, the same shapes of multiply twice over. Nothing is recomputed, since each layer cached what it needs, and the precision is the same. This is the 2 and 4 FLOPs per parameter that Counting a model's cost added up to 6 per training step.",
    ["why"],
)

# =====================================================================================
# exercises
# =====================================================================================

write(
    "exercises/example-backward-through-a-stack/exercise.yaml",
    f'''id: example-backward-through-a-stack
stage: worked_example
rev: 1
title: "Backward through a stack"
prompt: |
  The module's classes with `backward` added, a loss layer for mean squared error and one for softmax cross-entropy, a numeric gradient check over every parameter, the formula behind `dW` confirmed on one entry, and sixty training steps taken with the new pieces. Press **Run**, then read how each part works.
steps:
  - label: "Dense, with a memory"
    lines: "{ln('class Dense:')}-{ln('return [self.dW, self.db]')}"
    note: "`forward` keeps `X`. `backward` takes the loss's gradient with respect to the output, `grad_out`, and computes three things from the chain rule: `dW = X.T @ grad_out` (each weight's input times the gradient at its output, summed over the batch), `db = grad_out.sum(axis=0)`, and the gradient to hand to the layer before, `grad_out @ W.T`. `gradients()` lines up with `parameters()`."
  - label: "ReLU, and the backward chain"
    lines: "{ln('class ReLU:')}-{ln('return [g for layer in self.layers')}"
    note: "ReLU keeps the mask of where the input was positive and lets the gradient through only there. `Sequential.backward` walks the layers in reverse, feeding each the gradient the layer after it returned, so every parameter's gradient appears without any layer knowing about the others."
  - label: "Two losses as layers"
    lines: "{ln('class MSELoss:')}-{ln('return grad / len(self.labels)')}"
    note: "Mean squared error's backward is `2 * (pred - target) / size`. Softmax cross-entropy shifts the logits and uses log-sum-exp (Floating point), so a logit of 1,000 stays finite; its backward is `(p - onehot) / n`, because the log and the exp cancel in the derivative."
  - label: "The gradient check"
    lines: "{ln('def numeric_gradient')}-{ln('return worst')}"
    note: "`numeric_gradient` nudges one parameter entry at a time by a millionth, up and down, and takes the slope of the loss; `gradient_check` does it for every parameter of a network and reports the worst gap against the stored gradient. In float64 a correct backward lands under about 1e-6; a dropped mask or a missing factor of two lands far above that, and a wrong transpose usually crashes with a shape error before any gap is measured."
  - label: "A stack checked, and dW explained on one entry"
    lines: "{ln('X = np.array([[1.0, 2.0, 0.5]')}-{ln('a Dense layer does 1 matrix multiply forward')}"
    note: "On five rows, the loss, the gradient shapes (one per parameter, matching) and the gradient for the input itself; the check passes for every parameter. `dW[0, 0]` is confirmed as the sum over the batch of input 0 times the gradient at output 0, which is what `X.T @ grad_out` computes for every entry at once; the two backward multiplies are the same size as the forward one, which is why backward costs about twice forward."
  - label: "Softmax cross-entropy, checked"
    lines: "{ln('logits = np.array([[2.0, 1.0, 0.1]')}-{ln('logits of 1,000 stay finite')}"
    note: "Two rows of three logits: the probabilities, the loss, and the gradient `(p - onehot) / 2`, negative at each true class and positive elsewhere, confirmed against the numeric derivative. A row with logits of 1,000 and 1,001 gives the same loss as 0 and 1 would, 0.3133, instead of NaN."
  - label: "Sixty steps with the new pieces"
    lines: "{ln('for step in range(60):')}-{ln('round(value, 3)')}"
    note: "Forward, loss, backward, then `param -= 0.1 * grad` for every parameter and gradient pair: the loss falls steadily. The training loop topic turns these lines into a function with batches, epochs and a validation set."
''',
)
write("exercises/example-backward-through-a-stack/solution.py", EXAMPLE)
write(
    "exercises/example-backward-through-a-stack/test_exercise.py",
    f'''from checks import run


def test_the_walkthrough():
    """Prints the shapes, the passing checks, the softmax numbers and a falling loss."""
    assert run() == {EXAMPLE_OUT!r}
''',
)

write(
    "exercises/fill-dense-backward/exercise.yaml",
    f'''id: fill-dense-backward
stage: fill_in
rev: 1
title: "A dense layer's backward pass"
prompt: |
  `backward(grad_out)` receives the loss's gradient with respect to the layer's output, one row per example. Replace each `...` so it stores the weight gradient (each weight's input times the gradient at its output, summed over the batch), the bias gradient (the gradient summed down the rows), and returns the gradient for the layer's input, so that the program prints:

  ```
{block(FILL_OUT)}  ```

  The program fails until every `...` is replaced.
hints:
  - "The weight gradient has the shape of `W`, `(inputs, outputs)`: the transposed input, `(inputs, rows)`, times the gradient, `(rows, outputs)`."
  - "The input gradient has the shape of `X`: the gradient, `(rows, outputs)`, times the transposed weights, `(outputs, inputs)`."
skills: [layer-backward]
''',
)
write("exercises/fill-dense-backward/starter.py", FILL_STARTER)
write("exercises/fill-dense-backward/solution.py", FILL_SOLUTION)
write(
    "exercises/fill-dense-backward/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def central(f, param, h=1e-6):
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


def test_the_output():
    """Prints the weight and bias gradients, then the input gradient."""
    printed = run()
    assert printed == {FILL_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_against_numeric_gradients():
    """On other weights and a loss that sums the squared outputs, every stored gradient matches a numeric one."""
    Dense = function("Dense")
    layer = Dense(np.array([[0.3, -0.7, 1.1], [0.9, 0.2, -0.4]]), np.array([0.1, -0.2, 0.3]))
    X = np.array([[1.0, -1.0], [2.0, 0.5], [-0.5, 1.5]])

    def total():
        return float((layer.forward(X) ** 2).sum())

    total()
    grad_in = layer.backward(2 * layer.forward(X))
    assert np.allclose(layer.dW, central(total, layer.W), atol=1e-6)
    assert np.allclose(layer.db, central(total, layer.b), atol=1e-6)
    assert np.allclose(grad_in, central(total, X), atol=1e-6)
''',
)
write("exercises/fill-dense-backward/wrong/bias-summed-along-rows.py", FILL_WRONG)
write(
    "exercises/fill-dense-backward/wrong/typed-in.py",
    "import numpy as np\n\n\nclass Dense:\n    def __init__(self, W, b):\n        self.W = W\n        self.b = b\n        self.dW = W\n        self.db = b\n\n    def forward(self, X):\n        return X\n\n    def backward(self, grad_out):\n        return grad_out\n\n\n" + "".join(f"print({line!r})\n" for line in FILL_OUT.splitlines()),
)

write(
    "exercises/write-sigmoid-and-tanh/exercise.yaml",
    f'''id: write-sigmoid-and-tanh
stage: write
rev: 1
title: "Sigmoid and tanh, with backward"
prompt: |
  Write two activation layers with the module's contract. `Sigmoid.forward(X)` returns `1 / (1 + exp(-X))` and keeps the output; its `backward(grad_out)` returns `grad_out * out * (1 - out)`. `Tanh.forward(X)` returns `np.tanh(X)` and keeps the output; its `backward(grad_out)` returns `grad_out * (1 - out ** 2)`. The starter gives `numeric_gradient`; the program checks each layer's backward against it and prints:

  ```
{block(WRITE_OUT)}  ```
hints:
  - "Both derivatives are written in terms of the output, which is why forward keeps `self.out` rather than the input."
  - "The check sums the forward output, so the gradient coming back is all ones; your backward multiplies it by the derivative elementwise."
skills: [layer-backward]
''',
)
write("exercises/write-sigmoid-and-tanh/starter.py", WRITE_STARTER)
write("exercises/write-sigmoid-and-tanh/solution.py", WRITE_SOLUTION)
write(
    "exercises/write-sigmoid-and-tanh/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints each layer's first row and a passing check."""
    printed = run()
    assert printed == {WRITE_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_values_and_gradients():
    """Sigmoid of 0 is 0.5 with slope 0.25; tanh of 0 is 0 with slope 1; both backward passes scale an arbitrary gradient."""
    Sigmoid = function("Sigmoid")
    Tanh = function("Tanh")
    X = np.array([[0.0, 2.0], [-3.0, 0.5]])
    s, t = Sigmoid(), Tanh()
    assert np.allclose(s.forward(X)[0, 0], 0.5) and np.allclose(t.forward(X)[0, 0], 0.0)
    g = np.array([[2.0, -1.0], [0.5, 4.0]])
    assert np.allclose(s.backward(g)[0, 0], 0.5) and np.allclose(t.backward(g)[0, 0], 2.0)
    out = s.forward(X)
    assert np.allclose(s.backward(g), g * out * (1 - out))
    out = t.forward(X)
    assert np.allclose(t.backward(g), g * (1 - out ** 2))
''',
)
write("exercises/write-sigmoid-and-tanh/wrong/sigmoid-missing-a-factor.py", WRITE_SIGMOID_WRONG)
write("exercises/write-sigmoid-and-tanh/wrong/tanh-not-squared.py", WRITE_TANH_WRONG)
write(
    "exercises/write-sigmoid-and-tanh/wrong/typed-in.py",
    WRITE_HEAD + "\n\nclass Sigmoid:\n    def forward(self, X):\n        return X\n\n    def backward(self, grad_out):\n        return grad_out\n\n\nclass Tanh(Sigmoid):\n    pass\n\n\n" + "".join(f"print({line!r})\n" for line in WRITE_OUT.splitlines()),
)

# --- the proof -----------------------------------------------------------------------------------

write(
    "exercises/build-layers-with-backward/exercise.yaml",
    f'''id: build-layers-with-backward
stage: build
rev: 1
title: "Layers with backward"
prompt: |
  Starting from a blank editor, write the module's classes with their backward passes and the gradient check:

  - `Dense(n_in, n_out, seed=0)`: `W` of shape `(n_in, n_out)` from `np.random.default_rng(seed).standard_normal` divided by `sqrt(n_in)`, `b` of zeros; `forward(X)` keeps `X` and returns `X @ W + b`; `backward(grad_out)` stores `dW = X.T @ grad_out` and `db = grad_out.sum(axis=0)` and returns `grad_out @ W.T`; `parameters()` is `[W, b]` and `gradients()` is `[dW, db]`.
  - `ReLU()`: `forward` keeps the mask `X > 0` and returns `np.maximum(X, 0.0)`; `backward(grad_out)` returns `grad_out * mask`; `parameters()` and `gradients()` are empty.
  - `Sequential(layers)`: `forward` runs the layers in order; `backward(grad)` runs their `backward` in reverse and returns the gradient for the input; `parameters()` and `gradients()` gather the layers' lists in order.
  - `MSELoss()`: `forward(pred, target)` returns the mean of the squared differences over every entry and keeps the differences; `backward()` returns `2 * diff / diff.size`.
  - `SoftmaxCrossEntropy()`: `forward(logits, labels)` shifts each row by its maximum, computes log-softmax with log-sum-exp, keeps the probabilities, and returns the mean negative log probability of the true class (labels are integer class indices); `backward()` returns the probabilities with 1 subtracted at each true class, divided by the number of rows.
  - `numeric_gradient(f, param, h=1e-6)`: the central-difference gradient of `f()` with respect to every entry of `param`, which `f` reads (nudge, call, restore).
  - `gradient_check(net, loss, X, y)`: run forward and backward, then return the largest gap between any parameter's stored gradient and its numeric one.

  Then print:

  ```python
  X = np.array([[1.0, 2.0, 0.5], [0.0, 1.0, -1.0], [2.0, -1.0, 0.0], [-1.0, 0.5, 1.5]])
  y = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0], [0.0, 0.0]])
  net = Sequential([Dense(3, 4, seed=1), ReLU(), Dense(4, 2, seed=2)])
  loss = MSELoss()
  print(round(loss.forward(net.forward(X), y), 4), net.backward(loss.backward()).shape, [g.shape for g in net.gradients()])
  print(gradient_check(net, loss, X, y) < 1e-6)
  ce = SoftmaxCrossEntropy()
  logits = np.array([[2.0, 1.0, 0.1], [0.5, 2.5, 0.2]])
  labels = np.array([0, 1])
  print(round(ce.forward(logits, labels), 4), np.round(ce.backward(), 3).tolist())
  classifier = Sequential([Dense(3, 5, seed=3), ReLU(), Dense(5, 3, seed=4)])
  print(gradient_check(classifier, ce, X, np.array([0, 1, 2, 1])) < 1e-6, round(ce.forward(np.array([[1000.0, 1001.0]]), np.array([1])), 4))
  ```

  ```
{block(BUILD_OUT)}  ```

  The checks compare every layer's backward with numeric gradients on other data, compare `Sequential.backward` with the layers called by hand in reverse, test both losses against their formulas and the softmax on logits of 5,000, and hand `gradient_check` a network with a deliberately wrong backward to see that it reports a large gap.
skills: [layer-backward, loss-layers, chain, why]
''',
)
write("exercises/build-layers-with-backward/starter.py", "")
write("exercises/build-layers-with-backward/solution.py", BUILD_SOLUTION)
write(
    "exercises/build-layers-with-backward/test_exercise.py",
    f'''import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def central(f, param, h=1e-6):
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


def test_the_output():
    """Prints the four lines."""
    assert run() == {BUILD_OUT!r}


def test_dense_and_relu_backward():
    """A dense layer's three gradients and a ReLU's match numeric derivatives of a squared-output loss."""
    Dense = function("Dense")
    ReLU = function("ReLU")
    layer, relu = Dense(3, 2, seed=5), ReLU()
    X = np.random.default_rng(3).standard_normal((4, 3))

    def total():
        return float((relu.forward(layer.forward(X)) ** 2).sum())

    total()
    grad_in = layer.backward(relu.backward(2 * relu.forward(layer.forward(X))))
    assert np.allclose(layer.dW, central(total, layer.W), atol=1e-6)
    assert np.allclose(layer.db, central(total, layer.b), atol=1e-6)
    assert np.allclose(grad_in, central(total, X), atol=1e-6)
    assert layer.gradients()[0] is layer.dW and relu.gradients() == []


def test_sequential_matches_by_hand():
    """Sequential.backward equals the layers' backward calls in reverse, and the gradients line up with the parameters."""
    Dense = function("Dense")
    ReLU = function("ReLU")
    Sequential = function("Sequential")
    MSELoss = function("MSELoss")
    net = Sequential([Dense(3, 4, seed=1), ReLU(), Dense(4, 4, seed=2), ReLU(), Dense(4, 2, seed=3)])
    X = np.random.default_rng(4).standard_normal((6, 3))
    y = np.random.default_rng(5).standard_normal((6, 2))
    loss = MSELoss()
    loss.forward(net.forward(X), y)
    grad_in = net.backward(loss.backward())
    grad = loss.backward()
    for layer in reversed(net.layers):
        grad = layer.backward(grad)
    assert np.allclose(grad_in, grad)
    assert [g.shape for g in net.gradients()] == [p.shape for p in net.parameters()]


def test_losses():
    """MSE and its gradient match the formulas; softmax cross-entropy matches a hand computation, its gradient is (p - onehot) / n, and logits of 5,000 stay finite."""
    MSELoss = function("MSELoss")
    SoftmaxCrossEntropy = function("SoftmaxCrossEntropy")
    pred = np.array([[1.0, 2.0], [0.0, -1.0]])
    target = np.array([[0.0, 2.0], [1.0, 1.0]])
    mse = MSELoss()
    assert abs(mse.forward(pred, target) - 1.5) < 1e-12 and np.allclose(mse.backward(), 2 * (pred - target) / 4)
    ce = SoftmaxCrossEntropy()
    logits = np.array([[1.0, 2.0, 3.0], [0.0, 0.0, 0.0]])
    labels = np.array([2, 0])
    p = np.exp(logits) / np.exp(logits).sum(axis=1, keepdims=True)
    expected = -np.log(p[[0, 1], labels]).mean()
    assert abs(ce.forward(logits, labels) - expected) < 1e-12
    onehot = np.zeros_like(logits)
    onehot[[0, 1], labels] = 1
    assert np.allclose(ce.backward(), (p - onehot) / 2)
    assert np.isfinite(ce.forward(np.array([[5000.0, 5001.0, 4999.0]]), np.array([0])))


def test_gradient_check_catches_a_bug():
    """gradient_check passes a correct network and reports a gap far above 1e-6 for a layer whose backward drops the mask."""
    Dense = function("Dense")
    ReLU = function("ReLU")
    Sequential = function("Sequential")
    MSELoss = function("MSELoss")
    gradient_check = function("gradient_check")
    X = np.random.default_rng(6).standard_normal((5, 3))
    y = np.random.default_rng(7).standard_normal((5, 2))
    assert gradient_check(Sequential([Dense(3, 4, seed=1), ReLU(), Dense(4, 2, seed=2)]), MSELoss(), X, y) < 1e-6

    class LeakyBug(ReLU):
        def backward(self, grad_out):
            return grad_out

    assert gradient_check(Sequential([Dense(3, 4, seed=1), LeakyBug(), Dense(4, 2, seed=2)]), MSELoss(), X, y) > 1e-3
''',
)
for key, code in BUILD_WRONGS.items():
    write(f"exercises/build-layers-with-backward/wrong/{key}.py", code)
write(
    "exercises/build-layers-with-backward/wrong/typed-in.py",
    "import numpy as np\n\n\nclass Dense:\n    def __init__(self, n_in, n_out, seed=0):\n        self.W = np.zeros((n_in, n_out))\n        self.b = np.zeros(n_out)\n        self.dW = self.W\n        self.db = self.b\n\n    def forward(self, X):\n        return X\n\n    def backward(self, grad_out):\n        return grad_out\n\n    def parameters(self):\n        return [self.W, self.b]\n\n    def gradients(self):\n        return [self.dW, self.db]\n\n\nclass ReLU(Dense):\n    def __init__(self):\n        pass\n\n    def parameters(self):\n        return []\n\n    def gradients(self):\n        return []\n\n\nclass Sequential:\n    def __init__(self, layers):\n        self.layers = layers\n\n    def forward(self, X):\n        return X\n\n    def backward(self, grad):\n        return grad\n\n    def parameters(self):\n        return []\n\n    def gradients(self):\n        return []\n\n\nclass MSELoss:\n    def forward(self, pred, target):\n        return 0.0\n\n    def backward(self):\n        return 0.0\n\n\nclass SoftmaxCrossEntropy(MSELoss):\n    pass\n\n\ndef numeric_gradient(f, param, h=1e-6):\n    return param\n\n\ndef gradient_check(net, loss, X, y):\n    return 0.0\n\n\n"
    + "".join(f"print({line!r})\n" for line in BUILD_OUT.splitlines()),
)

write(
    "exercises/debug-a-gradient-that-fails-its-check/exercise.yaml",
    f'''id: debug-a-gradient-that-fails-its-check
stage: debug
rev: 1
title: "A gradient that fails its check"
prompt: |
  The module's classes on three rows, with the gradient check. The program should print:

  ```
{block(DEBUG_OUT)}  ```

  It has two bugs. Run it: it crashes inside the gradient check with a broadcasting error, because `Dense.backward` computes `dW` as `grad_out.T @ X`, which has the shape of `W` **transposed**; the weight gradient is `X.T @ grad_out`, one entry per entry of `W`. Fix that, and the worst gap is "too big": `ReLU.backward` takes its mask from the sign of the **gradient** coming back instead of from the input it saw in `forward`. The gradient passes where the input was positive, which is what `self.mask` recorded.
skills: [layer-backward, chain]
''',
)
write("exercises/debug-a-gradient-that-fails-its-check/starter.py", DEBUG_STARTER)
write("exercises/debug-a-gradient-that-fails-its-check/solution.py", DEBUG_SOLUTION)
write(
    "exercises/debug-a-gradient-that-fails-its-check/test_exercise.py",
    f'''import numpy as np

from checks import function, run

EXPECTED = {DEBUG_OUT!r}


def test_the_output():
    """Prints matching shapes and a worst gap under a millionth."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\\n{{EXPECTED}}\\nYour program printed:\\n{{printed}}"


def test_on_other_data():
    """The check passes on random data through a deeper stack, and a ReLU passes a gradient only where its input was positive."""
    Dense = function("Dense")
    ReLU = function("ReLU")
    Sequential = function("Sequential")
    MSELoss = function("MSELoss")
    gradient_check = function("gradient_check")
    X = np.random.default_rng(8).standard_normal((5, 3))
    y = np.random.default_rng(9).standard_normal((5, 2))
    assert gradient_check(Sequential([Dense(3, 4, seed=1), ReLU(), Dense(4, 4, seed=2), ReLU(), Dense(4, 2, seed=3)]), MSELoss(), X, y) < 1e-6
    relu = ReLU()
    relu.forward(np.array([[1.0, -1.0]]))
    assert relu.backward(np.array([[-3.0, 3.0]])).tolist() == [[-3.0, 0.0]]
''',
)
write("exercises/debug-a-gradient-that-fails-its-check/wrong/still-transposed.py", DEBUG_STILL_DW)
write("exercises/debug-a-gradient-that-fails-its-check/wrong/still-the-wrong-mask.py", DEBUG_STILL_MASK)
write(
    "exercises/debug-a-gradient-that-fails-its-check/wrong/typed-in.py",
    "import numpy as np\n\n\nclass Dense:\n    def __init__(self, n_in, n_out, seed=0):\n        self.W = np.zeros((n_in, n_out))\n\n\nclass ReLU:\n    pass\n\n\nclass Sequential:\n    pass\n\n\nclass MSELoss:\n    pass\n\n\ndef gradient_check(net, loss, X, y):\n    return 0.0\n\n\n" + "".join(f"print({line!r})\n" for line in DEBUG_OUT.splitlines()),
)

write(
    "exercises/review-relu-with-backward/exercise.yaml",
    f'''id: review-relu-with-backward
stage: review_code
rev: 1
title: "ReLU with backward, from memory"
prompt: |
  Write `ReLU` with the module's contract: `forward(X)` keeps a mask of where the input is positive and returns the input with the rest zeroed; `backward(grad_out)` returns the gradient where the mask is true and zero elsewhere. Print the forward output on `[[2, -1, 0], [-0.5, 3, 1]]` and then the backward output for `[[1, 1, 1], [0.5, -2, 4]]`:

  ```
{block(REVIEW_CODE_OUT)}  ```
skills: [layer-backward]
''',
)
write("exercises/review-relu-with-backward/starter.py", "")
write("exercises/review-relu-with-backward/solution.py", REVIEW_CODE_SOLUTION)
write(
    "exercises/review-relu-with-backward/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints the forward and backward outputs."""
    assert run() == {REVIEW_CODE_OUT!r}


def test_the_mask_comes_from_the_input():
    """The gradient passes where the input was positive, whatever the gradient's own sign."""
    ReLU = function("ReLU")
    relu = ReLU()
    relu.forward(np.array([[1.0, -1.0, 0.0]]))
    assert relu.backward(np.array([[-5.0, 5.0, 5.0]])).tolist() == [[-5.0, 0.0, 0.0]]
''',
)
write("exercises/review-relu-with-backward/wrong/mask-from-the-gradient.py", REVIEW_CODE_WRONG)
write(
    "exercises/review-relu-with-backward/wrong/typed-in.py",
    "class ReLU:\n    pass\n\n\n" + "".join(f"print({line!r})\n" for line in REVIEW_CODE_OUT.splitlines()),
)

print("ml.nn.backward-layers written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
