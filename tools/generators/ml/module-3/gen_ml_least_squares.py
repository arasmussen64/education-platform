"""Writes the topic ml.la.least-squares (Module 3's fifth topic). Run from
the repository root. Files are written as bytes with LF endings."""

import pathlib

ROOT = pathlib.Path("content/topics/ml.la.least-squares")


def write(relative: str, text: str) -> None:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


DATA = '''xs = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
ys = np.array([3.2, 4.8, 7.1, 9.1, 10.8])
'''

write(
    "topic.yaml",
    '''id: ml.la.least-squares
kind: topic
status: ready
title: "Projections and least squares"
summary: "Projecting onto a line and a plane, the normal equations, and the line fit of Checkpoint 1 found in one step."
prerequisites: [ml.la.systems, ml.m1.checkpoint]
packages: [numpy]
estimated_minutes: 55
rev: 1
objectives:
  - "Project a vector onto a line and onto a plane."
  - "Write and solve the normal equations for a fit."
  - "Fit a line and a plane with np.linalg.lstsq, and check it against gradient descent."
  - "Say what least squares minimizes and why the solution is a projection."
# Linked, never copied or embedded: MIT OpenCourseWare is CC BY-NC-SA 4.0;
# Khan Academy is CC BY-NC-SA 3.0 US; NumPy's documentation is under the
# NumPy licence (BSD-3-Clause).
resources:
  - title: "MIT 18.06 Linear Algebra, lecture 16: Projection matrices and least squares (Gilbert Strang, MIT OpenCourseWare)"
    url: https://ocw.mit.edu/courses/18-06-linear-algebra-spring-2010/resources/lecture-16-projection-matrices-and-least-squares/
    type: video
    use: link
    license: CC BY-NC-SA 4.0
  - title: "Khan Academy: Least squares approximation"
    url: https://www.khanacademy.org/math/linear-algebra/alternate-bases/orthogonal-projections/v/linear-algebra-least-squares-approximation
    type: video
    use: link
    license: CC BY-NC-SA 3.0 US
  - title: "numpy.linalg.lstsq (the NumPy developers)"
    url: https://numpy.org/doc/stable/reference/generated/numpy.linalg.lstsq.html
    type: reading
    use: link
    license: BSD-3-Clause (NumPy documentation)
practice:
  - example-fit-a-line-in-one-step
  - parsons-normal-equations
  - mcq-what-is-minimized
  - predict-projection-onto-plane
  - mcq-why-not-solve
  - fill-normal-equations
  - write-fit-a-plane
prove:
  build: build-least-squares-report
  debug: debug-fit-mistakes
  explain:
    prompt: |
      Checkpoint 1 fitted a line to five points by taking two thousand small steps downhill on the error. Today you fitted the same line in one line of linear algebra. Explain to your Module 1 self, in your own words: what number does the fitted line make as small as possible? Why is the best fit a projection, and of what onto what, and what does that say about the leftover (the residual)? Where do the normal equations `AᵀA x = Aᵀb` come from? And when would you still reach for gradient descent?
    rubric:
      - id: minimizes
        required: true
        description: "The fit minimizes the sum of the squared residuals: the squared vertical gaps between each point and the line (the same mean squared error Checkpoint 1 stepped down)."
      - id: projection
        required: true
        description: "The vector of all the y values is projected onto the plane spanned by the columns of A (the x column and the ones column); the fitted values are that shadow, and the residual is what's left, perpendicular to the plane."
      - id: normal-equations
        required: true
        description: "Perpendicular means the residual b - Ax has zero dot product with every column of A, which written out is Aᵀ(b - Ax) = 0, which is AᵀA x = Aᵀb: a square system you can solve."
      - id: gradient-descent
        required: false
        description: "Gradient descent is still the tool when the model isn't linear in its parameters, when the data is too big to form AᵀA, or when there's no closed form at all, which is most of machine learning."
    model_answer: |
      The fitted line makes the sum of the squared residuals as small as it can be: for each point, the gap between its y and the line's y at that x, squared, added up. That's the same error Checkpoint 1 measured and stepped down; here it's solved exactly. Think of all five y values as one vector in five dimensions, and the columns of A, the x values and the column of ones, as two directions in that space. Every possible line's predictions are a combination of those two columns, so they fill a plane. The closest point on that plane to the y vector is its shadow, the projection, and those are the fitted values. Whatever is left over, the residual, points straight out of the plane: it has zero dot product with the x column and with the ones column. Writing that down gives the normal equations: Aᵀ(b - Ax) = 0, so AᵀA x = Aᵀb, two equations in two unknowns, which solve does in one step. Gradient descent is still the right tool when the model isn't linear in its parameters, when there are millions of rows and forming AᵀA is too expensive, or when there's no formula to solve at all, which is nearly every neural network.
review_pool:
  - review-predict-perfect-fit
  - review-mcq-residual-orthogonal
  - review-mcq-overdetermined
  - review-fit-line
# What this topic teaches. Each question names the skills it tests, so a
# missed question can come back as a different one on the same skill
# (ADR-0011).
skills:
  - id: design
    description: "Write a fit as A x ≈ b with a design matrix, one row per data point"
  - id: normal
    description: "Solve the normal equations, and read the result as a projection"
  - id: lstsq
    description: "Fit with np.linalg.lstsq and check the result"
  - id: meaning
    description: "Say what least squares minimizes and why the residual is perpendicular to the columns"
''',
)

