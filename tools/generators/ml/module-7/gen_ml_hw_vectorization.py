"""Writes the topic ml.hw.vectorization (Module 7's fourth topic). Run from
the repository root under uv (python -m uv run python <this file>), so every
program's expected output is captured from CPython rather than typed in.
Timings appear only in the worked example and are checked by shape; every
pinned number is a count, a shape or a stride, and every array has a named
dtype so that 32-bit Pyodide prints the same thing. Files are written as
bytes with LF endings."""

import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path("content/topics/ml.hw.vectorization")


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


# An array that counts Python-level iteration and element-by-element access.
# The tests hand it to a function that should be vectorized and expect zero.
WATCHED = '''class Watched(np.ndarray):
    """An array that counts how often Python iterates over it or reads single elements from it."""

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
        Watched.elements += self.size
        return super().tolist()


def watched(a):
    """A counting view of a, with the counts reset."""
    Watched.iterations = 0
    Watched.elements = 0
    return np.asarray(a, dtype=np.float64).view(Watched)
'''

# --- the worked example ----------------------------------------------------------------------

EXAMPLE = '''import time

import numpy as np

rng = np.random.default_rng(0)
X = rng.standard_normal((2000, 8))
w = rng.standard_normal(8)


def predict_loop(X, w):
    """One row at a time, one element at a time: what every Python loop over an array does."""
    out = []
    for row in X:
        total = 0.0
        for x, weight in zip(row, w):
            total += x * weight
        out.append(total)
    return np.array(out)


def predict_vectorized(X, w):
    return X @ w


print("the loop and X @ w agree:", np.allclose(predict_loop(X, w), predict_vectorized(X, w)))

stretched = np.broadcast_to(w, X.shape)
print("w stretched to", stretched.shape, "has strides", stretched.strides, "| (X * w).sum(axis=1) agrees with X @ w:", np.allclose((X * w).sum(axis=1), X @ w))
print(f"the loop asks the interpreter for {X.size:,} multiplications and {X.size:,} additions, one at a time; X @ w asks once")


def seconds(function, *args, repeats=1):
    start = time.perf_counter()
    for _ in range(repeats):
        function(*args)
    return (time.perf_counter() - start) / repeats


def ratio(a, b):
    return f"{a / b:.1f}" if b > 0 else "n/a"


double = np.vstack([X, X])
loop_small, loop_double = seconds(predict_loop, X, w, repeats=5), seconds(predict_loop, double, w, repeats=5)
fast_small, fast_double = seconds(predict_vectorized, X, w, repeats=200), seconds(predict_vectorized, double, w, repeats=200)
print(f"loop: {loop_small * 1000:.1f} ms for 2,000 rows, {loop_double * 1000:.1f} ms for 4,000; ratio {ratio(loop_double, loop_small)}")
print(f"X @ w: {fast_small * 1000:.3f} ms for 2,000 rows, {fast_double * 1000:.3f} ms for 4,000; ratio {ratio(fast_double, fast_small)}")
print(f"at 4,000 rows the vectorized form is {ratio(loop_double, fast_double)} times faster")


def moving_average(X, alpha):
    """Each row's state depends on the row before, so the rows stay a loop; the 8 columns are one vector operation."""
    state = np.zeros(X.shape[1])
    out = np.empty_like(X)
    for t in range(len(X)):
        state = alpha * X[t] + (1 - alpha) * state
        out[t] = state
    return out


smoothed = moving_average(X, 0.1)
print(f"the moving average: {len(X):,} steps that each need the last, so {len(X):,} vector operations instead of {X.size:,} scalar ones")
print("a running total has a library form, np.cumsum:", np.allclose(np.cumsum(X[:, 0]), [X[: t + 1, 0].sum() for t in range(len(X))]))
'''
EXAMPLE_OUT = out(EXAMPLE)
print("example:\n" + EXAMPLE_OUT)
EX = EXAMPLE_OUT.splitlines()
assert len(EX) == 8, EX
TIMING_SHAPES = {
    3: r"loop: [0-9]+\.[0-9] ms for 2,000 rows, [0-9]+\.[0-9] ms for 4,000; ratio (?:[0-9]+\.[0-9]|n/a)",
    4: r"X @ w: [0-9]+\.[0-9]{3} ms for 2,000 rows, [0-9]+\.[0-9]{3} ms for 4,000; ratio (?:[0-9]+\.[0-9]|n/a)",
    5: r"at 4,000 rows the vectorized form is (?:[0-9]+\.[0-9]|n/a) times faster",
}
EXACT_LINES = {i: line for i, line in enumerate(EX) if i not in TIMING_SHAPES}
assert EX[0] == "the loop and X @ w agree: True", EX[0]
assert EX[1] == "w stretched to (2000, 8) has strides (0, 8) | (X * w).sum(axis=1) agrees with X @ w: True", EX[1]
assert EX[2] == "the loop asks the interpreter for 16,000 multiplications and 16,000 additions, one at a time; X @ w asks once", EX[2]
for i, pattern in TIMING_SHAPES.items():
    assert re.fullmatch(pattern, EX[i]), EX[i]
assert EX[6] == "the moving average: 2,000 steps that each need the last, so 2,000 vector operations instead of 16,000 scalar ones", EX[6]
assert EX[7] == "a running total has a library form, np.cumsum: True", EX[7]
SPEEDUP = float(EX[5].split()[7])
assert SPEEDUP > 20, SPEEDUP
EXAMPLE_LINES = EXAMPLE.splitlines()


def ln(text: str, after: int = 0) -> int:
    return next(i + 1 for i, line in enumerate(EXAMPLE_LINES) if i + 1 > after and text in line)


# --- recall programs ----------------------------------------------------------------------------

PREDICT_BROADCAST = '''import numpy as np

X = np.arange(6, dtype=np.float64).reshape(2, 3)
print(X + np.array([10.0, 20.0, 30.0]))
print(X * np.array([[1.0], [-1.0]]))
print((X - X.mean(axis=0)).sum(axis=0), X.mean(axis=1))
'''
PREDICT_BROADCAST_OUT = out(PREDICT_BROADCAST)
assert PREDICT_BROADCAST_OUT == "[[10. 21. 32.]\n [13. 24. 35.]]\n[[ 0.  1.  2.]\n [-3. -4. -5.]]\n[0. 0. 0.] [1. 4.]\n", PREDICT_BROADCAST_OUT

REVIEW_STRIDES = '''import numpy as np

a = np.ones((4, 1), dtype=np.float64)
b = np.arange(3, dtype=np.float64)
total = a + b
print(total.shape, np.broadcast_to(b, total.shape).strides, np.broadcast_to(a, total.shape).strides)
print((np.zeros((2, 3, 4)) + np.ones((3, 1))).shape)
'''
REVIEW_STRIDES_OUT = out(REVIEW_STRIDES)
assert REVIEW_STRIDES_OUT == "(4, 3) (0, 8) (8, 0)\n(2, 3, 4)\n", REVIEW_STRIDES_OUT

