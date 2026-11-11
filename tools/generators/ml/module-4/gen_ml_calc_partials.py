"""Writes the topic ml.calc.partials-and-gradient (Module 4's second topic).
Run from the repository root under uv (python -m uv run python <this file>),
so every program's expected output is captured from CPython rather than
typed in. Files are written as bytes with LF endings."""

import pathlib
import subprocess
import sys

ROOT = pathlib.Path("content/topics/ml.calc.partials-and-gradient")


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


NUMERIC_GRADIENT = '''def numeric_gradient(f, p, h=1e-6):
    grad = np.zeros(len(p))
    for i in range(len(p)):
        step = np.zeros(len(p))
        step[i] = h
        grad[i] = (f(p + step) - f(p - step)) / (2 * h)
    return grad
'''

# --- the worked example -----------------------------------------------------------

EXAMPLE = '''import numpy as np


def f(p):
    x, y = p
    return x**2 + 3 * y**2


def gradient(p):
    x, y = p
    return np.array([2 * x, 6 * y])


''' + NUMERIC_GRADIENT + '''

p = np.array([1.0, 1.0])
g = gradient(p)
print(g)
print(np.round(numeric_gradient(f, p), 6))
print(np.allclose(g, numeric_gradient(f, p)))

uphill = g / np.linalg.norm(g)
print(np.round(uphill, 3), round(float(np.linalg.norm(g)), 3))
along = np.array([-6.0, 2.0]) / np.linalg.norm([-6.0, 2.0])
print(round(float(g @ uphill), 3), round(float(g @ along), 3) + 0.0)
print(round(f(p + 0.01 * uphill) - f(p), 4), round(f(p + 0.01 * along) - f(p), 4))
'''
EXAMPLE_OUT = out(EXAMPLE)
print("example:\n" + numbered(EXAMPLE) + EXAMPLE_OUT)
assert EXAMPLE_OUT.startswith("[2. 6.]\n[2. 6.]\nTrue\n"), EXAMPLE_OUT

# --- the fill-in -------------------------------------------------------------------

FILL_TAIL = '''

print(np.round(numeric_gradient(lambda p: p[0] ** 2 + 3 * p[1] ** 2, np.array([1.0, 1.0])), 6))
print(np.round(numeric_gradient(lambda p: p[0] * p[1], np.array([2.0, 3.0])), 6))
print(np.round(numeric_gradient(lambda p: p[0] * p[1] ** 2 + p[2], np.array([1.0, 2.0, 5.0])), 6))
'''
FILL_SOLUTION = "import numpy as np\n\n\n" + NUMERIC_GRADIENT + FILL_TAIL
FILL_STARTER = FILL_SOLUTION.replace("        step[i] = h\n", "        step[i] = ...\n").replace(
    "/ (2 * h)", "/ (... * h)"
)
FILL_ALL_AT_ONCE = FILL_SOLUTION.replace(
    "        step = np.zeros(len(p))\n        step[i] = h\n        grad[i] = (f(p + step) - f(p - step)) / (2 * h)",
    "        grad[i] = (f(p + h) - f(p - h)) / (2 * h)",
)
FILL_OUT = out(FILL_SOLUTION)
print("fill:\n" + FILL_OUT)
assert FILL_OUT == "[2. 6.]\n[3. 2.]\n[4. 4. 1.]\n", FILL_OUT
assert out(FILL_ALL_AT_ONCE) != FILL_OUT

# --- the write ----------------------------------------------------------------------

WRITE_STARTER = '''import numpy as np

grad = np.array([3.0, 4.0])
'''
WRITE_SOLUTION = WRITE_STARTER + '''

def steepest_ascent(grad):
    return grad / np.linalg.norm(grad)


def directional_derivative(grad, direction):
    return grad @ direction / np.linalg.norm(direction)


print(steepest_ascent(grad))
for direction in [np.array([1.0, 0.0]), np.array([-4.0, 3.0]), grad]:
    print(round(float(directional_derivative(grad, direction)), 6) + 0.0)
'''
WRITE_OUT = out(WRITE_SOLUTION)
print("write:\n" + WRITE_OUT)
assert WRITE_OUT == "[0.6 0.8]\n3.0\n0.0\n5.0\n", WRITE_OUT

# --- the build ---------------------------------------------------------------------------

BUILD_SOLUTION = "import numpy as np\n\n\n" + NUMERIC_GRADIENT + '''

def check_gradient(f, grad_f, points):
    return max(np.abs(grad_f(p) - numeric_gradient(f, p)).max() for p in points)


def steepest(grad):
    return grad / np.linalg.norm(grad)


def f(p):
    x, y, z = p
    return x**2 + y * z + z**3


def grad_f(p):
    x, y, z = p
    return np.array([2 * x, z, y + 3 * z**2])


points = [np.array([1.0, 2.0, 3.0]), np.array([0.0, -1.0, 2.0])]
print("gradient", grad_f(points[0]))
print("gap below 1e-6", check_gradient(f, grad_f, points) < 1e-6)
print("steepest", np.round(steepest(grad_f(points[0])), 3))
'''
BUILD_OUT = out(BUILD_SOLUTION)
print("build:\n" + BUILD_OUT)
assert BUILD_OUT == "gradient [ 2.  3. 29.]\ngap below 1e-6 True\nsteepest [0.068 0.103 0.992]\n", BUILD_OUT
BUILD_FORWARD = BUILD_SOLUTION.replace(
    "        grad[i] = (f(p + step) - f(p - step)) / (2 * h)", "        grad[i] = (f(p + step) - f(p)) / h"
)
assert out(BUILD_FORWARD) != BUILD_OUT, "the forward difference must visibly fail"

