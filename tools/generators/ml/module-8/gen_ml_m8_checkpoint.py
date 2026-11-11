"""Writes Checkpoint 8, ml.m8.checkpoint: a network that reads digits. Run
from the repository root under uv (python -m uv run python <this file>), so
every program's expected output is captured from CPython rather than typed
in. The digits are a 5-by-7 pixel font drawn into 10-by-10 images at a
random one-pixel shift with Gaussian noise, so no dataset is downloaded;
accuracies are pinned to two decimals and the generator checks that a
tenth-decimal nudge of one pixel leaves every printed line unchanged, while
the hidden tests hold the learner's network to an accuracy bar rather than
to those digits. Files are written as bytes with LF endings."""

import pathlib
import subprocess
import sys

ROOT = pathlib.Path("content/topics/ml.m8.checkpoint")


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


# =====================================================================================
# The module's code, as the seven topics left it.
# =====================================================================================

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
            grad = grad + self.weight_decay * param
            self.m[i] = self.beta1 * self.m[i] + (1 - self.beta1) * grad
            self.v[i] = self.beta2 * self.v[i] + (1 - self.beta2) * grad ** 2
            m_hat = self.m[i] / (1 - self.beta1 ** self.t)
            v_hat = self.v[i] / (1 - self.beta2 ** self.t)
            param -= self.rate * m_hat / (np.sqrt(v_hat) + self.eps)
'''

LOOP = '''

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
'''

DATA = '''

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
'''

DIGITS = {
    "0": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "1": ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "2": [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
    "3": ["####.", "....#", "....#", ".###.", "....#", "....#", "####."],
    "4": ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
    "5": ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    "6": [".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."],
    "7": ["#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."],
    "8": [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
    "9": [".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."],
}
LETTERS = {
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "C": [".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
}
SYMBOLS = {
    "+": [".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."],
    "-": [".....", ".....", ".....", "#####", ".....", ".....", "....."],
    "x": [".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "....."],
    "/": ["....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."],
    "#": ["#####", "#...#", "#...#", "#...#", "#...#", "#...#", "#####"],
    "o": [".....", ".....", ".###.", "#...#", ".###.", ".....", "....."],
}
SHAPES = {
    "bar": [".....", ".....", ".....", "#####", ".....", ".....", "....."],
    "post": ["..#..", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "cross": [".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."],
    "box": ["#####", "#...#", "#...#", "#...#", "#...#", "#...#", "#####"],
}
for font in (DIGITS, LETTERS, SYMBOLS, SHAPES):
    for rows in font.values():
        assert len(rows) == 7 and all(len(row) == 5 for row in rows)


def glyph_literal(name: str, font: dict[str, list[str]]) -> str:
    """The font as a Python dict literal, one glyph per line."""
    lines = [f"{name} = {{"]
    for key, rows in font.items():
        lines.append(f"    {key!r}: [" + ", ".join(repr(row) for row in rows) + "],")
    lines.append("}")
    return "\n".join(lines) + "\n"


def pipeline(font_name: str, font: dict[str, list[str]], maker: str, noun: str) -> str:
    """The program that trains on a font and prints the four lines: the data, the gradient check, the accuracy and the double evaluation, then what it reads."""
    n_classes = len(font)
    return (
        "import numpy as np\n\n\n"
        + LAYERS
        + LOOP
        + DATA
        + "\n\n"
        + glyph_literal(font_name, font)
        + f'''

def {maker}(n_per_class, seed):
    """n_per_class noisy, shifted images of each {noun}, with labels in font order."""
    return make_images({font_name}, n_per_class, seed)


X_train, y_train = {maker}(60, seed=1)
X_val, y_val = {maker}(20, seed=2)
loss = SoftmaxCrossEntropy()
print(X_train.shape, X_val.shape, np.bincount(y_val).tolist())
tiny = Sequential([Conv2D(2, 3, seed=1), ReLU(), MaxPool2D(2), Flatten(), Dense(32, {n_classes}, seed=2)])
print("gradient check:", "passes" if gradient_check(tiny, loss, X_train[:4], y_train[:4]) < 1e-6 else "fails")
net = Sequential([Conv2D(6, 3, seed=1), ReLU(), MaxPool2D(2), Flatten(), Dropout(0.2, seed=5), Dense(96, {n_classes}, seed=2)])
history = fit(net, loss, Adam(0.01, weight_decay=1e-4), X_train, y_train, X_val, y_val, epochs=20)
accuracy = history["val_accuracy"][-1]
print(f"loss {{history['train_loss'][0]:.2f}} -> {{history['train_loss'][-1]:.2f}} | held-out accuracy {{accuracy:.2f}} | at least 0.9: {{accuracy >= 0.9}} | {{sum(p.size for p in net.parameters())}} parameters")
print("evaluating twice gives the same answer:", evaluate(net, loss, X_val, y_val)[0] == evaluate(net, loss, X_val, y_val)[0])
names = list({font_name})
net.eval()
print("the first held-out image of each {noun} reads:", " ".join(names[i] for i in net.forward(X_val[::20]).argmax(axis=1)))
'''
    )


def check_pipeline(program: str, n_classes: int, names: list[str]) -> str:
    """Runs a pipeline, asserts its story and that a nudge of one pixel leaves it unchanged; returns the output."""
    printed = out(program)
    lines = printed.splitlines()
    assert len(lines) == 5, printed
    assert lines[0] == f"({60 * n_classes}, 10, 10) ({20 * n_classes}, 10, 10) {[20] * n_classes}", lines[0]
    assert lines[1] == "gradient check: passes", lines[1]
    assert "| at least 0.9: True |" in lines[2], lines[2]
    assert lines[3] == "evaluating twice gives the same answer: True", lines[3]
    read = lines[4].split("reads: ")[1].split(" ")
    assert sum(a == b for a, b in zip(read, names)) >= n_classes - 1, lines[4]
    nudged = program.replace("X_val, y_val = ", "X_val, y_val = ", 1).replace("loss = SoftmaxCrossEntropy()\nprint(X_train.shape", "X_train[0, 0, 0] += 1e-10\nloss = SoftmaxCrossEntropy()\nprint(X_train.shape", 1)
    assert nudged != program
    assert out(nudged) == printed, "a tenth-decimal nudge changed a printed line"
    return printed


BUILD = pipeline("DIGITS", DIGITS, "make_digits", "digit")
BUILD_OUT = check_pipeline(BUILD, 10, list(DIGITS))
print("build:\n" + BUILD_OUT)
BUILD_ACC = BUILD_OUT.splitlines()[2].split("accuracy ")[1].split(" |")[0]
LETTERS_BUILD = pipeline("LETTERS", LETTERS, "make_letters", "letter")
LETTERS_OUT = check_pipeline(LETTERS_BUILD, 8, list(LETTERS))
print("letters:\n" + LETTERS_OUT)
SYMBOLS_BUILD = pipeline("SYMBOLS", SYMBOLS, "make_symbols", "symbol")
SYMBOLS_OUT = check_pipeline(SYMBOLS_BUILD, 6, list(SYMBOLS))
print("symbols:\n" + SYMBOLS_OUT)
EXAMPLE = pipeline("SHAPES", SHAPES, "make_shapes", "shape")
EXAMPLE_OUT = check_pipeline(EXAMPLE, 4, list(SHAPES))
print("example:\n" + EXAMPLE_OUT)
EXAMPLE_ACC = EXAMPLE_OUT.splitlines()[2].split("accuracy ")[1].split(" |")[0]
EXAMPLE_LINES = EXAMPLE.splitlines()


def ln(text: str, after: int = 0) -> int:
    return next(i + 1 for i, line in enumerate(EXAMPLE_LINES) if i + 1 > after and text in line)


# Known-wrongs for every build: the planted mistakes the module's topics taught against.
def build_wrongs(program: str) -> dict[str, str]:
    wrongs = {
        "dw-from-the-first-row-only": program.replace("        self.dW = self.X.T @ grad_out", "        self.dW = self.X.T[:, :1] @ grad_out[:1]"),
        "relu-passes-everything": program.replace("        return grad_out * self.mask", "        return grad_out"),
        "dropout-on-at-evaluation": program.replace('    """The loss and the accuracy on a set, with dropout off and no update."""\n    net.eval()\n', '    """The loss and the accuracy on a set, with dropout off and no update."""\n'),
        "conv-kernel-transposed-going-back": program.replace("(grad_out * self.W[None, :, i, j, None, None]).sum(axis=1)", "(grad_out * self.W[None, :, j, i, None, None]).sum(axis=1)"),
        "pool-spreads-the-gradient": program.replace("        spread = self.mask * grad_out[:, :, :, None, :, None]", "        spread = np.ones_like(self.mask) * grad_out[:, :, :, None, :, None]"),
        "decay-pushes-outwards": program.replace("            grad = grad + self.weight_decay * param", "            grad = grad - self.weight_decay * param"),
        "never-shuffles": program.replace("    order = rng.permutation(n)\n", "    order = np.arange(n)\n"),
        "weights-start-at-zero": program.replace("        self.W = rng.standard_normal((n_in, n_out)) * self.scale", "        self.W = np.zeros((n_in, n_out))").replace("        self.W = rng.standard_normal((n_kernels, k, k)) * self.scale", "        self.W = np.zeros((n_kernels, k, k))"),
    }
    for key, code in wrongs.items():
        assert code != program, key
    return wrongs


# =====================================================================================
# The debug: three bugs in the digits script.
# =====================================================================================

DEBUG_SOLUTION = (
    "import numpy as np\n\n\n"
    + '''def start_weights(rng, shape, fan_in):
    """A small random start, scaled by the fan-in, so the signal neither vanishes nor explodes and no two units begin alike."""
    return rng.standard_normal(shape) / np.sqrt(fan_in)


