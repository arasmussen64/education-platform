"""Writes ml.m4.checkpoint, "Checkpoint 4: train a tiny network", which closes
the ML track's Module 4. Run from the repository root under uv (python -m uv
run python <this file>), so every program's expected output is captured from
CPython rather than typed in. Files are written as bytes with LF endings."""

import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path("content/topics/ml.m4.checkpoint")


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


# --- the pieces ------------------------------------------------------------------------

GRID = '''g = np.array([-1.5, -0.5, 0.5, 1.5])
X = np.array([[a, b] for a in g for b in g])
'''
LABELS = {
    "circle": "y = (X[:, 0] ** 2 + X[:, 1] ** 2 < 1).astype(float)\n",
    "quadrants": "y = (X[:, 0] * X[:, 1] > 0).astype(float)\n",
    "band": "y = (np.abs(X[:, 0] + X[:, 1]) < 1).astype(float)\n",
}
PARAMS = '''params = {
    "W1": np.array([[0.2, -0.4, -0.3, -2.0], [1.4, 0.9, -0.3, 0.6]]),
    "b1": np.array([0.1, -0.2, 0.25, -0.15]),
    "W2": np.array([-0.3, -0.6, 0.4, -0.1]),
    "b2": np.array(0.0),
}
'''
OTHER_PARAMS = '''{
        "W1": np.array([[-0.5, -0.1, 1.3, 0.5], [-1.3, 0.2, -0.5, 0.1]]),
        "b1": np.array([-0.5, 0.1, 0.15, 0.5]),
        "W2": np.array([0.3, 0.4, -1.2, 1.8]),
        "b2": np.array(0.2),
    }'''

SIGMOID = '''def sigmoid(z):
    return 1 / (1 + np.exp(-z))
'''
FORWARD = '''def forward(X, params):
    z1 = X @ params["W1"] + params["b1"]
    h = np.maximum(z1, 0.0)
    p = sigmoid(h @ params["W2"] + params["b2"])
    return z1, h, p
'''
LOSS = '''def loss(p, y):
    p = np.clip(p, 1e-12, 1 - 1e-12)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))
'''
BACKWARD = '''def backward(X, y, params, z1, h, p):
    dz2 = (p - y) / len(y)
    dh = np.outer(dz2, params["W2"])
    dz1 = dh * (z1 > 0)
    return {"W1": X.T @ dz1, "b1": dz1.sum(axis=0), "W2": h.T @ dz2, "b2": dz2.sum()}
'''
TRAIN = '''def train(X, y, params, rate, beta, steps):
    vel = {key: np.zeros_like(value) for key, value in params.items()}
    losses = []
    for step in range(steps):
        z1, h, p = forward(X, params)
        losses.append(loss(p, y))
        grads = backward(X, y, params, z1, h, p)
        for key in params:
            vel[key] = beta * vel[key] + grads[key]
            params[key] = params[key] - rate * vel[key]
    return losses
'''
REPORT = '''def report(X, y, params):
    losses = train(X, y, params, 0.1, 0.9, 2000)
    p = forward(X, params)[2]
    print("loss", round(losses[0], 3), round(losses[500], 3), round(losses[-1], 3))
    print("accuracy", np.mean((p > 0.5) == (y == 1)))
    print("classes", (p > 0.5).astype(int))
'''
FUNCTIONS = SIGMOID + "\n\n" + FORWARD + "\n\n" + LOSS + "\n\n" + BACKWARD + "\n\n" + TRAIN + "\n\n" + REPORT


def build_solution(label):
    return "import numpy as np\n\n\n" + FUNCTIONS + "\n\n" + GRID + LABELS[label] + PARAMS + "report(X, y, params)\n"


EXPECTED = {label: out(build_solution(label)) for label in LABELS}
for label, text in EXPECTED.items():
    print(label + ":\n" + text)
    assert "accuracy 1.0\n" in text and "e-" not in text and "nan" not in text, text
    lines = text.splitlines()
    assert lines[0].startswith("loss 0.") and float(lines[0].split()[-1]) < 0.01, text
    nudged = build_solution(label).replace('"W1": np.array([[0.2,', '"W1": np.array([[0.2000000001,')
    assert out(nudged) == text, "a ninth-decimal nudge changed the output"
MAIN_EXPECTED = EXPECTED["circle"]

# known-wrong variants of the build, each of which must fail
WRONG = {
    "no-mask": ("    dz1 = dh * (z1 > 0)\n", "    dz1 = dh\n"),
    "no-velocity": ("            vel[key] = beta * vel[key] + grads[key]\n", "            vel[key] = grads[key]\n"),
    "ascent": ("            params[key] = params[key] - rate * vel[key]\n", "            params[key] = params[key] + rate * vel[key]\n"),
}
for name, (old, new) in WRONG.items():
    assert old in build_solution("circle"), name
    assert out(build_solution("circle").replace(old, new)) != MAIN_EXPECTED, name

# --- the debug: three bugs, each hiding the next -----------------------------------------------

