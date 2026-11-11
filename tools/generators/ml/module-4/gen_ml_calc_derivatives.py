"""Writes the topic ml.calc.derivatives (Module 4's first topic). Run from the
repository root under uv (python -m uv run python <this file>), so every
program's expected output is captured from CPython rather than typed in.
Files are written as bytes with LF endings."""

import pathlib
import subprocess
import sys

ROOT = pathlib.Path("content/topics/ml.calc.derivatives")


def write(relative: str, text: str) -> None:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


def out(program: str) -> str:
    """What CPython prints for the program (the pinned expected output)."""
    result = subprocess.run(
        [sys.executable, "-c", program], capture_output=True, text=True, check=True
    )
    return result.stdout.replace("\r\n", "\n")


def block(text: str, indent: str = "  ") -> str:
    """Indent a program or an output for a YAML block scalar."""
    return "".join(indent + line + "\n" for line in text.rstrip("\n").splitlines())


def numbered(program: str) -> str:
    return "".join(f"{i + 1:>3} {line}\n" for i, line in enumerate(program.splitlines()))


SIGMOID = '''def sigmoid(x):
    return 1 / (1 + np.exp(-x))
'''

# --- the worked example -----------------------------------------------------------

EXAMPLE = '''import numpy as np


def slope(f, x, h=1e-6):
    return (f(x + h) - f(x - h)) / (2 * h)


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def relu(x):
    return np.maximum(x, 0.0)


print(round(slope(lambda x: x**3, 2.0), 6), 3 * 2.0**2)
print(round(slope(np.exp, 1.0), 6), round(float(np.exp(1.0)), 6))
print(round(slope(np.log, 4.0), 6), 1 / 4.0)
s = sigmoid(2.0)
print(round(slope(sigmoid, 2.0), 6), round(float(s * (1 - s)), 6))
print(round(slope(relu, -1.0), 6), round(slope(relu, 1.0), 6))

xs = np.array([-5.0, -2.0, 0.0, 2.0, 5.0])
print(np.round(sigmoid(xs) * (1 - sigmoid(xs)), 4))
print(np.where(xs > 0, 1.0, 0.0))
'''
EXAMPLE_OUT = out(EXAMPLE)
print("example:\n" + numbered(EXAMPLE) + EXAMPLE_OUT)

# --- the fill-in -------------------------------------------------------------------

FILL_BODY = '''

def sigmoid(x):
    return 1 / (1 + np.exp(-x))


checks = [
    ("x**2", lambda x: x**2, lambda x: 2 * x),
    ("exp", np.exp, np.exp),
    ("log", np.log, lambda x: 1 / x),
    ("sigmoid", sigmoid, lambda x: sigmoid(x) * (1 - sigmoid(x))),
]
for name, f, rule in checks:
    gap = max(abs(derivative(f, x) - rule(x)) for x in [0.5, 1.0, 2.0])
    print(name, gap < 1e-6)
'''
FILL_SOLUTION = '''import numpy as np


def derivative(f, x, h=1e-6):
    return (f(x + h) - f(x - h)) / (2 * h)
''' + FILL_BODY
FILL_STARTER = '''import numpy as np


def derivative(f, x, h=1e-6):
    return (f(x + ...) - f(x - h)) / (... * h)
''' + FILL_BODY
FILL_FORWARD = '''import numpy as np


def derivative(f, x, h=1e-6):
    return (f(x + h) - f(x)) / h
''' + FILL_BODY
FILL_OUT = out(FILL_SOLUTION)
print("fill:\n" + FILL_OUT)
assert FILL_OUT == "x**2 True\nexp True\nlog True\nsigmoid True\n", FILL_OUT
assert out(FILL_FORWARD) != FILL_OUT, "the forward difference must visibly fail"

# --- the write ------------------------------------------------------------------------

WRITE_STARTER = "import numpy as np\n\n\n" + SIGMOID
WRITE_SOLUTION = WRITE_STARTER + '''

def d_sigmoid(x):
    s = sigmoid(x)
    return s * (1 - s)


print(np.round(d_sigmoid(np.array([-4.0, 0.0, 4.0])), 4))
'''
WRITE_OUT = out(WRITE_SOLUTION)
print("write:\n" + WRITE_OUT)

# --- the build -------------------------------------------------------------------------

BUILD_SOLUTION = '''import numpy as np


def numeric_derivative(f, x, h=1e-6):
    return (f(x + h) - f(x - h)) / (2 * h)


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def d_sigmoid(x):
    s = sigmoid(x)
    return s * (1 - s)


def relu(x):
    return np.maximum(x, 0.0)


def d_relu(x):
    return np.where(x > 0, 1.0, 0.0)


def max_error(f, df, xs):
    return max(abs(df(x) - numeric_derivative(f, x)) for x in xs)


xs = np.array([-2.0, -0.5, 0.5, 2.0])
print("power", max_error(lambda x: x**3, lambda x: 3 * x**2, xs) < 1e-6)
print("exp", max_error(np.exp, np.exp, xs) < 1e-6)
print("sigmoid", max_error(sigmoid, d_sigmoid, xs) < 1e-6)
print("relu", max_error(relu, d_relu, xs) < 1e-6)
'''
BUILD_OUT = out(BUILD_SOLUTION)
print("build:\n" + BUILD_OUT)
assert BUILD_OUT == "power True\nexp True\nsigmoid True\nrelu True\n", BUILD_OUT

