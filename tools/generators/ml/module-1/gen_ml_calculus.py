"""Writes the topic ml.math.calculus (the ML track's seventh topic). Run from
the repository root. Files are written as bytes with LF endings."""

import pathlib

ROOT = pathlib.Path("content/topics/ml.math.calculus")


def write(relative: str, text: str) -> None:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


write(
    "topic.yaml",
    '''id: ml.math.calculus
kind: topic
status: ready
title: "Calculus"
summary: "The slope of a curve at a point, the power rule checked in code, and finding a minimum by going downhill."
prerequisites: [ml.math.functions, py.while-loops]
estimated_minutes: 50
rev: 1
objectives:
  - "Estimate a function's slope at a point from two nearby values."
  - "Check the power rule numerically."
  - "Read the sign of the derivative as going up or going down."
  - "Find a minimum by stepping against the slope."
resources:
  - title: "OpenStax Calculus Volume 1: sections 3.1 (Defining the Derivative), 3.3 (Differentiation Rules) and 4.3 (Maxima and Minima)"
    url: https://openstax.org/details/books/calculus-volume-1
    type: reading
    use: link
    license: CC BY 4.0
  - title: "3Blue1Brown: Essence of calculus (Grant Sanderson), chapters 1 to 3"
    url: https://www.3blue1brown.com/topics/calculus
    type: video
    use: link
    license: Standard YouTube licence (linked, not copied)
  - title: "Khan Academy: Differential calculus"
    url: https://www.khanacademy.org/math/differential-calculus
    type: interactive
    use: link
    license: CC BY-NC-SA 3.0 US (linked, not copied)
practice:
  - example-slope-at-a-point
  - parsons-numeric-derivative
  - mcq-sign-of-the-derivative
  - predict-power-rule-check
  - mcq-derivative-of-a-power
  - fill-one-step-downhill
  - write-walk-downhill
prove:
  build: build-find-the-minimum
  debug: debug-the-walk-goes-wrong
  explain:
    prompt: |
      A program is looking for the lowest point of a curve `loss(x)` by repeating `x = x - rate * slope`, where `slope` is the derivative of `loss` at `x`. In your own words: why does subtracting the slope move `x` towards the bottom, whichever side of the bottom it starts on? Why do the steps get smaller as it gets close, without anyone telling them to? And what goes wrong if `rate` is too large?
    rubric:
      - id: sign
        required: true
        description: "The derivative's sign says which way is uphill: positive means the curve rises to the right, so subtracting moves left, towards the bottom; negative means it falls to the right, so subtracting a negative moves right."
      - id: shrinking
        required: true
        description: "Near the bottom the slope approaches zero, so rate * slope, the step, shrinks by itself."
      - id: too-large
        required: true
        description: "Too large a rate overshoots the bottom, lands on the other side higher up, and can bounce further out each step instead of settling."
      - id: ml
        required: false
        description: "Says this is how a model is trained: the loss is a function of its knobs, and gradient descent turns them."
    model_answer: |
      The derivative at x is the slope of the curve there. If it's positive the curve goes up to the right, so the bottom is to the left, and x - rate * slope makes x smaller: a step left. If it's negative the curve goes down to the right, so the bottom is to the right, and subtracting a negative number makes x bigger: a step right. Either way the step is against the slope, which is downhill. As x gets close to the bottom the curve flattens out and the slope approaches zero, so rate * slope, the size of the step, shrinks on its own; nothing has to count down. If the rate is too large, a step can jump right over the bottom and land on the other side, higher than where it started, and the next step, with an even bigger slope, jumps further still, so instead of settling the walk bounces away. This is how a model is trained: its loss is a function of its knobs, and gradient descent turns the knobs a little against the slope, over and over.
review_pool:
  - review-predict-slope-sign
  - review-mcq-learning-rate
  - review-two-steps
# What this topic teaches. Each question names the skills it tests, so a
# missed question can come back as a different one on the same skill
# (ADR-0011).
skills:
  - id: numeric-derivative
    description: "Estimate a function's slope at a point from two nearby values"
  - id: power-rule
    description: "Know the derivative of a power, and check it numerically"
  - id: sign
    description: "Read the sign of the derivative as going up or going down"
  - id: descent
    description: "Find a minimum by stepping against the slope"
''',
)