DEBUG_SOLUTION = build_solution("circle")
BUG_SHAPE = ('    dh = np.outer(dz2, params["W2"])\n', '    dh = dz2 @ params["W2"]\n')
BUG_SIGN = WRONG["ascent"]
BUG_ORDER = ('    return {"W1": X.T @ dz1,', '    return {"W1": X.T @ dh,')
for old, new in (BUG_SHAPE, BUG_SIGN, BUG_ORDER):
    assert old in DEBUG_SOLUTION, old
DEBUG_STARTER = DEBUG_SOLUTION.replace(*BUG_SHAPE).replace(*BUG_SIGN).replace(*BUG_ORDER)
DEBUG_TWO_LEFT = DEBUG_SOLUTION.replace(*BUG_SIGN).replace(*BUG_ORDER)
DEBUG_ONE_LEFT = DEBUG_SOLUTION.replace(*BUG_ORDER)
crash = subprocess.run([sys.executable, "-c", DEBUG_STARTER], capture_output=True, text=True)
assert crash.returncode != 0 and "ValueError" in crash.stderr, crash.stderr[-400:]
print("two bugs left prints:\n" + out(DEBUG_TWO_LEFT))
print("one bug left prints:\n" + out(DEBUG_ONE_LEFT))
assert out(DEBUG_TWO_LEFT) != MAIN_EXPECTED and out(DEBUG_ONE_LEFT) != MAIN_EXPECTED
ONE_LEFT_LAST = out(DEBUG_ONE_LEFT).splitlines()[0].split()[-1]
MAIN_LAST = MAIN_EXPECTED.splitlines()[0].split()[-1]
assert float(ONE_LEFT_LAST) > 3 * float(MAIN_LAST), (ONE_LEFT_LAST, MAIN_LAST)

# --- the solved sibling: XOR with momentum ---------------------------------------------------------

EXAMPLE = "import numpy as np\n\n\n" + SIGMOID + "\n\n" + FORWARD + "\n\n" + LOSS + "\n\n" + BACKWARD + "\n\n" + TRAIN + '''

X = np.array([[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]])
y = np.array([0.0, 1.0, 1.0, 0.0])
params = {
    "W1": np.array([[0.3, 0.8, 0.3, -1.3], [0.9, 0.4, -0.5, 0.6]]),
    "b1": np.array([0.2, 0.1, 0.1, 0.3]),
    "W2": np.array([-0.7, -0.2, -0.5, 0.6]),
    "b2": np.array(0.0),
}
losses = train(X, y, params, 0.1, 0.9, 500)
print("loss", round(losses[0], 3), round(losses[100], 3), round(losses[-1], 3))
p = forward(X, params)[2]
print("accuracy", np.mean((p > 0.5) == (y == 1)))
print("classes", (p > 0.5).astype(int))
'''
EXAMPLE_OUT = out(EXAMPLE)
print("example:\n" + EXAMPLE_OUT)
assert EXAMPLE_OUT.endswith("accuracy 1.0\nclasses [0 1 1 0]\n"), EXAMPLE_OUT
EXAMPLE_LINES = EXAMPLE.splitlines()


def ln(text):
    return next(i + 1 for i, line in enumerate(EXAMPLE_LINES) if text in line)


# --- the steps -------------------------------------------------------------------------------------------

PRELUDE = "import numpy as np\n\n" + GRID + LABELS["circle"] + PARAMS + "\n\n" + SIGMOID + "\n\n"

STEP1_HEAD = PRELUDE + '''def forward(X, params):
    z1 = X @ params["W1"] + params["b1"]
    h = np.maximum(z1, BEND)
    p = sigmoid(h @ params["W2"] + params[BIAS])
    return z1, h, p


z1, h, p = forward(X, params)
print(z1.shape, h.shape, p.shape)
print(np.round(p[:4], 3))
'''
STEP1_SOLUTION = STEP1_HEAD.replace("BEND", "0.0").replace("BIAS", '"b2"')
STEP1_STARTER = STEP1_HEAD.replace("BEND", "...").replace("BIAS", "...")
STEP1_OUT = out(STEP1_SOLUTION)
print("step 1:\n" + STEP1_OUT)
assert STEP1_OUT.startswith("(16, 4) (16, 4) (16,)\n"), STEP1_OUT

STEP2_HEAD = PRELUDE + FORWARD + '''

def loss(p, y):
    p = np.clip(p, 1e-12, 1 - 1e-12)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(ONE - p)))


z1, h, p = forward(X, params)
print(round(loss(p, y), 3))
dz2 = (p - y) / N
print(np.round(dz2[:4], 4))
'''
STEP2_SOLUTION = STEP2_HEAD.replace("ONE", "1").replace("/ N", "/ len(y)")
STEP2_STARTER = STEP2_HEAD.replace("ONE", "...").replace("/ N", "/ ...")
STEP2_OUT = out(STEP2_SOLUTION)
print("step 2:\n" + STEP2_OUT)

