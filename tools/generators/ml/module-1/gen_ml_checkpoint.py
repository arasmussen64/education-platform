"""Writes ml.m1.checkpoint, "Checkpoint 1: fit a line", which closes the math
refresher (ADR-0012 shape: build and debug with test_skills, explain, and a
way through: a solved sibling, four steps, two fresh versions). Run from the
repository root. Files are written as bytes with LF endings."""

import pathlib

ROOT = pathlib.Path("content/topics/ml.m1.checkpoint")


def write(relative: str, text: str) -> None:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


write(
    "topic.yaml",
    '''id: ml.m1.checkpoint
kind: checkpoint
status: ready
title: "Checkpoint 1: fit a line"
summary: "Find the line that fits some points best by stepping downhill on the error."
prerequisites: [ml.math.exponents-and-logs, ml.math.probability-and-statistics, ml.math.vectors-and-matrices, ml.math.calculus]
estimated_minutes: 90
rev: 1
objectives:
  - "Write a model as a function with knobs: a line with a slope and an intercept."
  - "Measure how wrong it is with a mean of squared errors."
  - "Turn the knobs against the slope of the error until it stops improving."
  - "Find and fix the mistakes in a statistics report: its mean, median and spread."
  - "Explain why stepping against the derivative finds the bottom of a valley."
prove:
  build: build-fit-a-line
  debug: debug-statistics-report
  explain:
    prompt: |
      Your line-fitting program has two knobs, the slope `m` and the intercept `b`, and an error that depends on both. Each step it does `m = m - rate * slope_m` and `b = b - rate * slope_b`, where `slope_m` is how fast the error changes when `m` moves and `slope_b` the same for `b`.

      In your own words: why does each of those two lines lower the error? Why do the steps get smaller as the line gets close to the best one, without anyone telling them to? And what is the program really doing when it has finished: what does "the best line" mean here?
    rubric:
      - id: against-the-slope
        required: true
        description: "Each knob moves against its own slope: if the error rises as m increases, m is lowered, and if it falls, m is raised; the same for b, so every step lowers the error."
      - id: shrinking
        required: true
        description: "Near the best line the error is nearly flat, so the slopes approach zero and rate * slope, the step, shrinks by itself."
      - id: meaning
        required: true
        description: "The best line is the one with the smallest mean squared error: the m and b at the bottom of the error valley, where both slopes are zero."
      - id: two-knobs
        required: false
        description: "Notes that with two knobs the valley is a surface and the two slopes together point downhill; or names this as training, with rate the learning rate."
    model_answer: |
      The error is a function of two knobs, m and b, so it's a valley-shaped surface rather than a curve. slope_m is how the error changes when m alone moves a little. If it's positive, the error goes up as m goes up, so lowering m lowers the error, and m - rate * slope_m does exactly that; if it's negative, subtracting a negative raises m, which is again the downhill direction. The line for b does the same for the other knob, so each step moves both knobs against their own slopes, which is downhill on the surface. As the line gets close to the best one the surface flattens out: both slopes approach zero, so rate times the slope, the size of each step, shrinks on its own. When the program stops, the slopes are nearly zero, which means it's at the bottom: the m and b for which the mean of the squared errors is as small as it can be. That's what "the best line" means here, and this is what training a model is, with rate the learning rate and many more knobs.
# For a learner who's stuck on the build (ADR-0012): a solved sibling, the
# build in steps with hints, then fresh versions.
unstuck:
  example: example-fit-a-constant
  steps: [step-the-error, step-the-slopes, step-one-update, step-the-loop]
  versions: [build-fit-cooling, build-fit-heights]
''',
)

# ---------------------------------------------------------------------------
# The build, and its two fresh versions, share one shape.

FIT_SOLUTION = '''xs = {xs}
ys = {ys}


def predict(m, b, x):
    return m * x + b


def error(m, b, xs, ys):
    total = 0
    for i in range(len(xs)):
        total = total + (predict(m, b, xs[i]) - ys[i]) ** 2
    return total / len(xs)


def fit(xs, ys, rate, steps):
    m = 0.0
    b = 0.0
    for step in range(steps):
        slope_m = 0
        slope_b = 0
        for i in range(len(xs)):
            miss = predict(m, b, xs[i]) - ys[i]
            slope_m = slope_m + 2 * miss * xs[i]
            slope_b = slope_b + 2 * miss
        slope_m = slope_m / len(xs)
        slope_b = slope_b / len(xs)
        m = m - rate * slope_m
        b = b - rate * slope_b
    return [m, b]


line = fit(xs, ys, 0.05, 2000)
print("slope", round(line[0], 2))
print("intercept", round(line[1], 2))
'''

