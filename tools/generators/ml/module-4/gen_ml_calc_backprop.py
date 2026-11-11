"""Writes the topic ml.calc.backpropagation (Module 4's sixth topic). Run from
the repository root under uv (python -m uv run python <this file>), so every
program's expected output is captured from CPython rather than typed in.
Files are written as bytes with LF endings."""

import pathlib
import subprocess
import sys

ROOT = pathlib.Path("content/topics/ml.calc.backpropagation")


def write(relative: str, text: str) -> None:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


def out(program: str) -> str:
    result = subprocess.run(
        [sys.executable, "-c", program], capture_output=True, text=True, check=True
    )
    return result.stdout.replace("\r\n", "\n")


def block(text: str, indent: str = "  ") -> str:
    return "".join(indent + line + "\n" for line in text.rstrip("\n").splitlines())


def numbered(program: str) -> str:
    return "".join(f"{i + 1:>3} {line}\n" for i, line in enumerate(program.splitlines()))


SIGMOID = '''def sigmoid(z):
    return 1 / (1 + np.exp(-z))
'''
DATA = '''X = np.array([[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]])
y = np.array([0.0, 1.0, 1.0, 0.0])
'''
WEIGHTS = '''W1 = np.array([[0.3, 0.8, 0.3, -1.3], [0.9, 0.4, -0.5, 0.6]])
b1 = np.array([0.2, 0.1, 0.1, 0.3])
W2 = np.array([-0.7, -0.2, -0.5, 0.6])
b2 = 0.0
'''
FORWARD = '''def forward(X, W1, b1, W2, b2):
    z1 = X @ W1 + b1
    h = np.maximum(z1, 0.0)
    p = sigmoid(h @ W2 + b2)
    return z1, h, p
'''
LOSS = '''def loss(p, y):
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))
'''
BACKWARD = '''def backward(X, y, W2, z1, h, p):
    dz2 = (p - y) / len(y)
    dW2 = h.T @ dz2
    db2 = dz2.sum()
    dh = np.outer(dz2, W2)
    dz1 = dh * (z1 > 0)
    dW1 = X.T @ dz1
    db1 = dz1.sum(axis=0)
    return dW1, db1, dW2, db2
'''

# --- the worked example --------------------------------------------------------------------

EXAMPLE = (
    "import numpy as np\n\n\n"
    + SIGMOID
    + "\n\n"
    + DATA
    + WEIGHTS
    + "\n\n"
    + FORWARD
    + "\n\n"
    + LOSS
    + "\n\n"
    + BACKWARD
    + '''

z1, h, p = forward(X, W1, b1, W2, b2)
print(np.round(p, 3), round(loss(p, y), 3))
dW1, db1, dW2, db2 = backward(X, y, W2, z1, h, p)
print(dW1.shape, db1.shape, dW2.shape)

numeric = np.zeros_like(W1)
for i in range(2):
    for j in range(4):
        step = np.zeros_like(W1)
        step[i, j] = 1e-6
        up = loss(forward(X, W1 + step, b1, W2, b2)[2], y)
        down = loss(forward(X, W1 - step, b1, W2, b2)[2], y)
        numeric[i, j] = (up - down) / 2e-6
print(np.allclose(dW1, numeric, atol=1e-6))

for step in range(1000):
    z1, h, p = forward(X, W1, b1, W2, b2)
    if step in (0, 100, 500):
        print(step, round(loss(p, y), 3))
    dW1, db1, dW2, db2 = backward(X, y, W2, z1, h, p)
    W1 = W1 - 0.5 * dW1
    b1 = b1 - 0.5 * db1
    W2 = W2 - 0.5 * dW2
    b2 = b2 - 0.5 * db2
z1, h, p = forward(X, W1, b1, W2, b2)
print(round(loss(p, y), 3), np.round(p, 2), np.mean((p > 0.5) == (y == 1)))
'''
)
EXAMPLE_OUT = out(EXAMPLE)
print("example:\n" + numbered(EXAMPLE) + EXAMPLE_OUT)
lines = EXAMPLE_OUT.splitlines()
assert lines[1] == "(2, 4) (4,) (4,)" and lines[2] == "True", EXAMPLE_OUT
assert lines[3].startswith("0 0.7") and lines[-1].endswith("[0. 1. 1. 0.] 1.0"), EXAMPLE_OUT
assert "e-" not in EXAMPLE_OUT and "e+" not in EXAMPLE_OUT
# A nudge in the ninth decimal of one weight must not change what's printed,
# or the two runtimes' last-ulp differences could.
assert out(EXAMPLE.replace("0.3, 0.8, 0.3, -1.3", "0.3000000001, 0.8, 0.3, -1.3")) == EXAMPLE_OUT

# --- the fill-in ------------------------------------------------------------------------------

FILL_HEAD = (
    "import numpy as np\n\n\n"
    + SIGMOID
    + "\n\n"
    + DATA
    + WEIGHTS
    + "\n\n"
    + FORWARD
    + "\n\n"
    + LOSS
    + '''

def backward(X, y, W2, z1, h, p):
    dz2 = (p - y) / len(y)
    dW2 = h.T @ dz2
    db2 = dz2.sum()
    dh = np.outer(dz2, OUTER)
    dz1 = dh * (z1 > ZERO)
    dW1 = X.T @ dz1
    db1 = dz1.sum(axis=0)
    return dW1, db1, dW2, db2


def numeric_dW1():
    grad = np.zeros_like(W1)
    for i in range(2):
        for j in range(4):
            step = np.zeros_like(W1)
            step[i, j] = 1e-6
            up = loss(forward(X, W1 + step, b1, W2, b2)[2], y)
            down = loss(forward(X, W1 - step, b1, W2, b2)[2], y)
            grad[i, j] = (up - down) / 2e-6
    return grad


z1, h, p = forward(X, W1, b1, W2, b2)
dW1, db1, dW2, db2 = backward(X, y, W2, z1, h, p)
print(np.round(dW2, 3))
print(np.round(dW1, 3))
print(np.allclose(dW1, numeric_dW1(), atol=1e-6))
'''
)
FILL_SOLUTION = FILL_HEAD.replace("OUTER", "W2").replace("ZERO", "0")
FILL_STARTER = FILL_HEAD.replace("OUTER", "...").replace("ZERO", "...")
FILL_H_MASK = FILL_SOLUTION.replace("    dz1 = dh * (z1 > 0)", "    dz1 = dh * h")
FILL_OUT = out(FILL_SOLUTION)
print("fill:\n" + FILL_OUT)
assert FILL_OUT.endswith("True\n") and "e-" not in FILL_OUT, FILL_OUT
assert out(FILL_H_MASK) != FILL_OUT