# --- the debug ---------------------------------------------------------------------------

DEBUG_SOLUTION = '''import numpy as np


def slope(f, x, h=1e-6):
    return (f(x + h) - f(x - h)) / (2 * h)


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def d_sigmoid(x):
    s = sigmoid(x)
    return s * (1 - s)


print("x**2 at 3:", round(slope(lambda x: x**2, 3.0), 6))
print("sigmoid at 0:", round(float(d_sigmoid(0.0)), 6), round(slope(sigmoid, 0.0), 6))
print("sigmoid at 2:", round(float(d_sigmoid(2.0)), 6), round(slope(sigmoid, 2.0), 6))
'''
DEBUG_STARTER = DEBUG_SOLUTION.replace("h=1e-6", "h=1e-12").replace("s * (1 - s)", "s * (1 - x)")
DEBUG_H_ONLY = DEBUG_SOLUTION.replace("s * (1 - s)", "s * (1 - x)")
DEBUG_OUT = out(DEBUG_SOLUTION)
print("debug:\n" + DEBUG_OUT + "--- buggy prints:\n" + out(DEBUG_STARTER))
assert DEBUG_OUT == "x**2 at 3: 6.0\nsigmoid at 0: 0.25 0.25\nsigmoid at 2: 0.104994 0.104994\n", DEBUG_OUT
assert out(DEBUG_STARTER).splitlines()[0] != "x**2 at 3: 6.0", "the tiny h must visibly fail"

# --- predict items ------------------------------------------------------------------------

PREDICT_RELU = '''import numpy as np

z = np.array([-2.0, -0.5, 0.5, 3.0])
relu = np.maximum(z, 0.0)
print(relu)
print(np.where(z > 0, 1.0, 0.0))
print(relu * 2)
'''
PREDICT_RELU_OUT = out(PREDICT_RELU)
print("predict relu:\n" + PREDICT_RELU_OUT)

REVIEW_POWER = '''import numpy as np

x = np.array([1.0, 2.0, 3.0])
f = x**3
df = 3 * x**2
print(f)
print(df)
print(df[2] > df[0])
'''
REVIEW_POWER_OUT = out(REVIEW_POWER)
print("review power:\n" + REVIEW_POWER_OUT)

REVIEW_RELU_STARTER = "import numpy as np\n"
REVIEW_RELU_SOLUTION = REVIEW_RELU_STARTER + '''

def d_relu(x):
    return np.where(x > 0, 1.0, 0.0)


print(d_relu(np.array([-3.0, 0.5, 2.0])))
'''
REVIEW_RELU_OUT = out(REVIEW_RELU_SOLUTION)
print("review relu:\n" + REVIEW_RELU_OUT)
assert REVIEW_RELU_OUT == "[0. 1. 1.]\n", REVIEW_RELU_OUT

# =====================================================================================
# topic.yaml
# =====================================================================================

