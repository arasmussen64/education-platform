"""Writes Checkpoint 7, ml.m7.checkpoint ("make it fast"). Run from the
repository root under uv (python -m uv run python <this file>), so every
program's expected output is captured from CPython rather than typed in.
Nothing is timed: the hot loop is found by call counts, the vectorized fix
is proven by a profile with zero calls and by an array subclass that counts
Python-level iteration, and the numeric bugs print exact values. Files are
written as bytes with LF endings."""

import pathlib
import subprocess
import sys

ROOT = pathlib.Path("content/topics/ml.m7.checkpoint")


def write(relative: str, text: str) -> None:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


def out(program: str) -> str:
    """Run with warnings as errors: a reference solution must be silent."""
    result = subprocess.run([sys.executable, "-W", "error", "-c", program], capture_output=True, text=True, check=True)
    return result.stdout.replace("\r\n", "\n")


def out_loose(program: str) -> str:
    """Run as the browser would: a known-wrong solution may warn on its way to a wrong answer."""
    result = subprocess.run([sys.executable, "-c", program], capture_output=True, text=True, check=True)
    return result.stdout.replace("\r\n", "\n")


def block(text: str, indent: str = "  ") -> str:
    return "".join(indent + line + "\n" for line in text.rstrip("\n").splitlines())


# An array that counts Python-level iteration and element-by-element access;
# the checks hand it to a function that should be vectorized and expect zero.
WATCHED = '''class Watched(np.ndarray):
    """An array that counts how often Python iterates over it, reads single elements from it, or turns a matrix into lists."""

    iterations = 0
    elements = 0

    def __iter__(self):
        Watched.iterations += 1
        return super().__iter__()

    def __getitem__(self, key):
        result = super().__getitem__(key)
        if np.ndim(result) == 0:
            Watched.elements += 1
        return result

    def tolist(self):
        if self.ndim >= 2:
            Watched.elements += self.size
        return super().tolist()


def watched(a, dtype=np.float64):
    """A counting view of a, with the counts reset."""
    Watched.iterations = 0
    Watched.elements = 0
    return np.asarray(a, dtype=dtype).view(Watched)
'''

# =====================================================================================
# the pipeline's pieces, shared by the build, its versions and the steps
# =====================================================================================

PIECES = '''import cProfile
import pstats

import numpy as np


def standardize(X):
    """Each column minus its mean, over its standard deviation; a column with no spread becomes zeros."""
    spread = X.std(axis=0)
    return (X - X.mean(axis=0)) / np.where(spread == 0, 1.0, spread)


def nearest_centroid(X, centroids):
    """The index of the nearest centroid for every row, by squared distance, the first on a tie: one array operation, no Python loop."""
    squared = ((X[:, None, :] - centroids[None, :, :]) ** 2).sum(axis=2)
    return np.argmin(squared, axis=1).tolist()


def weekly(clicks):
    """Seven times the daily clicks, in an integer type wide enough to hold them whatever the column's dtype."""
    return clicks.astype(np.int64) * 7


def mean_loss(losses):
    """The mean, summed as one array operation and accumulated in float64, so a hundred thousand small values don't drift."""
    return float(losses.sum(dtype=np.float64) / len(losses))


def softmax(logits):
    """Row-wise softmax with the largest logit of each row subtracted first, so exp never overflows and no row becomes NaN."""
    shifted = np.exp(logits - logits.max(axis=1, keepdims=True))
    return shifted / shifted.sum(axis=1, keepdims=True)


def model_cost(layers, examples, batch, itemsize):
    """(parameters, training FLOPs, bytes): weights and biases per dense layer; 6 FLOPs per parameter per example; four copies of the parameters plus one batch of activations."""
    params = sum(i * o + o for i, o in zip(layers, layers[1:]))
    flops = 6 * params * examples
    bytes_needed = params * 4 * itemsize + batch * sum(layers) * itemsize
    return params, flops, bytes_needed


def calls_to(function, name, *args):
    """How many times the function called name runs while function(*args) runs, read from a cProfile table: the hot loop, found by its call count."""
    profiler = cProfile.Profile()
    profiler.enable()
    function(*args)
    profiler.disable()
    return sum(row[1] for (file, line, func), row in pstats.Stats(profiler).stats.items() if func == name)
'''

WRONG_LOOPED_NEAREST = (
    "    squared = ((X[:, None, :] - centroids[None, :, :]) ** 2).sum(axis=2)\n    return np.argmin(squared, axis=1).tolist()",
    "    labels = []\n    for row in X:\n        best, best_d = -1, float(\"inf\")\n        for j, c in enumerate(centroids):\n            d = float(((row - c) ** 2).sum())\n            if d < best_d:\n                best, best_d = j, d\n        labels.append(best)\n    return labels",
)
WRONG_INT8_WEEKLY = ("    return clicks.astype(np.int64) * 7", "    return clicks * 7")
WRONG_LOOPED_MEAN = (
    "    return float(losses.sum(dtype=np.float64) / len(losses))",
    "    total = np.float32(0)\n    for loss in losses:\n        total += loss\n    return float(total / len(losses))",
)
WRONG_NAIVE_SOFTMAX = ("    shifted = np.exp(logits - logits.max(axis=1, keepdims=True))", "    shifted = np.exp(logits)")
for old, new in (WRONG_LOOPED_NEAREST, WRONG_INT8_WEEKLY, WRONG_LOOPED_MEAN, WRONG_NAIVE_SOFTMAX):
    assert PIECES.count(old) == 1, old[:40]


def variants(solution: str) -> dict[str, str]:
    """The four known-wrong versions of a solution built on PIECES."""
    return {
        "looped-nearest": solution.replace(*WRONG_LOOPED_NEAREST),
        "int8-weekly": solution.replace(*WRONG_INT8_WEEKLY),
        "running-total-in-float32": solution.replace(*WRONG_LOOPED_MEAN),
        "naive-softmax": solution.replace(*WRONG_NAIVE_SOFTMAX),
    }


# --- the build and its two fresh versions ------------------------------------------------------

