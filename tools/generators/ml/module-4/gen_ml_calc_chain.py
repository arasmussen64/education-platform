"""Writes the topic ml.calc.chain-rule (Module 4's fourth topic). Run from the
repository root under uv (python -m uv run python <this file>), so every
program's expected output is captured from CPython rather than typed in.
Files are written as bytes with LF endings."""

import pathlib
import subprocess
import sys

ROOT = pathlib.Path("content/topics/ml.calc.chain-rule")


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


SIGMOID = '''def sigmoid(x):
    return 1 / (1 + np.exp(-x))
'''
SLOPE = '''def slope(f, x, h=1e-6):
    return (f(x + h) - f(x - h)) / (2 * h)
'''

# --- the worked example ------------------------------------------------------------------

EXAMPLE = "import numpy as np\n\n\n" + SLOPE + "\n\n" + SIGMOID + '''

x = 2.0
u = 3 * x + 1
print(2 * u * 3, round(slope(lambda x: (3 * x + 1) ** 2, x), 6))

u = 2 * x + 1
s = sigmoid(u)
print(round(float(s * (1 - s) * 2), 6), round(slope(lambda x: sigmoid(2 * x + 1), x), 6))

u = 2 * x
v = np.exp(u)
w = 1 + v
y = np.log(w)
print(round(float(y), 6))
print(2, round(float(v), 6), 1, round(float(1 / w), 6))
print(round(float(2 * v * 1 * (1 / w)), 6), round(slope(lambda x: np.log(1 + np.exp(2 * x)), x), 6))

grad = 1.0
for local in [1 / w, 1, v, 2]:
    grad = grad * local
print(round(float(grad), 6))
'''
EXAMPLE_OUT = out(EXAMPLE)
print("example:\n" + numbered(EXAMPLE) + EXAMPLE_OUT)
assert EXAMPLE_OUT.startswith("42.0 42.0\n0.013296 0.013296\n4.01815\n2 54.59815 1 0.017986\n"), EXAMPLE_OUT
assert EXAMPLE_OUT.endswith("1.964028 1.964028\n1.964028\n"), EXAMPLE_OUT

# --- the fill-in ---------------------------------------------------------------------------

FILL_HEAD = '''import numpy as np

functions = [lambda x: 3 * x + 1, np.exp, lambda v: 1 / v]
derivatives = [lambda x: 3.0, np.exp, lambda v: -1 / v**2]


def forward(x):
    values = [x]
    for f in functions:
        values.append(f(VALUE))
    return values


def backward(values):
    grad = 1.0
    for df, v in zip(reversed(derivatives), reversed(values[:-1])):
        grad = grad * df(ARG)
    return grad


def whole(x):
    return 1 / np.exp(3 * x + 1)


values = forward(0.5)
print(np.round(values, 6))
print(round(float(backward(values)), 6))
print(abs(backward(values) - (whole(0.5 + 1e-6) - whole(0.5 - 1e-6)) / 2e-6) < 1e-6)
'''
FILL_SOLUTION = FILL_HEAD.replace("VALUE", "values[-1]").replace("ARG", "v")
FILL_STARTER = FILL_HEAD.replace("VALUE", "...").replace("ARG", "...")
FILL_AT_X = FILL_HEAD.replace("VALUE", "values[-1]").replace("ARG", "values[0]")
FILL_OUT = out(FILL_SOLUTION)
print("fill:\n" + FILL_OUT)
assert FILL_OUT == "[ 0.5       2.5      12.182494  0.082085]\n-0.246255\nTrue\n", FILL_OUT
assert out(FILL_AT_X) != FILL_OUT

# --- the write ------------------------------------------------------------------------------

WRITE_STARTER = "import numpy as np\n\n\n" + SLOPE + "\n\n" + SIGMOID
WRITE_SOLUTION = WRITE_STARTER + '''

def d_sigmoid_of_linear(a, b, x):
    s = sigmoid(a * x + b)
    return s * (1 - s) * a


print(round(float(d_sigmoid_of_linear(2, 1, 2.0)), 6))
print(round(float(d_sigmoid_of_linear(-1, 0, 0.0)), 6))
print(abs(d_sigmoid_of_linear(2, 1, 2.0) - slope(lambda x: sigmoid(2 * x + 1), 2.0)) < 1e-6)
'''
WRITE_OUT = out(WRITE_SOLUTION)
print("write:\n" + WRITE_OUT)
assert WRITE_OUT == "0.013296\n-0.25\nTrue\n", WRITE_OUT

# --- the build --------------------------------------------------------------------------------