write(
    "topic.yaml",
    '''id: ml.calc.derivatives
kind: topic
status: ready
title: "Derivatives of the functions ML uses"
summary: "The derivatives of powers, exp, log, the sigmoid and ReLU, each checked numerically, and what each one's shape means for learning."
prerequisites: [ml.math.calculus, ml.math.exponents-and-logs, ml.la.numpy-arrays]
packages: [numpy]
estimated_minutes: 50
rev: 1
objectives:
  - "Differentiate powers, exp, log, the sigmoid and ReLU by rule, and check each numerically."
  - "Say why the sigmoid's derivative is small far from zero and what that does to learning."
  - "Apply a derivative to a whole array of inputs at once."
  - "Read a derivative's sign and size as the direction and speed to move."
# Linked, never copied or embedded: OpenStax is CC BY 4.0; 3Blue1Brown's
# videos are under the standard YouTube licence; NumPy's documentation is
# under the NumPy licence (BSD-3-Clause).
resources:
  - title: "3Blue1Brown: Essence of calculus (Grant Sanderson), chapters 3 (Derivative formulas through geometry) and 5 (What's so special about Euler's number e?)"
    url: https://www.3blue1brown.com/topics/calculus
    type: video
    use: link
    license: Standard YouTube licence (linked, not copied)
  - title: "OpenStax Calculus Volume 1: sections 3.3 (Differentiation Rules) and 3.9 (Derivatives of Exponential and Logarithmic Functions)"
    url: https://openstax.org/details/books/calculus-volume-1
    type: reading
    use: link
    license: CC BY 4.0
  - title: "numpy.where (the NumPy developers)"
    url: https://numpy.org/doc/stable/reference/generated/numpy.where.html
    type: reading
    use: link
    license: BSD-3-Clause (NumPy documentation)
practice:
  - example-five-derivatives-checked
  - parsons-sigmoid-check
  - mcq-sigmoid-flat
  - predict-relu-derivative
  - mcq-exp-and-log
  - fill-derivative-table
  - write-d-sigmoid
prove:
  build: build-derivative-checker
  debug: debug-derivative-report
  explain:
    prompt: |
      A teammate is watching a training run. The network's early layers barely change when every unit uses the sigmoid, and switching those units to ReLU helped. They ask you why. In your own words: what does a derivative tell training, in direction and in speed? Why is the sigmoid's derivative small far from zero, and what does that do to learning? What is ReLU's derivative, and why does that help? And why do you check a derivative numerically before trusting it?
    rubric:
      - id: direction-and-speed
        required: true
        description: "The derivative's sign says which way the output rises, so descent steps the other way; its size says how fast the output changes, so how far a step moves."
      - id: saturation
        required: true
        description: "The sigmoid flattens towards 0 and 1, so its derivative sigma(1 - sigma) is at most 0.25 and nearly zero far from zero; a unit out there passes almost no slope back, and it (and everything behind it) stops learning."
      - id: relu
        required: true
        description: "ReLU is max(x, 0): derivative 1 wherever the unit is active and 0 where it's off, so an active unit passes the slope through at full strength rather than shrinking it."
      - id: numeric-check
        required: false
        description: "A rule can be misremembered or mistyped; comparing it with a central difference, (f(x + h) - f(x - h)) / 2h, at a few points catches that before training runs on a wrong slope."
    model_answer: |
      Training moves each knob a little, and the derivative of the loss with respect to that knob says how. Its sign says which way the loss rises, so the step goes the other way; its size says how fast the loss changes there, so a big derivative means a big step and a tiny one means almost no movement. The sigmoid is the trouble. It squashes any input into a number between 0 and 1, so it flattens out on both sides, and its derivative, sigma times one minus sigma, is at most 0.25 at zero and almost nothing far from zero: about 0.0066 at 5 and 0.00005 at 10. A unit whose input is out there is saturated: it passes almost no slope back to the layers behind it, so they barely change, and a stack of such units multiplies several tiny factors together. ReLU is max(x, 0). Its derivative is 1 wherever the unit is active and 0 where it's off, so an active unit hands the slope straight through at full strength, which is why the early layers started moving. And a rule is only a claim until it's checked: I compute the central difference, f(x + h) minus f(x - h) over 2h with a small h, at a few points and compare. A misremembered rule, or a slip like one minus x instead of one minus sigma, shows up as a gap in the sixth decimal before it has cost a day of training.
review_pool:
  - review-predict-power-rule
  - review-mcq-exp-derivative
  - review-mcq-direction-and-speed
  - review-d-relu
# What this topic teaches. Each question names the skills it tests, so a
# missed question can come back as a different one on the same skill
# (ADR-0011).
skills:
  - id: rules
    description: "Differentiate powers, exp, log, the sigmoid and ReLU by rule"
  - id: numeric-check
    description: "Check a derivative against a central difference"
  - id: arrays
    description: "Apply a function and its derivative to a whole array"
  - id: reading
    description: "Read a derivative's sign and size as direction and speed, and a tiny one as a unit that has stopped learning"
''',
)

# =====================================================================================
# lesson.mdx
# =====================================================================================