# --- the debug -----------------------------------------------------------------------------

DEBUG_SOLUTION = '''import numpy as np


def f(p):
    x, y = p
    return x**2 + 3 * y**2


''' + NUMERIC_GRADIENT + '''

def directional_derivative(grad, direction):
    return grad @ direction / np.linalg.norm(direction)


p = np.array([1.0, 1.0])
g = numeric_gradient(f, p)
print("gradient", np.round(g, 6))
print("east", round(float(directional_derivative(g, np.array([2.0, 0.0]))), 3))
print("north-east", round(float(directional_derivative(g, np.array([3.0, 3.0]))), 3))
'''
DEBUG_STARTER = DEBUG_SOLUTION.replace(
    "    grad = np.zeros(len(p))\n    for i in range(len(p)):\n        step = np.zeros(len(p))\n",
    "    grad = np.zeros(len(p))\n    step = np.zeros(len(p))\n    for i in range(len(p)):\n",
).replace("    return grad @ direction / np.linalg.norm(direction)", "    return grad @ direction")
DEBUG_STEP_ONLY = DEBUG_SOLUTION.replace(
    "    return grad @ direction / np.linalg.norm(direction)", "    return grad @ direction"
)
DEBUG_OUT = out(DEBUG_SOLUTION)
print("debug:\n" + DEBUG_OUT + "--- buggy prints:\n" + out(DEBUG_STARTER))
assert DEBUG_OUT == "gradient [2. 6.]\neast 2.0\nnorth-east 5.657\n", DEBUG_OUT
assert out(DEBUG_STARTER).startswith("gradient [2. 8.]\n"), out(DEBUG_STARTER)

# --- predict items ----------------------------------------------------------------------------

PREDICT_PRODUCT = '''import numpy as np


def grad(p):
    return np.array([p[1] + 2 * p[0], p[0]])


p = np.array([1.0, 4.0])
g = grad(p)
print(g)
print(round(float(np.linalg.norm(g)), 3))
print(np.round(g / np.linalg.norm(g), 3))
'''
PREDICT_PRODUCT_OUT = out(PREDICT_PRODUCT)
print("predict product:\n" + PREDICT_PRODUCT_OUT)
assert PREDICT_PRODUCT_OUT == "[6. 1.]\n6.083\n[0.986 0.164]\n", PREDICT_PRODUCT_OUT

REVIEW_PARTIALS = '''import numpy as np


def grad(p):
    x, y = p
    return np.array([2 * x * y, x**2])


print(grad(np.array([3.0, 2.0])))
print(grad(np.array([3.0, 0.0])))
'''
REVIEW_PARTIALS_OUT = out(REVIEW_PARTIALS)
print("review partials:\n" + REVIEW_PARTIALS_OUT)
assert REVIEW_PARTIALS_OUT == "[12.  9.]\n[0. 9.]\n", REVIEW_PARTIALS_OUT

REVIEW_CODE_STARTER = '''import numpy as np


def f(p):
    x, y = p
    return x**2 + 3 * y**2
'''
REVIEW_CODE_SOLUTION = REVIEW_CODE_STARTER + "\n\n" + NUMERIC_GRADIENT + '''

print(np.round(numeric_gradient(f, np.array([1.0, 1.0])), 6))
'''
REVIEW_CODE_OUT = out(REVIEW_CODE_SOLUTION)
print("review code:\n" + REVIEW_CODE_OUT)
assert REVIEW_CODE_OUT == "[2. 6.]\n", REVIEW_CODE_OUT

# =====================================================================================
# topic.yaml
# =====================================================================================

