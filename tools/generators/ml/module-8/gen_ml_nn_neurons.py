"""Writes the topic ml.nn.neurons-and-layers (Module 8's first topic). Run from
the repository root under uv (python -m uv run python <this file>), so every
program's expected output is captured from CPython rather than typed in.
Random weights are drawn with a seed and only their shapes and the booleans
computed from them are printed; every printed number comes from hand-set
weights. Files are written as bytes with LF endings."""

import pathlib
import subprocess
import sys

ROOT = pathlib.Path("content/topics/ml.nn.neurons-and-layers")


def write(relative: str, text: str) -> None:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


def out(program: str) -> str:
    result = subprocess.run([sys.executable, "-W", "error", "-c", program], capture_output=True, text=True, check=True)
    return result.stdout.replace("\r\n", "\n")


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


# The three classes the module builds on. Every later topic adds to them.
CLASSES = '''class Dense:
    """A layer of neurons: every output is a weighted sum of every input plus a bias. W is (inputs, outputs)."""

    def __init__(self, n_in, n_out, seed=0):
        rng = np.random.default_rng(seed)
        self.W = rng.standard_normal((n_in, n_out)) / np.sqrt(n_in)
        self.b = np.zeros(n_out)

    def forward(self, X):
        return X @ self.W + self.b

    def parameters(self):
        return [self.W, self.b]


class ReLU:
    """Keeps the positive part of every value and zeroes the rest; it has nothing to learn."""

    def forward(self, X):
        return np.maximum(X, 0.0)

    def parameters(self):
        return []


class Sequential:
    """Layers run one after another; the output of each is the input of the next."""

    def __init__(self, layers):
        self.layers = layers

    def forward(self, X):
        for layer in self.layers:
            X = layer.forward(X)
        return X

    def parameters(self):
        return [p for layer in self.layers for p in layer.parameters()]
'''

# --- the worked example ----------------------------------------------------------------------

EXAMPLE = '''import numpy as np

x = np.array([1.0, 2.0])
w = np.array([0.5, -0.25])
b = 0.1
z = x @ w + b
print("one neuron: z = 0.5 * 1 + -0.25 * 2 + 0.1 =", round(float(z), 2), "| relu(z) =", round(float(max(z, 0.0)), 2))

W = np.array([[0.5, -1.0, 0.2], [-0.25, 0.5, 0.4]])
b3 = np.array([0.1, -0.3, -0.5])
print("a layer of 3 neurons on one input: z =", np.round(x @ W + b3, 2).tolist(), "| relu:", np.maximum(x @ W + b3, 0.0).round(2).tolist())
X = np.array([[1.0, 2.0], [0.0, 0.0], [-1.0, 1.0], [2.0, -2.0]])
print("the same layer on a batch of 4 rows:", (X @ W + b3).shape, "| row 0 is the single input's answer:", np.round((X @ W + b3)[0], 2).tolist())


''' + CLASSES + '''

net = Sequential([Dense(35, 16, seed=1), ReLU(), Dense(16, 10, seed=2)])
batch = np.random.default_rng(0).standard_normal((8, 35))
h = batch
trace = [f"input {h.shape}"]
for layer in net.layers:
    h = layer.forward(h)
    trace.append(f"{type(layer).__name__} -> {h.shape}")
print(" | ".join(trace))
print("parameters:", sum(p.size for p in net.parameters()), "= 35 * 16 + 16 + 16 * 10 + 10")

first, second = Dense(35, 16, seed=1), Dense(16, 10, seed=2)
merged = Dense(35, 10)
merged.W, merged.b = first.W @ second.W, first.b @ second.W + second.b
print("two Dense layers with nothing between equal one Dense:", np.allclose(second.forward(first.forward(batch)), merged.forward(batch)), "| with a ReLU between:", np.allclose(net.forward(batch), merged.forward(batch)))

points = np.array([[0.0, 0.0], [2.0, 0.0], [0.0, 2.0], [2.0, 2.0], [-1.0, -1.0]])
print("a neuron with w = [1, 1] and b = -1.5 fires where x + y > 1.5:", (points @ np.array([1.0, 1.0]) - 1.5 > 0).tolist())
'''
EXAMPLE_OUT = out(EXAMPLE)
print("example:\n" + EXAMPLE_OUT)
EX = EXAMPLE_OUT.splitlines()
assert len(EX) == 7, EX
assert EX[0] == "one neuron: z = 0.5 * 1 + -0.25 * 2 + 0.1 = 0.1 | relu(z) = 0.1", EX[0]
assert EX[1] == "a layer of 3 neurons on one input: z = [0.1, -0.3, 0.5] | relu: [0.1, 0.0, 0.5]", EX[1]
assert EX[2] == "the same layer on a batch of 4 rows: (4, 3) | row 0 is the single input's answer: [0.1, -0.3, 0.5]", EX[2]
assert EX[3] == "input (8, 35) | Dense -> (8, 16) | ReLU -> (8, 16) | Dense -> (8, 10)", EX[3]
assert EX[4] == "parameters: 746 = 35 * 16 + 16 + 16 * 10 + 10", EX[4]
assert EX[5] == "two Dense layers with nothing between equal one Dense: True | with a ReLU between: False", EX[5]
assert EX[6] == "a neuron with w = [1, 1] and b = -1.5 fires where x + y > 1.5: [False, True, True, True, False]", EX[6]
EXAMPLE_LINES = EXAMPLE.splitlines()


def ln(text: str, after: int = 0) -> int:
    return next(i + 1 for i, line in enumerate(EXAMPLE_LINES) if i + 1 > after and text in line)


# --- recall programs ----------------------------------------------------------------------------

PREDICT_NEURON = '''import numpy as np

w = np.array([0.5, 1.0])
b = 0.25
for x in (np.array([2.0, -1.0]), np.array([-2.0, 0.5]), np.array([0.0, 0.0])):
    z = x @ w + b
    print(round(float(z), 2), round(float(max(z, 0.0)), 2))
'''
PREDICT_NEURON_OUT = out(PREDICT_NEURON)
assert PREDICT_NEURON_OUT == "0.25 0.25\n-0.25 0.0\n0.25 0.25\n", PREDICT_NEURON_OUT

PREDICT_SHAPES = '''import numpy as np

X = np.ones((6, 4))
W1, b1 = np.full((4, 8), 0.1), np.zeros(8)
W2, b2 = np.full((8, 2), 0.5), np.ones(2)
h = np.maximum(X @ W1 + b1, 0.0)
out = h @ W2 + b2
print(h.shape, out.shape, np.round(out[0], 2).tolist())
print([p.shape for p in (W1, b1, W2, b2)], sum(p.size for p in (W1, b1, W2, b2)))
'''
PREDICT_SHAPES_OUT = out(PREDICT_SHAPES)
assert PREDICT_SHAPES_OUT == "(6, 8) (6, 2) [2.6, 2.6]\n[(4, 8), (8,), (8, 2), (2,)] 58\n", PREDICT_SHAPES_OUT