write(
    "lesson.mdx",
    '''<Intro>

Module 1 estimated a slope by nudging the input, and walked downhill against it. Training a model is that, millions of knobs at a time, and the slopes come from a handful of functions every model is built from: powers, the exponential, the logarithm, the sigmoid and ReLU. This topic learns each one's derivative as a rule, checks every rule in code with a better slope estimate than Module 1's, and reads what each derivative's shape means for learning.

The main resource is **3Blue1Brown's _Essence of calculus_**, chapter 3 (derivative formulas through geometry) and chapter 5 (what's so special about e); about 35 minutes. OpenStax _Calculus Volume 1_, sections 3.3 and 3.9, has the same rules as text. Watch for:

- **The power rule as a picture:** nudging the side of a square by `dx` adds two thin strips, which is where `2x` comes from.
- **Why e:** it's the base whose exponential is its own derivative. Every other base drags a constant along.
- **A rule is a claim.** Each one here is checked against a numeric slope before it's used.

The chain rule, how these pieces combine, is two topics away. Here each function is on its own.

</Intro>

<Resource index={0} />

<Recap>

- **A better slope estimate.** Module 1 used `(f(x + h) - f(x)) / h`. The **central difference** `(f(x + h) - f(x - h)) / (2 * h)` steps both ways and is far more accurate: its error shrinks with `h²`, not `h`. With `h = 1e-6` it agrees with the exact derivative to about six decimals, which is the standard every check in this module holds to. Smaller is not better: at `h = 1e-12` the two function values are so close that rounding noise swamps their difference.
- **The rules.** `x ** n` has derivative `n * x ** (n - 1)`. `np.exp(x)` is its own derivative. `np.log(x)` has derivative `1 / x` (for `x > 0`). A constant times a function multiplies the derivative by that constant; the derivative of a sum is the sum of the derivatives.
- **The sigmoid** `σ(x) = 1 / (1 + np.exp(-x))` squashes any number into the range 0 to 1, which is how a model turns a score into a probability. Its derivative is `σ(x) * (1 - σ(x))`: 0.25 at zero, 0.105 at 2, 0.0066 at 5, 0.000045 at 10. Far from zero it is **saturated**: nearly flat, so a change in input barely changes the output, and almost no slope passes back through it. A saturated unit has, in effect, stopped learning.
- **ReLU** (the rectified linear unit) is `np.maximum(x, 0.0)`: zero on the left, the input itself on the right. Its derivative is 0 for `x < 0` and 1 for `x > 0`, `np.where(x > 0, 1.0, 0.0)`; at exactly 0 there's a corner, and training uses 0 there by convention. An active ReLU passes the slope through at full strength, which is why it replaced the sigmoid inside networks.
- **Whole arrays at once.** Every formula above takes an array and returns one: `sigmoid(xs) * (1 - sigmoid(xs))` is the derivative at every entry. That's how a layer of a thousand units is handled in one line.
- **Reading a derivative.** The **sign** is the direction: positive means the output rises as the input grows, so descent steps the other way. The **size** is the speed: how much the output moves per unit of input, and so how far a descent step goes. **Zero** means flat: the bottom of a valley, the top of a hill, or a ReLU that's off.
- **In machine learning:** a loss is built from these pieces, and training multiplies their derivatives together (the gradient next, then the chain rule). One saturated sigmoid contributes a factor like 0.0066, and everything behind it learns 150 times slower.

</Recap>
''',
)

# =====================================================================================
# recall
# =====================================================================================

write(
    "recall/parsons-sigmoid-check.yaml",
    '''id: parsons-sigmoid-check
type: parsons
rev: 1
prompt: |
  Put the lines in order to check the sigmoid's derivative rule at `x = 1` against a central difference, printing `True`. One line is a decoy that doesn't belong.
lines:
  - 'import numpy as np'
  - 'def sigmoid(x):'
  - '    return 1 / (1 + np.exp(-x))'
  - 's = sigmoid(1.0)'
  - 'by_rule = s * (1 - s)'
  - 'numeric = (sigmoid(1.0 + 1e-6) - sigmoid(1.0 - 1e-6)) / 2e-6'
  - 'print(abs(by_rule - numeric) < 1e-6)'
distractors:
  - 'by_rule = s * (1 + s)'
explanation: |
  The sigmoid's derivative is `σ(x) * (1 - σ(x))`, the output times one minus the output. The central difference steps a millionth each way and divides by the two-millionth gap; the two agree to six decimals, so the comparison prints `True`. The decoy's `1 + s` gives about 1.3 at `x = 1` instead of about 0.197, nothing like the slope.
skills: [rules, numeric-check]
''',
)

write(
    "recall/mcq-sigmoid-flat.yaml",
    '''id: mcq-sigmoid-flat
type: mcq
rev: 1
prompt: |
  A unit in a network computes `sigmoid(z)`, and during training its input `z` is about 10. Its derivative there is about 0.000045. What does that mean for learning?
choices:
  - 'The unit is learning quickly: a small derivative means a small, careful step'
  - 'The sigmoid is nearly flat there, so a change in `z` barely changes the output; almost no slope passes back through the unit, and it (and the layers behind it) barely learn'
  - 'The derivative is small because `z` is positive; it would be large if `z` were -10'
  - 'Nothing: the derivative only matters at `z = 0`'
answer: 1
explanation: |
  Far from zero the sigmoid has flattened out towards 1 (or towards 0 at -10, where the derivative is the same 0.000045). A flat function doesn't respond to its input, and training can only move what responds. The unit is **saturated**, and since slopes multiply through a network, everything behind it is starved too. That's the reason ReLU replaced the sigmoid inside networks.
skills: [reading]
''',
)

write(
    "recall/predict-relu-derivative.yaml",
    f'''id: predict-relu-derivative
type: predict_output
rev: 1
prompt: |
  ReLU and its derivative, applied to a whole array. What does the program print?
code: |
{block(PREDICT_RELU)}expected_output: |
{block(PREDICT_RELU_OUT)}explanation: |
  `np.maximum(z, 0.0)` keeps the positive entries and turns the negative ones into 0: that's ReLU. Its derivative is 1 where the input was positive and 0 where it wasn't, which `np.where(z > 0, 1.0, 0.0)` writes in one line. The last line is just ReLU doubled: the slope of `2 * relu` is 2 on the right and 0 on the left, a constant times a function has a constant times the derivative.
skills: [arrays, rules]
''',
)