STEP3_HEAD = PRELUDE + FORWARD + "\n\n" + LOSS + '''

def backward(X, y, params, z1, h, p):
    dz2 = (p - y) / len(y)
    dh = np.outer(dz2, params[OUTER])
    dz1 = dh * (z1 > ZERO)
    return {"W1": X.T @ dz1, "b1": dz1.sum(axis=0), "W2": h.T @ dz2, "b2": dz2.sum()}


z1, h, p = forward(X, params)
grads = backward(X, y, params, z1, h, p)
print({key: grads[key].shape for key in grads})
numeric = np.zeros((2, 4))
for i in range(2):
    for j in range(4):
        step = np.zeros((2, 4))
        step[i, j] = 1e-6
        up = loss(forward(X, {**params, "W1": params["W1"] + step})[2], y)
        down = loss(forward(X, {**params, "W1": params["W1"] - step})[2], y)
        numeric[i, j] = (up - down) / 2e-6
print(np.allclose(grads["W1"], numeric, atol=1e-6))
'''
STEP3_SOLUTION = STEP3_HEAD.replace("OUTER", '"W2"').replace("ZERO", "0")
STEP3_STARTER = STEP3_HEAD.replace("OUTER", "...").replace("ZERO", "...")
STEP3_OUT = out(STEP3_SOLUTION)
print("step 3:\n" + STEP3_OUT)
assert STEP3_OUT.endswith("True\n"), STEP3_OUT

STEP4_HEAD = PRELUDE + FORWARD + "\n\n" + LOSS + "\n\n" + BACKWARD + '''

def train(X, y, params, rate, beta, steps):
    vel = {key: np.zeros_like(value) for key, value in params.items()}
    losses = []
    for step in range(steps):
        z1, h, p = forward(X, params)
        losses.append(loss(p, y))
        grads = backward(X, y, params, z1, h, p)
        for key in params:
            vel[key] = BETA * vel[key] + grads[key]
            params[key] = params[key] - RATE * vel[key]
    return losses


losses = train(X, y, params, 0.1, 0.9, 300)
print(round(losses[0], 3), round(losses[-1], 3))
print(np.round(params["W2"], 3))
'''
STEP4_SOLUTION = STEP4_HEAD.replace("BETA", "beta").replace("RATE", "rate")
STEP4_STARTER = STEP4_HEAD.replace("BETA", "...").replace("RATE", "...")
STEP4_PLAIN = STEP4_SOLUTION.replace("            vel[key] = beta * vel[key] + grads[key]\n", "            vel[key] = grads[key]\n")
STEP4_OUT = out(STEP4_SOLUTION)
print("step 4:\n" + STEP4_OUT)
assert out(STEP4_PLAIN) != STEP4_OUT

# =====================================================================================
# the build (and its fresh versions)
# =====================================================================================

TEST_SKILLS = '''# Every test names the module skills it checks (ADR-0012), so a failed test
# says which topics to revisit.
test_skills:
  test_the_output: [ml.calc.backpropagation/train, ml.calc.optimizers/momentum, ml.calc.loss-functions/cross-entropy]
  test_forward_and_loss: [ml.calc.backpropagation/forward, ml.calc.loss-functions/cross-entropy]
  test_every_gradient_from_other_weights: [ml.calc.backpropagation/backward, ml.calc.backpropagation/check, ml.calc.chain-rule/many, ml.calc.loss-functions/gradient]
  test_the_momentum_update: [ml.calc.optimizers/momentum, ml.calc.descent-in-many-dimensions/loop]
  test_training_learns_the_data: [ml.calc.backpropagation/train, ml.calc.descent-in-many-dimensions/rate]
'''