'''
    + LAYERS.replace("        self.scale = 1 / np.sqrt(n_in) if scale is None else scale\n        self.W = rng.standard_normal((n_in, n_out)) * self.scale\n", "        self.W = start_weights(rng, (n_in, n_out), n_in)\n").replace("        self.scale = 1 / k if scale is None else scale\n        self.W = rng.standard_normal((n_kernels, k, k)) * self.scale\n", "        self.W = start_weights(rng, (n_kernels, k, k), k * k)\n")
    + LOOP
    + DATA
    + "\n\n"
    + glyph_literal("DIGITS", DIGITS)
    + '''
RATE = 0.01

X_train, y_train = make_images(DIGITS, 60, seed=1)
X_val, y_val = make_images(DIGITS, 20, seed=2)
loss = SoftmaxCrossEntropy()
net = Sequential([Conv2D(6, 3, seed=1), ReLU(), MaxPool2D(2), Flatten(), Dropout(0.2, seed=5), Dense(96, 10, seed=2)])
history = fit(net, loss, Adam(RATE, weight_decay=1e-4), X_train, y_train, X_val, y_val, epochs=20)
accuracy = history["val_accuracy"][-1]
print(f"loss {history['train_loss'][0]:.2f} -> {history['train_loss'][-1]:.2f} | held-out accuracy {accuracy:.2f} | at least 0.9: {accuracy >= 0.9}")
print("evaluating twice gives the same answer:", evaluate(net, loss, X_val, y_val)[0] == evaluate(net, loss, X_val, y_val)[0])
'''
)
assert "scale=None" in DEBUG_SOLUTION and "self.scale" not in DEBUG_SOLUTION.split("class Dense")[1].split("class ReLU")[0]
BUG_ZERO = ("    return rng.standard_normal(shape) / np.sqrt(fan_in)\n", "    return np.zeros(shape)\n")
BUG_EVAL = ('    """The loss and the accuracy on a set, with dropout off and no update."""\n    net.eval()\n', '    """The loss and the accuracy on a set, with dropout off and no update."""\n')
BUG_RATE = ("RATE = 0.01\n", "RATE = 0.1\n")
for old, new in (BUG_ZERO, BUG_EVAL, BUG_RATE):
    assert DEBUG_SOLUTION.count(old) == 1, old
DEBUG_STARTER = DEBUG_SOLUTION.replace(*BUG_ZERO).replace(*BUG_EVAL).replace(*BUG_RATE)
DEBUG_STILL_ZERO = DEBUG_SOLUTION.replace(*BUG_ZERO)
DEBUG_STILL_EVAL = DEBUG_SOLUTION.replace(*BUG_EVAL)
DEBUG_STILL_RATE = DEBUG_SOLUTION.replace(*BUG_RATE)
DEBUG_AFTER_ZERO = DEBUG_SOLUTION.replace(*BUG_EVAL).replace(*BUG_RATE)
DEBUG_AFTER_RATE = DEBUG_SOLUTION.replace(*BUG_EVAL)
DEBUG_OUT = out(DEBUG_SOLUTION)
STARTER_OUT = out(DEBUG_STARTER)
AFTER_ZERO_OUT = out(DEBUG_AFTER_ZERO)
AFTER_RATE_OUT = out(DEBUG_AFTER_RATE)
print("debug:\n" + DEBUG_OUT + "starter:\n" + STARTER_OUT + "after the zero fix:\n" + AFTER_ZERO_OUT + "after the rate fix:\n" + AFTER_RATE_OUT)
assert DEBUG_OUT.splitlines()[0].startswith("loss ") and "| at least 0.9: True" in DEBUG_OUT and DEBUG_OUT.endswith("evaluating twice gives the same answer: True\n"), DEBUG_OUT
assert STARTER_OUT.startswith("loss 2.31 -> 2.30 | held-out accuracy 0.10 | at least 0.9: False\n"), STARTER_OUT
assert "at least 0.9: False" in AFTER_ZERO_OUT and AFTER_ZERO_OUT.endswith("same answer: False\n"), AFTER_ZERO_OUT
assert AFTER_RATE_OUT.endswith("same answer: False\n"), AFTER_RATE_OUT
assert all(differs(code, DEBUG_OUT) for code in (DEBUG_STILL_ZERO, DEBUG_STILL_EVAL, DEBUG_STILL_RATE))
STARTER_ACC = STARTER_OUT.splitlines()[0].split("accuracy ")[1].split(" |")[0]
AFTER_ZERO_ACC = AFTER_ZERO_OUT.splitlines()[0].split("accuracy ")[1].split(" |")[0]
AFTER_ZERO_LAST = AFTER_ZERO_OUT.splitlines()[0].split("-> ")[1].split(" |")[0]
AFTER_RATE_ACC = AFTER_RATE_OUT.splitlines()[0].split("accuracy ")[1].split(" |")[0]
DEBUG_ACC = DEBUG_OUT.splitlines()[0].split("accuracy ")[1].split(" |")[0]
STILL_RATE_OUT = out(DEBUG_STILL_RATE)
STILL_RATE_ACC = STILL_RATE_OUT.splitlines()[0].split("accuracy ")[1].split(" |")[0]
assert "at least 0.9: False" in STILL_RATE_OUT and STILL_RATE_OUT.endswith("same answer: True\n"), STILL_RATE_OUT
DEBUG_LAST = DEBUG_OUT.splitlines()[0].split("-> ")[1].split(" |")[0]

# =====================================================================================
# The steps: four fill-ins, each one piece of the build.
# =====================================================================================

STEP_LAYERS = (
    "import numpy as np\n\n\n"
    + LAYERS.split("class Dropout:")[0].rstrip("\n")
    + "\n\n\n"
    + "class Sequential:" + LAYERS.split("class Sequential:")[1].split("class Conv2D:")[0].rstrip("\n")
    + "\n\n\n"
    + "class SoftmaxCrossEntropy:" + LAYERS.split("class SoftmaxCrossEntropy:")[1].split("class Adam:")[0].rstrip("\n")
    + "\n"
    + LOOP.split("def batches")[0].rstrip("\n")
    + '''


rng = np.random.default_rng(0)
X = rng.standard_normal((6, 5))
y = rng.integers(0, 3, size=6)
net = Sequential([Dense(5, 8, seed=1), ReLU(), Dense(8, 3, seed=2)])
loss = SoftmaxCrossEntropy()
print("gradient check:", "passes" if gradient_check(net, loss, X, y) < 1e-6 else "fails")
print(sum(p.size for p in net.parameters()), net.forward(X).shape)
'''
)
STEP_LAYERS_STARTER = STEP_LAYERS.replace("        self.dW = self.X.T @ grad_out\n        self.db = grad_out.sum(axis=0)\n        return grad_out @ self.W.T", "        self.dW = ... @ grad_out\n        self.db = grad_out.sum(axis=...)\n        return grad_out @ ...").replace("        return grad_out * self.mask\n\n    def parameters(self):\n        return []\n\n    def gradients(self):\n        return []\n\n\nclass Sequential", "        return grad_out * ...\n\n    def parameters(self):\n        return []\n\n    def gradients(self):\n        return []\n\n\nclass Sequential")
assert STEP_LAYERS_STARTER.count("...") == 4, STEP_LAYERS_STARTER.count("...")
STEP_LAYERS_OUT = out(STEP_LAYERS)
assert STEP_LAYERS_OUT == "gradient check: passes\n75 (6, 3)\n", STEP_LAYERS_OUT
STEP_LAYERS_WRONG = STEP_LAYERS.replace("        self.dW = self.X.T @ grad_out", "        self.dW = (grad_out.T @ self.X).T * 0.5")
assert differs(STEP_LAYERS_WRONG, STEP_LAYERS_OUT)

STEP_CONV = (
    "import numpy as np\n\n\n"
    + LAYERS.split("class Dropout:")[0].rstrip("\n")
    + "\n\n\n"
    + "class Sequential:" + LAYERS.split("class Sequential:")[1].split("class Adam:")[0].rstrip("\n")
    + "\n"
    + LOOP.split("def batches")[0].rstrip("\n")
    + '''


