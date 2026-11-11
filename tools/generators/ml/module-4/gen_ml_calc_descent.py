"""Writes the topic ml.calc.descent-in-many-dimensions (Module 4's third
topic). Run from the repository root under uv (python -m uv run python
<this file>), so every program's expected output is captured from CPython
rather than typed in. Files are written as bytes with LF endings."""

import pathlib
import subprocess
import sys

ROOT = pathlib.Path("content/topics/ml.calc.descent-in-many-dimensions")


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


POINTS = '''points = np.array([
    [0.0, 0.0, 3.1],
    [1.0, 0.0, 4.9],
    [0.0, 1.0, 2.05],
    [2.0, 3.0, 3.95],
    [3.0, 1.0, 8.1],
    [1.0, 2.0, 2.9],
])
A = np.column_stack([points[:, 0], points[:, 1], np.ones(6)])
z = points[:, 2]
'''
EXACT = '''X = np.array([[0.0, 0.0], [1.0, 0.0], [0.0, 1.0], [2.0, 3.0]])
A = np.column_stack([X, np.ones(4)])
z = np.array([3.0, 5.0, 2.0, 4.0])
'''

# --- the worked example -------------------------------------------------------------

EXAMPLE = '''import numpy as np


def bowl(p):
    x, y = p
    return x**2 + 3 * y**2


def grad_bowl(p):
    x, y = p
    return np.array([2 * x, 6 * y])


p = np.array([4.0, 2.0])
for step in range(11):
    if step in (0, 1, 2, 5, 10):
        print(step, np.round(p, 3), round(float(bowl(p)), 4))
    p = p - 0.1 * grad_bowl(p)

for rate in [0.05, 0.1, 0.3, 0.4]:
    p = np.array([4.0, 2.0])
    for step in range(10):
        p = p - rate * grad_bowl(p)
    print(rate, round(float(bowl(p)), 3))

''' + POINTS + '''w = np.zeros(3)
losses = []
for step in range(2000):
    miss = A @ w - z
    losses.append(float(np.mean(miss**2)))
    w = w - 0.1 * (2 / 6) * (A.T @ miss)
print(round(losses[0], 4), round(losses[10], 4), round(losses[100], 4), round(losses[-1], 4))
print(np.round(w, 3))
print(np.allclose(w, np.linalg.lstsq(A, z)[0], atol=1e-6))
'''
EXAMPLE_OUT = out(EXAMPLE)
print("example:\n" + numbered(EXAMPLE) + EXAMPLE_OUT)
assert "e-" not in EXAMPLE_OUT and "e+" not in EXAMPLE_OUT, "scientific notation would differ by runtime"
assert EXAMPLE_OUT.endswith("[ 2.015 -1.035  3.024]\nTrue\n"), EXAMPLE_OUT

# --- the fill-in --------------------------------------------------------------------------

FILL_TAIL = '''

def grad_bowl(p):
    return np.array([2 * p[0], 6 * p[1]])


for rate in [0.1, 0.05]:
    p, steps = descend(grad_bowl, np.array([4.0, 2.0]), rate)
    print(np.round(p, 6), steps)
'''
FILL_SOLUTION = '''import numpy as np


def descend(grad, p, rate, tol=1e-6, max_steps=10000):
    steps = 0
    g = grad(p)
    while np.linalg.norm(g) > tol and steps < max_steps:
        p = p - rate * g
        g = grad(p)
        steps += 1
    return p, steps
''' + FILL_TAIL
FILL_STARTER = FILL_SOLUTION.replace("    while np.linalg.norm(g) > tol and", "    while np.linalg.norm(g) > ... and").replace(
    "        p = p - rate * g\n", "        p = p - ... * g\n"
)
FILL_NO_REFRESH = FILL_SOLUTION.replace("        g = grad(p)\n        steps += 1", "        steps += 1")
FILL_OUT = out(FILL_SOLUTION)
print("fill:\n" + FILL_OUT)
assert FILL_OUT == "[0. 0.] 72\n[0. 0.] 151\n", FILL_OUT
assert out(FILL_NO_REFRESH) != FILL_OUT

# --- the write -------------------------------------------------------------------------------

WRITE_STARTER = '''import numpy as np

''' + EXACT + '''

def numeric_gradient(f, p, h=1e-6):
    grad = np.zeros(len(p))
    for i in range(len(p)):
        step = np.zeros(len(p))
        step[i] = h
        grad[i] = (f(p + step) - f(p - step)) / (2 * h)
    return grad
'''
WRITE_SOLUTION = WRITE_STARTER + '''

def mse(w):
    return np.mean((A @ w - z) ** 2)


def mse_gradient(w):
    return 2 / len(z) * (A.T @ (A @ w - z))


print(mse_gradient(np.zeros(3)))
for w in [np.zeros(3), np.array([1.0, 1.0, 1.0])]:
    print(np.allclose(mse_gradient(w), numeric_gradient(mse, w)))
'''
WRITE_OUT = out(WRITE_SOLUTION)
print("write:\n" + WRITE_OUT)
assert WRITE_OUT == "[-6.5 -7.  -7. ]\nTrue\nTrue\n", WRITE_OUT

# --- the build --------------------------------------------------------------------------------

