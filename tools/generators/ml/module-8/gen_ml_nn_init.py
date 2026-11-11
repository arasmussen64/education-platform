"""Writes the topic ml.nn.initialization-and-activations (Module 8's third
topic). Run from the repository root under uv (python -m uv run python
<this file>), so every program's expected output is captured from CPython
rather than typed in. Random weights come from seeded generators (NumPy is
pinned to the same version in the browser); sizes that could differ in the
last bits are printed rounded to two decimals or as words, and the generator
checks that a tenth-decimal nudge of the data leaves every line unchanged.
Files are written as bytes with LF endings."""

import pathlib
import subprocess
import sys

ROOT = pathlib.Path("content/topics/ml.nn.initialization-and-activations")


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


# The module's classes; Dense now takes a starting scale, and the three
# activations each carry their backward.
LAYERS = '''class Dense:
    """A dense layer whose starting weights are standard normals times a scale (1 / sqrt(n_in) unless told otherwise)."""

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


class Tanh:
    def forward(self, X):
        self.out = np.tanh(X)
        return self.out

    def backward(self, grad_out):
        return grad_out * (1 - self.out ** 2)

    def parameters(self):
        return []

    def gradients(self):
        return []


class Sigmoid:
    def forward(self, X):
        self.out = 1 / (1 + np.exp(-X))
        return self.out

    def backward(self, grad_out):
        return grad_out * self.out * (1 - self.out)

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


class MSELoss:
    def forward(self, pred, target):
        self.diff = pred - target
        return float(np.mean(self.diff ** 2))

    def backward(self):
        return 2 * self.diff / self.diff.size
'''

DESCRIBE = '''

def describe(std):
    """A size in words: the words are the same on every machine even when the last digits aren't."""
    if std < 1e-3:
        return "vanished"
    if std > 1e3:
        return "exploded"
    if 0.1 <= std <= 10:
        return "stable"
    return "drifting"
'''

# --- the worked example ----------------------------------------------------------------------

EXAMPLE_HEAD = "import numpy as np\n\n\n" + LAYERS + DESCRIBE
EXAMPLE_TAIL = '''

X = np.array([[1.0, 2.0, 0.5], [0.0, 1.0, -1.0], [2.0, -1.0, 0.0], [-1.0, 0.5, 1.5], [0.5, 0.5, 0.5], [-2.0, 1.0, 1.0]])
y = np.array([[1.0], [0.0], [1.0], [0.0], [1.0], [0.0]])


def train(net, steps=200, rate=0.1):
    loss = MSELoss()
    for _ in range(steps):
        loss.forward(net.forward(X), y)
        net.backward(loss.backward())
        for param, grad in zip(net.parameters(), net.gradients()):
            param -= rate * grad
    return round(loss.forward(net.forward(X), y), 3)


zeros = Sequential([Dense(3, 4, scale=0.0), ReLU(), Dense(4, 1, scale=0.0)])
clones = Sequential([Dense(3, 4, seed=1), ReLU(), Dense(4, 1, seed=2)])
clones.layers[0].W[:] = clones.layers[0].W[:, :1]
clones.layers[2].W[:] = clones.layers[2].W[0, 0]
random = Sequential([Dense(3, 4, seed=1), ReLU(), Dense(4, 1, seed=2)])
for name, net in (("all zeros", zeros), ("four copies of one unit", clones), ("random", random)):
    final = train(net)
    W1 = net.layers[0].W
    print(f"start {name}: loss after 200 steps {final} | hidden units identical: {bool(np.allclose(W1, W1[:, :1]))}")

rng = np.random.default_rng(0)
X_deep = rng.standard_normal((256, 100))


def through_depth(scale, activation, depth=10):
    """A 10-layer stack of 100-unit layers: the std of the activations after each layer, and the gradient reaching the input."""
    layers = []
    for i in range(depth):
        layers += [Dense(100, 100, seed=i, scale=scale), activation()]
    net = Sequential(layers)
    stds = []
    h = X_deep
    for layer in net.layers:
        h = layer.forward(h)
        if isinstance(layer, activation):
            stds.append(float(h.std()))
    grad_in = net.backward(np.random.default_rng(1).standard_normal(h.shape))
    return stds, float(grad_in.std())


for name, scale, activation in (("0.01 with tanh", 0.01, Tanh), ("1.0 with tanh", 1.0, Tanh), ("Xavier 0.1 with tanh", 0.1, Tanh), ("0.1 with ReLU", 0.1, ReLU), ("0.3 with ReLU", 0.3, ReLU), ("He 0.14 with ReLU", np.sqrt(2 / 100), ReLU)):
    stds, grad_std = through_depth(scale, activation)
    print(f"scale {name}: activations after layers 1, 5, 10 have std {stds[0]:.2f}, {stds[4]:.2f}, {stds[9]:.2f} ({describe(stds[9])}); the gradient reaching the input: {describe(grad_std)}")

big = Tanh()
big.forward(Dense(100, 100, seed=0, scale=1.0).forward(X_deep))
print("scale 1.0 with tanh: fraction of outputs beyond 0.99, where the slope is under 0.02:", round(float((np.abs(big.out) > 0.99).mean()), 2))
z = Dense(100, 100, seed=0, scale=1.0).forward(X_deep)
print("scale 1.0 with sigmoid: fraction of inputs beyond 4, where the slope is under 0.02:", round(float((np.abs(z) > 4).mean()), 2))
dead = Dense(100, 100, seed=3, scale=np.sqrt(2 / 100))
dead.b[:] = -5.0
h = ReLU().forward(dead.forward(X_deep))
print("He weights but a bias of -5: fraction of ReLU units that never fire on 256 inputs:", round(float((h.max(axis=0) == 0).mean()), 2))
print("rules of thumb: tanh or sigmoid -> Xavier, 1 / sqrt(n_in) = 0.10 for 100 inputs | ReLU -> He, sqrt(2 / n_in) = 0.14 | biases -> 0")
'''
EXAMPLE = EXAMPLE_HEAD + EXAMPLE_TAIL
EXAMPLE_OUT = out(EXAMPLE)
print("example:\n" + EXAMPLE_OUT)
EX = EXAMPLE_OUT.splitlines()
assert len(EX) == 13, EX
assert EX[0].startswith("start all zeros: loss after 200 steps ") and EX[0].endswith("hidden units identical: True"), EX[0]
assert EX[1].startswith("start four copies of one unit:") and EX[1].endswith("hidden units identical: True"), EX[1]
assert EX[2].startswith("start random:") and EX[2].endswith("hidden units identical: False"), EX[2]
final_losses = [float(line.split("steps ")[1].split(" |")[0]) for line in EX[:3]]
assert final_losses[2] < final_losses[1] <= final_losses[0] + 1e-9, final_losses
assert EX[3].endswith("(vanished); the gradient reaching the input: vanished"), EX[3]
assert "(stable)" in EX[4] and EX[4].endswith(": exploded"), EX[4]
assert "(stable)" in EX[5] and EX[5].endswith(": stable"), EX[5]
assert "(drifting)" in EX[6] and EX[6].endswith(": drifting"), EX[6]
assert EX[7].endswith("(exploded); the gradient reaching the input: exploded"), EX[7]
assert "(stable)" in EX[8] and EX[8].endswith(": stable"), EX[8]
SATURATED_TANH = float(EX[9].split()[-1])
SATURATED_SIGMOID = float(EX[10].split()[-1])
DEAD = float(EX[11].split()[-1])
ZERO_LOSS, CLONE_LOSS, RANDOM_LOSS = final_losses
assert SATURATED_TANH > 0.7 and SATURATED_SIGMOID > 0.5 and DEAD > 0.8, (SATURATED_TANH, SATURATED_SIGMOID, DEAD)
NUDGED = EXAMPLE.replace("X_deep = rng.standard_normal((256, 100))", "X_deep = rng.standard_normal((256, 100))\nX_deep[0, 0] += 1e-10")
assert out(NUDGED) == EXAMPLE_OUT, "a tenth-decimal nudge changed a printed line"
EXAMPLE_LINES = EXAMPLE.splitlines()