# --- the write -----------------------------------------------------------------------------------

WRITE_STARTER = '''import numpy as np

M = np.array([[1.0, -2.0], [0.5, 3.0]])
'''
WRITE_SOLUTION = WRITE_STARTER + '''

def numeric_grad(f, W, h=1e-6):
    grad = np.zeros_like(W)
    for index in np.ndindex(W.shape):
        step = np.zeros_like(W)
        step[index] = h
        grad[index] = (f(W + step) - f(W - step)) / (2 * h)
    return grad


print(np.round(numeric_grad(lambda W: np.sum(W**2), M), 4))
print(np.allclose(numeric_grad(lambda W: np.sum(W**2), M), 2 * M, atol=1e-6))
'''
WRITE_OUT = out(WRITE_SOLUTION)
print("write:\n" + WRITE_OUT)
assert WRITE_OUT == "[[ 2. -4.]\n [ 1.  6.]]\nTrue\n", WRITE_OUT

# --- the build ---------------------------------------------------------------------------------------

BUILD_SOLUTION = (
    "import numpy as np\n\n\n"
    + SIGMOID
    + '''

def forward(X, params):
    z1 = X @ params["W1"] + params["b1"]
    h = np.maximum(z1, 0.0)
    p = sigmoid(h @ params["W2"] + params["b2"])
    return z1, h, p


'''
    + LOSS
    + '''

def backward(X, y, params, z1, h, p):
    dz2 = (p - y) / len(y)
    dh = np.outer(dz2, params["W2"])
    dz1 = dh * (z1 > 0)
    return {"W1": X.T @ dz1, "b1": dz1.sum(axis=0), "W2": h.T @ dz2, "b2": dz2.sum()}


def train(X, y, params, rate, steps):
    losses = []
    for step in range(steps):
        z1, h, p = forward(X, params)
        losses.append(loss(p, y))
        grads = backward(X, y, params, z1, h, p)
        for key in params:
            params[key] = params[key] - rate * grads[key]
    return losses


def numeric_grad(f, W, h=1e-6):
    grad = np.zeros_like(W)
    for index in np.ndindex(W.shape):
        step = np.zeros_like(W)
        step[index] = h
        grad[index] = (f(W + step) - f(W - step)) / (2 * h)
    return grad


'''
    + DATA
    + '''params = {
    "W1": np.array([[0.3, 0.8, 0.3, -1.3], [0.9, 0.4, -0.5, 0.6]]),
    "b1": np.array([0.2, 0.1, 0.1, 0.3]),
    "W2": np.array([-0.7, -0.2, -0.5, 0.6]),
    "b2": np.array(0.0),
}
z1, h, p = forward(X, params)
grads = backward(X, y, params, z1, h, p)
for key in params:

    def loss_of(value, key=key):
        return loss(forward(X, {**params, key: value})[2], y)

    print("check", key, np.allclose(grads[key], numeric_grad(loss_of, params[key]), atol=1e-6))
losses = train(X, y, params, 0.5, 1000)
print("loss", round(losses[0], 3), round(losses[100], 3), round(losses[500], 3), round(losses[-1], 3))
z1, h, p = forward(X, params)
print("predictions", np.round(p, 2))
print("accuracy", np.mean((p > 0.5) == (y == 1)))
'''
)
BUILD_OUT = out(BUILD_SOLUTION)
print("build:\n" + BUILD_OUT)
assert BUILD_OUT.startswith("check W1 True\ncheck b1 True\ncheck W2 True\ncheck b2 True\nloss 0.7"), BUILD_OUT
assert BUILD_OUT.endswith("predictions [0. 1. 1. 0.]\naccuracy 1.0\n"), BUILD_OUT
BUILD_NO_MASK = BUILD_SOLUTION.replace("    dz1 = dh * (z1 > 0)\n", "    dz1 = dh\n")
BUILD_ASCENT = BUILD_SOLUTION.replace("params[key] = params[key] - rate * grads[key]", "params[key] = params[key] + rate * grads[key]")
BUILD_NO_N = BUILD_SOLUTION.replace("    dz2 = (p - y) / len(y)\n    dh", "    dz2 = p - y\n    dh")
for wrong in (BUILD_NO_MASK, BUILD_ASCENT, BUILD_NO_N):
    assert out(wrong) != BUILD_OUT

# --- the debug ------------------------------------------------------------------------------------------

DEBUG_SOLUTION = (
    "import numpy as np\n\n\n"
    + SIGMOID
    + "\n\n"
    + DATA
    + WEIGHTS
    + "\n\n"
    + FORWARD
    + "\n\n"
    + LOSS
    + "\n\n"
    + BACKWARD
    + '''

for step in range(1000):
    z1, h, p = forward(X, W1, b1, W2, b2)
    if step == 0:
        print("start", round(loss(p, y), 3))
    dW1, db1, dW2, db2 = backward(X, y, W2, z1, h, p)
    W1 = W1 - 0.5 * dW1
    b1 = b1 - 0.5 * db1
    W2 = W2 - 0.5 * dW2
    b2 = b2 - 0.5 * db2
z1, h, p = forward(X, W1, b1, W2, b2)
print("end", round(loss(p, y), 3))
print("predictions", np.round(p, 2))
'''
)
DEBUG_STARTER = DEBUG_SOLUTION.replace("    dW1 = X.T @ dz1\n", "    dW1 = X @ dz1\n").replace(
    "    dz1 = dh * (z1 > 0)\n", "    dz1 = dh * h\n"
)
DEBUG_SHAPE_ONLY = DEBUG_SOLUTION.replace("    dz1 = dh * (z1 > 0)\n", "    dz1 = dh * h\n")
DEBUG_OUT = out(DEBUG_SOLUTION)
print("debug:\n" + DEBUG_OUT + "--- mask bug alone prints:\n" + out(DEBUG_SHAPE_ONLY))
assert DEBUG_OUT.startswith("start 0.7") and "\nend 0.00" in DEBUG_OUT, DEBUG_OUT
assert DEBUG_OUT.endswith("predictions [0. 1. 1. 0.]\n"), DEBUG_OUT
assert out(DEBUG_SHAPE_ONLY) != DEBUG_OUT

# --- predict items ---------------------------------------------------------------------------------------