def build_tests(label):
    return f'''import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).

g = np.array([-1.5, -0.5, 0.5, 1.5])
X = np.array([[a, b] for a in g for b in g])
{LABELS[label]}

def start_params():
    return {{
        "W1": np.array([[0.2, -0.4, -0.3, -2.0], [1.4, 0.9, -0.3, 0.6]]),
        "b1": np.array([0.1, -0.2, 0.25, -0.15]),
        "W2": np.array([-0.3, -0.6, 0.4, -0.1]),
        "b2": np.array(0.0),
    }}


def other_params():
    return {OTHER_PARAMS}


def central(f, W, h=1e-6):
    grad = np.zeros_like(W)
    for index in np.ndindex(W.shape):
        step = np.zeros_like(W)
        step[index] = h
        grad[index] = (f(W + step) - f(W - step)) / (2 * h)
    return grad


def test_the_output():
    """Prints the loss curve, the accuracy and the classes."""
    assert run() == {EXPECTED[label]!r}


def test_forward_and_loss():
    """forward gives the right shapes with a non-negative hidden layer, and loss is log 2 for guessing a half."""
    forward = function("forward")
    loss = function("loss")
    z1, h, p = forward(X, other_params())
    assert z1.shape == (16, 4) and h.shape == (16, 4) and p.shape == (16,)
    assert (h >= 0).all() and ((p > 0) & (p < 1)).all()
    assert abs(loss(np.full(16, 0.5), y) - np.log(2)) < 1e-9


def test_every_gradient_from_other_weights():
    """From other starting weights, every gradient matches a numeric one."""
    forward = function("forward")
    loss = function("loss")
    backward = function("backward")
    params = other_params()
    z1, h, p = forward(X, params)
    grads = backward(X, y, params, z1, h, p)
    for key in params:
        numeric = central(lambda value, key=key: loss(forward(X, {{**params, key: value}})[2], y), params[key])
        assert np.allclose(grads[key], numeric, atol=1e-6), key


def test_the_momentum_update():
    """Two steps of train match two heavy-ball steps computed from the program's own backward pass."""
    forward = function("forward")
    backward = function("backward")
    train = function("train")
    expected = other_params()
    vel = {{key: np.zeros_like(value) for key, value in expected.items()}}
    for step in range(2):
        z1, h, p = forward(X, expected)
        grads = backward(X, y, expected, z1, h, p)
        for key in expected:
            vel[key] = 0.9 * vel[key] + grads[key]
            expected[key] = expected[key] - 0.1 * vel[key]
    params = other_params()
    losses = train(X, y, params, 0.1, 0.9, 2)
    assert len(losses) == 2
    for key in params:
        assert np.allclose(params[key], expected[key]), key


def test_training_learns_the_data():
    """From the starting weights, 2000 steps give every class right and a loss below 0.05, with one loss per step."""
    forward = function("forward")
    train = function("train")
    params = start_params()
    losses = train(X, y, params, 0.1, 0.9, 2000)
    assert len(losses) == 2000
    assert losses[-1] < 0.05 < losses[0]
    p = forward(X, params)[2]
    assert ((p > 0.5) == (y == 1)).all()
'''


def write_build(folder, title, opening, label, what):
    prompt = f'''  {opening}

  **The data.** Sixteen points on a grid, each labelled 1 or 0:

  ```python
{block(GRID + LABELS[label])}  ```

  {what}

  **The network.** Two inputs, four hidden ReLU units, one sigmoid output. The parameters live in a dict `params` with keys `"W1"` (2 by 4), `"b1"` (4), `"W2"` (4) and `"b2"` (a 0-d array). Write:

  - `forward(X, params)` returning `(z1, h, p)`, with `sigmoid` written by you.
  - `loss(p, y)`: the mean cross-entropy, with `p` clipped into `[1e-12, 1 - 1e-12]` first, as a float.
  - `backward(X, y, params, z1, h, p)` returning a dict of gradients with the same keys, by the chain rule from `dz2 = (p - y) / n` inward.
  - `train(X, y, params, rate, beta, steps)`: `steps` steps of **momentum**, a velocity per parameter (`v = beta * v + grad`, then `param = param - rate * v`), updating `params` in place and returning the list of losses, one per step, measured before the step.
  - `report(X, y, params)`: trains for 2000 steps at rate 0.1 with `beta = 0.9`, then prints three lines: the losses at steps 0, 500 and the last, rounded to 3; the accuracy, `np.mean((p > 0.5) == (y == 1))`; and the predicted classes, `(p > 0.5).astype(int)`.

  **The starting weights**, then the call:

  ```python
{block(PARAMS + "report(X, y, params)" + chr(10))}  ```

  ```
{block(EXPECTED[label])}  ```

  The checks compare every gradient with a numeric one from other starting weights, check two steps of your `train` against the momentum rule, and train from the weights above.
'''
    write(
        f"exercises/{folder}/exercise.yaml",
        f'''id: {folder}
stage: build
rev: 1
title: "{title}"
prompt: |
{prompt}{TEST_SKILLS}''',
    )
    write(f"exercises/{folder}/starter.py", "")
    write(f"exercises/{folder}/solution.py", build_solution(label))
    write(f"exercises/{folder}/test_exercise.py", build_tests(label))
    for name, (old, new) in WRONG.items():
        write(f"exercises/{folder}/wrong/{name}.py", build_solution(label).replace(old, new))
    write(
        f"exercises/{folder}/wrong/typed-in.py",
        "import numpy as np\n\n\n"
        + "def forward(X, params):\n    z1 = np.zeros((16, 4))\n    return z1, z1, np.full(16, 0.5)\n\n\n"
        + "def loss(p, y):\n    return 0.0\n\n\n"
        + "def backward(X, y, params, z1, h, p):\n    return {key: np.zeros_like(value) for key, value in params.items()}\n\n\n"
        + "def train(X, y, params, rate, beta, steps):\n    return [0.0] * steps\n\n\n"
        + "def report(X, y, params):\n"
        + "".join(f"    print({line!r})\n" for line in EXPECTED[label].splitlines())
        + "\n\n"
        + GRID
        + LABELS[label]
        + PARAMS
        + "report(X, y, params)\n",
    )