BUILD_FUNCTIONS = '''def mse(A, w, z):
    return float(np.mean((A @ w - z) ** 2))


def gradient(A, w, z):
    return 2 / len(z) * (A.T @ (A @ w - z))


def fit_by_descent(A, z, rate, steps):
    w = np.zeros(A.shape[1])
    losses = []
    for step in range(steps):
        losses.append(mse(A, w, z))
        w = w - rate * gradient(A, w, z)
    return w, losses
'''
BUILD_SOLUTION = "import numpy as np\n\n\n" + BUILD_FUNCTIONS + "\n\n" + POINTS + '''w, losses = fit_by_descent(A, z, 0.1, 2000)
print("plane", np.round(w, 3))
print("lstsq agrees", np.allclose(w, np.linalg.lstsq(A, z)[0], atol=1e-4))
print("loss", round(losses[0], 4), round(losses[10], 4), round(losses[-1], 4))
'''
BUILD_OUT = out(BUILD_SOLUTION)
print("build:\n" + BUILD_OUT)
assert BUILD_OUT.startswith("plane [ 2.015 -1.035  3.024]\nlstsq agrees True\nloss "), BUILD_OUT
BUILD_ASCENT = BUILD_SOLUTION.replace("        w = w - rate * gradient(A, w, z)", "        w = w + rate * gradient(A, w, z)")
BUILD_NO_TWO_OVER_N = BUILD_SOLUTION.replace("    return 2 / len(z) * (A.T @ (A @ w - z))", "    return A.T @ (A @ w - z)")
BUILD_LOSS_AFTER = BUILD_SOLUTION.replace(
    "        losses.append(mse(A, w, z))\n        w = w - rate * gradient(A, w, z)",
    "        w = w - rate * gradient(A, w, z)\n        losses.append(mse(A, w, z))",
)

# --- the debug ----------------------------------------------------------------------------------

DEBUG_SOLUTION = "import numpy as np\n\n" + POINTS + '''

def loss(w):
    return np.mean((A @ w - z) ** 2)


def gradient(w):
    return 2 / len(z) * (A.T @ (A @ w - z))


w = np.zeros(3)
for step in range(2000):
    w = w - 0.1 * gradient(w)
print("plane", np.round(w, 3))
print("loss", round(float(loss(w)), 4))
'''
DEBUG_STARTER = DEBUG_SOLUTION.replace("np.mean((A @ w - z) ** 2)", "np.sum((A @ w - z) ** 2)").replace(
    "(A.T @ (A @ w - z))", "(A @ (A @ w - z))"
)
DEBUG_SHAPE_ONLY = DEBUG_SOLUTION.replace("np.mean((A @ w - z) ** 2)", "np.sum((A @ w - z) ** 2)")
DEBUG_OUT = out(DEBUG_SOLUTION)
print("debug:\n" + DEBUG_OUT)
assert DEBUG_OUT.startswith("plane [ 2.015 -1.035  3.024]\nloss 0.0"), DEBUG_OUT
assert BUILD_OUT.splitlines()[2].endswith(DEBUG_OUT.splitlines()[1].split()[1]), (BUILD_OUT, DEBUG_OUT)

# --- predict items -------------------------------------------------------------------------------

PREDICT_STEPS = '''import numpy as np

p = np.array([4.0, 2.0])
for step in range(3):
    grad = 2 * p
    p = p - 0.25 * grad
    print(p)
'''
PREDICT_STEPS_OUT = out(PREDICT_STEPS)
print("predict steps:\n" + PREDICT_STEPS_OUT)
assert PREDICT_STEPS_OUT == "[2. 1.]\n[1.  0.5]\n[0.5  0.25]\n", PREDICT_STEPS_OUT

REVIEW_STEPS = '''import numpy as np

p = np.array([1.0, 1.0])
for step in range(2):
    grad = np.array([2 * p[0], 6 * p[1]])
    p = p - 0.1 * grad
    print(p)
'''
REVIEW_STEPS_OUT = out(REVIEW_STEPS)
print("review steps:\n" + REVIEW_STEPS_OUT)
assert REVIEW_STEPS_OUT == "[0.8 0.4]\n[0.64 0.16]\n", REVIEW_STEPS_OUT

REVIEW_CODE_STARTER = '''import numpy as np


def grad(p):
    return 2 * p
'''
REVIEW_CODE_SOLUTION = REVIEW_CODE_STARTER + '''

def descend(grad, p, rate, steps):
    for step in range(steps):
        p = p - rate * grad(p)
    return p


print(descend(grad, np.array([4.0, 2.0]), 0.25, 3))
'''
REVIEW_CODE_OUT = out(REVIEW_CODE_SOLUTION)
print("review code:\n" + REVIEW_CODE_OUT)
assert REVIEW_CODE_OUT == "[0.5  0.25]\n", REVIEW_CODE_OUT

LOSS_LINE = BUILD_OUT.splitlines()[2]  # "loss 21.xxxx 0.xxxx 0.xxxx"
FINAL_LOSS = LOSS_LINE.split()[-1]
LOSS0 = f"{float(EXAMPLE_OUT.splitlines()[9].split()[0]):.2f}"
assert LOSS0 == "21.24", LOSS0

# =====================================================================================
# topic.yaml
# =====================================================================================