write(
    "recall/mcq-exp-and-log.yaml",
    '''id: mcq-exp-and-log
type: mcq
rev: 1
prompt: |
  Which pair of rules is right?
choices:
  - 'The derivative of `np.exp(x)` is `x * np.exp(x - 1)`, and the derivative of `np.log(x)` is `np.log(x) / x`'
  - 'The derivative of `np.exp(x)` is `np.exp(x)` itself, and the derivative of `np.log(x)` is `1 / x`'
  - 'The derivative of `np.exp(x)` is `1 / np.exp(x)`, and the derivative of `np.log(x)` is `np.exp(x)`'
  - 'Neither has a rule; they can only be estimated numerically'
answer: 1
explanation: |
  `e` is the base chosen so that the exponential is its own derivative: the slope of `np.exp` at any `x` is its value there. The natural log undoes it, and its derivative is `1 / x`, which is why log loss has such a simple gradient later in this module. The first choice misapplies the power rule, which is for a variable base and a fixed power, not the other way round.
skills: [rules]
''',
)

write(
    "recall/review-predict-power-rule.yaml",
    f'''id: review-predict-power-rule
type: predict_output
rev: 1
prompt: |
  The power rule on a whole array. What does the program print?
code: |
{block(REVIEW_POWER)}expected_output: |
{block(REVIEW_POWER_OUT)}explanation: |
  `x ** 3` has derivative `3 * x ** 2`, and NumPy applies both to every entry at once: 1, 8, 27 for the cubes, and 3, 12, 27 for the slopes. The slope grows with `x`, so the cube is rising faster at 3 than at 1, and the comparison prints `True`.
skills: [rules, arrays]
''',
)

write(
    "recall/review-mcq-exp-derivative.yaml",
    '''id: review-mcq-exp-derivative
type: mcq
rev: 1
prompt: |
  At `x = 3`, `np.exp(x)` is about 20.09. What is its derivative there?
choices:
  - 'About 20.09: the exponential is its own derivative'
  - 'About 22.17, which is `3 * np.exp(2)`'
  - 'About 0.33, which is `1 / 3`'
  - 'Exactly 3'
answer: 0
explanation: |
  The slope of `e ** x` at any point equals its height there, so at 3 both are about 20.09. The second choice applies the power rule to the exponent, which is the wrong rule for a fixed base; the third is the derivative of `np.log`, not of `np.exp`.
skills: [rules]
''',
)

write(
    "recall/review-mcq-direction-and-speed.yaml",
    '''id: review-mcq-direction-and-speed
type: mcq
rev: 1
prompt: |
  During gradient descent on one knob `x`, the loss's derivative at the current `x` is `-6`. What does that tell the next step, `x = x - rate * slope`?
choices:
  - 'The loss is falling as `x` grows, so the step moves `x` to the right, and the steep slope makes it a large step'
  - 'The loss is negative, so training is finished'
  - 'The loss is rising as `x` grows, so the step moves `x` to the left'
  - 'The slope is negative, so the step is small'
answer: 0
explanation: |
  The sign is the direction: a negative derivative means the loss goes down as `x` goes up, so downhill is to the right, and subtracting a negative number moves `x` right. The size is the speed: 6 is steep, so `rate * 6` is a big step. A derivative says nothing about whether the loss itself is positive or negative, only about which way it's heading.
skills: [reading]
''',
)

# =====================================================================================
# exercises
# =====================================================================================

write(
    "exercises/example-five-derivatives-checked/exercise.yaml",
    f'''id: example-five-derivatives-checked
stage: worked_example
rev: 1
title: "Five derivatives, each checked"
prompt: |
  This program checks the derivative of a power, `exp`, `log`, the sigmoid and ReLU against a numeric slope, then applies two of them to a whole array. Press **Run**, then read how each part works.
steps:
  - label: "A better slope estimate"
    lines: "4-5"
    note: "Module 1 stepped one way: `(f(x + h) - f(x)) / h`. Stepping both ways and dividing by `2 * h` is the **central difference**, and its error shrinks with `h` squared rather than `h`. At `h = 1e-6` it matches the exact derivative to about six decimals, so every check in this module can ask for six decimals."
  - label: "Three rules, checked"
    lines: "16-18"
    note: "Each line prints the numeric slope, then the rule's answer. The power rule: `3 * x ** 2` is 12 at 2. The exponential is its own derivative: both numbers are `e`, 2.718282. The log's derivative is `1 / x`: 0.25 at 4."
  - label: "The sigmoid"
    lines: "19-20"
    note: "`sigmoid` (lines 8 and 9) squashes any number into the range 0 to 1. Its derivative is the output times one minus the output, `s * (1 - s)`: at 2, the numeric slope and the rule both give 0.104994. Notice how small that already is."
  - label: "ReLU"
    lines: "21"
    note: "`relu` (lines 12 and 13) is `max(x, 0)`. Left of zero it's flat, slope 0; right of zero it's the input itself, slope 1. At exactly 0 there's a corner with no single slope; training uses 0 there by convention."
  - label: "Whole arrays at once"
    lines: "23-25"
    note: "The same formulas take an array and return one. The sigmoid's derivative is 0.25 at zero and 0.0066 at plus or minus 5: a unit that far out is **saturated** and barely learns. ReLU's derivative is 0 or 1, written with `np.where`: wherever the input is positive, the slope passes through at full strength."
''',
)
write("exercises/example-five-derivatives-checked/solution.py", EXAMPLE)
write(
    "exercises/example-five-derivatives-checked/test_exercise.py",
    f'''from checks import run


def test_the_walkthrough():
    """Prints five checked derivatives, then the sigmoid's and ReLU's derivatives on an array."""
    assert run() == {EXAMPLE_OUT!r}
''',
)