PREDICT_FORWARD = '''import numpy as np

X = np.array([[1.0, 2.0]])
W1 = np.array([[1.0, -1.0], [0.0, 1.0]])
b1 = np.array([0.0, -1.0])
W2 = np.array([2.0, -1.0])
z1 = X @ W1 + b1
h = np.maximum(z1, 0.0)
z2 = h @ W2 + 0.5
print(z1)
print(h)
print(z2)
'''
PREDICT_FORWARD_OUT = out(PREDICT_FORWARD)
print("predict forward:\n" + PREDICT_FORWARD_OUT)
assert PREDICT_FORWARD_OUT == "[[1. 0.]]\n[[1. 0.]]\n[2.5]\n", PREDICT_FORWARD_OUT

PARSONS_LINES = [
    "import numpy as np",
    "X, y, W1, W2 = np.array([[0.0, 1.0], [1.0, 1.0]]), np.array([1.0, 0.0]), np.array([[1.0, -1.0], [0.5, 0.5]]), np.array([1.0, -1.0])",
    "z1 = X @ W1",
    "h = np.maximum(z1, 0.0)",
    "p = 1 / (1 + np.exp(-(h @ W2)))",
    "dz2 = (p - y) / 2",
    "dh = np.outer(dz2, W2)",
    "dz1 = dh * (z1 > 0)",
    "dW1 = X.T @ dz1",
    "print(np.round(dW1, 3))",
]
PARSONS_OUT = out("\n".join(PARSONS_LINES) + "\n")
print("parsons:\n" + PARSONS_OUT)
PARSONS_WRONG = out("\n".join(PARSONS_LINES).replace("dz1 = dh * (z1 > 0)", "dz1 = dh * h") + "\n")
assert PARSONS_WRONG != PARSONS_OUT

REVIEW_MASK = '''import numpy as np

z1 = np.array([[2.0, -1.0], [-0.5, 3.0]])
dh = np.array([[0.4, 0.4], [0.2, 0.2]])
print(dh * (z1 > 0))
'''
REVIEW_MASK_OUT = out(REVIEW_MASK)
print("review mask:\n" + REVIEW_MASK_OUT)
assert REVIEW_MASK_OUT == "[[0.4 0. ]\n [0.  0.2]]\n", REVIEW_MASK_OUT

REVIEW_CODE_STARTER = '''import numpy as np

X = np.array([[1.0, 2.0]])
W1 = np.array([[1.0, -1.0], [0.0, 1.0]])
b1 = np.array([0.0, -1.0])
W2 = np.array([2.0, -1.0])
b2 = 0.5
'''
REVIEW_CODE_SOLUTION = REVIEW_CODE_STARTER + '''

def forward(X, W1, b1, W2, b2):
    h = np.maximum(X @ W1 + b1, 0.0)
    return 1 / (1 + np.exp(-(h @ W2 + b2)))


print(np.round(forward(X, W1, b1, W2, b2), 3))
'''
REVIEW_CODE_OUT = out(REVIEW_CODE_SOLUTION)
print("review code:\n" + REVIEW_CODE_OUT)
assert REVIEW_CODE_OUT == "[0.924]\n", REVIEW_CODE_OUT

LOSS_LINE = BUILD_OUT.splitlines()[4]  # "loss <start> <step 100> <step 500> <last>"
LOSS0, LOSS100, FINAL_LOSS = LOSS_LINE.split()[1], LOSS_LINE.split()[2], LOSS_LINE.split()[-1]

# =====================================================================================
# topic.yaml
# =====================================================================================

write(
    "topic.yaml",
    '''id: ml.calc.backpropagation
kind: topic
status: ready
title: "Backpropagation"
summary: "A tiny network as composed functions: the forward pass, the backward pass by the chain rule, a gradient check, and the first training loop."
prerequisites: [ml.calc.chain-rule, ml.calc.descent-in-many-dimensions, ml.calc.loss-functions, ml.la.matrices-as-maps]
packages: [numpy]
estimated_minutes: 60
rev: 1
objectives:
  - "Write a one-hidden-layer network as a forward pass of matrix products and a bend."
  - "Compute every gradient with the chain rule, layer by layer, from the loss backwards."
  - "Check the gradients against finite differences before trusting them."
  - "Train the network with gradient descent and watch the loss fall."
# Linked, never copied or embedded: 3Blue1Brown's videos are under the
# standard YouTube licence; Michael Nielsen's book is CC BY-NC 3.0; NumPy's
# documentation is under the NumPy licence (BSD-3-Clause).
resources:
  - title: "3Blue1Brown: Neural networks (Grant Sanderson), chapters 3 and 4: What is backpropagation really doing? and Backpropagation calculus"
    url: https://www.3blue1brown.com/topics/neural-networks
    type: video
    use: link
    license: Standard YouTube licence (linked, not copied)
  - title: "Neural Networks and Deep Learning, chapter 2: How the backpropagation algorithm works (Michael Nielsen)"
    url: https://neuralnetworksanddeeplearning.com/chap2.html
    type: reading
    use: link
    license: CC BY-NC 3.0 (linked, not copied)
  - title: "numpy.outer (the NumPy developers)"
    url: https://numpy.org/doc/stable/reference/generated/numpy.outer.html
    type: reading
    use: link
    license: BSD-3-Clause (NumPy documentation)
practice:
  - example-a-tiny-network-trained
  - parsons-backward-pass
  - mcq-the-first-factor
  - predict-a-forward-pass
  - mcq-a-dead-unit
  - fill-the-backward-pass
  - write-numeric-grad
prove:
  build: build-a-tiny-network
  debug: debug-training-loop
  explain:
    prompt: |
      A teammate has read that "backpropagation is just the chain rule" but can't see how the six lines of your backward pass follow from it. In your own words: what does the forward pass keep, and why? Walk the backward pass from `dz2 = (p - y) / n` to `dW1`: at each line, which local derivative is being multiplied in, and why does `dW2` involve `h` while `dW1` involves `X`? Why does ReLU's mask appear, and what happens to a hidden unit whose `z1` is negative for every example? And why do you check the gradients numerically before training?
    rubric:
      - id: forward-keeps
        required: true
        description: "The forward pass keeps z1, h and p (and X) because each local derivative in the backward pass is evaluated at that link's own input: ReLU's at z1, the output layer's weight gradient at h, the first layer's at X."
      - id: chain
        required: true
        description: "dz2 = (p - y)/n is the loss-through-sigmoid gradient at the output score; dW2 = hᵀ dz2 because z2 = h·W2 + b2 so dz2/dW2 is h; dh = dz2 ⊗ W2 passes the gradient through the same product the other way; dz1 = dh times the ReLU mask; dW1 = Xᵀ dz1 and db1 sums dz1 over examples, because z1 = X W1 + b1."
      - id: mask
        required: true
        description: "ReLU's derivative is 1 where z1 > 0 and 0 elsewhere, so the mask zeroes the gradient for inactive units; a unit that is negative for every example gets zero gradient on all its weights and never changes: a dead unit."
      - id: check
        required: false
        description: "A backward pass can be wrong and still train a little or not at all; comparing each gradient with a central difference of the loss, one weight at a time, catches a wrong line before any training time is spent."
    model_answer: |
      The forward pass is the chain run forwards: z1 is the first layer's scores, h is z1 after the ReLU bend, p is the sigmoid of the output score, and the loss comes from p. It keeps z1, h and p because the backward pass multiplies in each link's local derivative evaluated at that link's own input, and those inputs are exactly these values. The backward pass starts at the end. dz2 equals p minus y over n, which is the gradient of the mean cross-entropy with respect to the output score, the two derivatives having cancelled as they did in the loss topic. The output score is h times W2 plus b2, so its derivative with respect to W2 is h, and dW2 is h transposed times dz2: each weight's gradient is its input times the gradient at its output, summed over examples; db2 is dz2 summed. The same product read the other way gives dh, the gradient with respect to the hidden values: each example's dz2 spread along W2, which is the outer product. Then comes ReLU, whose derivative is 1 where z1 was positive and 0 where it wasn't, so dz1 is dh with the inactive entries zeroed: that's the mask. Finally z1 is X times W1 plus b1, so dW1 is X transposed times dz1, which is why X appears where h did a layer later, and db1 is dz1 summed over the examples. A hidden unit whose z1 is negative for every example has a mask of all zeros, so dz1 is zero in its column, its weights get no gradient, and it never changes: a dead unit, which no amount of training revives. I check all of this numerically before training because a backward pass can be subtly wrong and still make the loss fall a little; nudging each weight up and down, running the forward pass, and comparing the slope with my gradient takes seconds and catches a wrong line before I spend an hour training on it.
review_pool:
  - review-predict-the-mask
  - review-mcq-why-h
  - review-mcq-where-is-the-bug
  - review-mcq-a-dead-layer
  - review-forward
# What this topic teaches. Each question names the skills it tests, so a
# missed question can come back as a different one on the same skill
# (ADR-0011).
skills:
  - id: forward
    description: "Write a one-hidden-layer network as matrix products and a bend, and compute its output"
  - id: backward
    description: "Compute every gradient from the loss backwards by the chain rule, with the right local derivative at each line"
  - id: check
    description: "Check a gradient against finite differences, one weight at a time, and locate a wrong line from which checks fail"
  - id: train
    description: "Train the network by descent, read the loss falling, and know what a dead unit is"
''',
)