PARSONS_LINES = [
    "import numpy as np",
    "X = np.arange(12, dtype=np.float64).reshape(4, 3)",
    "centered = X - X.mean(axis=0)",
    "print(centered.sum(axis=0))",
]
assert out("\n".join(PARSONS_LINES) + "\n") == "[0. 0. 0.]\n"
assert out("\n".join(PARSONS_LINES).replace("X.mean(axis=0)", "X.mean()") + "\n") != "[0. 0. 0.]\n"

# --- the fill-in --------------------------------------------------------------------------------

FILL_SOLUTION = '''import numpy as np

x = np.array([-2.0, -0.5, 0.0, 1.5, 3.0, -1.0])


def relu(x):
    """x where it is positive and 0 elsewhere, with no Python loop: a mask picks, np.where chooses."""
    return np.where(x > 0, x, 0.0)


def count_positive(x):
    """How many entries are positive: a boolean array summed (True counts as 1)."""
    return int((x > 0).sum())


print(relu(x), count_positive(x))
'''
FILL_STARTER = FILL_SOLUTION.replace("    return np.where(x > 0, x, 0.0)", "    return np.where(..., x, 0.0)").replace("    return int((x > 0).sum())", "    return int((...).sum())")
FILL_WRONG = FILL_SOLUTION.replace("    return int((x > 0).sum())", "    return int((x >= 0).sum())")
FILL_OUT = out(FILL_SOLUTION)
assert FILL_OUT == "[0.  0.  0.  1.5 3.  0. ] 2\n", FILL_OUT
assert out(FILL_WRONG) != FILL_OUT

# --- the write ----------------------------------------------------------------------------------

WRITE_LOOPS = '''import numpy as np


def relu_loop(x):
    out = np.empty_like(x)
    for i in range(len(x)):
        out[i] = x[i] if x[i] > 0 else 0.0
    return out


def standardize_loop(X):
    out = np.empty_like(X)
    for j in range(X.shape[1]):
        column = X[:, j]
        mean = sum(column) / len(column)
        spread = (sum((value - mean) ** 2 for value in column) / len(column)) ** 0.5
        for i in range(X.shape[0]):
            out[i, j] = (X[i, j] - mean) / spread
    return out
'''
WRITE_VECTOR = '''

def relu(x):
    """x where positive, 0 elsewhere: one mask, one choice."""
    return np.where(x > 0, x, 0.0)


def standardize(X):
    """Each column minus its mean, divided by its standard deviation; broadcasting stretches the (3,) rows of means over the (4, 3) matrix."""
    return (X - X.mean(axis=0)) / X.std(axis=0)
'''
WRITE_TAIL = '''

x = np.array([-2.0, -0.5, 0.0, 1.5, 3.0])
X = np.arange(12, dtype=np.float64).reshape(4, 3) ** 2
print(relu(x), np.allclose(relu(x), relu_loop(x)))
print(np.round(standardize(X), 3))
print(np.allclose(standardize(X), standardize_loop(X)))
'''
WRITE_SOLUTION = WRITE_LOOPS + WRITE_VECTOR + WRITE_TAIL
WRITE_STARTER = WRITE_LOOPS + WRITE_TAIL
WRITE_OUT = out(WRITE_SOLUTION)
print("write:\n" + WRITE_OUT)
assert WRITE_OUT.splitlines()[0] == "[0.  0.  0.  1.5 3. ] True" and WRITE_OUT.splitlines()[-1] == "True", WRITE_OUT
WRITE_STILL_A_LOOP = WRITE_LOOPS + "\n\nrelu = relu_loop\nstandardize = standardize_loop\n" + WRITE_TAIL
assert out(WRITE_STILL_A_LOOP) == WRITE_OUT, "the loop version prints the same thing and fails the counting test"
WRITE_GRAND_MEAN = WRITE_SOLUTION.replace("(X - X.mean(axis=0)) / X.std(axis=0)", "(X - X.mean()) / X.std()")
assert out(WRITE_GRAND_MEAN) != WRITE_OUT

# --- the build ----------------------------------------------------------------------------------

BUILD_SOLUTION = '''import numpy as np


def predict(X, w, b):
    """One score per row: the weighted sum of its columns plus a bias."""
    return X @ w + b


def standardize(X):
    """Each column minus its mean, over its standard deviation; a column with no spread becomes zeros."""
    spread = X.std(axis=0)
    return (X - X.mean(axis=0)) / np.where(spread == 0, 1.0, spread)


def relu(x):
    """x where positive, 0 elsewhere."""
    return np.maximum(x, 0.0)


def running_max(x):
    """The largest value seen so far at each position: a loop in C, not in Python."""
    return np.maximum.accumulate(x)


def ema(X, alpha):
    """An exponential moving average down the rows: each row needs the one before, so the rows loop and the columns don't."""
    state = np.zeros(X.shape[1])
    out = np.empty_like(X)
    for t in range(len(X)):
        state = alpha * X[t] + (1 - alpha) * state
        out[t] = state
    return out


X = np.arange(12, dtype=np.float64).reshape(4, 3)
w = np.array([1.0, -1.0, 0.5])
print(predict(X, w, 2.0))
print(np.round(standardize(X), 3))
print(relu(np.array([-1.0, 0.0, 2.5])), running_max(np.array([1.0, 3.0, 2.0, 5.0, 4.0])))
print(np.round(ema(X, 0.5), 3))
'''
BUILD_OUT = out(BUILD_SOLUTION)
print("build:\n" + BUILD_OUT)
assert BUILD_OUT.splitlines()[0] == "[2.  3.5 5.  6.5]", BUILD_OUT
assert BUILD_OUT.splitlines()[-1] == " [6.375 7.312 8.25 ]]", BUILD_OUT
BUILD_LOOPED_PREDICT = BUILD_SOLUTION.replace("    return X @ w + b", "    return np.array([sum(x * weight for x, weight in zip(row, w)) + b for row in X])")
BUILD_UNGUARDED = BUILD_SOLUTION.replace("    spread = X.std(axis=0)\n    return (X - X.mean(axis=0)) / np.where(spread == 0, 1.0, spread)", "    return (X - X.mean(axis=0)) / X.std(axis=0)")
BUILD_ELEMENT_EMA = BUILD_SOLUTION.replace("        state = alpha * X[t] + (1 - alpha) * state\n        out[t] = state", "        for j in range(X.shape[1]):\n            state[j] = alpha * X[t, j] + (1 - alpha) * state[j]\n            out[t, j] = state[j]")
assert BUILD_LOOPED_PREDICT != BUILD_SOLUTION and out(BUILD_LOOPED_PREDICT) == BUILD_OUT
assert BUILD_UNGUARDED != BUILD_SOLUTION and out(BUILD_UNGUARDED) == BUILD_OUT
assert BUILD_ELEMENT_EMA != BUILD_SOLUTION and out(BUILD_ELEMENT_EMA) == BUILD_OUT

# --- the debug ----------------------------------------------------------------------------------