BUILD_SOLUTION = '''import numpy as np


def forward(functions, x):
    values = [x]
    for f in functions:
        values.append(f(values[-1]))
    return values


def backward(derivatives, values):
    grad = 1.0
    for df, v in zip(reversed(derivatives), reversed(values[:-1])):
        grad = grad * df(v)
    return grad


def chain_derivative(functions, derivatives, x):
    return backward(derivatives, forward(functions, x))


def numeric(functions, x, h=1e-6):
    return (forward(functions, x + h)[-1] - forward(functions, x - h)[-1]) / (2 * h)


functions = [lambda x: 2 * x, np.exp, lambda v: 1 + v, np.log]
derivatives = [lambda x: 2.0, np.exp, lambda v: 1.0, lambda w: 1 / w]
d = chain_derivative(functions, derivatives, 2.0)
print(round(float(d), 6), abs(d - numeric(functions, 2.0)) < 1e-6)
'''
BUILD_OUT = out(BUILD_SOLUTION)
print("build:\n" + BUILD_OUT)
assert BUILD_OUT == "1.964028 True\n", BUILD_OUT
BUILD_AT_X = BUILD_SOLUTION.replace("        grad = grad * df(v)", "        grad = grad * df(values[0])")
BUILD_OUTPUTS = BUILD_SOLUTION.replace("reversed(values[:-1])", "reversed(values[1:])")
BUILD_ADDS = BUILD_SOLUTION.replace("        grad = grad * df(v)", "        grad = grad + df(v)")
for wrong in (BUILD_AT_X, BUILD_OUTPUTS, BUILD_ADDS):
    assert out(wrong) != BUILD_OUT, wrong

# --- the debug -----------------------------------------------------------------------------------

DEBUG_SOLUTION = "import numpy as np\n\n\n" + SIGMOID + '''

def y(x):
    return sigmoid(3 * x + 1) ** 2


def dy(x):
    u = 3 * x + 1
    s = sigmoid(u)
    return 2 * s * (s * (1 - s)) * 3


x = 0.5
print("y", round(float(y(x)), 6))
print("dy/dx", round(float(dy(x)), 6))
numeric = (y(x + 1e-6) - y(x - 1e-6)) / 2e-6
print("matches", abs(dy(x) - numeric) < 1e-6)
'''
DEBUG_STARTER = DEBUG_SOLUTION.replace("    s = sigmoid(u)\n", "    s = sigmoid(x)\n").replace(
    "    return 2 * s * (s * (1 - s)) * 3", "    return 2 * s + (s * (1 - s)) + 3"
)
DEBUG_VALUE_ONLY = DEBUG_SOLUTION.replace("    return 2 * s * (s * (1 - s)) * 3", "    return 2 * s + (s * (1 - s)) + 3")
DEBUG_OUT = out(DEBUG_SOLUTION)
print("debug:\n" + DEBUG_OUT + "--- buggy prints:\n" + out(DEBUG_STARTER))
assert DEBUG_OUT == "y 0.854038\ndy/dx 0.388715\nmatches True\n", DEBUG_OUT

# --- predict items ----------------------------------------------------------------------------------

PREDICT_THREE = '''x = 1.0
u = 2 * x + 1
v = u**3
y = 5 * v
print(u, v, y)
print(5 * (3 * u**2) * 2)
'''
PREDICT_THREE_OUT = out(PREDICT_THREE)
print("predict three:\n" + PREDICT_THREE_OUT)
assert PREDICT_THREE_OUT == "3.0 27.0 135.0\n270.0\n", PREDICT_THREE_OUT

REVIEW_TWO = '''x = 1.0
u = x**2 + 1
y = u**3
print(u, y)
print(3 * u**2 * (2 * x))
'''
REVIEW_TWO_OUT = out(REVIEW_TWO)
print("review two:\n" + REVIEW_TWO_OUT)
assert REVIEW_TWO_OUT == "2.0 8.0\n24.0\n", REVIEW_TWO_OUT

REVIEW_CODE_STARTER = "import numpy as np\n"
REVIEW_CODE_SOLUTION = REVIEW_CODE_STARTER + '''

def chain_derivative(x):
    return 3 * np.exp(3 * x)


print(round(float(chain_derivative(0.5)), 6))
'''
REVIEW_CODE_OUT = out(REVIEW_CODE_SOLUTION)
print("review code:\n" + REVIEW_CODE_OUT)
assert REVIEW_CODE_OUT == "13.445067\n", REVIEW_CODE_OUT

# =====================================================================================
# topic.yaml
# =====================================================================================