FIT_TEST_SKILLS = '''# Every test names the module skills it checks (ADR-0012), so a failed test
# says which topics to revisit.
test_skills:
  test_the_fit: [ml.math.calculus/descent, ml.math.functions/lines]
  test_predict_and_error: [ml.math.functions/evaluate, ml.math.probability-and-statistics/center, ml.math.algebra/substitute]
  test_fit_other_data: [ml.math.calculus/descent, ml.math.calculus/sign]
'''


def fit_test(expected: str, other_data: str) -> str:
    return f'''from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_fit():
    """Prints the slope and intercept of the best line through the given points."""
    assert run() == "{expected}"


def test_predict_and_error():
    """predict gives m * x + b, and error is the mean of the squared misses."""
    predict = function("predict")
    error = function("error")
    assert predict(2, 1, 3) == 7
    assert error(2, 1, [1, 2, 3, 4, 5], [3, 5, 7, 9, 11]) == 0.0
    assert error(0, 0, [1, 2, 3, 4, 5], [3, 5, 7, 9, 11]) == 57.0


def test_fit_other_data():
    """fit finds other lines too, including one that slopes down."""
    fit = function("fit")
{other_data}
'''


def fit_wrongs(folder: str, xs: str, ys: str, printed: str) -> None:
    base = FIT_SOLUTION.format(xs=xs, ys=ys)
    write(
        f"{folder}/wrong/steps-uphill.py",
        base.replace("        m = m - rate * slope_m\n        b = b - rate * slope_b\n",
                     "        m = m + rate * slope_m\n        b = b + rate * slope_b\n"),
    )
    write(
        f"{folder}/wrong/forgets-the-mean.py",
        base.replace("        slope_m = slope_m / len(xs)\n        slope_b = slope_b / len(xs)\n", ""),
    )
    write(
        f"{folder}/wrong/typed-in.py",
        f'''xs = {xs}
ys = {ys}


def predict(m, b, x):
    return m * x + b


def error(m, b, xs, ys):
    return 0.0


def fit(xs, ys, rate, steps):
    return {printed}


print("slope", {printed}[0])
print("intercept", {printed}[1])
''',
    )


OTHER_DATA = '''    assert [round(v, 2) for v in fit([1, 2, 3, 4, 5], [1, 4, 7, 10, 13], 0.05, 2000)] == [3.0, -2.0]
    assert [round(v, 2) for v in fit([1, 2, 3, 4, 5], [30, 28, 26, 24, 22], 0.05, 2000)] == [-2.0, 32.0]'''

write(
    "exercises/build-fit-a-line/exercise.yaml",
    '''id: build-fit-a-line
stage: build
rev: 1
title: "Fit a line"
prompt: |
  Five points lie near a line: `xs = [1, 2, 3, 4, 5]` and `ys = [3, 5, 7, 9, 11]`. Starting from a blank editor, with those two lines first, find the line that fits them best.

  Write three functions. `predict(m, b, x)` returns the line's value, `m * x + b`. `error(m, b, xs, ys)` returns the **mean of the squared misses**: for each point, the difference between the prediction and the real y, squared; averaged over the points. `fit(xs, ys, rate, steps)` starts with `m = 0.0` and `b = 0.0` and takes `steps` steps downhill on the error, returning `[m, b]`. For each step, the slope of the error with respect to `m` is the mean over the points of `2 * miss * x`, and with respect to `b` the mean of `2 * miss`, where `miss` is the prediction minus the real y; then `m = m - rate * slope_m` and `b = b - rate * slope_b`.

  Finally print the fit for a rate of 0.05 and 2000 steps, each number rounded to 2 decimal places:

  ```
  slope 2.0
  intercept 1.0
  ```

  The checks call your functions with other points too, including points on a line that slopes down.
''' + FIT_TEST_SKILLS,
)
write("exercises/build-fit-a-line/starter.py", "")
write("exercises/build-fit-a-line/solution.py", FIT_SOLUTION.format(xs="[1, 2, 3, 4, 5]", ys="[3, 5, 7, 9, 11]"))
write("exercises/build-fit-a-line/test_exercise.py", fit_test("slope 2.0\\nintercept 1.0\\n", OTHER_DATA))
fit_wrongs("exercises/build-fit-a-line", "[1, 2, 3, 4, 5]", "[3, 5, 7, 9, 11]", "[2.0, 1.0]")

