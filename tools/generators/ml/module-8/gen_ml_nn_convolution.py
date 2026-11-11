"""Writes the topic ml.nn.convolution (Module 8's sixth topic). Run from the
repository root under uv (python -m uv run python <this file>), so every
program's expected output is captured from CPython rather than typed in.
The convolutional layer loops over the kernel's k-by-k offsets, each a
shifted slice of the batch times one weight, so forward and backward are a
few lines and fast enough for the browser; the gradient checks print
"passes" rather than a gap in digits, and the generator checks that a
tenth-decimal nudge of the data leaves every line unchanged. Files are
written as bytes with LF endings."""

import pathlib
import subprocess
import sys

ROOT = pathlib.Path("content/topics/ml.nn.convolution")


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


# The module's classes as they stand after the backward-layers topic.
MODULE = '''class Dense:
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


def input_gradient_check(net, loss, X, y):
    """The largest gap between the gradient backward hands back for X and the numeric one."""
    loss.forward(net.forward(X), y)
    grad = net.backward(loss.backward())
    numeric = numeric_gradient(lambda: loss.forward(net.forward(X), y), X)
    return float(np.abs(grad - numeric).max())
'''

# This topic's additions.
CONV = '''

def correlate2d(image, kernel, padding=0, stride=1):
    """Slide the kernel over the image (padded with zeros on every side), moving stride pixels at a time; each output cell is the sum of the kernel times the patch under it. Libraries call this a convolution."""
    if padding:
        image = np.pad(image, padding)
    k = kernel.shape[0]
    h_out = (image.shape[0] - k) // stride + 1
    w_out = (image.shape[1] - k) // stride + 1
    out = np.zeros((h_out, w_out))
    for y in range(h_out):
        for x in range(w_out):
            patch = image[y * stride : y * stride + k, x * stride : x * stride + k]
            out[y, x] = (patch * kernel).sum()
    return out


class Conv2D:
    """n_kernels square kernels of size k slid over single-channel images (N, H, W), giving (N, n_kernels, H - k + 1, W - k + 1): one feature map per kernel."""

    def __init__(self, n_kernels, k, seed=0):
        rng = np.random.default_rng(seed)
        self.W = rng.standard_normal((n_kernels, k, k)) / np.sqrt(k * k)
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
                # Every output cell times weight (i, j) sees the input shifted by (i, j).
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
                # Weight (i, j) was used at every position: its gradient sums them all.
                self.dW[:, i, j] = (grad_out * patch[:, None]).sum(axis=(0, 2, 3))
                # Each output gradient flows back to the input cells it read, through weight (i, j).
                grad_in[:, i : i + h_out, j : j + w_out] += (grad_out * self.W[None, :, i, j, None, None]).sum(axis=1)
        return grad_in

    def parameters(self):
        return [self.W, self.b]

    def gradients(self):
        return [self.dW, self.db]


class MaxPool2D:
    """Keep the largest value in each size-by-size window of every feature map (N, C, H, W), dividing height and width by size."""

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
        # Only the cell that won its window affected the output, so only it gets the gradient.
        spread = self.mask * grad_out[:, :, :, None, :, None]
        return spread.reshape(n, c, h_out * s, w_out * s)

    def parameters(self):
        return []

    def gradients(self):
        return []


class Flatten:
    """Feature maps (N, C, H, W) to rows (N, C * H * W), so a Dense layer can follow."""

    def forward(self, X):
        self.shape = X.shape
        return X.reshape(len(X), -1)

    def backward(self, grad_out):
        return grad_out.reshape(self.shape)

    def parameters(self):
        return []

    def gradients(self):
        return []


def make_bars(n, seed):
    """n noisy 8x8 images: the first half with a horizontal bar, the second half with a vertical one, each at a random position."""
    rng = np.random.default_rng(seed)
    X = rng.normal(0.0, 0.3, size=(n, 8, 8))
    y = np.repeat([0, 1], n // 2)
    for image, label in zip(X, y):
        at = rng.integers(1, 7)
        if label == 0:
            image[at, :] += 1.0
        else:
            image[:, at] += 1.0
    return X, y
'''

EXAMPLE_HEAD = "import numpy as np\n\n\n" + MODULE + CONV
EXAMPLE_TAIL = '''

# A vertical edge, and two kernels slid over it.
image = np.zeros((6, 6))
image[:, 3:] = 1.0
vertical = np.array([[-1.0, 0.0, 1.0], [-1.0, 0.0, 1.0], [-1.0, 0.0, 1.0]])
horizontal = vertical.T
print("row 0 of the image:", image[0].tolist())
print("vertical-edge kernel, row 0 of the output:", correlate2d(image, vertical)[0].tolist())
print("horizontal-edge kernel, row 0 of the output:", correlate2d(image, horizontal)[0].tolist())
print("valid:", correlate2d(image, vertical).shape, "| padded by 1:", correlate2d(image, vertical, padding=1).shape, "| stride 2:", correlate2d(image, vertical, stride=2).shape)

# Parameters: a dense layer on an image against a few kernels.
dense_params = 28 * 28 * 28 * 28 + 28 * 28
conv_params = 8 * 3 * 3 + 8
print(f"a dense layer from a 28x28 image to a 28x28 output: {dense_params:,} parameters | eight 3x3 kernels: {conv_params} | ratio {dense_params // conv_params:,}")

# The layer, checked against correlate2d, on a shift, and numerically.
rng = np.random.default_rng(0)
images = rng.standard_normal((5, 8, 8))
labels = rng.integers(0, 3, size=5)
conv = Conv2D(4, 3, seed=1)
maps = conv.forward(images)
by_hand = correlate2d(images[2], conv.W[1]) + conv.b[1]
print("Conv2D output shape:", maps.shape, "| kernel 1 on image 2 matches correlate2d:", bool(np.allclose(maps[2, 1], by_hand)))
bars = np.zeros((2, 8, 8))
bars[0, 2, :] = 1.0
bars[1, 4, :] = 1.0
maps = conv.forward(bars)
print("a bar two rows lower gives the feature map two rows lower:", bool(np.allclose(maps[1, :, 2:, :], maps[0, :, :-2, :])))
net = Sequential([Conv2D(4, 3, seed=1), ReLU(), MaxPool2D(2), Flatten(), Dense(4 * 3 * 3, 3, seed=2)])
loss = SoftmaxCrossEntropy()
print("gradient check of the parameters:", "passes" if gradient_check(net, loss, images, labels) < 1e-6 else "fails", "| of the input:", "passes" if input_gradient_check(net, loss, images, labels) < 1e-6 else "fails")

# Pooling, and where its gradient goes.
block = np.array([[[[1.0, 2.0, 5.0, 6.0], [3.0, 4.0, 7.0, 8.0], [9.0, 10.0, 13.0, 14.0], [11.0, 12.0, 15.0, 16.0]]]])
pool = MaxPool2D(2)
print("max pooling a 4x4:", pool.forward(block)[0, 0].tolist())
print("where a gradient of 1 per pooled cell goes back:", pool.backward(np.ones((1, 1, 2, 2)))[0, 0].tolist())

# A small network learns to tell a horizontal bar from a vertical one.
X_train, y_train = make_bars(100, seed=1)
X_test, y_test = make_bars(100, seed=2)
net = Sequential([Conv2D(4, 3, seed=1), ReLU(), MaxPool2D(2), Flatten(), Dense(4 * 3 * 3, 2, seed=2)])
first = loss.forward(net.forward(X_train), y_train)
for step in range(300):
    loss.forward(net.forward(X_train), y_train)
    net.backward(loss.backward())
    for param, grad in zip(net.parameters(), net.gradients()):
        param -= 0.1 * grad
last = loss.forward(net.forward(X_train), y_train)
accuracy = float((net.forward(X_test).argmax(axis=1) == y_test).mean())
print(f"bars: training loss {first:.2f} -> {last:.2f} after 300 steps | held-out accuracy {accuracy:.2f} | {sum(p.size for p in net.parameters())} parameters")
'''
EXAMPLE = EXAMPLE_HEAD + EXAMPLE_TAIL
EXAMPLE_OUT = out(EXAMPLE)
print("example:\n" + EXAMPLE_OUT)
EX = EXAMPLE_OUT.splitlines()
assert len(EX) == 11, EX
assert EX[0] == "row 0 of the image: [0.0, 0.0, 0.0, 1.0, 1.0, 1.0]", EX[0]
assert EX[1] == "vertical-edge kernel, row 0 of the output: [0.0, 3.0, 3.0, 0.0]", EX[1]
assert EX[2] == "horizontal-edge kernel, row 0 of the output: [0.0, 0.0, 0.0, 0.0]", EX[2]
assert EX[3] == "valid: (4, 4) | padded by 1: (6, 6) | stride 2: (2, 2)", EX[3]
assert EX[4] == "a dense layer from a 28x28 image to a 28x28 output: 615,440 parameters | eight 3x3 kernels: 80 | ratio 7,693", EX[4]
assert EX[5] == "Conv2D output shape: (5, 4, 6, 6) | kernel 1 on image 2 matches correlate2d: True", EX[5]
assert EX[6].endswith("True"), EX[6]
assert EX[7] == "gradient check of the parameters: passes | of the input: passes", EX[7]
assert EX[8] == "max pooling a 4x4: [[4.0, 8.0], [12.0, 16.0]]", EX[8]
assert EX[9] == "where a gradient of 1 per pooled cell goes back: [[0.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 1.0], [0.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 1.0]]", EX[9]
assert EX[10].startswith("bars: training loss ") and EX[10].endswith("| 114 parameters"), EX[10]
BARS_ACC = float(EX[10].split("accuracy ")[1].split(" |")[0])
assert BARS_ACC >= 0.95, BARS_ACC
BARS_FIRST = EX[10].split("loss ")[1].split(" ->")[0]
BARS_LAST = EX[10].split("-> ")[1].split(" after")[0]
NUDGED = EXAMPLE.replace("X_train, y_train = make_bars(100, seed=1)", "X_train, y_train = make_bars(100, seed=1)\nX_train[0, 0, 0] += 1e-10")
assert out(NUDGED) == EXAMPLE_OUT, "a tenth-decimal nudge changed a printed line"
EXAMPLE_LINES = EXAMPLE.splitlines()