write(
    "topic.yaml",
    '''id: ml.calc.chain-rule
kind: topic
status: ready
title: "The chain rule"
summary: "Derivatives of composed functions, computed one layer at a time, which is the whole of backpropagation."
prerequisites: [ml.calc.derivatives]
packages: [numpy]
estimated_minutes: 50
rev: 1
objectives:
  - "Differentiate a composition of two functions by the chain rule, by hand and in code."
  - "Chain three or more functions, keeping the intermediate values."
  - "Check a chained derivative numerically."
  - "Say why the chain rule is what makes training a layered model possible."
# Linked, never copied or embedded: 3Blue1Brown's videos are under the
# standard YouTube licence; OpenStax is CC BY 4.0; Khan Academy is
# CC BY-NC-SA 3.0 US.
resources:
  - title: "3Blue1Brown: Essence of calculus (Grant Sanderson), chapter 4: Visualizing the chain rule and product rule"
    url: https://www.3blue1brown.com/topics/calculus
    type: video
    use: link
    license: Standard YouTube licence (linked, not copied)
  - title: "OpenStax Calculus Volume 1: section 3.6 (The Chain Rule)"
    url: https://openstax.org/details/books/calculus-volume-1
    type: reading
    use: link
    license: CC BY 4.0
  - title: "Khan Academy: Differential calculus, the chain rule unit"
    url: https://www.khanacademy.org/math/differential-calculus
    type: interactive
    use: link
    license: CC BY-NC-SA 3.0 US (linked, not copied)
practice:
  - example-three-chains-checked
  - parsons-chain-of-two
  - mcq-the-rule
  - predict-chain-of-three
  - mcq-why-layers-can-train
  - fill-forward-and-backward
  - write-d-sigmoid-of-linear
prove:
  build: build-forward-and-backward
  debug: debug-backward-pass
  explain:
    prompt: |
      A teammate asks how a 50-layer network can compute the derivative of its loss with respect to a weight in layer 3, when the loss is 47 functions away from it. In your own words: what does the chain rule say for two functions, and for a chain of many? Why does the backward pass need the values the forward pass computed? Why run it from the loss backwards rather than from the input forwards? And how would you convince yourself that a chain-rule derivative you wrote by hand is right?
    rubric:
      - id: two
        required: true
        description: "For h(x) = f(g(x)), h'(x) = f'(g(x)) times g'(x): the outer derivative evaluated at the inner value, times the inner derivative."
      - id: many
        required: true
        description: "For a chain of many, the derivative is the product of every link's local derivative, each evaluated at that link's own input; those inputs are the intermediate values, which is why the forward pass keeps them."
      - id: backwards
        required: true
        description: "The loss is one number and the weights are many: multiplying from the loss end, each layer takes the gradient accumulated so far and multiplies in its own local derivative, so one backward pass gives the derivative for every weight; from the input end you'd repeat the work for each weight."
      - id: check
        required: false
        description: "Compare it with a central difference of the whole chain at a few points; a gap in the sixth decimal means a link is wrong or evaluated at the wrong value."
    model_answer: |
      For two functions, if h is f applied after g, the derivative of h at x is the derivative of f evaluated at g(x), times the derivative of g at x. The outer slope has to be taken at the inner value, not at x, which is the mistake everyone makes once. For a chain of many functions it's the same thing repeated: the derivative of the whole chain is the product of each link's own derivative, each one evaluated at the value that link received. Those values are exactly what the forward pass computes on its way to the loss, so the forward pass stores them and the backward pass reads them; without them you'd have to recompute every link's input. The backward pass runs from the loss end because the loss is a single number while the weights are many. Starting with the derivative of the loss with respect to itself, which is 1, each layer multiplies in its own local derivative and hands the running product to the layer before it. That running product is shared by every weight further back, so one pass from the loss gives the derivative for all 50 layers' weights; going forwards from the input you would need a separate pass for each weight. To convince myself a hand-written chain-rule derivative is right, I check it numerically: nudge x up and down by a small h, run the whole chain both times, divide the difference by 2h, and compare with the formula at a few points. Agreement to six decimals means the links and the values they're evaluated at are right.
review_pool:
  - review-predict-chain-of-two
  - review-mcq-which-value
  - review-mcq-three-links
  - review-mcq-one-pass
  - review-chain-derivative
# What this topic teaches. Each question names the skills it tests, so a
# missed question can come back as a different one on the same skill
# (ADR-0011).
skills:
  - id: two
    description: "Differentiate a composition of two functions by the chain rule"
  - id: many
    description: "Chain three or more functions with a forward pass that keeps the values and a backward pass that multiplies the local derivatives"
  - id: check
    description: "Check a chained derivative against a central difference of the whole chain"
  - id: why
    description: "Say why the chain rule makes a layered model trainable"
''',
)

# =====================================================================================
# lesson.mdx
# =====================================================================================