write(
    "lesson.mdx",
    '''<Intro>

The derivative of a function is its slope at a point: how fast the output changes when the input moves a little. A computer can estimate it without any rules, by moving the input a little and dividing. That estimate, and the idea of walking downhill against it, is how every machine-learning model is trained; this topic builds both from scratch.

The main resource is the free textbook *OpenStax Calculus Volume 1*: **section 3.1** (what a derivative is, up to the first examples), **section 3.3** (the differentiation rules, as far as the power rule) and **section 4.3** (maxima and minima, the first page or two). About 30 minutes; the proofs can wait, the pictures can't. If you'd rather watch, the first three chapters of 3Blue1Brown's *Essence of calculus* are linked below the lesson. Watch for:

- **The slope at a point** is what the slope between two points becomes as they get close together.
- **The power rule:** the derivative of xⁿ is n·xⁿ⁻¹. You'll check it with code.
- **The sign of the derivative** says whether the function is going up or down there, and a minimum is where the slope is zero.

Everything here runs: `(f(x + h) - f(x)) / h` with a small `h` is a derivative you can print.

</Intro>

<Resource index={0} />

<Recap>

- **A slope between two points** is rise over run: `(f(x + h) - f(x)) / h`. As `h` shrinks, it settles on the **slope at the point**, the derivative. For `f(x) = x ** 2` at `x = 3`: `h = 0.1` gives 6.1, `h = 0.001` gives 6.001, and the exact answer is 6. With `h = 0.000001` the estimate is good to several decimals; that's what the code uses.
- **The power rule:** the derivative of `x ** n` is `n * x ** (n - 1)`. So `x ** 2` has derivative `2 * x`, and `x ** 3` has `3 * x ** 2`. Check any rule you're told by comparing it with the numeric slope at a few points.
- **The sign tells the direction.** A positive derivative means the function is going up as x increases; negative means going down; zero means flat, which at the bottom of a valley is a **minimum**.
- **Walking downhill (gradient descent):** from any x, `x = x - rate * slope` moves against the slope, towards lower values. The `rate` is the step size. Near the bottom the slope shrinks, so the steps shrink by themselves; too large a rate overshoots and can bounce away.
- **Stop when the slope is small:** `while abs(slope) > 0.01`, counting the steps.
- **In machine learning:** a model's loss is a function of its knobs; the derivative of the loss with respect to each knob says which way to turn it; training is gradient descent, millions of knobs at a time. The learning rate you'll see in every training script is the `rate` here.

</Recap>
''',
)

# --- practice: recall --------------------------------------------------------

write(
    "recall/parsons-numeric-derivative.yaml",
    '''id: parsons-numeric-derivative
type: parsons
rev: 1
prompt: |
  Put the lines in order so the program estimates the slope of `x ** 3` at `x = 2` and prints `12.0`. One line is a decoy that doesn't belong.
lines:
  - 'def f(x):'
  - '    return x ** 3'
  - 'h = 0.0001'
  - 'slope = (f(2 + h) - f(2)) / h'
  - 'print(round(slope, 2))'
distractors:
  - 'slope = (f(2 + h) - f(2)) * h'
explanation: |
  The slope between two nearby points is rise over run: the change in `f` **divided** by the small step `h`. With `h` small the estimate is close to the exact derivative, `3 * 2 ** 2`, which is 12. The decoy multiplies by `h` instead of dividing, and gives nearly 0.
skills: [numeric-derivative]
''',
)

write(
    "recall/mcq-sign-of-the-derivative.yaml",
    '''id: mcq-sign-of-the-derivative
type: mcq
rev: 1
prompt: |
  The derivative of a function is negative everywhere between `x = 2` and `x = 5`. What is the function doing there?
choices:
  - 'Going down as x increases'
  - 'Going up as x increases'
  - 'Staying constant'
  - 'Crossing zero'
answer: 0
explanation: |
  The derivative is the slope. A negative slope means the function falls as x moves right: it's going down. (A function that stays constant has derivative zero, and the sign of the derivative says nothing about whether the function itself is positive or negative.)
skills: [sign]
''',
)