write(
    "topic.yaml",
    '''id: ml.calc.descent-in-many-dimensions
kind: topic
status: ready
title: "Gradient descent in many dimensions"
summary: "Stepping against the gradient with a learning rate, watching the loss, and fitting a plane by descent to compare with least squares."
prerequisites: [ml.calc.partials-and-gradient, ml.la.least-squares]
packages: [numpy]
estimated_minutes: 55
rev: 1
objectives:
  - "Write gradient descent for a function of several variables, with a learning rate and a stopping rule."
  - "Fit a plane by descent and compare the answer with the normal equations."
  - "Say what a learning rate too large and too small each do, and recognise each from the loss curve."
  - "Explain why descent slows near the bottom without being told to."
# Linked, never copied or embedded: 3Blue1Brown's videos are under the
# standard YouTube licence; Michael Nielsen's book is CC BY-NC 3.0; NumPy's
# documentation is under the NumPy licence (BSD-3-Clause).
resources:
  - title: "3Blue1Brown: Neural networks (Grant Sanderson), chapter 2: Gradient descent, how neural networks learn"
    url: https://www.3blue1brown.com/topics/neural-networks
    type: video
    use: link
    license: Standard YouTube licence (linked, not copied)
  - title: "Neural Networks and Deep Learning, chapter 1, the section Learning with gradient descent (Michael Nielsen)"
    url: https://neuralnetworksanddeeplearning.com/chap1.html#learning_with_gradient_descent
    type: reading
    use: link
    license: CC BY-NC 3.0 (linked, not copied)
  - title: "numpy.linalg.lstsq (the NumPy developers)"
    url: https://numpy.org/doc/stable/reference/generated/numpy.linalg.lstsq.html
    type: reading
    use: link
    license: BSD-3-Clause (NumPy documentation)
practice:
  - example-downhill-in-two-and-three-dimensions
  - parsons-descent-loop
  - mcq-which-rate-is-too-large
  - predict-three-steps
  - mcq-why-descent-slows
  - fill-descent-with-a-stopping-rule
  - write-mse-and-its-gradient
prove:
  build: build-fit-a-plane-by-descent
  debug: debug-plane-by-descent
  explain:
    prompt: |
      A teammate shows you three training runs of the same model. At a learning rate of 0.5 the loss goes 13.5, 40, 150, 600 and keeps climbing. At 0.0005 it goes 13.5, 13.46, 13.42, 13.38 and is still near 13 after hundreds of steps. At 0.05 it goes 13.5, 2.1, 0.4, 0.1, 0.05, 0.05, 0.05. In your own words: what does the learning rate trade off, and what is each curve telling you? Why does the healthy run slow down by itself near the end, when nobody changed the rate? And when you fitted a plane today, descent and the normal equations gave the same answer, so why does anyone use descent at all?
    rubric:
      - id: trade-off
        required: true
        description: "A large rate takes big steps that can overshoot the bottom and land higher, so the loss grows (the 0.5 run is diverging); a small rate is safe but crawls (the 0.0005 run); the 0.05 run falls fast and then flattens at the floor, which is what a good rate looks like."
      - id: self-slowing
        required: true
        description: "Each step is rate times the gradient, and the gradient shrinks to zero at the bottom, so the steps shrink by themselves as the loss flattens; the rate never changed."
      - id: why-descent
        required: true
        description: "The normal equations exist only because the plane is linear in its weights; most models (any network) have no formula for the minimum, and even for linear ones forming AᵀA can be too big; descent only needs the gradient, so the same loop trains anything differentiable."
      - id: floor
        required: false
        description: "The healthy run's loss settles at 0.05 rather than 0 because the data doesn't fit the model exactly; that floor is the least-squares residual, not a sign that descent stopped early."
    model_answer: |
      The learning rate is how far each step goes along the downhill direction, and it trades speed against safety. At 0.5 the steps are so long that each one jumps past the bottom and lands higher up the other side, and the next step, from a steeper place, jumps further still: the loss climbs, and the run is diverging. At 0.0005 every step is safe and tiny, so the loss creeps down by a few hundredths at a time and would need thousands of steps to arrive. At 0.05 the loss falls fast and then levels off at 0.05, which is what a good rate looks like; the 0.05 it settles at isn't zero because the data doesn't fit the model exactly, and that floor is the same residual least squares would leave. The healthy run slows down on its own because each step is the rate times the gradient, and the gradient is the slope, which shrinks to nothing at the bottom of the valley. Near the floor the slope is tiny, so the steps are tiny, with the rate untouched. As for why descent at all: the normal equations gave the plane in one line only because a plane is linear in its weights, so the minimum has a formula. A neural network has no such formula, and even a linear model with millions of rows and columns can make AᵀA too big to build. Descent asks only for the gradient, and the same loop that fitted the plane today will train anything whose loss has a derivative.
review_pool:
  - review-predict-two-steps
  - review-mcq-crawling
  - review-mcq-stopping-rule
  - review-mcq-descent-and-lstsq
  - review-descend
# What this topic teaches. Each question names the skills it tests, so a
# missed question can come back as a different one on the same skill
# (ADR-0011).
skills:
  - id: loop
    description: "Write gradient descent for several variables, with a learning rate and a stopping rule"
  - id: fit
    description: "Fit a linear model by descent on the mean squared error, and compare with the normal equations"
  - id: rate
    description: "Recognise a learning rate too large or too small from the loss curve"
  - id: slowing
    description: "Explain why descent slows near the bottom by itself, and when it has arrived"
''',
)

# =====================================================================================
# lesson.mdx
# =====================================================================================