write(
    "lesson.mdx",
    '''<Intro>

A network is functions applied one after another: multiply by weights, bend, multiply, bend, measure the loss. To train it you need the derivative of the loss with respect to a weight deep inside, and the **chain rule** is the one fact that makes that possible: the derivative of a chain is the product of the derivatives of its links. Done in order, from the loss backwards, it is backpropagation. This topic learns the rule on two functions, then three and four, and builds the forward-and-backward pattern that the next topics run on a whole network.

The main resource is **3Blue1Brown's _Essence of calculus_, chapter 4**, visualizing the chain rule and product rule; 17 minutes. OpenStax _Calculus Volume 1_, section 3.6, has the rule with worked examples, and Khan Academy's chain rule unit has practice problems. Watch for:

- **The nested nudge:** a small change in `x` changes the inner function a little, and that change is what the outer function sees.
- **Where the outer derivative is evaluated:** at the inner function's value, never at `x` itself.
- **Why it's a product**, and why a chain of many is just the same product with more factors.

</Intro>

<Resource index={0} />

<Recap>

- **The rule.** If `y = f(g(x))`, then `dy/dx = f'(g(x)) * g'(x)`: the outer derivative **at the inner value**, times the inner derivative. For `(3x + 1)²`: inner `u = 3x + 1`, outer `u²`, so `2u * 3`; at `x = 2`, `u = 7` and the slope is 42. For `sigmoid(2x + 1)`: `s * (1 - s) * 2` with `s = sigmoid(2x + 1)`.
- **A chain of many** is the same rule applied link by link: the derivative of the whole is the **product of the local derivatives**, each evaluated at the value its link received. For `log(1 + exp(2x))`: `u = 2x`, `v = exp(u)`, `w = 1 + v`, `y = log(w)`, with local derivatives `2`, `v`, `1`, `1 / w`, so `dy/dx = 2 * v * 1 * (1 / w)` (1.964028 at `x = 2`).
- **The forward pass** runs the chain and keeps every intermediate value (`x, u, v, w, y`), because the backward pass needs them: each local derivative is evaluated at its own input.
- **The backward pass** starts from `grad = 1` at the output and multiplies in the local derivatives from the output end inward: `1 / w`, then `1`, then `v`, then `2`. In code, `for df, value in zip(reversed(derivatives), reversed(values[:-1]))`. The running product is the derivative of the output with respect to each intermediate value as it passes.
- **Check it.** Run the whole chain at `x + h` and `x - h`, take the central difference, and compare with the product. The two commonest mistakes, evaluating a link at `x` instead of at its own input and adding the local derivatives instead of multiplying, both show up in the sixth decimal.
- **Why layers can train.** A network is a long chain, and the loss is one number. Multiplying from the loss end, each layer takes the gradient accumulated so far, multiplies in its own local derivative and passes the result back, so one backward pass gives the derivative of the loss for every weight at once. No one writes a formula for the whole network; each layer only knows itself.
- **In machine learning:** this is backpropagation in miniature. The next topics add loss functions as the last link, then run the same forward-and-backward pattern on a network with matrices in place of numbers.

</Recap>
''',
)

# =====================================================================================
# recall
# =====================================================================================

write(
    "recall/parsons-chain-of-two.yaml",
    '''id: parsons-chain-of-two
type: parsons
rev: 1
prompt: |
  Put the lines in order to differentiate `exp(x²)` at `x = 2` by the chain rule and check it numerically, printing `True`. One line is a decoy that doesn't belong.
lines:
  - 'import numpy as np'
  - 'x = 2.0'
  - 'u = x**2'
  - 'by_rule = np.exp(u) * 2 * x'
  - 'numeric = (np.exp((x + 1e-6) ** 2) - np.exp((x - 1e-6) ** 2)) / 2e-6'
  - 'print(abs(by_rule - numeric) < 1e-6)'
distractors:
  - 'by_rule = np.exp(x) * 2 * x'
explanation: |
  Inner `u = x²`, outer `exp(u)`. The outer derivative is `exp` evaluated at the **inner value** `u = 4`, times the inner derivative `2x = 4`: about 218.4, and the numeric slope agrees. The decoy evaluates `exp` at `x` itself, about 29.6, which is nothing like the slope.
skills: [two, check]
''',
)

write(
    "recall/mcq-the-rule.yaml",
    '''id: mcq-the-rule
type: mcq
rev: 1
prompt: |
  `h(x) = f(g(x))`: first `g`, then `f` on the result. Which is `h'(x)`?
choices:
  - '`f''(g(x)) * g''(x)`: the outer derivative, evaluated at the inner value, times the inner derivative'
  - '`f''(x) * g''(x)`: both derivatives at `x`, multiplied'
  - '`f''(g(x)) + g''(x)`: the two derivatives added'
  - '`f(g''(x))`: the outer function applied to the inner derivative'
answer: 0
explanation: |
  A nudge to `x` changes `g` by about `g'(x)` times the nudge, and that change is what `f` sees, at the point `g(x)`, so it changes `f` by about `f'(g(x))` times that: a product, with the outer slope taken where the outer function actually is. Adding the derivatives, or evaluating the outer one at `x`, are the two mistakes the check exercises are built to catch.
skills: [two]
''',
)