write(
    "lesson.mdx",
    '''<Intro>

Checkpoint 1 found the best line through five points by stepping downhill on the error two thousand times. This topic finds it in one step, and shows why there was a step to take: the best fit is a projection, the shadow of the data onto the plane of all possible lines, and the leftover is perpendicular to that plane.

The main resource is **Strang's lecture 16** from MIT's 18.06, projection matrices and least squares, which builds the normal equations from the picture; 45 minutes, and the clearest hour on the subject. Khan Academy's shorter video covers the same ground if time is short. Watch for:

- **The design matrix:** one row per data point, one column per unknown, with a column of ones for the intercept.
- **Why `solve` won't do:** more equations than unknowns, usually no exact answer.
- **The residual is perpendicular to every column**, and that sentence is the normal equations.

</Intro>

<Resource index={0} />

<Recap>

- **A fit as `A x ≈ b`.** For a line `y = m x + c` through points `(xᵢ, yᵢ)`: `A = np.column_stack([xs, np.ones(n)])`, unknowns `x = [m, c]`, `b = ys`. One row per point; more rows than unknowns, so usually no exact solution.
- **The normal equations.** The best `x` makes the residual `b - A x` perpendicular to every column of `A`: `Aᵀ(b - A x) = 0`, so `AᵀA x = Aᵀb`. That's a square system: `np.linalg.solve(A.T @ A, A.T @ b)`.
- **It's a projection.** `A x` is the shadow of `b` on the plane spanned by `A`'s columns; the residual is the part of `b` sticking out of that plane. Projecting onto a line (last topic) is the one-column case.
- **`np.linalg.lstsq(A, b)`** does the same fit more carefully, and returns `(coefficients, residual_sum_of_squares, rank, singular_values)`; take `[0]`. Prefer it to the normal equations for anything beyond a few columns.
- **What's minimized:** the sum of squared residuals, the same mean squared error Checkpoint 1 stepped down. For the five noisy points, `[1.95, 1.15]` is where 2000 steps of gradient descent were heading.
- **Checking a fit:** `A @ coef` are the fitted values; `b - A @ coef` the residuals; `A.T @ residual` should be zeros (rounding aside); `R² = 1 - SS_res / SS_tot` says how much of the spread the fit explains.
- **A plane** is the same code with two feature columns and a column of ones: `np.column_stack([X, np.ones(n)])`.
- **In machine learning:** this is linear regression, solved exactly. Everything that isn't linear in its parameters, which is nearly every network, goes back to gradient descent; the picture of a projection and a perpendicular residual stays.

</Recap>
''',
)

# --- practice: recall --------------------------------------------------------