# =====================================================================================
# lesson.mdx
# =====================================================================================

write(
    "lesson.mdx",
    f'''<Intro>

Everything in this module meets here. A network is a chain: multiply the inputs by a matrix of weights, add a bias, bend with ReLU, multiply again, squash with a sigmoid, measure the cross-entropy. The forward pass runs that chain and keeps every intermediate value. The backward pass is the chain rule from the last topic run from the loss inward, with matrices where the numbers were, and the loss topic's `p - y` as its first factor. Then gradient descent trains it. This topic builds a network of two inputs, four hidden units and one output, checks every gradient numerically, and trains it to learn XOR, the small problem no single line can solve.

The main resource is **3Blue1Brown's _Neural networks_, chapters 3 and 4**, what backpropagation is really doing and backpropagation calculus; about 25 minutes, and chapter 4 is this topic's backward pass drawn as a tree. Michael Nielsen's chapter 2 has the same derivation in text, with the four equations named. Watch for:

- **The sensitivity picture:** how much the loss cares about each weight, found by walking back from the output.
- **Why `h` appears in the gradient of `W2`:** a weight's gradient is its input times the gradient at its output.
- **The mask:** a ReLU that's off passes no gradient back.

</Intro>

<Resource index={{0}} />

<Recap>

- **The network.** For inputs `X` (one row per example, two columns), `z1 = X @ W1 + b1` (four hidden scores per example), `h = np.maximum(z1, 0.0)` (the bend), `z2 = h @ W2 + b2` (one output score), `p = sigmoid(z2)`. `W1` is 2 by 4, `b1` has 4 entries, `W2` has 4, `b2` is one number. The loss is the mean cross-entropy of `p` against `y`.
- **The forward pass** computes and **keeps** `z1`, `h` and `p`, because the backward pass evaluates each local derivative at that link's input.
- **The backward pass**, from the loss inward, one line per link:
  - `dz2 = (p - y) / n`: the gradient of the mean cross-entropy with respect to the output score (the loss topic's `p - y`).
  - `dW2 = h.T @ dz2` and `db2 = dz2.sum()`: `z2 = h @ W2 + b2`, so a weight's gradient is its input `h` times the gradient at its output, summed over examples.
  - `dh = np.outer(dz2, W2)`: the same product the other way, each example's `dz2` spread along `W2`.
  - `dz1 = dh * (z1 > 0)`: ReLU's derivative is the **mask**, 1 where the unit was on, 0 where it was off.
  - `dW1 = X.T @ dz1` and `db1 = dz1.sum(axis=0)`: `z1 = X @ W1 + b1`, so `X` plays the part `h` played a layer later.
- **Every gradient has the shape of its parameter:** `dW1` is 2 by 4 like `W1`, `db1` has 4 entries like `b1`. A shape error in the backward pass is a line with the wrong product or a missing transpose.
- **The gradient check.** For each weight: nudge it by `h = 1e-6` up and down, run the forward pass and the loss both times, and divide the difference by `2h`; compare with your gradient. `np.allclose(..., atol=1e-6)` for every parameter before any training. If `W2` passes and `W1` fails, the bug is between them: `dh`, the mask or `dW1`. One honest false alarm: a hidden unit sitting **exactly** at the bend (`z1 == 0` for some example) makes the two nudges land on different sides of the corner, so the numeric slope is half the analytic one there; starting weights without exact zeros avoid it.
- **Training** is the descent loop from three topics ago: forward, loss, backward, `W = W - rate * dW` for each parameter. From the worked example's starting weights at rate 0.5, the loss on XOR falls from {LOSS0} to {FINAL_LOSS} in a thousand steps and all four predictions are right.
- **Dead units.** A hidden unit whose `z1` is negative for every example has a mask of zeros, gets no gradient, and never changes. Big learning rates and bad starts kill units; it's a reason starting weights are small and random in practice.
- **In machine learning:** this is what `loss.backward()` does in PyTorch, for every layer type, with the same bookkeeping; the next topic improves the update rule, and the checkpoint trains this network with it.

</Recap>
''',
)