DEBUG_SOLUTION = '''import numpy as np


def center(X):
    """Subtract each column's own mean, so every column sums to 0."""
    return X - X.mean(axis=0)


def score(X, w):
    """The weighted sum of each row: one score per row, with one weight per column."""
    return (X * w).sum(axis=1)


X = np.arange(18, dtype=np.float64).reshape(6, 3)
w = np.array([0.5, -1.0, 2.0])
centered = center(X)
print("column sums after centering:", centered.sum(axis=0))
print("scores:", score(centered, w))
'''
BUG_COLUMN = ("w = np.array([0.5, -1.0, 2.0])", "w = np.array([0.5, -1.0, 2.0]).reshape(-1, 1)")
BUG_GRAND_MEAN = ("    return X - X.mean(axis=0)", "    return X - X.mean()")
DEBUG_STARTER = DEBUG_SOLUTION.replace(*BUG_COLUMN).replace(*BUG_GRAND_MEAN)
DEBUG_STILL_COLUMN = DEBUG_SOLUTION.replace(*BUG_COLUMN)
DEBUG_STILL_GRAND = DEBUG_SOLUTION.replace(*BUG_GRAND_MEAN)
DEBUG_OUT = out(DEBUG_SOLUTION)
print("debug:\n" + DEBUG_OUT)
assert DEBUG_OUT == "column sums after centering: [0. 0. 0.]\nscores: [-11.25  -6.75  -2.25   2.25   6.75  11.25]\n", DEBUG_OUT
STARTER_ERROR = fails(DEBUG_STARTER)
assert "operands could not be broadcast together with shapes (6,3) (3,1)" in STARTER_ERROR, STARTER_ERROR
GRAND_OUT = out(DEBUG_STILL_GRAND)
assert GRAND_OUT.splitlines()[0] == "column sums after centering: [-6.  0.  6.]", GRAND_OUT

REVIEW_CODE_SOLUTION = '''import numpy as np


def standardize(X):
    """Each column minus its mean, divided by its standard deviation, with no Python loop."""
    return (X - X.mean(axis=0)) / X.std(axis=0)


X = np.array([[1.0, 10.0], [2.0, 20.0], [3.0, 30.0], [6.0, 60.0]])
print(np.round(standardize(X), 3))
print(np.allclose(standardize(X).mean(axis=0), 0), np.allclose(standardize(X).std(axis=0), 1))
'''
REVIEW_CODE_OUT = out(REVIEW_CODE_SOLUTION)
assert REVIEW_CODE_OUT.splitlines()[-1] == "True True", REVIEW_CODE_OUT
REVIEW_CODE_LOOP = REVIEW_CODE_SOLUTION.replace(
    "    return (X - X.mean(axis=0)) / X.std(axis=0)",
    "    out = np.empty_like(X)\n    for j in range(X.shape[1]):\n        column = X[:, j]\n        for i in range(X.shape[0]):\n            out[i, j] = (X[i, j] - column.mean()) / column.std()\n    return out",
)
assert out(REVIEW_CODE_LOOP) == REVIEW_CODE_OUT

# =====================================================================================
# topic.yaml
# =====================================================================================

write(
    "topic.yaml",
    '''id: ml.hw.vectorization
kind: topic
status: ready
title: "Why vectorized code is fast"
summary: "What the interpreter does for every Python operation and what a NumPy operation skips, SIMD, broadcasting as a loop you don't write, the doubling test on a loop against its vectorized form, and when a loop can't be vectorized."
prerequisites: [ml.hw.memory-and-caches, ml.dsa.complexity]
packages: [numpy]
estimated_minutes: 50
rev: 1
objectives:
  - "Explain what a Python loop pays per element that a NumPy operation doesn't, and what SIMD adds."
  - "Rewrite a loop over an array as array operations with broadcasting, and check that the two agree."
  - "Measure the loop and the vectorized form with the doubling test, and read the constant against the order."
  - "Recognize a loop that can't be vectorized because each step depends on the last, and say what to do instead."
# Linked, never copied or embedded: NumPy's documentation is under the NumPy
# licence (BSD-3-Clause); Wikipedia is CC BY-SA 4.0.
resources:
  - title: "NumPy user guide: Broadcasting (the rules, with the stretched-array pictures)"
    url: https://numpy.org/doc/stable/user/basics.broadcasting.html
    type: reading
    use: link
    license: BSD-3-Clause (NumPy documentation)
  - title: "NumPy user guide: Universal functions (ufunc) basics (the element-wise functions that vectorized code is made of, and their accumulate method)"
    url: https://numpy.org/doc/stable/user/basics.ufuncs.html
    type: reading
    use: link
    license: BSD-3-Clause (NumPy documentation)
  - title: "Wikipedia: Single instruction, multiple data (what SIMD is and where it shows up)"
    url: https://en.wikipedia.org/wiki/Single_instruction,_multiple_data
    type: reading
    use: link
    license: CC BY-SA 4.0 (linked, not copied)
practice:
  - example-a-loop-and-its-vector-form
  - mcq-what-the-loop-pays
  - mcq-what-simd-adds
  - predict-broadcast-shapes
  - parsons-center-the-columns
  - mcq-reading-the-doubling-test
  - mcq-a-loop-over-batches
  - mcq-which-loop-cannot-be-vectorized
  - fill-relu-and-count
  - write-vectorize-two-loops
prove:
  build: build-vectorize-a-feature-step
  debug: debug-a-broadcast-that-went-wrong
  explain:
    prompt: |
      A teammate's feature code loops in Python over a million rows and takes minutes; another asks whether their training loop over a hundred batches, each a NumPy operation on ten thousand rows, is "unvectorized" too; a third has an exponential moving average they can't turn into array operations. In your own words: what the interpreter pays for every element of a Python loop and what a NumPy operation skips, and what SIMD adds; how you would rewrite the first teammate's loop with broadcasting and check that it agrees; what the doubling test shows for the loop against the vectorized form, and what it says about order and constant; and what a sequential dependence is and what the third teammate can do.
    rubric:
      - id: interpreter-cost
        required: true
        description: "Per element, the interpreter decodes bytecode, looks up names, checks types to pick the operation, unpacks the numbers from their objects and allocates a new object for the result, hundreds of nanoseconds; a NumPy operation checks types and shapes once and runs a C loop over contiguous bytes, nanoseconds per element, with SIMD doing several elements per instruction. The cost is per Python-level operation, so a hundred vectorized batches are fine and a million scalar steps are not."
      - id: broadcasting
        required: true
        description: "Replace the loop with whole-array operations: a weighted sum is X @ w or (X * w).sum(axis=1), a per-column centring is X - X.mean(axis=0). Broadcasting lines shapes up from the right and stretches length-1 or missing axes without copying (a stride of 0). Check with np.allclose against the loop on the same data."
      - id: doubling-test
        required: true
        description: "Doubling the rows roughly doubles both times: both forms are linear, same order. The vectorized form is tens to hundreds of times faster: a smaller constant, not a better order. Vectorizing never changes the order, because every element must still be touched."
      - id: dependence
        required: true
        description: "A sequential dependence is a step that needs the previous step's result, as an exponential moving average does; it can't be one array operation. Use a library function that runs the dependence in C when one exists (np.cumsum, np.maximum.accumulate), otherwise loop over the dependent axis only and vectorize across the other, or move the loop to compiled code."
    model_answer: |
      A Python loop pays for every element. For one `total += x * weight`, the interpreter fetches and decodes several bytecode instructions, looks up the names, checks the types of both operands to decide which multiplication to run, unpacks the two numbers from the objects that hold them, multiplies, allocates a fresh object for the result and later frees it, then does the same again for the addition. That is a few hundred nanoseconds per element, and a million rows of a handful of columns is seconds to minutes. A NumPy operation does the type and shape check once for the whole array and then runs a loop written in C over the raw bytes, which costs a few nanoseconds per element; where the data is contiguous and all of one type, that loop uses SIMD, single instruction multiple data, processor instructions that multiply four or eight numbers at once. The cost is per Python-level operation, so the second teammate is fine: a hundred batches means the interpreter overhead is paid a hundred times, and each time it buys ten thousand elements of work. The first teammate's loop is paid a million times for one element each. I would rewrite it as whole-array operations. If each row needs a weighted sum, that is X @ w, or (X * w).sum(axis=1), where broadcasting stretches the one-dimensional w across every row of X without copying it, with a stride of zero. If each column needs centring, that is X - X.mean(axis=0). Then I would run both versions on the same data and check np.allclose, because a wrong axis or a wrong shape fails silently or broadcasts into something I did not mean. The doubling test is the check from Counting steps and big-O: time each version at n rows and at 2n. Both ratios come out near two, so both are linear in n; the vectorized version is tens to hundreds of times faster at every size. Same order, different constant. Vectorizing never changes the order, because every element still has to be touched; it changes how much each element costs. The third teammate has a sequential dependence: each step of an exponential moving average needs the previous step's result, so there is no single array operation that gives all the steps at once. The options are, in order: a library function that runs the dependence in C, as np.cumsum does for a running total and np.maximum.accumulate for a running maximum; if none fits, loop only over the dependent axis, the time steps, and vectorize across the other, so a thousand steps over fifty columns is a thousand vector operations instead of fifty thousand scalar ones; and if that is still too slow, move the loop into compiled code with a tool like Numba or a C extension.
review_pool:
  - review-predict-strides-of-a-broadcast
  - review-mcq-constant-not-order
  - review-mcq-loop-over-the-dependent-axis
  - review-standardize
# What this topic teaches. Each question names the skills it tests, so a
# missed question can come back as a different one on the same skill
# (ADR-0011).
skills:
  - id: interpreter-cost
    description: "Explain what a Python loop pays per element, what NumPy skips, and what SIMD adds"
  - id: broadcasting
    description: "Rewrite a loop as array operations with broadcasting, and check that they agree"
  - id: doubling-test
    description: "Read the doubling test on a loop against its vectorized form: same order, smaller constant"
  - id: dependence
    description: "Recognize a sequential dependence, and say what to do instead of vectorizing"
''',
)