def ln(text: str, after: int = 0) -> int:
    return next(i + 1 for i, line in enumerate(EXAMPLE_LINES) if i + 1 > after and text in line)


XAVIER_TANH_STD_10 = EX[5].split("std ")[1].split(" (")[0].split(", ")[2]
HE_RELU_STD_10 = EX[8].split("std ")[1].split(" (")[0].split(", ")[2]
RELU_01_STD_10 = EX[6].split("std ")[1].split(" (")[0].split(", ")[2]

# --- recall programs ----------------------------------------------------------------------------

PREDICT_CLONES = '''import numpy as np

x = np.array([[1.0, 2.0]])
W1 = np.array([[0.5, 0.5], [0.2, 0.2]])
W2 = np.array([[1.0], [1.0]])
h = np.maximum(x @ W1, 0.0)
grad_h = np.ones((1, 1)) @ W2.T * (h > 0)
dW1 = x.T @ grad_h
print(h.tolist(), dW1.tolist())
print(bool(np.allclose(dW1[:, 0], dW1[:, 1])), bool(np.allclose((W1 - 0.1 * dW1)[:, 0], (W1 - 0.1 * dW1)[:, 1])))
'''
PREDICT_CLONES_OUT = out(PREDICT_CLONES)
assert PREDICT_CLONES_OUT == "[[0.9, 0.9]] [[1.0, 1.0], [2.0, 2.0]]\nTrue True\n", PREDICT_CLONES_OUT

PREDICT_SCALE = '''n_in = 100
for scale in (0.05, 0.1, 0.2):
    std = 1.0
    for layer in range(5):
        std = std * scale * n_in ** 0.5
    print(scale, round(std, 5))
'''
PREDICT_SCALE_OUT = out(PREDICT_SCALE)
assert PREDICT_SCALE_OUT == "0.05 0.03125\n0.1 1.0\n0.2 32.0\n", PREDICT_SCALE_OUT

REVIEW_XAVIER = '''import numpy as np

for n_in in (4, 100, 784):
    print(n_in, round(float(np.sqrt(1 / n_in)), 4), round(float(np.sqrt(2 / n_in)), 4))
'''
REVIEW_XAVIER_OUT = out(REVIEW_XAVIER)
assert REVIEW_XAVIER_OUT == "4 0.5 0.7071\n100 0.1 0.1414\n784 0.0357 0.0505\n", REVIEW_XAVIER_OUT

PARSONS_LINES = [
    "import numpy as np",
    "rng = np.random.default_rng(0)",
    "X = rng.standard_normal((64, 100))",
    "W = rng.standard_normal((X.shape[1], 100)) * np.sqrt(2 / X.shape[1])",
    "h = np.maximum(X @ W, 0.0)",
    "print(round(float(h.std()), 1))",
]
PARSONS_OUT = out("\n".join(PARSONS_LINES) + "\n")
assert PARSONS_OUT in ("0.8\n", "0.9\n"), PARSONS_OUT

# --- the fill-in --------------------------------------------------------------------------------

FILL_SOLUTION = '''import numpy as np


def xavier_scale(n_in):
    """Keeps the size of the signal through a tanh or sigmoid layer: 1 / sqrt(n_in)."""
    return float(np.sqrt(1 / n_in))


def he_scale(n_in):
    """Keeps the size of the signal through a ReLU layer, which zeroes half of it: sqrt(2 / n_in)."""
    return float(np.sqrt(2 / n_in))


print(xavier_scale(100), he_scale(50), he_scale(2))
'''
FILL_STARTER = FILL_SOLUTION.replace("    return float(np.sqrt(1 / n_in))", "    return float(np.sqrt(... / n_in))").replace("    return float(np.sqrt(2 / n_in))", "    return float(np.sqrt(... / n_in))")
FILL_WRONG = FILL_SOLUTION.replace("    return float(np.sqrt(2 / n_in))", "    return float(np.sqrt(1 / n_in))")
FILL_OUT = out(FILL_SOLUTION)
assert FILL_OUT == "0.1 0.2 1.0\n", FILL_OUT
assert differs(FILL_WRONG, FILL_OUT)

# --- the write ----------------------------------------------------------------------------------

WRITE_SOLUTION = '''import numpy as np


def dead_fraction(H):
    """The share of ReLU units (columns of H) that are zero for every input in the batch."""
    return float((H.max(axis=0) == 0).mean())


def saturated_fraction(Z, threshold=4.0):
    """The share of pre-activations whose size is beyond the threshold, where a sigmoid's slope is under 0.02."""
    return float((np.abs(Z) > threshold).mean())


H = np.array([[0.0, 1.5, 0.0, 2.0], [0.0, 0.0, 0.0, 0.5], [0.0, 3.0, 0.0, 0.0]])
Z = np.array([[5.0, -1.0, 0.5, -6.0], [3.9, 4.1, -4.0, 10.0]])
print(dead_fraction(H), saturated_fraction(Z), saturated_fraction(Z, threshold=3.0))
'''
WRITE_TAIL = WRITE_SOLUTION.split('\n\n\nH = np.array')[1]
WRITE_TAIL = 'H = np.array' + WRITE_TAIL
WRITE_OUT = out(WRITE_SOLUTION)
assert WRITE_OUT == "0.5 0.5 0.75\n", WRITE_OUT
WRITE_DEAD_PER_ROW = WRITE_SOLUTION.replace("    return float((H.max(axis=0) == 0).mean())", "    return float((H == 0).mean())")
WRITE_SATURATED_UNSIGNED = WRITE_SOLUTION.replace("    return float((np.abs(Z) > threshold).mean())", "    return float((Z > threshold).mean())")
assert differs(WRITE_DEAD_PER_ROW, WRITE_OUT) and differs(WRITE_SATURATED_UNSIGNED, WRITE_OUT)

# --- the build ----------------------------------------------------------------------------------