REVIEW_LAYER = '''import numpy as np

W = np.array([[1.0, -1.0], [0.0, 2.0], [0.5, 0.5]])
b = np.array([-0.5, 0.0])
X = np.array([[1.0, 1.0, 1.0], [2.0, 0.0, -2.0]])
z = X @ W + b
print(z.tolist())
print(np.maximum(z, 0.0).tolist(), z.shape)
'''
REVIEW_LAYER_OUT = out(REVIEW_LAYER)
assert REVIEW_LAYER_OUT == "[[1.0, 1.5], [0.5, -3.0]]\n[[1.0, 1.5], [0.5, 0.0]] (2, 2)\n", REVIEW_LAYER_OUT

PARSONS_LINES = [
    "import numpy as np",
    "X = np.ones((4, 5))",
    "h = np.maximum(X @ np.full((5, 3), 0.2) + 0.1, 0.0)",
    "out = h @ np.full((3, 2), -0.5) + 1.0",
    "print(out.shape, np.round(out[0], 2).tolist())",
]
PARSONS_OUT = out("\n".join(PARSONS_LINES) + "\n")
assert PARSONS_OUT == "(4, 2) [-0.65, -0.65]\n", PARSONS_OUT

# --- the fill-in --------------------------------------------------------------------------------

FILL_SOLUTION = '''import numpy as np


class Dense:
    """A layer of neurons: W holds one column of weights per output neuron, b one bias each."""

    def __init__(self, W, b):
        self.W = W
        self.b = b

    def forward(self, X):
        return X @ self.W + self.b

    def parameters(self):
        return [self.W, self.b]


layer = Dense(np.array([[0.5, -1.0, 0.2], [-0.25, 0.5, 0.4]]), np.array([0.1, -0.3, -0.5]))
X = np.array([[1.0, 2.0], [0.0, 0.0], [-1.0, 1.0]])
print(np.round(layer.forward(X), 2).tolist())
print([p.shape for p in layer.parameters()], sum(p.size for p in layer.parameters()))
'''
FILL_STARTER = FILL_SOLUTION.replace("        return X @ self.W + self.b", "        return X @ ... + ...").replace("        return [self.W, self.b]", "        return [..., ...]")
FILL_WRONG = FILL_SOLUTION.replace("        return X @ self.W + self.b", "        return X @ self.W")
FILL_OUT = out(FILL_SOLUTION)
assert FILL_OUT == "[[0.1, -0.3, 0.5], [0.1, -0.3, -0.5], [-0.65, 1.2, -0.3]]\n[(2, 3), (3,)] 9\n", FILL_OUT
assert out(FILL_WRONG) != FILL_OUT

# --- the write ----------------------------------------------------------------------------------

WRITE_HEAD = '''import numpy as np


class Dense:
    def __init__(self, n_in, n_out, seed=0):
        rng = np.random.default_rng(seed)
        self.W = rng.standard_normal((n_in, n_out)) / np.sqrt(n_in)
        self.b = np.zeros(n_out)

    def forward(self, X):
        return X @ self.W + self.b

    def parameters(self):
        return [self.W, self.b]


class ReLU:
    def forward(self, X):
        return np.maximum(X, 0.0)

    def parameters(self):
        return []
'''
WRITE_SEQUENTIAL = '''

class Sequential:
    """Layers run one after another; the output of each is the input of the next."""

    def __init__(self, layers):
        self.layers = layers

    def forward(self, X):
        for layer in self.layers:
            X = layer.forward(X)
        return X

    def parameters(self):
        return [p for layer in self.layers for p in layer.parameters()]
'''
WRITE_TAIL = '''

net = Sequential([Dense(4, 8, seed=1), ReLU(), Dense(8, 2, seed=2)])
X = np.ones((6, 4))
print(net.forward(X).shape, [p.shape for p in net.parameters()], sum(p.size for p in net.parameters()))
by_hand = net.layers[2].forward(net.layers[1].forward(net.layers[0].forward(X)))
print(np.allclose(net.forward(X), by_hand))
'''
WRITE_SOLUTION = WRITE_HEAD + WRITE_SEQUENTIAL + WRITE_TAIL
WRITE_STARTER = WRITE_HEAD + WRITE_TAIL
WRITE_OUT = out(WRITE_SOLUTION)
assert WRITE_OUT == "(6, 2) [(4, 8), (8,), (8, 2), (2,)] 58\nTrue\n", WRITE_OUT
WRITE_SKIPS_LAST = WRITE_SOLUTION.replace("        for layer in self.layers:\n            X = layer.forward(X)\n        return X", "        for layer in self.layers[:-1]:\n            X = layer.forward(X)\n        return X")
WRITE_FIRST_ONLY = WRITE_SOLUTION.replace("        return [p for layer in self.layers for p in layer.parameters()]", "        return self.layers[0].parameters()")
def differs(program: str, expected: str) -> bool:
    """True if the program fails or prints something other than expected: what a known-wrong must do."""
    result = subprocess.run([sys.executable, "-W", "error", "-c", program], capture_output=True, text=True)
    return result.returncode != 0 or result.stdout.replace("\r\n", "\n") != expected


assert differs(WRITE_SKIPS_LAST, WRITE_OUT) and differs(WRITE_FIRST_ONLY, WRITE_OUT)

# --- the build ----------------------------------------------------------------------------------

BUILD_SOLUTION = "import numpy as np\n\n\n" + CLASSES + '''

def count_parameters(net):
    """How many numbers the network can learn."""
    return sum(p.size for p in net.parameters())


def shapes_through(net, X):
    """The shape of the batch after each layer, in order."""
    shapes = []
    for layer in net.layers:
        X = layer.forward(X)
        shapes.append(X.shape)
    return shapes


net = Sequential([Dense(35, 16, seed=1), ReLU(), Dense(16, 10, seed=2)])
X = np.random.default_rng(0).standard_normal((8, 35))
print(shapes_through(net, X), count_parameters(net))
hand = Dense(2, 3)
hand.W, hand.b = np.array([[0.5, -1.0, 0.2], [-0.25, 0.5, 0.4]]), np.array([0.1, -0.3, -0.5])
tiny = Sequential([hand, ReLU()])
print(np.round(tiny.forward(np.array([[1.0, 2.0], [-1.0, 1.0]])), 2).tolist())
first, second = Dense(35, 16, seed=1), Dense(16, 10, seed=2)
merged = Dense(35, 10)
merged.W, merged.b = first.W @ second.W, first.b @ second.W + second.b
print(np.allclose(Sequential([first, second]).forward(X), merged.forward(X)), np.allclose(net.forward(X), merged.forward(X)))
'''
BUILD_OUT = out(BUILD_SOLUTION)
print("build:\n" + BUILD_OUT)
assert BUILD_OUT == "[(8, 16), (8, 16), (8, 10)] 746\n[[0.1, 0.0, 0.5], [0.0, 1.2, 0.0]]\nTrue False\n", BUILD_OUT
BUILD_NO_BIAS = BUILD_SOLUTION.replace("        return X @ self.W + self.b\n", "        return X @ self.W\n")
BUILD_RELU_KEEPS_NEGATIVES = BUILD_SOLUTION.replace("        return np.maximum(X, 0.0)\n", "        return np.minimum(X, 0.0)\n")
BUILD_COUNTS_LAYERS = BUILD_SOLUTION.replace("    return sum(p.size for p in net.parameters())", "    return len(net.parameters())")
for wrong in (BUILD_NO_BIAS, BUILD_RELU_KEEPS_NEGATIVES, BUILD_COUNTS_LAYERS):
    assert wrong != BUILD_SOLUTION and out(wrong) != BUILD_OUT