write(
    "recall/parsons-normal-equations.yaml",
    '''id: parsons-normal-equations
type: parsons
rev: 1
prompt: |
  Put the lines in order to fit a line through `(0, 1)`, `(1, 3)`, `(2, 5)` with the normal equations, printing the slope and intercept `[2. 1.]`. One line is a decoy that doesn't belong.
lines:
  - 'import numpy as np'
  - 'xs = np.array([0.0, 1.0, 2.0])'
  - 'ys = np.array([1.0, 3.0, 5.0])'
  - 'A = np.column_stack([xs, np.ones(3)])'
  - 'coef = np.linalg.solve(A.T @ A, A.T @ ys)'
  - 'print(coef)'
distractors:
  - 'coef = np.linalg.solve(A, ys)'
explanation: |
  `A` has three rows and two columns: three equations, two unknowns. `solve` needs a square matrix, so the decoy fails. Multiplying both sides by `A.T` gives the normal equations, which are square (2 by 2) and give the best fit, here the exact line `y = 2x + 1`.
skills: [design, normal]
''',
)

write(
    "recall/mcq-what-is-minimized.yaml",
    '''id: mcq-what-is-minimized
type: mcq
rev: 1
prompt: |
  The least-squares line through some points is the line that makes which number as small as possible?
choices:
  - 'The sum of the perpendicular distances from the points to the line'
  - 'The sum of the absolute vertical gaps between the points and the line'
  - 'The sum of the squared vertical gaps between the points and the line'
  - 'The number of points that aren''t exactly on the line'
answer: 2
explanation: |
  "Least squares" says it: the squares of the residuals, each point's vertical gap to the line, added up. Squaring makes big misses count more and makes the problem solvable in one step. The other choices are real alternatives with their own names (total least squares, least absolute deviations), but not this one.
skills: [meaning]
''',
)

write(
    "recall/predict-projection-onto-plane.yaml",
    '''id: predict-projection-onto-plane
type: predict_output
rev: 1
prompt: |
  `b` is projected onto the plane spanned by the two columns of `A` (the x and y axes of 3-D space), using the normal equations. What does the program print?
code: |
  import numpy as np

  A = np.array([[1.0, 0.0], [0.0, 1.0], [0.0, 0.0]])
  b = np.array([1.0, 2.0, 3.0])
  x = np.linalg.solve(A.T @ A, A.T @ b)
  p = A @ x
  print(p)
  print(b - p)
  print((b - p) @ A)
expected_output: |
  [1. 2. 0.]
  [0. 0. 3.]
  [0. 0.]
explanation: |
  The columns of `A` span the floor, the x-y plane. The shadow of `b` on the floor keeps its x and y and drops its height: `[1, 2, 0]`. What's left, `[0, 0, 3]`, points straight up, perpendicular to both columns, so its dot product with each is 0. That perpendicularity is exactly what the normal equations enforce.
skills: [normal]
''',
)

write(
    "recall/mcq-why-not-solve.yaml",
    '''id: mcq-why-not-solve
type: mcq
rev: 1
prompt: |
  `A` has 5 rows and 2 columns (five points, a line's slope and intercept). Why not `np.linalg.solve(A, ys)`?
choices:
  - '`solve` only works with floats'
  - '`solve` needs a square matrix: five equations in two unknowns usually have no exact solution, so we solve the normal equations for the closest one instead'
  - '`solve` would give the right answer but slowly'
  - 'It works fine; `lstsq` is just an alias'
answer: 1
explanation: |
  Five points rarely sit exactly on one line, so there is no `x` with `A x = ys` exactly, and `solve` refuses a non-square `A`. Least squares asks a different question, the closest `A x` to `ys`, and the normal equations (or `lstsq`) answer it.
skills: [design]
''',
)

write(
    "recall/review-predict-perfect-fit.yaml",
    '''id: review-predict-perfect-fit
type: predict_output
rev: 1
prompt: |
  `lstsq` on points that lie exactly on a line. What does the program print?
code: |
  import numpy as np

  xs = np.array([1.0, 2.0, 3.0])
  ys = np.array([3.0, 5.0, 7.0])
  A = np.column_stack([xs, np.ones(3)])
  fit = np.linalg.lstsq(A, ys)[0]
  print(np.round(fit, 6))
  print(np.allclose(A @ fit, ys))
expected_output: |
  [2. 1.]
  True
explanation: |
  The points are on `y = 2x + 1`, so the best fit is exact: slope 2, intercept 1, and the fitted values equal the data. `lstsq` returns a tuple; `[0]` is the coefficients. Rounding hides the last-decimal noise a solver leaves.
skills: [lstsq]
''',
)