# =====================================================================================
# lesson.mdx
# =====================================================================================

write(
    "lesson.mdx",
    '''<Intro>

Memory, caches and locality showed where bytes sit; this one is about what each operation on them costs, and why the same arithmetic can take a minute in a Python loop and a few milliseconds as array operations. The interpreter pays a price for every element it touches, a NumPy operation pays it once, and the processor can multiply several numbers in one instruction if the data is laid out for it. The topic ends with the loops that can't be vectorized, where each step needs the last, and what to do with them.

The main resource is **NumPy's user guide page on broadcasting**: the rules that let a `(8,)` vector act on every row of a `(2000, 8)` matrix without a loop or a copy; about 15 minutes. The ufunc basics page lists the element-wise functions and their `accumulate` method, and Wikipedia's _Single instruction, multiple data_ page is the one-paragraph version of SIMD. Watch for:

- **The broadcasting rules**: line the shapes up from the right; a 1 or a missing axis stretches.
- **`ufunc.accumulate`** and `np.cumsum`: a running loop, run in C.
- **What SIMD needs**: the same operation on many values that sit together.

</Intro>

<Resource index={0} />

<Recap>

- **What a loop pays per element.** For `total += x * weight`, the interpreter fetches and decodes several bytecode instructions (the instructions Python compiles your code into), looks up `x` and `weight`, checks both types to choose the right `*`, unpacks the floats from the objects that hold them, multiplies, allocates a new float object for the result, and then does it all again for `+=`: a few hundred nanoseconds. A NumPy operation checks types and shapes once and runs a loop written in C over the raw bytes: a few nanoseconds per element. The cost is **per Python-level operation**, not per element; a loop over a hundred batches that each do one array operation is fine, and `np.vectorize` is a Python loop in disguise.
- **SIMD** (single instruction, multiple data): the processor has registers wide enough for 4 or 8 float64s and instructions that add or multiply all of them at once. NumPy's C loops use them when the data is contiguous and all one dtype, which is what Memory, caches and locality was about; a Python loop never can, because each element is a separate object.
- **Broadcasting is a loop you don't write.** Shapes are lined up from the right; an axis of length 1, or a missing axis, is stretched to match. `X * w` with shapes `(2000, 8)` and `(8,)` applies `w` to every row; `X - X.mean(axis=0)` centres every column. The stretched array is a view with a **stride of 0** on the stretched axis: `np.broadcast_to(w, X.shape).strides` is `(0, 8)`. Nothing is copied. A shape that doesn't line up fails loudly (`operands could not be broadcast together`); a shape that lines up the wrong way succeeds silently, so check with `np.allclose` against the loop you replaced.
- **The doubling test, on both forms.** Time each at `n` and `2n` rows: both ratios come out near 2, so both are linear in `n`, the same order. The vectorized form is tens to hundreds of times faster at every size (the number varies by machine, and the browser's clock is coarse). Vectorizing never changes the order, because every element must still be touched; it changes the **constant**, how much each element costs.
- **Masks instead of `if`.** `np.where(x > 0, x, 0.0)` is a ReLU (the activation from Module 4 that zeroes negatives) with no loop; `(x > 0).sum()` counts; `x[x > 0]` selects. A condition becomes a boolean array and the choice becomes one operation.
- **Fewer passes.** `(X * w).sum(axis=1)` makes a `(2000, 8)` intermediate and reads it back; `X @ w` does it in one pass with no intermediate. For big arrays the bytes moved are the cost, as Memory, caches and locality showed; `out=` arguments and in-place operators keep the intermediates down.
- **A sequential dependence** is a step that needs the result of the step before: an exponential moving average, `state = alpha * x[t] + (1 - alpha) * state`, or a running state in a simulation. No single array operation gives every step at once. In order: a library function that runs the dependence in C (`np.cumsum`, `np.cumprod`, `np.maximum.accumulate`, `ufunc.accumulate`); otherwise loop over the dependent axis only and vectorize across the other (2,000 vector operations over 8 columns, not 16,000 scalar ones); otherwise compiled code (Numba, Cython, or a C extension), which the next topics don't need.
- **In machine learning** (names you'll meet later): a per-example Python loop is the most common performance bug in a training script; frameworks are vectorized across the batch axis for exactly these reasons; `torch.vmap` and `jax.vmap` write the batch loop for you; and a recurrent network is a sequential dependence over time with the batch vectorized, which is why it trains slower than a model that can look at the whole sequence at once.

</Recap>
''',
)