write(
    "topic.yaml",
    '''id: ml.calc.partials-and-gradient
kind: topic
status: ready
title: "Partial derivatives and the gradient"
summary: "Functions of several variables, partial derivatives by holding the rest fixed, and the gradient as the vector that points uphill fastest."
prerequisites: [ml.calc.derivatives, ml.la.vectors]
packages: [numpy]
estimated_minutes: 50
rev: 1
objectives:
  - "Take a partial derivative by holding the other variables fixed."
  - "Assemble the gradient as a vector, and check it against finite differences."
  - "Say why the gradient points in the direction of steepest ascent, and what its length means."
  - "Read a contour picture: the gradient is perpendicular to the contours."
# Linked, never copied or embedded: Khan Academy is CC BY-NC-SA 3.0 US;
# OpenStax is CC BY 4.0; NumPy's documentation is under the NumPy licence
# (BSD-3-Clause).
resources:
  - title: "Khan Academy: Multivariable calculus, partial derivatives and the gradient (Grant Sanderson)"
    url: https://www.khanacademy.org/math/multivariable-calculus/multivariable-derivatives
    type: video
    use: link
    license: CC BY-NC-SA 3.0 US (linked, not copied)
  - title: "OpenStax Calculus Volume 3: sections 4.3 (Partial Derivatives) and 4.6 (Directional Derivatives and the Gradient)"
    url: https://openstax.org/details/books/calculus-volume-3
    type: reading
    use: link
    license: CC BY 4.0
  - title: "numpy.zeros (the NumPy developers)"
    url: https://numpy.org/doc/stable/reference/generated/numpy.zeros.html
    type: reading
    use: link
    license: BSD-3-Clause (NumPy documentation)
practice:
  - example-gradient-of-a-bowl
  - parsons-numeric-gradient
  - mcq-what-a-partial-holds-fixed
  - predict-gradient-and-its-length
  - mcq-gradient-and-contours
  - fill-numeric-gradient
  - write-steepest-ascent
prove:
  build: build-gradient-check
  debug: debug-gradient-routine
  explain:
    prompt: |
      A model's loss depends on two weights, and your training code computes `grad = [dL/dw1, dL/dw2]` and steps against it. A teammate asks what that vector is. In your own words: what is a partial derivative, and what is held fixed while you take it? Why does the gradient point in the direction the loss rises fastest, and what does its length tell you? Why is it perpendicular to the loss's contour lines (the curves along which the loss doesn't change)? And what is the first thing you'd do if you suspected a hand-written gradient was wrong?
    rubric:
      - id: partial
        required: true
        description: "A partial derivative is the ordinary derivative with respect to one variable while every other variable is held fixed at its current value; the gradient is the vector of all of them."
      - id: steepest
        required: true
        description: "The rate of change along a unit direction u is the dot product grad . u, which is largest when u points along the gradient; so the gradient is the uphill direction and its length is that largest rate (how steep the steepest way is)."
      - id: contours
        required: true
        description: "Along a contour the function doesn't change, so grad . u = 0 for a direction u along the contour: the gradient is perpendicular to it (and descent, which steps against the gradient, crosses contours at right angles)."
      - id: check
        required: false
        description: "Compare it with finite differences: nudge one weight at a time by a small h, both ways, and divide; a gap in the sixth decimal means the formula is wrong."
    model_answer: |
      With two weights, the loss is a surface over the plane of weights, and a partial derivative is its slope in one of the two directions: change w1 a little while w2 stays exactly where it is, and see how fast the loss moves; then the same for w2 with w1 fixed. The gradient is those two slopes stacked into a vector. To see why it points uphill fastest, ask how fast the loss changes if you walk in some unit direction u. The answer is the dot product of the gradient with u, and a dot product with a unit vector is largest when the vector points the same way as the gradient. So the gradient is the direction of steepest rise, and its length is that steepest rate: how much the loss changes per unit step in that direction. A contour line is a curve along which the loss doesn't change at all, so walking along it gives a rate of zero, which means the dot product of the gradient with that direction is zero: the gradient is perpendicular to the contour. Descent steps against the gradient, so it crosses contours at right angles, straight towards lower ones. If I thought a hand-written gradient was wrong, I'd check it numerically before anything else: nudge one weight at a time by a small h, up and down, divide the change in loss by 2h, and compare each entry with the formula. Anything beyond the sixth decimal is a bug in the formula, not in the training.
review_pool:
  - review-predict-partials
  - review-mcq-zero-gradient
  - review-mcq-steepest-descent
  - review-numeric-gradient
# What this topic teaches. Each question names the skills it tests, so a
# missed question can come back as a different one on the same skill
# (ADR-0011).
skills:
  - id: partial
    description: "Take a partial derivative by holding the other variables fixed"
  - id: gradient
    description: "Assemble the gradient and check it against finite differences, one coordinate at a time"
  - id: direction
    description: "Read the gradient as the steepest-ascent direction and its length as the rate"
  - id: contours
    description: "Use the directional derivative, and know the gradient is perpendicular to the contours"
''',
)

# =====================================================================================
# lesson.mdx
# =====================================================================================