write(
    "lesson.mdx",
    f'''<Intro>

Module 1 walked downhill on one knob, and Checkpoint 1 on two, with the slopes written out by hand. The last topic built the gradient. This topic is the loop that training runs on: step against the gradient, scaled by a **learning rate**, until the gradient is small; watch the loss as you go; and learn to read the loss curve, because the rate is the one number a learner tunes most. The worked example fits a plane this way and gets the same plane the normal equations gave in Module 3.

The main resource is **3Blue1Brown's _Neural networks_, chapter 2**, gradient descent, how neural networks learn, which draws the loss as a landscape and the gradient as the way down; 20 minutes. Michael Nielsen's free book has the same picture in text (chapter 1, _Learning with gradient descent_). Watch for:

- **The loss landscape:** one height for every setting of the knobs, and the gradient pointing uphill at every point.
- **The step is `-rate * gradient`:** against the slope, longer where it's steep.
- **Why "learning" is just this loop**, run on a loss with thousands of knobs.

</Intro>

<Resource index={{0}} />

<Recap>

- **The loop.** From a starting point `p`, repeat `p = p - rate * grad(p)`. In code the point is an array and the gradient is an array of the same shape, so one line updates every variable at once. The **learning rate** is the step scale; `0.1` is a usual first try.
- **A stopping rule.** Stop when the gradient's length is below a tolerance (`np.linalg.norm(g) < 1e-6`: flat, so arrived), or after a maximum number of steps (so a bad rate can't run forever). Count the steps; they're the first thing to look at when tuning.
- **Too small, too large.** On the bowl `x² + 3y²` from `(4, 2)`, ten steps at rate 0.1 leave a loss of 0.18; at 0.05 it's still 1.96 (crawling); at 0.4 it's over 10,000, because the step in `y` is `1 - 0.4 * 6 = -1.4` times the old value: each step overshoots the bottom and lands further up the other side. Too large **diverges**; too small **crawls**; the right one falls fast and then flattens.
- **Descent slows by itself.** The step is `rate * gradient`, and the gradient shrinks to zero at the bottom. Nobody changes the rate; the slope does. (Steps 0, 1, 2, 5, 10 on the bowl: 4, 3.2, 2.56, 1.31, 0.43 along `x`, each 0.8 of the last.)
- **Reading a loss curve.** Falling fast then flat: good. Climbing, or bouncing up and down: the rate is too large. Falling by a hair each step: too small. Flat from the start at a high value: a zero gradient (a bad start, or a bug in the gradient; check it numerically).
- **Fitting a plane by descent.** The loss is the mean squared error `np.mean((A @ w - z) ** 2)`, whose gradient is `2 / n * A.T @ (A @ w - z)`. Two thousand steps at rate 0.1 from `w = 0` give `[2.015, -1.035, 3.024]`, the plane `lstsq` returned in Module 3, and the loss settles at {FINAL_LOSS}: the floor the data leaves, not zero.
- **Why descent when a formula exists?** It doesn't, for most models: the normal equations need a loss that's quadratic in the weights. Descent only needs the gradient, so the same loop fits a plane today and a network in three topics' time.
- **In machine learning:** every optimizer in the next topics is this loop with a better step; every training script's `lr` is this `rate`; the loss curve on the dashboard is `losses` here.

</Recap>
''',
)

# =====================================================================================
# recall
# =====================================================================================

write(
    "recall/parsons-descent-loop.yaml",
    '''id: parsons-descent-loop
type: parsons
rev: 1
prompt: |
  Put the lines in order to run ten steps of gradient descent on `x² + 3y²` from `(4, 2)` with a learning rate of 0.1, printing `[0.429 0.   ]`. One line is a decoy that doesn't belong.
lines:
  - 'import numpy as np'
  - 'def grad(p):'
  - '    return np.array([2 * p[0], 6 * p[1]])'
  - 'p = np.array([4.0, 2.0])'
  - 'for step in range(10):'
  - '    p = p - 0.1 * grad(p)'
  - 'print(np.round(p, 3))'
distractors:
  - '    p = p + 0.1 * grad(p)'
explanation: |
  Descent steps **against** the gradient: `p - rate * grad(p)`. Each step multiplies `x` by `1 - 0.1 * 2 = 0.8` and `y` by `1 - 0.1 * 6 = 0.4`, so after ten steps `x` is `4 * 0.8 ** 10 = 0.429` and `y` has all but vanished. The decoy steps with the gradient, uphill, and the point runs away from the bottom.
skills: [loop]
''',
)

write(
    "recall/mcq-which-rate-is-too-large.yaml",
    '''id: mcq-which-rate-is-too-large
type: mcq
rev: 1
prompt: |
  Three runs of the same descent, with the loss after each of the first five steps:

  - Run A: 13.5, 4.1, 1.3, 0.5, 0.4
  - Run B: 13.5, 20.3, 31.0, 48.2, 75.6
  - Run C: 13.5, 13.4, 13.3, 13.2, 13.1

  Which run's learning rate is too large?
choices:
  - 'Run B: each step overshoots the bottom and lands higher than the last, so the loss climbs'
  - 'Run A: the loss changes too much per step to be safe'
  - 'Run C: the loss barely moves, so the steps must be huge'
  - 'None; a learning rate can only be too small'
answer: 0
explanation: |
  A climbing loss is the signature of a rate that's too large: the step jumps past the bottom to a higher point on the other side, and the next step, from a steeper place, jumps further. Run A is healthy, falling fast and then flattening. Run C is the opposite problem: a rate so small the loss creeps down by a tenth a step.
skills: [rate]
''',
)