# =====================================================================================
# recall
# =====================================================================================

mcq(
    "mcq-what-the-loop-pays",
    "`for x in xs: total += x * w` over a million floats takes a few tenths of a second; `xs * w` on the same data takes a few milliseconds. Where does the second go?",
    [
        "Into the interpreter: per element it decodes bytecode, looks up names, checks types, unpacks floats and allocates a result",
        "Into the multiplications: a Python float multiply is slower than a NumPy one because NumPy drops to lower precision for speed on big arrays",
        "Into memory: the loop reads each float from RAM one at a time, while NumPy keeps the whole array in the processor's registers",
        "Into the garbage collector, which pauses the loop every few thousand iterations to scan the heap for reference cycles",
    ],
    0,
    "The arithmetic is the same and the precision is the same; what differs is everything around it. For each element the interpreter runs several bytecode instructions, resolves the names, checks the operand types to pick the right operation, unpacks the floats from their objects, allocates a new object for the product and another for the sum. NumPy does the checks once and runs a C loop. The memory traffic is the same either way, and the garbage collector is not involved in freeing floats.",
    ["interpreter-cost"],
)

mcq(
    "mcq-what-simd-adds",
    "What does SIMD add to a vectorized NumPy operation, and what does it need?",
    [
        "A second processor core for each array, so that two arrays can be processed at the same time on different cores",
        "A cache of recent results, so that repeated operations on the same array are free the second time round",
        "Instructions that apply one operation to 4 or 8 numbers at once; it needs contiguous data of one dtype",
        "Compression of the array in memory, so that fewer bytes have to be moved for the same number of elements",
    ],
    2,
    "Single instruction, multiple data: a register holds several floats side by side and one instruction adds or multiplies all of them. NumPy's C loops use it when the elements sit next to each other in memory and share a type, which a contiguous float64 array does and a list of Python objects never does. It has nothing to do with extra cores, caching or compression.",
    ["interpreter-cost"],
)

write(
    "recall/predict-broadcast-shapes.yaml",
    f'''id: predict-broadcast-shapes
type: predict_output
rev: 1
prompt: |
  A `(2, 3)` matrix combined with a `(3,)` row, a `(2, 1)` column, and its own column means. What does the program print?
code: |
{block(PREDICT_BROADCAST)}expected_output: |
{block(PREDICT_BROADCAST_OUT)}explanation: |
  A `(3,)` row lines up with the last axis of `(2, 3)` and is stretched down both rows, so each column gets its own addend. A `(2, 1)` column lines up with the first axis and is stretched across the columns, so row 0 is multiplied by 1 and row 1 by -1. `X.mean(axis=0)` is one mean per column, `(3,)`, subtracted from every row, so each column sums to 0; `X.mean(axis=1)` is one mean per row.
skills: [broadcasting]
''',
)

write(
    "recall/parsons-center-the-columns.yaml",
    "id: parsons-center-the-columns\ntype: parsons\nrev: 1\nprompt: |\n"
    + block("Put the lines in order to subtract each column's mean from a `(4, 3)` matrix and print the column sums, `[0. 0. 0.]`. One line is a decoy that doesn't belong.")
    + "lines:\n"
    + "".join(f"  - {quoted(line)}\n" for line in PARSONS_LINES)
    + "distractors:\n  - "
    + quoted("centered = X - X.mean()")
    + "\nexplanation: |\n"
    + block("`X.mean(axis=0)` is a `(3,)` vector of column means, which broadcasting stretches down every row, so each column ends up summing to 0. The decoy subtracts the single grand mean from everything, which centres the matrix as a whole but leaves the columns off by their differences from it.")
    + "skills: [broadcasting]\n",
)

mcq(
    "mcq-reading-the-doubling-test",
    "The doubling test on a Python loop gives 20 ms for 2,000 rows and 40 ms for 4,000; on the vectorized form, 0.2 ms and 0.4 ms. What does that say?",
    [
        "The vectorized form is O(1): its time barely changes with the input, which is what vectorizing is for",
        "The loop is O(n squared), because its time grew faster in absolute terms than the vectorized form's did",
        "The test is inconclusive, because the vectorized times are too small to trust and should be measured again",
        "Both are linear in the rows, the same order; vectorizing made the constant about a hundred times smaller",
    ],
    3,
    "Both ratios are 2, so doubling the input doubles the time for both: linear, the same order. What differs is the constant per element, about a hundred times smaller for the vectorized form. Vectorizing never changes the order, since every element must still be touched; it changes what each one costs. Small times are fine as long as they are measured over enough repeats to be above the clock's resolution.",
    ["doubling-test"],
)

mcq(
    "mcq-a-loop-over-batches",
    "A training loop runs 100 batches; each iteration does a few NumPy operations on a `(10000, 64)` batch. Is this loop a problem of the kind this topic is about?",
    [
        "Yes: any Python `for` over data pays the interpreter's per-element cost, so the batches should be stacked into one array and done at once",
        "Yes, unless the loop uses `np.vectorize` on the update, which removes the interpreter overhead from the iterations",
        "No: the interpreter's cost is paid per Python-level operation, a few hundred here, each doing 640,000 elements of work in C",
        "No, because NumPy caches the result of the first batch and reuses it for the others, so only the first iteration costs anything",
    ],
    2,
    "The overhead is per operation the interpreter dispatches, not per element the data contains. A hundred iterations of a handful of array operations is a few hundred dispatches, each buying hundreds of thousands of elements of C-loop work; the overhead is lost in the noise. The problem loop is the one that dispatches once per element. `np.vectorize` is itself a per-element Python loop, and NumPy caches nothing between calls.",
    ["interpreter-cost"],
)

mcq(
    "mcq-which-loop-cannot-be-vectorized",
    "Which of these loops can't be replaced by a single array operation, and why?",
    [
        "`for t: state = a * x[t] + (1 - a) * state; out[t] = state`, because each step needs the state the step before produced",
        "`for i: out[i] = x[i] ** 2`, because exponentiation isn't a NumPy operation and has to go through Python's `**` for every element",
        "`for i: out[i] = x[i] if x[i] > 0 else 0`, because an `if` can't be vectorized and has to be decided one element at a time",
        "`for i: row_sums[i] = X[i].sum()`, because each row has to be summed separately before the results can be collected",
    ],
    0,
    "Squaring is `x ** 2`, the `if` is `np.where(x > 0, x, 0)`, and the row sums are `X.sum(axis=1)`: each element's answer depends only on its own inputs, so all of them can be computed at once. The moving average is different: step `t` needs the state after step `t - 1`, a sequential dependence. For that, look for a library function that runs the recurrence in C (a running total is `np.cumsum`), or loop over the time axis only and vectorize across everything else.",
    ["dependence"],
)