def ln(text: str, after: int = 0) -> int:
    return next(i + 1 for i, line in enumerate(EXAMPLE_LINES) if i + 1 > after and text in line)


# --- recall programs ----------------------------------------------------------------------------

PREDICT_CORRELATION = '''import numpy as np

image = np.array([[1.0, 2.0, 0.0], [0.0, 1.0, 3.0], [2.0, 0.0, 1.0]])
kernel = np.array([[1.0, 2.0], [0.0, -1.0]])
out = np.zeros((2, 2))
for y in range(2):
    for x in range(2):
        out[y, x] = (image[y:y + 2, x:x + 2] * kernel).sum()
print(out.tolist())
'''
PREDICT_CORRELATION_OUT = out(PREDICT_CORRELATION)
assert PREDICT_CORRELATION_OUT == "[[4.0, -1.0], [2.0, 6.0]]\n", PREDICT_CORRELATION_OUT

PREDICT_SHAPES = '''def output_size(n, k, padding=0, stride=1):
    """The height (or width) of the output when a k-wide kernel slides over n pixels."""
    return (n + 2 * padding - k) // stride + 1


print(output_size(28, 3), output_size(28, 3, padding=1), output_size(28, 5, padding=2))
print(output_size(28, 3, stride=2), output_size(32, 2, stride=2))
'''
PREDICT_SHAPES_OUT = out(PREDICT_SHAPES)
assert PREDICT_SHAPES_OUT == "26 28 28\n13 16\n", PREDICT_SHAPES_OUT

PREDICT_PARAMS = '''def conv_parameters(n_kernels, k):
    return n_kernels * k * k + n_kernels


def dense_parameters(n_in, n_out):
    return n_in * n_out + n_out


print(conv_parameters(16, 5), conv_parameters(32, 3))
print(dense_parameters(32 * 32, 10), dense_parameters(16 * 14 * 14, 10))
'''
PREDICT_PARAMS_OUT = out(PREDICT_PARAMS)
assert PREDICT_PARAMS_OUT == "416 320\n10250 31370\n", PREDICT_PARAMS_OUT

PREDICT_CONV = '''import numpy as np

X = np.array([[[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]])
W = np.array([[[1.0, 0.0], [0.0, 1.0]], [[0.0, 1.0], [0.0, 0.0]]])
out = np.zeros((1, 2, 2, 2))
for i in range(2):
    for j in range(2):
        out += X[:, i:i + 2, j:j + 2][:, None] * W[None, :, i, j, None, None]
print(out.shape, out[0, 0].tolist(), out[0, 1].tolist())
'''
PREDICT_CONV_OUT = out(PREDICT_CONV)
assert PREDICT_CONV_OUT == "(1, 2, 2, 2) [[6.0, 8.0], [12.0, 14.0]] [[2.0, 3.0], [5.0, 6.0]]\n", PREDICT_CONV_OUT

PREDICT_POOL = '''import numpy as np

X = np.array([[2.0, 7.0, 1.0, 0.0], [4.0, 3.0, 5.0, 8.0], [0.0, 1.0, 9.0, 2.0], [6.0, 0.0, 3.0, 3.0]])
windows = X.reshape(2, 2, 2, 2)
pooled = windows.max(axis=(1, 3))
print(pooled.tolist())
print(int((windows == pooled[:, None, :, None]).sum()))
'''
PREDICT_POOL_OUT = out(PREDICT_POOL)
assert PREDICT_POOL_OUT == "[[7.0, 8.0], [6.0, 9.0]]\n4\n", PREDICT_POOL_OUT

REVIEW_PREDICT = '''import numpy as np

image = np.array([[0.0, 0.0, 1.0, 1.0], [0.0, 0.0, 1.0, 1.0], [0.0, 0.0, 1.0, 1.0], [0.0, 0.0, 1.0, 1.0]])
kernel = np.array([[-1.0, 1.0], [-1.0, 1.0]])
out = np.zeros((3, 3))
for y in range(3):
    for x in range(3):
        out[y, x] = (image[y:y + 2, x:x + 2] * kernel).sum()
print(out[0].tolist(), out.shape)
'''
REVIEW_PREDICT_OUT = out(REVIEW_PREDICT)
assert REVIEW_PREDICT_OUT == "[0.0, 2.0, 0.0] (3, 3)\n", REVIEW_PREDICT_OUT

PARSONS_LINES = [
    "import numpy as np",
    "image, kernel = np.arange(9.0).reshape(3, 3), np.array([[0.0, 1.0], [1.0, 0.0]])",
    "out = np.zeros((image.shape[0] - 1, image.shape[1] - 1))",
    "for y in range(out.shape[0]):",
    "    for x in range(out.shape[1]):",
    "        out[y, x] = (image[y:y + 2, x:x + 2] * kernel).sum()",
    "print(out.tolist())",
]
PARSONS_OUT = out("\n".join(PARSONS_LINES) + "\n")
assert PARSONS_OUT == "[[4.0, 6.0], [10.0, 12.0]]\n", PARSONS_OUT

# --- the fill-in --------------------------------------------------------------------------------

FILL_SOLUTION = '''import numpy as np


def correlate2d(image, kernel, padding=0, stride=1):
    """Slide the kernel over the image (padded with zeros by `padding` on every side), moving `stride` pixels at a time; each output cell is the sum of the kernel times the patch under it."""
    if padding:
        image = np.pad(image, padding)
    k = kernel.shape[0]
    h_out = (image.shape[0] - k) // stride + 1
    w_out = (image.shape[1] - k) // stride + 1
    out = np.zeros((h_out, w_out))
    for y in range(h_out):
        for x in range(w_out):
            patch = image[y * stride : y * stride + k, x * stride : x * stride + k]
            out[y, x] = (patch * kernel).sum()
    return out


image = (np.arange(36.0).reshape(6, 6) ** 2) % 7
kernel = np.array([[1.0, 0.0, -1.0], [2.0, 0.0, -2.0], [1.0, 0.0, -1.0]])
print(correlate2d(image, kernel)[0].tolist())
print(correlate2d(image, kernel, padding=1).shape, correlate2d(image, kernel, stride=2).tolist())
'''
FILL_STARTER = (
    FILL_SOLUTION.replace("    h_out = (image.shape[0] - k) // stride + 1", "    h_out = (image.shape[0] - k) // ... + 1")
    .replace("    w_out = (image.shape[1] - k) // stride + 1", "    w_out = (image.shape[1] - k) // ... + 1")
    .replace("            patch = image[y * stride : y * stride + k, x * stride : x * stride + k]", "            patch = image[y * stride : y * stride + ..., x * stride : x * stride + ...]")
    .replace("            out[y, x] = (patch * kernel).sum()", "            out[y, x] = (patch * ...).sum()")
)
assert FILL_STARTER.count("...") == 5
FILL_OUT = out(FILL_SOLUTION)
print("fill:\n" + FILL_OUT)
FILL_NO_STRIDE_IN_SLICE = FILL_SOLUTION.replace("            patch = image[y * stride : y * stride + k, x * stride : x * stride + k]", "            patch = image[y : y + k, x : x + k]")
FILL_OFF_BY_ONE = FILL_SOLUTION.replace("    h_out = (image.shape[0] - k) // stride + 1\n    w_out = (image.shape[1] - k) // stride + 1", "    h_out = (image.shape[0] - k) // stride\n    w_out = (image.shape[1] - k) // stride")
assert differs(FILL_NO_STRIDE_IN_SLICE, FILL_OUT) and differs(FILL_OFF_BY_ONE, FILL_OUT)

# --- the write ----------------------------------------------------------------------------------

WRITE_SOLUTION = '''import numpy as np


def max_pool(X, size=2):
    """Pool every image in X (n, h, w) over size-by-size windows: the pooled array (n, h // size, w // size) and a boolean mask of where each window's maximum sat."""
    n, h, w = X.shape
    windows = X.reshape(n, h // size, size, w // size, size)
    pooled = windows.max(axis=(2, 4))
    mask = windows == pooled[:, :, None, :, None]
    return pooled, mask


def max_pool_backward(mask, grad_out):
    """Send each pooled cell's gradient back to the cell that won its window; every other cell gets zero."""
    n, h_out, size, w_out, _ = mask.shape
    return (mask * grad_out[:, :, None, :, None]).reshape(n, h_out * size, w_out * size)


X = np.array([[[2.0, 7.0, 1.0, 0.0], [4.0, 3.0, 5.0, 8.0], [0.0, 1.0, 9.0, 2.0], [6.0, 0.0, 3.0, 3.0]]])
pooled, mask = max_pool(X)
print(pooled[0].tolist())
print(max_pool_backward(mask, np.array([[[1.0, 2.0], [3.0, 4.0]]]))[0].tolist())
'''
WRITE_TAIL = "X = np.array" + WRITE_SOLUTION.split("\n\n\nX = np.array", 1)[1]
WRITE_OUT = out(WRITE_SOLUTION)
assert WRITE_OUT == "[[7.0, 8.0], [6.0, 9.0]]\n[[0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 0.0, 2.0], [0.0, 0.0, 4.0, 0.0], [3.0, 0.0, 0.0, 0.0]]\n", WRITE_OUT
WRITE_AVERAGES = WRITE_SOLUTION.replace("    pooled = windows.max(axis=(2, 4))", "    pooled = windows.mean(axis=(2, 4))")
WRITE_SPREADS = WRITE_SOLUTION.replace("    return (mask * grad_out[:, :, None, :, None]).reshape(n, h_out * size, w_out * size)", "    return (np.ones_like(mask) * grad_out[:, :, None, :, None]).reshape(n, h_out * size, w_out * size)")
assert differs(WRITE_AVERAGES, WRITE_OUT) and differs(WRITE_SPREADS, WRITE_OUT)