write(
    "recall/predict-three-steps.yaml",
    f'''id: predict-three-steps
type: predict_output
rev: 1
prompt: |
  Three steps of gradient descent on `f(x, y) = x² + y²`, whose gradient is `2 * p`. What does the program print?
code: |
{block(PREDICT_STEPS)}expected_output: |
{block(PREDICT_STEPS_OUT)}explanation: |
  With rate 0.25 and gradient `2 * p`, each step subtracts `0.5 * p`, so the point halves: `(4, 2)` to `(2, 1)` to `(1, 0.5)` to `(0.5, 0.25)`. The steps shrink by themselves, from a length of about 2.2 to about 0.56, because the gradient shrinks as the point nears the bottom.
skills: [loop, slowing]
''',
)

write(
    "recall/mcq-why-descent-slows.yaml",
    '''id: mcq-why-descent-slows
type: mcq
rev: 1
prompt: |
  Nobody changes the learning rate during a run, yet the steps get shorter as descent nears the bottom. Why?
choices:
  - 'The step is `rate * gradient`, and the gradient shrinks towards zero as the surface flattens near the bottom'
  - 'NumPy reduces the step size automatically once the loss is small'
  - 'The learning rate is divided by the step number inside the loop'
  - 'It doesn''t; the steps stay the same length until the stopping rule fires'
answer: 0
explanation: |
  The gradient is the slope, and the bottom of a valley is flat. The update multiplies a fixed rate by a shrinking slope, so the steps shrink on their own: on the bowl, each step along `x` is 0.8 of the one before. Nothing in NumPy or the loop adjusts anything; schedules that do divide the rate by the step count exist (next topics), but this happens without them.
skills: [slowing]
''',
)

write(
    "recall/review-predict-two-steps.yaml",
    f'''id: review-predict-two-steps
type: predict_output
rev: 1
prompt: |
  Two steps of descent on `x² + 3y²` from `(1, 1)` at rate 0.1. What does the program print?
code: |
{block(REVIEW_STEPS)}expected_output: |
{block(REVIEW_STEPS_OUT)}explanation: |
  Each step multiplies `x` by `1 - 0.1 * 2 = 0.8` and `y` by `1 - 0.1 * 6 = 0.4`. The steeper direction, `y`, is the one that arrives first: the same rate takes a bigger bite where the slope is bigger.
skills: [loop]
''',
)

write(
    "recall/review-mcq-crawling.yaml",
    '''id: review-mcq-crawling
type: mcq
rev: 1
prompt: |
  A run set for 200 steps prints the loss after each of the first six: 13.5, 13.46, 13.42, 13.38, 13.34, 13.30. What is the most likely problem, and the fix?
choices:
  - 'The learning rate is too small, so descent is crawling; raise it (try ten times larger) and watch the curve again'
  - 'The learning rate is too large; lower it'
  - 'Descent has converged; stop the run'
  - 'The gradient is zero; check it numerically'
answer: 0
explanation: |
  A loss that falls by a hair each step, steadily, is a rate that's too small: the direction is right, the steps are tiny. Too large looks like climbing or bouncing; converged looks flat at a floor after a fall, not flat from the start; a zero gradient wouldn't move the loss at all.
skills: [rate]
''',
)

write(
    "recall/review-mcq-descent-and-lstsq.yaml",
    '''id: review-mcq-descent-and-lstsq
type: mcq
rev: 1
prompt: |
  You fit a plane to some points twice: with `np.linalg.lstsq`, and with two thousand steps of gradient descent on the mean squared error. The two answers agree to six decimals. Why?
choices:
  - 'Both minimize the same loss, the mean squared error; `lstsq` reaches the minimum in one step because that loss is quadratic in the weights, and descent walks to the same minimum because there is only one'
  - 'Descent copies its answer from `lstsq` internally'
  - 'It''s a coincidence of these points; on other points they would disagree'
  - 'They agree only because the learning rate was 0.1'
answer: 0
explanation: |
  A plane's mean squared error is a bowl in the weights, with one bottom. The normal equations and `lstsq` jump to it because a bowl's minimum has a formula; descent walks down to it. Any rate that converges arrives at the same place, only faster or slower. The reason to learn descent is the models whose loss has no formula for the bottom.
skills: [fit]
''',
)

write(
    "recall/review-mcq-stopping-rule.yaml",
    '''id: review-mcq-stopping-rule
type: mcq
rev: 1
prompt: |
  Which is a sound rule for when gradient descent should stop?
choices:
  - 'When the gradient''s length is below a small tolerance, or after a maximum number of steps, whichever comes first'
  - 'When the loss is exactly zero'
  - 'The first time the loss goes up'
  - 'After exactly 100 steps, whatever the problem'
answer: 0
explanation: |
  A tiny gradient means the surface is flat, so descent has arrived; the step cap means a bad rate can't run forever. The loss rarely reaches exactly zero (a plane through noisy points can't), one upward step can be a bounce that recovers, and a fixed count ignores whether the run has arrived.
skills: [loop, slowing]
''',
)

# =====================================================================================
# exercises
# =====================================================================================