write(
    "lesson.mdx",
    '''<Intro>

A model's loss doesn't depend on one knob; it depends on thousands. The last topic's derivatives were slopes along one axis. This topic puts them together: the slope along each axis with the others held still is a **partial derivative**, the vector of all of them is the **gradient**, and the gradient is the direction in which the loss rises fastest. Training steps the other way. Every claim here is checked in code, one coordinate at a time.

The main resource is **Khan Academy's multivariable calculus** unit on partial derivatives and the gradient, made by Grant Sanderson of 3Blue1Brown: the videos _Partial derivatives, introduction_, _Gradient_, _Gradient and graphs_, _Directional derivative_ and _Why the gradient is the direction of steepest ascent_; about 40 minutes. OpenStax _Calculus Volume 3_, sections 4.3 and 4.6, is the same ground as text. Watch for:

- **Holding the rest fixed:** a partial derivative treats every other variable as a constant.
- **The gradient as a vector field:** at every point, an arrow pointing uphill, longer where the hill is steeper.
- **Contour lines:** the curves along which the function doesn't change, and the arrows cross them at right angles.

</Intro>

<Resource index={0} />

<Recap>

- **Several inputs, one output.** `f(x, y) = x² + 3y²` is a bowl over the plane, steeper in `y`. In code a point is an array `p = np.array([x, y])` and `f(p)` returns one number; a loss is this with thousands of entries in `p`.
- **A partial derivative** is the derivative with respect to one variable while the others are held fixed: `∂f/∂x = 2x` (treat `y` as a constant), `∂f/∂y = 6y`. The curly `∂` just says "one variable of several".
- **The gradient** stacks the partials into a vector: `∇f = [2x, 6y]`, so `[2, 6]` at `(1, 1)`. Its **direction** is the way `f` rises fastest from that point; its **length** (6.325 there) is how fast `f` rises per unit step in that direction.
- **Checking it numerically**, one coordinate at a time: nudge entry `i` by `h` up and down, leaving the others alone, and take the central difference. In code: a `step` array of zeros with `h` in slot `i`, `(f(p + step) - f(p - step)) / (2 * h)`. Nudging every entry at once gives the sum of the partials, which is wrong.
- **The directional derivative:** the rate of change along a **unit** direction `u` is `∇f · u`. Along the gradient's own direction it's the gradient's length; along a direction perpendicular to the gradient it's zero. Divide a direction by its length before using it, or the answer scales with the arrow you drew.
- **Contours.** A contour line (a height line on a map) is a curve along which `f` doesn't change. Along it the rate is zero, so the gradient is **perpendicular** to the contour through the point. Descent, stepping against the gradient, crosses contours at right angles towards lower ones.
- **Where the gradient is zero,** the surface is flat: the bottom of a bowl, the top of a hill, or a saddle. Descent stops moving there, which is what it's looking for.
- **In machine learning:** the backward pass of a network computes exactly this, the gradient of the loss with respect to every weight, and every optimizer in the next topics is a rule for stepping against it. A numeric gradient check is the standard way to prove a hand-written one is right before training on it.

</Recap>
''',
)

# =====================================================================================
# recall
# =====================================================================================

write(
    "recall/parsons-numeric-gradient.yaml",
    '''id: parsons-numeric-gradient
type: parsons
rev: 1
prompt: |
  Put the lines in order to estimate the gradient of `f(x, y) = x * y` at `(2, 3)` one coordinate at a time, printing `[3. 2.]`. One line is a decoy that doesn't belong.
lines:
  - 'import numpy as np'
  - 'def f(p):'
  - '    return p[0] * p[1]'
  - 'p = np.array([2.0, 3.0])'
  - 'h = 1e-6'
  - 'dx = (f(p + [h, 0]) - f(p - [h, 0])) / (2 * h)'
  - 'dy = (f(p + [0, h]) - f(p - [0, h])) / (2 * h)'
  - 'print(np.round([dx, dy], 6))'
distractors:
  - 'dy = (f(p + [h, h]) - f(p - [h, h])) / (2 * h)'
explanation: |
  Each partial derivative nudges **one** coordinate and leaves the other alone: `[h, 0]` for the slope in `x`, `[0, h]` for the slope in `y`. With `f = x * y`, the slope in `x` is `y = 3` and the slope in `y` is `x = 2`. The decoy nudges both at once, which measures the slope along the diagonal, `3 + 2 = 5`, not the partial derivative in `y`.
skills: [gradient, partial]
''',
)

write(
    "recall/mcq-what-a-partial-holds-fixed.yaml",
    '''id: mcq-what-a-partial-holds-fixed
type: mcq
rev: 1
prompt: |
  `f(x, y) = x² y + y³`. What is the partial derivative with respect to `x`, at the point `(2, 3)`?
choices:
  - '12: treat `y` as a constant, so the derivative of `x² y` is `2 x y` and `y³` contributes nothing'
  - '31: `x² + 3 y²`'
  - '43: `2 x y + x² + 3 y²`'
  - '4: `2 x`'
answer: 0
explanation: |
  Holding `y` fixed, `x² y` is a constant times `x²`, whose derivative is `2 x y = 12`, and `y³` is a constant, whose derivative is 0. The 31 is the **other** partial, with respect to `y` (`x² + 3 y²`); the 43 adds both; the 4 forgot the constant `y` multiplying `x²`.
skills: [partial]
''',
)

write(
    "recall/predict-gradient-and-its-length.yaml",
    f'''id: predict-gradient-and-its-length
type: predict_output
rev: 1
prompt: |
  `grad` is the gradient of `f(x, y) = x y + x²`. What does the program print?
code: |
{block(PREDICT_PRODUCT)}expected_output: |
{block(PREDICT_PRODUCT_OUT)}explanation: |
  At `(1, 4)` the partial in `x` is `y + 2x = 6` and the partial in `y` is `x = 1`, so the gradient is `[6, 1]`. Its length, `sqrt(37) = 6.083`, is how fast `f` rises per unit step in the steepest direction, and dividing by it gives that direction as a unit vector: almost all `x`, a little `y`.
skills: [gradient, direction]
''',
)