write(
    "recall/predict-power-rule-check.yaml",
    '''id: predict-power-rule-check
type: predict_output
rev: 1
prompt: |
  The power rule says the derivative of `x ** 2` is `2 * x`. This program checks it at `x = 5`. What does it print?
code: |
  def f(x):
      return x ** 2


  def rule(x):
      return 2 * x


  h = 0.000001
  print(rule(5))
  print(round((f(5 + h) - f(5)) / h, 3))
expected_output: |
  10
  10.0
explanation: |
  The rule gives `2 * 5`, `10`. The numeric slope `(f(5.000001) - f(5)) / 0.000001` is 10.000001, which rounds to `10.0`; it's a float because of the division. The two agree, which is the point: a rule you can check is a rule you can trust.
skills: [power-rule, numeric-derivative]
''',
)

write(
    "recall/mcq-derivative-of-a-power.yaml",
    '''id: mcq-derivative-of-a-power
type: mcq
rev: 1
prompt: |
  What is the derivative of `x ** 3`?
choices:
  - '`x ** 2`'
  - '`3 * x ** 2`'
  - '`3 * x`'
  - '`x ** 4 / 4`'
answer: 1
explanation: |
  The power rule: bring the exponent down as a multiplier and lower it by one, so `x ** 3` becomes `3 * x ** 2`. At `x = 2` that's 12, which the numeric slope confirms. (`x ** 4 / 4` is the integral, the reverse operation.)
skills: [power-rule]
''',
)

write(
    "recall/review-predict-slope-sign.yaml",
    '''id: review-predict-slope-sign
type: predict_output
rev: 1
prompt: |
  The slope of `x ** 2 - 4 * x` at two points. What does the program print, and which way is the function going at each?
code: |
  def f(x):
      return x ** 2 - 4 * x


  h = 0.000001
  print(round((f(1 + h) - f(1)) / h, 2))
  print(round((f(3 + h) - f(3)) / h, 2))
expected_output: |
  -2.0
  2.0
explanation: |
  The derivative of `x ** 2 - 4 * x` is `2 * x - 4`: at `x = 1` it's `-2.0` (going down) and at `x = 3` it's `2.0` (going up). The bottom of this valley is at `x = 2`, where the slope is zero.
skills: [sign, numeric-derivative]
''',
)

write(
    "recall/review-mcq-learning-rate.yaml",
    '''id: review-mcq-learning-rate
type: mcq
rev: 1
prompt: |
  A program walks downhill with `x = x - rate * slope`. The `rate` is set far too large. What happens?
choices:
  - 'It reaches the bottom in fewer steps'
  - 'It overshoots the bottom and can bounce further away each step'
  - 'It stops immediately, because the slope becomes zero'
  - 'Nothing changes: the rate only affects how long each step takes'
answer: 1
explanation: |
  The step is `rate * slope`. Too large a rate jumps past the bottom to the other side, where the slope is bigger still, so the next jump is bigger too, and the walk can bounce out of the valley instead of settling. Machine learning calls `rate` the learning rate, and this is why choosing it matters.
skills: [descent]
''',
)

# --- practice: exercises -------------------------------------------------------

write(
    "exercises/example-slope-at-a-point/exercise.yaml",
    '''id: example-slope-at-a-point
stage: worked_example
rev: 1
title: "The slope at a point"
prompt: |
  This program estimates the slope of `x ** 2` at `x = 3` from two nearby points, then moves the points closer. Press **Run**, then read how each part works.
steps:
  - label: "The function"
    lines: "1-2"
    note: "A curve to measure: `x ** 2`. Its exact slope at `x = 3` is 6, by the power rule; the program doesn't know that."
  - label: "Rise over run"
    lines: "5-6"
    note: "Move from 3 to 3.1 and see how much `f` rose: `(f(3.1) - f(3)) / 0.1` is 6.1. That's the slope of the line through the two points, a little too steep because the curve bends upward between them."
  - label: "Bring the points closer"
    lines: "8-9"
    note: "With `h = 0.001` the estimate is 6.001. As `h` shrinks, the estimate settles on the slope **at** the point: the derivative. `round` just tidies the float."
''',
)
write(
    "exercises/example-slope-at-a-point/solution.py",
    '''def f(x):
    return x ** 2


h = 0.1
print(round((f(3 + h) - f(3)) / h, 4))

h = 0.001
print(round((f(3 + h) - f(3)) / h, 4))
''',
)
write(
    "exercises/example-slope-at-a-point/test_exercise.py",
    '''from checks import run


def test_estimates_settle():
    """Prints 6.1, then 6.001."""
    assert run() == "6.1\\n6.001\\n"
''',
)