rng = np.random.default_rng(0)
X = rng.standard_normal((3, 8, 8))
y = rng.integers(0, 4, size=3)
net = Sequential([Conv2D(2, 3, seed=1), ReLU(), MaxPool2D(2), Flatten(), Dense(18, 4, seed=2)])
loss = SoftmaxCrossEntropy()
print(net.forward(X).shape, "| gradient check:", "passes" if gradient_check(net, loss, X, y) < 1e-6 else "fails")
loss.forward(net.forward(X), y)
grad_in = net.backward(loss.backward())
numeric = numeric_gradient(lambda: loss.forward(net.forward(X), y), X)
print("input gradient:", "passes" if np.abs(grad_in - numeric).max() < 1e-6 else "fails")
'''
)
STEP_CONV_STARTER = STEP_CONV.replace("                self.dW[:, i, j] = (grad_out * patch[:, None]).sum(axis=(0, 2, 3))\n                grad_in[:, i : i + h_out, j : j + w_out] += (grad_out * self.W[None, :, i, j, None, None]).sum(axis=1)", "                self.dW[:, i, j] = (grad_out * ...[:, None]).sum(axis=(0, 2, 3))\n                grad_in[:, i : i + h_out, j : j + w_out] += (grad_out * self.W[None, :, ..., ..., None, None]).sum(axis=1)").replace("        spread = self.mask * grad_out[:, :, :, None, :, None]", "        spread = ... * grad_out[:, :, :, None, :, None]")
assert STEP_CONV_STARTER.count("...") == 4, STEP_CONV_STARTER.count("...")
STEP_CONV_OUT = out(STEP_CONV)
assert STEP_CONV_OUT == "(3, 4) | gradient check: passes\ninput gradient: passes\n", STEP_CONV_OUT
STEP_CONV_WRONG = STEP_CONV.replace("(grad_out * self.W[None, :, i, j, None, None]).sum(axis=1)", "(grad_out * self.W[None, :, j, i, None, None]).sum(axis=1)")
assert differs(STEP_CONV_WRONG, STEP_CONV_OUT)

STEP_LOSS = (
    "import numpy as np\n\n\n"
    + "class SoftmaxCrossEntropy:" + LAYERS.split("class SoftmaxCrossEntropy:")[1].rstrip("\n")
    + '''


logits = np.array([[2.0, 0.0, -1.0], [0.0, 0.0, 0.0], [1000.0, 0.0, 0.0]])
labels = np.array([0, 1, 0])
loss = SoftmaxCrossEntropy()
print(round(loss.forward(logits, labels), 4), np.round(loss.backward()[1], 4).tolist())
W = np.array([2.0, -1.0, 0.5])
optimizer = Adam(0.1, weight_decay=0.5)
for step in range(3):
    optimizer.step([W], [np.zeros(3)])
print(np.round(W, 2).tolist())
'''
)
STEP_LOSS_STARTER = STEP_LOSS.replace("        grad = self.probs.copy()\n        grad[np.arange(len(self.labels)), self.labels] -= 1\n        return grad / len(self.labels)", "        grad = self.probs.copy()\n        grad[np.arange(len(self.labels)), self.labels] -= ...\n        return grad / ...").replace("            grad = grad + self.weight_decay * param\n", "            grad = grad + ... * param\n")
assert STEP_LOSS_STARTER.count("...") == 3, STEP_LOSS_STARTER.count("...")
STEP_LOSS_OUT = out(STEP_LOSS)
print("step loss:\n" + STEP_LOSS_OUT)
STEP_LOSS_LINES = STEP_LOSS_OUT.splitlines()
assert len(STEP_LOSS_LINES) == 2 and STEP_LOSS_LINES[0] == "0.4228 [0.1111, -0.2222, 0.1111]" and STEP_LOSS_LINES[1] == "[1.7, -0.7, 0.2]", STEP_LOSS_OUT
STEP_LOSS_WRONG = STEP_LOSS.replace("        return grad / len(self.labels)", "        return grad")
assert differs(STEP_LOSS_WRONG, STEP_LOSS_OUT)

STEP_TRAIN = (
    "import numpy as np\n\n\n"
    + LAYERS
    + LOOP
    + DATA
    + "\n\n"
    + glyph_literal("SHAPES", SHAPES)
    + '''
X_train, y_train = make_images(SHAPES, 60, seed=1)
X_val, y_val = make_images(SHAPES, 20, seed=2)
loss = SoftmaxCrossEntropy()
net = Sequential([Conv2D(6, 3, seed=1), ReLU(), MaxPool2D(2), Flatten(), Dropout(0.2, seed=5), Dense(96, 4, seed=2)])
history = fit(net, loss, Adam(0.01, weight_decay=1e-4), X_train, y_train, X_val, y_val, epochs=20)
dropout = net.layers[4]
print("held-out accuracy at least 0.9:", history["val_accuracy"][-1] >= 0.9, "| dropout off after evaluate:", dropout.training is False)
net.train()
print("dropout on after train:", dropout.training is True, "| evaluating twice gives the same answer:", evaluate(net, loss, X_val, y_val)[0] == evaluate(net, loss, X_val, y_val)[0])
'''
)
STEP_TRAIN_STARTER = STEP_TRAIN.replace('    """The loss and the accuracy on a set, with dropout off and no update."""\n    net.eval()\n', '    """The loss and the accuracy on a set, with dropout off and no update."""\n    net....()\n').replace("    for epoch in range(epochs):\n        net.train()\n", "    for epoch in range(epochs):\n        net....()\n")
assert STEP_TRAIN_STARTER.count("net....()") == 2, STEP_TRAIN_STARTER.count("net....()")  # the font's rows are dots too
STEP_TRAIN_OUT = out(STEP_TRAIN)
assert STEP_TRAIN_OUT == "held-out accuracy at least 0.9: True | dropout off after evaluate: True\ndropout on after train: True | evaluating twice gives the same answer: True\n", STEP_TRAIN_OUT
STEP_TRAIN_WRONG = STEP_TRAIN.replace('    """The loss and the accuracy on a set, with dropout off and no update."""\n    net.eval()\n', '    """The loss and the accuracy on a set, with dropout off and no update."""\n    net.train()\n')
assert differs(STEP_TRAIN_WRONG, STEP_TRAIN_OUT)

# =====================================================================================
# topic.yaml
# =====================================================================================

write(
    "topic.yaml",
    '''id: ml.m8.checkpoint
kind: checkpoint
status: ready
title: "Checkpoint 8: a network that reads digits"
summary: "Build the layers, the loss, the training loop and the regularizers from the module, train a small network on noisy, shifted images of the ten digits, reach the accuracy bar on images it hasn't seen, and find three bugs in a training script that won't learn."
prerequisites: [ml.nn.regularization, ml.nn.convolution, ml.nn.debugging-training]
packages: [numpy]
estimated_minutes: 150
rev: 1
objectives:
  - "Build dense and convolutional layers with forward and backward passes, softmax cross-entropy, and a mini-batch training loop with Adam, weight decay and dropout, and gradient-check the pieces."
  - "Train the network on the module's digit images, with a seed, to at least the accuracy bar on a held-out set, within the time the browser allows."
  - "Find and fix three bugs in a training script that won't learn (weights started at zero, dropout left on at evaluation, a learning rate ten times too high), and explain backpropagation and regularization in your own words."