# --- the build ----------------------------------------------------------------------------------

BUILD_TAIL = '''

image = np.zeros((6, 6))
image[:, 3:] = 1.0
vertical = np.array([[-1.0, 0.0, 1.0], [-1.0, 0.0, 1.0], [-1.0, 0.0, 1.0]])
print(correlate2d(image, vertical)[0].tolist(), correlate2d(image, vertical, padding=1).shape, correlate2d(image, vertical, stride=2).shape)
rng = np.random.default_rng(0)
images = rng.standard_normal((5, 8, 8))
labels = rng.integers(0, 3, size=5)
net = Sequential([Conv2D(4, 3, seed=1), ReLU(), MaxPool2D(2), Flatten(), Dense(36, 3, seed=2)])
loss = SoftmaxCrossEntropy()
print(net.forward(images).shape, gradient_check(net, loss, images, labels) < 1e-6, input_gradient_check(net, loss, images, labels) < 1e-6, sum(p.size for p in net.parameters()))
X_train, y_train = make_bars(100, seed=1)
X_test, y_test = make_bars(100, seed=2)
net = Sequential([Conv2D(4, 3, seed=1), ReLU(), MaxPool2D(2), Flatten(), Dense(36, 2, seed=2)])
for step in range(300):
    loss.forward(net.forward(X_train), y_train)
    net.backward(loss.backward())
    for param, grad in zip(net.parameters(), net.gradients()):
        param -= 0.1 * grad
print(round(float((net.forward(X_test).argmax(axis=1) == y_test).mean()), 2))
'''
BUILD_SOLUTION = "import numpy as np\n\n\n" + MODULE + CONV + BUILD_TAIL
BUILD_OUT = out(BUILD_SOLUTION)
print("build:\n" + BUILD_OUT)
BUILD_LINES = BUILD_OUT.splitlines()
assert BUILD_LINES[0] == "[0.0, 3.0, 3.0, 0.0] (6, 6) (2, 2)" and BUILD_LINES[1] == "(5, 3) True True 151", BUILD_OUT
assert float(BUILD_LINES[2]) >= 0.95, BUILD_OUT
assert out(BUILD_SOLUTION.replace("X_train, y_train = make_bars(100, seed=1)", "X_train, y_train = make_bars(100, seed=1)\nX_train[0, 0, 0] += 1e-10")) == BUILD_OUT
BUILD_WRONGS = {
    "weights-transposed-in-backward": BUILD_SOLUTION.replace("                self.dW[:, i, j] = (grad_out * patch[:, None]).sum(axis=(0, 2, 3))", "                self.dW[:, j, i] = (grad_out * patch[:, None]).sum(axis=(0, 2, 3))"),
    "pool-spreads-the-gradient": BUILD_SOLUTION.replace("        spread = self.mask * grad_out[:, :, :, None, :, None]", "        spread = np.ones_like(self.mask) * grad_out[:, :, :, None, :, None]"),
    "forgets-the-bias": BUILD_SOLUTION.replace("        return out + self.b[None, :, None, None]", "        return out"),
    "stride-ignored-in-the-slice": BUILD_SOLUTION.replace("            patch = image[y * stride : y * stride + k, x * stride : x * stride + k]", "            patch = image[y : y + k, x : x + k]"),
}
for key, code in BUILD_WRONGS.items():
    assert code != BUILD_SOLUTION, key

# --- the debug ----------------------------------------------------------------------------------

DEBUG_SOLUTION = "import numpy as np\n\n\n" + MODULE + CONV + '''

block = np.array([[[[1.0, 2.0, 5.0, 6.0], [3.0, 4.0, 7.0, 8.0], [9.0, 10.0, 13.0, 14.0], [11.0, 12.0, 15.0, 16.0]]]])
pool = MaxPool2D(2)
pooled = pool.forward(block)
print("pooling a 4x4:", pooled[0, 0].tolist(), "| cells that get gradient:", int((pool.backward(np.ones((1, 1, 2, 2))) != 0).sum()))
rng = np.random.default_rng(0)
images = rng.standard_normal((5, 8, 8))
labels = rng.integers(0, 3, size=5)
net = Sequential([Conv2D(4, 3, seed=1), ReLU(), MaxPool2D(2), Flatten(), Dense(36, 3, seed=2)])
loss = SoftmaxCrossEntropy()
print("gradient check of the parameters:", "passes" if gradient_check(net, loss, images, labels) < 1e-6 else "fails", "| of the input:", "passes" if input_gradient_check(net, loss, images, labels) < 1e-6 else "fails")
'''
BUG_POOL = ("        spread = self.mask * grad_out[:, :, :, None, :, None]", "        spread = grad_out[:, :, :, None, :, None] * np.ones((1, 1, 1, s, 1, s))")
BUG_CONV = (
    "                grad_in[:, i : i + h_out, j : j + w_out] += (grad_out * self.W[None, :, i, j, None, None]).sum(axis=1)",
    "                grad_in[:, i : i + h_out, j : j + w_out] += (grad_out * self.W[None, :, j, i, None, None]).sum(axis=1)",
)
DEBUG_STARTER = DEBUG_SOLUTION.replace(*BUG_POOL).replace(*BUG_CONV)
DEBUG_STILL_POOL = DEBUG_SOLUTION.replace(*BUG_POOL)
DEBUG_STILL_CONV = DEBUG_SOLUTION.replace(*BUG_CONV)
assert DEBUG_STARTER != DEBUG_STILL_POOL != DEBUG_SOLUTION != DEBUG_STILL_CONV
DEBUG_OUT = out(DEBUG_SOLUTION)
STARTER_OUT = out(DEBUG_STARTER)
print("debug:\n" + DEBUG_OUT + "starter:\n" + STARTER_OUT)
assert DEBUG_OUT == "pooling a 4x4: [[4.0, 8.0], [12.0, 16.0]] | cells that get gradient: 4\ngradient check of the parameters: passes | of the input: passes\n", DEBUG_OUT
assert STARTER_OUT == "pooling a 4x4: [[4.0, 8.0], [12.0, 16.0]] | cells that get gradient: 16\ngradient check of the parameters: fails | of the input: fails\n", STARTER_OUT
assert out(DEBUG_STILL_POOL).endswith("fails | of the input: fails\n") and out(DEBUG_STILL_CONV).endswith("passes | of the input: fails\n")

REVIEW_CODE_SOLUTION = '''import numpy as np


def correlate2d(image, kernel):
    """Slide the kernel over the image; each output cell is the sum of the kernel times the patch under it."""
    k = kernel.shape[0]
    h_out, w_out = image.shape[0] - k + 1, image.shape[1] - k + 1
    out = np.zeros((h_out, w_out))
    for y in range(h_out):
        for x in range(w_out):
            out[y, x] = (image[y : y + k, x : x + k] * kernel).sum()
    return out


image = np.array([[1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0], [9.0, 10.0, 11.0, 12.0]])
print(correlate2d(image, np.array([[1.0, -1.0], [1.0, -1.0]])).tolist())
print(correlate2d(image, np.array([[0.0, 1.0, 0.0], [1.0, 0.0, 1.0], [0.0, 1.0, 0.0]])).tolist())
'''
REVIEW_CODE_OUT = out(REVIEW_CODE_SOLUTION)
assert REVIEW_CODE_OUT == "[[-2.0, -2.0, -2.0], [-2.0, -2.0, -2.0]]\n[[24.0, 28.0]]\n", REVIEW_CODE_OUT
REVIEW_CODE_WRONG = REVIEW_CODE_SOLUTION.replace("            out[y, x] = (image[y : y + k, x : x + k] * kernel).sum()", "            out[y, x] = (image[x : x + k, y : y + k] * kernel).sum()")
assert differs(REVIEW_CODE_WRONG, REVIEW_CODE_OUT)

# =====================================================================================
# topic.yaml
# =====================================================================================