SLOW = '''

def distance_squared(a, b):
    return float(((a - b) ** 2).sum())


def nearest_centroid_loop(X, centroids):
    """The pipeline's hot loop as first written: every row against every centroid, one call each."""
    labels = []
    for row in X:
        best, best_d = -1, float("inf")
        for j, c in enumerate(centroids):
            d = distance_squared(row, c)
            if d < best_d:
                best, best_d = j, d
        labels.append(best)
    return labels
'''
BUILD_TAIL = '''

X = np.array([[1.0, 10.0], [2.0, 20.0], [3.0, 30.0], [6.0, 60.0]])
centroids = np.array([[-1.0, -1.0], [1.5, 1.5]])
Z = standardize(X)
print(np.round(Z, 3).tolist(), bool(np.allclose(Z.mean(axis=0), 0)))
print(nearest_centroid(Z, centroids))
print(calls_to(nearest_centroid_loop, "distance_squared", Z, centroids), calls_to(nearest_centroid, "distance_squared", Z, centroids), calls_to(nearest_centroid_loop, "distance_squared", np.vstack([Z, Z]), centroids))
print(weekly(np.array([20, 50, 100, 120], dtype=np.int8)).tolist())
print(round(mean_loss(np.full(100_000, 0.1, dtype=np.float32)), 6))
print(np.round(softmax(np.array([[1000.0, 1001.0], [1.0, 2.0]])), 3).tolist())
print(model_cost([4, 64, 32, 5], 400, 32, 4))
'''
SENSORS_TAIL = '''

X = np.array([[18.0, 40.0], [19.0, 42.0], [21.0, 45.0], [30.0, 80.0], [31.0, 85.0]])
centroids = np.array([[-0.5, -0.5], [1.5, 1.5]])
Z = standardize(X)
print(np.round(Z, 3).tolist(), bool(np.allclose(Z.std(axis=0), 1)))
print(nearest_centroid(Z, centroids))
print(calls_to(nearest_centroid_loop, "distance_squared", Z, centroids), calls_to(nearest_centroid, "distance_squared", Z, centroids), calls_to(nearest_centroid_loop, "distance_squared", np.vstack([Z, Z]), centroids))
print(weekly(np.array([24, 48, 96, 120], dtype=np.int8)).tolist())
print(round(mean_loss(np.full(100_000, 0.1, dtype=np.float32)), 6))
print(np.round(softmax(np.array([[2000.0, 2000.0, 2001.0]])), 3).tolist())
print(model_cost([2, 16, 8, 3], 500, 16, 4))
'''
TICKETS_TAIL = '''

X = np.array([[5.0, 1.0], [7.0, 2.0], [60.0, 9.0], [55.0, 8.0], [6.0, 1.0], [58.0, 9.0]])
centroids = np.array([[-0.8, -0.8], [0.9, 0.9]])
Z = standardize(X)
print(np.round(Z, 3).tolist(), bool(np.allclose(Z.mean(axis=0), 0)))
print(nearest_centroid(Z, centroids))
print(calls_to(nearest_centroid_loop, "distance_squared", Z, centroids), calls_to(nearest_centroid, "distance_squared", Z, centroids), calls_to(nearest_centroid_loop, "distance_squared", np.vstack([Z, Z]), centroids))
print(weekly(np.array([10, 30, 90, 127], dtype=np.int8)).tolist())
print(round(mean_loss(np.full(50_000, 0.3, dtype=np.float32)), 6))
print(np.round(softmax(np.array([[-1500.0, -1499.0], [0.0, 0.0]])), 3).tolist())
print(model_cost([2, 32, 4], 600, 8, 2))
'''
BUILDS = {
    "build-a-fast-pipeline": PIECES + SLOW + BUILD_TAIL,
    "build-a-fast-pipeline-sensors": PIECES + SLOW + SENSORS_TAIL,
    "build-a-fast-pipeline-tickets": PIECES + SLOW + TICKETS_TAIL,
}
PASTES = {
    "build-a-fast-pipeline": "import numpy as np\n\n" + (SLOW + BUILD_TAIL).strip("\n") + "\n",
    "build-a-fast-pipeline-sensors": "import numpy as np\n\n" + (SLOW + SENSORS_TAIL).strip("\n") + "\n",
    "build-a-fast-pipeline-tickets": "import numpy as np\n\n" + (SLOW + TICKETS_TAIL).strip("\n") + "\n",
}
BUILD_OUTS = {name: out(code) for name, code in BUILDS.items()}
for name, printed in BUILD_OUTS.items():
    print(name + ":\n" + printed)
assert BUILD_OUTS["build-a-fast-pipeline"] == "[[-1.069, -1.069], [-0.535, -0.535], [0.0, 0.0], [1.604, 1.604]] True\n[0, 0, 0, 1]\n8 0 16\n[140, 350, 700, 840]\n0.1\n[[0.269, 0.731], [0.269, 0.731]]\n(2565, 6156000, 54480)\n", BUILD_OUTS["build-a-fast-pipeline"]
assert BUILD_OUTS["build-a-fast-pipeline-sensors"].splitlines()[2:] == ["10 0 20", "[168, 336, 672, 840]", "0.1", "[[0.212, 0.212, 0.576]]", "(211, 633000, 5232)"], BUILD_OUTS["build-a-fast-pipeline-sensors"]
assert BUILD_OUTS["build-a-fast-pipeline-tickets"].splitlines()[2:] == ["12 0 24", "[70, 210, 630, 889]", "0.3", "[[0.269, 0.731], [0.5, 0.5]]", "(228, 820800, 2432)"], BUILD_OUTS["build-a-fast-pipeline-tickets"]
for name, code in BUILDS.items():
    wrongs = variants(code)
    assert out_loose(wrongs["looped-nearest"]) == BUILD_OUTS[name], "the loop prints the same labels and fails the counting test"
    for key in ("int8-weekly", "running-total-in-float32", "naive-softmax"):
        assert out_loose(wrongs[key]) != BUILD_OUTS[name], (name, key)

# --- the worked example ----------------------------------------------------------------------

EXAMPLE = '''import cProfile
import pstats

import numpy as np


def distance_squared(a, b):
    return float(((a - b) ** 2).sum())


def nearest_centroid_loop(X, centroids):
    """The pipeline's hot loop as first written: every row against every centroid, one call each."""
    labels = []
    for row in X:
        best, best_d = -1, float("inf")
        for j, c in enumerate(centroids):
            d = distance_squared(row, c)
            if d < best_d:
                best, best_d = j, d
        labels.append(best)
    return labels


def nearest_centroid(X, centroids):
    """The same labels as one array operation: broadcasting makes every row-centroid difference at once."""
    squared = ((X[:, None, :] - centroids[None, :, :]) ** 2).sum(axis=2)
    return np.argmin(squared, axis=1).tolist()


def profile(function, *args):
    profiler = cProfile.Profile()
    profiler.enable()
    result = function(*args)
    profiler.disable()
    return result, pstats.Stats(profiler)


def calls(stats, name):
    return sum(row[1] for (file, line, func), row in stats.stats.items() if func == name)


rng = np.random.default_rng(0)
X = rng.standard_normal((400, 4))
centroids = np.array([[2.0, 2.0, 2.0, 2.0], [-2.0, -2.0, -2.0, -2.0], [2.0, -2.0, 2.0, -2.0], [-2.0, 2.0, -2.0, 2.0], [0.0, 0.0, 0.0, 0.0]])
slow, stats = profile(nearest_centroid_loop, X, centroids)
fast, fast_stats = profile(nearest_centroid, X, centroids)
print(f"the loop: {calls(stats, 'distance_squared'):,} calls to distance_squared for 400 rows | vectorized: {calls(fast_stats, 'distance_squared')} calls, same labels: {slow == fast}")
_, doubled = profile(nearest_centroid_loop, np.vstack([X, X]), centroids)
print(f"doubling the rows: {calls(doubled, 'distance_squared'):,} calls, {calls(doubled, 'distance_squared') / calls(stats, 'distance_squared'):.1f} times as many: linear in the rows either way; vectorizing changes the constant, not the order")

clicks = np.array([20, 50, 100, 120], dtype=np.int8)
print("weekly clicks from an int8 column:", (clicks * 7).tolist(), "| widened to int64 first:", (clicks.astype(np.int64) * 7).tolist())

losses = np.full(100_000, 0.1, dtype=np.float32)
total = np.float32(0)
for loss in losses:
    total += loss
print(f"mean loss from a float32 running total: {float(total) / len(losses):.6f} | summed in float64: {float(losses.sum(dtype=np.float64)) / len(losses):.6f}")

logits = np.array([[1000.0, 1001.0], [1.0, 2.0]])
with np.errstate(over="ignore", invalid="ignore"):
    naive = np.exp(logits) / np.exp(logits).sum(axis=1, keepdims=True)
shifted = np.exp(logits - logits.max(axis=1, keepdims=True))
stable = shifted / shifted.sum(axis=1, keepdims=True)
print("softmax of a logit of 1,000: naive has NaN:", bool(np.isnan(naive).any()), "| stable rows sum to 1:", bool(np.allclose(stable.sum(axis=1), 1)), "| first row:", np.round(stable[0], 3).tolist())

LAYERS = [4, 64, 32, 5]
params = sum(i * o + o for i, o in zip(LAYERS, LAYERS[1:]))
print(f"the model the pipeline feeds, layers {LAYERS}: {params:,} parameters, {6 * params * 400:,} FLOPs to train on the 400 rows, {params * 16 + sum(LAYERS) * 32 * 4:,} bytes of state and activations at a batch of 32")
'''
EXAMPLE_OUT = out(EXAMPLE)
print("example:\n" + EXAMPLE_OUT)
EX = EXAMPLE_OUT.splitlines()
assert len(EX) == 6, EX
assert EX[0] == "the loop: 2,000 calls to distance_squared for 400 rows | vectorized: 0 calls, same labels: True", EX[0]
assert EX[1] == "doubling the rows: 4,000 calls, 2.0 times as many: linear in the rows either way; vectorizing changes the constant, not the order", EX[1]
assert EX[2] == "weekly clicks from an int8 column: [-116, 94, -68, 72] | widened to int64 first: [140, 350, 700, 840]", EX[2]
assert EX[3] == "mean loss from a float32 running total: 0.099986 | summed in float64: 0.100000", EX[3]
assert EX[4] == "softmax of a logit of 1,000: naive has NaN: True | stable rows sum to 1: True | first row: [0.269, 0.731]", EX[4]
assert EX[5] == "the model the pipeline feeds, layers [4, 64, 32, 5]: 2,565 parameters, 6,156,000 FLOPs to train on the 400 rows, 54,480 bytes of state and activations at a batch of 32", EX[5]
EXAMPLE_LINES = EXAMPLE.splitlines()