# --- the debug ----------------------------------------------------------------------------------

DEBUG_SOLUTION = '''import numpy as np


class Dense:
    """W is (inputs, outputs), so a batch of shape (rows, inputs) times W is (rows, outputs)."""

    def __init__(self, n_in, n_out, seed=0):
        rng = np.random.default_rng(seed)
        self.W = rng.standard_normal((n_in, n_out)) / np.sqrt(n_in)
        self.b = np.zeros(n_out)

    def forward(self, X):
        return X @ self.W + self.b


class ReLU:
    """Zero below zero, unchanged above."""

    def forward(self, X):
        return np.maximum(X, 0.0)


class Sequential:
    def __init__(self, layers):
        self.layers = layers

    def forward(self, X):
        for layer in self.layers:
            X = layer.forward(X)
        return X


net = Sequential([Dense(3, 4, seed=1), ReLU(), Dense(4, 2, seed=2)])
X = np.array([[1.0, -2.0, 0.5], [0.0, 1.0, 1.0]])
print("output shape:", net.forward(X).shape)
hidden = net.layers[1].forward(net.layers[0].forward(X))
print("hidden values are never negative:", bool((hidden >= 0).all()), "| some are zero:", bool((hidden == 0).any()))
'''
BUG_TRANSPOSED = ("        self.W = rng.standard_normal((n_in, n_out)) / np.sqrt(n_in)", "        self.W = rng.standard_normal((n_out, n_in)) / np.sqrt(n_in)")
BUG_MINIMUM = ("        return np.maximum(X, 0.0)", "        return np.minimum(X, 0.0)")
DEBUG_STARTER = DEBUG_SOLUTION.replace(*BUG_TRANSPOSED).replace(*BUG_MINIMUM)
DEBUG_STILL_TRANSPOSED = DEBUG_SOLUTION.replace(*BUG_TRANSPOSED)
DEBUG_STILL_MINIMUM = DEBUG_SOLUTION.replace(*BUG_MINIMUM)
DEBUG_OUT = out(DEBUG_SOLUTION)
print("debug:\n" + DEBUG_OUT)
assert DEBUG_OUT == "output shape: (2, 2)\nhidden values are never negative: True | some are zero: True\n", DEBUG_OUT
assert "ValueError" in fails(DEBUG_STARTER)
assert out(DEBUG_STILL_MINIMUM).splitlines()[1] == "hidden values are never negative: False | some are zero: True"

REVIEW_CODE_SOLUTION = WRITE_HEAD + WRITE_SEQUENTIAL + '''

net = Sequential([Dense(3, 5, seed=3), ReLU(), Dense(5, 1, seed=4)])
print(net.forward(np.zeros((7, 3))).shape, sum(p.size for p in net.parameters()))
'''
REVIEW_CODE_OUT = out(REVIEW_CODE_SOLUTION)
assert REVIEW_CODE_OUT == "(7, 1) 26\n", REVIEW_CODE_OUT
REVIEW_CODE_WRONG = REVIEW_CODE_SOLUTION.replace("        return [p for layer in self.layers for p in layer.parameters()]", "        return self.layers[0].parameters()")
assert out(REVIEW_CODE_WRONG) != REVIEW_CODE_OUT

# =====================================================================================
# topic.yaml
# =====================================================================================

write(
    "topic.yaml",
    '''id: ml.nn.neurons-and-layers
kind: topic
status: ready
title: "Neurons, layers and a network's shape"
summary: "A neuron as a weighted sum through an activation, a layer as a matrix multiply plus a bias, a network as layers in a list: the forward pass written as objects, the shape of the data at every step, and the parameter count that falls out of the layer sizes."
prerequisites: [ml.m4.checkpoint, ml.m7.checkpoint]
packages: [numpy]
estimated_minutes: 50
rev: 1
objectives:
  - "Write a neuron and a dense layer as a weighted sum plus a bias through an activation, and say what each weight means."
  - "Compose layers into a network object with a forward pass, and track the shape of a batch through it."
  - "Count a network's parameters from its layer sizes."
  - "Explain why a network with no activation between its layers is one linear layer in disguise."
# Linked, never copied or embedded: 3Blue1Brown's videos are under the
# standard YouTube licence; Nielsen's book is CC BY-NC 3.0; Wikipedia is
# CC BY-SA 4.0.
resources:
  - title: "3Blue1Brown: Neural networks (Grant Sanderson), chapter 1: But what is a neural network?"
    url: https://www.3blue1brown.com/lessons/neural-networks
    type: video
    use: link
    license: Standard YouTube licence (linked, not copied)
  - title: "Neural Networks and Deep Learning, chapter 1: Using neural nets to recognize handwritten digits (Michael Nielsen), the sections on perceptrons, sigmoid neurons and the architecture of neural networks"
    url: https://neuralnetworksanddeeplearning.com/chap1.html
    type: reading
    use: link
    license: CC BY-NC 3.0 (linked, not copied)
  - title: "Wikipedia: Multilayer perceptron (the layers, the activation function and why it is needed)"
    url: https://en.wikipedia.org/wiki/Multilayer_perceptron
    type: reading
    use: link
    license: CC BY-SA 4.0 (linked, not copied)
practice:
  - example-a-network-as-objects
  - predict-one-neuron
  - mcq-what-a-weight-means
  - predict-shapes-and-counts
  - mcq-the-shape-rule
  - parsons-a-forward-pass
  - mcq-why-no-activation-collapses
  - fill-dense-layer
  - write-sequential
prove:
  build: build-a-network-of-objects
  debug: debug-a-network-that-will-not-run
  explain:
    prompt: |
      A teammate is reading your network code for the first time and asks four things. "What does one number in `W` mean, and what is `b` for?" "Why is the network `Dense, ReLU, Dense` and not just `Dense, Dense`, which would be simpler?" "A batch of 32 images of 784 pixels goes into `[784, 128, 10]`: what shape is it after each layer, and how many numbers does the network learn?" "What does one hidden neuron actually do to an input?" In your own words, answer all four.
    rubric:
      - id: neuron
        required: true
        description: "W[j, k] is how much input j pushes output k, per unit of input; b[k] shifts output k's starting point, the threshold a ReLU neuron has to clear. A neuron computes a weighted sum plus its bias and passes it through the activation; before the activation its sum is zero along a line (a plane) in input space, positive on one side and negative on the other; after the ReLU the neuron is zero on one side of it."
      - id: compose
        required: true
        description: "A batch of (32, 784) times W1 (784, 128) plus b1 is (32, 128); ReLU keeps the shape; times W2 (128, 10) plus b2 is (32, 10): rows are examples throughout, and each layer's input width must equal the previous layer's output width. Sequential runs the layers in order and gathers their parameters."
      - id: count
        required: true
        description: "in times out plus out per dense layer: 784 times 128 plus 128, plus 128 times 10 plus 10, is 101,770 parameters."
      - id: nonlinearity
        required: true
        description: "Two Dense layers with nothing between are one Dense layer: W1 W2 and b1 W2 + b2 give exactly the same outputs, so the depth buys nothing. ReLU bends the function between the layers, and a stack of bends can fit curves and corners a line can't; that is what the hidden layer is for."
    model_answer: |
      One number in `W`, say `W[j, k]`, is how much input `j` pushes output neuron `k`, for every unit of that input: a positive weight makes a bigger input raise the neuron's sum, a negative one lowers it, and zero means the neuron ignores that input. `b[k]` is the bias of neuron `k`, the value its sum starts from before any input is counted; for a ReLU neuron it sets the threshold the weighted inputs have to clear before the neuron gives anything but zero. A neuron is just that: the weighted sum of its inputs plus its bias, passed through the activation function. The network is `Dense, ReLU, Dense` because `Dense, Dense` would be one layer wearing two coats. A dense layer is a matrix multiply plus a bias, which is a linear function, and a linear function of a linear function is linear: multiplying out, two layers with weights `W1` and `W2` are one layer with weights `W1 @ W2` and bias `b1 @ W2 + b2`, and the example checked that they give exactly the same outputs. The ReLU between them bends the function, zeroing each hidden neuron on one side of its line, and a stack of such bends can fit curves and corners that no single line can; the hidden layer only earns its keep because of the activation. For the shapes: rows are examples all the way through. The batch is `(32, 784)`; times `W1`, which is `(784, 128)`, plus `b1` broadcast across the rows, it is `(32, 128)`; the ReLU doesn't change the shape; times `W2`, which is `(128, 10)`, plus `b2`, it is `(32, 10)`, one score per class per image. The rule is that each layer's input width must equal the previous layer's output width, and the usual bug is a `W` built the wrong way round, which fails loudly with a shape error. The network learns `784 * 128 + 128` numbers in the first layer and `128 * 10 + 10` in the second, 101,770 in all; the activation has nothing to learn. One hidden neuron takes the whole input, multiplies each pixel by its own weight, adds them up with its bias, and keeps the result if it is positive. Before the activation that is a weighted vote over the pixels, which is zero along a flat boundary in the 784-dimensional input space; after it, the neuron is silent on one side of that boundary and grows linearly on the other, so each hidden neuron is a detector for one direction in the input, and the next layer combines a hundred and twenty-eight such detectors.
review_pool:
  - review-predict-a-layer-by-hand
  - review-mcq-parameter-count
  - review-mcq-what-relu-adds
  - review-sequential
# What this topic teaches. Each question names the skills it tests, so a
# missed question can come back as a different one on the same skill
# (ADR-0011).
skills:
  - id: neuron
    description: "Write a neuron and a dense layer, and say what each weight and bias means"
  - id: compose
    description: "Compose layers into a network with a forward pass, and track the shape of a batch through it"
  - id: count
    description: "Count a network's parameters from its layer sizes"
  - id: nonlinearity
    description: "Explain why a network with no activation between its layers is one linear layer in disguise"
''',
)