write_build(
    "build-train-a-tiny-network",
    "Train a tiny network",
    "Starting from a blank editor, do Module 4 in one program: build a two-layer network, train it with backpropagation and momentum on sixteen labelled points, and report its loss and accuracy.",
    "circle",
    "A point is labelled 1 when it lies inside the circle of radius 1 around the origin: the four points nearest the centre. No straight line separates them from the rest, so the hidden layer has work to do.",
)
write_build(
    "build-train-a-tiny-network-quadrants",
    "Train a tiny network: opposite corners",
    "Starting from a blank editor, build a two-layer network and train it with backpropagation and momentum on sixteen labelled points, then report its loss and accuracy.",
    "quadrants",
    "A point is labelled 1 when its two coordinates have the same sign (the first and third quadrants): XOR on a grid, eight of the sixteen points. No straight line separates them from the rest.",
)
write_build(
    "build-train-a-tiny-network-band",
    "Train a tiny network: a diagonal band",
    "Starting from a blank editor, build a two-layer network and train it with backpropagation and momentum on sixteen labelled points, then report its loss and accuracy.",
    "band",
    "A point is labelled 1 when `x + y` is between -1 and 1: a diagonal band through the origin, four of the sixteen points. The band has two edges, so one straight line can't mark it out.",
)

# =====================================================================================
# the debug
# =====================================================================================

write(
    "exercises/debug-training-loop/exercise.yaml",
    f'''id: debug-training-loop
stage: debug
rev: 1
title: "Three bugs in a training loop"
prompt: |
  This is the checkpoint's program on the circle data, and it should print:

  ```
{block(MAIN_EXPECTED)}  ```

  It has three bugs, each of which hides the next. Run it and read each error:

  1. A **shape mistake** in `backward`: the gradient at the hidden layer spreads each example's `dz2` along `W2`, which is an outer product, not a matrix product of two flat arrays.
  2. Once it runs, the loss **climbs** instead of falling: the momentum update has the wrong sign.
  3. Once it falls, it stops well above the floor ({ONE_LEFT_LAST} at the end, where {MAIN_LAST} is expected): a **chain-rule step is out of order**. ReLU's mask must be applied before the first layer's weight gradient is formed, so `dW1` must use `dz1`, not `dh`.
# Every test names the module skills it checks (ADR-0012), so a failed test
# says which topics to revisit.
test_skills:
  test_the_output: [ml.calc.backpropagation/backward, ml.calc.optimizers/momentum, ml.calc.backpropagation/train]
  test_the_mask_comes_before_dW1: [ml.calc.backpropagation/backward, ml.calc.chain-rule/many]
  test_descent_not_ascent: [ml.calc.descent-in-many-dimensions/loop, ml.calc.optimizers/momentum]
''',
)
write("exercises/debug-training-loop/starter.py", DEBUG_STARTER)
write("exercises/debug-training-loop/solution.py", DEBUG_SOLUTION)
write(
    "exercises/debug-training-loop/test_exercise.py",
    f'''import numpy as np

from checks import function, run

EXPECTED = {MAIN_EXPECTED!r}


def test_the_output():
    """Prints the loss curve, the accuracy and the classes."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\\n{{EXPECTED}}\\nYour program printed:\\n{{printed}}"


def test_the_mask_comes_before_dW1():
    """A hidden unit that is off for every example gets a zero gradient in W1 and b1, and dh has the hidden layer's shape."""
    backward = function("backward")
    params = {{
        "W1": np.zeros((2, 3)),
        "b1": np.zeros(3),
        "W2": np.array([0.5, -0.5, 1.0]),
        "b2": np.array(0.0),
    }}
    X = np.array([[1.0, 0.0], [0.0, 1.0]])
    y = np.array([1.0, 0.0])
    z1 = np.array([[1.0, -1.0, 2.0], [0.5, -2.0, 1.0]])
    h = np.maximum(z1, 0.0)
    p = np.array([0.7, 0.4])
    grads = backward(X, y, params, z1, h, p)
    assert grads["W1"].shape == (2, 3)
    assert np.abs(grads["W1"][:, 1]).max() == 0 and grads["b1"][1] == 0
    assert np.abs(grads["W1"][:, 0]).max() > 0


def test_descent_not_ascent():
    """After twenty steps the loss is lower than at the start."""
    forward = function("forward")
    loss = function("loss")
    train = function("train")
    g = np.array([-1.5, -0.5, 0.5, 1.5])
    X = np.array([[a, b] for a in g for b in g])
    y = (X[:, 0] ** 2 + X[:, 1] ** 2 < 1).astype(float)
    params = {{
        "W1": np.array([[0.2, -0.4, -0.3, -2.0], [1.4, 0.9, -0.3, 0.6]]),
        "b1": np.array([0.1, -0.2, 0.25, -0.15]),
        "W2": np.array([-0.3, -0.6, 0.4, -0.1]),
        "b2": np.array(0.0),
    }}
    losses = train(X, y, params, 0.1, 0.9, 20)
    assert loss(forward(X, params)[2], y) < losses[0]
''',
)
write("exercises/debug-training-loop/wrong/two-of-three.py", DEBUG_ONE_LEFT)
write("exercises/debug-training-loop/wrong/one-of-three.py", DEBUG_TWO_LEFT)
write(
    "exercises/debug-training-loop/wrong/typed-in.py",
    "import numpy as np\n\n\n"
    + "def forward(X, params):\n    z1 = np.zeros((16, 4))\n    return z1, z1, np.full(16, 0.5)\n\n\n"
    + "def loss(p, y):\n    return 0.0\n\n\n"
    + "def backward(X, y, params, z1, h, p):\n    return {key: np.zeros_like(value) for key, value in params.items()}\n\n\n"
    + "def train(X, y, params, rate, beta, steps):\n    return [0.0] * steps\n\n\n"
    + "".join(f"print({line!r})\n" for line in MAIN_EXPECTED.splitlines()),
)