write(
    "recall/mcq-gradient-and-contours.yaml",
    '''id: mcq-gradient-and-contours
type: mcq
rev: 1
prompt: |
  You stand on a hillside where the gradient of the height is `(3, 0)`: an arrow pointing east, of length 3. Which is true?
choices:
  - 'Walking east the height rises fastest, 3 metres per metre walked; walking north or south it doesn''t change at first, because the contour line through you runs north to south, perpendicular to the gradient'
  - 'Walking north the height rises fastest, because the gradient points along the contour line'
  - 'The height at that point is 3 metres'
  - 'The hill is flat there, because one entry of the gradient is 0'
answer: 0
explanation: |
  The gradient points uphill and its length is the steepest rate, so east is up at 3 per unit. The rate in any unit direction is the dot product with the gradient: `(3, 0) · (0, 1) = 0` going north, so the contour, the line of no change, runs north to south, at right angles to the gradient. The gradient says nothing about the height itself, only about how it changes; and a hill is flat only where **both** entries are zero.
skills: [contours, direction]
''',
)

write(
    "recall/review-predict-partials.yaml",
    f'''id: review-predict-partials
type: predict_output
rev: 1
prompt: |
  `grad` is the gradient of `f(x, y) = x² y`. What does the program print?
code: |
{block(REVIEW_PARTIALS)}expected_output: |
{block(REVIEW_PARTIALS_OUT)}explanation: |
  Holding `y` fixed, `x² y` has derivative `2 x y`; holding `x` fixed, it has derivative `x²`. At `(3, 2)` that's `[12, 9]`. At `(3, 0)` the first partial is 0 (there's no `y` to multiply) while the second is still 9: the function doesn't change in `x` there, but it does in `y`.
skills: [partial, gradient]
''',
)

write(
    "recall/review-mcq-zero-gradient.yaml",
    '''id: review-mcq-zero-gradient
type: mcq
rev: 1
prompt: |
  During training, the gradient of the loss comes out as exactly `[0, 0]`. What does that tell you?
choices:
  - 'The surface is flat there: the bottom of a valley, the top of a hill, or a saddle; a descent step of `-rate * grad` moves nowhere'
  - 'The loss is zero'
  - 'The learning rate is too small'
  - 'The weights are both zero'
answer: 0
explanation: |
  The gradient is a slope, not a height: zero slope means flat, whatever the loss's value. Flat can be a minimum (what descent hopes for), a maximum, or a saddle that is a minimum one way and a maximum another. Either way the update `-rate * grad` is zero, so descent stops moving, whatever the rate.
skills: [direction]
''',
)

write(
    "recall/review-mcq-steepest-descent.yaml",
    '''id: review-mcq-steepest-descent
type: mcq
rev: 1
prompt: |
  At the current weights the gradient of the loss is `[3, -4]`. Which unit direction lowers the loss fastest?
choices:
  - '`[-0.6, 0.8]`: against the gradient, scaled to length 1'
  - '`[0.6, -0.8]`: along the gradient, scaled to length 1'
  - '`[-4, 3]`: perpendicular to the gradient'
  - '`[-3, 4]`: it must not be scaled, or the step is wrong'
answer: 0
explanation: |
  The gradient points uphill fastest, so straight downhill is its opposite, `[-3, 4]`, and as a unit direction that's `[-3, 4] / 5 = [-0.6, 0.8]`. Perpendicular to the gradient is along the contour, where the loss doesn't change at all. Gradient descent takes the direction `-grad` with its length too; the question asked for the unit direction.
skills: [direction, contours]
''',
)

# =====================================================================================
# exercises
# =====================================================================================