def ln(text: str, after: int = 0) -> int:
    return next(i + 1 for i, line in enumerate(EXAMPLE_LINES) if i + 1 > after and text in line)


# --- the debug ----------------------------------------------------------------------------------

DEBUG_SOLUTION = '''import numpy as np


def weekly(clicks):
    """Seven times the daily clicks, in an integer type wide enough to hold them."""
    return clicks.astype(np.int64) * 7


def mean_loss(losses):
    """The mean, summed as one array operation and accumulated in float64."""
    return float(losses.sum(dtype=np.float64) / len(losses))


def softmax(logits):
    """Row-wise softmax, with each row's largest logit subtracted first so that exp never overflows."""
    shifted = np.exp(logits - logits.max(axis=1, keepdims=True))
    return shifted / shifted.sum(axis=1, keepdims=True)


clicks = np.array([20, 50, 100, 120], dtype=np.int8)
print("weekly:", weekly(clicks).tolist())
print("mean loss:", round(mean_loss(np.full(100_000, 0.1, dtype=np.float32)), 6))
print("softmax:", np.round(softmax(np.array([[1000.0, 1001.0], [1.0, 2.0]])), 3).tolist())
'''
DEBUG_STARTER = DEBUG_SOLUTION.replace(*WRONG_INT8_WEEKLY).replace(*WRONG_LOOPED_MEAN).replace(*WRONG_NAIVE_SOFTMAX)
DEBUG_WRONGS = {
    "still-int8": DEBUG_SOLUTION.replace(*WRONG_INT8_WEEKLY),
    "still-a-running-total": DEBUG_SOLUTION.replace(*WRONG_LOOPED_MEAN),
    "still-overflows": DEBUG_SOLUTION.replace(*WRONG_NAIVE_SOFTMAX),
}
DEBUG_OUT = out(DEBUG_SOLUTION)
STARTER_OUT = out_loose(DEBUG_STARTER)
print("debug:\n" + DEBUG_OUT + "starter:\n" + STARTER_OUT)
assert DEBUG_OUT == "weekly: [140, 350, 700, 840]\nmean loss: 0.1\nsoftmax: [[0.269, 0.731], [0.269, 0.731]]\n", DEBUG_OUT
assert STARTER_OUT == "weekly: [-116, 94, -68, 72]\nmean loss: 0.099986\nsoftmax: [[nan, nan], [0.269, 0.731]]\n", STARTER_OUT
for key, code in DEBUG_WRONGS.items():
    assert code != DEBUG_SOLUTION and out_loose(code) != DEBUG_OUT, key

# --- the steps ----------------------------------------------------------------------------------

STEP_NEAREST = '''import numpy as np


def nearest_centroid(X, centroids):
    """The index of the nearest centroid for every row, as one array operation: broadcasting makes every row-centroid difference at once."""
    squared = ((X[:, None, :] - centroids[None, :, :]) ** 2).sum(axis=2)
    return np.argmin(squared, axis=1).tolist()


X = np.array([[0.0, 0.0], [5.0, 5.0], [4.0, 6.0], [-1.0, 1.0]])
centroids = np.array([[0.0, 1.0], [5.0, 6.0]])
print(nearest_centroid(X, centroids))
'''
STEP_NEAREST_STARTER = STEP_NEAREST.replace("** 2).sum(axis=2)", "** 2).sum(axis=...)").replace("np.argmin(squared, axis=1)", "np.argmin(squared, axis=...)")
STEP_NEAREST_WRONG = STEP_NEAREST.replace("** 2).sum(axis=2)", "** 2).sum(axis=0)")
STEP_NEAREST_OUT = out(STEP_NEAREST)
assert STEP_NEAREST_OUT == "[0, 1, 1, 0]\n", STEP_NEAREST_OUT
assert out(STEP_NEAREST_WRONG) != STEP_NEAREST_OUT

STEP_WIDEN = '''import numpy as np


def weekly(clicks):
    """Seven times the daily clicks: widen the column to int64 before multiplying, whatever dtype it arrived in."""
    return clicks.astype(np.int64) * 7


clicks = np.array([20, 50, 100, 120], dtype=np.int8)
print(weekly(clicks).tolist(), weekly(clicks).dtype)
'''
STEP_WIDEN_STARTER = STEP_WIDEN.replace("clicks.astype(np.int64) * 7", "clicks.astype(...) * 7")
STEP_WIDEN_WRONG = STEP_WIDEN.replace("clicks.astype(np.int64) * 7", "clicks.astype(np.int8) * 7")
STEP_WIDEN_OUT = out(STEP_WIDEN)
assert STEP_WIDEN_OUT == "[140, 350, 700, 840] int64\n", STEP_WIDEN_OUT
assert out(STEP_WIDEN_WRONG) != STEP_WIDEN_OUT

STEP_SUM = '''import numpy as np


def mean_loss(losses):
    """Sum as one array operation, accumulating in float64, then divide: no running total, no drift."""
    return float(losses.sum(dtype=np.float64) / len(losses))


losses = np.full(100_000, 0.1, dtype=np.float32)
print(round(mean_loss(losses), 6))
'''
STEP_SUM_STARTER = STEP_SUM.replace("losses.sum(dtype=np.float64)", "losses.sum(dtype=...)")
STEP_SUM_WRONG = STEP_SUM.replace("    return float(losses.sum(dtype=np.float64) / len(losses))", WRONG_LOOPED_MEAN[1])
STEP_SUM_OUT = out(STEP_SUM)
assert STEP_SUM_OUT == "0.1\n", STEP_SUM_OUT
assert out(STEP_SUM_WRONG) == "0.099986\n"

STEP_SOFTMAX = '''import numpy as np


def softmax(logits):
    """Row-wise softmax: subtract each row's largest logit first, so the biggest exponent is 0 and nothing overflows."""
    shifted = np.exp(logits - logits.max(axis=1, keepdims=True))
    return shifted / shifted.sum(axis=1, keepdims=True)


print(np.round(softmax(np.array([[1000.0, 1001.0], [1.0, 2.0]])), 3).tolist())
'''
STEP_SOFTMAX_STARTER = STEP_SOFTMAX.replace("np.exp(logits - logits.max(axis=1, keepdims=True))", "np.exp(logits - ...)")
STEP_SOFTMAX_WRONG = STEP_SOFTMAX.replace("np.exp(logits - logits.max(axis=1, keepdims=True))", "np.exp(logits - 0)")
STEP_SOFTMAX_OUT = out(STEP_SOFTMAX)
assert STEP_SOFTMAX_OUT == "[[0.269, 0.731], [0.269, 0.731]]\n", STEP_SOFTMAX_OUT
assert out_loose(STEP_SOFTMAX_WRONG) != STEP_SOFTMAX_OUT


STEP_COST = '''def model_cost(layers, examples, batch, itemsize):
    """(parameters, training FLOPs, bytes): in * out + out per dense layer; 6 FLOPs per parameter per example; four copies of the parameters plus one batch of activations."""
    params = sum(i * o + o for i, o in zip(layers, layers[1:]))
    flops = 6 * params * examples
    bytes_needed = params * 4 * itemsize + batch * sum(layers) * itemsize
    return params, flops, bytes_needed


print(model_cost([4, 64, 32, 5], 400, 32, 4))
print(model_cost([4, 3, 2], 10, 2, 2))
'''
STEP_COST_STARTER = STEP_COST.replace("    flops = 6 * params * examples", "    flops = ... * params * examples").replace("    bytes_needed = params * 4 * itemsize", "    bytes_needed = params * ... * itemsize")
STEP_COST_WRONG = STEP_COST.replace("    flops = 6 * params * examples", "    flops = 2 * params * examples")
STEP_COST_OUT = out(STEP_COST)
assert STEP_COST_OUT == "(2565, 6156000, 54480)\n(23, 1380, 220)\n", STEP_COST_OUT
assert out(STEP_COST_WRONG) != STEP_COST_OUT