# =====================================================================================
# recall
# =====================================================================================

write(
    "recall/parsons-backward-pass.yaml",
    f'''id: parsons-backward-pass
type: parsons
rev: 1
prompt: |
  Put the lines in order to run a forward pass through a two-unit hidden layer (no biases) and then the backward pass down to `dW1`, printing:

  ```
{block(PARSONS_OUT)}  ```

  One line is a decoy that doesn't belong.
lines:
{"".join("  - " + repr(line) + chr(10) for line in PARSONS_LINES)}distractors:
  - 'dz1 = dh * h'
explanation: |
  Forward: `z1`, then `h`, then `p`. Backward, from the loss inward: `dz2` is `(p - y) / n`; `dh` spreads it along `W2`; `dz1` applies ReLU's derivative, the **mask** `z1 > 0`; `dW1` is the input transposed times `dz1`. The decoy multiplies by `h`, ReLU's value, instead of its derivative; the derivative of `max(z, 0)` is 1 or 0, never `z`.
skills: [backward]
''',
)

write(
    "recall/mcq-the-first-factor.yaml",
    '''id: mcq-the-first-factor
type: mcq
rev: 1
prompt: |
  The backward pass begins with `dz2 = (p - y) / n`. Why does it start there, and why that formula?
choices:
  - 'It''s the gradient of the mean cross-entropy with respect to the output score, the last link of the chain; every other gradient is built from it by multiplying in local derivatives from the output inward'
  - 'It''s the gradient with respect to the first layer''s weights, which is where training starts'
  - 'It''s the loss itself, which the backward pass then divides among the layers'
  - 'Any starting value works; `p - y` is a convention'
answer: 0
explanation: |
  The chain rule multiplies from the output end, so the first factor is the derivative of the loss with respect to the thing nearest it, the output score `z2`. For cross-entropy through a sigmoid that derivative is `p - y` per example (the log and the sigmoid cancel), and the `1 / n` is the mean. From there each line multiplies in one more link.
skills: [backward]
''',
)

write(
    "recall/predict-a-forward-pass.yaml",
    f'''id: predict-a-forward-pass
type: predict_output
rev: 1
prompt: |
  One example through a two-unit hidden layer. What does the program print?
code: |
{block(PREDICT_FORWARD)}expected_output: |
{block(PREDICT_FORWARD_OUT)}explanation: |
  `X @ W1` is `[1*1 + 2*0, 1*(-1) + 2*1] = [1, 1]`; adding `b1` gives `z1 = [1, 0]`. ReLU leaves `[1, 0]` as it is (nothing is negative). The output score is `1*2 + 0*(-1) + 0.5 = 2.5`. The second hidden unit sits exactly at the bend, where the mask would make its gradient 0.
skills: [forward]
''',
)

write(
    "recall/mcq-a-dead-unit.yaml",
    '''id: mcq-a-dead-unit
type: mcq
rev: 1
prompt: |
  During training, hidden unit 3''s score `z1[:, 3]` is negative for every example in the data. What happens to the gradient of its incoming weights, `W1[:, 3]`, and to the unit?
choices:
  - 'The mask `z1 > 0` is 0 for that unit on every example, so `dz1[:, 3]` is all zeros, `dW1[:, 3]` is zero, and the unit never changes again: it''s dead'
  - 'The gradient is large and negative, so the unit recovers on the next step'
  - 'The gradient is the same as the other units'', since `dW1 = X.T @ dz1` doesn''t depend on `z1`'
  - 'Only `b1[3]` stops changing; the weights keep learning'
answer: 0
explanation: |
  ReLU''s derivative is 0 on the left of the bend. If the unit is off for every example, every entry of its column of the mask is 0, so no gradient reaches `W1[:, 3]` or `b1[3]`, and nothing can push its scores back above zero. That''s a dead unit, and the usual causes are a learning rate too large or an unlucky start.
skills: [train, backward]
''',
)

write(
    "recall/review-predict-the-mask.yaml",
    f'''id: review-predict-the-mask
type: predict_output
rev: 1
prompt: |
  ReLU's part of the backward pass. What does the program print?
code: |
{block(REVIEW_MASK)}expected_output: |
{block(REVIEW_MASK_OUT)}explanation: |
  `z1 > 0` is `[[True, False], [False, True]]`, and multiplying by it keeps the gradient where the unit was on and zeroes it where the unit was off. The gradient passes through an active ReLU unchanged and stops at an inactive one.
skills: [backward]
''',
)

write(
    "recall/review-mcq-why-h.yaml",
    '''id: review-mcq-why-h
type: mcq
rev: 1
prompt: |
  In the backward pass, `dW2 = h.T @ dz2`. Why `h`?
choices:
  - 'Because `z2 = h @ W2 + b2`: the derivative of the output score with respect to `W2` is `h`, so each weight''s gradient is its input times the gradient at its output, summed over the examples'
  - 'Because `h` is the largest array available, which makes the gradient more accurate'
  - 'Because ReLU''s derivative is `h`'
  - 'It should be `X`; `h` is a bug'
answer: 0
explanation: |
  A weight multiplies its input; nudge the weight and the score moves by the input times the nudge. So the gradient of the loss with respect to the weight is the input (`h` for the output layer, `X` for the first layer) times the gradient arriving at the score, added over examples, which is what the transposed product does.
skills: [backward]
''',
)

write(
    "recall/review-mcq-a-dead-layer.yaml",
    '''id: review-mcq-a-dead-layer
type: mcq
rev: 1
prompt: |
  You raise the learning rate from 0.5 to 50. After a few steps the loss sits at 0.69 and stays there, and every hidden unit's `z1` is negative for every example. What happened?
choices:
  - 'The huge steps pushed every hidden unit''s scores below zero; all the masks are zero, so no gradient reaches `W1` or `b1`, and the output can only learn a constant, which is guessing (`log 2` is 0.693)'
  - 'The network has converged; 0.69 is the floor for XOR'
  - 'Nothing is wrong with the units; the learning rate just needs to be larger still'
  - 'The gradient check must have been wrong'
answer: 0
explanation: |
  A dead unit is one whose ReLU is off for every example, and a rate of 50 can kill the whole layer in one step. With every mask zero, `dz1` is zero, the first layer never changes, and the only thing still learning is `b2`, which settles at the loss of guessing a half. XOR's floor is near zero, as the worked example showed at rate 0.5.
skills: [train]
''',
)