# =====================================================================================
# lesson.mdx
# =====================================================================================

write(
    "lesson.mdx",
    '''<Intro>

Module 4 built a two-layer network as four arrays and three functions, to learn the calculus. This module builds networks the way libraries do: as **layers**, each an object that knows its own weights and its own forward pass, stacked in a list. This first topic is the forward direction only: what a single neuron computes, how a layer of them is one matrix multiply, how a batch flows through a stack of layers and what shape it has at every step, how many numbers the network can learn, and why the activation function between the layers is the whole point of having more than one. The backward pass comes in the next topic, Layers that carry their gradient.

The main resource is **3Blue1Brown's first neural-network video**, _But what is a neural network?_, which draws a layer of neurons reading a digit and shows the weights as a picture; about 20 minutes. Nielsen's first chapter covers the same ground in prose, from perceptrons to the architecture of a network, and Wikipedia's _Multilayer perceptron_ page is the reference for the names. Watch for:

- **A neuron as a weighted sum**: every weight is a vote on one input.
- **Layers as matrices**: why a whole layer is one multiplication.
- **The activation function**: what it adds, and what a network without one can't do.

</Intro>

<Resource index={0} />

<Recap>

- **A neuron** takes an input vector `x`, computes `z = x @ w + b` (a **weighted sum**: each input times its own weight, plus a **bias**), and passes `z` through an **activation function** such as ReLU, `max(z, 0)`. `w[j]` is how much input `j` pushes the neuron up or down per unit; `b` is where the sum starts, the threshold a ReLU neuron must clear. Before the activation, `z = 0` is a straight line (in more dimensions, a flat boundary) through the input space: the neuron with `w = [1, 1]` and `b = -1.5` fires where `x + y > 1.5` and is silent elsewhere.
- **A layer** is many neurons on the same input, and their weights stack into a matrix: `W` has shape `(inputs, outputs)`, one **column per neuron**, and `b` has one entry per neuron. `x @ W + b` computes every neuron at once; on a **batch** `X` of shape `(rows, inputs)`, `X @ W + b` is `(rows, outputs)`, every example through every neuron in one operation, with `b` broadcast across the rows (Why vectorized code is fast). Rows are examples, always.
- **The shape rule.** A layer's input width must equal the previous layer's output width: `(32, 784) @ (784, 128)` is `(32, 128)`; an activation keeps the shape; `(32, 128) @ (128, 10)` is `(32, 10)`. A `W` built the wrong way round fails loudly (`matmul: ... mismatch in its core dimension`), which is the most common bug in a new network and the easiest to fix: print the shapes after every layer.
- **Layers as objects.** `Dense(n_in, n_out)` owns `W` and `b` and has `forward(X)` and `parameters()`; `ReLU` has a `forward` and no parameters; `Sequential(layers)` runs them in order and gathers every parameter into one list. The point of the design: each piece can be tested alone, swapped, or given a `backward` (next topic) without touching the others. Weights start random, scaled by `1 / sqrt(n_in)`, and biases at zero; Starting weights and activation functions says why.
- **Parameter count:** `in * out + out` per dense layer, nothing for activations. `[35, 16, 10]` is 35 × 16 + 16 + 16 × 10 + 10 = 746; `[784, 128, 10]` is 101,770. It is the number of knobs the network can turn, and Counting a model's cost turned it into FLOPs and bytes.
- **Why the activation is the point.** Two dense layers with nothing between them are one dense layer in disguise: `(X @ W1 + b1) @ W2 + b2` is `X @ (W1 @ W2) + (b1 @ W2 + b2)`, and the example checks that the two give the same outputs, to within rounding. A linear function of a linear function is linear, so depth without an activation buys nothing. ReLU bends the function at each hidden neuron's boundary; a stack of bends can fit curves, corners and the XOR pattern of Checkpoint 4 that no single line can. Sigmoid and tanh (`np.tanh`, an S-curve from -1 to 1: a sigmoid centred on zero) bend it smoothly instead, with costs the initialization topic measures.
- **In machine learning** (names you'll meet later): `nn.Linear` is `Dense` (PyTorch stores `W` as `(out, in)` and multiplies by its transpose; the arithmetic is the same), `nn.Sequential` is `Sequential`, `model.parameters()` is the list the optimizer updates, and `model(x)` calls `forward`; a **multilayer perceptron** (MLP) is exactly this stack of dense layers and activations, and "hidden units" are the columns of a hidden layer's `W`.

</Recap>
''',
)