# =====================================================================================
# topic.yaml
# =====================================================================================

write(
    "topic.yaml",
    '''id: ml.m7.checkpoint
kind: checkpoint
status: ready
title: "Checkpoint 7: make it fast"
summary: "A slow, numerically shaky feature pipeline: profile it, vectorize the hot loop, fix the integer overflow and the float drift, keep a softmax finite, and estimate the cost of the model it feeds."
prerequisites: [ml.hw.floating-point, ml.hw.cost-of-a-model, ml.hw.profiling]
packages: [numpy]
estimated_minutes: 120
rev: 1
objectives:
  - "Profile a slow pipeline, find its hot loop and vectorize it, and show the gain with the doubling test and the profile."
  - "Find and fix three numeric bugs: an int8 column that wraps, a float32 sum that drifts, and a softmax that overflows to NaN."
  - "Estimate the parameters, FLOPs and memory of the model the pipeline feeds, and explain floating point and why vectorized code is fast."
prove:
  build: build-a-fast-pipeline
  debug: debug-a-shaky-pipeline
  explain:
    prompt: |
      Your fast pipeline is in code review. The reviewer asks four things. First: "the loop and the vectorized `nearest_centroid` give the same labels, and the doubling test says both are linear in the rows, so where does the hundred-fold difference come from, and how did the profile show it?" Second: "why did a float32 running total of a hundred thousand losses come out wrong, why is `0.1 + 0.2` not `0.3`, and what exactly went wrong in the softmax that printed NaN?" Third: "what did the int8 column do to the weekly clicks, and how do you choose a dtype for a column?" Fourth: "how did you estimate the model's parameters, FLOPs and memory, and why is the time you get from them optimistic?" In your own words, answer all four.
    rubric:
      - id: vectorized
        required: true
        description: "Both forms touch every row, so both are linear and the doubling test gives 2 for each; the difference is the constant: the loop pays the interpreter per element (bytecode, name lookups, type checks, boxing, a call per pair), the array operation pays once and runs a C loop, with SIMD where the data is contiguous. The profile shows it as one call to the per-pair function for every row and centroid before (8 for the build's 4 rows and 2 centroids, 2,000 in the worked example) and 0 after, with the same labels, and doubling the rows doubles the calls."
      - id: floats
        required: true
        description: "A float is sign, exponent and mantissa, a binary fraction times a power of two, so 0.1 is stored rounded and 0.1 + 0.2 lands a last digit from 0.3; compare with a tolerance. A float32 keeps about 7 digits, so once a running total is large, each small addition loses its low digits in the same direction and the drift accumulates: sum pairwise or accumulate in float64. exp(1000) overflows to inf and inf over inf is NaN; subtracting the row's maximum first leaves the ratios unchanged and every exponent at most 0."
      - id: integers
        required: true
        description: "An int8 holds -128 to 127 and wraps on overflow, so 20 times 7 is 140, which wraps to -116, silently for an array. Choose a dtype from the range the values can reach after every operation on them, not just the values stored: widen with astype before arithmetic, or store the column as int32 or int64; the saving of a narrow dtype is memory and bandwidth, which matters only for big columns."
      - id: cost
        required: true
        description: "Parameters are in times out plus out per dense layer; training costs about 6 FLOPs per parameter per example (2 forward, 4 backward); memory is four copies of the parameters for Adam (16 bytes each in float32) plus the activations of a batch. Time is FLOPs over the rate the machine sustains, and the peak rate is optimistic because of memory-bound steps, small matrix multiplies, data loading and Python between kernels; 30 to 50 percent of peak is a good run."
    model_answer: |
      The labels are the same because the arithmetic is the same: every row's squared distance to every centroid, and the smallest one wins. The doubling test says both forms are linear because both have to touch every row; doubling the rows doubles the calls in the loop and doubles the array operation's work, and no rewrite changes that. What changes is what each row costs. The loop asks the interpreter for one call per row and centroid, two thousand for four hundred rows, and for each one the interpreter decodes bytecode, looks up names, checks types, unpacks the numbers from their objects and allocates new ones; the array operation does its checks once and runs a loop written in C over contiguous bytes, several elements per instruction where the processor has SIMD. Same order, a constant tens to hundreds of times smaller. The profile showed it as counts, which are exact where times are not: two thousand calls to the per-pair function before, zero after, and the labels equal on the same input. The float trouble has one cause. A float is a sign, an exponent and a mantissa, a binary fraction times a power of two, so only fractions with a power-of-two denominator are exact; 0.1 is stored rounded, 0.2 too, and their sum lands a last digit away from the rounded 0.3, which is why floats are compared with a tolerance. A float32 keeps about seven digits, so once the running total of losses reached the thousands, each tenth added to it lost its low digits, always in the same direction, a hundred thousand times, and the mean came out at 0.09999 instead of 0.1. Summing as one array operation fixed it twice over: NumPy adds pairwise, so partners stay the same size, and the sum was accumulated in float64, which has digits to spare. The softmax went NaN because exp of a logit of a thousand is beyond the largest float, so it overflowed to infinity, and infinity divided by infinity is not a number. Subtracting the row's largest logit before the exponential changes nothing in the result, since the common factor cancels in the ratio, and makes every exponent at most zero, so every term is at most one. The int8 column held each day's clicks in one byte, which runs from -128 to 127, and multiplying by seven pushed 20 to 140, which wrapped around to -116, with no error, because array arithmetic in a fixed width wraps silently. The dtype of a column has to hold not the values stored but every value an operation on them can reach; widening with astype to int64 before the multiplication fixed it, and storing the column as int32 or int64 in the first place would have cost a few more bytes per row, which only matters for columns of millions. For the model, I counted in times out plus out for each dense layer, 2,565 parameters for the layer sizes [4, 64, 32, 5]; training costs about six FLOPs per parameter per example, two for the forward pass and four for the backward, so 6.2 million FLOPs for one pass over the 400 rows; and memory is four copies of the parameters for Adam, weights, gradients and two moments at four bytes each, plus the activations of a batch. Dividing FLOPs by a GPU's peak rate gives a time that is too hopeful, because a real step reaches perhaps a third to a half of peak: the elementwise work is memory-bound, the matrix multiplies of a small model don't fill the chip, the data has to be loaded and moved, and Python runs between the kernels.
# For a learner who's stuck on the build (ADR-0012): a solved sibling, the
# build in steps with hints, then fresh versions.
unstuck:
  example: example-a-pipeline-made-fast
  steps: [step-vectorize-nearest, step-widen-the-column, step-sum-in-float64, step-stable-softmax, step-count-the-model]
  versions: [build-a-fast-pipeline-sensors, build-a-fast-pipeline-tickets]
''',
)

# =====================================================================================
# the build, and its two versions
# =====================================================================================

TEST_SKILLS = '''# Every test names the module skills it checks (ADR-0012), so a failed test
# says which topics to revisit.
test_skills:
  test_the_output: [ml.hw.vectorization/broadcasting, ml.hw.floating-point/special, ml.hw.cost-of-a-model/parameters, ml.hw.profiling/cprofile]
  test_standardize: [ml.hw.vectorization/broadcasting, ml.hw.vectorization/interpreter-cost]
  test_nearest_centroid: [ml.hw.vectorization/broadcasting, ml.hw.vectorization/interpreter-cost, ml.hw.profiling/decide]
  test_weekly: [ml.hw.bits-and-integers/fixed-width, ml.hw.bits-and-integers/sizing]
  test_mean_loss: [ml.hw.floating-point/accumulation, ml.hw.vectorization/dependence]
  test_softmax: [ml.hw.floating-point/special, ml.hw.vectorization/broadcasting]
  test_model_cost: [ml.hw.cost-of-a-model/parameters, ml.hw.cost-of-a-model/flops, ml.hw.cost-of-a-model/memory]
  test_calls_to: [ml.hw.profiling/cprofile, ml.hw.profiling/decide, ml.hw.vectorization/doubling-test]
'''