write(
    "topic.yaml",
    '''id: ml.nn.convolution
kind: topic
status: ready
title: "Convolutions: a layer that reads images"
summary: "A 2-D cross-correlation by hand, a kernel as a feature detector, padding and stride, why a convolutional layer has far fewer parameters than a dense one on an image, pooling, and the forward and backward pass of a single-channel convolutional layer checked numerically."
prerequisites: [ml.nn.backward-layers]
packages: [numpy]
estimated_minutes: 60
rev: 1
objectives:
  - "Compute a 2-D cross-correlation by hand and in code, and say what an edge-detecting kernel does."
  - "Count the parameters of a convolutional layer against a dense layer on the same image, and say where the saving comes from."
  - "Implement the forward and backward pass of a single-channel convolutional layer and gradient-check it."
  - "Say what padding, stride and pooling do to the shape and to what the network can see."
# Linked, never copied or embedded: Wikipedia is CC BY-SA 4.0; the video is
# under YouTube's standard licence.
resources:
  - title: "3Blue1Brown: But what is a convolution? (the sliding window, image kernels from the 8-minute mark, and why blurring and edge detection are the same operation with different numbers)"
    url: https://www.youtube.com/watch?v=KuXjwB4LzSA
    type: video
    use: link
    license: Standard YouTube licence (linked, not embedded)
  - title: "Wikipedia: Kernel (image processing) (the table of kernels with their pictures, and the Convolution section)"
    url: https://en.wikipedia.org/wiki/Kernel_(image_processing)
    type: reading
    use: link
    license: CC BY-SA 4.0 (linked, not copied)
  - title: "Wikipedia: Convolutional neural network (the Architecture section: convolutional layers, pooling, receptive field, shared weights)"
    url: https://en.wikipedia.org/wiki/Convolutional_neural_network
    type: reading
    use: link
    license: CC BY-SA 4.0 (linked, not copied)
practice:
  - example-a-layer-that-reads-images
  - predict-a-cross-correlation
  - mcq-what-an-edge-kernel-does
  - parsons-correlate
  - predict-shapes
  - mcq-padding
  - predict-parameter-counts
  - mcq-where-the-saving-comes-from
  - predict-a-conv-forward
  - mcq-the-backward-pass
  - predict-max-pooling
  - mcq-what-pooling-and-stride-do
  - fill-correlate2d
  - write-max-pool
prove:
  build: build-a-convolutional-layer
  debug: debug-a-layer-that-fails-its-gradient-check
  explain:
    prompt: |
      A teammate has used a library's `Conv2d` for a year without looking inside. They ask: what does the layer actually compute, and why does the kernel `[[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]]` light up at vertical edges? Why does a convolutional layer have so few parameters next to a dense layer on the same image, and what does it give up for that? How does the gradient get back to a kernel's nine numbers when each is used at every position? And what do pooling and stride do to a network, and why would anyone throw resolution away? Answer in your own words.
    rubric:
      - id: cross-correlation
        required: true
        description: "The layer slides a small kernel over the image and at each position takes the sum of the kernel times the patch under it (a cross-correlation, what libraries call a convolution); a kernel is a pattern, and the output is large where the patch looks like it. The vertical-edge kernel subtracts the left column from the right, so it is zero on flat regions and horizontal edges, positive where the image brightens to the right and negative where it darkens."
      - id: parameters
        required: true
        description: "The same k-by-k weights are used at every position (weight sharing) and each output cell reads only its patch (locality), so the count is kernels times k squared plus biases, independent of the image's size, while a dense layer needs a weight per input pixel per output. It gives up weights that differ by position, which is the right trade when a feature looks the same wherever it appears."
      - id: backward
        required: true
        description: "Each kernel weight's gradient is the sum, over every position it was used at, of the output gradient there times the input pixel it multiplied: a cross-correlation of the input with the output gradient. The gradient for the input spreads each output cell's gradient back over its patch through the kernel's weights, and the gradient check (central differences) confirms both."
      - id: shapes
        required: true
        description: "Padding keeps the output the same size and lets edge pixels be seen as often as the middle; stride skips positions and shrinks the output; max pooling keeps the strongest response in each window and halves the map. Shrinking makes each later cell see a larger region of the original, gives a little tolerance to shifts, and costs exact position and compute, which is the point: later layers want what is there more than exactly where."
    model_answer: |
      A convolutional layer slides a small grid of numbers, the kernel, over the image, and at every position multiplies the kernel by the patch of pixels under it and adds up the products: one number per position, so the output is another image, a little smaller. (Strictly this is a cross-correlation; a true convolution flips the kernel first, and since the kernel is learned the flip makes no difference, so libraries call it a convolution.) The kernel is a pattern, and the output says how much each patch looks like the pattern. The vertical-edge kernel has -1 down its left column, 0 in the middle and +1 down the right, so at each position it subtracts what is to the left from what is to the right. On a flat region the two cancel and the output is zero; on a horizontal edge the left and right columns are the same, so it is zero again; only where the image changes from left to right does it respond, positive if it brightens to the right and negative if it darkens, which is why it lights up at vertical edges and tells you which way they face. The parameters are so few because the same nine numbers are reused at every position, instead of a separate weight for each pair of input and output pixel: eight 3-by-3 kernels on a 28-by-28 image are 80 parameters where a dense layer from the image to a 28-by-28 output is 615,440, and the convolution's count does not grow with the image at all. That reuse is a bet that a feature looks the same wherever it appears, and it also means each output reads only its own patch, so a single layer cannot relate pixels far apart; what the layer gives up is position-specific weights, which for images are rarely wanted. The gradient reaches a shared weight by adding up: the weight at kernel position (i, j) multiplied the pixel offset by (i, j) at every output position, so its gradient is the sum over all positions of the output gradient there times that pixel, which is itself a cross-correlation of the input with the output gradient. The gradient for the input runs the other way: each output cell's gradient is spread back over the patch it read, scaled by the kernel's weights, and a cell that several outputs read gets their contributions added. A numeric gradient check, nudging each weight up and down and watching the loss, confirms both against the code. Pooling keeps the largest value in each 2-by-2 window and halves the map; stride makes the kernel skip positions and shrinks the map too; padding with a border of zeros does the opposite and keeps the size. Throwing resolution away buys three things: each cell of the next layer now sees a larger region of the original image, so patterns bigger than the kernel can be detected; a response survives a shift of a pixel, since the maximum of a window does not care where in the window it sat; and the computation shrinks. The cost is exact position, which later layers rarely need: they want to know a feature is there more than exactly where.
review_pool:
  - review-predict-an-edge
  - review-mcq-parameters
  - review-mcq-pool-backward
  - review-correlate2d
# What this topic teaches. Each question names the skills it tests, so a
# missed question can come back as a different one on the same skill
# (ADR-0011).
skills:
  - id: cross-correlation
    description: "Compute a 2-D cross-correlation by hand and in code, and say what an edge kernel does"
  - id: parameters
    description: "Count a convolutional layer's parameters against a dense layer's, and say where the saving comes from"
  - id: conv-layer
    description: "Implement the forward and backward pass of a single-channel convolutional layer and gradient-check it"
  - id: shapes
    description: "Say what padding, stride and pooling do to the shape and to what the network can see"
''',
)

# =====================================================================================
# lesson.mdx
# =====================================================================================

write(
    "lesson.mdx",
    f'''<Intro>

A dense layer on an image needs a weight for every pair of input pixel and output, and treats the top-left corner and the middle as unrelated places. A **convolutional layer** instead slides one small grid of weights, a **kernel**, over the whole image and reads the same pattern everywhere, which is how every network that looks at pictures begins. This topic computes the sliding sum by hand, builds the layer with its backward pass in a few dozen lines of NumPy, checks it numerically, and trains it to tell a horizontal bar from a vertical one.

The main resource is **3Blue1Brown's _But what is a convolution?_** (23 minutes): the sliding window, image kernels from about the 8-minute mark, and why a blur and an edge detector are the same operation with different numbers. Wikipedia's _Kernel (image processing)_ page has a table of kernels with the picture each one makes, and the _Convolutional neural network_ page's Architecture section names the parts. Watch for:

- **The sliding sum**: multiply the kernel by the patch under it, add up, move one pixel, repeat.
- **Shared weights**: the same kernel at every position.
- **Pooling**: keeping the strongest response in each window.

</Intro>

<Resource index={{0}} />

<Recap>

- **A cross-correlation** slides a kernel over an image and, at each position, sums the kernel times the patch under it. `correlate2d` is two loops over output positions and one multiply-and-sum each. A true **convolution** flips the kernel first; for a learned kernel the flip changes nothing, so libraries say convolution and compute this.
- **A kernel is a feature detector.** The example's vertical-edge kernel, -1 down the left column and +1 down the right, gives 0 on flat regions and on horizontal edges, and 3 along the edge where the image goes from 0 to 1 (three rows of 1 - 0): the output says where the pattern is and, by its sign, which way it faces. A network learns its kernels; edge and blob detectors are what the first layer usually ends up with.
- **Shapes.** A k-wide kernel over n pixels gives n - k + 1 outputs (6 - 3 + 1 = 4). **Padding** the image with a border of zeros keeps the size (padding 1 for a 3-wide kernel) and lets edge pixels be read as often as the middle. **Stride** moves the kernel more than one pixel at a time and shrinks the output: `(n + 2 * padding - k) // stride + 1`.
- **Parameters.** A convolutional layer has `n_kernels * k * k + n_kernels` parameters, whatever the image's size: eight 3-by-3 kernels are 80. A dense layer from a 28-by-28 image to a 28-by-28 output is 615,440. The saving comes from **weight sharing** (the same kernel at every position) and **locality** (each output reads one patch); what it gives up is weights that differ by position, which images rarely want. The dense layer at the end of a small network is usually where most of its parameters are.
- **The layer.** (`Dense`, `ReLU`, `Sequential` and the loss are as Layers that carry their gradient left them.) `Conv2D` keeps `n_kernels` kernels `W` of shape `(n_kernels, k, k)` and a bias per kernel; its forward loops over the k-by-k offsets `(i, j)`, and for each adds the input shifted by `(i, j)` times weight `(i, j)`, giving one **feature map** per kernel: `(N, n_kernels, H - k + 1, W - k + 1)`. The backward pass loops over the same offsets: `dW[:, i, j]` is the sum over every position of the output gradient times the shifted input (a cross-correlation of the input with the output gradient), `db` sums the output gradient, and the input gradient accumulates each output gradient times weight `(i, j)` back onto the cells it read. `gradient_check` and `input_gradient_check` compare both with central differences.
- **Shift equivariance.** A bar two rows lower gives the same feature map two rows lower: the layer finds a pattern wherever it is, which is exactly what sharing the kernel buys.
- **Pooling and stride.** `MaxPool2D(2)` keeps the largest value in each 2-by-2 window and halves the height and width; its backward sends each pooled cell's gradient to the cell that won (every tied cell, in this code) and zero to the rest. Shrinking the map makes each cell of the next layer see a larger region of the original (a 3-by-3 kernel after a 2-by-2 pool sees 8 by 8, against 5 by 5 without it), lets a response survive a shift of a pixel, and cuts the computation; the cost is exact position, which later layers rarely need. `Flatten` turns the maps into rows so a `Dense` layer can finish.
- **Learning.** On noisy 8-by-8 images of bars, four kernels, a pool and a dense layer (114 parameters) go from a loss of {BARS_FIRST} to {BARS_LAST} in 300 steps of plain gradient descent and classify {BARS_ACC:.0%} of held-out images: the kernels learn the bars.
- **In machine learning** (names you'll meet later): `nn.Conv2d(in_channels, out_channels, kernel_size, stride, padding)` is this layer with **channels**, a sum over input channels per kernel (this topic's layer has one input channel; the three of an RGB image or the maps of a previous layer add a loop and a sum); `nn.MaxPool2d` and `nn.Flatten` are the other two; the **receptive field** is the region of the original image a cell sees; and libraries don't loop, they reshape patches into a matrix (`im2col`) so the whole layer is one matrix multiply, or call cuDNN, which Module 7's GPUs run.

</Recap>
''',
)