prove:
  build: build-a-network-that-reads-digits
  debug: debug-a-script-that-will-not-learn
  explain:
    prompt: |
      Your digit reader is in code review. The reviewer asks four things. First: "walk me through one training step: what does each layer store on the way forward, and what does backward do at each layer boundary to get from the loss to the kernel's nine numbers, which are used at every position of every image?" Second: "how do you know the gradients are right, and why did you run that check with dropout off?" Third: "what are the weight decay, the dropout and the held-out set each protecting against, what does each assume, and when would you take one out?" Fourth: "the script you fixed had its weights at zero, its dropout on at evaluation and its rate ten times too high: what did each one look like from the outside, and how did you tell them apart?" In your own words, answer all four.
    rubric:
      - id: backprop
        required: true
        description: "Forward, each layer stores what backward will need (Dense its input, ReLU its mask, the pool which cell won, dropout its mask, the loss its probabilities); backward starts from the loss's gradient (probabilities minus one-hot labels, over the batch) and each layer multiplies by its own local derivative and hands the result to the layer below (the chain rule at a boundary), setting its parameter gradients on the way. A kernel weight used at every position gets the sum over all of them, and a weight used by every row of the batch gets the sum over the rows."
      - id: gradient-check
        required: true
        description: "A central difference of the loss, nudging each parameter up and down, is compared with backward's gradient and the largest gap must be below about a millionth. Dropout draws a fresh random mask on every forward pass in training mode, so the function would change between the two evaluations and the check would fail for no reason; eval mode fixes the function."
      - id: regularization
        required: true
        description: "All three protect against fitting the training rows' noise. Weight decay pulls every weight towards zero so only weights the data keeps pushing stay large (assumes smooth, small-weight models are better; remove it when the network underfits). Dropout makes units redundant (assumes redundancy helps; remove it from small layers or when training is already too slow). The held-out set measures generalization and chooses when to stop; it assumes it comes from the same source as the training rows and is never trained on."
      - id: three-bugs
        required: true
        description: "Zero weights: the loss sits at log 10, 2.30, and accuracy at a tenth, because no gradient reaches any weight (every hidden value is zero) and only the output bias moves. Dropout on at evaluation: two evaluations of the same network give two different numbers, and the accuracy is lower than the network's. A rate ten times too high: the run learns something but ends short of the bar, each step overshooting. They are told apart by the first loss and whether it moves, the double evaluation, and the accuracy against the bar at a rate known to be sane, in that order."
    model_answer: |
      One training step runs the batch forward and the gradient backward. Going forward, each layer keeps what it will need: the dense layer keeps its input, because its weight gradient is that input transposed times the gradient from above; the ReLU keeps a mask of where its input was positive, because that is where it passes gradient; the pool keeps which cell of each window won, because only that cell affected the output; dropout keeps the random mask it applied and the scaling by one over one minus p; the loss keeps the softmax probabilities. Backward begins at the loss, whose gradient with respect to the logits is the probabilities minus the one-hot labels, divided by the batch size, and then each layer does one thing: it multiplies the gradient it receives by its own local derivative and passes the result down, setting its parameter gradients on the way. That is the chain rule applied at each boundary, and no layer needs to know what the others do. At the convolution the nine numbers of a kernel were used at every output position of every image, so the gradient for weight (i, j) is the sum, over all positions and all images in the batch, of the output gradient there times the input pixel that weight multiplied, which is itself a correlation of the input with the output gradient; and the gradient for the input spreads each output cell's gradient back over its patch through the kernel's weights. The dense layer's weights, used by every row of the batch, likewise get a sum over rows. I know the gradients are right because of the numeric check: nudge each parameter up and down by a millionth, measure the loss both times, and compare the central difference with what backward computed; the largest gap in the network is below a millionth. I ran it with dropout off because in training mode dropout draws a fresh random mask on every forward pass, so the two evaluations of the nudged loss would be of two different functions and the check would fail for no reason; evaluation mode makes the network a fixed function, which is what a derivative is a derivative of. The three regularizers all guard against fitting the noise in six hundred training images. Weight decay adds a small multiple of each weight to its gradient, a steady pull towards zero, so a weight stays large only if the data keeps pushing it; it assumes that a smooth model with small weights is the better one, which is usually right, and I would take it out if the network were underfitting, since it only makes that worse. Dropout zeroes a fifth of the flattened features on every training step, scaled up to keep the expected value, so the output layer cannot rely on any one feature and learns redundant ones; it assumes redundancy helps, and I would take it out of a layer too small to spare a fifth of itself, or if training were too slow, since it slows it. The held-out set is two hundred images the network never trains on, so its accuracy measures what the network has learned about digits rather than about those six hundred images; it assumes those images come from the same source as the training ones, and the one rule is that no decision about the network trains on them. The three bugs each had a face. With the weights at zero, every hidden value was zero, so no gradient reached any weight and only the output bias moved: the loss sat at log 10, 2.30, for twenty epochs and the accuracy at a tenth, a dead-flat curve from the first loss on, which no learning rate changes. With dropout left on at evaluation, the network gave a different answer every time it was asked, because a fresh mask was drawn each time, and the answers were worse than the network's: two evaluations in a row disagreeing is the tell, and it cannot be a learning-rate or an initialization problem, since the weights don't change between the two. With the rate ten times too high, the run learned, so the weights and the data were fine, but the accuracy ended short of the bar: each step overshoots, and lowering the rate by ten is what settled it. The order I told them apart in is the checklist's: the first loss and whether it moves at all, then whether the same network gives the same answer twice, then whether the run clears the bar at a rate known to be sane.
# For a learner who's stuck on the build (ADR-0012): a solved sibling, the
# build in steps with hints, then fresh versions.
unstuck:
  example: example-a-network-that-reads-shapes
  steps: [step-the-dense-layers, step-the-convolutional-layer, step-the-loss-and-the-optimizer, step-train-and-evaluate]
  versions: [build-a-network-that-reads-letters, build-a-network-that-reads-symbols]
''',
)

# =====================================================================================
# The worked example: the same pipeline on four shapes.
# =====================================================================================

write(
    "exercises/example-a-network-that-reads-shapes/exercise.yaml",
    f'''id: example-a-network-that-reads-shapes
stage: worked_example
rev: 1
title: "A network that reads shapes"
prompt: |
  The checkpoint's whole pipeline on a smaller font: four shapes drawn into noisy 10-by-10 images at a random shift, a convolutional network with dropout, Adam with weight decay, a gradient check, twenty epochs, and the held-out accuracy. Press **Run**, then read how each part works; the checkpoint is the same pipeline on the ten digits, with the checks holding your network to the bar.
steps:
  - label: "The layers, each with forward, backward, parameters and gradients"
    lines: "{ln('class Dense:')}-{ln('return [self.dW, self.db]', ln('class Conv2D:'))}"
    note: "`Dense`, `ReLU`, `Dropout` (with its `training` flag), `Sequential` (with `train()` and `eval()` to flip every flag), `Conv2D` (one feature map per kernel, forward and backward looping over the kernel's offsets), as the module built them. Each layer stores on the way forward what backward needs: the input, the mask, the winner."
  - label: "Pooling, flattening, the loss and Adam"
    lines: "{ln('class MaxPool2D:')}-{ln('param -= self.rate * m_hat')}"
    note: "`MaxPool2D` keeps each window's maximum and routes the gradient to it; `Flatten` turns maps into rows and the gradient back; `SoftmaxCrossEntropy` is the log-sum-exp loss with `probs - onehot` over the batch as its gradient; `Adam` adds `weight_decay * param` to each gradient first, the pull towards zero."
  - label: "The gradient check, batches, evaluation and the loop"
    lines: "{ln('def numeric_gradient')}-{ln('return history')}"
    note: "`gradient_check` puts the network in eval mode first, because dropout in training mode draws a new mask on every forward pass and the function being differentiated would change between the two nudged evaluations. `evaluate` is eval mode, a forward pass and the loss, no update. `fit` switches to train mode before each step and records the losses and the held-out accuracy after each epoch."
  - label: "A font, drawn into noisy, shifted images"
    lines: "{ln('def make_images')}-{ln('return make_images(SHAPES')}"
    note: "`make_images` draws Gaussian noise for every image, then adds 1.0 to each `#` pixel of the glyph, placed at the centre of the 10-by-10 image and shifted by up to one pixel each way; the shifts come from the same seeded generator as the noise, so the data is the same on every run. Four shapes here, a bar, a post, a cross and a box; the checkpoint's font is the ten digits."
  - label: "Data, gradient check, training, the double evaluation, and what it reads"
    lines: "{ln('X_train, y_train = make_shapes(60')}-{ln('the first held-out image of each shape reads')}"
    note: "Sixty training images per shape and twenty held out. A tiny two-kernel network passes the gradient check on four images. The real network, six kernels, a pool, dropout of 0.2 and a dense layer, trains for twenty epochs of Adam at 0.01 with weight decay 0.0001 and reads {EXAMPLE_ACC} of the held-out images; evaluating it twice gives the same number, because dropout is off; and the first held-out image of each shape reads as itself."
''',
)
write("exercises/example-a-network-that-reads-shapes/solution.py", EXAMPLE)
write(
    "exercises/example-a-network-that-reads-shapes/test_exercise.py",
    f'''from checks import run


def test_the_walkthrough():
    """Prints the data, the check, the accuracy, the double evaluation and the reading."""
    assert run() == {EXAMPLE_OUT!r}