FUNCTIONS_PROSE = '''  **Write seven functions**; none of the pipeline's own pieces may loop over the data in Python:

  - `standardize(X)`: each column minus its mean, divided by its standard deviation; a column with no spread becomes zeros rather than NaN.
  - `nearest_centroid(X, centroids)`: a list with the index of the nearest centroid (a reference point, the centre of a cluster) for every row of `X`, by squared distance, the first on a tie; broadcasting, not a loop over rows.
  - `weekly(clicks)`: seven times the daily clicks, in an integer type wide enough to hold them whatever dtype the column arrived in (an int8 column must not wrap).
  - `mean_loss(losses)`: the mean as a float, summed as one array operation and accumulated in float64, so a hundred thousand float32 values don't drift.
  - `softmax(logits)`: the row-wise softmax of a 2-D array, with each row's largest logit subtracted before the exponential so that a logit of 1,000 doesn't overflow to NaN.
  - `model_cost(layers, examples, batch, itemsize)`: the tuple `(parameters, training FLOPs, bytes)` of a dense network: `in * out + out` per layer; 6 FLOPs per parameter per example; four copies of the parameters (weights, gradients, two Adam moments) plus one batch of activations (`sum(layers)` values per example), all at `itemsize` bytes.
  - `calls_to(function, name, *args)`: how many times the function called `name` runs while `function(*args)` runs, counted with `cProfile` as Reading a profiler did: the way to find the hot loop by its call count, and to prove that the vectorized version makes none.
'''


def build_test(printed: str) -> str:
    return f'''import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


{WATCHED}

def test_the_output():
    """Prints the six lines."""
    assert run() == {printed!r}


def test_standardize():
    """Every column ends at mean 0 and spread 1, a constant column becomes zeros, and no Python loop touches the array."""
    standardize = function("standardize")
    Z = standardize(np.array([[1.0, 100.0, 3.0], [2.0, 50.0, 3.0], [6.0, 0.0, 3.0], [7.0, 10.0, 3.0]]))
    assert np.allclose(Z[:, :2].mean(axis=0), 0) and np.allclose(Z[:, :2].std(axis=0), 1)
    assert not np.isnan(Z).any() and np.allclose(Z[:, 2], 0)
    standardize(watched([[1.0, 2.0], [3.0, 5.0], [5.0, 11.0]]))
    assert Watched.iterations == 0 and Watched.elements == 0


def test_nearest_centroid():
    """Agrees with a plain loop on 60 random rows and 4 centroids, keeps the first centroid on a tie, and never iterates in Python."""
    nearest_centroid = function("nearest_centroid")
    rng = np.random.default_rng(7)
    X = rng.standard_normal((60, 3))
    centroids = rng.standard_normal((4, 3)) * 2
    expected = []
    for row in X:
        distances = [float(((row - c) ** 2).sum()) for c in centroids]
        expected.append(distances.index(min(distances)))
    assert list(nearest_centroid(X, centroids)) == expected
    assert list(nearest_centroid(np.array([[0.0, 0.0]]), np.array([[1.0, 0.0], [-1.0, 0.0]]))) == [0]
    nearest_centroid(watched(X), centroids)
    assert Watched.iterations == 0 and Watched.elements == 0


def test_weekly():
    """An int8 column of 127 gives 889, a uint8 column of 255 gives 1785, and the result holds them."""
    weekly = function("weekly")
    assert list(weekly(np.array([127, 20], dtype=np.int8))) == [889, 140]
    assert list(weekly(np.array([255, 1], dtype=np.uint8))) == [1785, 7]
    assert weekly(np.array([1], dtype=np.int8)).dtype.itemsize >= 4


def test_mean_loss():
    """A hundred thousand float32 tenths average to 0.1 within a millionth, with no Python loop over them."""
    mean_loss = function("mean_loss")
    assert abs(mean_loss(np.full(100_000, 0.1, dtype=np.float32)) - 0.1) < 1e-6
    assert abs(mean_loss(np.array([1.0, 2.0, 6.0])) - 3.0) < 1e-12
    mean_loss(watched([0.5, 1.5, 2.5]))
    assert Watched.iterations == 0 and Watched.elements == 0


def test_softmax():
    """Logits of 5,000 and of -5,000 give finite rows that sum to 1 with the right ratios, and no Python loop runs."""
    softmax = function("softmax")
    P = softmax(np.array([[5000.0, 5001.0, 4999.0], [-5000.0, -5001.0, -5000.0], [0.0, 0.0, 0.0]]))
    assert not np.isnan(P).any() and np.allclose(P.sum(axis=1), 1)
    assert np.isclose(P[0, 1] / P[0, 0], np.e) and np.allclose(P[2], 1 / 3)
    softmax(watched([[1.0, 2.0], [3.0, 1.0]]))
    assert Watched.iterations == 0 and Watched.elements == 0


def test_model_cost():
    """[4, 3, 2] is 23 parameters; 10 examples cost 1,380 FLOPs; a batch of 2 in float16 needs 23 * 8 + 2 * 9 * 2 bytes."""
    model_cost = function("model_cost")
    assert tuple(model_cost([4, 3, 2], 10, 2, 2)) == (23, 1380, 23 * 8 + 2 * 9 * 2)
    assert tuple(model_cost([5, 1], 1, 1, 4)) == (6, 36, 6 * 16 + 6 * 4)


def test_calls_to():
    """Counts 12 calls to a leaf through two levels of functions, 3 to the middle one, and 0 to a function that never runs."""
    calls_to = function("calls_to")

    def leaf():
        return 1

    def inner():
        total = 0
        for _ in range(4):
            total += leaf()
        return total

    def outer(n):
        total = 0
        for _ in range(n):
            total += inner()
        return total

    assert calls_to(outer, "leaf", 3) == 12 and calls_to(outer, "inner", 3) == 3 and calls_to(outer, "never", 3) == 0
'''


def typed_in(printed: str) -> str:
    return (
        "import numpy as np\n\n\ndef standardize(X):\n    return X\n\n\ndef nearest_centroid(X, centroids):\n    return [0]\n\n\ndef calls_to(function, name, *args):\n    return 0\n\n\ndef weekly(clicks):\n    return clicks\n\n\ndef mean_loss(losses):\n    return 0.1\n\n\ndef softmax(logits):\n    return logits\n\n\ndef model_cost(layers, examples, batch, itemsize):\n    return (0, 0, 0)\n\n\n"
        + "".join(f"print({line!r})\n" for line in printed.splitlines())
    )