write(
    "recall/review-predict-strides-of-a-broadcast.yaml",
    f'''id: review-predict-strides-of-a-broadcast
type: predict_output
rev: 1
prompt: |
  A `(4, 1)` column plus a `(3,)` row, the strides of each operand stretched to the result's shape, and the shape of a three-dimensional sum. What does the program print?
code: |
{block(REVIEW_STRIDES)}expected_output: |
{block(REVIEW_STRIDES_OUT)}explanation: |
  Lined up from the right, `(4, 1)` and `(3,)` become `(4, 3)`: the column is stretched across 3 columns and the row down 4 rows. A stretched axis has a stride of 0, so the same bytes are read again and again without being copied: the row's strides are `(0, 8)` and the column's `(8, 0)`. `(3, 1)` against `(2, 3, 4)` lines up as `(1, 3, 1)` and stretches to `(2, 3, 4)`.
skills: [broadcasting]
''',
)

mcq(
    "review-mcq-constant-not-order",
    "After vectorizing a feature step, the doubling test still shows a ratio of 2.0. A teammate says the vectorizing must have failed. Did it?",
    [
        "Yes: a successful vectorization makes the time independent of the number of rows, so the ratio should have dropped towards 1",
        "Yes, unless the array was converted to float32 along the way, which is what makes vectorized code fast in the first place",
        "Not necessarily: vectorizing can't change the order, since every row is still touched; compare times at one size, not ratios",
        "Not necessarily, but only if the whole array fits in the cache; otherwise the ratio would have changed along with the constant",
    ],
    2,
    "The ratio measures the order, and a linear step stays linear however it is written: twice the rows is twice the elements to touch. What vectorizing changes is the constant, which shows up as the time at a given size, not as the ratio between sizes. If the vectorized step is tens of times faster than the loop at 2,000 rows and at 4,000, it worked. Precision and cache fit affect the constant too, but neither changes the reading of the ratio.",
    ["doubling-test"],
)

mcq(
    "review-mcq-loop-over-the-dependent-axis",
    "An exponential moving average must be computed down a `(100000, 50)` matrix: each row's smoothed value depends on the previous row's. Which plan is right?",
    [
        "Loop over the 100,000 rows in Python and, inside, loop over the 50 columns, since the dependence rules out array operations",
        "Loop over the 100,000 rows in Python, computing each row's 50 values as one array operation on the previous state",
        "Loop over the 50 columns in Python and vectorize down the 100,000 rows with a single array operation per column",
        "Use `np.vectorize` on the update function, which removes the dependence",
    ],
    1,
    "The dependence runs down the rows, so the rows must be visited in order; the 50 columns are independent of each other, so each step can update all of them at once. That is 100,000 vector operations instead of 5,000,000 scalar ones. Looping over columns doesn't help, since the dependence inside a column still has to be unrolled one row at a time, and `np.vectorize` is a per-element Python loop that changes nothing.",
    ["dependence"],
)

# =====================================================================================
# exercises
# =====================================================================================

write(
    "exercises/example-a-loop-and-its-vector-form/exercise.yaml",
    f'''id: example-a-loop-and-its-vector-form
stage: worked_example
rev: 1
title: "A loop and its vector form"
prompt: |
  A weighted sum of every row, as a Python loop and as `X @ w`; the stretched weights and what the interpreter is asked to do; the doubling test on both; and a moving average that has to stay a loop. Press **Run**, then read how each part works. The three timing lines are measured on your machine and will differ from anyone else's.
steps:
  - label: "The loop and its vector form agree"
    lines: "{ln('def predict_loop')}-{ln('the loop and X @ w agree')}"
    note: "`predict_loop` visits 2,000 rows and 8 elements each, 16,000 steps the interpreter runs one at a time. `X @ w` is the same arithmetic as one operation. The first thing to do after vectorizing anything is to check the two agree with `np.allclose`, because the usual mistake, a wrong axis, fails silently."
  - label: "Broadcasting, and what the interpreter is asked"
    lines: "{ln('stretched = np.broadcast_to')}-{ln('the loop asks the interpreter')}"
    note: "`X * w` works because broadcasting stretches the `(8,)` vector to `(2000, 8)` without copying it: the stretched view has a stride of 0 down its first axis, so every row reads the same 64 bytes. The loop asks the interpreter for 16,000 multiplications and 16,000 additions, each one decoded, type-checked, unpacked and allocated separately; `X @ w` asks once and the rest happens in C."
  - label: "The doubling test on both"
    lines: "{ln('def seconds')}-{ln('at 4,000 rows the vectorized form')}"
    note: "Each form is timed at 2,000 rows and at 4,000, over repeats (5 for the loop, 200 for the fast one, whose single call is below the clock's resolution). Both ratios should land near 2, since both forms are linear in the rows, the same order; one run on a shared machine can land anywhere from about 1.2 to 2.5, so run it a few times and read the trend. The vectorized form is tens to hundreds of times faster at either size: a smaller constant. That is all vectorizing can do, and it is a lot."
  - label: "A loop that has to stay a loop"
    lines: "{ln('def moving_average')}-{ln('a running total has a library form')}"
    note: "Each row's smoothed state depends on the previous row's, so no single array operation produces all 2,000 rows at once. The loop stays, but only over the dependent axis: each step updates all 8 columns as one vector operation, 2,000 operations instead of 16,000. When the dependence has a library form, as a running total does in `np.cumsum`, use that: the loop runs in C."
''',
)
write("exercises/example-a-loop-and-its-vector-form/solution.py", EXAMPLE)
write(
    "exercises/example-a-loop-and-its-vector-form/test_exercise.py",
    f'''import re

from checks import run

EXACT = {EXACT_LINES!r}
# The timing lines differ by machine and by clock, so they are checked by shape.
SHAPES = {TIMING_SHAPES!r}


def test_the_walkthrough():
    """Prints the agreement, the broadcast, the counts, three timing lines in the right shape, and the moving average."""
    lines = run().splitlines()
    assert len(lines) == 8, lines
    for i, text in EXACT.items():
        assert lines[i] == text, lines[i]
    for i, pattern in SHAPES.items():
        assert re.fullmatch(pattern, lines[i]), lines[i]
''',
)