''',
)

# =====================================================================================
# The builds: digits, and the two fresh versions.
# =====================================================================================

TEST_SKILLS = '''# Every test names the module skills it checks (ADR-0012), so a failed test
# says which topics to revisit.
test_skills:
  test_the_output: [ml.nn.neurons-and-layers/compose, ml.nn.training-loop/loop, ml.nn.training-loop/validation, ml.nn.convolution/conv-layer, ml.nn.regularization/dropout]
  test_layer_gradients: [ml.nn.backward-layers/layer-backward, ml.nn.backward-layers/chain, ml.nn.convolution/conv-layer, ml.nn.convolution/shapes]
  test_loss_and_optimizer: [ml.nn.backward-layers/loss-layers, ml.nn.regularization/decay, ml.nn.training-loop/loop]
  test_dropout_and_modes: [ml.nn.regularization/dropout, ml.nn.training-loop/validation]
  test_starts_and_shapes: [ml.nn.initialization-and-activations/symmetry, ml.nn.initialization-and-activations/scale, ml.nn.neurons-and-layers/count, ml.nn.convolution/parameters]
  test_the_accuracy_bar: [ml.nn.training-loop/loop, ml.nn.training-loop/curves, ml.nn.regularization/overfitting, ml.nn.debugging-training/bug-or-hard]
'''


def build_test(expected: str, n_classes: int, maker: str, names: list[str]) -> str:
    return f'''import re

import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7). Everything is fetched from one
# import of the solution, so the classes compare equal across the tests and
# the training at the top of the file runs once per test.


def module():
    fit = function("fit")
    return fit.__globals__


def numeric(f, param, h=1e-6):
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
    """Prints the five lines: the shapes, a passing gradient check, a run over the bar with the right parameter count, a double evaluation that agrees, and the reading (the two-decimal loss and accuracy may differ with how the masks and batches are drawn)."""
    printed = run().splitlines()
    expected = {expected!r}.splitlines()
    assert len(printed) == 5 and printed[0] == expected[0] and printed[1] == expected[1] and printed[3] == expected[3]
    assert re.fullmatch(r"loss \\d+\\.\\d\\d -> \\d+\\.\\d\\d \\| held-out accuracy 0\\.\\d\\d \\| at least 0.9: True \\| {60 + 97 * n_classes} parameters", printed[2]), printed[2]
    assert printed[4].startswith(expected[4].split("reads: ")[0] + "reads: ")
    assert sum(a == b for a, b in zip(printed[4].split("reads: ")[1].split(" "), {names!r})) >= {n_classes - 1}


def test_layer_gradients():
    """Every parameter's gradient and the input gradient of a conv-ReLU-pool-flatten-dense network match central differences."""
    m = module()
    net = m["Sequential"]([m["Conv2D"](2, 3, seed=4), m["ReLU"](), m["MaxPool2D"](2), m["Flatten"](), m["Dense"](18, 3, seed=5)])
    loss = m["SoftmaxCrossEntropy"]()
    rng = np.random.default_rng(6)
    X = rng.standard_normal((3, 8, 8))
    y = rng.integers(0, 3, size=3)
    net.eval()
    loss.forward(net.forward(X), y)
    grad_in = net.backward(loss.backward())
    f = lambda: loss.forward(net.forward(X), y)
    for param, grad in zip(net.parameters(), net.gradients()):
        assert np.abs(grad - numeric(f, param)).max() < 1e-6
    assert np.abs(grad_in - numeric(f, X)).max() < 1e-6
    assert net.forward(X).shape == (3, 3)


def test_loss_and_optimizer():
    """The loss is the mean negative log-probability and stays finite at 1,000; its gradient is probabilities minus one-hot over the batch; Adam's decay pulls an undefended weight towards zero and no decay leaves it."""
    m = module()
    loss = m["SoftmaxCrossEntropy"]()
    logits = np.array([[2.0, 0.0, -1.0], [1000.0, 0.0, 0.0]])
    labels = np.array([1, 0])
    value = loss.forward(logits, labels)
    probs = np.exp(logits - logits.max(axis=1, keepdims=True))
    probs /= probs.sum(axis=1, keepdims=True)
    assert abs(value - (-np.log(probs[0, 1]) - np.log(probs[1, 0])) / 2) < 1e-9 and np.isfinite(value)
    onehot = np.zeros_like(probs)
    onehot[np.arange(2), labels] = 1
    assert np.allclose(loss.backward(), (probs - onehot) / 2)
    still = np.array([1.0, -2.0])
    m["Adam"](0.01).step([still], [np.zeros(2)])
    assert np.allclose(still, [1.0, -2.0])
    pulled = np.array([1.0, -2.0])
    optimizer = m["Adam"](0.01, weight_decay=0.1)
    for _ in range(50):
        optimizer.step([pulled], [np.zeros(2)])
    assert np.abs(pulled).max() < 1.9 and np.sign(pulled).tolist() == [1.0, -1.0]


def test_dropout_and_modes():
    """Training drops about p and scales survivors by 1 / (1 - p); eval passes everything; train() and eval() flip every flag; evaluate measures in eval mode without changing a weight."""
    m = module()
    layer = m["Dropout"](0.25, seed=2)
    X = np.ones((2000, 8))
    dropped = layer.forward(X)
    assert 0.22 < (dropped == 0).mean() < 0.28 and np.allclose(dropped[dropped > 0], 4 / 3)
    assert np.array_equal(layer.backward(np.ones_like(X)) == 0, dropped == 0)
    net = m["Sequential"]([m["Dense"](8, 4, seed=1), layer, m["Dense"](4, 2, seed=2)])
    net.eval()
    assert layer.training is False and np.array_equal(layer.forward(X), X)
    net.train()
    assert layer.training is True
    before = [p.copy() for p in net.parameters()]
    rows = np.random.default_rng(3).standard_normal((20, 8))
    labels = np.random.default_rng(4).integers(0, 2, size=20)
    first = m["evaluate"](net, m["SoftmaxCrossEntropy"](), rows, labels)
    second = m["evaluate"](net, m["SoftmaxCrossEntropy"](), rows, labels)
    assert first == second and layer.training is False
    assert all(np.array_equal(p, b) for p, b in zip(net.parameters(), before))


def test_starts_and_shapes():
    """Weights start random and scaled by the fan-in, biases at zero, no two units alike; the parameter counts follow the formulas."""
    m = module()
    dense = m["Dense"](100, 50, seed=7)
    assert dense.b.tolist() == [0.0] * 50 and 0.07 < dense.W.std() < 0.13 and not np.allclose(dense.W[:, 0], dense.W[:, 1])
    conv = m["Conv2D"](8, 3, seed=8)
    assert conv.b.tolist() == [0.0] * 8 and 0.2 < conv.W.std() < 0.5 and not np.allclose(conv.W[0], conv.W[1])
    assert sum(p.size for p in dense.parameters()) == 5050 and sum(p.size for p in conv.parameters()) == 80
    net = m["Sequential"]([m["Conv2D"](6, 3, seed=1), m["ReLU"](), m["MaxPool2D"](2), m["Flatten"](), m["Dense"](96, {n_classes}, seed=2)])
    assert sum(p.size for p in net.parameters()) == 60 + 96 * {n_classes} + {n_classes}
    assert net.forward(np.zeros((2, 10, 10))).shape == (2, {n_classes})


def test_the_accuracy_bar():
    """The trained network reads at least nine in ten held-out images, with a history one entry per epoch; the same seeds give the same history; a different data seed gives different images with the same labels; batches shuffle and cover every row once."""
    m = module()
    net, history, X_val, y_val = m["net"], m["history"], m["X_val"], m["y_val"]
    loss = m["SoftmaxCrossEntropy"]()
    net.eval()
    assert (net.forward(X_val).argmax(axis=1) == y_val).mean() >= 0.9
    assert len(history["train_loss"]) == len(history["val_loss"]) == len(history["val_accuracy"]) == 20
    assert history["train_loss"][-1] < history["train_loss"][0]
    X_train, y_train = m["{maker}"](60, seed=1)
    again = m["Sequential"]([m["Conv2D"](6, 3, seed=1), m["ReLU"](), m["MaxPool2D"](2), m["Flatten"](), m["Dropout"](0.2, seed=5), m["Dense"](96, {n_classes}, seed=2)])
    repeat = m["fit"](again, loss, m["Adam"](0.01, weight_decay=1e-4), X_train, y_train, X_val, y_val, epochs=3)
    assert repeat["val_accuracy"] == history["val_accuracy"][:3] and repeat["train_loss"] == history["train_loss"][:3]
    other, other_labels = m["{maker}"](60, seed=3)
    assert other.shape == X_train.shape and not np.array_equal(other, X_train) and np.array_equal(other_labels, y_train)
    order = np.concatenate(list(m["batches"](100, 32, np.random.default_rng(0))))
    assert sorted(order.tolist()) == list(range(100)) and order.tolist() != list(range(100))
    assert [len(b) for b in m["batches"](100, 32, np.random.default_rng(1))] == [32, 32, 32, 4]