write(
    "exercises/build-a-fast-pipeline/exercise.yaml",
    f'''id: build-a-fast-pipeline
stage: build
rev: 1
title: "Make it fast"
prompt: |
  Starting from a blank editor, build the pieces of a feature pipeline the way this module says to: vectorized where the work is independent, in a dtype that holds the numbers, summed so that rounding doesn't pile up, and with its softmax kept finite; then count what the model it feeds will cost.

{FUNCTIONS_PROSE}
  **Then paste the pipeline's slow first version of the nearest-centroid step, the hot loop you are replacing, and the data, and print:**

  ```python
{block(PASTES["build-a-fast-pipeline"], "  ")}  ```

  ```
{block(BUILD_OUTS["build-a-fast-pipeline"])}  ```

  Both columns standardize to the same values, since one is ten times the other; three rows sit nearer the first centroid; the slow version calls `distance_squared` 8 times for 4 rows and 2 centroids, the vectorized one 0 times, and doubling the rows doubles the calls to 16; an int8 column of 20, 50, 100 and 120 clicks gives 140, 350, 700 and 840 instead of wrapping; a hundred thousand tenths average to 0.1; a logit of 1,000 gives the same probabilities as a logit of 1, since only the difference matters; and the network with layer sizes `[4, 64, 32, 5]`, three dense layers, is 2,565 parameters.

  The checks hand `standardize`, `nearest_centroid`, `mean_loss` and `softmax` an array that counts Python-level iteration and single-element reads and expect none; compare `nearest_centroid` with a plain loop on random rows; feed `weekly` an int8 127 and a uint8 255; hold `mean_loss` to a millionth on a hundred thousand float32 tenths; give `softmax` logits of 5,000 and -5,000; count a tiny network by hand; and check the calls `calls_to` reports through two levels of functions.
{TEST_SKILLS}''',
)
write("exercises/build-a-fast-pipeline/starter.py", "")
write("exercises/build-a-fast-pipeline/solution.py", BUILDS["build-a-fast-pipeline"])
write("exercises/build-a-fast-pipeline/test_exercise.py", build_test(BUILD_OUTS["build-a-fast-pipeline"]))
for key, code in variants(BUILDS["build-a-fast-pipeline"]).items():
    write(f"exercises/build-a-fast-pipeline/wrong/{key}.py", code)
write("exercises/build-a-fast-pipeline/wrong/typed-in.py", typed_in(BUILD_OUTS["build-a-fast-pipeline"]))

write(
    "exercises/build-a-fast-pipeline-sensors/exercise.yaml",
    f'''id: build-a-fast-pipeline-sensors
stage: build
rev: 1
title: "Make it fast: sensor readings"
prompt: |
  Starting from a blank editor, build the same six pieces for a different pipeline: temperature and humidity readings from two rooms, a column of samples per day, a hundred thousand losses, a row of three logits, and a smaller model.

{FUNCTIONS_PROSE}
  **Then paste the pipeline's slow first version of the nearest-centroid step, the hot loop you are replacing, and the data, and print:**

  ```python
{block(PASTES["build-a-fast-pipeline-sensors"], "  ")}  ```

  ```
{block(BUILD_OUTS["build-a-fast-pipeline-sensors"])}  ```

  The three cool, dry readings sit nearer the first centroid and the two warm, humid ones nearer the second; the slow version calls `distance_squared` 10 times for 5 readings and 2 centroids, the vectorized one 0 times, and doubling the readings doubles the calls to 20; an int8 column of 24, 48, 96 and 120 samples gives 168, 336, 672 and 840 instead of wrapping; a hundred thousand tenths average to 0.1; the three logits of 2,000, 2,000 and 2,001 give 0.212, 0.212 and 0.576, the same as logits of 0, 0 and 1 would, since only the differences matter; and the network with layer sizes `[2, 16, 8, 3]`, three dense layers, is 211 parameters.

  The checks hand `standardize`, `nearest_centroid`, `mean_loss` and `softmax` an array that counts Python-level iteration and single-element reads and expect none; compare `nearest_centroid` with a plain loop on random rows; feed `weekly` an int8 127 and a uint8 255; hold `mean_loss` to a millionth on a hundred thousand float32 tenths; give `softmax` logits of 5,000 and -5,000; count a tiny network by hand; and check the calls `calls_to` reports through two levels of functions.
{TEST_SKILLS}''',
)
write("exercises/build-a-fast-pipeline-sensors/starter.py", "")
write("exercises/build-a-fast-pipeline-sensors/solution.py", BUILDS["build-a-fast-pipeline-sensors"])
write("exercises/build-a-fast-pipeline-sensors/test_exercise.py", build_test(BUILD_OUTS["build-a-fast-pipeline-sensors"]))
for key, code in variants(BUILDS["build-a-fast-pipeline-sensors"]).items():
    write(f"exercises/build-a-fast-pipeline-sensors/wrong/{key}.py", code)
write("exercises/build-a-fast-pipeline-sensors/wrong/typed-in.py", typed_in(BUILD_OUTS["build-a-fast-pipeline-sensors"]))

write(
    "exercises/build-a-fast-pipeline-tickets/exercise.yaml",
    f'''id: build-a-fast-pipeline-tickets
stage: build
rev: 1
title: "Make it fast: support tickets"
prompt: |
  Starting from a blank editor, build the same six pieces for a different pipeline: support tickets described by their word count and the number of replies, a column of tickets per day, fifty thousand losses, two rows of logits, and a smaller model.

{FUNCTIONS_PROSE}
  **Then paste the pipeline's slow first version of the nearest-centroid step, the hot loop you are replacing, and the data, and print:**

  ```python
{block(PASTES["build-a-fast-pipeline-tickets"], "  ")}  ```

  ```
{block(BUILD_OUTS["build-a-fast-pipeline-tickets"])}  ```

  The three short tickets sit nearer the first centroid and the three long ones nearer the second; the slow version calls `distance_squared` 12 times for 6 tickets and 2 centroids, the vectorized one 0 times, and doubling the tickets doubles the calls to 24; an int8 column of 10, 30, 90 and 127 tickets gives 70, 210, 630 and 889 instead of wrapping; fifty thousand values of 0.3 average to 0.3; logits of -1,500 and -1,499 give the same probabilities as 0 and 1, and two equal logits give a half each; and the network with layer sizes `[2, 32, 4]`, two dense layers, is 228 parameters.

  The checks hand `standardize`, `nearest_centroid`, `mean_loss` and `softmax` an array that counts Python-level iteration and single-element reads and expect none; compare `nearest_centroid` with a plain loop on random rows; feed `weekly` an int8 127 and a uint8 255; hold `mean_loss` to a millionth on a hundred thousand float32 tenths; give `softmax` logits of 5,000 and -5,000; count a tiny network by hand; and check the calls `calls_to` reports through two levels of functions.
{TEST_SKILLS}''',
)
write("exercises/build-a-fast-pipeline-tickets/starter.py", "")
write("exercises/build-a-fast-pipeline-tickets/solution.py", BUILDS["build-a-fast-pipeline-tickets"])
write("exercises/build-a-fast-pipeline-tickets/test_exercise.py", build_test(BUILD_OUTS["build-a-fast-pipeline-tickets"]))
for key, code in variants(BUILDS["build-a-fast-pipeline-tickets"]).items():
    write(f"exercises/build-a-fast-pipeline-tickets/wrong/{key}.py", code)
write("exercises/build-a-fast-pipeline-tickets/wrong/typed-in.py", typed_in(BUILD_OUTS["build-a-fast-pipeline-tickets"]))

# =====================================================================================
# the debug
# =====================================================================================