BUILD_TOOLS = '''

def xavier_scale(n_in):
    """The starting scale that keeps a tanh or sigmoid layer's signal the same size: 1 / sqrt(n_in)."""
    return float(np.sqrt(1 / n_in))


def he_scale(n_in):
    """The starting scale that keeps a ReLU layer's signal the same size, since ReLU zeroes half: sqrt(2 / n_in)."""
    return float(np.sqrt(2 / n_in))


def activation_stds(net, X):
    """The std of the batch after each layer of the network, in order."""
    stds = []
    for layer in net.layers:
        X = layer.forward(X)
        stds.append(float(X.std()))
    return stds


def input_gradient_std(net, X):
    """Run forward, push a unit-size gradient (standard normals, seed 1) back through the network, and return the std of what reaches the input."""
    out = net.forward(X)
    grad_in = net.backward(np.random.default_rng(1).standard_normal(out.shape))
    return float(grad_in.std())


def dead_fraction(H):
    """The share of ReLU units (columns) that are zero for every input in the batch."""
    return float((H.max(axis=0) == 0).mean())


def saturated_fraction(Z, threshold=4.0):
    """The share of pre-activations beyond the threshold in size."""
    return float((np.abs(Z) > threshold).mean())


def units_identical(W):
    """Whether every column of W is the same column: the symmetry that zero or copied starting weights never break."""
    return bool(np.allclose(W, W[:, :1]))
'''
BUILD_TAIL = '''

rng = np.random.default_rng(0)
X = rng.standard_normal((256, 100))


def stack(scale, activation, depth=8):
    return Sequential([piece for i in range(depth) for piece in (Dense(100, 100, seed=i, scale=scale), activation())])


print(xavier_scale(100), he_scale(100), he_scale(50))
for name, scale, activation in (("0.01 tanh", 0.01, Tanh), ("Xavier tanh", xavier_scale(100), Tanh), ("0.1 ReLU", 0.1, ReLU), ("He ReLU", he_scale(100), ReLU)):
    net = stack(scale, activation)
    stds = activation_stds(net, X)
    print(name, describe(stds[-1]), describe(input_gradient_std(net, X)))
layer = Dense(100, 100, seed=3, scale=he_scale(100))
layer.b[:] = -5.0
print(round(dead_fraction(ReLU().forward(layer.forward(X))), 2), round(saturated_fraction(Dense(100, 100, seed=0, scale=1.0).forward(X)), 2))
print(units_identical(np.zeros((3, 4))), units_identical(np.tile(np.array([[1.0], [2.0]]), (1, 5))), units_identical(Dense(3, 4, seed=1).W))
'''
BUILD_SOLUTION = "import numpy as np\n\n\n" + LAYERS + DESCRIBE + BUILD_TOOLS + BUILD_TAIL
BUILD_OUT = out(BUILD_SOLUTION)
print("build:\n" + BUILD_OUT)
BUILD_LINES = BUILD_OUT.splitlines()
assert BUILD_LINES[0].startswith("0.1 0.1414") and BUILD_LINES[1] == "0.01 tanh vanished vanished", BUILD_OUT
assert BUILD_LINES[4] == "He ReLU stable stable" and BUILD_LINES[5].startswith("0.9") and BUILD_LINES[6] == "True True False", BUILD_OUT
assert out(BUILD_SOLUTION.replace("X = rng.standard_normal((256, 100))", "X = rng.standard_normal((256, 100))\nX[0, 0] += 1e-10")) == BUILD_OUT
BUILD_WRONGS = {
    "he-without-the-two": BUILD_SOLUTION.replace('    """The starting scale that keeps a ReLU layer\'s signal the same size, since ReLU zeroes half: sqrt(2 / n_in)."""\n    return float(np.sqrt(2 / n_in))', '    """The starting scale that keeps a ReLU layer\'s signal the same size, since ReLU zeroes half: sqrt(2 / n_in)."""\n    return float(np.sqrt(1 / n_in))'),
    "dead-counted-per-entry": BUILD_SOLUTION.replace("    return float((H.max(axis=0) == 0).mean())", "    return float((H == 0).mean())"),
    "saturated-one-sided": BUILD_SOLUTION.replace("    return float((np.abs(Z) > threshold).mean())", "    return float((Z > threshold).mean())"),
    "identical-means-all-equal": BUILD_SOLUTION.replace("    return bool(np.allclose(W, W[:, :1]))", "    return bool(np.allclose(W, W[0, 0]))"),
}
for key, code in BUILD_WRONGS.items():
    assert code != BUILD_SOLUTION and differs(code, BUILD_OUT), key

# --- the debug ----------------------------------------------------------------------------------

DEBUG_HEAD = "import numpy as np\n\n\n" + LAYERS
DEBUG_TAIL = '''

X = np.array([[1.0, 2.0, 0.5], [0.0, 1.0, -1.0], [2.0, -1.0, 0.0], [-1.0, 0.5, 1.5], [0.5, 0.5, 0.5], [-2.0, 1.0, 1.0]])
y = np.array([[1.0], [0.0], [1.0], [0.0], [1.0], [0.0]])
hidden = Dense(3, 8, seed=1, scale=np.sqrt(2 / 3))
hidden.b[:] = 0.0
net = Sequential([hidden, ReLU(), Dense(8, 1, seed=2)])
loss = MSELoss()
first = loss.forward(net.forward(X), y)
for step in range(300):
    loss.forward(net.forward(X), y)
    net.backward(loss.backward())
    for param, grad in zip(net.parameters(), net.gradients()):
        param -= 0.05 * grad
last = loss.forward(net.forward(X), y)
h = net.layers[1].forward(hidden.forward(X))
print("loss", round(first, 4), "->", round(last, 4), "| the loss fell by more than half:", last < first / 2)
print("hidden units identical:", bool(np.allclose(hidden.W, hidden.W[:, :1])), "| dead hidden units:", int((h.max(axis=0) == 0).sum()), "of 8")
'''
DEBUG_SOLUTION = DEBUG_HEAD + DEBUG_TAIL
BUG_ZERO = ("hidden = Dense(3, 8, seed=1, scale=np.sqrt(2 / 3))", "hidden = Dense(3, 8, seed=1, scale=0.0)")
BUG_BIAS = ("hidden.b[:] = 0.0", "hidden.b[:] = -5.0")
DEBUG_STARTER = DEBUG_SOLUTION.replace(*BUG_ZERO).replace(*BUG_BIAS)
DEBUG_STILL_ZERO = DEBUG_SOLUTION.replace(*BUG_ZERO)
DEBUG_STILL_BIAS = DEBUG_SOLUTION.replace(*BUG_BIAS)
DEBUG_OUT = out(DEBUG_SOLUTION)
STARTER_OUT = out(DEBUG_STARTER)
print("debug:\n" + DEBUG_OUT + "starter:\n" + STARTER_OUT)
assert DEBUG_OUT.splitlines()[0].endswith("the loss fell by more than half: True") and DEBUG_OUT.splitlines()[1] == "hidden units identical: False | dead hidden units: 0 of 8", DEBUG_OUT
assert STARTER_OUT.splitlines()[0].endswith("False") and STARTER_OUT.splitlines()[1] == "hidden units identical: True | dead hidden units: 8 of 8", STARTER_OUT
assert out(DEBUG_STILL_ZERO).splitlines()[1].startswith("hidden units identical: True") and out(DEBUG_STILL_BIAS).splitlines()[1].endswith("dead hidden units: 8 of 8")
assert out(DEBUG_SOLUTION.replace("X = np.array([[1.0, 2.0, 0.5]", "X = np.array([[1.0000000001, 2.0, 0.5]")) == DEBUG_OUT

REVIEW_CODE_SOLUTION = '''import numpy as np


def xavier_scale(n_in):
    return float(np.sqrt(1 / n_in))


def he_scale(n_in):
    return float(np.sqrt(2 / n_in))


def start_weights(n_in, n_out, activation, seed=0):
    """Standard normals times He's scale for ReLU and Xavier's for anything else, with zero biases."""
    scale = he_scale(n_in) if activation == "relu" else xavier_scale(n_in)
    W = np.random.default_rng(seed).standard_normal((n_in, n_out)) * scale
    return W, np.zeros(n_out)


W, b = start_weights(100, 50, "relu", seed=1)
print(W.shape, b.tolist() == [0.0] * 50, round(float(W.std()), 2))
W, b = start_weights(100, 50, "tanh", seed=1)
print(round(float(W.std()), 2))
'''
REVIEW_CODE_OUT = out(REVIEW_CODE_SOLUTION)
assert REVIEW_CODE_OUT == "(100, 50) True 0.14\n0.1\n", REVIEW_CODE_OUT
REVIEW_CODE_WRONG = REVIEW_CODE_SOLUTION.replace('    scale = he_scale(n_in) if activation == "relu" else xavier_scale(n_in)', "    scale = xavier_scale(n_in)")
assert differs(REVIEW_CODE_WRONG, REVIEW_CODE_OUT)

# =====================================================================================
# topic.yaml
# =====================================================================================