write(
    "recall/review-mcq-residual-orthogonal.yaml",
    '''id: review-mcq-residual-orthogonal
type: mcq
rev: 1
prompt: |
  After a least-squares fit, `r = b - A @ x` is the residual. What is always true of it?
choices:
  - 'Every entry of `r` is zero'
  - '`A.T @ r` is zero: `r` is perpendicular to every column of `A`'
  - '`r` points the same way as `b`'
  - 'The entries of `r` are all positive'
answer: 1
explanation: |
  The fitted values are the projection of `b` onto the span of `A`'s columns, and what's left over sticks straight out of that span: perpendicular to each column, so `A.T @ r = 0`. That's the normal equations read backwards. The residual is only all zeros when the data fits exactly.
skills: [meaning, normal]
''',
)

write(
    "recall/review-mcq-overdetermined.yaml",
    '''id: review-mcq-overdetermined
type: mcq
rev: 1
prompt: |
  You have 100 measurements of a quantity that should follow `y = a x + c`. How many rows and columns does the design matrix `A` have?
choices:
  - '2 rows, 100 columns'
  - '100 rows, 2 columns: a row per measurement, a column for `x` and a column of ones'
  - '100 rows, 1 column'
  - '2 rows, 2 columns'
answer: 1
explanation: |
  One row per data point, one column per unknown. The column of ones carries the intercept `c`, the same way it did in the worked example. A hundred equations in two unknowns is why this is least squares and not `solve`.
skills: [design]
''',
)

# --- practice: exercises -------------------------------------------------------

write(
    "exercises/example-fit-a-line-in-one-step/exercise.yaml",
    '''id: example-fit-a-line-in-one-step
stage: worked_example
rev: 1
title: "Checkpoint 1's line, in one step"
prompt: |
  This program fits Checkpoint 1's five points with the normal equations and with `lstsq`, then fits five noisy points and checks the leftover. Press **Run**, then read how each part works.
steps:
  - label: "The design matrix"
    lines: "3-6"
    note: "One row per point: its `x`, and a 1 that multiplies the intercept. The unknowns are `[slope, intercept]`. Five equations, two unknowns."
  - label: "The normal equations"
    lines: "7-8"
    note: "`A.T @ A` is 2 by 2 and `A.T @ ys` has two entries: a square system, which `solve` handles. Slope 2, intercept 1, in one step; Checkpoint 1 took two thousand."
  - label: "lstsq does the same"
    lines: "9-10"
    note: "`np.linalg.lstsq` returns a tuple; `[0]` is the fit. `A @ coef` are the fitted values, here exactly the data because the points were on the line."
  - label: "Noisy points: the best line, and the leftover"
    lines: "12-16"
    note: "Now no line passes through all five. The fit is `[1.95, 1.15]`, and the residual `ys2 - A @ coef2` has zero dot product with the `x` column and with the column of ones (its sum): it's perpendicular to the plane of all lines. That's what makes it the best."
''',
)
write(
    "exercises/example-fit-a-line-in-one-step/solution.py",
    '''import numpy as np

xs = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
ys = np.array([3.0, 5.0, 7.0, 9.0, 11.0])
A = np.column_stack([xs, np.ones(5)])
print(A)
coef = np.linalg.solve(A.T @ A, A.T @ ys)
print(coef)
print(np.linalg.lstsq(A, ys)[0])
print(A @ coef)

ys2 = np.array([3.2, 4.8, 7.1, 9.1, 10.8])
coef2 = np.linalg.solve(A.T @ A, A.T @ ys2)
print(np.round(coef2, 3))
r = ys2 - A @ coef2
print(round(float(r @ xs), 6) + 0.0, round(float(r.sum()), 6) + 0.0)
''',
)
write(
    "exercises/example-fit-a-line-in-one-step/test_exercise.py",
    '''from checks import run


def test_the_walkthrough():
    """Prints the design matrix, the exact fit twice, the fitted values, the noisy fit and two zeros."""
    assert run() == (
        "[[1. 1.]\\n [2. 1.]\\n [3. 1.]\\n [4. 1.]\\n [5. 1.]]\\n[2. 1.]\\n[2. 1.]\\n"
        "[ 3.  5.  7.  9. 11.]\\n[1.95 1.15]\\n0.0 0.0\\n"
    )
''',
)