# Fresh versions: the same build in other stories, with their own data.
write(
    "exercises/build-fit-cooling/exercise.yaml",
    '''id: build-fit-cooling
stage: build
rev: 1
title: "Fit a line: a cooling cup"
prompt: |
  A cup of tea was measured once an hour: `xs = [1, 2, 3, 4, 5]` (hours) and `ys = [30, 28, 26, 24, 22]` (degrees above the room). Starting from a blank editor, with those two lines first, find the line that fits the cooling best.

  Write `predict(m, b, x)` (the line's value, `m * x + b`), `error(m, b, xs, ys)` (the mean of the squared misses between predictions and real values) and `fit(xs, ys, rate, steps)`, which starts from `m = 0.0`, `b = 0.0` and steps downhill on the error: each step, the slope of the error with respect to `m` is the mean of `2 * miss * x` over the points and with respect to `b` the mean of `2 * miss`, where `miss` is prediction minus real; then `m = m - rate * slope_m` and `b = b - rate * slope_b`. Return `[m, b]`.

  Print the fit for a rate of 0.05 and 2000 steps, rounded to 2 decimal places:

  ```
  slope -2.0
  intercept 32.0
  ```
''' + FIT_TEST_SKILLS,
)
write("exercises/build-fit-cooling/starter.py", "")
write("exercises/build-fit-cooling/solution.py", FIT_SOLUTION.format(xs="[1, 2, 3, 4, 5]", ys="[30, 28, 26, 24, 22]"))
write("exercises/build-fit-cooling/test_exercise.py", fit_test("slope -2.0\\nintercept 32.0\\n", OTHER_DATA.replace("[30, 28, 26, 24, 22], 0.05, 2000)] == [-2.0, 32.0]", "[3, 5, 7, 9, 11], 0.05, 2000)] == [2.0, 1.0]")))
fit_wrongs("exercises/build-fit-cooling", "[1, 2, 3, 4, 5]", "[30, 28, 26, 24, 22]", "[-2.0, 32.0]")

write(
    "exercises/build-fit-heights/exercise.yaml",
    '''id: build-fit-heights
stage: build
rev: 1
title: "Fit a line: growing up"
prompt: |
  A child's height was measured on five birthdays: `xs = [1, 2, 3, 4, 5]` (years) and `ys = [52, 54, 56, 58, 60]` (centimetres above a baseline). Starting from a blank editor, with those two lines first, find the line that fits the growth best.

  Write `predict(m, b, x)` (the line's value, `m * x + b`), `error(m, b, xs, ys)` (the mean of the squared misses between predictions and real values) and `fit(xs, ys, rate, steps)`, which starts from `m = 0.0`, `b = 0.0` and steps downhill on the error: each step, the slope of the error with respect to `m` is the mean of `2 * miss * x` over the points and with respect to `b` the mean of `2 * miss`, where `miss` is prediction minus real; then `m = m - rate * slope_m` and `b = b - rate * slope_b`. Return `[m, b]`.

  Print the fit for a rate of 0.05 and 2000 steps, rounded to 2 decimal places:

  ```
  slope 2.0
  intercept 50.0
  ```
''' + FIT_TEST_SKILLS,
)
write("exercises/build-fit-heights/starter.py", "")
write("exercises/build-fit-heights/solution.py", FIT_SOLUTION.format(xs="[1, 2, 3, 4, 5]", ys="[52, 54, 56, 58, 60]"))
write("exercises/build-fit-heights/test_exercise.py", fit_test("slope 2.0\\nintercept 50.0\\n", OTHER_DATA))
fit_wrongs("exercises/build-fit-heights", "[1, 2, 3, 4, 5]", "[52, 54, 56, 58, 60]", "[2.0, 50.0]")