write(
    "recall/predict-chain-of-three.yaml",
    f'''id: predict-chain-of-three
type: predict_output
rev: 1
prompt: |
  A chain of three links, `y = 5 * (2x + 1)³`, with its intermediate values kept. What does the program print?
code: |
{block(PREDICT_THREE)}expected_output: |
{block(PREDICT_THREE_OUT)}explanation: |
  Forward: `u = 3`, `v = 27`, `y = 135`. Backward, the local derivatives are 5 (for `5v`), `3u² = 27` (for `u³`, evaluated at `u = 3`) and 2 (for `2x + 1`), and their product is 270. Note the middle link is evaluated at `u`, the value it received, not at `x`.
skills: [many]
''',
)

write(
    "recall/mcq-why-layers-can-train.yaml",
    '''id: mcq-why-layers-can-train
type: mcq
rev: 1
prompt: |
  A network applies fifty functions one after another, and training needs the derivative of the loss with respect to a weight in the third one. Why does the chain rule make that possible?
choices:
  - 'The derivative of the whole chain is the product of each layer''s own local derivative, so each layer only needs its own derivative and the gradient handed back from the layer after it; no one needs a formula for the whole network'
  - 'The chain rule writes one closed formula for all fifty layers at once, which the computer then differentiates'
  - 'The chain rule only works for two functions, so networks are limited to two layers'
  - 'It makes the derivative independent of the layers in between, so the third layer can be trained on its own'
answer: 0
explanation: |
  Each layer knows how to differentiate itself, and nothing else. The backward pass multiplies those local derivatives from the loss inward, so the gradient arriving at layer 3 already contains everything after it, and layer 3 just multiplies in its own factor. That's why adding layers adds work but never requires new mathematics.
skills: [why]
''',
)

write(
    "recall/review-predict-chain-of-two.yaml",
    f'''id: review-predict-chain-of-two
type: predict_output
rev: 1
prompt: |
  `y = (x² + 1)³` at `x = 1`, by the chain rule. What does the program print?
code: |
{block(REVIEW_TWO)}expected_output: |
{block(REVIEW_TWO_OUT)}explanation: |
  Inner `u = x² + 1 = 2`, outer `u³ = 8`. The outer derivative `3u²` is evaluated at `u = 2`, giving 12, and the inner derivative is `2x = 2`: the product is 24.
skills: [two]
''',
)

write(
    "recall/review-mcq-which-value.yaml",
    '''id: review-mcq-which-value
type: mcq
rev: 1
prompt: |
  `h(x) = exp(x³)` at `x = 2`. By the chain rule, the outer derivative (which is `exp` again) is evaluated at which number?
choices:
  - '8, the inner value `x³`'
  - '2, the input `x`'
  - '12, the inner derivative `3x²`'
  - 'It doesn''t matter; `exp` is its own derivative'
answer: 0
explanation: |
  The outer function receives `x³ = 8`, so its slope is taken there: `exp(8)`, times the inner derivative 12. Taking `exp(2)` instead is the classic chain-rule slip, and `exp` being its own derivative is exactly why the point it's evaluated at matters.
skills: [two, check]
''',
)

write(
    "recall/review-mcq-one-pass.yaml",
    '''id: review-mcq-one-pass
type: mcq
rev: 1
prompt: |
  A network has a million weights and its loss is one number. How many backward passes does it take to get the derivative of the loss with respect to every weight?
choices:
  - 'One: the gradient flowing back from the loss is shared by every weight behind it, and each layer multiplies in its own local derivative as it passes'
  - 'A million, one per weight'
  - 'One per layer'
  - 'It depends on the learning rate'
answer: 0
explanation: |
  Multiplying from the loss end, the running product at any layer is the derivative of the loss with respect to that layer's output, and every weight in or before that layer reuses it. That's why the pass runs backwards: one pass, every weight. Going forwards from each weight in turn would need a pass per weight.
skills: [why]
''',
)

write(
    "recall/review-mcq-three-links.yaml",
    '''id: review-mcq-three-links
type: mcq
rev: 1
prompt: |
  A chain of three functions has local derivatives 2, 5 and 0.1 at the values each link received. What is the derivative of the whole chain there?
choices:
  - '1.0, the product'
  - '7.1, the sum'
  - '0.1, the last link''s'
  - '2, the first link''s'
answer: 0
explanation: |
  The chain rule multiplies: `2 * 5 * 0.1 = 1`. A nudge is scaled by each link in turn, so the scalings compound. Adding them is the mistake the debug exercise plants, and it gives 7.1 here.
skills: [many]
''',
)