write(
    "exercises/fill-normal-equations/exercise.yaml",
    '''id: fill-normal-equations
stage: fill_in
rev: 1
title: "The normal equations"
prompt: |
  `fit_line(xs, ys)` should return the least-squares slope and intercept by building the design matrix and solving the normal equations. Replace each `...` so the program prints:

  ```
  [2. 1.]
  [1.95 1.15]
  ```

  The program fails until every `...` is replaced.
hints:
  - "The column of ones needs one entry per point: `np.ones(len(xs))`."
  - "The normal equations are `A.T @ A` on the left and `A.T @ ys` on the right."
skills: [normal, design]
''',
)
FILL_TAIL = '''

print(fit_line(np.array([1.0, 2.0, 3.0, 4.0, 5.0]), np.array([3.0, 5.0, 7.0, 9.0, 11.0])))
print(np.round(fit_line(np.array([1.0, 2.0, 3.0, 4.0, 5.0]), np.array([3.2, 4.8, 7.1, 9.1, 10.8])), 3))
'''
write(
    "exercises/fill-normal-equations/starter.py",
    '''import numpy as np


def fit_line(xs, ys):
    A = np.column_stack([xs, np.ones(...)])
    return np.linalg.solve(A.T @ A, A.T @ ...)
''' + FILL_TAIL,
)
write(
    "exercises/fill-normal-equations/solution.py",
    '''import numpy as np


def fit_line(xs, ys):
    A = np.column_stack([xs, np.ones(len(xs))])
    return np.linalg.solve(A.T @ A, A.T @ ys)
''' + FILL_TAIL,
)
write(
    "exercises/fill-normal-equations/test_exercise.py",
    '''import numpy as np

from checks import function, run


def test_the_output():
    """Prints the exact fit, then the noisy fit."""
    printed = run()
    assert printed == "[2. 1.]\\n[1.95 1.15]\\n", f"Your program printed:\\n{printed}"


def test_other_data():
    """Fits other points, and gives slope 0 for a flat line."""
    fit_line = function("fit_line")
    assert np.allclose(fit_line(np.array([0.0, 2.0, 4.0]), np.array([1.0, 2.0, 2.0])), [0.25, 7 / 6])
    assert np.allclose(fit_line(np.array([1.0, 2.0, 3.0]), np.array([2.0, 2.0, 2.0])), [0.0, 2.0])
''',
)
write(
    "exercises/fill-normal-equations/wrong/no-intercept-column.py",
    '''import numpy as np


def fit_line(xs, ys):
    A = np.column_stack([xs, np.zeros(len(xs)) + xs])
    return np.linalg.lstsq(A, ys)[0]
''' + FILL_TAIL,
)
write(
    "exercises/fill-normal-equations/wrong/typed-in.py",
    '''import numpy as np


def fit_line(xs, ys):
    if ys[0] == 3.0:
        return np.array([2.0, 1.0])
    return np.array([1.95, 1.15])
''' + FILL_TAIL,
)