write(
    "exercises/example-gradient-of-a-bowl/exercise.yaml",
    f'''id: example-gradient-of-a-bowl
stage: worked_example
rev: 1
title: "The gradient of a bowl"
prompt: |
  This program takes the gradient of `f(x, y) = x² + 3y²` by rule, checks it one coordinate at a time, and then walks a little uphill and a little along the contour. Press **Run**, then read how each part works.
steps:
  - label: "A bowl and its two partials"
    lines: "4-11"
    note: "`f` takes a point as an array and returns one number: a bowl over the plane, three times steeper in `y`. The partial in `x` treats `y` as a constant: `2x`. The partial in `y` treats `x` as a constant: `6y`. `gradient` stacks the two into a vector."
  - label: "The numeric check, one coordinate at a time"
    lines: "14-20"
    note: "For each slot `i`, `step` is all zeros except `h` in that slot, so `p + step` nudges one coordinate and leaves the rest alone. The central difference of the last topic then gives that one partial. Nudging every coordinate at once would give the sum of the partials, which is wrong."
  - label: "Rule against check"
    lines: "23-27"
    note: "At `(1, 1)` the rule says `[2, 6]`, the numeric gradient agrees to six decimals, and `np.allclose` says so in one word."
  - label: "The steepest direction and the rate"
    lines: "29-30"
    note: "Dividing the gradient by its length gives a unit vector, the direction in which `f` rises fastest from `(1, 1)`: `[0.316, 0.949]`, mostly `y`, because the bowl is steeper that way. The length, 6.325, is the rate of rise per unit step in that direction."
  - label: "Along the contour"
    lines: "31-32"
    note: "`[-6, 2]` is perpendicular to `[2, 6]` (their dot product is 0), so it points along the contour, the curve where `f` stays the same. The rate of change in a unit direction is the dot product with the gradient: 6.325 straight uphill, 0 along the contour."
  - label: "Walking a little each way"
    lines: "33"
    note: "A step of 0.01 uphill raises `f` by 0.0635, close to `0.01 * 6.325`; the same step along the contour raises it by 0.0001, nearly nothing (the contour curves a little, so it isn't exactly zero). That's what the two dot products predicted."
''',
)
write("exercises/example-gradient-of-a-bowl/solution.py", EXAMPLE)
write(
    "exercises/example-gradient-of-a-bowl/test_exercise.py",
    f'''from checks import run


def test_the_walkthrough():
    """Prints the gradient by rule and by check, the steepest direction and rate, two dot products, and two small walks."""
    assert run() == {EXAMPLE_OUT!r}
''',
)