# =====================================================================================
# recall
# =====================================================================================

write(
    "recall/predict-one-neuron.yaml",
    f'''id: predict-one-neuron
type: predict_output
rev: 1
prompt: |
  One neuron with weights `[0.5, 1.0]` and bias `0.25`, on three inputs: its weighted sum and its ReLU output. What does the program print?
code: |
{block(PREDICT_NEURON)}expected_output: |
{block(PREDICT_NEURON_OUT)}explanation: |
  The sum is `0.5 * x0 + 1.0 * x1 + 0.25`: for `[2, -1]` that is 1 minus 1 plus 0.25; for `[-2, 0.5]` it is minus 1 plus 0.5 plus 0.25, which is negative, so the ReLU gives 0; for the zero input only the bias is left. The bias is what the neuron outputs when every input is zero.
skills: [neuron]
''',
)

mcq(
    "mcq-what-a-weight-means",
    "In a dense layer with `W` of shape `(inputs, outputs)`, what do `W[j, k]` and `b[k]` mean?",
    [
        "`W[j, k]` is the probability that input `j` belongs to class `k`, and `b[k]` is the class's prior probability before any input is seen",
        "`W[j, k]` is the distance between input `j` and output `k`, and `b[k]` is the layer's learning rate",
        "`W[j, k]` is how much input `j` pushes output `k` per unit of input; `b[k]` is where neuron `k`'s sum starts",
        "`W[j, k]` is the number of times input `j` is used by output `k`, and `b[k]` is the number of inputs",
    ],
    2,
    "Output `k` is `sum over j of x[j] * W[j, k]`, plus `b[k]`: each weight is a vote by one input on one neuron, scaled by the input's value, and the bias is the sum's starting point, which for a ReLU neuron sets the threshold the inputs have to clear. Weights are not probabilities, distances or counts, and the learning rate belongs to the optimizer, not the layer.",
    ["neuron"],
)

write(
    "recall/predict-shapes-and-counts.yaml",
    f'''id: predict-shapes-and-counts
type: predict_output
rev: 1
prompt: |
  A batch of six rows of ones through a `[4, 8, 2]` network whose weights are all 0.1 and then all 0.5, with a ReLU between: the shapes, the first output row, the parameter shapes and their total. What does the program print?
code: |
{block(PREDICT_SHAPES)}expected_output: |
{block(PREDICT_SHAPES_OUT)}explanation: |
  `(6, 4) @ (4, 8)` is `(6, 8)`: each hidden value is four inputs of 1 times 0.1, which is 0.4, and the ReLU keeps it. `(6, 8) @ (8, 2)` is `(6, 2)`: eight values of 0.4 times 0.5 is 1.6, plus the bias of 1, which is 2.6. The parameters are the two weight matrices and the two bias vectors, 32 + 8 + 16 + 2 = 58 numbers. (The first output is printed rounded: eight products of 0.4 and 0.5 add up to 1.6 only to within a last digit.)
skills: [compose, count]
''',
)

mcq(
    "mcq-the-shape-rule",
    "A batch `X` has shape `(32, 784)`. Which `W1` and `W2` make `relu(X @ W1 + b1) @ W2 + b2` a `(32, 10)` output, and why does the other way round fail?",
    [
        "`W1` of shape `(128, 784)` and `W2` of shape `(10, 128)`: the output size always comes first in a weight matrix, and NumPy transposes it for you when the batch arrives",
        "`W1` of shape `(32, 128)` and `W2` of shape `(32, 10)`: the batch size must appear in every weight matrix",
        "Any shapes with the right number of elements: NumPy reshapes the weights to fit the batch",
        "`W1` of shape `(784, 128)` and `W2` of shape `(128, 10)`: each layer's input width must equal the previous output width, and `(128, 784)` would put 128 against 784",
    ],
    3,
    "Matrix multiplication needs the inner sizes to agree: `(32, 784) @ (784, 128)` is `(32, 128)`, and then `(32, 128) @ (128, 10)` is `(32, 10)`. The batch size never appears in the weights, which is what lets the same network run on a batch of 1 or of 10,000, and NumPy never reshapes silently; a wrong width is a loud `matmul` error. Libraries that store weights as `(out, in)` multiply by the transpose, the same arithmetic.",
    ["compose"],
)

write(
    "recall/parsons-a-forward-pass.yaml",
    "id: parsons-a-forward-pass\ntype: parsons\nrev: 1\nprompt: |\n"
    + block("Put the lines in order to run a batch of four rows of ones through a two-layer network written as plain arrays (weights 0.2 and bias 0.1 in the first layer, weights -0.5 and bias 1.0 in the second, a ReLU between) and print `(4, 2) [-0.65, -0.65]`. One line is a decoy that doesn't belong.")
    + "lines:\n"
    + "".join(f"  - {quoted(line)}\n" for line in PARSONS_LINES)
    + "distractors:\n  - "
    + quoted("h = np.maximum(X @ np.full((3, 5), 0.2) + 0.1, 0.0)")
    + "\nexplanation: |\n"
    + block("The first layer's weights must be `(5, 3)` to meet a batch of width 5; each hidden value is five inputs times 0.2 plus 0.1, which is 1.1, kept by the ReLU; the second layer sums three of those times -0.5 and adds 1, which is -0.65. The decoy builds the first weights as `(3, 5)`, which can't multiply a `(4, 5)` batch.")
    + "skills: [compose]\n",
)

mcq(
    "mcq-why-no-activation-collapses",
    "Why does a network of two dense layers with nothing between them learn no more than a single dense layer?",
    [
        "Because the second layer overwrites the first layer's weights during training",
        "Because without an activation the gradients are zero and nothing trains",
        "Because `(X @ W1 + b1) @ W2 + b2` is `X @ (W1 @ W2) + (b1 @ W2 + b2)`: a linear function of a linear function is linear",
        "Because two layers have more parameters than the data can support, so they overfit before they can learn anything the first layer alone couldn't",
    ],
    2,
    "Multiply out the two layers and one matrix and one bias appear; the worked example checks that the stacked pair and the merged layer give the same outputs, to within rounding. The pair has more numbers but can express exactly the same functions, all of them linear. The activation is what breaks this: ReLU between the layers bends the function, and then the composition can do what one layer can't. Gradients don't vanish without an activation; they just lead to a linear fit.",
    ["nonlinearity"],
)

write(
    "recall/review-predict-a-layer-by-hand.yaml",
    f'''id: review-predict-a-layer-by-hand
type: predict_output
rev: 1
prompt: |
  A dense layer with two neurons on three inputs, on a batch of two rows, before and after a ReLU. What does the program print?
code: |
{block(REVIEW_LAYER)}expected_output: |
{block(REVIEW_LAYER_OUT)}explanation: |
  Each output is a column of `W` dotted with the row, plus that neuron's bias: for the first row, 1 + 0 + 0.5 - 0.5 and -1 + 2 + 0.5; for the second, 2 + 0 - 1 - 0.5 and -2 + 0 - 1. The ReLU zeroes the one negative value. Two rows and two neurons make a `(2, 2)` result.
skills: [neuron]
''',
)