write(
    "exercises/fill-one-step-downhill/exercise.yaml",
    '''id: fill-one-step-downhill
stage: fill_in
rev: 1
title: "One step downhill"
prompt: |
  The curve `(x - 3) ** 2` has its lowest point at `x = 3`, and its slope at any `x` is `2 * (x - 3)`. From `x = 0`, replace each `...` so the program takes one step against the slope with a rate of 0.1 and prints the new `x`:

  ```
  0.6
  ```

  Until every `...` is replaced, Python can't run the program at all, and shows a syntax error.
hints:
  - "The slope is twice the distance from 3: `2 * (x - 3)`. At `x = 0` that's -6, negative, so the bottom is to the right."
  - "A step against the slope **subtracts** `rate * slope`. Subtracting -0.6 moves x to the right."
skills: [descent]
''',
)
write(
    "exercises/fill-one-step-downhill/starter.py",
    '''x = 0
rate = 0.1
slope = 2 * (x ... 3)
x = x ... rate * slope
print(round(x, 2))
''',
)
write(
    "exercises/fill-one-step-downhill/solution.py",
    '''x = 0
rate = 0.1
slope = 2 * (x - 3)
x = x - rate * slope
print(round(x, 2))
''',
)
write(
    "exercises/fill-one-step-downhill/test_exercise.py",
    '''from checks import run, run_with


def test_from_zero():
    """Prints 0.6."""
    printed = run()
    assert printed == "0.6\\n", f"Your program printed:\\n{printed}"


def test_from_the_other_side():
    """From x = 5 the step goes left, to 4.6."""
    printed = run_with({"x": 5})
    assert printed == "4.6\\n", f"From x = 5 it should print 4.6. It printed:\\n{printed}"
''',
)
write(
    "exercises/fill-one-step-downhill/wrong/steps-uphill.py",
    '''x = 0
rate = 0.1
slope = 2 * (x - 3)
x = x + rate * slope
print(round(x, 2))
''',
)
write(
    "exercises/fill-one-step-downhill/wrong/typed-in.py",
    '''x = 0
rate = 0.1
x = 0.6
print(round(x, 2))
''',
)

write(
    "exercises/write-walk-downhill/exercise.yaml",
    '''id: write-walk-downhill
stage: write
rev: 1
title: "Walk downhill"
prompt: |
  Starting from `x = 0.0` with `rate = 0.1`, walk down the curve `(x - 3) ** 2`, whose slope is `2 * (x - 3)`: repeat `x = x - rate * slope` while the slope's absolute value is more than 0.01, counting the steps. Then print where you stopped, rounded to 3 decimal places, and how many steps it took:

  ```
  Stopped at 2.995 after 29 steps
  ```

  Keep the two starting lines: the checks run your program from another start too.
hints:
  - "Work out the slope at the current x at the top of each loop: `slope = 2 * (x - 3)`."
  - "`while abs(slope) > 0.01:` keeps going while the ground is still sloping."
  - "Inside the loop: take the step, recompute the slope, add one to the count."
skills: [descent]
''',
)
write("exercises/write-walk-downhill/starter.py", "x = 0.0\nrate = 0.1\n")
write(
    "exercises/write-walk-downhill/solution.py",
    '''x = 0.0
rate = 0.1
steps = 0
slope = 2 * (x - 3)
while abs(slope) > 0.01:
    x = x - rate * slope
    slope = 2 * (x - 3)
    steps = steps + 1
print(f"Stopped at {x:.3f} after {steps} steps")
''',
)
write(
    "exercises/write-walk-downhill/test_exercise.py",
    '''from checks import run, run_with


def test_from_zero():
    """Prints Stopped at 2.995 after 29 steps."""
    printed = run()
    assert printed == "Stopped at 2.995 after 29 steps\\n", f"Your program printed:\\n{printed}"


def test_from_ten():
    """From x = 10.0 it stops at 3.004 after 33 steps."""
    printed = run_with({"x": 10.0})
    assert printed == "Stopped at 3.004 after 33 steps\\n", (
        f"From x = 10.0 it should print Stopped at 3.004 after 33 steps. It printed:\\n{printed}"
    )
''',
)
write(
    "exercises/write-walk-downhill/wrong/slope-never-updated.py",
    '''x = 0.0
rate = 0.1
steps = 0
slope = 2 * (x - 3)
while abs(slope) > 0.01 and steps < 1000:
    x = x - rate * slope
    steps = steps + 1
print(f"Stopped at {x:.3f} after {steps} steps")
''',
)
write(
    "exercises/write-walk-downhill/wrong/typed-in.py",
    '''x = 0.0
rate = 0.1
print("Stopped at 2.995 after 29 steps")
''',
)