write(
    "topic.yaml",
    '''id: ml.nn.initialization-and-activations
kind: topic
status: ready
title: "Starting weights and activation functions"
summary: "Why a network started at zero can't learn, why weights that are too big or too small kill a deep network's signal, the Xavier and He rules that keep it alive, and what sigmoid, tanh and ReLU each do to the gradient flowing back."
prerequisites: [ml.nn.backward-layers]
packages: [numpy]
estimated_minutes: 50
rev: 1
objectives:
  - "Show that zero or identical starting weights keep every neuron in a layer identical forever, and say why."
  - "Measure how the size of activations and gradients changes layer by layer under too-small, too-large and Xavier or He starting weights."
  - "Choose an activation function and its starting scale, and say what saturation and dead ReLUs are."
  - "Explain why these choices matter more as a network gets deeper."
# Linked, never copied or embedded: Wikipedia is CC BY-SA 4.0; the paper is
# in the PMLR proceedings, linked.
resources:
  - title: "Wikipedia: Weight initialization (the Constant initialization, Random initialization, Glorot initialization and He initialization sections)"
    url: https://en.wikipedia.org/wiki/Weight_initialization
    type: reading
    use: link
    license: CC BY-SA 4.0 (linked, not copied)
  - title: "Wikipedia: Vanishing gradient problem (why a product of small slopes through many layers goes to zero)"
    url: https://en.wikipedia.org/wiki/Vanishing_gradient_problem
    type: reading
    use: link
    license: CC BY-SA 4.0 (linked, not copied)
  - title: "Glorot and Bengio 2010, Understanding the difficulty of training deep feedforward neural networks (the paper behind Xavier initialization; sections 3 and 4)"
    url: https://proceedings.mlr.press/v9/glorot10a.html
    type: reading
    use: link
    license: "PMLR proceedings, copyright the authors (linked, not copied)"
practice:
  - example-signals-through-depth
  - predict-identical-units
  - mcq-why-zeros-fail
  - predict-scale-through-depth
  - mcq-he-versus-xavier
  - parsons-he-init
  - mcq-saturation
  - mcq-dead-relus
  - mcq-deeper-is-harsher
  - fill-he-and-xavier
  - write-dead-and-saturated
prove:
  build: build-an-initialization-study
  debug: debug-a-network-that-will-not-learn
  explain:
    prompt: |
      Three teammates bring you networks that won't train. The first started every weight at zero "to be neutral" and gets the same output for every input. The second trains fine with two hidden layers but not with twelve, in tanh: the loss barely moves. The third uses ReLU with He weights but set every bias to -5 "so that units start quiet", and most hidden units never fire. In your own words: why zero (or copied) starting weights can never be told apart by training; what happens to the size of the activations and of the gradient as they pass through many layers when the weights are too small, too large, or scaled by the Xavier or He rule, and why depth makes it worse; what saturation does to a tanh or sigmoid layer's gradient; and what a dead ReLU is and how biases and learning rates make them.
    rubric:
      - id: symmetry
        required: true
        description: "Units with identical weights compute identical outputs, receive identical gradients and take identical steps, so they stay identical forever; the layer is one unit in disguise. All zeros is the extreme case: nothing moves at all except the last bias. Random starting weights break the symmetry."
      - id: scale
        required: true
        description: "Each layer multiplies the signal's size by about scale times sqrt(n_in): below 1 the activations shrink toward zero and the gradients with them, above 1 they grow until the activation saturates or the numbers explode; the Xavier rule 1 / sqrt(n_in) keeps the product at 1 for tanh, and the He rule sqrt(2 / n_in) does the same for ReLU, which halves the signal's mean square. Depth compounds the per-layer factor: 0.7 to the twelfth is 0.014."
      - id: activations
        required: true
        description: "A saturated tanh or sigmoid unit has a slope near zero (a sigmoid's slope is at most 0.25 and under 0.02 past |z| = 4), so the gradient through it is multiplied by nearly nothing at every such layer; a ReLU unit whose pre-activation is negative for every input gives zero output and zero gradient, so nothing can revive it; a large negative bias or a large learning-rate step makes them."
      - id: depth
        required: true
        description: "Two layers multiply the signal and the gradient by the per-layer factor twice and survive almost any choice; twelve layers multiply it twelve times, so a factor of 0.7 or 1.4 per layer becomes 0.01 or 50, which is why the deeper network needs the right scale and activation where the shallow one didn't."
    model_answer: |
      Zero starting weights can't be told apart by training because training only ever changes a weight in proportion to its gradient, and two units with the same weights have the same gradient. With everything at zero the hidden units all output zero, the ReLU masks are all off, and the gradient that reaches the hidden weights is zero, so nothing moves except the last layer's bias; the network can only learn the average target, which is why the first teammate sees the same output for every input. The same is true of any copied start: four units with the same weights compute the same thing, receive the same gradient and take the same step, forever, so the layer is one unit wearing four coats. The fix is random starting weights, which make the units different so that the gradients can tell them apart; the worked example shows the all-zero and the four-copies networks stuck at the same loss while the random one learns. The second teammate's problem is scale. A dense layer multiplies the size of its input by about the weight scale times the square root of the number of inputs, and the activation then shrinks it a little more; whatever that per-layer factor is, a deep network applies it once per layer. At a scale of 0.01 with a hundred inputs the factor is 0.1 and after ten layers the activations are ten billion times smaller, the gradient coming back is multiplied by the same small factors, and the loss barely moves. At a scale of 1 the factor is 10, the tanh units are driven to plus or minus one, where their slope is almost nothing, and yet the gradient coming back grows, because each layer's weights multiply it by ten; too-large weights fail both ways at once, and a ReLU stack at a scale of 0.3 simply explodes. The Xavier rule sets the scale to one over the square root of the number of inputs, so the factor is about one and the signal keeps its size through tanh layers, and the He rule uses the square root of two over the number of inputs for ReLU, because ReLU zeroes half of every layer's variance and the two puts it back. Two layers survive almost any scale because the factor is applied only twice; twelve layers raise it to the twelfth power, 0.7 becomes 0.014 and 1.4 becomes 57, which is why the deeper network needs the rule the shallow one got away without. Saturation is what a tanh or sigmoid does to the gradient when its input is large: a sigmoid's slope is at most a quarter, and past an input of four it is under 0.02, so the gradient through a saturated layer is multiplied by nearly nothing, and through several such layers it vanishes however good the weights are. A dead ReLU is a unit whose pre-activation is negative for every input, so its output is zero and, because the ReLU's gradient is zero on that side, its weights get no gradient and nothing can bring it back. The third teammate made them on purpose: with a bias of minus five and inputs of size about one, the pre-activations are almost never positive, so the units never fire and never learn. Biases should start at zero; the other common cause is a learning-rate step so large that it throws a unit's weights into the negative region for every input, which is one reason a too-high learning rate kills a ReLU network rather than just making it noisy.
review_pool:
  - review-predict-xavier-rule
  - review-mcq-all-the-same-but-not-zero
  - review-mcq-why-depth-amplifies
  - review-start-weights
# What this topic teaches. Each question names the skills it tests, so a
# missed question can come back as a different one on the same skill
# (ADR-0011).
skills:
  - id: symmetry
    description: "Show why zero or identical starting weights keep a layer's units identical forever"
  - id: scale
    description: "Measure the signal and the gradient through depth under different starting scales, and apply the Xavier and He rules"
  - id: activations
    description: "Say what saturation and dead ReLUs are, how they arise, and what they do to the gradient"
  - id: depth
    description: "Explain why starting scale and activation matter more as a network gets deeper"
''',
)

# =====================================================================================
# lesson.mdx
# =====================================================================================