write(
    "recall/review-mcq-where-is-the-bug.yaml",
    '''id: review-mcq-where-is-the-bug
type: mcq
rev: 1
prompt: |
  Your gradient check passes for `W2` and `b2` but fails for `W1` and `b1`. Where is the bug most likely?
choices:
  - 'Between the two layers: in `dh`, the ReLU mask or the `dW1` and `db1` lines, since everything up to `dz2` is proven right by the `W2` check'
  - 'In the forward pass, since the check uses it'
  - 'In `dz2`, since every gradient depends on it'
  - 'In the loss function'
answer: 0
explanation: |
  The checks are ordered like the chain. `dW2` is `h.T @ dz2`, so if it matches the numeric gradient, `dz2` and the forward values are right. What `W1` adds is `dh`, the mask and the first layer''s products; one of those is wrong. The check tells you not just that there''s a bug, but which lines it''s in.
skills: [check]
''',
)

# =====================================================================================
# exercises
# =====================================================================================

write(
    "exercises/example-a-tiny-network-trained/exercise.yaml",
    f'''id: example-a-tiny-network-trained
stage: worked_example
rev: 1
title: "A tiny network, checked and trained"
prompt: |
  This program builds a network with two inputs, four hidden ReLU units and one sigmoid output, runs the forward and backward passes, checks one gradient numerically, and trains it to learn XOR. Press **Run**, then read how each part works.
steps:
  - label: "The data and the starting weights"
    lines: "8-13"
    note: "Four examples: XOR is 1 when exactly one input is 1. No single straight line separates the ones from the zeros, which is why a hidden layer is needed. The weights are small hand-picked numbers; in practice they're small and random."
  - label: "The forward pass"
    lines: "16-20"
    note: "`z1` is every example's four hidden scores at once (4 by 4), `h` bends them with ReLU, and the output score `h @ W2 + b2` goes through the sigmoid. The function returns `z1` and `h` as well as `p`, because the backward pass needs them."
  - label: "The loss"
    lines: "23-24"
    note: "The mean cross-entropy from the last topic. At the start it's {LOSS0}, about `log 2`: the network is guessing."
  - label: "The backward pass"
    lines: "27-35"
    note: "The chain rule, one line per link, from the loss inward. `dz2 = (p - y) / n` is the loss-through-sigmoid gradient. `dW2 = h.T @ dz2` because the output score is `h @ W2`: a weight's gradient is its input times the gradient at its output. `dh` spreads `dz2` back along `W2`. `dz1` applies ReLU's mask. `dW1 = X.T @ dz1` is the first layer's version of the same rule, with `X` as the input."
  - label: "The shapes"
    lines: "38-41"
    note: "Each gradient has the shape of its parameter: `dW1` is 2 by 4, `db1` and `dW2` have four entries. A shape error here means a wrong product or a missing transpose."
  - label: "The gradient check"
    lines: "43-51"
    note: "For each of the eight entries of `W1`: nudge it by a millionth each way, run the whole forward pass and the loss, and divide. `np.allclose` against `dW1` prints `True`. This is done once, before training, every time a backward pass is written."
  - label: "Training"
    lines: "53-63"
    note: "The descent loop: forward, backward, step every parameter against its gradient at rate 0.5. The loss falls from {LOSS0} past {LOSS100} at step 100 to {FINAL_LOSS} at the end, the four predictions round to `[0, 1, 1, 0]`, and the accuracy is 1.0. The network has learned XOR."
''',
)
write("exercises/example-a-tiny-network-trained/solution.py", EXAMPLE)
write(
    "exercises/example-a-tiny-network-trained/test_exercise.py",
    f'''from checks import run


def test_the_walkthrough():
    """Prints the first predictions and loss, the gradient shapes, the check, the loss curve and the trained predictions."""
    assert run() == {EXAMPLE_OUT!r}
''',
)