# =====================================================================================
# recall
# =====================================================================================

write(
    "recall/predict-a-cross-correlation.yaml",
    f'''id: predict-a-cross-correlation
type: predict_output
rev: 1
prompt: |
  A 3-by-3 image and a 2-by-2 kernel, slid over it with two loops: at each of the four positions, the sum of the kernel times the patch under it. What does the program print?
code: |
{block(PREDICT_CORRELATION)}expected_output: |
{block(PREDICT_CORRELATION_OUT)}explanation: |
  Top-left patch [[1, 2], [0, 1]]: 1 + 4 + 0 - 1 = 4. Top-right [[2, 0], [1, 3]]: 2 + 0 + 0 - 3 = -1. Bottom-left [[0, 1], [2, 0]]: 0 + 2 + 0 - 0 = 2. Bottom-right [[1, 3], [0, 1]]: 1 + 6 + 0 - 1 = 6. A 3-wide image and a 2-wide kernel give 3 - 2 + 1 = 2 positions each way.
skills: [cross-correlation]
''',
)

mcq(
    "mcq-what-an-edge-kernel-does",
    "The kernel [[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]] is slid over an image. Where is its output large, and what does the sign say?",
    [
        "Wherever the image is bright, since the kernel sums the patch under it",
        "At vertical edges, where the columns to the right of a pixel differ from those to its left; positive when the image brightens to the right, negative the other way",
        "At horizontal edges, since the three rows of the kernel are identical and so the kernel compares the rows above a pixel with the rows below it, giving a large value wherever they differ",
        "Nowhere: its entries sum to zero, so its output is zero on every patch",
    ],
    1,
    "Each row of the kernel takes the pixel to the right minus the pixel to the left, and the three rows add up. A flat patch gives zero, and so does a horizontal edge, where left and right columns are the same. Only a change from left to right registers: three rows of (1 - 0) gave 3 in the example. The entries summing to zero is what makes flat regions give zero; edges don't.",
    ["cross-correlation"],
)

write(
    "recall/parsons-correlate.yaml",
    "id: parsons-correlate\ntype: parsons\nrev: 1\nprompt: |\n"
    + block("Put the lines in order to slide a 2-by-2 kernel over a 3-by-3 image and print the 2-by-2 output `[[4.0, 6.0], [10.0, 12.0]]`. One line is a decoy that doesn't belong.")
    + "lines:\n"
    + "".join(f"  - {quoted(line)}\n" for line in PARSONS_LINES)
    + "distractors:\n  - "
    + quoted("        out[y, x] = (image[x:x + 2, y:y + 2] * kernel).sum()")
    + "\nexplanation: |\n"
    + block("The output's size comes from the image's, so the image and kernel come first, then the empty output, then the two loops over output positions with the multiply-and-sum inside, then the print. The decoy swaps y and x in the slice, so the output comes out transposed: on this image the result would be [[4.0, 10.0], [6.0, 12.0]].")
    + "skills: [cross-correlation]\n",
)

write(
    "recall/predict-shapes.yaml",
    f'''id: predict-shapes
type: predict_output
rev: 1
prompt: |
  `output_size` gives the height (or width) of a convolution's output from the input size, the kernel size, the padding and the stride. What does the program print?
code: |
{block(PREDICT_SHAPES)}expected_output: |
{block(PREDICT_SHAPES_OUT)}explanation: |
  A 3-wide kernel over 28 pixels fits in 26 places; padding by 1 adds two pixels and brings it back to 28, as padding by 2 does for a 5-wide kernel. A stride of 2 takes every other position: (28 - 3) // 2 + 1 = 13, and a 2-wide kernel with stride 2 over 32 pixels tiles it exactly, 16 times.
skills: [shapes]
''',
)

mcq(
    "mcq-padding",
    "Why pad an image with a border of zeros before a 3-by-3 convolution?",
    [
        "So the output keeps the image's size and the edge pixels are read as often as the middle ones; without it each layer shrinks the map by two",
        "To make the kernel larger",
        "To make the convolution faster, since the padded zeros multiply to zero and the sums at the border can be skipped, which saves the time that would otherwise go to the edge pixels of the image",
        "To stop the kernel from reading outside the image, which would crash",
    ],
    0,
    "A 3-wide kernel fits n - 2 times across n pixels, so without padding a map loses two pixels a layer and a corner pixel is read by one position only. A border of one zero on each side gives n positions again and lets the kernel centre on every pixel. The kernel's size is unchanged, the sums aren't skipped, and the unpadded version doesn't crash, it just shrinks.",
    ["shapes"],
)

write(
    "recall/predict-parameter-counts.yaml",
    f'''id: predict-parameter-counts
type: predict_output
rev: 1
prompt: |
  A convolutional layer has one k-by-k kernel and one bias per output map; a dense layer has a weight per input per output and a bias per output. What does the program print?
code: |
{block(PREDICT_PARAMS)}expected_output: |
{block(PREDICT_PARAMS_OUT)}explanation: |
  Sixteen 5-by-5 kernels are 400 weights and 16 biases; thirty-two 3-by-3 kernels are 288 and 32. The dense layers are far bigger: 1,024 inputs to 10 outputs is 10,250, and the 16 maps of 14-by-14 that a small network flattens are 3,136 inputs, 31,370 parameters into 10 outputs. The dense layer at the end is where a small network's parameters live.
skills: [parameters]
''',
)

mcq(
    "mcq-where-the-saving-comes-from",
    "A dense layer from a 28-by-28 image to a 28-by-28 output has 615,440 parameters; eight 3-by-3 kernels have 80. Where does the saving come from, and what does it give up?",
    [
        "The same nine weights are used at every position (sharing) and each output reads only a 3-by-3 patch (locality); it gives up weights that differ by position, fine when a feature looks the same wherever it is",
        "The kernels are smaller than the image, so the layer reads only the pixels under the kernel's first placement and gives up the rest of the image; the saving comes from the pixels that are never read, which is fine when the subject is in the top-left corner",
        "Convolutions are linear and dense layers aren't, so the convolution needs fewer numbers",
        "The eight kernels share one bias, which is where most of the saving is",
    ],
    0,
    "The dense layer has a separate weight for every pair of input pixel and output pixel. The convolution has nine weights per kernel, reused at all 676 positions, and each output looks at its own patch rather than the whole image. Every pixel is read, by every position whose patch covers it. Both layers are linear, and the biases are eight numbers either way.",
    ["parameters"],
)

write(
    "recall/predict-a-conv-forward.yaml",
    f'''id: predict-a-conv-forward
type: predict_output
rev: 1
prompt: |
  `Conv2D.forward` written out for one 3-by-3 image and two 2-by-2 kernels: a loop over the kernel's four offsets, each adding the image shifted by that offset times one weight. What does the program print?
code: |
{block(PREDICT_CONV)}expected_output: |
{block(PREDICT_CONV_OUT)}explanation: |
  The output is one image, two maps, 2-by-2 each. Kernel 0 has 1s on its diagonal, so each output cell is the pixel under the top-left plus the pixel under the bottom-right: 1 + 5, 2 + 6, 4 + 8, 5 + 9. Kernel 1 has a single 1 at offset (0, 1), so its map is the image shifted left by one: the pixel to the right of each position.
skills: [conv-layer]
''',
)

mcq(
    "mcq-the-backward-pass",
    "A 3-by-3 kernel's weight W[0, 0] is used at every output position. What is its gradient, and how does the gradient reach the input?",
    [
        "The output gradient at the one position where W[0, 0] mattered most, since a weight can only have one gradient",
        "The sum over every output position of the output gradient there times the input pixel W[0, 0] met: a correlation of the input with the output gradient; each output gradient is spread back onto its 3-by-3 patch through the kernel's weights",
        "The average of the output gradients, since the weight was shared equally among the positions and each position should count the same; the input gradient is the output gradient copied to every pixel of the patch, with no weights involved, because the weights belong to the kernel and not to the input",
        "Zero, because the weight is shared and the contributions from different positions cancel",
    ],
    1,
    "A shared weight has one gradient that adds up every place it was used, as a Dense weight's gradient adds up every row of the batch. For offset (0, 0) that is the output gradient at each position times the pixel at that position, which is a cross-correlation. Going back, an input cell was read by up to nine output positions, each through a different weight, and its gradient is the sum of those. Nothing is averaged and nothing cancels.",
    ["conv-layer"],
)

write(
    "recall/predict-max-pooling.yaml",
    f'''id: predict-max-pooling
type: predict_output
rev: 1
prompt: |
  Max pooling a 4-by-4 with 2-by-2 windows by reshaping into windows and taking the maximum, then counting the cells that equal their window's maximum: the cells a gradient would go back to. What does the program print?
code: |
{block(PREDICT_POOL)}expected_output: |
{block(PREDICT_POOL_OUT)}explanation: |
  The reshape groups the rows in pairs and the columns in pairs, so each window is a 2-by-2 block: the top-left block [[2, 7], [4, 3]] has maximum 7, then 8, 6 and 9. Exactly one cell per window matches its maximum here, so four cells would receive gradient and the other twelve none.
skills: [shapes]
''',
)