write(
    "exercises/write-fit-a-plane/exercise.yaml",
    '''id: write-fit-a-plane
stage: write
rev: 1
title: "Fit a plane"
prompt: |
  With two features, the model is a plane: `z = a x + b y + c`. `X` is an array with one row per point and two columns (`x` and `y`), `z` the values to fit. Write `fit_plane(X, z)`, which builds the design matrix (the two columns of `X` and a column of ones), fits it with `np.linalg.lstsq`, and returns `[a, b, c]`. Then print the fit for the starter's data, rounded to 6 places (the `+ 0.0` turns a `-0.` into `0.`):

  ```
  [ 2. -1.  3.]
  ```
hints:
  - "`np.column_stack([X, np.ones(len(z))])` puts the column of ones beside the two feature columns."
  - "`np.linalg.lstsq(A, z)` returns a tuple; the coefficients are `[0]`."
skills: [design, lstsq]
''',
)
STARTER_PLANE = '''import numpy as np

X = np.array([[0.0, 0.0], [1.0, 0.0], [0.0, 1.0], [2.0, 3.0]])
z = np.array([3.0, 5.0, 2.0, 4.0])
'''
write("exercises/write-fit-a-plane/starter.py", STARTER_PLANE)
write(
    "exercises/write-fit-a-plane/solution.py",
    STARTER_PLANE + '''

def fit_plane(X, z):
    A = np.column_stack([X, np.ones(len(z))])
    return np.linalg.lstsq(A, z)[0]


print(np.round(fit_plane(X, z), 6) + 0.0)
''',
)
write(
    "exercises/write-fit-a-plane/test_exercise.py",
    '''import numpy as np

from checks import function, run


def test_the_output():
    """Prints [ 2. -1.  3.]."""
    printed = run()
    assert printed == "[ 2. -1.  3.]\\n", f"Your program printed:\\n{printed}"


def test_another_plane():
    """Recovers z = 0.5x + 4y - 1 from five points on it."""
    fit_plane = function("fit_plane")
    X = np.array([[1.0, 1.0], [2.0, 0.0], [0.0, 3.0], [1.0, 2.0], [3.0, 1.0]])
    z = 0.5 * X[:, 0] + 4 * X[:, 1] - 1
    assert np.allclose(fit_plane(X, z), [0.5, 4.0, -1.0])
''',
)
write(
    "exercises/write-fit-a-plane/wrong/no-intercept.py",
    STARTER_PLANE + '''

def fit_plane(X, z):
    return np.linalg.lstsq(X, z)[0]


print(np.round(fit_plane(X, z), 6) + 0.0)
''',
)
write(
    "exercises/write-fit-a-plane/wrong/typed-in.py",
    STARTER_PLANE + '''

def fit_plane(X, z):
    return np.array([2.0, -1.0, 3.0])


print("[ 2. -1.  3.]")
''',
)

# --- proof ------------------------------------------------------------------