write(
    "lesson.mdx",
    f'''<Intro>

A network's weights have to start somewhere, and where they start decides whether a deep network can learn at all. Start them at zero and every unit in a layer is a copy of every other, forever. Start them too small and the signal shrinks to nothing by the tenth layer; too big and it explodes, or drives tanh and sigmoid units into the flat parts of their curves where the gradient dies. This topic measures all of that on a ten-layer stack, states the two rules that keep the signal alive (**Xavier** for tanh and sigmoid, **He** for ReLU), and names the two ways an activation function kills a gradient: **saturation** and **dead ReLUs**.

The main resource is **Wikipedia's _Weight initialization_ page**, which walks from constant to random to the Glorot (Xavier) and He rules with the variance argument behind each; about 15 minutes. The _Vanishing gradient problem_ page explains why a product of small slopes goes to zero, and the Glorot and Bengio paper is where the Xavier rule and the measurements of activations through depth come from. Watch for:

- **Why constant weights fail**: symmetry, not size.
- **Variance through a layer**: what multiplies it and what keeps it at one.
- **The factor of two** in He's rule, and where it comes from.

</Intro>

<Resource index={{0}} />

<Recap>

- **Zero or copied weights never learn apart.** Units with identical weights compute identical outputs, get identical gradients (`dW = X.T @ grad_out`, the same for each column) and take identical steps, so they stay identical: a layer of four copies is one unit in disguise. All zeros is worse: the hidden outputs are zero, the ReLU masks are off, and no gradient reaches the first layer, so only the last bias moves and the network learns the average target. **Random** starting weights break the symmetry; that is their first job.
- **Scale through a layer.** For inputs of size about 1, a dense layer with weights of scale `s` and `n_in` inputs gives outputs of size about `s * sqrt(n_in)`, because a sum of `n_in` independent terms has standard deviation `sqrt(n_in)` times one term's. Whatever that per-layer factor is, a stack applies it once per layer: `0.5 ** 10` is 0.001 and `2 ** 10` is 1,024. In the example, scale 0.01 with tanh vanished by layer 10 and the gradient reaching the input vanished with it; scale 1.0 drove tanh to saturation ({SATURATED_TANH:.0%} of outputs beyond 0.99) while the gradient coming back **exploded**, multiplied by about 10 at every layer's weights even as the saturated units passed almost nothing through: too-large weights fail both ways at once.
- **Xavier** (Glorot): `scale = 1 / sqrt(n_in)`, so the factor is 1 and tanh or sigmoid layers roughly keep the signal's size (the example's Xavier tanh stack still shrinks a little each layer, since tanh squashes what it is given, and ended at a std of {XAVIER_TANH_STD_10} after ten; the full rule averages `n_in` and `n_out`, `sqrt(2 / (n_in + n_out))`, with the same idea). **He** (Kaiming): `scale = sqrt(2 / n_in)` for ReLU, because ReLU zeroes half of every layer's values, which halves the signal's mean square (its average squared size), and the 2 puts it back; the He ReLU stack ended at {HE_RELU_STD_10} and its gradient was stable, where the same stack at scale 0.1 drifted to {RELU_01_STD_10} and at 0.3 exploded past a thousand. Biases start at 0. Frameworks apply these rules by default, which is why a beginner rarely sees the failure; it is still there under the hood.
- **Saturation.** A sigmoid's slope is at most 0.25 and under 0.02 past `|z| = 4`; tanh's is under 0.02 past `|z|` of about 2.65 (where tanh passes 0.99). A unit driven there contributes almost no gradient, and a gradient that passes through several saturated layers is multiplied by nearly nothing: the **vanishing gradient** of deep sigmoid and tanh networks, which is the main reason ReLU replaced them in deep stacks. Large weights, large inputs and large learning-rate steps cause it.
- **Dead ReLUs.** A ReLU unit whose pre-activation is negative for every input gives zero output and, because its gradient is zero on that side, zero gradient to its own weights: nothing can revive it. A large negative bias makes them on purpose (the example's bias of -5 killed {DEAD:.0%} of the units); a learning-rate step big enough to push a unit's weights into the negative region for every input makes them by accident. Fixes: biases at 0, He scale, a smaller learning rate, or a leaky ReLU that keeps a small slope on the negative side.
- **Why depth makes it worse.** Two layers apply the per-layer factor twice and survive almost any choice; twelve apply it twelve times, so 0.7 becomes 0.014 and 1.4 becomes 57. The rules above exist so that deep networks start in a state where the signal and the gradient have a sensible size at every layer; without them, the loss curve of a deep network is flat from the first step, which When training goes wrong lists among the first things to check.
- **In machine learning** (names you'll meet later): `nn.init.xavier_uniform_` and `kaiming_normal_` are these rules; **batch normalization** and **layer normalization** re-scale the signal at every layer during training, which is why very deep networks tolerate imperfect starting weights; **residual connections** add a layer's input to its output so that the signal has a path that no scale can shrink; and **GELU** and **leaky ReLU** keep a little gradient on the negative side.

</Recap>
''',
)

# =====================================================================================
# recall
# =====================================================================================

write(
    "recall/predict-identical-units.yaml",
    f'''id: predict-identical-units
type: predict_output
rev: 1
prompt: |
  Two hidden units with the same weights, one input, a gradient of 1 at the output: the hidden values, the weight gradient, and whether the two units are still identical after a step. What does the program print?
code: |
{block(PREDICT_CLONES)}expected_output: |
{block(PREDICT_CLONES_OUT)}explanation: |
  Both units compute 0.5 + 0.4 = 0.9, both are active, and both receive the same gradient (1 through the output weights of 1), so their weight gradients are the same column: input 1 gives 1 and input 2 gives 2 for each. Identical weights, identical gradients, identical steps: after the update the columns still match, and they will after every update.
skills: [symmetry]
''',
)

mcq(
    "mcq-why-zeros-fail",
    "Why can't a network whose weights all start at zero learn anything but the average target?",
    [
        "Because zero weights make the loss exactly zero, so there is nothing to learn",
        "Because NumPy's random generator is seeded by the weights and zero is not a valid seed, so the first layer never gets random values and the forward pass repeats itself",
        "Because every hidden unit is identical and stays so: same outputs, same gradients, same steps; at zero no gradient even reaches the first layer",
        "Because the ReLU of zero is undefined, so the forward pass raises an error",
    ],
    2,
    "Training changes each weight by its own gradient, and units with the same weights have the same gradient, so they can never become different. At zero it is worse still: the hidden outputs are all zero, the ReLU masks are off, and the gradient for the first layer is zero, so only the last bias moves. The loss is not zero, the forward pass runs fine, and seeds have nothing to do with it.",
    ["symmetry"],
)

write(
    "recall/predict-scale-through-depth.yaml",
    f'''id: predict-scale-through-depth
type: predict_output
rev: 1
prompt: |
  The rule of thumb for the size of a signal through dense layers: each layer multiplies it by the weight scale times the square root of the number of inputs. Five layers of 100 inputs, at three scales. What does the program print?
code: |
{block(PREDICT_SCALE)}expected_output: |
{block(PREDICT_SCALE_OUT)}explanation: |
  With 100 inputs the square root is 10, so the per-layer factor is 0.5, 1 or 2. Five layers of 0.5 is 1/32; five of 1 is 1; five of 2 is 32. The scale that makes the factor exactly 1 is 1 over the square root of the inputs, which is the Xavier rule.
skills: [scale]
''',
)

mcq(
    "mcq-he-versus-xavier",
    "Xavier's rule scales the starting weights by `1 / sqrt(n_in)`; He's by `sqrt(2 / n_in)`. Where does the 2 come from?",
    [
        "From ReLU zeroing about half of every layer's outputs, which halves the variance; the 2 puts it back",
        "From ReLU having two sides, so each weight is counted twice",
        "From He's networks being twice as deep as Glorot's",
        "From the gradient being computed twice per layer in the backward pass, once for the input and once for the weights",
    ],
    0,
    "A pre-activation of variance 1 becomes, after ReLU, a signal whose mean square (its average squared size) is about one half, because the negative half is zeroed. Through many ReLU layers that halving compounds, so He's rule doubles the weight variance (multiplies the scale by the square root of 2) to cancel it. Tanh at small inputs is close to the identity and takes no such correction, which is why Xavier's rule has no 2.",
    ["scale"],
)

write(
    "recall/parsons-he-init.yaml",
    "id: parsons-he-init\ntype: parsons\nrev: 1\nprompt: |\n"
    + block("Put the lines in order to start a ReLU layer's weights by He's rule, run a batch of standard-normal inputs through it, and print the standard deviation of the activations (about 0.8 to 0.9, the signal kept alive). One line is a decoy that doesn't belong.")
    + "lines:\n"
    + "".join(f"  - {quoted(line)}\n" for line in PARSONS_LINES)
    + "distractors:\n  - "
    + quoted("W = rng.standard_normal((X.shape[1], 100)) * 0.01")
    + "\nexplanation: |\n"
    + block("The generator comes first, the batch draws from it, the weights are shaped by the batch's width and scaled by the square root of 2 over that width, and the ReLU output's spread is read off. The decoy scales the weights by 0.01, about a fourteenth of He's 0.14 for 100 inputs, which would shrink the signal tenfold at every layer (0.01 times the square root of 100).")
    + "skills: [scale]\n",
)