# ---------------------------------------------------------------------------
# The debug: a statistics report with three bugs, one per statistic.

write(
    "exercises/debug-statistics-report/exercise.yaml",
    '''id: debug-statistics-report
stage: debug
rev: 1
title: "A statistics report"
prompt: |
  This program should report the mean, the median and the standard deviation of `[15, 4, 42, 8, 23, 16]`, each to one decimal place:

  ```
  mean 18.0
  median 15.5
  spread 12.3
  ```

  It has three bugs, one in each statistic. Run it, fix what you find, and run it again. Check each number against its definition: the mean divides by the count; the median is the middle of the **sorted** values; the standard deviation is a square root.
test_skills:
  test_mean: [ml.math.probability-and-statistics/center]
  test_median: [ml.math.probability-and-statistics/center]
  test_spread: [ml.math.probability-and-statistics/spread, ml.math.exponents-and-logs/powers]
  test_other_values: [ml.math.probability-and-statistics/center, ml.math.probability-and-statistics/spread]
''',
)
write(
    "exercises/debug-statistics-report/starter.py",
    '''values = [15, 4, 42, 8, 23, 16]

mean = sum(values) / (len(values) - 1)

middle = len(values) // 2
median = (values[middle - 1] + values[middle]) / 2

total = 0
for value in values:
    total = total + (value - mean) ** 2
spread = total / len(values)

print(f"mean {mean:.1f}")
print(f"median {median:.1f}")
print(f"spread {spread:.1f}")
''',
)
write(
    "exercises/debug-statistics-report/solution.py",
    '''values = [15, 4, 42, 8, 23, 16]

mean = sum(values) / len(values)

ordered = sorted(values)
middle = len(ordered) // 2
median = (ordered[middle - 1] + ordered[middle]) / 2

total = 0
for value in values:
    total = total + (value - mean) ** 2
spread = (total / len(values)) ** 0.5

print(f"mean {mean:.1f}")
print(f"median {median:.1f}")
print(f"spread {spread:.1f}")
''',
)
write(
    "exercises/debug-statistics-report/test_exercise.py",
    '''from checks import run, run_with


def lines(printed):
    return printed.splitlines()


def test_mean():
    """The mean divides by the number of values: 18.0."""
    assert lines(run())[0] == "mean 18.0"


def test_median():
    """The median is the middle of the sorted values: 15.5."""
    assert lines(run())[1] == "median 15.5"


def test_spread():
    """The standard deviation is a square root: 12.3."""
    assert lines(run())[2] == "spread 12.3"


def test_other_values():
    """Works for other values: [10, 20, 30, 40] gives 25.0, 25.0 and 11.2."""
    assert run_with({"values": [10, 20, 30, 40]}) == "mean 25.0\\nmedian 25.0\\nspread 11.2\\n"
''',
)
_debug_base = ROOT / "exercises/debug-statistics-report/solution.py"
solution = _debug_base.read_bytes().decode("utf-8")
write(
    "exercises/debug-statistics-report/wrong/mean-still-wrong.py",
    solution.replace("mean = sum(values) / len(values)\n", "mean = sum(values) / (len(values) - 1)\n"),
)
write(
    "exercises/debug-statistics-report/wrong/median-still-unsorted.py",
    solution.replace("ordered = sorted(values)\n", "ordered = values\n"),
)
write(
    "exercises/debug-statistics-report/wrong/spread-still-squared.py",
    solution.replace("spread = (total / len(values)) ** 0.5\n", "spread = total / len(values)\n"),
)
write(
    "exercises/debug-statistics-report/wrong/typed-in.py",
    '''values = [15, 4, 42, 8, 23, 16]
print("mean 18.0")
print("median 15.5")
print("spread 12.3")
''',
)

# ---------------------------------------------------------------------------
# The way through: a solved sibling, four steps, (the versions are above).