# --- proof ------------------------------------------------------------------

write(
    "exercises/build-find-the-minimum/exercise.yaml",
    '''id: build-find-the-minimum
stage: build
rev: 1
title: "Find the minimum"
prompt: |
  Starting from a blank editor, write three functions. `loss(x)` returns `(x - 2) ** 2 + 1`. `slope_at(x)` estimates the derivative of `loss` at `x` numerically, with `h = 0.000001`. `minimize(start, rate, steps)` starts at `start`, takes `steps` steps of `x = x - rate * slope_at(x)`, and returns the final `x`. Then print, for a start of 10, a rate of 0.1 and 50 steps:

  ```
  Lowest at x = 2.0, loss = 1.0
  ```

  Round both numbers to 3 decimal places. The checks call your functions with other arguments too.
skills: [numeric-derivative, descent]
''',
)
write("exercises/build-find-the-minimum/starter.py", "")
write(
    "exercises/build-find-the-minimum/solution.py",
    '''def loss(x):
    return (x - 2) ** 2 + 1


def slope_at(x):
    h = 0.000001
    return (loss(x + h) - loss(x)) / h


def minimize(start, rate, steps):
    x = start
    for step in range(steps):
        x = x - rate * slope_at(x)
    return x


best = minimize(10, 0.1, 50)
print(f"Lowest at x = {round(best, 3)}, loss = {round(loss(best), 3)}")
''',
)
write(
    "exercises/build-find-the-minimum/test_exercise.py",
    '''from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints Lowest at x = 2.0, loss = 1.0."""
    assert run() == "Lowest at x = 2.0, loss = 1.0\\n"


def test_the_slope():
    """slope_at(3) is about 2, and slope_at(2) is about 0."""
    slope_at = function("slope_at")
    assert round(slope_at(3), 3) == 2.0
    assert round(slope_at(2), 3) == 0.0


def test_minimize_from_elsewhere():
    """minimize(-4, 0.2, 40) also ends near 2."""
    minimize = function("minimize")
    assert round(minimize(-4, 0.2, 40), 3) == 2.0
''',
)
write(
    "exercises/build-find-the-minimum/wrong/steps-uphill.py",
    '''def loss(x):
    return (x - 2) ** 2 + 1


def slope_at(x):
    h = 0.000001
    return (loss(x + h) - loss(x)) / h


def minimize(start, rate, steps):
    x = start
    for step in range(steps):
        x = x + rate * slope_at(x)
    return x


best = minimize(10, 0.1, 50)
print(f"Lowest at x = {round(best, 3)}, loss = {round(loss(best), 3)}")
''',
)
write(
    "exercises/build-find-the-minimum/wrong/coarse-slope.py",
    '''def loss(x):
    return (x - 2) ** 2 + 1


def slope_at(x):
    h = 1
    return (loss(x + h) - loss(x)) / h


def minimize(start, rate, steps):
    x = start
    for step in range(steps):
        x = x - rate * slope_at(x)
    return x


best = minimize(10, 0.1, 50)
print(f"Lowest at x = {round(best, 3)}, loss = {round(loss(best), 3)}")
''',
)
write(
    "exercises/build-find-the-minimum/wrong/typed-in.py",
    '''def loss(x):
    return (x - 2) ** 2 + 1


def slope_at(x):
    return 2.0


def minimize(start, rate, steps):
    return 2.0


print("Lowest at x = 2.0, loss = 1.0")
''',
)