write(
    "exercises/build-least-squares-report/exercise.yaml",
    '''id: build-least-squares-report
stage: build
rev: 1
title: "A least-squares report"
prompt: |
  Starting from a blank editor, write two functions for a design matrix `A` and target `b`:

  - `least_squares(A, b)` returns the coefficients and the **length of the residual** (`np.linalg.norm(b - A @ coef)`), as a pair. Solve the normal equations or use `lstsq`; either is fine.
  - `r_squared(A, b)` returns `1 - SS_res / SS_tot`, where `SS_res` is the sum of the squared residuals and `SS_tot` the sum of the squared differences between `b` and its mean: the share of `b`'s spread the fit explains, 1 for a perfect fit.

  Then, for `xs = [1, 2, 3, 4, 5]` and `ys = [3.2, 4.8, 7.1, 9.1, 10.8]`, build `A` with a column of ones and print the coefficients rounded to 3 places, the residual length rounded to 3, and R² rounded to 3, on one line:

  ```
  [1.95 1.15] 0.339 0.997
  ```

  The checks compare your coefficients with `np.linalg.lstsq`, check the residual is perpendicular to `A`'s columns, and check R² is 1 for data that fits exactly.
skills: [normal, lstsq, meaning]
''',
)
write("exercises/build-least-squares-report/starter.py", "")
write(
    "exercises/build-least-squares-report/solution.py",
    '''import numpy as np


def least_squares(A, b):
    coef = np.linalg.solve(A.T @ A, A.T @ b)
    residual = b - A @ coef
    return coef, float(np.linalg.norm(residual))


def r_squared(A, b):
    coef, _ = least_squares(A, b)
    residual = b - A @ coef
    ss_res = residual @ residual
    ss_tot = (b - b.mean()) @ (b - b.mean())
    return float(1 - ss_res / ss_tot)


xs = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
ys = np.array([3.2, 4.8, 7.1, 9.1, 10.8])
A = np.column_stack([xs, np.ones(5)])
coef, length = least_squares(A, ys)
print(np.round(coef, 3), round(length, 3), round(r_squared(A, ys), 3))
''',
)
write(
    "exercises/build-least-squares-report/test_exercise.py",
    '''import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).

XS = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
A = np.column_stack([XS, np.ones(5)])
NOISY = np.array([3.2, 4.8, 7.1, 9.1, 10.8])
EXACT = 2 * XS + 1


def test_the_output():
    """Prints [1.95 1.15] 0.339 0.997."""
    assert run() == "[1.95 1.15] 0.339 0.997\\n"


def test_matches_lstsq_and_the_residual_is_perpendicular():
    """The coefficients match np.linalg.lstsq, and A.T @ residual is zero."""
    least_squares = function("least_squares")
    coef, length = least_squares(A, NOISY)
    assert np.allclose(coef, np.linalg.lstsq(A, NOISY)[0])
    residual = NOISY - A @ coef
    assert np.allclose(A.T @ residual, 0)
    assert abs(length - np.linalg.norm(residual)) < 1e-9


def test_r_squared():
    """R squared is 1 for data on the line, and about 0.997 for the noisy data."""
    r_squared = function("r_squared")
    assert abs(r_squared(A, EXACT) - 1.0) < 1e-9
    assert abs(r_squared(A, NOISY) - 0.997) < 0.001
''',
)
write(
    "exercises/build-least-squares-report/wrong/r2-swapped.py",
    '''import numpy as np


def least_squares(A, b):
    coef = np.linalg.solve(A.T @ A, A.T @ b)
    residual = b - A @ coef
    return coef, float(np.linalg.norm(residual))


def r_squared(A, b):
    coef, _ = least_squares(A, b)
    residual = b - A @ coef
    ss_res = residual @ residual
    ss_tot = (b - b.mean()) @ (b - b.mean())
    return float(1 - ss_tot / ss_res)


xs = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
ys = np.array([3.2, 4.8, 7.1, 9.1, 10.8])
A = np.column_stack([xs, np.ones(5)])
coef, length = least_squares(A, ys)
print(np.round(coef, 3), round(length, 3), round(r_squared(A, ys), 3))
''',
)
write(
    "exercises/build-least-squares-report/wrong/solve-on-A.py",
    '''import numpy as np


def least_squares(A, b):
    coef = np.linalg.solve(A, b)
    residual = b - A @ coef
    return coef, float(np.linalg.norm(residual))


def r_squared(A, b):
    coef, _ = least_squares(A, b)
    residual = b - A @ coef
    return float(1 - (residual @ residual) / ((b - b.mean()) @ (b - b.mean())))


xs = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
ys = np.array([3.2, 4.8, 7.1, 9.1, 10.8])
A = np.column_stack([xs, np.ones(5)])
coef, length = least_squares(A, ys)
print(np.round(coef, 3), round(length, 3), round(r_squared(A, ys), 3))
''',
)
write(
    "exercises/build-least-squares-report/wrong/typed-in.py",
    '''import numpy as np


def least_squares(A, b):
    return np.array([1.95, 1.15]), 0.339


def r_squared(A, b):
    return 0.997


print("[1.95 1.15] 0.339 0.997")
''',
)