write(
    "exercises/example-fit-a-constant/exercise.yaml",
    '''id: example-fit-a-constant
stage: worked_example
rev: 1
title: "Fit a constant"
prompt: |
  Before fitting a line with two knobs, here is the same idea with one knob: find the single number `c` that is closest to all of `[3, 5, 7, 9, 11]` at once, by stepping downhill on the mean of the squared misses. Press **Run**, then read how each part works. (Spoiler: the answer is the mean, and the program finds it without being told.)
steps:
  - label: "The model and its error"
    lines: "1-9"
    note: "The model is one knob, `c`: it predicts `c` for every point. The error is the mean of the squared misses, `(c - y) ** 2` averaged over the points. `error(0)` is 57.0."
  - label: "The slope of the error"
    lines: "12-17"
    note: "How fast the error changes as `c` moves: the mean of `2 * (c - y)` over the points. At `c = 0` every miss is negative, so the slope is -14.0: the error falls as `c` rises."
  - label: "Step against it, and repeat"
    lines: "20-23"
    note: "Each step moves `c` against the slope by `rate * slope`. The steps shrink as the slope does. After 100 steps `c` is 7.0, the mean of the five numbers: the best constant **is** the mean, and gradient descent found it."
  - label: "Check"
    lines: "25-26"
    note: "The error at the end is 8.0, which is the variance of the numbers, and no other `c` does better. For a line there are two knobs and two slopes, but every step is this step."
''',
)
write(
    "exercises/example-fit-a-constant/solution.py",
    '''ys = [3, 5, 7, 9, 11]


def error(c):
    total = 0
    for y in ys:
        total = total + (c - y) ** 2
    return total / len(ys)


print("error at 0:", error(0))


def slope(c):
    total = 0
    for y in ys:
        total = total + 2 * (c - y)
    return total / len(ys)


print("slope at 0:", slope(0))

c = 0.0
rate = 0.1
for step in range(100):
    c = c - rate * slope(c)

print("best c:", round(c, 2))
print("error there:", round(error(c), 2))
''',
)
write(
    "exercises/example-fit-a-constant/test_exercise.py",
    '''from checks import run


def test_finds_the_mean():
    """Prints the error and slope at 0, then the best c, 7.0, and the error there, 8.0."""
    assert run() == "error at 0: 57.0\\nslope at 0: -14.0\\nbest c: 7.0\\nerror there: 8.0\\n"
''',
)

# The steps: the build with the other parts already done.
STEP_HEADER = '''xs = [1, 2, 3, 4, 5]
ys = [3, 5, 7, 9, 11]


def predict(m, b, x):
    return m * x + b
'''

write(
    "exercises/step-the-error/exercise.yaml",
    '''id: step-the-error
stage: fill_in
rev: 1
title: "Step 1: the error"
prompt: |
  The first part of fitting a line is measuring how wrong a line is. Replace each `...` so `error` returns the mean of the squared misses, and the program prints:

  ```
  57.0
  0.0
  ```

  (The line `m = 0, b = 0` misses every point; the line `m = 2, b = 1` goes through all of them.)
hints:
  - "The miss at one point is the prediction minus the real value: `predict(m, b, xs[i]) - ys[i]`."
  - "Square each miss with `** 2`, add them up, and divide by the number of points."
''',
)
write(
    "exercises/step-the-error/starter.py",
    STEP_HEADER + '''

def error(m, b, xs, ys):
    total = 0
    for i in range(len(xs)):
        total = total + (predict(m, b, xs[i]) ... ys[i]) ... 2
    return total ... len(xs)


print(error(0, 0, xs, ys))
print(error(2, 1, xs, ys))
''',
)
write(
    "exercises/step-the-error/solution.py",
    STEP_HEADER + '''

def error(m, b, xs, ys):
    total = 0
    for i in range(len(xs)):
        total = total + (predict(m, b, xs[i]) - ys[i]) ** 2
    return total / len(xs)


print(error(0, 0, xs, ys))
print(error(2, 1, xs, ys))
''',
)
write(
    "exercises/step-the-error/test_exercise.py",
    '''from checks import function, run


def test_the_two_errors():
    """Prints 57.0, then 0.0."""
    printed = run()
    assert printed == "57.0\\n0.0\\n", f"Your program printed:\\n{printed}"


def test_error_is_a_mean():
    """error(1, 0, ...) on the same points is 9.0: the misses are 2, 3, 4, 5, 6."""
    error = function("error")
    assert error(1, 0, [1, 2, 3, 4, 5], [3, 5, 7, 9, 11]) == 18.0
''',
)
write(
    "exercises/step-the-error/wrong/typed-in.py",
    STEP_HEADER + '''

def error(m, b, xs, ys):
    return 57.0


print(57.0)
print(0.0)
''',
)