write(
    "exercises/debug-the-walk-goes-wrong/exercise.yaml",
    '''id: debug-the-walk-goes-wrong
stage: debug
rev: 1
title: "The walk goes wrong"
prompt: |
  This program should walk down the curve `(x - 3) ** 2` from `x = 0` for 30 steps, estimating the slope numerically at each step, and print where it ends up, rounded to 2 decimal places:

  ```
  3.0
  ```

  It has two bugs. Run it, fix what you find, and run it again. One bug sends the walk the wrong way; the other makes it settle in the wrong place.
skills: [descent, numeric-derivative]
''',
)
write(
    "exercises/debug-the-walk-goes-wrong/starter.py",
    '''def f(x):
    return (x - 3) ** 2


x = 0
rate = 0.1
h = 1
for step in range(30):
    slope = (f(x + h) - f(x)) / h
    x = x + rate * slope
print(round(x, 2))
''',
)
write(
    "exercises/debug-the-walk-goes-wrong/solution.py",
    '''def f(x):
    return (x - 3) ** 2


x = 0
rate = 0.1
h = 0.000001
for step in range(30):
    slope = (f(x + h) - f(x)) / h
    x = x - rate * slope
print(round(x, 2))
''',
)
write(
    "exercises/debug-the-walk-goes-wrong/test_exercise.py",
    '''from checks import run, run_with


def test_from_zero():
    """Prints 3.0."""
    printed = run()
    assert printed == "3.0\\n", f"Your program printed:\\n{printed}"


def test_from_ten():
    """From x = 10 it also ends at 3.0."""
    printed = run_with({"x": 10})
    assert printed == "3.0\\n", f"From x = 10 it should print 3.0. It printed:\\n{printed}"
''',
)
write(
    "exercises/debug-the-walk-goes-wrong/wrong/only-direction-fixed.py",
    '''def f(x):
    return (x - 3) ** 2


x = 0
rate = 0.1
h = 1
for step in range(30):
    slope = (f(x + h) - f(x)) / h
    x = x - rate * slope
print(round(x, 2))
''',
)
write(
    "exercises/debug-the-walk-goes-wrong/wrong/only-step-fixed.py",
    '''def f(x):
    return (x - 3) ** 2


x = 0
rate = 0.1
h = 0.000001
for step in range(30):
    slope = (f(x + h) - f(x)) / h
    x = x + rate * slope
print(round(x, 2))
''',
)
write(
    "exercises/debug-the-walk-goes-wrong/wrong/typed-in.py",
    '''def f(x):
    return (x - 3) ** 2


x = 0
rate = 0.1
x = 3.0
print(round(x, 2))
''',
)

# --- review pool: a code exercise -------------------------------------------

write(
    "exercises/review-two-steps/exercise.yaml",
    '''id: review-two-steps
stage: review_code
rev: 1
title: "Two steps downhill"
prompt: |
  The curve `(x - 4) ** 2` has slope `2 * (x - 4)`. Starting from `x = 0.0` with `rate = 0.25`, take two steps of `x = x - rate * slope`, printing `x` after each:

  ```
  2.0
  3.0
  ```

  Keep the two starting lines: the checks run your program from another start too.
skills: [descent]
''',
)
write("exercises/review-two-steps/starter.py", "x = 0.0\nrate = 0.25\n")
write(
    "exercises/review-two-steps/solution.py",
    '''x = 0.0
rate = 0.25
for step in range(2):
    slope = 2 * (x - 4)
    x = x - rate * slope
    print(x)
''',
)
write(
    "exercises/review-two-steps/test_exercise.py",
    '''from checks import run, run_with


def test_from_zero():
    """Prints 2.0, then 3.0."""
    assert run() == "2.0\\n3.0\\n"


def test_from_eight():
    """From x = 8.0 the steps go left: 6.0, then 5.0."""
    assert run_with({"x": 8.0}) == "6.0\\n5.0\\n"
''',
)
write(
    "exercises/review-two-steps/wrong/same-slope-twice.py",
    '''x = 0.0
rate = 0.25
slope = 2 * (x - 4)
for step in range(2):
    x = x - rate * slope
    print(x)
''',
)
write(
    "exercises/review-two-steps/wrong/typed-in.py",
    '''x = 0.0
rate = 0.25
print(2.0)
print(3.0)
''',
)

print("ml.math.calculus written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