mcq(
    "mcq-saturation",
    "A sigmoid layer's inputs are mostly beyond 4 in size. What does that do to training?",
    [
        "Nothing: a sigmoid always outputs between 0 and 1, so its layer is safe at any input size, and large inputs just make the outputs more decisive, which helps",
        "The outputs overflow to infinity, as the exponential does",
        "Its outputs sit near 0 or 1 where the slope is under 0.02, so the gradient through it is multiplied by nearly nothing and earlier layers stop learning",
        "The layer learns faster, because large inputs mean confident outputs",
    ],
    2,
    "The sigmoid's slope is `out * (1 - out)`, at most 0.25 at an input of 0 and under 0.02 beyond 4. A gradient coming back through a saturated unit is multiplied by that slope, and through several such layers by their product, which is why deep sigmoid networks had vanishing gradients. The output is bounded, so nothing overflows; it is the gradient, not the output, that is lost.",
    ["activations"],
)

mcq(
    "mcq-dead-relus",
    "What is a dead ReLU, how does it happen, and why doesn't training fix it?",
    [
        "A unit whose weights have shrunk to exactly zero through weight decay; it outputs zero until decay is turned off, after which the gradient brings it back within a few steps, so it is harmless in practice",
        "A unit that fires for every input, so it carries no information; a smaller learning rate fixes it",
        "A unit whose output is NaN after an overflow; restarting the training fixes it",
        "A unit whose pre-activation is negative for every input: it outputs 0 and, ReLU's gradient being 0 there, its weights get no gradient; a big negative bias or a large step causes it",
    ],
    3,
    "On the negative side a ReLU is flat, so a unit that is negative for the whole dataset sends no gradient to its own weights and can't move. Biases that start negative put units there from the start; a learning-rate step large enough to throw a unit's weights across the boundary does it mid-training. Units that always fire are the opposite problem and still have a gradient; zeros from decay and NaNs are different failures.",
    ["activations"],
)

mcq(
    "mcq-deeper-is-harsher",
    "A tanh network trains fine with 2 hidden layers at a weight scale of 0.07 (100 inputs per layer) and not at all with 12. Why does depth change the answer?",
    [
        "Because a 12-layer network has far more parameters than a small dataset can support, so it overfits before the loss can move, which looks like not training",
        "Because the per-layer factor, about 0.7 here, applies once per layer: 0.7 squared is 0.5, 0.7 to the twelfth is 0.014, and signal and gradient vanish",
        "Because tanh's output is bounded, so after about 4 layers there is no range left for the signal to use",
        "Because the learning rate has to be divided by the number of layers",
    ],
    1,
    "Each dense layer multiplies the signal's size by about the scale times the square root of its inputs, 0.07 times 10 here, and the gradient coming back is multiplied by the same factors. Two layers lose half the size; twelve lose almost all of it, so the loss barely moves from the first step. The Xavier scale of 0.1 makes the factor 1, and then depth stops mattering for this reason.",
    ["depth"],
)

write(
    "recall/review-predict-xavier-rule.yaml",
    f'''id: review-predict-xavier-rule
type: predict_output
rev: 1
prompt: |
  The Xavier and He starting scales for layers with 4, 100 and 784 inputs. What does the program print?
code: |
{block(REVIEW_XAVIER)}expected_output: |
{block(REVIEW_XAVIER_OUT)}explanation: |
  Xavier is one over the square root of the inputs; He is that times the square root of 2, about 1.41 times larger, to make up for the half of the variance a ReLU zeroes. The scales shrink as the layer gets wider, because a wider sum has more terms to add up.
skills: [scale]
''',
)

mcq(
    "review-mcq-all-the-same-but-not-zero",
    "A teammate avoids zero starting weights by setting every weight to 0.5 instead. Does that fix the problem?",
    [
        "Yes: the units now produce nonzero outputs, so the gradients flow, the units drift apart as the data pulls on them, and training proceeds normally",
        "No: the units in each layer are still identical, so they get identical gradients and stay identical; the layer is still one unit in disguise",
        "Yes, as long as the biases are random",
        "No, because 0.5 is too large for a ReLU network and the activations explode",
    ],
    1,
    "The failure of zero starting weights is symmetry, not size: any constant makes every unit of a layer compute the same thing and take the same step forever. Random biases would break the symmetry a little, but the standard fix is random weights with a sensible scale and zero biases. Whether 0.5 is too large depends on the width; it is beside the point here.",
    ["symmetry"],
)

mcq(
    "review-mcq-why-depth-amplifies",
    "Why do frameworks apply the Xavier or He rule by default, when a two-layer network trains fine with almost any starting scale?",
    [
        "Because the rules make the first training step land exactly at the minimum",
        "Because the rules are required for the gradient check to pass",
        "Because the per-layer factor on the signal's size compounds with depth: a scale harmless twice is fatal twelve times; the rules keep the factor near 1",
        "Because random weights of any other scale would make training non-reproducible, and the rules fix the scale so that two runs with the same seed agree exactly",
    ],
    2,
    "A factor of 0.7 per layer leaves half the signal after two layers and about a hundredth after twelve, and the gradient coming back shrinks by the same product. Setting the factor to 1 at every layer, 1 over the square root of the inputs for tanh and the square root of 2 over the inputs for ReLU, is what lets a deep network start in a state where every layer has a signal and a gradient of sensible size. The gradient check and reproducibility don't depend on the scale.",
    ["depth"],
)

# =====================================================================================
# exercises
# =====================================================================================

write(
    "exercises/example-signals-through-depth/exercise.yaml",
    f'''id: example-signals-through-depth
stage: worked_example
rev: 1
title: "Signals through depth"
prompt: |
  Three starts for a small network (all zeros, four copies of one unit, random), then a ten-layer stack of 100-unit layers under six starting scales with the size of the activations and of the gradient measured layer by layer, then saturation and dead ReLUs counted, and the two rules of thumb. Press **Run**, then read how each part works.
steps:
  - label: "The classes, with a starting scale"
    lines: "{ln('class Dense:')}-{ln('drifting')}"
    note: "`Dense` now takes a `scale` for its starting weights (1 over the square root of the inputs unless told otherwise), and `Tanh` and `Sigmoid` join `ReLU`, each with its backward. `describe` turns a size into a word, so that a vanished or exploded signal reads the same on every machine."
  - label: "Zeros, copies and random"
    lines: "{ln('X = np.array([[1.0, 2.0, 0.5]')}-{ln('loss after 200 steps')}"
    note: "Started at zero, the hidden outputs are zero and no gradient reaches the first layer, so the loss stays where the last bias alone can take it, {ZERO_LOSS}. Started as four copies of one random unit, the units receive identical gradients and remain identical after 200 steps: the layer is one unit in disguise, and it learns exactly what one unit could, {CLONE_LOSS}. Random weights break the symmetry and the loss falls to {RANDOM_LOSS}."
  - label: "A ten-layer stack under six scales"
    lines: "{ln('rng = np.random.default_rng(0)')}-{ln('activations after layers 1, 5, 10')}"
    note: "Each layer multiplies the signal's size by about the scale times the square root of its 100 inputs. At 0.01 the activations vanish by layer 10 and so does the gradient reaching the input. At 1.0 the tanh units saturate near plus or minus one (their std reads stable, 0.96, only because tanh caps them at 1; the next lines count the saturation) while the gradient coming back explodes, since each layer's weights multiply it by about 10: too-large weights fail both ways. At Xavier's 0.1 the tanh stack keeps a usable size both ways. ReLU at 0.1 drifts down, because ReLU zeroes half of each layer's variance; at 0.3 it explodes; at He's 0.14 the activations and the gradient both stay stable."
  - label: "Saturation, counted"
    lines: "{ln('big = Tanh()')}-{ln('scale 1.0 with sigmoid:')}"
    note: "At scale 1.0 the pre-activations have a standard deviation of about 10, so most tanh outputs sit beyond 0.99 and most sigmoid inputs beyond 4, where the slopes are under 0.02: a gradient passing through is multiplied by almost nothing at every such layer."
  - label: "Dead ReLUs, counted"
    lines: "{ln('dead = Dense(100, 100, seed=3')}-{ln('He weights but a bias of -5')}"
    note: "With He weights but a bias of -5, a unit's pre-activation is almost never positive, so most units never fire on any of the 256 inputs. A unit that never fires has zero gradient and can't come back: that is a dead ReLU, and this is the easiest way to make one."
  - label: "The rules of thumb"
    lines: "{ln('rules of thumb:')}-{ln('rules of thumb:')}"
    note: "Xavier for tanh and sigmoid, He for ReLU, biases at zero. Frameworks apply these by default; this example is what they are protecting you from."
''',
)
write("exercises/example-signals-through-depth/solution.py", EXAMPLE)
write(
    "exercises/example-signals-through-depth/test_exercise.py",
    f'''from checks import run


def test_the_walkthrough():
    """Prints the three starts, the six scales, the two saturation fractions, the dead fraction and the rules."""
    assert run() == {EXAMPLE_OUT!r}
''',
)