write(
    "exercises/example-downhill-in-two-and-three-dimensions/exercise.yaml",
    f'''id: example-downhill-in-two-and-three-dimensions
stage: worked_example
rev: 1
title: "Downhill in two and three dimensions"
prompt: |
  This program walks down a bowl and prints the path, compares four learning rates, then fits a plane to six points by descent and checks it against `lstsq`. Press **Run**, then read how each part works.
steps:
  - label: "The bowl and its gradient"
    lines: "4-11"
    note: "`x² + 3y²`, the bowl from the last topic, with gradient `[2x, 6y]`. It's three times steeper in `y`, which is about to matter."
  - label: "The loop, and the path it takes"
    lines: "14-18"
    note: "One line, `p = p - 0.1 * grad_bowl(p)`, moves both coordinates at once. Each step multiplies `x` by 0.8 and `y` by 0.4, so `y` arrives almost at once and `x` takes its time: 4, 3.2, 2.56, 1.311, 0.429. The steps shrink on their own, because the gradient does; nobody touched the rate."
  - label: "Four learning rates"
    lines: "20-24"
    note: "After ten steps from the same start: 0.05 has barely begun (loss 1.96); 0.1 is well down (0.18); 0.3 is still fine; 0.4 has blown up past 10,000. At 0.4 the `y` step is `1 - 0.4 * 6 = -1.4` times the old value: each step overshoots the bottom and lands further up the far side. Too small crawls, too large diverges."
  - label: "A plane to fit, as a design matrix"
    lines: "26-36"
    note: "Module 3's six nearly planar points. `A` has a row per point (`x`, `y`, 1) and `z` is the target. The loss will be the mean squared error of `A @ w - z`, a bowl in three dimensions: one for each of `a`, `b`, `c`."
  - label: "Descent on the mean squared error"
    lines: "37-42"
    note: "`miss` is the vector of errors, the loss is the mean of their squares, and the gradient of that loss is `2 / n * A.T @ miss` (you'll derive and check it in the write exercise). Two thousand steps at rate 0.1 from all zeros. The loss falls from {LOSS0} and settles at {FINAL_LOSS} by step 100: the floor the data leaves, since no plane passes through all six points."
  - label: "The same plane least squares gave"
    lines: "43-45"
    note: "`[2.015, -1.035, 3.024]`, the plane `lstsq` returned in Module 3, to six decimals. The normal equations found it in one step because a plane is linear in its weights; descent found it with nothing but the gradient, which is why it works when there's no formula."
''',
)
write("exercises/example-downhill-in-two-and-three-dimensions/solution.py", EXAMPLE)
write(
    "exercises/example-downhill-in-two-and-three-dimensions/test_exercise.py",
    f'''from checks import run


def test_the_walkthrough():
    """Prints the path down the bowl, four rates compared, the plane fit's loss curve, the plane and the lstsq check."""
    assert run() == {EXAMPLE_OUT!r}
''',
)