mcq(
    "mcq-what-pooling-and-stride-do",
    "A 3-by-3 convolution, then a 2-by-2 max pool, then another 3-by-3 convolution. What has the pool done?",
    [
        "Halved the map's height and width, let each cell of the second convolution see an 8-by-8 region of the original instead of 5-by-5, and made the response tolerate a shift of a pixel, at the cost of exact position",
        "Doubled the number of parameters in the second convolution, since its kernel now has to cover twice the region of the original image to see the same thing, and it needs to be a 6-by-6 kernel to make up for the pooling",
        "Nothing to the shapes: pooling only removes noise by averaging",
        "Averaged each window's four cells, which blurs the map and loses the strongest response",
    ],
    0,
    "Each pooled cell covers 2-by-2 cells of the first map, which cover 4-by-4 pixels; a 3-by-3 kernel over pooled cells spans 6 of the first map's cells and so 8 pixels. The second kernel is still 3-by-3 with the same parameter count. Max is not linear and is not an average; it keeps the strongest response, which survives a shift inside its window.",
    ["shapes"],
)

write(
    "recall/review-predict-an-edge.yaml",
    f'''id: review-predict-an-edge
type: predict_output
rev: 1
prompt: |
  A 4-by-4 image that is dark on the left and bright on the right, and a 2-by-2 kernel that subtracts each left pixel from its right neighbour. What does the program print?
code: |
{block(REVIEW_PREDICT)}expected_output: |
{block(REVIEW_PREDICT_OUT)}explanation: |
  A 2-wide kernel over 4 pixels gives 3 positions each way. In row 0, the first patch is all zeros and the last all ones, and both give 0 (the kernel's entries cancel on a flat patch); the middle patch straddles the edge, 1 - 0 in each of its two rows, so 2. The edge shows up as a column of 2s.
skills: [cross-correlation]
''',
)

mcq(
    "review-mcq-parameters",
    "A convolutional layer with 32 kernels of 5-by-5 on a 64-by-64 image, against a dense layer from the 64-by-64 image to a 64-by-64 output. How many parameters each?",
    [
        "832 and 16,781,312: the convolution's count doesn't depend on the image's size at all",
        "832 and 16,777,216: the convolution reads just the 5-by-5 region in the middle of the image, and the dense layer's biases aren't counted, since they aren't multiplied by anything",
        "32 times 64 times 64, which is 131,072, and 16,781,312",
        "832 and 4,096",
    ],
    0,
    "Thirty-two kernels of 25 weights plus 32 biases is 832, and it would be 832 on a 640-by-640 image too, because the kernels are reused at every position and cover the whole image by sliding. The dense layer needs 4,096 weights for each of 4,096 outputs plus 4,096 biases: 16,781,312.",
    ["parameters"],
)

mcq(
    "review-mcq-pool-backward",
    "Max pooling has no parameters. In the backward pass, where does a pooled cell's gradient go?",
    [
        "To the one input cell that was its window's maximum; the others get zero, since they didn't affect the output",
        "Spread equally over the window's four cells, since each of them was a candidate for the maximum and should learn to be the one that wins next time",
        "To all four cells, scaled by their values",
        "Nowhere: a layer with no parameters has nothing to learn, so it stops the gradient",
    ],
    0,
    "The output was the maximum, so nudging any other cell of the window (by less than the gap) changes nothing: their derivative is zero. The winner's derivative is one, so it receives the whole gradient. The layer has no parameters of its own, but the gradient must still pass through it to reach the convolution underneath.",
    ["shapes"],
)

# =====================================================================================
# exercises
# =====================================================================================

write(
    "exercises/example-a-layer-that-reads-images/exercise.yaml",
    f'''id: example-a-layer-that-reads-images
stage: worked_example
rev: 1
title: "A layer that reads images"
prompt: |
  A kernel slid over a vertical edge, the parameter count against a dense layer, a convolutional layer with its backward pass checked against the sliding sum, against a shift and numerically, max pooling with its gradient, and a small network that learns to tell a horizontal bar from a vertical one. Press **Run**, then read how each part works.
steps:
  - label: "The sliding sum"
    lines: "{ln('def correlate2d')}-{ln('return out')}"
    note: "`correlate2d` pads the image with zeros if asked, works out how many positions the kernel fits in each direction, and at each position multiplies the kernel by the patch under it and adds up. That sum is what every library calls a convolution."
  - label: "The layer and its backward pass"
    lines: "{ln('class Conv2D:')}-{ln('return [self.dW, self.db]', ln('class Conv2D:'))}"
    note: "Rather than loop over every output position, `forward` loops over the kernel's k-by-k offsets: the input shifted by (i, j) times weight (i, j), added into every output cell at once, one feature map per kernel. `backward` loops over the same offsets: weight (i, j)'s gradient sums the output gradient times the shifted input over every position, and each output gradient flows back onto the cells it read, through weight (i, j)."
  - label: "Pooling and flattening"
    lines: "{ln('class MaxPool2D:')}-{ln('return []', ln('def gradients', ln('class Flatten:')))}"
    note: "`MaxPool2D` reshapes each map into 2-by-2 windows and keeps each window's maximum, remembering which cell won; `backward` gives the gradient to that cell and zero to the rest. `Flatten` turns maps into rows so a `Dense` layer can follow, and reshapes the gradient back."
  - label: "An edge and two kernels"
    lines: "{ln('image = np.zeros((6, 6))')}-{ln('print("valid:"')}"
    note: "The image is 0 on the left and 1 on the right. The vertical-edge kernel (-1 down its left column, +1 down its right) gives 3 at the two positions that straddle the edge and 0 elsewhere; its transpose, which compares rows, gives 0 everywhere, because every row is the same. Valid output is 6 - 3 + 1 = 4 wide; padding by 1 keeps 6; a stride of 2 halves it."
  - label: "Parameters"
    lines: "{ln('dense_params = ')}-{ln('ratio {dense_params')}"
    note: "A dense layer from 784 pixels to 784 outputs is 784 squared weights plus 784 biases. Eight 3-by-3 kernels are 72 weights and 8 biases, whatever the image's size: the kernels are reused at every position and each output reads one patch."
  - label: "The layer, checked three ways"
    lines: "{ln('rng = np.random.default_rng(0)')}-{ln('gradient check of the parameters')}"
    note: "Kernel 1's map for image 2 equals `correlate2d` of that image with that kernel plus its bias. A bar two rows lower gives the same feature map two rows lower. And with the layer inside a small network (convolution, ReLU, pool, flatten, dense), both gradient checks pass: every parameter's gradient and the gradient handed back for the input agree with central differences."
  - label: "Pooling a 4-by-4"
    lines: "{ln('block = np.array')}-{ln('where a gradient of 1')}"
    note: "The four 2-by-2 windows have maxima 4, 8, 12 and 16. A gradient of 1 per pooled cell goes back to exactly those four cells; the other twelve get 0, because nudging them would not have changed the output."
  - label: "Learning the bars"
    lines: "{ln('X_train, y_train = make_bars(100, seed=1)')}-{ln('bars: training loss')}"
    note: "A hundred noisy 8-by-8 images, half with a horizontal bar and half with a vertical one, at random positions. Four kernels, a pool and a dense layer, 114 parameters in all, trained by 300 steps of plain gradient descent on the whole batch, go from a loss of {BARS_FIRST} to {BARS_LAST} and classify {BARS_ACC:.0%} of a hundred held-out images: the kernels have learned the bars, wherever they are."
''',
)
write("exercises/example-a-layer-that-reads-images/solution.py", EXAMPLE)
write(
    "exercises/example-a-layer-that-reads-images/test_exercise.py",
    f'''from checks import run


def test_the_walkthrough():
    """Prints the edge, the shapes, the counts, the checks, the pooling and the bars."""
    assert run() == {EXAMPLE_OUT!r}
''',
)