write(
    "exercises/fill-he-and-xavier/exercise.yaml",
    f'''id: fill-he-and-xavier
stage: fill_in
rev: 1
title: "The two scales"
prompt: |
  `xavier_scale(n_in)` keeps a tanh or sigmoid layer's signal the same size; `he_scale(n_in)` does the same for a ReLU layer, which zeroes half of its values and so halves its mean square. Replace each `...` with the right numerator so that the program prints:

  ```
{block(FILL_OUT)}  ```

  The program fails until every `...` is replaced.
hints:
  - "Xavier's variance is 1 over the inputs: the per-layer factor scale times the square root of the inputs comes to exactly 1."
  - "He doubles that variance, because a ReLU keeps only about half of each layer's variance."
skills: [scale]
''',
)
write("exercises/fill-he-and-xavier/starter.py", FILL_STARTER)
write("exercises/fill-he-and-xavier/solution.py", FILL_SOLUTION)
write(
    "exercises/fill-he-and-xavier/test_exercise.py",
    f'''from checks import function, run


def test_the_output():
    """Prints the three scales."""
    printed = run()
    assert printed == {FILL_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_more_widths():
    """Xavier for 784 inputs is about 0.0357 and He about 0.0505; He is always sqrt(2) times Xavier."""
    xavier_scale = function("xavier_scale")
    he_scale = function("he_scale")
    assert abs(xavier_scale(784) - 0.0357) < 1e-4 and abs(he_scale(784) - 0.0505) < 1e-4
    for n_in in (1, 16, 300):
        assert abs(he_scale(n_in) / xavier_scale(n_in) - 2 ** 0.5) < 1e-12
''',
)
write("exercises/fill-he-and-xavier/wrong/he-without-the-two.py", FILL_WRONG)
write(
    "exercises/fill-he-and-xavier/wrong/typed-in.py",
    "def xavier_scale(n_in):\n    return 0.1\n\n\ndef he_scale(n_in):\n    return 0.2\n\n\n" + "".join(f"print({line!r})\n" for line in FILL_OUT.splitlines()),
)