# =====================================================================================
# the way through: a solved sibling
# =====================================================================================

write(
    "exercises/example-xor-with-momentum/exercise.yaml",
    f'''id: example-xor-with-momentum
stage: worked_example
rev: 1
title: "XOR again, with momentum"
prompt: |
  The checkpoint's program on the backpropagation topic's four XOR points, with momentum in place of plain descent. Press **Run**, then read how each part works; the checkpoint is this with sixteen points and a report.
steps:
  - label: "The network and the loss"
    lines: "{ln('def sigmoid')}-{ln('return float(-np.mean')}"
    note: "`forward` keeps `z1`, `h` and `p` for the backward pass. `loss` clips `p` away from 0 and 1 before the logs, so a confident prediction can't make the loss infinite; the backpropagation topic's version didn't, and the checkpoint's does."
  - label: "The backward pass, as a dict"
    lines: "{ln('def backward')}-{ln('return {' + chr(34) + 'W1' + chr(34))}"
    note: "The same four lines as the backpropagation topic, returning the gradients under the same keys as the parameters, so a loop over `params` can update every one."
  - label: "Momentum"
    lines: "{ln('def train')}-{ln('return losses')}"
    note: "One velocity per parameter, all starting at zero. Each step: forward, loss, backward, then for every key `v = beta * v + grad` and `param = param - rate * v`. With `beta = 0` this is plain descent; with 0.9, gradients that agree step after step build speed."
  - label: "Training, and the report"
    lines: "{ln('losses = train(X, y, params, 0.1, 0.9, 500)')}-{ln('print(' + chr(34) + 'classes' + chr(34))}"
    note: "Five hundred steps at rate 0.1. The loss falls from {EXAMPLE_OUT.split()[1]} to {EXAMPLE_OUT.splitlines()[0].split()[-1]}, the accuracy is 1.0 and the classes are XOR's `[0, 1, 1, 0]`. The backpropagation topic needed a thousand steps of plain descent at rate 0.5 for the same result."
''',
)
write("exercises/example-xor-with-momentum/solution.py", EXAMPLE)
write(
    "exercises/example-xor-with-momentum/test_exercise.py",
    f'''from checks import run


def test_the_walkthrough():
    """Prints the loss curve, the accuracy and the classes."""
    assert run() == {EXAMPLE_OUT!r}
''',
)

# =====================================================================================
# the way through: the build in steps
# =====================================================================================


def write_step(folder, title, prompt, hints, starter, solution, tests, wrong_name, wrong, typed_in):
    write(
        f"exercises/{folder}/exercise.yaml",
        f'''id: {folder}
stage: fill_in
rev: 1
title: "{title}"
prompt: |
{block(prompt)}hints:
{"".join("  - " + json.dumps(h) + chr(10) for h in hints)}''',
    )
    write(f"exercises/{folder}/starter.py", starter)
    write(f"exercises/{folder}/solution.py", solution)
    write(f"exercises/{folder}/test_exercise.py", tests)
    write(f"exercises/{folder}/wrong/{wrong_name}.py", wrong)
    write(f"exercises/{folder}/wrong/typed-in.py", typed_in)