write(
    "exercises/fill-the-backward-pass/exercise.yaml",
    f'''id: fill-the-backward-pass
stage: fill_in
rev: 1
title: "The backward pass"
prompt: |
  The network, its forward pass and its loss are written; `backward` is missing two pieces. Replace each `...` so the gradient flows back through `W2` and then through ReLU's mask, and the program prints `dW2`, `dW1` and a numeric check of `dW1`:

  ```
{block(FILL_OUT)}  ```

  The program fails until every `...` is replaced.
hints:
  - "`dh` spreads each example's `dz2` back along the output weights: `np.outer(dz2, W2)`."
  - "ReLU's derivative is 1 where `z1` was positive: the mask is `z1 > 0`."
skills: [backward, check]
''',
)
write("exercises/fill-the-backward-pass/starter.py", FILL_STARTER)
write("exercises/fill-the-backward-pass/solution.py", FILL_SOLUTION)
write(
    "exercises/fill-the-backward-pass/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints dW2, dW1 and True."""
    printed = run()
    assert printed == {FILL_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_shapes_and_the_mask():
    """Gradients have their parameters' shapes, and a hidden unit that is off for every example gets a zero gradient."""
    backward = function("backward")
    X = np.array([[1.0, 0.0], [0.0, 1.0]])
    y = np.array([1.0, 0.0])
    W2 = np.array([0.5, -0.5, 1.0])
    z1 = np.array([[1.0, -1.0, 2.0], [0.5, -2.0, 1.0]])
    h = np.maximum(z1, 0.0)
    p = np.array([0.7, 0.4])
    dW1, db1, dW2, db2 = backward(X, y, W2, z1, h, p)
    assert dW1.shape == (2, 3) and db1.shape == (3,) and dW2.shape == (3,)
    assert np.abs(dW1[:, 1]).max() == 0 and db1[1] == 0
''',
)
write("exercises/fill-the-backward-pass/wrong/mask-is-h.py", FILL_H_MASK)
write(
    "exercises/fill-the-backward-pass/wrong/typed-in.py",
    "import numpy as np\n\n\n"
    + "def backward(X, y, W2, z1, h, p):\n    return np.zeros((2, 4)), np.zeros(4), np.zeros(4), 0.0\n\n\n"
    + "".join(f"print({line!r})\n" for line in FILL_OUT.splitlines()),
)

write(
    "exercises/write-numeric-grad/exercise.yaml",
    f'''id: write-numeric-grad
stage: write
rev: 1
title: "A numeric gradient for a matrix"
prompt: |
  The gradient check needs a numeric gradient for a whole matrix of weights. Write `numeric_grad(f, W, h=1e-6)`, which takes a function `f` of an array `W` that returns one number, and returns an array the shape of `W` holding the central difference for every entry (nudge that one entry by `h` up and down, leaving the rest alone). `np.ndindex(W.shape)` walks every index of an array of any shape. Then print it for `f(W) = np.sum(W**2)` on the starter's `M`, rounded to 4 places, and whether it matches the rule `2 * M`:

  ```
{block(WRITE_OUT)}  ```
hints:
  - "`for index in np.ndindex(W.shape):` gives tuples like `(0, 1)` that index `W` directly."
  - "Build a `step` array of zeros with `h` at `index`, and use `W + step` and `W - step`."
skills: [check]
''',
)
write("exercises/write-numeric-grad/starter.py", WRITE_STARTER)
write("exercises/write-numeric-grad/solution.py", WRITE_SOLUTION)
write(
    "exercises/write-numeric-grad/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints 2M and True."""
    printed = run()
    assert printed == {WRITE_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_other_shapes_and_functions():
    """Works for a 2-by-3 matrix with f = sum of cubes (gradient 3W²) and for a vector with f = a dot product."""
    numeric_grad = function("numeric_grad")
    W = np.array([[1.0, 2.0, -1.0], [0.5, 0.0, 3.0]])
    assert np.allclose(numeric_grad(lambda W: np.sum(W**3), W), 3 * W**2, atol=1e-5)
    v = np.array([1.0, -2.0, 0.5])
    a = np.array([3.0, 1.0, 2.0])
    assert np.allclose(numeric_grad(lambda v: v @ a, v), a, atol=1e-6)
''',
)
write(
    "exercises/write-numeric-grad/wrong/nudges-everything.py",
    WRITE_STARTER + '''

def numeric_grad(f, W, h=1e-6):
    grad = np.zeros_like(W)
    for index in np.ndindex(W.shape):
        grad[index] = (f(W + h) - f(W - h)) / (2 * h)
    return grad


print(np.round(numeric_grad(lambda W: np.sum(W**2), M), 4))
print(np.allclose(numeric_grad(lambda W: np.sum(W**2), M), 2 * M, atol=1e-6))
''',
)
write(
    "exercises/write-numeric-grad/wrong/typed-in.py",
    WRITE_STARTER + '''

def numeric_grad(f, W, h=1e-6):
    return 2 * W


print(np.round(2 * M, 4))
print(True)
''',
)

# --- the proof -------------------------------------------------------------------------------------------------

write(
    "exercises/build-a-tiny-network/exercise.yaml",
    f'''id: build-a-tiny-network
stage: build
rev: 1
title: "A tiny network, from scratch"
prompt: |
  Starting from a blank editor, write a one-hidden-layer network with its training loop. The parameters live in a dict `params` with keys `"W1"` (2 by 4), `"b1"` (4), `"W2"` (4) and `"b2"` (a 0-d array, `np.array(0.0)`):

  - `forward(X, params)` returns `(z1, h, p)`: `z1 = X @ W1 + b1`, `h = np.maximum(z1, 0.0)`, `p = sigmoid(h @ W2 + b2)`. Write `sigmoid` yourself.
  - `loss(p, y)`: the mean cross-entropy, as a float.
  - `backward(X, y, params, z1, h, p)` returns a dict of gradients with the same keys as `params`, by the chain rule from `dz2 = (p - y) / n` inward.
  - `train(X, y, params, rate, steps)` runs `steps` steps of descent, updating every entry of `params` in place (`params[key] = params[key] - rate * grads[key]`), and returns the list of losses, one per step, measured before the step.
  - `numeric_grad(f, W, h=1e-6)`: the central difference for every entry of `W`, as in the practice exercise.

  Then, on XOR with the starting weights below, print a `check` line per parameter (`np.allclose` of your gradient against `numeric_grad` of the loss, `atol=1e-6`), train for 1000 steps at rate 0.5, and print the losses at steps 0, 100, 500 and the last, the final predictions rounded to 2 places, and the accuracy:

  ```python
{block(DATA)}  params = {{
      "W1": np.array([[0.3, 0.8, 0.3, -1.3], [0.9, 0.4, -0.5, 0.6]]),
      "b1": np.array([0.2, 0.1, 0.1, 0.3]),
      "W2": np.array([-0.7, -0.2, -0.5, 0.6]),
      "b2": np.array(0.0),
  }}
  ```

  ```
{block(BUILD_OUT)}  ```

  The checks compare every gradient with a numeric one from other starting weights, and train from the weights above.
skills: [forward, backward, check, train]
''',
)
write("exercises/build-a-tiny-network/starter.py", "")
write("exercises/build-a-tiny-network/solution.py", BUILD_SOLUTION)
write(
    "exercises/build-a-tiny-network/test_exercise.py",
    f'''import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).

X = np.array([[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]])
Y = np.array([0.0, 1.0, 1.0, 0.0])


def other_params():
    return {{
        "W1": np.array([[0.2, -0.5, -0.4, -2.4], [1.8, 1.1, -0.3, 0.8]]),
        "b1": np.array([0.1, -0.3, 0.5, -0.2]),
        "W2": np.array([-0.3, -0.8, 0.5, -0.1]),
        "b2": np.array(0.4),
    }}


def start_params():
    return {{
        "W1": np.array([[0.3, 0.8, 0.3, -1.3], [0.9, 0.4, -0.5, 0.6]]),
        "b1": np.array([0.2, 0.1, 0.1, 0.3]),
        "W2": np.array([-0.7, -0.2, -0.5, 0.6]),
        "b2": np.array(0.0),
    }}


def central(f, W, h=1e-6):
    grad = np.zeros_like(W)
    for index in np.ndindex(W.shape):
        step = np.zeros_like(W)
        step[index] = h
        grad[index] = (f(W + step) - f(W - step)) / (2 * h)
    return grad


def test_the_output():
    """Prints four checks, the loss curve, the predictions and the accuracy."""
    assert run() == {BUILD_OUT!r}


def test_forward_and_loss():
    """forward gives the right shapes and a loss of about log 2 for a network that guesses a half."""
    forward = function("forward")
    loss = function("loss")
    params = other_params()
    z1, h, p = forward(X, params)
    assert z1.shape == (4, 4) and h.shape == (4, 4) and p.shape == (4,)
    assert (h >= 0).all()
    assert abs(loss(np.array([0.5, 0.5, 0.5, 0.5]), Y) - np.log(2)) < 1e-9


def test_every_gradient_from_other_weights():
    """From other starting weights, every gradient matches a numeric one."""
    forward = function("forward")
    loss = function("loss")
    backward = function("backward")
    params = other_params()
    z1, h, p = forward(X, params)
    grads = backward(X, Y, params, z1, h, p)
    for key in params:
        numeric = central(lambda value, key=key: loss(forward(X, {{**params, key: value}})[2], Y), params[key])
        assert np.allclose(grads[key], numeric, atol=1e-6), key


def test_training_learns_xor():
    """train returns one loss per step, the loss falls below 0.05, and all four predictions are right."""
    forward = function("forward")
    train = function("train")
    params = start_params()
    losses = train(X, Y, params, 0.5, 1000)
    assert len(losses) == 1000
    assert losses[-1] < 0.05 < losses[0]
    p = forward(X, params)[2]
    assert ((p > 0.5) == (Y == 1)).all()
''',
)
write("exercises/build-a-tiny-network/wrong/no-mask.py", BUILD_NO_MASK)
write("exercises/build-a-tiny-network/wrong/ascent.py", BUILD_ASCENT)
write("exercises/build-a-tiny-network/wrong/dz2-without-the-mean.py", BUILD_NO_N)
write(
    "exercises/build-a-tiny-network/wrong/typed-in.py",
    "import numpy as np\n\n\n"
    + "def forward(X, params):\n    z1 = np.zeros((4, 4))\n    return z1, z1, np.array([0.0, 1.0, 1.0, 0.0])\n\n\n"
    + "def loss(p, y):\n    return 0.0\n\n\n"
    + "def backward(X, y, params, z1, h, p):\n    return {key: np.zeros_like(value) for key, value in params.items()}\n\n\n"
    + "def train(X, y, params, rate, steps):\n    return [0.0] * steps\n\n\n"
    + "def numeric_grad(f, W, h=1e-6):\n    return np.zeros_like(W)\n\n\n"
    + "".join(f"print({line!r})\n" for line in BUILD_OUT.splitlines()),
)

write(
    "exercises/debug-training-loop/exercise.yaml",
    f'''id: debug-training-loop
stage: debug
rev: 1
title: "A network that won't learn"
prompt: |
  This program trains the tiny network on XOR and should print:

  ```
{block(DEBUG_OUT)}  ```

  It has two bugs, both in `backward`. Run it: the first is a shape error at `dW1`, because `X @ dz1` multiplies a 4-by-2 matrix by a 4-by-4 one; the first layer's weight gradient is the input **transposed** times `dz1`, like `h.T @ dz2` a layer later. Fix that and it runs, but the loss doesn't reach the floor and the predictions stay wrong: `dz1` multiplies by `h`, ReLU's **value**, where it should multiply by ReLU's **derivative**, the mask `z1 > 0`.
skills: [backward, train]
''',
)
write("exercises/debug-training-loop/starter.py", DEBUG_STARTER)
write("exercises/debug-training-loop/solution.py", DEBUG_SOLUTION)
write(
    "exercises/debug-training-loop/test_exercise.py",
    f'''import numpy as np

from checks import function, run

EXPECTED = {DEBUG_OUT!r}


def test_the_output():
    """Prints the starting loss, the final loss and the predictions."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\\n{{EXPECTED}}\\nYour program printed:\\n{{printed}}"


def test_the_mask():
    """A hidden unit that is off for every example gets a zero gradient; dW1 has W1's shape."""
    backward = function("backward")
    X = np.array([[1.0, 0.0], [0.0, 1.0]])
    y = np.array([1.0, 0.0])
    W2 = np.array([0.5, -0.5, 1.0, 2.0])
    z1 = np.array([[1.0, -1.0, 2.0, 0.5], [0.5, -2.0, 1.0, 0.1]])
    h = np.maximum(z1, 0.0)
    p = np.array([0.7, 0.4])
    dW1, db1, dW2, db2 = backward(X, y, W2, z1, h, p)
    assert dW1.shape == (2, 4)
    assert np.abs(dW1[:, 1]).max() == 0
    assert np.abs(dW1[:, 0]).max() > 0
''',
)
write("exercises/debug-training-loop/wrong/shape-only.py", DEBUG_SHAPE_ONLY)
write(
    "exercises/debug-training-loop/wrong/typed-in.py",
    "import numpy as np\n\n\n"
    + "def backward(X, y, W2, z1, h, p):\n    return np.zeros((2, 4)), np.zeros(4), np.zeros(4), 0.0\n\n\n"
    + "".join(f"print({line!r})\n" for line in DEBUG_OUT.splitlines()),
)

# --- review pool: a code exercise ------------------------------------------------------------------------------

write(
    "exercises/review-forward/exercise.yaml",
    f'''id: review-forward
stage: review_code
rev: 1
title: "A forward pass, from memory"
prompt: |
  Write `forward(X, W1, b1, W2, b2)`, which returns the network's output probability `p` (ReLU hidden layer, sigmoid output), and print it for the starter's one example rounded to 3 places:

  ```
{block(REVIEW_CODE_OUT)}  ```
skills: [forward]
''',
)
write("exercises/review-forward/starter.py", REVIEW_CODE_STARTER)
write("exercises/review-forward/solution.py", REVIEW_CODE_SOLUTION)
write(
    "exercises/review-forward/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints [0.924]."""
    assert run() == {REVIEW_CODE_OUT!r}


def test_two_examples_and_the_bend():
    """Two examples give two probabilities, and a negative hidden score is bent to zero before the output."""
    forward = function("forward")
    X = np.array([[1.0, 2.0], [-3.0, 0.0]])
    W1 = np.array([[1.0, -1.0], [0.0, 1.0]])
    b1 = np.array([0.0, -1.0])
    W2 = np.array([2.0, -1.0])
    p = forward(X, W1, b1, W2, 0.5)
    assert p.shape == (2,)
    assert abs(p[1] - 1 / (1 + np.exp(1.5))) < 1e-9
''',
)
write(
    "exercises/review-forward/wrong/no-bend.py",
    REVIEW_CODE_STARTER + '''

def forward(X, W1, b1, W2, b2):
    h = X @ W1 + b1
    return 1 / (1 + np.exp(-(h @ W2 + b2)))


print(np.round(forward(X, W1, b1, W2, b2), 3))
''',
)
write(
    "exercises/review-forward/wrong/typed-in.py",
    REVIEW_CODE_STARTER + '''

def forward(X, W1, b1, W2, b2):
    return np.array([0.924])


print("[0.924]")
''',
)

print("ml.calc.backpropagation written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