mcq(
    "review-mcq-parameter-count",
    "How many parameters does the network `[784, 256, 128, 10]` (three dense layers with activations between) learn?",
    [
        "784 + 256 + 128 + 10 = 1,178, one per neuron",
        "784 × 256 × 128 × 10, since every path through the network has its own weight",
        "784 × 256 + 256 + 256 × 128 + 128 + 128 × 10 + 10 = 235,146: a weight per input-output pair and a bias per output",
        "784 × 256 + 256 × 128 + 128 × 10 = 234,752, since biases are not trained and so are not counted among the parameters",
    ],
    2,
    "Each dense layer has one weight for every pair of an input and an output, `in * out`, plus a bias for every output; activations have nothing to learn. The three layers give 200,960 + 32,896 + 1,290. Biases are trained like any other parameter, and the count grows with products of neighbouring widths, not with the product of all of them.",
    ["count"],
)

mcq(
    "review-mcq-what-relu-adds",
    "A hidden neuron computes `relu(x @ w + b)`. What does the ReLU add that the weighted sum alone doesn't?",
    [
        "It scales the sum into the range 0 to 1, so the neuron's output can be read as a probability and compared with the outputs of the other neurons in the layer",
        "It speeds up the matrix multiply by skipping the zeros",
        "It normalizes the sum by the number of inputs, so wide layers don't dominate",
        "It silences the neuron on one side of the boundary `x @ w + b = 0` and leaves it linear on the other: a bend that layers can combine into curves",
    ],
    3,
    "The weighted sum is a flat function of the input, positive on one side of a boundary and negative on the other. ReLU replaces the negative side with zero: the neuron becomes a one-sided detector, and a layer of such detectors feeding another layer can represent functions with bends wherever the boundaries lie. That is why depth with activations can fit what a single line can't. ReLU's output isn't bounded or normalized, and it does no arithmetic on the multiply.",
    ["nonlinearity"],
)

# =====================================================================================
# exercises
# =====================================================================================

write(
    "exercises/example-a-network-as-objects/exercise.yaml",
    f'''id: example-a-network-as-objects
stage: worked_example
rev: 1
title: "A network as objects"
prompt: |
  One neuron by hand, a layer of three on one input and on a batch, then the module's three classes (`Dense`, `ReLU`, `Sequential`) with a batch traced through them, the parameter count, two dense layers collapsing into one, and what one neuron's boundary looks like. Press **Run**, then read how each part works.
steps:
  - label: "One neuron"
    lines: "{ln('x = np.array([1.0, 2.0])')}-{ln('one neuron: z =')}"
    note: "A neuron is a weighted sum plus a bias, `x @ w + b`, through an activation. Here the first input pushes the sum up by 0.5 per unit and the second down by 0.25 per unit; the bias starts it at 0.1. The sum is 0.1, positive, so the ReLU passes it through."
  - label: "A layer, on one input and on a batch"
    lines: "{ln('W = np.array([[0.5, -1.0, 0.2]')}-{ln('the same layer on a batch')}"
    note: "Three neurons on the same input stack their weights as the three columns of `W`, with a bias each, so `x @ W + b` is all three sums at once; the ReLU zeroes the negative one. A batch of four rows goes through the same layer as `X @ W + b`, `(4, 2) @ (2, 3)` giving `(4, 3)`, with the bias broadcast across the rows; row 0 is the single input's answer again."
  - label: "The three classes"
    lines: "{ln('class Dense:')}-{ln('return [p for layer in self.layers')}"
    note: "`Dense` owns its `W` (shape `(inputs, outputs)`, started random and scaled by `1 / sqrt(inputs)`, which the initialization topic explains) and its `b` (zeros); `forward` is the matrix multiply plus the bias, and `parameters` hands them out. `ReLU` has a `forward` and nothing to learn. `Sequential` runs its layers in order and gathers every parameter into one list. Each piece can be tested and replaced alone."
  - label: "Shapes and the parameter count"
    lines: "{ln('net = Sequential([Dense(35, 16, seed=1)')}-{ln('parameters:')}"
    note: "A batch of 8 rows of 35 features is `(8, 35)`; after the first dense layer it is `(8, 16)`; the ReLU keeps the shape; the last layer makes it `(8, 10)`, a score per class per row. The parameters are `35 * 16 + 16` in the first layer and `16 * 10 + 10` in the second, 746 numbers to learn."
  - label: "Two dense layers with nothing between"
    lines: "{ln('first, second = Dense(35, 16, seed=1)')}-{ln('two Dense layers with nothing between')}"
    note: "Multiply the two layers out and one layer appears: weights `W1 @ W2`, bias `b1 @ W2 + b2`. The merged layer gives the same outputs as the stacked pair, so without an activation the second layer added nothing. With the ReLU between them the outputs differ: the bend is what makes depth matter."
  - label: "A neuron is a boundary"
    lines: "{ln('points = np.array([[0.0, 0.0]')}-{ln('a neuron with w = [1, 1]')}"
    note: "Before the activation a neuron's sum is zero along a line (a flat boundary, in more dimensions), here `x + y = 1.5`. The neuron fires for inputs on one side and is silent on the other: a detector for one direction in the input, which the next layer combines with others."
''',
)
write("exercises/example-a-network-as-objects/solution.py", EXAMPLE)
write(
    "exercises/example-a-network-as-objects/test_exercise.py",
    f'''from checks import run


def test_the_walkthrough():
    """Prints the neuron, the layer, the shapes, the count, the collapse and the boundary."""
    assert run() == {EXAMPLE_OUT!r}
''',
)