write(
    "exercises/fill-correlate2d/exercise.yaml",
    f'''id: fill-correlate2d
stage: fill_in
rev: 1
title: "The sliding sum, with padding and stride"
prompt: |
  `correlate2d` should slide the kernel over the image (padded with zeros by `padding` on every side), moving `stride` pixels at a time, and at each position take the sum of the kernel times the patch under it. Replace each `...` so the program prints the first row of the valid output, the padded output's shape and the stride-2 output:

  ```
{block(FILL_OUT)}  ```

  The program fails until every `...` is replaced.
hints:
  - "The number of positions is `(size - k) // stride + 1`: how many times the kernel fits when it moves `stride` at a time."
  - "Output position `y` reads the patch starting at row `y * stride`, `k` rows tall."
skills: [cross-correlation, shapes]
''',
)
write("exercises/fill-correlate2d/starter.py", FILL_STARTER)
write("exercises/fill-correlate2d/solution.py", FILL_SOLUTION)
write(
    "exercises/fill-correlate2d/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints the row, the shape and the strided output."""
    printed = run()
    assert printed == {FILL_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_other_cases():
    """A 2-by-2 kernel by hand, padding that keeps the size, a stride of 3, and a 1-by-1 kernel that scales."""
    correlate2d = function("correlate2d")
    image = np.array([[1.0, 2.0, 0.0], [0.0, 1.0, 3.0], [2.0, 0.0, 1.0]])
    assert correlate2d(image, np.array([[1.0, 2.0], [0.0, -1.0]])).tolist() == [[4.0, -1.0], [2.0, 6.0]]
    box = np.ones((3, 3))
    padded = correlate2d(image, box, padding=1)
    assert padded.shape == (3, 3) and padded[1, 1] == image.sum() and padded[0, 0] == image[:2, :2].sum()
    strided = correlate2d(np.arange(49.0).reshape(7, 7), np.ones((1, 1)), stride=3)
    assert strided.tolist() == [[0.0, 3.0, 6.0], [21.0, 24.0, 27.0], [42.0, 45.0, 48.0]]
    assert np.array_equal(correlate2d(image, np.array([[2.0]])), 2 * image)
''',
)
write("exercises/fill-correlate2d/wrong/stride-ignored-in-the-slice.py", FILL_NO_STRIDE_IN_SLICE)
write("exercises/fill-correlate2d/wrong/one-position-short.py", FILL_OFF_BY_ONE)
write(
    "exercises/fill-correlate2d/wrong/typed-in.py",
    "import numpy as np\n\n\ndef correlate2d(image, kernel, padding=0, stride=1):\n    return np.zeros((2, 2))\n\n\n" + "".join(f"print({line!r})\n" for line in FILL_OUT.splitlines()),
)

write(
    "exercises/write-max-pool/exercise.yaml",
    f'''id: write-max-pool
stage: write
rev: 1
title: "Max pooling, forward and back"
prompt: |
  Write two functions for a batch of images `X` of shape `(n, h, w)`:

  - `max_pool(X, size=2)`: pool over `size`-by-`size` windows and return the pooled array, shape `(n, h // size, w // size)`, and a boolean mask of the reshaped windows, shape `(n, h // size, size, w // size, size)`, that is `True` where a cell equals its window's maximum.
  - `max_pool_backward(mask, grad_out)`: send each pooled cell's gradient, `grad_out` of shape `(n, h // size, w // size)`, back to the cell that won its window, zero everywhere else, as an array of the original shape `(n, h, w)`.

  Reshaping to `(n, h // size, size, w // size, size)` groups each window's rows and columns together. Called on the 4-by-4 image and the 2-by-2 gradient in the starter, the program prints:

  ```
{block(WRITE_OUT)}  ```
hints:
  - "`windows.max(axis=(2, 4))` takes the maximum inside each window; compare `windows` with the pooled array (with `None` axes inserted) to find the winners."
  - "`mask * grad_out[:, :, None, :, None]` puts each window's gradient on its winner; reshape back to `(n, h, w)`."
skills: [shapes]
''',
)
write("exercises/write-max-pool/starter.py", "import numpy as np\n\n\n# Write max_pool and max_pool_backward here, above the data.\n\n\n" + WRITE_TAIL)
write("exercises/write-max-pool/solution.py", WRITE_SOLUTION)
write(
    "exercises/write-max-pool/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints the pooled 2-by-2 and the routed gradient."""
    printed = run()
    assert printed == {WRITE_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_other_sizes():
    """A batch of two 6-by-6 images pooled by 3: the maxima, one winner per window, and a gradient that lands only on winners."""
    max_pool = function("max_pool")
    max_pool_backward = function("max_pool_backward")
    rng = np.random.default_rng(4)
    X = rng.standard_normal((2, 6, 6))
    pooled, mask = max_pool(X, size=3)
    assert pooled.shape == (2, 2, 2) and mask.shape == (2, 2, 3, 2, 3)
    for n in range(2):
        for y in range(2):
            for x in range(2):
                assert pooled[n, y, x] == X[n, 3 * y : 3 * y + 3, 3 * x : 3 * x + 3].max()
    assert int(mask.sum()) == 8
    grad_out = np.arange(1.0, 9.0).reshape(2, 2, 2)
    back = max_pool_backward(mask, grad_out)
    assert back.shape == (2, 6, 6) and int((back != 0).sum()) == 8 and back.sum() == grad_out.sum()
    assert back[0, :3, :3].max() == 1.0 and back[1, 3:, 3:].max() == 8.0
''',
)
write("exercises/write-max-pool/wrong/averages.py", WRITE_AVERAGES)
write("exercises/write-max-pool/wrong/spreads-the-gradient.py", WRITE_SPREADS)
write(
    "exercises/write-max-pool/wrong/typed-in.py",
    "import numpy as np\n\n\ndef max_pool(X, size=2):\n    return X[:, ::size, ::size], None\n\n\ndef max_pool_backward(mask, grad_out):\n    return grad_out\n\n\n" + "".join(f"print({line!r})\n" for line in WRITE_OUT.splitlines()),
)

# --- the proof -----------------------------------------------------------------------------------

write(
    "exercises/build-a-convolutional-layer/exercise.yaml",
    f'''id: build-a-convolutional-layer
stage: build
rev: 1
title: "A convolutional layer"
prompt: |
  Starting from a blank editor, paste the module's `Dense`, `ReLU`, `Sequential`, `SoftmaxCrossEntropy`, `numeric_gradient` and `gradient_check` as they stand, then write:

  - `correlate2d(image, kernel, padding=0, stride=1)`: the sliding sum over one image, with zero padding and a stride.
  - `Conv2D(n_kernels, k, seed=0)`: kernels `W` of shape `(n_kernels, k, k)` drawn from `default_rng(seed).standard_normal` and divided by `k`, a bias `b` of zeros per kernel; `forward(X)` takes images `(N, H, W)` to maps `(N, n_kernels, H - k + 1, W - k + 1)`, kernel `q`'s map being `correlate2d(image, W[q]) + b[q]` for each image; `backward(grad_out)` sets `dW` and `db` and returns the gradient for `X`; `parameters()` and `gradients()` as in `Dense`.
  - `MaxPool2D(size=2)`: keeps each window's maximum over maps `(N, C, H, W)`; `backward` sends each gradient to the cell that won.
  - `Flatten`: maps to rows and back.
  - `input_gradient_check(net, loss, X, y)`: the largest gap between the gradient `net.backward` returns for `X` and the numeric one.
  - `make_bars(n, seed)`: `n` images of `rng.normal(0.0, 0.3, size=(n, 8, 8))` with `rng = default_rng(seed)`, labels `np.repeat([0, 1], n // 2)`; for each image in order, draw `at = rng.integers(1, 7)` and add 1.0 to row `at` for label 0 or column `at` for label 1.

  Then print:

  ```python
  image = np.zeros((6, 6))
  image[:, 3:] = 1.0
  vertical = np.array([[-1.0, 0.0, 1.0], [-1.0, 0.0, 1.0], [-1.0, 0.0, 1.0]])
  print(correlate2d(image, vertical)[0].tolist(), correlate2d(image, vertical, padding=1).shape, correlate2d(image, vertical, stride=2).shape)
  rng = np.random.default_rng(0)
  images = rng.standard_normal((5, 8, 8))
  labels = rng.integers(0, 3, size=5)
  net = Sequential([Conv2D(4, 3, seed=1), ReLU(), MaxPool2D(2), Flatten(), Dense(36, 3, seed=2)])
  loss = SoftmaxCrossEntropy()
  print(net.forward(images).shape, gradient_check(net, loss, images, labels) < 1e-6, input_gradient_check(net, loss, images, labels) < 1e-6, sum(p.size for p in net.parameters()))
  X_train, y_train = make_bars(100, seed=1)
  X_test, y_test = make_bars(100, seed=2)
  net = Sequential([Conv2D(4, 3, seed=1), ReLU(), MaxPool2D(2), Flatten(), Dense(36, 2, seed=2)])
  for step in range(300):
      loss.forward(net.forward(X_train), y_train)
      net.backward(loss.backward())
      for param, grad in zip(net.parameters(), net.gradients()):
          param -= 0.1 * grad
  print(round(float((net.forward(X_test).argmax(axis=1) == y_test).mean()), 2))
  ```

  ```
{block(BUILD_OUT)}  ```

  The checks test the sliding sum by hand with padding and stride, the layer's forward against `correlate2d`, its three gradients against central differences, pooling's forward and backward, the flatten round trip, the parameter count, and that the trained network reads nine in ten held-out bars.
skills: [cross-correlation, parameters, conv-layer, shapes]
''',
)
write("exercises/build-a-convolutional-layer/starter.py", "")
write("exercises/build-a-convolutional-layer/solution.py", BUILD_SOLUTION)
write(
    "exercises/build-a-convolutional-layer/test_exercise.py",
    f'''import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


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
    """Prints the three lines."""
    assert run() == {BUILD_OUT!r}


def test_correlate2d():
    """A 2-by-2 kernel by hand, padding that keeps the size, and a stride of 3."""
    correlate2d = function("correlate2d")
    image = np.array([[1.0, 2.0, 0.0], [0.0, 1.0, 3.0], [2.0, 0.0, 1.0]])
    assert correlate2d(image, np.array([[1.0, 2.0], [0.0, -1.0]])).tolist() == [[4.0, -1.0], [2.0, 6.0]]
    padded = correlate2d(image, np.ones((3, 3)), padding=1)
    assert padded.shape == (3, 3) and padded[1, 1] == image.sum() and padded[0, 0] == image[:2, :2].sum()
    assert correlate2d(np.arange(49.0).reshape(7, 7), np.ones((1, 1)), stride=3).tolist() == [[0.0, 3.0, 6.0], [21.0, 24.0, 27.0], [42.0, 45.0, 48.0]]


def test_conv_forward():
    """Each kernel's map is correlate2d of the image with that kernel plus its bias, and the shape is right."""
    Conv2D = function("Conv2D")
    correlate2d = function("correlate2d")
    rng = np.random.default_rng(7)
    X = rng.standard_normal((3, 7, 6))
    conv = Conv2D(5, 2, seed=3)
    conv.b[:] = rng.standard_normal(5)
    maps = conv.forward(X)
    assert maps.shape == (3, 5, 6, 5) and conv.W.shape == (5, 2, 2)
    for n in range(3):
        for q in range(5):
            assert np.allclose(maps[n, q], correlate2d(X[n], conv.W[q]) + conv.b[q])


def test_conv_backward():
    """dW, db and the input gradient agree with central differences on a weighted sum of the maps."""
    Conv2D = function("Conv2D")
    rng = np.random.default_rng(8)
    X = rng.standard_normal((2, 5, 5))
    weights = rng.standard_normal((2, 3, 3, 3))
    conv = Conv2D(3, 3, seed=5)
    conv.forward(X)
    grad_in = conv.backward(weights)
    f = lambda: float((conv.forward(X) * weights).sum())
    assert np.allclose(conv.dW, numeric(f, conv.W), atol=1e-6)
    assert np.allclose(conv.db, numeric(f, conv.b), atol=1e-6)
    assert np.allclose(grad_in, numeric(f, X), atol=1e-6)
    assert conv.parameters()[0] is conv.W and conv.gradients()[0] is conv.dW


def test_pool_and_flatten():
    """Pooling keeps each window's maximum and routes the gradient to the winner; Flatten round-trips."""
    MaxPool2D = function("MaxPool2D")
    Flatten = function("Flatten")
    block = np.array([[[[1.0, 2.0, 5.0, 6.0], [3.0, 4.0, 7.0, 8.0], [9.0, 10.0, 13.0, 14.0], [11.0, 12.0, 15.0, 16.0]]]])
    pool = MaxPool2D(2)
    assert pool.forward(block).tolist() == [[[[4.0, 8.0], [12.0, 16.0]]]]
    back = pool.backward(np.array([[[[1.0, 2.0], [3.0, 4.0]]]]))
    assert back.tolist() == [[[[0.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 2.0], [0.0, 0.0, 0.0, 0.0], [0.0, 3.0, 0.0, 4.0]]]]
    rng = np.random.default_rng(9)
    maps = rng.standard_normal((4, 3, 6, 6))
    flat = Flatten()
    rows = flat.forward(maps)
    assert rows.shape == (4, 108) and np.array_equal(flat.backward(rows), maps)
    assert pool.parameters() == [] and flat.gradients() == []


def test_counts_and_learning():
    """The parameter count follows the formula, the same seeds repeat, and the network reads nine in ten held-out bars."""
    Conv2D = function("Conv2D")
    ReLU = function("ReLU")
    MaxPool2D = function("MaxPool2D")
    Flatten = function("Flatten")
    Dense = function("Dense")
    Sequential = function("Sequential")
    SoftmaxCrossEntropy = function("SoftmaxCrossEntropy")
    make_bars = function("make_bars")
    assert sum(p.size for p in Conv2D(6, 5, seed=1).parameters()) == 6 * 25 + 6
    X_train, y_train = make_bars(100, seed=1)
    X_test, y_test = make_bars(100, seed=2)
    assert X_train.shape == (100, 8, 8) and y_train.tolist() == [0] * 50 + [1] * 50
    assert np.array_equal(make_bars(100, seed=1)[0], X_train) and not np.array_equal(X_test, X_train)
    net = Sequential([Conv2D(4, 3, seed=1), ReLU(), MaxPool2D(2), Flatten(), Dense(36, 2, seed=2)])
    loss = SoftmaxCrossEntropy()
    for step in range(300):
        loss.forward(net.forward(X_train), y_train)
        net.backward(loss.backward())
        for param, grad in zip(net.parameters(), net.gradients()):
            param -= 0.1 * grad
    assert (net.forward(X_test).argmax(axis=1) == y_test).mean() >= 0.9
''',
)
for key, code in BUILD_WRONGS.items():
    write(f"exercises/build-a-convolutional-layer/wrong/{key}.py", code)
write(
    "exercises/build-a-convolutional-layer/wrong/typed-in.py",
    "import numpy as np\n\n\ndef correlate2d(image, kernel, padding=0, stride=1):\n    return np.zeros((4, 4))\n\n\nclass Conv2D:\n    def __init__(self, n_kernels, k, seed=0):\n        self.W = np.zeros((n_kernels, k, k))\n        self.b = np.zeros(n_kernels)\n\n    def forward(self, X):\n        return np.zeros((len(X), len(self.W), 6, 6))\n\n    def backward(self, grad_out):\n        return np.zeros((len(grad_out), 8, 8))\n\n    def parameters(self):\n        return [self.W, self.b]\n\n    def gradients(self):\n        return [self.W, self.b]\n\n\nclass MaxPool2D:\n    def __init__(self, size=2):\n        self.size = size\n\n    def forward(self, X):\n        return X[:, :, ::2, ::2]\n\n    def backward(self, grad_out):\n        return grad_out\n\n    def parameters(self):\n        return []\n\n    def gradients(self):\n        return []\n\n\nclass Flatten:\n    def forward(self, X):\n        return X.reshape(len(X), -1)\n\n    def backward(self, grad_out):\n        return grad_out\n\n    def parameters(self):\n        return []\n\n    def gradients(self):\n        return []\n\n\ndef make_bars(n, seed):\n    return np.zeros((n, 8, 8)), np.repeat([0, 1], n // 2)\n\n\n"
    + "".join(f"print({line!r})\n" for line in BUILD_OUT.splitlines()),
)

write(
    "exercises/debug-a-layer-that-fails-its-gradient-check/exercise.yaml",
    f'''id: debug-a-layer-that-fails-its-gradient-check
stage: debug
rev: 1
title: "A layer that fails its gradient check"
prompt: |
  A convolutional network checked two ways. It should print:

  ```
{block(DEBUG_OUT)}  ```

  It has two bugs. Run it: sixteen cells get gradient from the pool instead of four, and both gradient checks fail. `MaxPool2D.backward` spreads each pooled cell's gradient over its whole window instead of giving it to the cell that won (the mask the forward pass saved); only the winner affected the output, so only it should get the gradient. Fix that, and the parameters pass but the **input** check still fails: in `Conv2D.backward`, the line that sends each output gradient back onto the input cells it read uses weight `(j, i)` where the forward pass used weight `(i, j)`, so the kernel is transposed on the way back.
skills: [conv-layer, shapes]
''',
)
write("exercises/debug-a-layer-that-fails-its-gradient-check/starter.py", DEBUG_STARTER)
write("exercises/debug-a-layer-that-fails-its-gradient-check/solution.py", DEBUG_SOLUTION)
write(
    "exercises/debug-a-layer-that-fails-its-gradient-check/test_exercise.py",
    f'''import numpy as np

from checks import function, run

EXPECTED = {DEBUG_OUT!r}


def test_the_output():
    """Prints four cells and two passes."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\\n{{EXPECTED}}\\nYour program printed:\\n{{printed}}"


def test_the_pieces():
    """The pool's gradient lands on the winners only, and the conv's input gradient matches central differences on an asymmetric kernel."""
    MaxPool2D = function("MaxPool2D")
    Conv2D = function("Conv2D")
    pool = MaxPool2D(2)
    pool.forward(np.array([[[[1.0, 2.0, 5.0, 6.0], [3.0, 4.0, 7.0, 8.0], [9.0, 10.0, 13.0, 14.0], [11.0, 12.0, 15.0, 16.0]]]]))
    back = pool.backward(np.array([[[[1.0, 2.0], [3.0, 4.0]]]]))
    assert back.tolist() == [[[[0.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 2.0], [0.0, 0.0, 0.0, 0.0], [0.0, 3.0, 0.0, 4.0]]]]
    conv = Conv2D(1, 2, seed=0)
    conv.W[0] = np.array([[1.0, 2.0], [3.0, 4.0]])
    X = np.arange(9.0).reshape(1, 3, 3)
    conv.forward(X)
    grad_in = conv.backward(np.ones((1, 1, 2, 2)))
    assert grad_in[0].tolist() == [[1.0, 3.0, 2.0], [4.0, 10.0, 6.0], [3.0, 7.0, 4.0]]
''',
)
write("exercises/debug-a-layer-that-fails-its-gradient-check/wrong/still-spreading-the-pool-gradient.py", DEBUG_STILL_POOL)
write("exercises/debug-a-layer-that-fails-its-gradient-check/wrong/still-transposed.py", DEBUG_STILL_CONV)
write(
    "exercises/debug-a-layer-that-fails-its-gradient-check/wrong/typed-in.py",
    "import numpy as np\n\n\nclass MaxPool2D:\n    def __init__(self, size=2):\n        self.size = size\n\n    def forward(self, X):\n        return X[:, :, ::2, ::2]\n\n    def backward(self, grad_out):\n        return grad_out\n\n\nclass Conv2D:\n    def __init__(self, n_kernels, k, seed=0):\n        self.W = np.zeros((n_kernels, k, k))\n\n    def forward(self, X):\n        return X\n\n    def backward(self, grad_out):\n        return grad_out\n\n\n" + "".join(f"print({line!r})\n" for line in DEBUG_OUT.splitlines()),
)

write(
    "exercises/review-correlate2d/exercise.yaml",
    f'''id: review-correlate2d
stage: review_code
rev: 1
title: "The sliding sum, from memory"
prompt: |
  Write `correlate2d(image, kernel)`: slide the square kernel over the image (no padding, stride 1) and return the array of sums of the kernel times the patch under it. Print it for the 3-by-4 image `[[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]` with the kernel `[[1, -1], [1, -1]]`, then with the 3-by-3 kernel that has 1s above, below, left and right of its centre and 0 elsewhere:

  ```
{block(REVIEW_CODE_OUT)}  ```
skills: [cross-correlation]
''',
)
write("exercises/review-correlate2d/starter.py", "")
write("exercises/review-correlate2d/solution.py", REVIEW_CODE_SOLUTION)
write(
    "exercises/review-correlate2d/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints the two outputs."""
    assert run() == {REVIEW_CODE_OUT!r}


def test_other_cases():
    """A 2-by-2 kernel by hand, and a 1-by-1 kernel that scales."""
    correlate2d = function("correlate2d")
    image = np.array([[1.0, 2.0, 0.0], [0.0, 1.0, 3.0], [2.0, 0.0, 1.0]])
    assert correlate2d(image, np.array([[1.0, 2.0], [0.0, -1.0]])).tolist() == [[4.0, -1.0], [2.0, 6.0]]
    assert np.array_equal(correlate2d(image, np.array([[3.0]])), 3 * image)
''',
)
write("exercises/review-correlate2d/wrong/transposed.py", REVIEW_CODE_WRONG)
write(
    "exercises/review-correlate2d/wrong/typed-in.py",
    "import numpy as np\n\n\ndef correlate2d(image, kernel):\n    return np.zeros((2, 3))\n\n\n" + "".join(f"print({line!r})\n" for line in REVIEW_CODE_OUT.splitlines()),
)

print("ml.nn.convolution written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