# =====================================================================================
# exercises
# =====================================================================================

write(
    "exercises/example-three-chains-checked/exercise.yaml",
    f'''id: example-three-chains-checked
stage: worked_example
rev: 1
title: "Three chains, each checked"
prompt: |
  This program differentiates a chain of two, then a sigmoid of a line, then a chain of four, by the chain rule, checks each against a numeric slope, and finishes with a backward pass that multiplies the local derivatives from the output end inward. Press **Run**, then read how each part works.
steps:
  - label: "A chain of two"
    lines: "12-14"
    note: "`(3x + 1)²` is `u²` with `u = 3x + 1` inside. The outer derivative is `2u`, taken at the inner value `u = 7`, and the inner derivative is 3: `2 * 7 * 3 = 42`. The numeric slope of the whole thing agrees."
  - label: "The sigmoid of a line"
    lines: "16-18"
    note: "Outer `sigmoid`, inner `2x + 1`. The sigmoid's derivative is `s * (1 - s)` at the inner value `u = 5`, times the inner derivative 2: 0.013296 either way. This is the shape of every unit in a network: a line, then a bend."
  - label: "Four links: the forward pass"
    lines: "20-25"
    note: "`log(1 + exp(2x))`, link by link: `u = 2x`, `v = exp(u)`, `w = 1 + v`, `y = log(w)`. Each line is one link, and each value is kept, because the next line prints the four **local derivatives** evaluated at those values: 2, `v`, 1 and `1 / w`."
  - label: "The product of the local derivatives"
    lines: "26"
    note: "The derivative of the whole chain is the product of the four: 1.964028, and the numeric slope of the whole chain agrees to six decimals."
  - label: "The backward pass"
    lines: "28-31"
    note: "The same product, done the way a network does it: start at the output with `grad = 1`, multiply in `1 / w` (the last link), then 1, then `v`, then 2. Each step, `grad` is the derivative of `y` with respect to the value at that point in the chain. This loop, with matrices in place of numbers, is backpropagation."
''',
)
write("exercises/example-three-chains-checked/solution.py", EXAMPLE)
write(
    "exercises/example-three-chains-checked/test_exercise.py",
    f'''from checks import run


def test_the_walkthrough():
    """Prints three checked chain-rule derivatives and a backward pass."""
    assert run() == {EXAMPLE_OUT!r}
''',
)