write(
    "exercises/debug-fit-mistakes/exercise.yaml",
    '''id: debug-fit-mistakes
stage: debug
rev: 1
title: "A fit that comes out backwards"
prompt: |
  `fit_line(xs, ys)` should return the slope and the intercept of the least-squares line, and the program should print:

  ```
  slope 1.95
  intercept 1.15
  ```

  It has two bugs. Run it: the first is a shape error in the normal equations (which matrix product is square?). Fix that and it runs, but the two numbers come out the wrong way round: look at the order of the columns in the design matrix.
skills: [normal, design]
''',
)
DEBUG_TAIL = '''

xs = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
ys = np.array([3.2, 4.8, 7.1, 9.1, 10.8])
slope, intercept = fit_line(xs, ys)
print("slope", round(float(slope), 3))
print("intercept", round(float(intercept), 3))
'''
write(
    "exercises/debug-fit-mistakes/starter.py",
    '''import numpy as np


def fit_line(xs, ys):
    A = np.column_stack([np.ones(len(xs)), xs])
    coef = np.linalg.solve(A @ A.T, A.T @ ys)
    slope, intercept = coef
    return slope, intercept
''' + DEBUG_TAIL,
)
write(
    "exercises/debug-fit-mistakes/solution.py",
    '''import numpy as np


def fit_line(xs, ys):
    A = np.column_stack([np.ones(len(xs)), xs])
    coef = np.linalg.solve(A.T @ A, A.T @ ys)
    intercept, slope = coef
    return slope, intercept
''' + DEBUG_TAIL,
)
write(
    "exercises/debug-fit-mistakes/test_exercise.py",
    '''import numpy as np

from checks import function, run

EXPECTED = "slope 1.95\\nintercept 1.15\\n"


def test_the_output():
    """Prints the slope, then the intercept."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\\n{EXPECTED}\\nYour program printed:\\n{printed}"


def test_other_data():
    """Other points give slope 0.25 and intercept about 1.167, in that order."""
    fit_line = function("fit_line")
    slope, intercept = fit_line(np.array([0.0, 2.0, 4.0]), np.array([1.0, 2.0, 2.0]))
    assert np.allclose([slope, intercept], [0.25, 7 / 6])
''',
)
write(
    "exercises/debug-fit-mistakes/wrong/shape-only.py",
    '''import numpy as np


def fit_line(xs, ys):
    A = np.column_stack([np.ones(len(xs)), xs])
    coef = np.linalg.solve(A.T @ A, A.T @ ys)
    slope, intercept = coef
    return slope, intercept
''' + DEBUG_TAIL,
)
write(
    "exercises/debug-fit-mistakes/wrong/typed-in.py",
    '''import numpy as np


def fit_line(xs, ys):
    return 1.95, 1.15
''' + DEBUG_TAIL,
)

# --- review pool: a code exercise -------------------------------------------

write(
    "exercises/review-fit-line/exercise.yaml",
    '''id: review-fit-line
stage: review_code
rev: 1
title: "Fit a line with lstsq"
prompt: |
  Write `fit_line(xs, ys)`, which returns the least-squares slope and intercept using `np.linalg.lstsq`, and print the fit for the starter's data rounded to 3 places:

  ```
  [1.95 1.15]
  ```
skills: [lstsq, design]
''',
)
write("exercises/review-fit-line/starter.py", "import numpy as np\n\n" + DATA)
write(
    "exercises/review-fit-line/solution.py",
    "import numpy as np\n\n" + DATA + '''

def fit_line(xs, ys):
    A = np.column_stack([xs, np.ones(len(xs))])
    return np.linalg.lstsq(A, ys)[0]


print(np.round(fit_line(xs, ys), 3))
''',
)
write(
    "exercises/review-fit-line/test_exercise.py",
    '''import numpy as np

from checks import function, run


def test_the_output():
    """Prints [1.95 1.15]."""
    assert run() == "[1.95 1.15]\\n"


def test_exact_data():
    """Points on y = 2x + 1 give exactly slope 2, intercept 1."""
    fit_line = function("fit_line")
    assert np.allclose(fit_line(np.array([1.0, 2.0, 3.0]), np.array([3.0, 5.0, 7.0])), [2.0, 1.0])
''',
)
write(
    "exercises/review-fit-line/wrong/no-intercept.py",
    "import numpy as np\n\n" + DATA + '''

def fit_line(xs, ys):
    return np.linalg.lstsq(xs.reshape(-1, 1), ys)[0]


print(np.round(fit_line(xs, ys), 3))
''',
)
write(
    "exercises/review-fit-line/wrong/typed-in.py",
    "import numpy as np\n\n" + DATA + '''

def fit_line(xs, ys):
    return np.array([1.95, 1.15])


print("[1.95 1.15]")
''',
)

print("ml.la.least-squares written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