write(
    "exercises/fill-derivative-table/exercise.yaml",
    f'''id: fill-derivative-table
stage: fill_in
rev: 1
title: "A table of checked rules"
prompt: |
  `derivative(f, x, h)` should estimate the slope of `f` at `x` with the central difference, stepping `h` each way. Replace each `...` so the program checks four rules at three points each and prints:

  ```
{block(FILL_OUT)}  ```

  The program fails until every `...` is replaced.
hints:
  - "The central difference evaluates `f` at `x + h` and at `x - h`."
  - "The two points are `2 * h` apart, so that's what the difference is divided by."
skills: [numeric-check, rules]
''',
)
write("exercises/fill-derivative-table/starter.py", FILL_STARTER)
write("exercises/fill-derivative-table/solution.py", FILL_SOLUTION)
write(
    "exercises/fill-derivative-table/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints True for all four rules."""
    printed = run()
    assert printed == {FILL_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_accuracy():
    """The estimate is within a millionth of the exact derivative for x ** 3 at 2 and exp at 3."""
    derivative = function("derivative")
    assert abs(derivative(lambda x: x**3, 2.0) - 12.0) < 1e-6
    assert abs(derivative(np.exp, 3.0) - np.exp(3.0)) < 1e-5
''',
)
write("exercises/fill-derivative-table/wrong/forward-difference.py", FILL_FORWARD)
write(
    "exercises/fill-derivative-table/wrong/typed-in.py",
    '''import numpy as np


def derivative(f, x, h=1e-6):
    return f(x) * 0 + 2 * x


for name in ["x**2", "exp", "log", "sigmoid"]:
    print(name, True)
''',
)

write(
    "exercises/write-d-sigmoid/exercise.yaml",
    f'''id: write-d-sigmoid
stage: write
rev: 1
title: "The sigmoid's derivative, for arrays"
prompt: |
  The starter defines `sigmoid`. Write `d_sigmoid(x)`, which returns the sigmoid's derivative, `σ(x) * (1 - σ(x))`, for a single number or a whole array. Then print it for `np.array([-4.0, 0.0, 4.0])`, rounded to 4 places:

  ```
{block(WRITE_OUT)}  ```

  The checks compare your function with a central difference at other points, and call it on an array.
hints:
  - "Call `sigmoid(x)` once, keep the result, and use it twice."
  - "Arithmetic on an array happens entry by entry, so the same two lines work for a number and for an array."
skills: [rules, arrays]
''',
)
write("exercises/write-d-sigmoid/starter.py", WRITE_STARTER)
write("exercises/write-d-sigmoid/solution.py", WRITE_SOLUTION)
write(
    "exercises/write-d-sigmoid/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def test_the_output():
    """Prints the derivative at -4, 0 and 4, rounded to 4 places."""
    printed = run()
    assert printed == {WRITE_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_matches_a_numeric_slope():
    """At -3, -1, 0.5 and 2 the rule agrees with a central difference to six decimals."""
    d_sigmoid = function("d_sigmoid")
    for x in [-3.0, -1.0, 0.5, 2.0]:
        numeric = (sigmoid(x + 1e-6) - sigmoid(x - 1e-6)) / 2e-6
        assert abs(d_sigmoid(x) - numeric) < 1e-6


def test_arrays():
    """An array in gives an array of the same shape out, with 0.25 at zero."""
    d_sigmoid = function("d_sigmoid")
    result = d_sigmoid(np.array([[0.0, 1.0], [-1.0, 10.0]]))
    assert result.shape == (2, 2)
    assert abs(result[0, 0] - 0.25) < 1e-9
    assert result[1, 1] < 0.0001
''',
)
write(
    "exercises/write-d-sigmoid/wrong/one-minus-x.py",
    WRITE_STARTER + '''

def d_sigmoid(x):
    s = sigmoid(x)
    return s * (1 - x)


print(np.round(d_sigmoid(np.array([-4.0, 0.0, 4.0])), 4))
''',
)
write(
    "exercises/write-d-sigmoid/wrong/typed-in.py",
    WRITE_STARTER + f'''

def d_sigmoid(x):
    return np.array([0.0177, 0.25, 0.0177])


print({WRITE_OUT.strip()!r})
''',
)

# --- the proof -------------------------------------------------------------------------------

write(
    "exercises/build-derivative-checker/exercise.yaml",
    f'''id: build-derivative-checker
stage: build
rev: 1
title: "A derivative checker"
prompt: |
  Starting from a blank editor, write the five functions a network is made of, their derivatives, and a checker that catches a wrong rule:

  - `numeric_derivative(f, x, h=1e-6)`: the central difference, `(f(x + h) - f(x - h)) / (2 * h)`.
  - `sigmoid(x)` and `d_sigmoid(x)`; `relu(x)` and `d_relu(x)`. Each works on a number or an array. `d_relu` is `1.0` where `x > 0` and `0.0` elsewhere.
  - `max_error(f, df, xs)`: the **largest** absolute gap between `df(x)` and `numeric_derivative(f, x)` over the points in the array `xs`.

  Then, for `xs = np.array([-2.0, -0.5, 0.5, 2.0])`, print one line per function: its name, then whether `max_error` is below `1e-6`. Check `x ** 3` against `3 * x ** 2` (call it `power`), `np.exp` against itself, and your two pairs:

  ```
{block(BUILD_OUT)}  ```

  The checks call your functions at other points, with a rule that is wrong on purpose, and with arrays.
skills: [rules, numeric-check, arrays]
''',
)
write("exercises/build-derivative-checker/starter.py", "")
write("exercises/build-derivative-checker/solution.py", BUILD_SOLUTION)
write(
    "exercises/build-derivative-checker/test_exercise.py",
    f'''import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints True for power, exp, sigmoid and relu."""
    assert run() == {BUILD_OUT!r}


def test_numeric_derivative_is_central():
    """The estimate is within a millionth of 12 for x ** 3 at 2, and of exp(3) for exp at 3."""
    numeric_derivative = function("numeric_derivative")
    assert abs(numeric_derivative(lambda x: x**3, 2.0) - 12.0) < 1e-6
    assert abs(numeric_derivative(np.exp, 3.0) - np.exp(3.0)) < 1e-5


def test_sigmoid_pair():
    """d_sigmoid matches a central difference of sigmoid at four points, and keeps an array's shape."""
    sigmoid = function("sigmoid")
    d_sigmoid = function("d_sigmoid")
    for x in [-3.0, -1.0, 0.5, 2.0]:
        numeric = (sigmoid(x + 1e-6) - sigmoid(x - 1e-6)) / 2e-6
        assert abs(d_sigmoid(x) - numeric) < 1e-6
    assert d_sigmoid(np.array([[0.0, 1.0], [2.0, 3.0]])).shape == (2, 2)
    assert abs(float(d_sigmoid(0.0)) - 0.25) < 1e-9


def test_relu_pair():
    """relu keeps positives and zeroes negatives; d_relu is 1.0 on the right and 0.0 on the left."""
    relu = function("relu")
    d_relu = function("d_relu")
    assert relu(np.array([-1.0, 0.0, 2.5])).tolist() == [0.0, 0.0, 2.5]
    assert d_relu(np.array([-1.0, -0.1, 0.1, 2.0])).tolist() == [0.0, 0.0, 1.0, 1.0]
    assert str(d_relu(np.array([-1.0, 2.0]))) == "[0. 1.]"


def test_max_error_is_the_largest_gap():
    """With a rule that is wrong by exactly x, the max error over 0, 1, 2 is 2 (not the mean, 1)."""
    max_error = function("max_error")
    xs = np.array([0.0, 1.0, 2.0])
    assert max_error(lambda x: x**2, lambda x: 2 * x, xs) < 1e-6
    assert abs(max_error(lambda x: x**2, lambda x: 2 * x + x, xs) - 2.0) < 1e-5
''',
)
write(
    "exercises/build-derivative-checker/wrong/forward-difference.py",
    BUILD_SOLUTION.replace(
        "    return (f(x + h) - f(x - h)) / (2 * h)", "    return (f(x + h) - f(x)) / h"
    ),
)
write(
    "exercises/build-derivative-checker/wrong/sigmoid-one-minus-x.py",
    BUILD_SOLUTION.replace("    return s * (1 - s)", "    return s * (1 - x)"),
)
write(
    "exercises/build-derivative-checker/wrong/relu-passes-x.py",
    BUILD_SOLUTION.replace(
        "    return np.where(x > 0, 1.0, 0.0)", "    return np.where(x > 0, x, 0.0)"
    ),
)
write(
    "exercises/build-derivative-checker/wrong/mean-error.py",
    BUILD_SOLUTION.replace(
        "    return max(abs(df(x) - numeric_derivative(f, x)) for x in xs)",
        "    return sum(abs(df(x) - numeric_derivative(f, x)) for x in xs) / len(xs)",
    ),
)
write(
    "exercises/build-derivative-checker/wrong/typed-in.py",
    '''import numpy as np


def numeric_derivative(f, x, h=1e-6):
    return 3 * x**2


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def d_sigmoid(x):
    return 0.25


def relu(x):
    return np.maximum(x, 0.0)


def d_relu(x):
    return 1.0


def max_error(f, df, xs):
    return 0.0


for name in ["power", "exp", "sigmoid", "relu"]:
    print(name, True)
''',
)

write(
    "exercises/debug-derivative-report/exercise.yaml",
    f'''id: debug-derivative-report
stage: debug
rev: 1
title: "A slope that won't settle"
prompt: |
  This program should check the sigmoid's derivative rule against a numeric slope, and print:

  ```
{block(DEBUG_OUT)}  ```

  It has two bugs. Run it: the first line is off in the fourth or fifth decimal, which means the numeric slope itself is wrong. Look at `h`: a step of `1e-12` is so small that the two function values are nearly identical and rounding noise swamps their difference. Fix that, and the first line is right, but the rule's numbers still disagree with the numeric ones: the sigmoid's derivative is the output times one minus the **output**.
skills: [numeric-check, rules]
''',
)
write("exercises/debug-derivative-report/starter.py", DEBUG_STARTER)
write("exercises/debug-derivative-report/solution.py", DEBUG_SOLUTION)
write(
    "exercises/debug-derivative-report/test_exercise.py",
    f'''import numpy as np

from checks import function, run

EXPECTED = {DEBUG_OUT!r}


def test_the_output():
    """Prints the three checked lines."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\\n{{EXPECTED}}\\nYour program printed:\\n{{printed}}"


def test_the_slope_is_accurate():
    """slope gets x ** 3 at 2 right to six decimals."""
    slope = function("slope")
    assert abs(slope(lambda x: x**3, 2.0) - 12.0) < 1e-6


def test_the_rule_on_an_array():
    """d_sigmoid is the same at 1 and -1 (the curve is symmetric), and 0.25 at 0."""
    d_sigmoid = function("d_sigmoid")
    values = d_sigmoid(np.array([1.0, -1.0, 0.0]))
    assert abs(values[0] - values[1]) < 1e-12
    assert abs(values[2] - 0.25) < 1e-12
''',
)
write("exercises/debug-derivative-report/wrong/h-only.py", DEBUG_H_ONLY)
write(
    "exercises/debug-derivative-report/wrong/typed-in.py",
    '''import numpy as np


def slope(f, x, h=1e-6):
    return 12.0


def d_sigmoid(x):
    return 0.25


print("x**2 at 3: 6.0")
print("sigmoid at 0: 0.25 0.25")
print("sigmoid at 2: 0.104994 0.104994")
''',
)

# --- review pool: a code exercise ----------------------------------------------------------

write(
    "exercises/review-d-relu/exercise.yaml",
    f'''id: review-d-relu
stage: review_code
rev: 1
title: "ReLU's derivative"
prompt: |
  Write `d_relu(x)`, which returns ReLU's derivative for an array: `1.0` where `x > 0`, `0.0` elsewhere. Then print it for `np.array([-3.0, 0.5, 2.0])`:

  ```
{block(REVIEW_RELU_OUT)}  ```
skills: [rules, arrays]
''',
)
write("exercises/review-d-relu/starter.py", REVIEW_RELU_STARTER)
write("exercises/review-d-relu/solution.py", REVIEW_RELU_SOLUTION)
write(
    "exercises/review-d-relu/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints [0. 1. 1.]."""
    assert run() == {REVIEW_RELU_OUT!r}


def test_other_inputs():
    """Zero on the left, one on the right, as floats, for another array."""
    d_relu = function("d_relu")
    assert d_relu(np.array([-0.5, -2.0, 4.0, 0.1])).tolist() == [0.0, 0.0, 1.0, 1.0]
    assert str(d_relu(np.array([7.0, -7.0]))) == "[1. 0.]"
''',
)
write(
    "exercises/review-d-relu/wrong/returns-x.py",
    REVIEW_RELU_STARTER + '''

def d_relu(x):
    return np.where(x > 0, x, 0.0)


print(d_relu(np.array([-3.0, 0.5, 2.0])))
''',
)
write(
    "exercises/review-d-relu/wrong/typed-in.py",
    REVIEW_RELU_STARTER + '''

def d_relu(x):
    return np.array([0.0, 1.0, 1.0])


print("[0. 1. 1.]")
''',
)

print("ml.calc.derivatives written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