write(
    "exercises/fill-dense-layer/exercise.yaml",
    f'''id: fill-dense-layer
stage: fill_in
rev: 1
title: "A dense layer's forward pass"
prompt: |
  `Dense` holds a weight matrix `W` of shape `(inputs, outputs)` and a bias `b` with one entry per output. Replace each `...` so `forward` computes every neuron on every row of the batch at once, and `parameters` hands out the two arrays, so that the program prints:

  ```
{block(FILL_OUT)}  ```

  The program fails until every `...` is replaced.
hints:
  - "A batch of shape `(rows, inputs)` times `W` is `(rows, outputs)`; the bias is added to every row."
  - "The parameters are the weights and the bias, in that order."
skills: [neuron]
''',
)
write("exercises/fill-dense-layer/starter.py", FILL_STARTER)
write("exercises/fill-dense-layer/solution.py", FILL_SOLUTION)
write(
    "exercises/fill-dense-layer/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints the three rows and the parameter shapes."""
    printed = run()
    assert printed == {FILL_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_another_layer():
    """A layer with a single neuron gives the weighted sum plus the bias for every row, and its parameters are W and b."""
    Dense = function("Dense")
    layer = Dense(np.array([[2.0], [-1.0]]), np.array([0.5]))
    assert layer.forward(np.array([[1.0, 1.0], [3.0, 0.0]])).tolist() == [[1.5], [6.5]]
    W, b = layer.parameters()
    assert W.shape == (2, 1) and b.shape == (1,)
''',
)
write("exercises/fill-dense-layer/wrong/no-bias.py", FILL_WRONG)
write(
    "exercises/fill-dense-layer/wrong/typed-in.py",
    "class Dense:\n    def __init__(self, W, b):\n        self.W = W\n        self.b = b\n\n    def forward(self, X):\n        return X\n\n    def parameters(self):\n        return []\n\n\n" + "".join(f"print({line!r})\n" for line in FILL_OUT.splitlines()),
)

write(
    "exercises/write-sequential/exercise.yaml",
    f'''id: write-sequential
stage: write
rev: 1
title: "Sequential"
prompt: |
  The starter has `Dense` and `ReLU`. Write `Sequential`, which takes a list of layers: `forward(X)` runs them in order, feeding each layer's output to the next, and `parameters()` returns every layer's parameters in one list, in order. The program builds a `[4, 8, 2]` network, runs six rows through it, and checks the result against the three layers called by hand:

  ```
{block(WRITE_OUT)}  ```
hints:
  - "Loop over the layers, replacing `X` with `layer.forward(X)` each time, and return the last `X`."
  - "A list comprehension with two `for` clauses flattens the layers' parameter lists into one."
skills: [compose]
''',
)
write("exercises/write-sequential/starter.py", WRITE_STARTER)
write("exercises/write-sequential/solution.py", WRITE_SOLUTION)
write(
    "exercises/write-sequential/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints the output shape, the parameter shapes and the count, then True."""
    printed = run()
    assert printed == {WRITE_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_other_stacks():
    """A one-layer stack is that layer; a three-layer stack runs all three in order and lists six parameters."""
    Sequential = function("Sequential")
    Dense = function("Dense")
    ReLU = function("ReLU")
    layer = Dense(3, 2, seed=9)
    X = np.array([[1.0, -1.0, 2.0], [0.5, 0.5, 0.5]])
    assert np.allclose(Sequential([layer]).forward(X), layer.forward(X))
    stack = Sequential([Dense(3, 4, seed=1), ReLU(), Dense(4, 4, seed=2), ReLU(), Dense(4, 1, seed=3)])
    by_hand = X
    for piece in stack.layers:
        by_hand = piece.forward(by_hand)
    assert np.allclose(stack.forward(X), by_hand) and stack.forward(X).shape == (2, 1)
    assert [p.shape for p in stack.parameters()] == [(3, 4), (4,), (4, 4), (4,), (4, 1), (1,)]
''',
)
write("exercises/write-sequential/wrong/skips-the-last-layer.py", WRITE_SKIPS_LAST)
write("exercises/write-sequential/wrong/first-layer-only.py", WRITE_FIRST_ONLY)
write(
    "exercises/write-sequential/wrong/typed-in.py",
    WRITE_HEAD + "\n\nclass Sequential:\n    def __init__(self, layers):\n        self.layers = layers\n\n    def forward(self, X):\n        return X\n\n    def parameters(self):\n        return []\n\n\n" + "".join(f"print({line!r})\n" for line in WRITE_OUT.splitlines()),
)

# --- the proof -----------------------------------------------------------------------------------

write(
    "exercises/build-a-network-of-objects/exercise.yaml",
    f'''id: build-a-network-of-objects
stage: build
rev: 1
title: "A network of objects"
prompt: |
  Starting from a blank editor, write the module's three classes and two helpers:

  - `Dense(n_in, n_out, seed=0)`: `W` of shape `(n_in, n_out)` drawn from `np.random.default_rng(seed).standard_normal` and divided by `sqrt(n_in)`, `b` of zeros; `forward(X)` is `X @ W + b`; `parameters()` returns `[W, b]`.
  - `ReLU()`: `forward(X)` keeps the positive part of every value; `parameters()` returns `[]`.
  - `Sequential(layers)`: `forward(X)` runs the layers in order; `parameters()` gathers every layer's parameters into one list, in order.
  - `count_parameters(net)`: how many numbers the network learns.
  - `shapes_through(net, X)`: the shape of the batch after each layer, as a list of tuples.

  Then print:

  ```python
  net = Sequential([Dense(35, 16, seed=1), ReLU(), Dense(16, 10, seed=2)])
  X = np.random.default_rng(0).standard_normal((8, 35))
  print(shapes_through(net, X), count_parameters(net))
  hand = Dense(2, 3)
  hand.W, hand.b = np.array([[0.5, -1.0, 0.2], [-0.25, 0.5, 0.4]]), np.array([0.1, -0.3, -0.5])
  tiny = Sequential([hand, ReLU()])
  print(np.round(tiny.forward(np.array([[1.0, 2.0], [-1.0, 1.0]])), 2).tolist())
  first, second = Dense(35, 16, seed=1), Dense(16, 10, seed=2)
  merged = Dense(35, 10)
  merged.W, merged.b = first.W @ second.W, first.b @ second.W + second.b
  print(np.allclose(Sequential([first, second]).forward(X), merged.forward(X)), np.allclose(net.forward(X), merged.forward(X)))
  ```

  ```
{block(BUILD_OUT)}  ```

  The checks run a hand-set layer against the arithmetic, feed ReLU negatives and positives, compare `Sequential` with the layers called one by one, count a `[7, 5, 3]` network by hand, check that two layers with the same seed start identical and that the starting scale is about `1 / sqrt(n_in)`, and trace the shapes of a four-layer stack.
skills: [neuron, compose, count, nonlinearity]
''',
)
write("exercises/build-a-network-of-objects/starter.py", "")
write("exercises/build-a-network-of-objects/solution.py", BUILD_SOLUTION)
write(
    "exercises/build-a-network-of-objects/test_exercise.py",
    f'''import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints the three lines."""
    assert run() == {BUILD_OUT!r}


def test_dense_by_hand():
    """A hand-set layer gives X @ W + b for a batch, and parameters() is [W, b]."""
    Dense = function("Dense")
    layer = Dense(3, 2)
    layer.W, layer.b = np.array([[1.0, -1.0], [0.0, 2.0], [0.5, 0.5]]), np.array([-0.5, 0.0])
    X = np.array([[1.0, 1.0, 1.0], [2.0, 0.0, -2.0]])
    assert layer.forward(X).tolist() == [[1.0, 1.5], [0.5, -3.0]]
    W, b = layer.parameters()
    assert W is layer.W and b is layer.b


def test_relu():
    """ReLU zeroes negatives, keeps positives and zero, keeps the shape, and has no parameters."""
    ReLU = function("ReLU")
    out = ReLU().forward(np.array([[-2.0, 0.0, 3.5], [1e-9, -1e-9, -100.0]]))
    assert out.tolist() == [[0.0, 0.0, 3.5], [1e-9, 0.0, 0.0]] and ReLU().parameters() == []


def test_sequential_and_counts():
    """A [7, 5, 3] stack matches its layers called one by one, lists four parameters of the right shapes, and counts 58."""
    Dense = function("Dense")
    ReLU = function("ReLU")
    Sequential = function("Sequential")
    count_parameters = function("count_parameters")
    shapes_through = function("shapes_through")
    stack = Sequential([Dense(7, 5, seed=3), ReLU(), Dense(5, 3, seed=4)])
    X = np.random.default_rng(1).standard_normal((4, 7))
    by_hand = stack.layers[2].forward(stack.layers[1].forward(stack.layers[0].forward(X)))
    assert np.allclose(stack.forward(X), by_hand)
    assert [p.shape for p in stack.parameters()] == [(7, 5), (5,), (5, 3), (3,)]
    assert count_parameters(stack) == 58
    assert shapes_through(stack, X) == [(4, 5), (4, 5), (4, 3)]
    deep = Sequential([Dense(7, 6, seed=1), ReLU(), Dense(6, 6, seed=2), ReLU(), Dense(6, 2, seed=3)])
    assert shapes_through(deep, X) == [(4, 6), (4, 6), (4, 6), (4, 6), (4, 2)] and count_parameters(deep) == 7 * 6 + 6 + 6 * 6 + 6 + 6 * 2 + 2


def test_starting_weights():
    """Two layers with the same seed start identical, different seeds differ, biases are zero, and the scale is about 1 / sqrt(n_in)."""
    Dense = function("Dense")
    a, b, c = Dense(100, 50, seed=7), Dense(100, 50, seed=7), Dense(100, 50, seed=8)
    assert np.array_equal(a.W, b.W) and not np.array_equal(a.W, c.W)
    assert np.array_equal(a.b, np.zeros(50)) and 0.07 < a.W.std() < 0.13
''',
)
write("exercises/build-a-network-of-objects/wrong/no-bias.py", BUILD_NO_BIAS)
write("exercises/build-a-network-of-objects/wrong/relu-keeps-negatives.py", BUILD_RELU_KEEPS_NEGATIVES)
write("exercises/build-a-network-of-objects/wrong/counts-arrays-not-numbers.py", BUILD_COUNTS_LAYERS)
write(
    "exercises/build-a-network-of-objects/wrong/typed-in.py",
    "import numpy as np\n\n\nclass Dense:\n    def __init__(self, n_in, n_out, seed=0):\n        self.W = np.zeros((n_in, n_out))\n        self.b = np.zeros(n_out)\n\n    def forward(self, X):\n        return X\n\n    def parameters(self):\n        return []\n\n\nclass ReLU:\n    def forward(self, X):\n        return X\n\n    def parameters(self):\n        return []\n\n\nclass Sequential:\n    def __init__(self, layers):\n        self.layers = layers\n\n    def forward(self, X):\n        return X\n\n    def parameters(self):\n        return []\n\n\ndef count_parameters(net):\n    return 746\n\n\ndef shapes_through(net, X):\n    return [(8, 16), (8, 16), (8, 10)]\n\n\n"
    + "".join(f"print({line!r})\n" for line in BUILD_OUT.splitlines()),
)

write(
    "exercises/debug-a-network-that-will-not-run/exercise.yaml",
    f'''id: debug-a-network-that-will-not-run
stage: debug
rev: 1
title: "A network that won't run"
prompt: |
  A `[3, 4, 2]` network of the module's classes on a batch of two rows. It should print:

  ```
{block(DEBUG_OUT)}  ```

  It has two bugs. Run it: it crashes inside `forward` with a `matmul` shape error, because `Dense` builds `W` as `(n_out, n_in)`, the wrong way round for `X @ W`; a batch of shape `(rows, inputs)` needs `W` of shape `(inputs, outputs)`. Fix that, and the hidden values come out negative or zero: `ReLU` keeps the **negative** part with `np.minimum`. A ReLU keeps the positive part, `np.maximum(X, 0.0)`.
skills: [compose, nonlinearity]
''',
)
write("exercises/debug-a-network-that-will-not-run/starter.py", DEBUG_STARTER)
write("exercises/debug-a-network-that-will-not-run/solution.py", DEBUG_SOLUTION)
write(
    "exercises/debug-a-network-that-will-not-run/test_exercise.py",
    f'''import numpy as np

from checks import function, run

EXPECTED = {DEBUG_OUT!r}


def test_the_output():
    """Prints the output shape and the two facts about the hidden layer."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\\n{{EXPECTED}}\\nYour program printed:\\n{{printed}}"


def test_the_classes():
    """Dense builds W as (inputs, outputs) and computes X @ W + b; ReLU zeroes negatives and keeps positives."""
    Dense = function("Dense")
    ReLU = function("ReLU")
    layer = Dense(5, 2, seed=3)
    assert layer.W.shape == (5, 2) and layer.b.shape == (2,)
    X = np.random.default_rng(0).standard_normal((3, 5))
    assert np.allclose(layer.forward(X), X @ layer.W + layer.b)
    assert ReLU().forward(np.array([-1.0, 0.0, 2.0])).tolist() == [0.0, 0.0, 2.0]
''',
)
write("exercises/debug-a-network-that-will-not-run/wrong/still-transposed.py", DEBUG_STILL_TRANSPOSED)
write("exercises/debug-a-network-that-will-not-run/wrong/still-minimum.py", DEBUG_STILL_MINIMUM)
write(
    "exercises/debug-a-network-that-will-not-run/wrong/typed-in.py",
    "import numpy as np\n\n\nclass Dense:\n    def __init__(self, n_in, n_out, seed=0):\n        self.W = np.zeros((n_in, n_out))\n        self.b = np.zeros(n_out)\n\n    def forward(self, X):\n        return X\n\n\nclass ReLU:\n    def forward(self, X):\n        return X\n\n\n" + "".join(f"print({line!r})\n" for line in DEBUG_OUT.splitlines()),
)

write(
    "exercises/review-sequential/exercise.yaml",
    f'''id: review-sequential
stage: review_code
rev: 1
title: "Sequential, from memory"
prompt: |
  Write `Dense(n_in, n_out, seed=0)` (random `W` of shape `(n_in, n_out)` scaled by `1 / sqrt(n_in)`, zero `b`, `forward`, `parameters`), `ReLU` and `Sequential` (`forward` runs the layers in order, `parameters` gathers theirs), then print the output shape of seven rows of zeros through `[3, 5, 1]` and the parameter count:

  ```
{block(REVIEW_CODE_OUT)}  ```
skills: [compose, count]
''',
)
write("exercises/review-sequential/starter.py", "")
write("exercises/review-sequential/solution.py", REVIEW_CODE_SOLUTION)
write(
    "exercises/review-sequential/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints the shape and the count."""
    assert run() == {REVIEW_CODE_OUT!r}


def test_the_stack():
    """A [4, 3, 2] stack matches its layers called one by one and lists parameters of the right shapes."""
    Dense = function("Dense")
    ReLU = function("ReLU")
    Sequential = function("Sequential")
    stack = Sequential([Dense(4, 3, seed=1), ReLU(), Dense(3, 2, seed=2)])
    X = np.random.default_rng(2).standard_normal((5, 4))
    by_hand = stack.layers[2].forward(stack.layers[1].forward(stack.layers[0].forward(X)))
    assert np.allclose(stack.forward(X), by_hand)
    assert [p.shape for p in stack.parameters()] == [(4, 3), (3,), (3, 2), (2,)]
''',
)
write("exercises/review-sequential/wrong/first-layer-only.py", REVIEW_CODE_WRONG)
write(
    "exercises/review-sequential/wrong/typed-in.py",
    "class Sequential:\n    pass\n\n\n" + "".join(f"print({line!r})\n" for line in REVIEW_CODE_OUT.splitlines()),
)

print("ml.nn.neurons-and-layers written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