write(
    "exercises/debug-a-shaky-pipeline/exercise.yaml",
    f'''id: debug-a-shaky-pipeline
stage: debug
rev: 1
title: "Three numeric bugs in a pipeline"
prompt: |
  This is the pipeline's numeric core on its data, and it should print:

  ```
{block(DEBUG_OUT)}  ```

  It has three bugs, one in each function. Run it:

  1. **The weekly clicks are negative:** `[-116, 94, -68, 72]`. The clicks column is an **int8**, one byte per value with a range of -128 to 127, and `clicks * 7` stays int8: 20 times 7 is 140, which wraps round to -116, silently, because array arithmetic in a fixed width wraps. Widen the column before multiplying (`astype(np.int64)`).
  2. **The mean loss is `0.099986`, not `0.1`:** `mean_loss` adds a hundred thousand float32 tenths to a float32 running total, one at a time. Once the total is in the thousands, each tenth's low bits are dropped in the same direction every time, and the drift is visible in the fifth digit. It is also the pipeline's hot loop. Sum as one array operation (NumPy adds pairwise) and accumulate in float64 (`sum(dtype=np.float64)`).
  3. **The first softmax row is `[nan, nan]`:** `exp(1000)` is beyond the largest float, so it overflows to infinity, and infinity over infinity is NaN. Subtract each row's largest logit before the exponential (`logits.max(axis=1, keepdims=True)`); the ratios don't change and every exponent is at most 0.

  The checks also feed `weekly` an int8 127, hold `mean_loss` to a millionth on two hundred thousand float32 tenths with no Python loop over them, and give `softmax` logits of 5,000 and -5,000.
# Every test names the module skills it checks (ADR-0012), so a failed test
# says which topics to revisit.
test_skills:
  test_the_output: [ml.hw.bits-and-integers/fixed-width, ml.hw.floating-point/accumulation, ml.hw.floating-point/special]
  test_weekly_widens: [ml.hw.bits-and-integers/fixed-width, ml.hw.bits-and-integers/sizing]
  test_mean_does_not_drift: [ml.hw.floating-point/accumulation, ml.hw.vectorization/dependence, ml.hw.profiling/decide]
  test_softmax_stays_finite: [ml.hw.floating-point/special]
''',
)
write("exercises/debug-a-shaky-pipeline/starter.py", DEBUG_STARTER)
write("exercises/debug-a-shaky-pipeline/solution.py", DEBUG_SOLUTION)
write(
    "exercises/debug-a-shaky-pipeline/test_exercise.py",
    f'''import numpy as np

from checks import function, run


{WATCHED}
EXPECTED = {DEBUG_OUT!r}


def test_the_output():
    """Prints the widened weekly clicks, a mean of 0.1 and two finite softmax rows."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\\n{{EXPECTED}}\\nYour program printed:\\n{{printed}}"


def test_weekly_widens():
    """An int8 127 gives 889 and a uint8 255 gives 1785."""
    weekly = function("weekly")
    assert list(weekly(np.array([127, 3], dtype=np.int8))) == [889, 21]
    assert list(weekly(np.array([255], dtype=np.uint8))) == [1785]


def test_mean_does_not_drift():
    """Two hundred thousand float32 tenths average to 0.1 within a millionth, with no Python loop over the array."""
    mean_loss = function("mean_loss")
    assert abs(mean_loss(np.full(200_000, 0.1, dtype=np.float32)) - 0.1) < 1e-6
    mean_loss(watched([0.5, 1.5, 2.5]))
    assert Watched.iterations == 0 and Watched.elements == 0


def test_softmax_stays_finite():
    """Logits of 5,000 and of -5,000 give finite rows that sum to 1."""
    softmax = function("softmax")
    P = softmax(np.array([[5000.0, 5001.0], [-5000.0, -5001.0]]))
    assert not np.isnan(P).any() and np.allclose(P.sum(axis=1), 1) and np.isclose(P[0, 1] / P[0, 0], np.e)
''',
)
for key, code in DEBUG_WRONGS.items():
    write(f"exercises/debug-a-shaky-pipeline/wrong/{key}.py", code)
write(
    "exercises/debug-a-shaky-pipeline/wrong/typed-in.py",
    "import numpy as np\n\n\ndef weekly(clicks):\n    return clicks\n\n\ndef mean_loss(losses):\n    return 0.1\n\n\ndef softmax(logits):\n    return logits\n\n\n" + "".join(f"print({line!r})\n" for line in DEBUG_OUT.splitlines()),
)

# =====================================================================================
# the worked example
# =====================================================================================

write(
    "exercises/example-a-pipeline-made-fast/exercise.yaml",
    f'''id: example-a-pipeline-made-fast
stage: worked_example
rev: 1
title: "A pipeline made fast"
prompt: |
  The checkpoint's four fixes, each shown before and after on a small pipeline: the hot loop found by its call count and vectorized, an int8 column widened, a float32 running total summed in float64, a softmax kept finite; then the cost of the model the pipeline feeds. Press **Run**, then read how each part works; the checkpoint is the same fixes on your own code, with the checks counting what they cost.
steps:
  - label: "The hot loop, found by counting"
    lines: "{ln('def distance_squared')}-{ln('the loop: ')}"
    note: "The loop version calls `distance_squared` once per row and centroid (a reference point, the centre of a cluster): 2,000 calls for 400 rows. The vectorized version makes every row-centroid difference in one broadcast, `(400, 1, 4)` against `(1, 5, 4)`, sums the squares along the last axis and takes `argmin` along the centroids: 0 calls, and the same labels. The profile is read in code, as Reading a profiler does, so the counts are exact."
  - label: "The doubling test on counts"
    lines: "{ln('_, doubled = profile')}-{ln('doubling the rows')}"
    note: "Doubling the rows doubles the calls: the loop is linear in the rows, and so is the array operation, since both must touch every row. Vectorizing can't change that; it changes what each row costs, the constant, by a factor of tens to hundreds, because the interpreter's per-element work is gone."
  - label: "An int8 column that wraps"
    lines: "{ln('clicks = np.array')}-{ln('weekly clicks from an int8 column')}"
    note: "An int8 holds -128 to 127; `clicks * 7` stays int8, so 140 wraps to -116 with no error. Widening the column to int64 first gives the real numbers. A column's dtype must hold every value an operation on it can reach, not just the values stored."
  - label: "A running total that drifts"
    lines: "{ln('losses = np.full')}-{ln('mean loss from a float32 running total')}"
    note: "A hundred thousand float32 tenths added one at a time to a float32 total come out at 0.099986 on average: once the total is in the thousands, each tenth's low bits fall off in the same direction every time. Summed as one array operation, NumPy adds pairwise, and with `dtype=np.float64` the accumulation has digits to spare: 0.100000. It is also the pipeline's second hot loop, gone."
  - label: "A softmax that overflows"
    lines: "{ln('logits = np.array')}-{ln('softmax of a logit of 1,000')}"
    note: "`exp(1000)` overflows to infinity and infinity over infinity is NaN (the `errstate` only silences the warning so the result can be shown). Subtracting each row's largest logit first leaves the ratios, and so the probabilities, unchanged, and makes every exponent at most 0: finite rows that sum to 1."
  - label: "What the model will cost"
    lines: "{ln('LAYERS = [4, 64, 32, 5]')}-{ln('the model the pipeline feeds')}"
    note: "Parameters are `in * out + out` per dense layer, 2,565 here; training costs about 6 FLOPs per parameter per example, 6.2 million for one pass over the 400 rows; and memory is four copies of the parameters (weights, gradients, two Adam moments, 16 bytes each in float32) plus one batch of activations. The time those FLOPs take on a machine is optimistic by the utilization it really reaches."
''',
)
write("exercises/example-a-pipeline-made-fast/solution.py", EXAMPLE)
write(
    "exercises/example-a-pipeline-made-fast/test_exercise.py",
    f'''from checks import run


def test_the_walkthrough():
    """Prints the call counts, the doubling test, the int8 column, the drift, the softmax and the model's cost."""
    assert run() == {EXAMPLE_OUT!r}
''',
)

# =====================================================================================
# the steps
# =====================================================================================

write(
    "exercises/step-vectorize-nearest/exercise.yaml",
    f'''id: step-vectorize-nearest
stage: fill_in
rev: 1
title: "Step 1: vectorize the hot loop"
prompt: |
  The first piece of the checkpoint. `nearest_centroid` makes every row-centroid difference in one broadcast, `X[:, None, :] - centroids[None, :, :]`, a `(rows, centroids, features)` array. Replace each `...` with the axis to sum the squares along and the axis to take the `argmin` along, so the program prints the index of the nearest centroid for each of four rows:

  ```
{block(STEP_NEAREST_OUT)}  ```
hints:
  - "The squared differences have shape `(rows, centroids, features)`; the distance sums over the features, the last axis, which is axis 2."
  - "After the sum, the array is `(rows, centroids)`; the nearest centroid for each row is the smallest along axis 1."
''',
)
write("exercises/step-vectorize-nearest/starter.py", STEP_NEAREST_STARTER)
write("exercises/step-vectorize-nearest/solution.py", STEP_NEAREST)
write(
    "exercises/step-vectorize-nearest/test_exercise.py",
    f'''import numpy as np

from checks import function, run


{WATCHED}

def test_the_output():
    """Prints the four labels."""
    printed = run()
    assert printed == {STEP_NEAREST_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_agrees_with_a_loop():
    """Matches a plain loop on 40 random rows and 3 centroids, and never iterates over the rows in Python."""
    nearest_centroid = function("nearest_centroid")
    rng = np.random.default_rng(3)
    X = rng.standard_normal((40, 2))
    centroids = rng.standard_normal((3, 2)) * 2
    expected = []
    for row in X:
        distances = [float(((row - c) ** 2).sum()) for c in centroids]
        expected.append(distances.index(min(distances)))
    assert list(nearest_centroid(X, centroids)) == expected
    nearest_centroid(watched(X), centroids)
    assert Watched.iterations == 0 and Watched.elements == 0
''',
)
write("exercises/step-vectorize-nearest/wrong/sums-the-wrong-axis.py", STEP_NEAREST_WRONG)
write(
    "exercises/step-vectorize-nearest/wrong/typed-in.py",
    "def nearest_centroid(X, centroids):\n    return [0, 1, 1, 0]\n\n\n" + "".join(f"print({line!r})\n" for line in STEP_NEAREST_OUT.splitlines()),
)