write(
    "exercises/write-dead-and-saturated/exercise.yaml",
    f'''id: write-dead-and-saturated
stage: write
rev: 1
title: "Counting dead units and saturated inputs"
prompt: |
  Write two diagnostics. `dead_fraction(H)` takes a ReLU layer's outputs for a batch (rows are inputs, columns are units) and returns the share of units that are zero for every input in the batch. `saturated_fraction(Z, threshold=4.0)` takes a layer's pre-activations and returns the share of entries whose size is beyond the threshold (in either direction), where a sigmoid's slope is under 0.02. Called on the `H` and `Z` in the starter, the program prints:

  ```
{block(WRITE_OUT)}  ```
hints:
  - "A unit is dead for the batch when the largest value in its column is 0; `H.max(axis=0)` gives one number per unit."
  - "Size means absolute value: `np.abs(Z) > threshold` catches -6 as well as 5."
skills: [activations]
''',
)
write("exercises/write-dead-and-saturated/starter.py", "import numpy as np\n\n\n# Write dead_fraction and saturated_fraction here, above the data.\n\n\n" + WRITE_TAIL)
write("exercises/write-dead-and-saturated/solution.py", WRITE_SOLUTION)
write(
    "exercises/write-dead-and-saturated/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints the dead fraction and the two saturated fractions."""
    printed = run()
    assert printed == {WRITE_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_other_batches():
    """A unit that fires once is alive; all-zero outputs are all dead; saturation counts both signs and respects the threshold."""
    dead_fraction = function("dead_fraction")
    saturated_fraction = function("saturated_fraction")
    assert dead_fraction(np.array([[0.0, 0.0], [0.0, 0.1]])) == 0.5
    assert dead_fraction(np.zeros((5, 4))) == 1.0 and dead_fraction(np.ones((5, 4))) == 0.0
    Z = np.array([[-5.0, 5.0, 3.0, -3.0]])
    assert saturated_fraction(Z) == 0.5 and saturated_fraction(Z, threshold=2.0) == 1.0 and saturated_fraction(Z, threshold=6.0) == 0.0
''',
)
write("exercises/write-dead-and-saturated/wrong/dead-counted-per-entry.py", WRITE_DEAD_PER_ROW)
write("exercises/write-dead-and-saturated/wrong/saturated-one-sided.py", WRITE_SATURATED_UNSIGNED)
write(
    "exercises/write-dead-and-saturated/wrong/typed-in.py",
    "def dead_fraction(H):\n    return 0.5\n\n\ndef saturated_fraction(Z, threshold=4.0):\n    return 0.375\n\n\n" + "".join(f"print({line!r})\n" for line in WRITE_OUT.splitlines()),
)

# --- the proof -----------------------------------------------------------------------------------

write(
    "exercises/build-an-initialization-study/exercise.yaml",
    f'''id: build-an-initialization-study
stage: build
rev: 1
title: "An initialization study"
prompt: |
  Starting from a blank editor, write the module's classes as Layers that carry their gradient left them, with this topic's one addition (`Dense` now taking `scale=None`, meaning `1 / sqrt(n_in)`, plus `ReLU`, `Tanh` and `Sigmoid` with backward, `Sequential` and `MSELoss`), the `describe` helper from the worked example (`"vanished"` under 1e-3, `"exploded"` over 1e3, `"stable"` between 0.1 and 10, `"drifting"` otherwise), and seven tools:

  - `xavier_scale(n_in)`: `sqrt(1 / n_in)`, and `he_scale(n_in)`: `sqrt(2 / n_in)`, both as floats.
  - `activation_stds(net, X)`: the standard deviation of the batch after each layer of `net`, in order.
  - `input_gradient_std(net, X)`: run forward, push a unit-size gradient back through the network (`np.random.default_rng(1).standard_normal` in the output's shape), and return the standard deviation of the gradient that reaches the input.
  - `dead_fraction(H)`: the share of columns of `H` that are zero for every row.
  - `saturated_fraction(Z, threshold=4.0)`: the share of entries of `Z` beyond the threshold in size.
  - `units_identical(W)`: whether every column of `W` is the same column.

  Then print:

  ```python
  rng = np.random.default_rng(0)
  X = rng.standard_normal((256, 100))


  def stack(scale, activation, depth=8):
      return Sequential([piece for i in range(depth) for piece in (Dense(100, 100, seed=i, scale=scale), activation())])


  print(xavier_scale(100), he_scale(100), he_scale(50))
  for name, scale, activation in (("0.01 tanh", 0.01, Tanh), ("Xavier tanh", xavier_scale(100), Tanh), ("0.1 ReLU", 0.1, ReLU), ("He ReLU", he_scale(100), ReLU)):
      net = stack(scale, activation)
      stds = activation_stds(net, X)
      print(name, describe(stds[-1]), describe(input_gradient_std(net, X)))
  layer = Dense(100, 100, seed=3, scale=he_scale(100))
  layer.b[:] = -5.0
  print(round(dead_fraction(ReLU().forward(layer.forward(X))), 2), round(saturated_fraction(Dense(100, 100, seed=0, scale=1.0).forward(X)), 2))
  print(units_identical(np.zeros((3, 4))), units_identical(np.tile(np.array([[1.0], [2.0]]), (1, 5))), units_identical(Dense(3, 4, seed=1).W))
  ```

  ```
{block(BUILD_OUT)}  ```

  The checks compare the scales with the formulas, run a six-layer stack under He and under 0.01 and read the sizes off, check the gradient's size the same way, count dead units and saturated entries on hand-made arrays, and tell copied columns from a constant matrix.
skills: [symmetry, scale, activations, depth]
''',
)
write("exercises/build-an-initialization-study/starter.py", "")
write("exercises/build-an-initialization-study/solution.py", BUILD_SOLUTION)
write(
    "exercises/build-an-initialization-study/test_exercise.py",
    f'''import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints the seven lines."""
    assert run() == {BUILD_OUT!r}


def test_scales():
    """Xavier and He match their formulas for several widths."""
    xavier_scale = function("xavier_scale")
    he_scale = function("he_scale")
    for n_in in (2, 50, 784):
        assert abs(xavier_scale(n_in) - (1 / n_in) ** 0.5) < 1e-12 and abs(he_scale(n_in) - (2 / n_in) ** 0.5) < 1e-12


def test_sizes_through_depth():
    """A six-layer ReLU stack under He keeps activations and the input gradient between 0.1 and 10; under 0.01 both fall below 1e-3."""
    Dense = function("Dense")
    ReLU = function("ReLU")
    Sequential = function("Sequential")
    activation_stds = function("activation_stds")
    input_gradient_std = function("input_gradient_std")
    he_scale = function("he_scale")
    X = np.random.default_rng(1).standard_normal((128, 64))
    good = Sequential([piece for i in range(6) for piece in (Dense(64, 64, seed=i, scale=he_scale(64)), ReLU())])
    stds = activation_stds(good, X)
    assert len(stds) == 12 and 0.1 <= stds[-1] <= 10 and 0.1 <= input_gradient_std(good, X) <= 10
    bad = Sequential([piece for i in range(6) for piece in (Dense(64, 64, seed=i, scale=0.01), ReLU())])
    assert activation_stds(bad, X)[-1] < 1e-3 and input_gradient_std(bad, X) < 1e-3


def test_counts():
    """Dead units are columns that never fire; saturation counts both signs; identical columns are not the same as a constant matrix."""
    dead_fraction = function("dead_fraction")
    saturated_fraction = function("saturated_fraction")
    units_identical = function("units_identical")
    assert dead_fraction(np.array([[0.0, 0.0, 1.0], [0.0, 2.0, 0.0]])) == 1 / 3
    assert saturated_fraction(np.array([[-5.0, 5.0, 3.0, -3.0]])) == 0.5 and saturated_fraction(np.array([[-5.0, 5.0, 3.0, -3.0]]), threshold=2.5) == 1.0
    assert units_identical(np.tile(np.array([[0.3], [-0.7], [0.1]]), (1, 6))) and not units_identical(np.array([[1.0, 2.0], [1.0, 2.0]]))
    assert units_identical(np.full((3, 3), 0.5))
''',
)
for key, code in BUILD_WRONGS.items():
    write(f"exercises/build-an-initialization-study/wrong/{key}.py", code)
write(
    "exercises/build-an-initialization-study/wrong/typed-in.py",
    "import numpy as np\n\n\ndef xavier_scale(n_in):\n    return 0.1\n\n\ndef he_scale(n_in):\n    return 0.1414\n\n\ndef activation_stds(net, X):\n    return [1.0]\n\n\ndef input_gradient_std(net, X):\n    return 1.0\n\n\ndef dead_fraction(H):\n    return 1.0\n\n\ndef saturated_fraction(Z, threshold=4.0):\n    return 0.7\n\n\ndef units_identical(W):\n    return True\n\n\n"
    + "".join(f"print({line!r})\n" for line in BUILD_OUT.splitlines()),
)

write(
    "exercises/debug-a-network-that-will-not-learn/exercise.yaml",
    f'''id: debug-a-network-that-will-not-learn
stage: debug
rev: 1
title: "A network that won't learn"
prompt: |
  A `[3, 8, 1]` ReLU network trained for 300 steps on six rows. It should print:

  ```
{block(DEBUG_OUT)}  ```

  It has two bugs, both in how the hidden layer starts. Run it: the loss doesn't fall by more than half, the hidden units are identical and all 8 read dead, because the hidden layer's weights start at **zero** (`scale=0.0`), so every unit is a copy of every other and no gradient reaches them; start them random at He's scale, `sqrt(2 / 3)` for 3 inputs. Fix that, and the units are distinct but all 8 are still **dead**: their biases start at -5, so no unit's pre-activation is ever positive and no gradient ever reaches their weights. Biases start at 0.
skills: [symmetry, activations]
''',
)
write("exercises/debug-a-network-that-will-not-learn/starter.py", DEBUG_STARTER)
write("exercises/debug-a-network-that-will-not-learn/solution.py", DEBUG_SOLUTION)
write(
    "exercises/debug-a-network-that-will-not-learn/test_exercise.py",
    f'''import numpy as np

from checks import function, run

EXPECTED = {DEBUG_OUT!r}


def test_the_output():
    """Prints a loss that fell by half, distinct hidden units and no dead ones."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\\n{{EXPECTED}}\\nYour program printed:\\n{{printed}}"


def test_the_starting_layer():
    """A fresh Dense(3, 8) at He's scale has distinct columns, zero biases and a spread near sqrt(2 / 3)."""
    Dense = function("Dense")
    layer = Dense(3, 8, seed=4, scale=np.sqrt(2 / 3))
    assert not np.allclose(layer.W, layer.W[:, :1]) and np.array_equal(layer.b, np.zeros(8))
    assert 0.3 < layer.W.std() < 1.6
''',
)
write("exercises/debug-a-network-that-will-not-learn/wrong/still-zero.py", DEBUG_STILL_ZERO)
write("exercises/debug-a-network-that-will-not-learn/wrong/still-dead.py", DEBUG_STILL_BIAS)
write(
    "exercises/debug-a-network-that-will-not-learn/wrong/typed-in.py",
    "import numpy as np\n\n\nclass Dense:\n    def __init__(self, n_in, n_out, seed=0, scale=None):\n        self.W = np.zeros((n_in, n_out))\n        self.b = np.zeros(n_out)\n\n\n" + "".join(f"print({line!r})\n" for line in DEBUG_OUT.splitlines()),
)

write(
    "exercises/review-start-weights/exercise.yaml",
    f'''id: review-start-weights
stage: review_code
rev: 1
title: "Starting weights, from memory"
prompt: |
  Write `xavier_scale(n_in)`, `he_scale(n_in)` and `start_weights(n_in, n_out, activation, seed=0)`, which returns `(W, b)`: `W` standard normals from `np.random.default_rng(seed)` times He's scale if `activation` is `"relu"` and Xavier's otherwise, `b` zeros. Print the shape, whether the biases are all zero and the spread of the weights (rounded to 2 places) for a ReLU layer of 100 inputs and 50 outputs with seed 1, then the spread for the same layer with tanh:

  ```
{block(REVIEW_CODE_OUT)}  ```
skills: [scale]
''',
)
write("exercises/review-start-weights/starter.py", "")
write("exercises/review-start-weights/solution.py", REVIEW_CODE_SOLUTION)
write(
    "exercises/review-start-weights/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints the shape, the zero biases and the two spreads."""
    assert run() == {REVIEW_CODE_OUT!r}


def test_the_rule():
    """ReLU gets sqrt(2) times the tanh scale, the biases are zero, and the same seed gives the same weights."""
    start_weights = function("start_weights")
    W_relu, b = start_weights(64, 32, "relu", seed=2)
    W_tanh, _ = start_weights(64, 32, "tanh", seed=2)
    assert np.array_equal(b, np.zeros(32)) and np.allclose(W_relu, W_tanh * 2 ** 0.5)
    assert np.array_equal(W_relu, start_weights(64, 32, "relu", seed=2)[0])
''',
)
write("exercises/review-start-weights/wrong/always-xavier.py", REVIEW_CODE_WRONG)
write(
    "exercises/review-start-weights/wrong/typed-in.py",
    "def start_weights(n_in, n_out, activation, seed=0):\n    return None, None\n\n\n" + "".join(f"print({line!r})\n" for line in REVIEW_CODE_OUT.splitlines()),
)

print("ml.nn.initialization-and-activations written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