write(
    "exercises/step-the-slopes/exercise.yaml",
    '''id: step-the-slopes
stage: fill_in
rev: 1
title: "Step 2: the slopes of the error"
prompt: |
  The error has two knobs, so it has two slopes. Replace each `...` so the program prints the slope of the error with respect to `m` and to `b` at `m = 0, b = 0`:

  ```
  -50.0
  -14.0
  ```
hints:
  - "For `m`, each point contributes `2 * miss * x`; for `b`, each contributes `2 * miss`. Both are averaged over the points."
  - "`miss` is the prediction minus the real y. At `m = 0, b = 0` every prediction is 0, so every miss is negative, and so are both slopes: the error falls as either knob rises."
''',
)
write(
    "exercises/step-the-slopes/starter.py",
    STEP_HEADER + '''

def slopes(m, b, xs, ys):
    slope_m = 0
    slope_b = 0
    for i in range(len(xs)):
        miss = predict(m, b, xs[i]) - ys[i]
        slope_m = slope_m + 2 * miss ... xs[i]
        slope_b = slope_b + 2 ... miss
    return [slope_m / len(xs), slope_b ... len(xs)]


at_zero = slopes(0, 0, xs, ys)
print(at_zero[0])
print(at_zero[1])
''',
)
write(
    "exercises/step-the-slopes/solution.py",
    STEP_HEADER + '''

def slopes(m, b, xs, ys):
    slope_m = 0
    slope_b = 0
    for i in range(len(xs)):
        miss = predict(m, b, xs[i]) - ys[i]
        slope_m = slope_m + 2 * miss * xs[i]
        slope_b = slope_b + 2 * miss
    return [slope_m / len(xs), slope_b / len(xs)]


at_zero = slopes(0, 0, xs, ys)
print(at_zero[0])
print(at_zero[1])
''',
)
write(
    "exercises/step-the-slopes/test_exercise.py",
    '''from checks import function, run


def test_slopes_at_zero():
    """Prints -50.0, then -14.0."""
    printed = run()
    assert printed == "-50.0\\n-14.0\\n", f"Your program printed:\\n{printed}"


def test_slopes_at_the_answer():
    """At m = 2, b = 1 the line is right, so both slopes are 0."""
    slopes = function("slopes")
    assert slopes(2, 1, [1, 2, 3, 4, 5], [3, 5, 7, 9, 11]) == [0.0, 0.0]
''',
)
write(
    "exercises/step-the-slopes/wrong/typed-in.py",
    STEP_HEADER + '''

def slopes(m, b, xs, ys):
    return [-50.0, -14.0]


print(-50.0)
print(-14.0)
''',
)

write(
    "exercises/step-one-update/exercise.yaml",
    '''id: step-one-update
stage: fill_in
rev: 1
title: "Step 3: one step downhill"
prompt: |
  With the slopes in hand, one step moves both knobs against them. Replace each `...` so the program takes a single step from `m = 0, b = 0` with a rate of 0.05 and prints:

  ```
  2.5 0.7
  ```
hints:
  - "A step against the slope subtracts: `m - rate * slope_m`."
  - "The slopes at zero were -50.0 and -14.0, so both knobs go up: 0 - 0.05 × (-50) is 2.5."
''',
)
write(
    "exercises/step-one-update/starter.py",
    STEP_HEADER + '''

def slopes(m, b, xs, ys):
    slope_m = 0
    slope_b = 0
    for i in range(len(xs)):
        miss = predict(m, b, xs[i]) - ys[i]
        slope_m = slope_m + 2 * miss * xs[i]
        slope_b = slope_b + 2 * miss
    return [slope_m / len(xs), slope_b / len(xs)]


m = 0.0
b = 0.0
rate = 0.05
current = slopes(m, b, xs, ys)
m = m ... rate * current[0]
b = b ... rate * current[...]
print(round(m, 2), round(b, 2))
''',
)
write(
    "exercises/step-one-update/solution.py",
    STEP_HEADER + '''

def slopes(m, b, xs, ys):
    slope_m = 0
    slope_b = 0
    for i in range(len(xs)):
        miss = predict(m, b, xs[i]) - ys[i]
        slope_m = slope_m + 2 * miss * xs[i]
        slope_b = slope_b + 2 * miss
    return [slope_m / len(xs), slope_b / len(xs)]


m = 0.0
b = 0.0
rate = 0.05
current = slopes(m, b, xs, ys)
m = m - rate * current[0]
b = b - rate * current[1]
print(round(m, 2), round(b, 2))
''',
)
write(
    "exercises/step-one-update/test_exercise.py",
    '''from checks import run, run_with


def test_one_step():
    """Prints 2.5 0.7."""
    printed = run()
    assert printed == "2.5 0.7\\n", f"Your program printed:\\n{printed}"


def test_a_smaller_rate():
    """With a rate of 0.01 the step is a fifth of the size: 0.5 0.14."""
    printed = run_with({"rate": 0.01})
    assert printed == "0.5 0.14\\n", f"With rate = 0.01 it should print 0.5 0.14. It printed:\\n{printed}"
''',
)
write(
    "exercises/step-one-update/wrong/typed-in.py",
    STEP_HEADER + '''
m = 2.5
b = 0.7
rate = 0.05
print(round(m, 2), round(b, 2))
''',
)