write_step(
    "step-forward-pass",
    "Step 1: the forward pass",
    f"The first part of the checkpoint is the forward pass. Replace each `...` so `forward` bends the hidden scores with ReLU and adds the output bias, and the program prints the three shapes and the first four probabilities:\n\n```\n{STEP1_OUT}```\n",
    ["ReLU is `np.maximum(z1, 0.0)`.", 'The output bias is `params["b2"]`.'],
    STEP1_STARTER,
    STEP1_SOLUTION,
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints the shapes and the first four probabilities."""
    printed = run()
    assert printed == {STEP1_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_the_bend():
    """A hidden score below zero comes out of the bend as exactly zero."""
    forward = function("forward")
    params = {{"W1": np.array([[1.0, -1.0], [0.0, 0.0]]), "b1": np.zeros(2), "W2": np.ones(2), "b2": np.array(0.0)}}
    z1, h, p = forward(np.array([[2.0, 0.0]]), params)
    assert z1.tolist() == [[2.0, -2.0]] and h.tolist() == [[2.0, 0.0]]
''',
    "no-bend",
    STEP1_SOLUTION.replace("    h = np.maximum(z1, 0.0)\n", "    h = z1\n"),
    PRELUDE + "def forward(X, params):\n    return np.zeros((16, 4)), np.zeros((16, 4)), np.full(16, 0.5)\n\n\n" + "".join(f"print({line!r})\n" for line in STEP1_OUT.splitlines()),
)

write_step(
    "step-loss-and-first-gradient",
    "Step 2: the loss, and the first gradient",
    f"With the forward pass written, the loss is the mean cross-entropy and the backward pass starts from `dz2 = (p - y) / n`. Replace each `...` so the program prints the loss at the starting weights and the first four entries of `dz2`:\n\n```\n{STEP2_OUT}```\n",
    ["A true 0 had probability `1 - p`, so its cost is `-log(1 - p)`.", "`n` is the number of examples, `len(y)`."],
    STEP2_STARTER,
    STEP2_SOLUTION,
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints the loss and the first four entries of dz2."""
    printed = run()
    assert printed == {STEP2_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_known_losses():
    """Guessing a half costs log 2, and a prediction of exactly 1 for a true 0 stays finite."""
    loss = function("loss")
    assert abs(loss(np.full(16, 0.5), np.zeros(16)) - np.log(2)) < 1e-9
    assert np.isfinite(loss(np.array([1.0]), np.array([0.0])))
''',
    "no-mean",
    STEP2_SOLUTION.replace("dz2 = (p - y) / len(y)", "dz2 = p - y"),
    PRELUDE + FORWARD + "\n\ndef loss(p, y):\n    return 0.0\n\n\n" + "".join(f"print({line!r})\n" for line in STEP2_OUT.splitlines()),
)

write_step(
    "step-backward-pass",
    "Step 3: the backward pass",
    f"Now the backward pass, one line per link, returning the gradients as a dict. Replace each `...` so the gradient flows back along `W2` and through ReLU's mask, and the program prints the gradients' shapes and a numeric check of `W1`'s:\n\n```\n{STEP3_OUT}```\n",
    ['`dh` spreads each example\'s `dz2` along the output weights: `np.outer(dz2, params["W2"])`.', "ReLU's derivative is 1 where `z1` was positive: the mask is `z1 > 0`."],
    STEP3_STARTER,
    STEP3_SOLUTION,
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints the shapes and True."""
    printed = run()
    assert printed == {STEP3_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_a_unit_that_is_off():
    """A hidden unit that is off for every example gets a zero gradient."""
    backward = function("backward")
    params = {{"W1": np.zeros((2, 3)), "b1": np.zeros(3), "W2": np.array([0.5, -0.5, 1.0]), "b2": np.array(0.0)}}
    X = np.array([[1.0, 0.0], [0.0, 1.0]])
    z1 = np.array([[1.0, -1.0, 2.0], [0.5, -2.0, 1.0]])
    grads = backward(X, np.array([1.0, 0.0]), params, z1, np.maximum(z1, 0.0), np.array([0.7, 0.4]))
    assert np.abs(grads["W1"][:, 1]).max() == 0 and grads["b1"][1] == 0
    assert np.abs(grads["W1"][:, 0]).max() > 0 and np.abs(grads["W2"]).max() > 0
''',
    "mask-is-h",
    STEP3_SOLUTION.replace("    dz1 = dh * (z1 > 0)\n", "    dz1 = dh * h\n"),
    PRELUDE + FORWARD + "\n\n" + LOSS + "\n\ndef backward(X, y, params, z1, h, p):\n    return {key: np.zeros_like(value) for key, value in params.items()}\n\n\n" + "".join(f"print({line!r})\n" for line in STEP3_OUT.splitlines()),
)

write_step(
    "step-momentum-update",
    "Step 4: the momentum update",
    f"The last piece before the full build: the training loop with a velocity per parameter. Replace each `...` so each step adds the gradient to `beta` times the old velocity and moves the parameter by `rate` times the velocity, and the program prints the loss at the start and after 300 steps, then the output weights:\n\n```\n{STEP4_OUT}```\n",
    ["The velocity keeps `beta` of its old value: `beta * vel[key] + grads[key]`.", "The parameter moves against the velocity: `params[key] - rate * vel[key]`."],
    STEP4_STARTER,
    STEP4_SOLUTION,
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints the two losses and W2."""
    printed = run()
    assert printed == {STEP4_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_two_steps_follow_the_rule():
    """Two steps of train match two heavy-ball steps computed from the program's own backward pass."""
    forward = function("forward")
    backward = function("backward")
    train = function("train")
    g = np.array([-1.5, -0.5, 0.5, 1.5])
    X = np.array([[a, b] for a in g for b in g])
    y = (X[:, 0] ** 2 + X[:, 1] ** 2 < 1).astype(float)

    def fresh():
        return {OTHER_PARAMS}

    expected = fresh()
    vel = {{key: np.zeros_like(value) for key, value in expected.items()}}
    for step in range(2):
        z1, h, p = forward(X, expected)
        grads = backward(X, y, expected, z1, h, p)
        for key in expected:
            vel[key] = 0.9 * vel[key] + grads[key]
            expected[key] = expected[key] - 0.1 * vel[key]
    params = fresh()
    train(X, y, params, 0.1, 0.9, 2)
    for key in params:
        assert np.allclose(params[key], expected[key]), key
''',
    "no-velocity",
    STEP4_PLAIN,
    PRELUDE + FORWARD + "\n\n" + LOSS + "\n\n" + BACKWARD + "\n\ndef train(X, y, params, rate, beta, steps):\n    return [0.0] * steps\n\n\n" + "".join(f"print({line!r})\n" for line in STEP4_OUT.splitlines()),
)

# =====================================================================================
# topic.yaml
# =====================================================================================

write(
    "topic.yaml",
    '''id: ml.m4.checkpoint
kind: checkpoint
status: ready
title: "Checkpoint 4: train a tiny network"
summary: "A two-layer network built from scratch and trained with backpropagation and an optimizer, on a small dataset."
prerequisites: [ml.calc.backpropagation, ml.calc.loss-functions, ml.calc.optimizers]
estimated_minutes: 120
packages: [numpy]
rev: 1
objectives:
  - "Build a two-layer network from scratch, train it with backpropagation and an optimizer, and report its loss and accuracy."
  - "Find and fix three bugs in a training loop: a chain-rule step out of order, an update with the wrong sign, and a shape mistake."
  - "Explain the chain rule as backpropagation, and what the learning rate trades off."
prove:
  build: build-train-a-tiny-network
  debug: debug-training-loop
  explain:
    prompt: |
      Your checkpoint program trained a network from scratch with nothing but NumPy. Explain it to a teammate who has only ever called `loss.backward()` and `optimizer.step()`. In your own words: how is backpropagation the chain rule, line by line, and what does the forward pass keep for it? Why does each layer need only the gradient handed back to it? What does the learning rate trade off, and what did momentum change about the step? And what would you look at first if the loss fell but the accuracy stayed at 0.75?
    rubric:
      - id: chain-rule
        required: true
        description: "The network is a chain of functions; the derivative of the loss with respect to any weight is the product of the local derivatives from the loss back to it, each evaluated at the value the forward pass kept (z1 for ReLU's mask, h for dW2, X for dW1); the backward pass computes those products from the loss inward, so each layer multiplies its own local derivative into the gradient it receives and passes the result on."
      - id: learning-rate
        required: true
        description: "The step is the rate times the gradient (or the velocity): too large overshoots and the loss climbs or bounces, too small crawls; a good rate falls fast and then flattens, and the steps shrink by themselves as the gradient does."
      - id: momentum
        required: true
        description: "Momentum keeps a velocity per parameter, beta times the old velocity plus the gradient, and steps along it; agreeing gradients build speed along a valley and alternating ones cancel across it, which is why it reached the floor in fewer steps."
      - id: diagnosis
        required: false
        description: "Check the gradients numerically, then look at which examples are wrong and whether a hidden unit is dead (off for every example), and whether the loss is at a floor (rate too large or a dead unit) or still falling (more steps)."
    model_answer: |
      The network is a chain: multiply by W1 and add b1, bend with ReLU, multiply by W2 and add b2, squash with the sigmoid, measure the cross-entropy. The chain rule says the derivative of the loss with respect to anything inside is the product of each link's own derivative from the loss back to that point, each one evaluated at the value that link received, which is why the forward pass keeps z1, h and p. The backward pass is that product computed from the loss inward. dz2 is p minus y over n, the loss and the sigmoid together. dW2 is h transposed times dz2, because the output score is h times W2 and a weight's derivative is its input. dh spreads dz2 back along W2. dz1 is dh with ReLU's mask applied, 1 where z1 was positive and 0 where it wasn't. dW1 is X transposed times dz1, the same rule one layer earlier, and the biases are the column sums. Each layer needs only the gradient handed to it from the layer after, because that gradient already contains every link beyond it; the layer multiplies in its own local derivative and passes the result back. That is what loss.backward() does. The learning rate scales each step: too large and the step overshoots the bottom, so the loss climbs or bounces at a floor; too small and it crawls; a good one falls fast and then flattens, and the steps shrink by themselves because the gradient does. Momentum changed the step from the gradient to a velocity, beta times the old velocity plus the new gradient. Along a valley the gradients agree and the velocity builds speed; across it they alternate and cancel; so the same rate reached the floor in fewer steps. If the loss fell but the accuracy sat at 0.75, four of the sixteen points are still wrong. I'd check the gradients numerically first, then look at which four points they are and whether a hidden unit is dead, off for every example, since a dead unit can't move, and whether the loss had reached a floor or was still falling, which would mean more steps or a smaller rate rather than a bug.
# For a learner who's stuck on the build (ADR-0012): a solved sibling, the
# build in steps with hints, then fresh versions.
unstuck:
  example: example-xor-with-momentum
  steps: [step-forward-pass, step-loss-and-first-gradient, step-backward-pass, step-momentum-update]
  versions: [build-train-a-tiny-network-quadrants, build-train-a-tiny-network-band]
''',
)

print("ml.m4.checkpoint written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