write(
    "exercises/fill-forward-and-backward/exercise.yaml",
    f'''id: fill-forward-and-backward
stage: fill_in
rev: 1
title: "Forward and backward"
prompt: |
  The chain is `1 / exp(3x + 1)`: three links, listed inner first in `functions`, with their derivatives in `derivatives`. `forward` should run the links in turn and keep every value; `backward` should multiply the local derivatives from the output end inward, each evaluated at the value its link received. Replace each `...` so the program prints the values, the derivative at `x = 0.5`, and a numeric check:

  ```
{block(FILL_OUT)}  ```

  The program fails until every `...` is replaced.
hints:
  - "Each link takes the value the previous link produced: the last entry of `values`."
  - "`zip(reversed(derivatives), reversed(values[:-1]))` pairs each link's derivative with the value that link received; evaluate the derivative there."
skills: [many, check]
''',
)
write("exercises/fill-forward-and-backward/starter.py", FILL_STARTER)
write("exercises/fill-forward-and-backward/solution.py", FILL_SOLUTION)
write(
    "exercises/fill-forward-and-backward/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints the four values, the derivative and True."""
    printed = run()
    assert printed == {FILL_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_at_another_point():
    """At x = 0 the values are [0, 1, e, 1/e] and the derivative is -3/e."""
    forward = function("forward")
    backward = function("backward")
    values = forward(0.0)
    assert np.allclose(values, [0.0, 1.0, np.e, 1 / np.e])
    assert abs(backward(values) + 3 / np.e) < 1e-9
''',
)
write("exercises/fill-forward-and-backward/wrong/evaluated-at-x.py", FILL_AT_X)
write(
    "exercises/fill-forward-and-backward/wrong/typed-in.py",
    '''import numpy as np


def forward(x):
    return [x, 2.5, 12.182494, 0.082085]


def backward(values):
    return -0.246255


print("[ 0.5       2.5      12.182494  0.082085]")
print(-0.246255)
print(True)
''',
)

write(
    "exercises/write-d-sigmoid-of-linear/exercise.yaml",
    f'''id: write-d-sigmoid-of-linear
stage: write
rev: 1
title: "The derivative of a unit"
prompt: |
  One unit of a network is a line followed by a bend: `sigmoid(a * x + b)`. Write `d_sigmoid_of_linear(a, b, x)`, its derivative with respect to `x` by the chain rule, using the starter's `sigmoid`. Then print it, rounded to 6 places, for `a = 2, b = 1, x = 2.0` and for `a = -1, b = 0, x = 0.0`, and whether the first agrees with the starter's `slope` of the whole unit (`abs(...) < 1e-6`):

  ```
{block(WRITE_OUT)}  ```
hints:
  - "Inner `u = a * x + b`, with derivative `a`; outer `sigmoid`, with derivative `s * (1 - s)` evaluated at `u`."
  - "A negative `a` flips the sign: the unit falls as `x` rises."
skills: [two, check]
''',
)
write("exercises/write-d-sigmoid-of-linear/starter.py", WRITE_STARTER)
write("exercises/write-d-sigmoid-of-linear/solution.py", WRITE_SOLUTION)
write(
    "exercises/write-d-sigmoid-of-linear/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def test_the_output():
    """Prints the two derivatives and True."""
    printed = run()
    assert printed == {WRITE_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_other_units():
    """For a = 3, b = -1 at x = 0.4 the result matches a central difference, and a = 0 gives 0."""
    d = function("d_sigmoid_of_linear")
    numeric = (sigmoid(3 * 0.4 - 1 + 3e-6) - sigmoid(3 * 0.4 - 1 - 3e-6)) / 2e-6
    assert abs(d(3, -1, 0.4) - numeric) < 1e-6
    assert abs(d(0, 2, 1.0)) < 1e-12
''',
)
write(
    "exercises/write-d-sigmoid-of-linear/wrong/forgets-a.py",
    WRITE_SOLUTION.replace("    return s * (1 - s) * a", "    return s * (1 - s)"),
)
write(
    "exercises/write-d-sigmoid-of-linear/wrong/typed-in.py",
    WRITE_STARTER + '''

def d_sigmoid_of_linear(a, b, x):
    return 0.013296 if a == 2 else -0.25


print(0.013296)
print(-0.25)
print(True)
''',
)

# --- the proof ----------------------------------------------------------------------------------------

write(
    "exercises/build-forward-and-backward/exercise.yaml",
    f'''id: build-forward-and-backward
stage: build
rev: 1
title: "A forward pass and a backward pass"
prompt: |
  Starting from a blank editor, write the pattern a network's training runs on, for a chain of one-input functions:

  - `forward(functions, x)`: applies the functions in order, each to the previous result, and returns the list of **all** the values, starting with `x` itself (so it has one more entry than `functions`).
  - `backward(derivatives, values)`: given the links' derivative functions (in the same order as the links) and the values from `forward`, returns the derivative of the whole chain with respect to `x`: the product of each link's derivative **evaluated at the value that link received**, multiplied from the output end inward.
  - `chain_derivative(functions, derivatives, x)`: the two together.
  - `numeric(functions, x, h=1e-6)`: the central difference of the whole chain, for checking.

  Then, for the chain `log(1 + exp(2x))` as four links (`2x`, `exp`, `1 + v`, `log`), print its derivative at `x = 2.0` rounded to 6 places and whether `numeric` agrees within `1e-6`:

  ```
{block(BUILD_OUT)}  ```

  The checks run other chains, including ones where evaluating a link at the wrong value gives a wrong answer.
skills: [many, check, two]
''',
)
write("exercises/build-forward-and-backward/starter.py", "")
write("exercises/build-forward-and-backward/solution.py", BUILD_SOLUTION)
write(
    "exercises/build-forward-and-backward/test_exercise.py",
    f'''import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints 1.964028 True."""
    assert run() == {BUILD_OUT!r}


def test_forward_keeps_every_value():
    """forward([x², x + 1], 3) is [3, 9, 10]."""
    forward = function("forward")
    assert forward([lambda x: x**2, lambda u: u + 1], 3.0) == [3.0, 9.0, 10.0]


def test_links_are_evaluated_at_their_own_inputs():
    """For x² then u³ at x = 2 the derivative is 192 (3u² at u = 4, times 2x); a chain of one exp at 0 gives 1."""
    chain_derivative = function("chain_derivative")
    d = chain_derivative([lambda x: x**2, lambda u: u**3], [lambda x: 2 * x, lambda u: 3 * u**2], 2.0)
    assert abs(d - 192.0) < 1e-9
    assert abs(chain_derivative([np.exp], [np.exp], 0.0) - 1.0) < 1e-12


def test_numeric_and_rule_agree_on_another_chain():
    """For x² then exp at 1.5, numeric and chain_derivative agree, and both are about 28.46."""
    chain_derivative = function("chain_derivative")
    numeric = function("numeric")
    functions = [lambda x: x**2, np.exp]
    d = chain_derivative(functions, [lambda x: 2 * x, np.exp], 1.5)
    assert abs(d - 3 * np.exp(2.25)) < 1e-9
    assert abs(numeric(functions, 1.5) - d) < 1e-5
''',
)
write("exercises/build-forward-and-backward/wrong/evaluated-at-x.py", BUILD_AT_X)
write("exercises/build-forward-and-backward/wrong/evaluated-at-outputs.py", BUILD_OUTPUTS)
write("exercises/build-forward-and-backward/wrong/adds-the-links.py", BUILD_ADDS)
write(
    "exercises/build-forward-and-backward/wrong/typed-in.py",
    '''import numpy as np


def forward(functions, x):
    return [x, 4.0, 54.59815, 55.59815, 4.01815]


def backward(derivatives, values):
    return 1.964028


def chain_derivative(functions, derivatives, x):
    return 1.964028


def numeric(functions, x, h=1e-6):
    return 1.964028


print("1.964028 True")
''',
)

write(
    "exercises/debug-backward-pass/exercise.yaml",
    f'''id: debug-backward-pass
stage: debug
rev: 1
title: "A derivative that doesn't match"
prompt: |
  `y(x)` is `sigmoid(3x + 1)` squared, a chain of three links, and `dy(x)` should be its derivative by the chain rule. The program should print:

  ```
{block(DEBUG_OUT)}  ```

  It has two bugs, both in `dy`, and the last line says so (`matches False`). Read `dy` against the chain: the middle link, the sigmoid, must be evaluated at the value it receives, `u = 3x + 1`, not at `x`; and the three local derivatives must be **multiplied**, not added.
skills: [two, many, check]
''',
)
write("exercises/debug-backward-pass/starter.py", DEBUG_STARTER)
write("exercises/debug-backward-pass/solution.py", DEBUG_SOLUTION)
write(
    "exercises/debug-backward-pass/test_exercise.py",
    f'''import numpy as np

from checks import function, run

EXPECTED = {DEBUG_OUT!r}


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def test_the_output():
    """Prints y, dy/dx and matches True."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\\n{{EXPECTED}}\\nYour program printed:\\n{{printed}}"


def test_at_another_point():
    """At x = -1 the derivative matches a central difference of y."""
    y = function("y")
    dy = function("dy")
    numeric = (y(-1 + 1e-6) - y(-1 - 1e-6)) / 2e-6
    assert abs(dy(-1.0) - numeric) < 1e-6
''',
)
write("exercises/debug-backward-pass/wrong/value-only.py", DEBUG_VALUE_ONLY)
write(
    "exercises/debug-backward-pass/wrong/typed-in.py",
    "import numpy as np\n\n\n"
    + SIGMOID
    + "\n\ndef y(x):\n    return sigmoid(3 * x + 1) ** 2\n\n\ndef dy(x):\n    return 0.388715\n\n\n"
    + "".join(f"print({line!r})\n" for line in DEBUG_OUT.splitlines()),
)

# --- review pool: a code exercise ---------------------------------------------------------------------

write(
    "exercises/review-chain-derivative/exercise.yaml",
    f'''id: review-chain-derivative
stage: review_code
rev: 1
title: "A chain of two, from memory"
prompt: |
  Write `chain_derivative(x)`, the derivative of `exp(3 * x)` with respect to `x` by the chain rule, and print it at `x = 0.5` rounded to 6 places:

  ```
{block(REVIEW_CODE_OUT)}  ```
skills: [two]
''',
)
write("exercises/review-chain-derivative/starter.py", REVIEW_CODE_STARTER)
write("exercises/review-chain-derivative/solution.py", REVIEW_CODE_SOLUTION)
write(
    "exercises/review-chain-derivative/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints 13.445067."""
    assert run() == {REVIEW_CODE_OUT!r}


def test_other_points():
    """At 0 the derivative is 3, and at 1 it matches a central difference."""
    chain_derivative = function("chain_derivative")
    assert abs(chain_derivative(0.0) - 3.0) < 1e-9
    numeric = (np.exp(3 * (1 + 1e-6)) - np.exp(3 * (1 - 1e-6))) / 2e-6
    assert abs(chain_derivative(1.0) - numeric) < 1e-5
''',
)
write(
    "exercises/review-chain-derivative/wrong/forgets-the-inner.py",
    REVIEW_CODE_STARTER + '''

def chain_derivative(x):
    return np.exp(3 * x)


print(round(float(chain_derivative(0.5)), 6))
''',
)
write(
    "exercises/review-chain-derivative/wrong/typed-in.py",
    REVIEW_CODE_STARTER + '''

def chain_derivative(x):
    return 13.445067


print(13.445067)
''',
)

print("ml.calc.chain-rule written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