write(
    "exercises/fill-descent-with-a-stopping-rule/exercise.yaml",
    f'''id: fill-descent-with-a-stopping-rule
stage: fill_in
rev: 1
title: "Descent with a stopping rule"
prompt: |
  `descend(grad, p, rate, tol, max_steps)` should step against the gradient until the gradient's length is below `tol` or `max_steps` have been taken, and return the point and the number of steps. Replace each `...` so the program prints:

  ```
{block(FILL_OUT)}  ```

  Both runs arrive (the point rounds to zero); the smaller rate needs about twice the steps. The program fails until every `...` is replaced.
hints:
  - "The loop runs while the gradient is still longer than the tolerance."
  - "The step is the rate times the gradient, subtracted."
skills: [loop, slowing]
''',
)
write("exercises/fill-descent-with-a-stopping-rule/starter.py", FILL_STARTER)
write("exercises/fill-descent-with-a-stopping-rule/solution.py", FILL_SOLUTION)
write(
    "exercises/fill-descent-with-a-stopping-rule/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints the arrival point and the step count for both rates."""
    printed = run()
    assert printed == {FILL_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_the_rule():
    """On x² + y² from (3, 4) at rate 0.25 it arrives in a few dozen steps; with max_steps=5 it stops at 5."""
    descend = function("descend")
    p, steps = descend(lambda p: 2 * p, np.array([3.0, 4.0]), 0.25)
    assert np.linalg.norm(p) < 1e-6
    assert 10 < steps < 100
    p5, steps5 = descend(lambda p: 2 * p, np.array([3.0, 4.0]), 0.25, 1e-6, 5)
    assert steps5 == 5
    assert np.allclose(p5, [3.0 * 0.5**5, 4.0 * 0.5**5])
''',
)
write("exercises/fill-descent-with-a-stopping-rule/wrong/stale-gradient.py", FILL_NO_REFRESH)
write(
    "exercises/fill-descent-with-a-stopping-rule/wrong/typed-in.py",
    '''import numpy as np


def descend(grad, p, rate, tol=1e-6, max_steps=10000):
    return np.zeros(2), 72


print("[0. 0.] 72")
print("[0. 0.] 151")
''',
)

write(
    "exercises/write-mse-and-its-gradient/exercise.yaml",
    f'''id: write-mse-and-its-gradient
stage: write
rev: 1
title: "The mean squared error and its gradient"
prompt: |
  The starter has a design matrix `A` (four points, a column of ones), targets `z`, and the numeric gradient from the last topic. Write two functions of the weights `w`:

  - `mse(w)`: the mean squared error, `np.mean((A @ w - z) ** 2)`.
  - `mse_gradient(w)`: its gradient by rule, `2 / n * A.T @ (A @ w - z)`, where `n` is the number of points.

  Then print the gradient at `w = np.zeros(3)`, and whether the rule agrees with the numeric gradient (`np.allclose`) at `np.zeros(3)` and at `np.array([1.0, 1.0, 1.0])`:

  ```
{block(WRITE_OUT)}  ```
hints:
  - "`A @ w - z` is the vector of misses, one per point."
  - "`len(z)` is `n`. The factor `2 / n` comes from differentiating the mean of squares: the 2 from the square, the `1 / n` from the mean."
skills: [fit]
''',
)
write("exercises/write-mse-and-its-gradient/starter.py", WRITE_STARTER)
write("exercises/write-mse-and-its-gradient/solution.py", WRITE_SOLUTION)
write(
    "exercises/write-mse-and-its-gradient/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints the gradient at zero and two Trues."""
    printed = run()
    assert printed == {WRITE_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_at_the_solution():
    """At the exact plane [2, -1, 3] the error is 0 and the gradient is zero; at [2, -1, 4] the error is 1."""
    mse = function("mse")
    mse_gradient = function("mse_gradient")
    assert abs(mse(np.array([2.0, -1.0, 3.0]))) < 1e-12
    assert np.abs(mse_gradient(np.array([2.0, -1.0, 3.0]))).max() < 1e-12
    assert abs(mse(np.array([2.0, -1.0, 4.0])) - 1.0) < 1e-12
    assert np.allclose(mse_gradient(np.array([2.0, -1.0, 4.0])), [1.5, 2.0, 2.0])
''',
)
write(
    "exercises/write-mse-and-its-gradient/wrong/no-two-over-n.py",
    WRITE_SOLUTION.replace("    return 2 / len(z) * (A.T @ (A @ w - z))", "    return A.T @ (A @ w - z)"),
)
write(
    "exercises/write-mse-and-its-gradient/wrong/typed-in.py",
    WRITE_STARTER + '''

def mse(w):
    return 0.0


def mse_gradient(w):
    return np.array([-6.5, -7.0, -7.0])


print("[-6.5 -7.  -7. ]")
print(True)
print(True)
''',
)

# --- the proof ----------------------------------------------------------------------------------

write(
    "exercises/build-fit-a-plane-by-descent/exercise.yaml",
    f'''id: build-fit-a-plane-by-descent
stage: build
rev: 1
title: "Fit a plane by descent"
prompt: |
  Starting from a blank editor, write the training loop for a linear model:

  - `mse(A, w, z)`: the mean squared error of the weights `w` on the design matrix `A` and targets `z`, as a float.
  - `gradient(A, w, z)`: its gradient, `2 / n * A.T @ (A @ w - z)`.
  - `fit_by_descent(A, z, rate, steps)`: starts from `w` all zeros, takes `steps` steps of `w = w - rate * gradient`, and returns `w` and a list `losses` with the loss **before** each step (so `losses[0]` is the loss at all zeros, and there are `steps` entries).

  Then build `A` and `z` from Module 3's six points, fit with rate 0.1 for 2000 steps, and print the plane rounded to 3 places, whether it agrees with `np.linalg.lstsq` (`np.allclose` with `atol=1e-4`), and the losses at steps 0, 10 and the last, rounded to 4:

  ```python
{block(POINTS)}  ```

  ```
{block(BUILD_OUT)}  ```

  The checks fit other points, including four that lie exactly on a plane, and compare your gradient with a numeric one.
skills: [fit, loop, rate]
''',
)
write("exercises/build-fit-a-plane-by-descent/starter.py", "")
write("exercises/build-fit-a-plane-by-descent/solution.py", BUILD_SOLUTION)
write(
    "exercises/build-fit-a-plane-by-descent/test_exercise.py",
    f'''import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).

X = np.array([[0.0, 0.0], [1.0, 0.0], [0.0, 1.0], [2.0, 3.0]])
A_EXACT = np.column_stack([X, np.ones(4)])
Z_EXACT = np.array([3.0, 5.0, 2.0, 4.0])


def test_the_output():
    """Prints the plane, the lstsq check and three losses."""
    assert run() == {BUILD_OUT!r}


def test_exact_plane():
    """Four points on z = 2x - y + 3: descent finds [2, -1, 3] to three decimals and the loss falls below 1e-6."""
    fit_by_descent = function("fit_by_descent")
    w, losses = fit_by_descent(A_EXACT, Z_EXACT, 0.1, 4000)
    assert np.allclose(w, [2.0, -1.0, 3.0], atol=1e-3)
    assert losses[-1] < 1e-6


def test_losses_start_at_zero_weights_and_never_rise():
    """losses[0] is the loss at all-zero weights (the mean of z squared), there is one entry per step, and the curve never rises."""
    fit_by_descent = function("fit_by_descent")
    w, losses = fit_by_descent(A_EXACT, Z_EXACT, 0.1, 300)
    assert len(losses) == 300
    assert abs(losses[0] - np.mean(Z_EXACT**2)) < 1e-9
    assert all(b <= a + 1e-12 for a, b in zip(losses, losses[1:]))


def test_gradient_matches_a_numeric_one():
    """gradient(A, w, z) agrees with a one-coordinate-at-a-time numeric gradient of mse."""
    mse = function("mse")
    gradient = function("gradient")
    w = np.array([0.5, -0.5, 1.0])
    numeric = np.zeros(3)
    for i in range(3):
        step = np.zeros(3)
        step[i] = 1e-6
        numeric[i] = (mse(A_EXACT, w + step, Z_EXACT) - mse(A_EXACT, w - step, Z_EXACT)) / 2e-6
    assert np.abs(gradient(A_EXACT, w, Z_EXACT) - numeric).max() < 1e-6
''',
)
write("exercises/build-fit-a-plane-by-descent/wrong/ascent.py", BUILD_ASCENT)
write("exercises/build-fit-a-plane-by-descent/wrong/no-two-over-n.py", BUILD_NO_TWO_OVER_N)
write("exercises/build-fit-a-plane-by-descent/wrong/loss-after-the-step.py", BUILD_LOSS_AFTER)
write(
    "exercises/build-fit-a-plane-by-descent/wrong/typed-in.py",
    "import numpy as np\n\n\n"
    + "def mse(A, w, z):\n    return 0.0\n\n\n"
    + "def gradient(A, w, z):\n    return np.zeros(3)\n\n\n"
    + "def fit_by_descent(A, z, rate, steps):\n    return np.array([2.015, -1.035, 3.024]), [0.0] * steps\n\n\n"
    + "".join(f"print({line!r})\n" for line in BUILD_OUT.splitlines()),
)

write(
    "exercises/debug-plane-by-descent/exercise.yaml",
    f'''id: debug-plane-by-descent
stage: debug
rev: 1
title: "A plane fit that won't run"
prompt: |
  This program fits a plane to six points by gradient descent and should print:

  ```
{block(DEBUG_OUT)}  ```

  It has two bugs. Run it: the first is a shape error inside `gradient`. The misses `A @ w - z` are one per point (six of them), and the gradient needs one number per **weight** (three), so the product that turns misses into a gradient must use `A.T`, not `A`. Fix that and the plane is right, but the loss printed is six times too large: look at how `loss` averages.
skills: [fit, loop]
''',
)
write("exercises/debug-plane-by-descent/starter.py", DEBUG_STARTER)
write("exercises/debug-plane-by-descent/solution.py", DEBUG_SOLUTION)
write(
    "exercises/debug-plane-by-descent/test_exercise.py",
    f'''import numpy as np

from checks import function, run

EXPECTED = {DEBUG_OUT!r}


def test_the_output():
    """Prints the plane and its loss."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\\n{{EXPECTED}}\\nYour program printed:\\n{{printed}}"


def test_loss_is_a_mean():
    """At the plane [2, -1, 4] (one unit too high everywhere) the loss is about 1 plus the floor, not six times that."""
    loss = function("loss")
    assert abs(float(loss(np.array([2.0, -1.0, 4.0]))) - float(loss(np.array([2.0, -1.0, 3.0]))) - 1.0) < 0.1


def test_gradient_shape():
    """The gradient has one entry per weight."""
    gradient = function("gradient")
    assert gradient(np.zeros(3)).shape == (3,)
''',
)
write("exercises/debug-plane-by-descent/wrong/shape-only.py", DEBUG_SHAPE_ONLY)
write(
    "exercises/debug-plane-by-descent/wrong/typed-in.py",
    "import numpy as np\n\n"
    + POINTS
    + "\n\ndef loss(w):\n    return 0.0\n\n\ndef gradient(w):\n    return np.zeros(3)\n\n\n"
    + "".join(f"print({line!r})\n" for line in DEBUG_OUT.splitlines()),
)

# --- review pool: a code exercise ---------------------------------------------------------------

write(
    "exercises/review-descend/exercise.yaml",
    f'''id: review-descend
stage: review_code
rev: 1
title: "A descent loop, from memory"
prompt: |
  Write `descend(grad, p, rate, steps)`, which takes `steps` steps of gradient descent from the array `p` and returns where it ends up, and print the result of three steps on `x² + y²` (the starter's `grad`) from `(4, 2)` at rate 0.25:

  ```
{block(REVIEW_CODE_OUT)}  ```
skills: [loop]
''',
)
write("exercises/review-descend/starter.py", REVIEW_CODE_STARTER)
write("exercises/review-descend/solution.py", REVIEW_CODE_SOLUTION)
write(
    "exercises/review-descend/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints [0.5  0.25]."""
    assert run() == {REVIEW_CODE_OUT!r}


def test_other_runs():
    """Ten steps at rate 0.1 on x² + y² from (1, 1) give (0.8 ** 10, 0.8 ** 10); zero steps give the start."""
    descend = function("descend")
    assert np.allclose(descend(lambda p: 2 * p, np.array([1.0, 1.0]), 0.1, 10), [0.8**10, 0.8**10])
    assert np.allclose(descend(lambda p: 2 * p, np.array([1.0, 1.0]), 0.1, 0), [1.0, 1.0])
''',
)
write(
    "exercises/review-descend/wrong/ascent.py",
    REVIEW_CODE_STARTER + '''

def descend(grad, p, rate, steps):
    for step in range(steps):
        p = p + rate * grad(p)
    return p


print(descend(grad, np.array([4.0, 2.0]), 0.25, 3))
''',
)
write(
    "exercises/review-descend/wrong/typed-in.py",
    REVIEW_CODE_STARTER + '''

def descend(grad, p, rate, steps):
    return np.array([0.5, 0.25])


print("[0.5  0.25]")
''',
)

print("ml.calc.descent-in-many-dimensions written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