write(
    "exercises/fill-numeric-gradient/exercise.yaml",
    f'''id: fill-numeric-gradient
stage: fill_in
rev: 1
title: "A numeric gradient"
prompt: |
  `numeric_gradient(f, p, h)` should estimate every partial derivative of `f` at the point `p`, nudging one coordinate at a time with the central difference. Replace each `...` so the program prints:

  ```
{block(FILL_OUT)}  ```

  The program fails until every `...` is replaced.
hints:
  - "`step` starts as zeros; slot `i` should hold the nudge, `h`."
  - "The two nudged points are `2 * h` apart."
skills: [gradient]
''',
)
write("exercises/fill-numeric-gradient/starter.py", FILL_STARTER)
write("exercises/fill-numeric-gradient/solution.py", FILL_SOLUTION)
write(
    "exercises/fill-numeric-gradient/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints the three gradients."""
    printed = run()
    assert printed == {FILL_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_another_function():
    """For f = x y² + exp(z) at (1, 2, 0) the gradient is [4, 4, 1], to six decimals."""
    numeric_gradient = function("numeric_gradient")
    g = numeric_gradient(lambda p: p[0] * p[1] ** 2 + np.exp(p[2]), np.array([1.0, 2.0, 0.0]))
    assert np.abs(g - [4.0, 4.0, 1.0]).max() < 1e-6
''',
)
write("exercises/fill-numeric-gradient/wrong/all-at-once.py", FILL_ALL_AT_ONCE)
write(
    "exercises/fill-numeric-gradient/wrong/typed-in.py",
    '''import numpy as np


def numeric_gradient(f, p, h=1e-6):
    return np.zeros(len(p)) + 2.0


print("[2. 6.]")
print("[3. 2.]")
print("[4. 4. 1.]")
''',
)

write(
    "exercises/write-steepest-ascent/exercise.yaml",
    f'''id: write-steepest-ascent
stage: write
rev: 1
title: "Steepest ascent and the rate in a direction"
prompt: |
  The starter has a gradient, `[3, 4]`. Write two functions:

  - `steepest_ascent(grad)` returns the unit vector pointing along the gradient.
  - `directional_derivative(grad, direction)` returns the rate of change along `direction`, which may have any length: the dot product of `grad` with `direction` **scaled to length 1**.

  Then print the steepest-ascent direction, and the directional derivative along `[1, 0]`, along `[-4, 3]` and along `grad` itself, each as `round(float(...), 6) + 0.0` (the `+ 0.0` turns a `-0.0` into `0.0`):

  ```
{block(WRITE_OUT)}  ```
hints:
  - "A vector divided by `np.linalg.norm` of itself has length 1."
  - "Divide the direction by its length, or divide the dot product by it; either way the rate along `[-4, 3]` comes out 0, because it's perpendicular to the gradient."
skills: [direction, contours]
''',
)
write("exercises/write-steepest-ascent/starter.py", WRITE_STARTER)
write("exercises/write-steepest-ascent/solution.py", WRITE_SOLUTION)
write(
    "exercises/write-steepest-ascent/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints the unit direction, then rates of 3, 0 and 5."""
    printed = run()
    assert printed == {WRITE_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_other_gradients():
    """Unit length for another gradient; the rate along a direction of length 10 is the same as along length 1."""
    steepest_ascent = function("steepest_ascent")
    directional_derivative = function("directional_derivative")
    g = np.array([1.0, 2.0, 2.0])
    assert np.allclose(steepest_ascent(g), [1 / 3, 2 / 3, 2 / 3])
    assert abs(directional_derivative(g, np.array([0.0, 10.0, 0.0])) - 2.0) < 1e-9
    assert abs(directional_derivative(g, np.array([0.0, 1.0, 0.0])) - 2.0) < 1e-9
    assert abs(directional_derivative(g, np.array([2.0, -1.0, 0.0]))) < 1e-9
''',
)
write(
    "exercises/write-steepest-ascent/wrong/not-scaled.py",
    WRITE_STARTER + '''

def steepest_ascent(grad):
    return grad / np.linalg.norm(grad)


def directional_derivative(grad, direction):
    return grad @ direction


print(steepest_ascent(grad))
for direction in [np.array([1.0, 0.0]), np.array([-4.0, 3.0]), grad]:
    print(round(float(directional_derivative(grad, direction)), 6) + 0.0)
''',
)
write(
    "exercises/write-steepest-ascent/wrong/typed-in.py",
    WRITE_STARTER + '''

def steepest_ascent(grad):
    return np.array([0.6, 0.8])


def directional_derivative(grad, direction):
    return 3.0


print("[0.6 0.8]")
print(3.0)
print(0.0)
print(5.0)
''',
)

# --- the proof -----------------------------------------------------------------------------

write(
    "exercises/build-gradient-check/exercise.yaml",
    f'''id: build-gradient-check
stage: build
rev: 1
title: "A gradient check"
prompt: |
  Starting from a blank editor, write the tool every hand-written gradient is tested with:

  - `numeric_gradient(f, p, h=1e-6)`: the gradient of `f` at the point `p` (an array), estimated one coordinate at a time with the central difference.
  - `check_gradient(f, grad_f, points)`: the **largest** absolute gap, over every point in the list `points` and every coordinate, between `grad_f(p)` and `numeric_gradient(f, p)`.
  - `steepest(grad)`: the gradient scaled to length 1, the direction of steepest ascent.

  Then try it on `f(x, y, z) = x² + y z + z³`, whose gradient by rule is `[2x, z, y + 3z²]`, at the points `[1, 2, 3]` and `[0, -1, 2]`. Print the gradient by rule at the first point, whether the largest gap is below `1e-6`, and the steepest direction at the first point rounded to 3 places:

  ```
{block(BUILD_OUT)}  ```

  The checks call your functions on other functions and points, including a gradient formula that is wrong on purpose.
skills: [gradient, partial, direction]
''',
)
write("exercises/build-gradient-check/starter.py", "")
write("exercises/build-gradient-check/solution.py", BUILD_SOLUTION)
write(
    "exercises/build-gradient-check/test_exercise.py",
    f'''import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints the gradient, the check and the steepest direction."""
    assert run() == {BUILD_OUT!r}


def test_numeric_gradient():
    """For f = x y² + exp(z) at (1, 2, 0) the estimate is [4, 4, 1] to six decimals, one coordinate at a time."""
    numeric_gradient = function("numeric_gradient")
    g = numeric_gradient(lambda p: p[0] * p[1] ** 2 + np.exp(p[2]), np.array([1.0, 2.0, 0.0]))
    assert np.abs(g - [4.0, 4.0, 1.0]).max() < 1e-6


def test_check_gradient_reports_the_largest_gap():
    """A formula that is right gives a gap below 1e-6; one that is off by 0.5 in one slot at one point gives 0.5."""
    check_gradient = function("check_gradient")

    def f(p):
        return p[0] ** 2 + p[1] ** 3

    def right(p):
        return np.array([2 * p[0], 3 * p[1] ** 2])

    def off(p):
        return right(p) + np.array([0.0, 0.5 * (p[0] == 1.0)])

    points = [np.array([1.0, 1.0]), np.array([2.0, -1.0])]
    assert check_gradient(f, right, points) < 1e-6
    assert abs(check_gradient(f, off, points) - 0.5) < 1e-5


def test_steepest():
    """steepest([3, 4]) is [0.6, 0.8], and the result always has length 1."""
    steepest = function("steepest")
    assert np.allclose(steepest(np.array([3.0, 4.0])), [0.6, 0.8])
    assert abs(np.linalg.norm(steepest(np.array([1.0, -2.0, 2.0]))) - 1.0) < 1e-9
''',
)
write(
    "exercises/build-gradient-check/wrong/all-at-once.py",
    BUILD_SOLUTION.replace(
        "        step = np.zeros(len(p))\n        step[i] = h\n        grad[i] = (f(p + step) - f(p - step)) / (2 * h)",
        "        grad[i] = (f(p + h) - f(p - h)) / (2 * h)",
    ),
)
write("exercises/build-gradient-check/wrong/forward-difference.py", BUILD_FORWARD)
write(
    "exercises/build-gradient-check/wrong/mean-gap.py",
    BUILD_SOLUTION.replace(
        "    return max(np.abs(grad_f(p) - numeric_gradient(f, p)).max() for p in points)",
        "    return sum(np.abs(grad_f(p) - numeric_gradient(f, p)).mean() for p in points) / len(points)",
    ),
)
write(
    "exercises/build-gradient-check/wrong/not-unit.py",
    BUILD_SOLUTION.replace("    return grad / np.linalg.norm(grad)", "    return grad / grad.sum()"),
)
write(
    "exercises/build-gradient-check/wrong/typed-in.py",
    '''import numpy as np


def numeric_gradient(f, p, h=1e-6):
    return np.array([2.0, 3.0, 29.0])


def check_gradient(f, grad_f, points):
    return 0.0


def steepest(grad):
    return np.array([0.068, 0.103, 0.992])


'''
    + "".join(f"print({line!r})\n" for line in BUILD_OUT.splitlines()),
)

write(
    "exercises/debug-gradient-routine/exercise.yaml",
    f'''id: debug-gradient-routine
stage: debug
rev: 1
title: "A gradient with a stray nudge"
prompt: |
  This program estimates the gradient of `f(x, y) = x² + 3y²` at `(1, 1)` and the rate of change along two directions. It should print:

  ```
{block(DEBUG_OUT)}  ```

  It has two bugs. Run it: the gradient's second entry is 8 where it should be 6. The `step` array is made once, outside the loop, so by the second coordinate it still holds the first coordinate's nudge and both move at once. Fix that, and the two rates are still too big: `directional_derivative` dots the gradient with the direction as given, but the rate along a direction is defined for a direction of **length 1**.
skills: [gradient, contours]
''',
)
write("exercises/debug-gradient-routine/starter.py", DEBUG_STARTER)
write("exercises/debug-gradient-routine/solution.py", DEBUG_SOLUTION)
write(
    "exercises/debug-gradient-routine/test_exercise.py",
    f'''import numpy as np

from checks import function, run

EXPECTED = {DEBUG_OUT!r}


def test_the_output():
    """Prints the gradient and the two rates."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\\n{{EXPECTED}}\\nYour program printed:\\n{{printed}}"


def test_three_coordinates():
    """numeric_gradient nudges one coordinate at a time: f = x y z at (1, 2, 3) gives [6, 3, 2]."""
    numeric_gradient = function("numeric_gradient")
    g = numeric_gradient(lambda p: p[0] * p[1] * p[2], np.array([1.0, 2.0, 3.0]))
    assert np.abs(g - [6.0, 3.0, 2.0]).max() < 1e-6


def test_direction_length_does_not_matter():
    """The rate along [0, 5] equals the rate along [0, 1]."""
    directional_derivative = function("directional_derivative")
    g = np.array([2.0, 6.0])
    assert abs(directional_derivative(g, np.array([0.0, 5.0])) - 6.0) < 1e-9
''',
)
write("exercises/debug-gradient-routine/wrong/step-only.py", DEBUG_STEP_ONLY)
write(
    "exercises/debug-gradient-routine/wrong/typed-in.py",
    '''import numpy as np


def numeric_gradient(f, p, h=1e-6):
    return np.array([2.0, 6.0])


def directional_derivative(grad, direction):
    return 2.0


print("gradient [2. 6.]")
print("east 2.0")
print("north-east 5.657")
''',
)

# --- review pool: a code exercise ------------------------------------------------------------

write(
    "exercises/review-numeric-gradient/exercise.yaml",
    f'''id: review-numeric-gradient
stage: review_code
rev: 1
title: "A numeric gradient, from memory"
prompt: |
  Write `numeric_gradient(f, p, h=1e-6)`, which estimates the gradient of `f` at the array `p` one coordinate at a time with the central difference, and print it for the starter's `f` at `(1, 1)`, rounded to 6 places:

  ```
{block(REVIEW_CODE_OUT)}  ```
skills: [gradient]
''',
)
write("exercises/review-numeric-gradient/starter.py", REVIEW_CODE_STARTER)
write("exercises/review-numeric-gradient/solution.py", REVIEW_CODE_SOLUTION)
write(
    "exercises/review-numeric-gradient/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints [2. 6.]."""
    assert run() == {REVIEW_CODE_OUT!r}


def test_another_point_and_function():
    """f = x y at (2, 3) gives [3, 2] to six decimals."""
    numeric_gradient = function("numeric_gradient")
    g = numeric_gradient(lambda p: p[0] * p[1], np.array([2.0, 3.0]))
    assert np.abs(g - [3.0, 2.0]).max() < 1e-6
''',
)
write(
    "exercises/review-numeric-gradient/wrong/all-at-once.py",
    REVIEW_CODE_STARTER + '''

def numeric_gradient(f, p, h=1e-6):
    grad = np.zeros(len(p))
    for i in range(len(p)):
        grad[i] = (f(p + h) - f(p - h)) / (2 * h)
    return grad


print(np.round(numeric_gradient(f, np.array([1.0, 1.0])), 6))
''',
)
write(
    "exercises/review-numeric-gradient/wrong/typed-in.py",
    REVIEW_CODE_STARTER + '''

def numeric_gradient(f, p, h=1e-6):
    return np.array([2.0, 6.0])


print("[2. 6.]")
''',
)

print("ml.calc.partials-and-gradient written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