'''


def write_build(folder: str, title: str, program: str, expected: str, font_name: str, font: dict[str, list[str]], maker: str, noun: str, plural: str, intro: str, version_note: str) -> None:
    n_classes = len(font)
    code_block = glyph_literal(font_name, font) + f'''

def {maker}(n_per_class, seed):
    """n_per_class noisy, shifted images of each {noun}, with labels in font order."""
    return make_images({font_name}, n_per_class, seed)


X_train, y_train = {maker}(60, seed=1)
X_val, y_val = {maker}(20, seed=2)
loss = SoftmaxCrossEntropy()
print(X_train.shape, X_val.shape, np.bincount(y_val).tolist())
tiny = Sequential([Conv2D(2, 3, seed=1), ReLU(), MaxPool2D(2), Flatten(), Dense(32, {n_classes}, seed=2)])
print("gradient check:", "passes" if gradient_check(tiny, loss, X_train[:4], y_train[:4]) < 1e-6 else "fails")
net = Sequential([Conv2D(6, 3, seed=1), ReLU(), MaxPool2D(2), Flatten(), Dropout(0.2, seed=5), Dense(96, {n_classes}, seed=2)])
history = fit(net, loss, Adam(0.01, weight_decay=1e-4), X_train, y_train, X_val, y_val, epochs=20)
accuracy = history["val_accuracy"][-1]
print(f"loss {{history['train_loss'][0]:.2f}} -> {{history['train_loss'][-1]:.2f}} | held-out accuracy {{accuracy:.2f}} | at least 0.9: {{accuracy >= 0.9}} | {{sum(p.size for p in net.parameters())}} parameters")
print("evaluating twice gives the same answer:", evaluate(net, loss, X_val, y_val)[0] == evaluate(net, loss, X_val, y_val)[0])
names = list({font_name})
net.eval()
print("the first held-out image of each {noun} reads:", " ".join(names[i] for i in net.forward(X_val[::20]).argmax(axis=1)))
'''
    write(
        f"exercises/{folder}/exercise.yaml",
        f'''id: {folder}