write(
    "exercises/fill-relu-and-count/exercise.yaml",
    f'''id: fill-relu-and-count
stage: fill_in
rev: 1
title: "A mask instead of an if"
prompt: |
  `relu(x)` should return `x` where it is positive and `0` elsewhere, and `count_positive(x)` how many entries are positive, neither with a Python loop: a comparison on the whole array gives a boolean mask, `np.where` chooses by it, and a mask summed counts its `True`s. Replace each `...` so the program prints:

  ```
{block(FILL_OUT)}  ```

  The program fails until every `...` is replaced.
hints:
  - "The mask is the comparison itself: `x > 0` is an array of booleans the same shape as `x`."
  - "Summing a boolean array counts the Trues; `int(...)` turns the NumPy integer into a plain one."
skills: [broadcasting]
''',
)
write("exercises/fill-relu-and-count/starter.py", FILL_STARTER)
write("exercises/fill-relu-and-count/solution.py", FILL_SOLUTION)
write(
    "exercises/fill-relu-and-count/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints the rectified array and the count."""
    printed = run()
    assert printed == {FILL_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_more_values():
    """relu keeps positives, zeroes the rest, and works on a matrix; count_positive is 0 for all-negative input."""
    relu = function("relu")
    count_positive = function("count_positive")
    assert relu(np.array([[-1.0, 2.0], [3.0, -4.0]])).tolist() == [[0.0, 2.0], [3.0, 0.0]]
    assert count_positive(np.array([-1.0, -2.0, 0.0])) == 0 and count_positive(np.array([0.5, 1e-9])) == 2
''',
)
write("exercises/fill-relu-and-count/wrong/counts-zero.py", FILL_WRONG)
write(
    "exercises/fill-relu-and-count/wrong/typed-in.py",
    "def relu(x):\n    return x\n\n\ndef count_positive(x):\n    return 2\n\n\n" + "".join(f"print({line!r})\n" for line in FILL_OUT.splitlines()),
)

write(
    "exercises/write-vectorize-two-loops/exercise.yaml",
    f'''id: write-vectorize-two-loops
stage: write
rev: 1
title: "Vectorize two loops"
prompt: |
  The starter has `relu_loop` and `standardize_loop`, written one element at a time. Write `relu(x)` and `standardize(X)` as array operations with no Python loop: `relu` keeps `x` where it is positive and puts 0 elsewhere; `standardize` subtracts each column's mean from the column and divides by the column's standard deviation (`X.mean(axis=0)` and `X.std(axis=0)` are one value per column, and broadcasting stretches them down the rows). The program then compares each against its loop and prints:

  ```
{block(WRITE_OUT)}  ```

  The checks also hand your functions an array that counts how often Python iterates over it or reads single elements from it, and expect zero.
hints:
  - "A condition becomes a mask: `np.where(x > 0, x, 0.0)` chooses from `x` where the mask is true and from 0 elsewhere."
  - "`axis=0` means down the rows, giving one number per column; without it, `mean` and `std` collapse the whole matrix to one number."
skills: [broadcasting]
''',
)
write("exercises/write-vectorize-two-loops/starter.py", WRITE_STARTER)
write("exercises/write-vectorize-two-loops/solution.py", WRITE_SOLUTION)
write(
    "exercises/write-vectorize-two-loops/test_exercise.py",
    f'''import numpy as np

from checks import function, run


{WATCHED}

def test_the_output():
    """Prints the two agreements and the standardized matrix."""
    printed = run()
    assert printed == {WRITE_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_no_python_loop():
    """Neither function iterates over its array in Python or reads it one element at a time."""
    relu = function("relu")
    standardize = function("standardize")
    relu(watched([-1.0, 2.0, -3.0, 4.0]))
    assert Watched.iterations == 0 and Watched.elements == 0, "relu loops in Python"
    standardize(watched([[1.0, 2.0], [3.0, 5.0], [5.0, 11.0]]))
    assert Watched.iterations == 0 and Watched.elements == 0, "standardize loops in Python"


def test_other_shapes():
    """relu on a matrix, and standardize gives every column a mean of 0 and a spread of 1."""
    relu = function("relu")
    standardize = function("standardize")
    assert relu(np.array([[-1.0, 0.5], [2.0, -2.0]])).tolist() == [[0.0, 0.5], [2.0, 0.0]]
    Z = standardize(np.array([[1.0, 100.0, -3.0], [2.0, 50.0, 0.0], [6.0, 0.0, 3.0]]))
    assert np.allclose(Z.mean(axis=0), 0) and np.allclose(Z.std(axis=0), 1)
''',
)
write("exercises/write-vectorize-two-loops/wrong/still-a-loop.py", WRITE_STILL_A_LOOP)
write("exercises/write-vectorize-two-loops/wrong/grand-mean.py", WRITE_GRAND_MEAN)
write(
    "exercises/write-vectorize-two-loops/wrong/typed-in.py",
    "def relu(x):\n    return x\n\n\ndef standardize(X):\n    return X\n\n\n" + "".join(f"print({line!r})\n" for line in WRITE_OUT.splitlines()),
)

# --- the proof -----------------------------------------------------------------------------------

write(
    "exercises/build-vectorize-a-feature-step/exercise.yaml",
    f'''id: build-vectorize-a-feature-step
stage: build
rev: 1
title: "A feature step, vectorized"
prompt: |
  Starting from a blank editor, write five functions, none with a Python loop except where a step needs the step before:

  - `predict(X, w, b)`: one score per row, the weighted sum of its columns plus the bias `b`.
  - `standardize(X)`: each column minus its mean, divided by its standard deviation; a column with no spread (standard deviation 0) becomes zeros rather than NaN.
  - `relu(x)`: `x` where positive, 0 elsewhere.
  - `running_max(x)`: the largest value seen so far at each position, using the library's accumulate (`np.maximum.accumulate`).
  - `ema(X, alpha)`: the exponential moving average down the rows of a matrix, starting from a state of zeros: `state = alpha * row + (1 - alpha) * state` for each row in order, returning the states as a matrix of the same shape. Loop over the rows only; each update is one array operation over the columns.

  Then print:

  ```python
  X = np.arange(12, dtype=np.float64).reshape(4, 3)
  w = np.array([1.0, -1.0, 0.5])
  print(predict(X, w, 2.0))
  print(np.round(standardize(X), 3))
  print(relu(np.array([-1.0, 0.0, 2.5])), running_max(np.array([1.0, 3.0, 2.0, 5.0, 4.0])))
  print(np.round(ema(X, 0.5), 3))
  ```

  ```
{block(BUILD_OUT)}  ```

  The checks compare each function with a plain loop on other data, hand `predict`, `standardize`, `relu` and `running_max` an array that counts Python-level iteration and single-element reads and expect none, allow `ema` to iterate over rows but not to read single elements, and give `standardize` a column with no spread.
skills: [broadcasting, dependence]
''',
)
write("exercises/build-vectorize-a-feature-step/starter.py", "")
write("exercises/build-vectorize-a-feature-step/solution.py", BUILD_SOLUTION)
write(
    "exercises/build-vectorize-a-feature-step/test_exercise.py",
    f'''import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


{WATCHED}

def test_the_output():
    """Prints the four lines."""
    assert run() == {BUILD_OUT!r}


def test_against_loops():
    """Each function agrees with a plain loop on a 5 by 4 matrix."""
    predict = function("predict")
    standardize = function("standardize")
    relu = function("relu")
    running_max = function("running_max")
    ema = function("ema")
    X = (np.arange(20, dtype=np.float64).reshape(5, 4) * 1.5 - 7) ** 2 / 3
    w = np.array([0.5, -2.0, 1.0, 0.25])
    assert np.allclose(predict(X, w, -1.0), [sum(row[j] * w[j] for j in range(4)) - 1.0 for row in X])
    expected = np.empty_like(X)
    for j in range(4):
        column = X[:, j]
        expected[:, j] = (column - column.mean()) / column.std()
    assert np.allclose(standardize(X), expected)
    assert np.allclose(relu(X - 20), [[max(v - 20, 0.0) for v in row] for row in X])
    assert np.allclose(running_max(X[:, 1]), [max(X[: i + 1, 1]) for i in range(5)])
    state, rows = np.zeros(4), []
    for row in X:
        state = 0.3 * row + 0.7 * state
        rows.append(state.copy())
    assert np.allclose(ema(X, 0.3), rows)


def test_no_python_loops():
    """predict, standardize, relu and running_max never iterate in Python or read single elements; ema never reads single elements."""
    predict = function("predict")
    standardize = function("standardize")
    relu = function("relu")
    running_max = function("running_max")
    ema = function("ema")
    rows = [[1.0, 2.0, 3.0], [4.0, 6.0, 8.0], [0.0, -1.0, 5.0]]
    predict(watched(rows), np.array([1.0, 0.5, -1.0]), 0.0)
    assert Watched.iterations == 0 and Watched.elements == 0
    standardize(watched(rows))
    assert Watched.iterations == 0 and Watched.elements == 0
    relu(watched([-1.0, 2.0, -3.0]))
    assert Watched.iterations == 0 and Watched.elements == 0
    running_max(watched([1.0, 0.0, 2.0]))
    assert Watched.iterations == 0 and Watched.elements == 0
    ema(watched(rows), 0.5)
    assert Watched.elements == 0


def test_no_spread():
    """A constant column standardizes to zeros, not NaN, and the other columns are unaffected."""
    standardize = function("standardize")
    Z = standardize(np.array([[3.0, 1.0], [3.0, 2.0], [3.0, 6.0]]))
    assert not np.isnan(Z).any() and np.allclose(Z[:, 0], 0) and np.allclose(Z[:, 1].std(), 1)
''',
)
write("exercises/build-vectorize-a-feature-step/wrong/looped-predict.py", BUILD_LOOPED_PREDICT)
write("exercises/build-vectorize-a-feature-step/wrong/unguarded-spread.py", BUILD_UNGUARDED)
write("exercises/build-vectorize-a-feature-step/wrong/element-by-element-ema.py", BUILD_ELEMENT_EMA)
write(
    "exercises/build-vectorize-a-feature-step/wrong/typed-in.py",
    "import numpy as np\n\n\ndef predict(X, w, b):\n    return np.array([2.0, 3.5, 5.0, 6.5])\n\n\ndef standardize(X):\n    return X\n\n\ndef relu(x):\n    return x\n\n\ndef running_max(x):\n    return x\n\n\ndef ema(X, alpha):\n    return X\n\n\n"
    + "".join(f"print({line!r})\n" for line in BUILD_OUT.splitlines()),
)

write(
    "exercises/debug-a-broadcast-that-went-wrong/exercise.yaml",
    f'''id: debug-a-broadcast-that-went-wrong
stage: debug
rev: 1
title: "A broadcast that went wrong"
prompt: |
  `center` should subtract each column's mean so that every column sums to 0, and `score` should give one weighted sum per row. The program should print:

  ```
{block(DEBUG_OUT)}  ```

  It has two bugs. Run it: it crashes with `operands could not be broadcast together with shapes (6,3) (3,1)`, because the weights are reshaped into a `(3, 1)` column. Lined up from the right against `(6, 3)`, the column's 1 would stretch to match the 3 columns, but its 3 then has to match the 6 rows and can't; one weight per column is a `(3,)` vector. Fix that, and the column sums come out `[-6. 0. 6.]`: `center` subtracts the single grand mean from everything instead of each column's own mean. The mean needs an axis.
skills: [broadcasting]
''',
)
write("exercises/debug-a-broadcast-that-went-wrong/starter.py", DEBUG_STARTER)
write("exercises/debug-a-broadcast-that-went-wrong/solution.py", DEBUG_SOLUTION)
write(
    "exercises/debug-a-broadcast-that-went-wrong/test_exercise.py",
    f'''import numpy as np

from checks import function, run

EXPECTED = {DEBUG_OUT!r}


def test_the_output():
    """Prints zero column sums and the six scores."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\\n{{EXPECTED}}\\nYour program printed:\\n{{printed}}"


def test_other_shapes():
    """center zeroes the column sums of a 3 by 2 matrix, and score weights a 2 by 4 matrix row by row."""
    center = function("center")
    score = function("score")
    assert np.allclose(center(np.array([[1.0, 10.0], [2.0, 40.0], [6.0, 10.0]])).sum(axis=0), 0)
    assert np.allclose(score(np.ones((2, 4)), np.arange(4, dtype=np.float64)), [6.0, 6.0])
''',
)
write("exercises/debug-a-broadcast-that-went-wrong/wrong/still-a-column.py", DEBUG_STILL_COLUMN)
write("exercises/debug-a-broadcast-that-went-wrong/wrong/still-the-grand-mean.py", DEBUG_STILL_GRAND)
write(
    "exercises/debug-a-broadcast-that-went-wrong/wrong/typed-in.py",
    "import numpy as np\n\n\ndef center(X):\n    return X\n\n\ndef score(X, w):\n    return X\n\n\n" + "".join(f"print({line!r})\n" for line in DEBUG_OUT.splitlines()),
)

write(
    "exercises/review-standardize/exercise.yaml",
    f'''id: review-standardize
stage: review_code
rev: 1
title: "Standardize, from memory"
prompt: |
  Write `standardize(X)`: each column minus its own mean, divided by its own standard deviation, as array operations with no Python loop. Print it, rounded to 3 places, for the matrix `[[1, 10], [2, 20], [3, 30], [6, 60]]` (as floats), then whether the result's column means are all 0 and its column standard deviations all 1:

  ```
{block(REVIEW_CODE_OUT)}  ```

  The checks hand your function an array that counts Python-level iteration and single-element reads, and expect none.
skills: [broadcasting]
''',
)
write("exercises/review-standardize/starter.py", "")
write("exercises/review-standardize/solution.py", REVIEW_CODE_SOLUTION)
write(
    "exercises/review-standardize/test_exercise.py",
    f'''import numpy as np

from checks import function, run


{WATCHED}

def test_the_output():
    """Prints the standardized matrix and two Trues."""
    assert run() == {REVIEW_CODE_OUT!r}


def test_no_python_loop():
    """standardize never iterates in Python or reads single elements, and handles a 3 by 3 matrix."""
    standardize = function("standardize")
    Z = standardize(watched([[1.0, 2.0, 0.0], [3.0, 5.0, 1.0], [5.0, 11.0, 8.0]]))
    assert Watched.iterations == 0 and Watched.elements == 0
    assert np.allclose(np.asarray(Z).mean(axis=0), 0) and np.allclose(np.asarray(Z).std(axis=0), 1)
''',
)
write("exercises/review-standardize/wrong/still-a-loop.py", REVIEW_CODE_LOOP)
write(
    "exercises/review-standardize/wrong/typed-in.py",
    "def standardize(X):\n    return X\n\n\n" + "".join(f"print({line!r})\n" for line in REVIEW_CODE_OUT.splitlines()),
)

print("ml.hw.vectorization written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