write(
    "exercises/step-widen-the-column/exercise.yaml",
    f'''id: step-widen-the-column
stage: fill_in
rev: 1
title: "Step 2: widen the column"
prompt: |
  The clicks column arrives as int8, one byte per value, and seven times 20 doesn't fit in a byte. Replace the `...` with the dtype to widen the column to before multiplying, so the program prints the real weekly clicks and the result's dtype:

  ```
{block(STEP_WIDEN_OUT)}  ```
hints:
  - "`astype` makes a copy in another dtype; the multiplication then happens in that width."
  - "`np.int64` holds anything a count of clicks can reach; `np.int32` would do here too, but the output names int64."
''',
)
write("exercises/step-widen-the-column/starter.py", STEP_WIDEN_STARTER)
write("exercises/step-widen-the-column/solution.py", STEP_WIDEN)
write(
    "exercises/step-widen-the-column/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints the four weekly counts and int64."""
    printed = run()
    assert printed == {STEP_WIDEN_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_the_edge():
    """An int8 127 gives 889 and a uint8 255 gives 1785."""
    weekly = function("weekly")
    assert list(weekly(np.array([127], dtype=np.int8))) == [889]
    assert list(weekly(np.array([255], dtype=np.uint8))) == [1785]
''',
)
write("exercises/step-widen-the-column/wrong/still-a-byte.py", STEP_WIDEN_WRONG)
write(
    "exercises/step-widen-the-column/wrong/typed-in.py",
    "def weekly(clicks):\n    return clicks\n\n\n" + "".join(f"print({line!r})\n" for line in STEP_WIDEN_OUT.splitlines()),
)

write(
    "exercises/step-sum-in-float64/exercise.yaml",
    f'''id: step-sum-in-float64
stage: fill_in
rev: 1
title: "Step 3: sum in float64"
prompt: |
  A hundred thousand float32 losses, averaged. The running total that drifted is gone; `sum` is one array operation, and its `dtype` argument says what to accumulate in. Replace the `...` so the program prints:

  ```
{block(STEP_SUM_OUT)}  ```
hints:
  - "`np.float64` has 53 significant bits against float32's 24; the low bits of each tenth survive the addition."
  - "The array itself stays float32; only the accumulator is wider."
''',
)
write("exercises/step-sum-in-float64/starter.py", STEP_SUM_STARTER)
write("exercises/step-sum-in-float64/solution.py", STEP_SUM)
write(
    "exercises/step-sum-in-float64/test_exercise.py",
    f'''import numpy as np

from checks import function, run


{WATCHED}

def test_the_output():
    """Prints 0.1."""
    printed = run()
    assert printed == {STEP_SUM_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_no_drift_and_no_loop():
    """Two hundred thousand tenths average to 0.1 within a millionth, three values average to 3, and no Python loop runs."""
    mean_loss = function("mean_loss")
    assert abs(mean_loss(np.full(200_000, 0.1, dtype=np.float32)) - 0.1) < 1e-6
    assert abs(mean_loss(np.array([1.0, 2.0, 6.0])) - 3.0) < 1e-12
    mean_loss(watched([0.5, 1.5, 2.5]))
    assert Watched.iterations == 0 and Watched.elements == 0
''',
)
write("exercises/step-sum-in-float64/wrong/a-running-total.py", STEP_SUM_WRONG)
write(
    "exercises/step-sum-in-float64/wrong/typed-in.py",
    "def mean_loss(losses):\n    return 0.1\n\n\n" + "".join(f"print({line!r})\n" for line in STEP_SUM_OUT.splitlines()),
)

write(
    "exercises/step-stable-softmax/exercise.yaml",
    f'''id: step-stable-softmax
stage: fill_in
rev: 1
title: "Step 4: keep the softmax finite"
prompt: |
  `exp(1000)` overflows, so the softmax of a row with a logit of 1,000 comes out NaN unless something is subtracted from every logit first. Replace the `...` with each row's largest logit, kept as a column so that it broadcasts across the row, so the program prints:

  ```
{block(STEP_SOFTMAX_OUT)}  ```
hints:
  - "`logits.max(axis=1, keepdims=True)` is one maximum per row, shaped `(rows, 1)`, which broadcasts across each row."
  - "Subtracting the same number from every logit in a row leaves the ratios of the exponentials unchanged, so the probabilities are the same; only the overflow goes."
''',
)
write("exercises/step-stable-softmax/starter.py", STEP_SOFTMAX_STARTER)
write("exercises/step-stable-softmax/solution.py", STEP_SOFTMAX)
write(
    "exercises/step-stable-softmax/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints two finite rows."""
    printed = run()
    assert printed == {STEP_SOFTMAX_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_extremes():
    """Logits of 5,000 and of -5,000 give finite rows that sum to 1."""
    softmax = function("softmax")
    P = softmax(np.array([[5000.0, 5001.0], [-5000.0, -5001.0]]))
    assert not np.isnan(P).any() and np.allclose(P.sum(axis=1), 1)
''',
)
write("exercises/step-stable-softmax/wrong/still-overflows.py", STEP_SOFTMAX_WRONG)
write(
    "exercises/step-stable-softmax/wrong/typed-in.py",
    "def softmax(logits):\n    return logits\n\n\n" + "".join(f"print({line!r})\n" for line in STEP_SOFTMAX_OUT.splitlines()),
)


write(
    "exercises/step-count-the-model/exercise.yaml",
    f'''id: step-count-the-model
stage: fill_in
rev: 1
title: "Step 5: count the model"
prompt: |
  The model the pipeline feeds, counted as Counting a model's cost did: parameters are `in * out + out` per dense layer, a training step costs about 6 FLOPs per parameter per example, and training needs four copies of the parameters (weights, gradients, two Adam moments) plus one batch of activations. Replace each `...` so the program prints the cost of the pipeline's model and of a tiny one:

  ```
{block(STEP_COST_OUT)}  ```
hints:
  - "Forward is 2 FLOPs per parameter and backward about 4: 6 in all, times the examples."
  - "Weights, gradients, first moment, second moment: four arrays the size of the parameters, each `itemsize` bytes per value."
''',
)
write("exercises/step-count-the-model/starter.py", STEP_COST_STARTER)
write("exercises/step-count-the-model/solution.py", STEP_COST)
write(
    "exercises/step-count-the-model/test_exercise.py",
    f'''from checks import function, run


def test_the_output():
    """Prints the two cost tuples."""
    printed = run()
    assert printed == {STEP_COST_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_another_network():
    """A single layer from 5 to 1, one example, a batch of 1 in float32: 6 parameters, 36 FLOPs, 6 * 16 + 6 * 4 bytes."""
    model_cost = function("model_cost")
    assert tuple(model_cost([5, 1], 1, 1, 4)) == (6, 36, 6 * 16 + 6 * 4)
''',
)
write("exercises/step-count-the-model/wrong/forward-only.py", STEP_COST_WRONG)
write(
    "exercises/step-count-the-model/wrong/typed-in.py",
    "def model_cost(layers, examples, batch, itemsize):\n    return (2565, 6156000, 54480)\n\n\n" + "".join(f"print({line!r})\n" for line in STEP_COST_OUT.splitlines()),
)

print("ml.m7.checkpoint written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