stage: build
rev: 1
title: "{title}"
prompt: |
  {intro}

  **Starting from a blank editor, write the module's pieces.** In the topics you pasted the pieces already proven and wrote the new one; the checkpoint is the proof of the whole, so this time type them all (your own solutions are the reference). The printed loss and accuracy depend on how the random numbers are drawn, so draw them as stated:

  - `Dense(n_in, n_out, seed=0, scale=None)`: weights from `default_rng(seed).standard_normal` times `1 / sqrt(n_in)` (or `scale`), zero biases; `forward`, `backward` (setting `dW`, `db`, returning the input's gradient), `parameters()`, `gradients()`.
  - `ReLU`, `Flatten`, `MaxPool2D(size=2)` (the gradient goes to the cell that won) and `Dropout(p, seed=0)` (inverted: a `np.random.default_rng(seed)` made once in `__init__` draws `rng.random(X.shape)` on each training forward pass and keeps where it is at least `p`, scaling survivors by `1 / (1 - p)`; a `training` flag; eval passes everything through), each with the same four methods (empty lists where there are no parameters).
  - `Sequential(layers)`: `forward`, `backward`, `parameters`, `gradients`, and `train()` / `eval()` that set `training` on every layer that has it.
  - `Conv2D(n_kernels, k, seed=0, scale=None)`: kernels `(n_kernels, k, k)` from `standard_normal` times `1 / k` (or `scale`), zero biases; `forward` from images `(N, H, W)` to maps `(N, n_kernels, H - k + 1, W - k + 1)`; `backward` setting `dW` and `db` and returning the input's gradient.
  - `SoftmaxCrossEntropy`: `forward(logits, labels)` as the mean negative log-probability by log-sum-exp (finite for a logit of 1,000); `backward()` as probabilities minus one-hot labels over the batch size.
  - `Adam(rate, weight_decay=0.0, beta1=0.9, beta2=0.999, eps=1e-8)` with `step(params, grads)`, adding `weight_decay * param` to each gradient before the moments.
  - `numeric_gradient(f, param, h=1e-6)` and `gradient_check(net, loss, X, y)`: the largest gap between backward and central differences over every parameter, **with the network put in eval mode first**.
  - `batches(n, batch_size, rng)` (one `rng.permutation(n)` per epoch, sliced `batch_size` at a time), `evaluate(net, loss, X, y)` (eval mode, then the loss and the accuracy, no update) and `fit(net, loss, optimizer, X_train, y_train, X_val, y_val, epochs, batch_size=32, seed=0)` (one `np.random.default_rng(seed)` made once and handed to `batches` for every epoch; train mode before each epoch's steps; after each epoch, `evaluate` on the whole training set and on the validation set, giving one history entry per epoch with `train_loss`, `val_loss` and `val_accuracy`).

  **Then paste the data, which isn't what is being proven,** and the training script, and run it:

  ```python
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


{block(code_block, "  ")}  ```

  ```
{block(expected)}  ```

  {version_note}The checks compare every layer's gradient and the input gradient with central differences, test the loss and Adam's decay on known numbers, dropout's two modes and that `evaluate` leaves no weight changed, the random starts and the parameter counts, and hold the trained network to nine in ten held-out {plural}, with the same seeds giving the same history. The browser allows about a minute; the reference solution trains in a few seconds.
{TEST_SKILLS}''',
    )
    write(f"exercises/{folder}/starter.py", "")
    write(f"exercises/{folder}/solution.py", program)
    write(f"exercises/{folder}/test_exercise.py", build_test(expected, n_classes, maker, list(font)))
    for key, code in build_wrongs(program).items():
        write(f"exercises/{folder}/wrong/{key}.py", code)
    write(
        f"exercises/{folder}/wrong/typed-in.py",
        "import numpy as np\n\n\nclass Dense:\n    def __init__(self, n_in, n_out, seed=0, scale=None):\n        self.W = np.zeros((n_in, n_out))\n        self.b = np.zeros(n_out)\n\n    def parameters(self):\n        return [self.W, self.b]\n\n\ndef fit(*args, **kwargs):\n    return {}\n\n\nnet = None\nhistory = {}\nX_val = None\ny_val = None\n\n\n" + "".join(f"print({line!r})\n" for line in expected.splitlines()),
    )


write_build(
    "build-a-network-that-reads-digits",
    "A network that reads digits",
    BUILD,
    BUILD_OUT,
    "DIGITS",
    DIGITS,
    "make_digits",
    "digit",
    "digits",
    "Build the module's network from its pieces and train it to read the ten digits: noisy 10-by-10 images of a 5-by-7 pixel font, each shifted by up to a pixel, six hundred to train on and two hundred held out. The worked example runs the same pipeline on four shapes.",
    "",
)
write_build(
    "build-a-network-that-reads-letters",
    "A network that reads letters",
    LETTERS_BUILD,
    LETTERS_OUT,
    "LETTERS",
    LETTERS,
    "make_letters",
    "letter",
    "letters",
    "A fresh version of the build: the same network and loop, trained to read eight capital letters (A, C, E, F, H, L, T, U) from the same kind of noisy, shifted images; four hundred and eighty to train on and a hundred and sixty held out.",
    "The output layer has eight units and the network 836 parameters. ",
)
write_build(
    "build-a-network-that-reads-symbols",
    "A network that reads symbols",
    SYMBOLS_BUILD,
    SYMBOLS_OUT,
    "SYMBOLS",
    SYMBOLS,
    "make_symbols",
    "symbol",
    "symbols",
    "A fresh version of the build: the same network and loop, trained to read six symbols (a plus, a minus, a times, a slash, a box and a small ring) from the same kind of noisy, shifted images; three hundred and sixty to train on and a hundred and twenty held out.",
    "The output layer has six units and the network 642 parameters. ",
)
assert "| 1030 parameters" in BUILD_OUT and "| 836 parameters" in LETTERS_OUT and "| 642 parameters" in SYMBOLS_OUT

# =====================================================================================
# The debug.
# =====================================================================================

write(
    "exercises/debug-a-script-that-will-not-learn/exercise.yaml",
    f'''id: debug-a-script-that-will-not-learn
stage: debug
rev: 1
title: "Three bugs in a training script"
prompt: |
  This is the digit reader, with the weights of both layer types started by one helper, `start_weights` (its `fan_in` is the number of inputs a unit sums: `n_in` for a dense layer, `k * k` for a kernel), and the learning rate in one name, `RATE`. It should print:

  ```
{block(DEBUG_OUT)}  ```

  It has three bugs, and each shows from the outside. Run it:

  1. **The loss sits at 2.30 for twenty epochs and the accuracy at {STARTER_ACC}:** 2.30 is log 10, the loss of guessing evenly among ten digits, and the curve never moves. `start_weights` returns zeros, a placeholder that was never replaced: with every weight at zero, every hidden value is zero, no gradient reaches any weight, and only the output bias moves. Starting weights must be small random numbers scaled by the fan-in (`standard_normal(shape) / sqrt(fan_in)`), so that the signal neither vanishes nor explodes and no two units begin alike.
  2. **The run now learns, but ends at {AFTER_ZERO_ACC}, short of the bar, and evaluating twice already gives two different answers** (that is the third bug showing; hold it for a moment): `RATE` is 0.1, ten times too high for Adam on this network, so each step overshoots; with the evaluation fixed as well, a rate of 0.1 still stops at {STILL_RATE_ACC}. The checklist's fix is the rate by a factor of ten: 0.01.
  3. **The accuracy is {AFTER_RATE_ACC}, but evaluating the network twice gives two different answers:** `evaluate` never switches the network to eval mode, so dropout is still drawing a fresh random mask on every forward pass while the network is being measured. `evaluate` must call `net.eval()` before its forward pass; `fit` already calls `net.train()` before each epoch's steps.

  The checks also hold `start_weights` to a random, fan-in-scaled start, `RATE` to 0.01, and `evaluate` to leaving dropout off.
# Every test names the module skills it checks (ADR-0012), so a failed test
# says which topics to revisit.
test_skills:
  test_the_output: [ml.nn.initialization-and-activations/symmetry, ml.nn.regularization/dropout, ml.nn.debugging-training/learning-rate]
  test_the_pieces: [ml.nn.initialization-and-activations/symmetry, ml.nn.initialization-and-activations/scale, ml.nn.regularization/dropout, ml.nn.debugging-training/learning-rate, ml.nn.debugging-training/bug-or-hard]
''',
)
write("exercises/debug-a-script-that-will-not-learn/starter.py", DEBUG_STARTER)
write("exercises/debug-a-script-that-will-not-learn/solution.py", DEBUG_SOLUTION)
write(
    "exercises/debug-a-script-that-will-not-learn/test_exercise.py",
    f'''import numpy as np

from checks import function, run

EXPECTED = {DEBUG_OUT!r}


def test_the_output():
    """Prints a run that clears the bar and a double evaluation that agrees."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\\n{{EXPECTED}}\\nYour program printed:\\n{{printed}}"


def test_the_pieces():
    """start_weights is random and scaled by the fan-in, RATE is 0.01, and evaluate leaves dropout off."""
    fit = function("fit")
    m = fit.__globals__
    W = m["start_weights"](np.random.default_rng(1), (400, 50), 400)
    assert W.shape == (400, 50) and 0.04 < W.std() < 0.06 and not np.allclose(W[:, 0], W[:, 1])
    assert m["RATE"] == 0.01
    layer = m["Dropout"](0.5, seed=1)
    net = m["Sequential"]([layer])
    X = np.ones((50, 4))
    first = m["evaluate"](net, m["SoftmaxCrossEntropy"](), X, np.zeros(50, dtype=int))
    assert layer.training is False and first == m["evaluate"](net, m["SoftmaxCrossEntropy"](), X, np.zeros(50, dtype=int))
''',
)
write("exercises/debug-a-script-that-will-not-learn/wrong/still-starting-at-zero.py", DEBUG_STILL_ZERO)
write("exercises/debug-a-script-that-will-not-learn/wrong/still-dropping-at-evaluation.py", DEBUG_STILL_EVAL)
write("exercises/debug-a-script-that-will-not-learn/wrong/still-ten-times-too-fast.py", DEBUG_STILL_RATE)
write(
    "exercises/debug-a-script-that-will-not-learn/wrong/typed-in.py",
    "import numpy as np\n\n\ndef start_weights(rng, shape, fan_in):\n    return np.zeros(shape)\n\n\nRATE = 0.01\n\n\nclass Dropout:\n    def __init__(self, p, seed=0):\n        self.training = True\n\n\nclass Sequential:\n    def __init__(self, layers):\n        self.layers = layers\n\n\nclass SoftmaxCrossEntropy:\n    pass\n\n\ndef evaluate(net, loss, X, y):\n    return 0.0, 0.0\n\n\ndef fit(*args, **kwargs):\n    return {}\n\n\n" + "".join(f"print({line!r})\n" for line in DEBUG_OUT.splitlines()),
)

# =====================================================================================
# The steps.
# =====================================================================================

write(
    "exercises/step-the-dense-layers/exercise.yaml",
    f'''id: step-the-dense-layers
stage: fill_in
rev: 1
title: "Step 1: the dense layers and their gradients"
prompt: |
  `Dense.backward` must set the weight gradient (the stored input, transposed, times the gradient from above), the bias gradient (the gradient from above summed over the rows), and return the gradient for its input (the gradient from above times the transposed weights); `ReLU.backward` passes the gradient only where the input was positive. Replace each `...` so the gradient check passes and the program prints:

  ```
{block(STEP_LAYERS_OUT)}  ```
hints:
  - "`dW = X.T @ grad_out` has shape `(n_in, n_out)`, like `W`; `db` sums `grad_out` down the rows (`axis=0`); the input's gradient is `grad_out @ W.T`, shaped like `X`."
  - "ReLU stored `self.mask` on the way forward; backward multiplies by it."
''',
)
write("exercises/step-the-dense-layers/starter.py", STEP_LAYERS_STARTER)
write("exercises/step-the-dense-layers/solution.py", STEP_LAYERS)
write(
    "exercises/step-the-dense-layers/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """The gradient check passes and the counts are right."""
    printed = run()
    assert printed == {STEP_LAYERS_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_by_hand():
    """One dense layer's three gradients on a tiny case, by hand."""
    Dense = function("Dense")
    layer = Dense(2, 2, seed=0)
    layer.W[:] = np.array([[1.0, 2.0], [3.0, 4.0]])
    layer.forward(np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]]))
    grad_in = layer.backward(np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]]))
    assert layer.dW.tolist() == [[2.0, 1.0], [1.0, 2.0]] and layer.db.tolist() == [2.0, 2.0]
    assert grad_in.tolist() == [[1.0, 3.0], [2.0, 4.0], [3.0, 7.0]]
''',
)
write("exercises/step-the-dense-layers/wrong/half-the-weight-gradient.py", STEP_LAYERS_WRONG)
write(
    "exercises/step-the-dense-layers/wrong/typed-in.py",
    "import numpy as np\n\n\nclass Dense:\n    def __init__(self, n_in, n_out, seed=0, scale=None):\n        self.W = np.zeros((n_in, n_out))\n        self.b = np.zeros(n_out)\n\n    def forward(self, X):\n        return X @ self.W\n\n    def backward(self, grad_out):\n        return grad_out\n\n\n" + "".join(f"print({line!r})\n" for line in STEP_LAYERS_OUT.splitlines()),
)

write(
    "exercises/step-the-convolutional-layer/exercise.yaml",
    f'''id: step-the-convolutional-layer
stage: fill_in
rev: 1
title: "Step 2: the convolutional layer and the pool"
prompt: |
  `Conv2D.backward` loops over the kernel's offsets: weight `(i, j)`'s gradient is the output gradient times the input shifted by `(i, j)`, summed over images and positions, and each output gradient flows back onto the input cells it read, through weight `(i, j)`; `MaxPool2D.backward` gives each pooled cell's gradient to the cell that won its window, using the mask saved on the way forward. Replace each `...` so both checks pass and the program prints:

  ```
{block(STEP_CONV_OUT)}  ```
hints:
  - "The shifted input is `patch`, already sliced; the weight going back is the same `self.W[None, :, i, j, None, None]` the forward pass used."
  - "`self.mask` is True where a cell equalled its window's maximum; multiply the spread gradient by it."