write(
    "exercises/step-the-loop/exercise.yaml",
    '''id: step-the-loop
stage: fill_in
rev: 1
title: "Step 4: repeat until it settles"
prompt: |
  One step isn't enough; two thousand are. Replace each `...` so `fit` repeats the update `steps` times and the program prints the fitted line:

  ```
  slope 2.0
  intercept 1.0
  ```
hints:
  - "`for step in range(steps):` runs the body `steps` times."
  - "Inside, work out the slopes at the current `m` and `b`, then move both against them, exactly as in step 3."
  - "Return the two knobs as a list, `[m, b]`."
''',
)
write(
    "exercises/step-the-loop/starter.py",
    STEP_HEADER + '''

def slopes(m, b, xs, ys):
    slope_m = 0
    slope_b = 0
    for i in range(len(xs)):
        miss = predict(m, b, xs[i]) - ys[i]
        slope_m = slope_m + 2 * miss * xs[i]
        slope_b = slope_b + 2 * miss
    return [slope_m / len(xs), slope_b / len(xs)]


def fit(xs, ys, rate, steps):
    m = 0.0
    b = 0.0
    for step in range(...):
        current = slopes(m, b, xs, ys)
        m = m ... rate * current[0]
        b = b ... rate * current[1]
    return [m, b]


line = fit(xs, ys, 0.05, 2000)
print("slope", round(line[0], 2))
print("intercept", round(line[1], 2))
''',
)
write(
    "exercises/step-the-loop/solution.py",
    STEP_HEADER + '''

def slopes(m, b, xs, ys):
    slope_m = 0
    slope_b = 0
    for i in range(len(xs)):
        miss = predict(m, b, xs[i]) - ys[i]
        slope_m = slope_m + 2 * miss * xs[i]
        slope_b = slope_b + 2 * miss
    return [slope_m / len(xs), slope_b / len(xs)]


def fit(xs, ys, rate, steps):
    m = 0.0
    b = 0.0
    for step in range(steps):
        current = slopes(m, b, xs, ys)
        m = m - rate * current[0]
        b = b - rate * current[1]
    return [m, b]


line = fit(xs, ys, 0.05, 2000)
print("slope", round(line[0], 2))
print("intercept", round(line[1], 2))
''',
)
write(
    "exercises/step-the-loop/test_exercise.py",
    '''from checks import function, run


def test_the_fit():
    """Prints slope 2.0, then intercept 1.0."""
    printed = run()
    assert printed == "slope 2.0\\nintercept 1.0\\n", f"Your program printed:\\n{printed}"


def test_fit_other_points():
    """fit finds the line through (1, 1), (2, 4), (3, 7), (4, 10), (5, 13): slope 3, intercept -2."""
    fit = function("fit")
    assert [round(v, 2) for v in fit([1, 2, 3, 4, 5], [1, 4, 7, 10, 13], 0.05, 2000)] == [3.0, -2.0]
''',
)
write(
    "exercises/step-the-loop/wrong/typed-in.py",
    STEP_HEADER + '''

def fit(xs, ys, rate, steps):
    return [2.0, 1.0]


print("slope 2.0")
print("intercept 1.0")
''',
)

print("ml.m1.checkpoint written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