''',
)
write("exercises/step-the-convolutional-layer/starter.py", STEP_CONV_STARTER)
write("exercises/step-the-convolutional-layer/solution.py", STEP_CONV)
write(
    "exercises/step-the-convolutional-layer/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Both gradient checks pass."""
    printed = run()
    assert printed == {STEP_CONV_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_by_hand():
    """A 2-by-2 kernel's gradients and the pool's routing on tiny cases, by hand."""
    Conv2D = function("Conv2D")
    MaxPool2D = function("MaxPool2D")
    conv = Conv2D(1, 2, seed=0)
    conv.W[0] = np.array([[1.0, 2.0], [3.0, 4.0]])
    conv.forward(np.arange(9.0).reshape(1, 3, 3))
    grad_in = conv.backward(np.ones((1, 1, 2, 2)))
    assert conv.dW[0].tolist() == [[8.0, 12.0], [20.0, 24.0]] and conv.db.tolist() == [4.0]
    assert grad_in[0].tolist() == [[1.0, 3.0, 2.0], [4.0, 10.0, 6.0], [3.0, 7.0, 4.0]]
    pool = MaxPool2D(2)
    pool.forward(np.array([[[[1.0, 2.0, 5.0, 6.0], [3.0, 4.0, 7.0, 8.0], [9.0, 10.0, 13.0, 14.0], [11.0, 12.0, 15.0, 16.0]]]]))
    assert pool.backward(np.array([[[[1.0, 2.0], [3.0, 4.0]]]])).tolist() == [[[[0.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 2.0], [0.0, 0.0, 0.0, 0.0], [0.0, 3.0, 0.0, 4.0]]]]
''',
)
write("exercises/step-the-convolutional-layer/wrong/kernel-transposed-going-back.py", STEP_CONV_WRONG)
write(
    "exercises/step-the-convolutional-layer/wrong/typed-in.py",
    "import numpy as np\n\n\nclass Conv2D:\n    def __init__(self, n_kernels, k, seed=0, scale=None):\n        self.W = np.zeros((n_kernels, k, k))\n        self.b = np.zeros(n_kernels)\n\n    def forward(self, X):\n        return X\n\n    def backward(self, grad_out):\n        return grad_out\n\n\nclass MaxPool2D:\n    def __init__(self, size=2):\n        self.size = size\n\n    def forward(self, X):\n        return X[:, :, ::2, ::2]\n\n    def backward(self, grad_out):\n        return grad_out\n\n\n" + "".join(f"print({line!r})\n" for line in STEP_CONV_OUT.splitlines()),
)

write(
    "exercises/step-the-loss-and-the-optimizer/exercise.yaml",
    f'''id: step-the-loss-and-the-optimizer
stage: fill_in
rev: 1
title: "Step 3: the loss's gradient and weight decay"
prompt: |
  `SoftmaxCrossEntropy.backward` is the probabilities with 1 subtracted at each row's true label, divided by the number of rows; `Adam.step` adds `weight_decay` times the parameter to each gradient before updating the moments. Replace each `...` so the program prints the loss of three rows (one of them with a logit of 1,000), the gradient of the all-zero row, and three decay-only steps on a weight vector:

  ```
{block(STEP_LOSS_OUT)}  ```
hints:
  - "For the row `[0, 0, 0]` the probabilities are a third each; subtracting 1 at the true label and dividing by 3 rows gives the printed row."
  - "With a zero gradient, the only pull is `weight_decay * param`; Adam normalizes it, so each step moves every weight by about the rate towards zero."
''',
)
write("exercises/step-the-loss-and-the-optimizer/starter.py", STEP_LOSS_STARTER)
write("exercises/step-the-loss-and-the-optimizer/solution.py", STEP_LOSS)
write(
    "exercises/step-the-loss-and-the-optimizer/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints the loss, the gradient row and the decayed weights."""
    printed = run()
    assert printed == {STEP_LOSS_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_by_hand():
    """The gradient is probabilities minus one-hot over the batch; a decay of zero leaves an undefended weight alone."""
    SoftmaxCrossEntropy = function("SoftmaxCrossEntropy")
    Adam = function("Adam")
    loss = SoftmaxCrossEntropy()
    logits = np.array([[1.0, 2.0, 3.0], [0.0, 0.0, 5.0]])
    labels = np.array([2, 0])
    loss.forward(logits, labels)
    probs = np.exp(logits - logits.max(axis=1, keepdims=True))
    probs /= probs.sum(axis=1, keepdims=True)
    onehot = np.zeros_like(probs)
    onehot[np.arange(2), labels] = 1
    assert np.allclose(loss.backward(), (probs - onehot) / 2)
    still = np.array([2.0, -1.0])
    Adam(0.1).step([still], [np.zeros(2)])
    assert np.allclose(still, [2.0, -1.0])
''',
)
write("exercises/step-the-loss-and-the-optimizer/wrong/forgets-the-batch-size.py", STEP_LOSS_WRONG)
write(
    "exercises/step-the-loss-and-the-optimizer/wrong/typed-in.py",
    "import numpy as np\n\n\nclass SoftmaxCrossEntropy:\n    def forward(self, logits, labels):\n        return 0.0\n\n    def backward(self):\n        return np.zeros((2, 3))\n\n\nclass Adam:\n    def __init__(self, rate, weight_decay=0.0):\n        pass\n\n    def step(self, params, grads):\n        pass\n\n\n" + "".join(f"print({line!r})\n" for line in STEP_LOSS_OUT.splitlines()),
)

write(
    "exercises/step-train-and-evaluate/exercise.yaml",
    f'''id: step-train-and-evaluate
stage: fill_in
rev: 1
title: "Step 4: train mode, eval mode"
prompt: |
  The whole pipeline on the four shapes, with two calls missing: `fit` must put the network in **train** mode before each epoch's steps, so dropout drops, and `evaluate` must put it in **eval** mode before measuring, so dropout passes everything through and the same network gives the same answer twice. Replace each `...` with the right mode so the program prints:

  ```
{block(STEP_TRAIN_OUT)}  ```
hints:
  - "`Sequential.train()` sets every `training` flag to True; `Sequential.eval()` sets them to False."
  - "Measuring with dropout on gives a different answer every time, because a fresh mask is drawn on every forward pass."
''',
)
write("exercises/step-train-and-evaluate/starter.py", STEP_TRAIN_STARTER)
write("exercises/step-train-and-evaluate/solution.py", STEP_TRAIN)
write(
    "exercises/step-train-and-evaluate/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """The run clears the bar and the modes are right."""
    printed = run()
    assert printed == {STEP_TRAIN_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_the_modes():
    """evaluate leaves dropout off and changes no weight; fit leaves the network in eval mode after its last measurement."""
    fit = function("fit")
    m = fit.__globals__
    layer = m["Dropout"](0.5, seed=1)
    net = m["Sequential"]([m["Dense"](4, 3, seed=1), layer, m["Dense"](3, 2, seed=2)])
    X = np.random.default_rng(2).standard_normal((30, 4))
    y = np.random.default_rng(3).integers(0, 2, size=30)
    loss = m["SoftmaxCrossEntropy"]()
    before = [p.copy() for p in net.parameters()]
    assert m["evaluate"](net, loss, X, y) == m["evaluate"](net, loss, X, y) and layer.training is False
    assert all(np.array_equal(p, b) for p, b in zip(net.parameters(), before))
    history = m["fit"](net, loss, m["Adam"](0.01), X, y, X, y, epochs=2, batch_size=10)
    assert len(history["val_accuracy"]) == 2 and layer.training is False
''',
)
write("exercises/step-train-and-evaluate/wrong/measures-in-train-mode.py", STEP_TRAIN_WRONG)
write(
    "exercises/step-train-and-evaluate/wrong/typed-in.py",
    "import numpy as np\n\n\nclass Dropout:\n    def __init__(self, p, seed=0):\n        self.training = True\n\n\nclass Dense:\n    def __init__(self, n_in, n_out, seed=0):\n        self.W = np.zeros((n_in, n_out))\n\n    def parameters(self):\n        return [self.W]\n\n\nclass Sequential:\n    def __init__(self, layers):\n        self.layers = layers\n\n    def parameters(self):\n        return [p for layer in self.layers if hasattr(layer, 'parameters') for p in layer.parameters()]\n\n\nclass SoftmaxCrossEntropy:\n    pass\n\n\nclass Adam:\n    def __init__(self, rate):\n        pass\n\n\ndef evaluate(net, loss, X, y):\n    return 0.0, 0.0\n\n\ndef fit(net, loss, optimizer, X_train, y_train, X_val, y_val, epochs, batch_size=32, seed=0):\n    return {'val_accuracy': [0.0] * epochs}\n\n\n" + "".join(f"print({line!r})\n" for line in STEP_TRAIN_OUT.splitlines()),
)

print("ml.m8.checkpoint written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
print("accuracies:", BUILD_ACC, "digits |", LETTERS_OUT.splitlines()[2].split("accuracy ")[1].split(" |")[0], "letters |", SYMBOLS_OUT.splitlines()[2].split("accuracy ")[1].split(" |")[0], "symbols |", EXAMPLE_ACC, "shapes |", DEBUG_ACC, "debug")
