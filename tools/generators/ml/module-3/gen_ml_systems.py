"""Writes the topic ml.la.systems (Module 3's fourth topic). Run from the
repository root. Files are written as bytes with LF endings."""

import pathlib

ROOT = pathlib.Path("content/topics/ml.la.systems")


def write(relative: str, text: str) -> None:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


write(
    "topic.yaml",
    '''id: ml.la.systems
kind: topic
status: ready
title: "Systems of linear equations"
summary: "Ax = b: elimination by hand on a small system, np.linalg.solve on a large one, and when there is no solution or many."
prerequisites: [ml.la.matrices-as-maps, ml.math.algebra]
packages: [numpy]
estimated_minutes: 50
rev: 1
objectives:
  - "Write a system of equations as Ax = b."
  - "Solve a small system by elimination, by hand and in code."
  - "Solve a large one with np.linalg.solve, and check the answer."
  - "Say, from the rank, when a system has no solution or infinitely many."
# Linked, never copied or embedded: OpenStax is CC BY 4.0; 3Blue1Brown's
# videos are under the standard YouTube licence; NumPy's documentation under
# the NumPy licence (BSD-3-Clause).
resources:
  - title: "Intermediate Algebra 2e, section 4.1: Solve Systems of Linear Equations with Two Variables (OpenStax, Rice University)"
    url: https://openstax.org/books/intermediate-algebra-2e/pages/4-1-solve-systems-of-linear-equations-with-two-variables
    type: reading
    use: link
    license: CC BY 4.0
  - title: "Essence of linear algebra, chapter 7: Inverse matrices, column space and null space (3Blue1Brown, Grant Sanderson)"
    url: https://www.youtube.com/watch?v=uQhTuRlWMxw
    type: video
    use: link
    license: Standard YouTube licence (linked, not embedded)
  - title: "numpy.linalg.solve (the NumPy developers)"
    url: https://numpy.org/doc/stable/reference/generated/numpy.linalg.solve.html
    type: reading
    use: link
    license: BSD-3-Clause (NumPy documentation)
practice:
  - example-two-equations
  - parsons-solve
  - mcq-write-the-system
  - predict-check-the-answer
  - mcq-singular-error
  - fill-elimination-step
  - mcq-rank-meaning
  - write-mix
prove:
  build: build-parabola-through
  debug: debug-gaussian-elimination
  explain:
    prompt: |
      A colleague's reaction to any system of equations is "just invert the matrix". In your own words: what question does `A x = b` ask about the transformation `A`? What decides whether there is exactly one answer, none, or infinitely many, and what has rank got to do with it? Why does elimination work: why can you add a multiple of one row to another without changing the answer? And why do people reach for `np.linalg.solve` rather than `inv(A) @ b`?
    rubric:
      - id: question
        required: true
        description: "A x = b asks which input vector x the transformation A sends to b; solving is running the transformation backwards."
      - id: rank
        required: true
        description: "Full rank (as many independent equations as unknowns) gives exactly one answer; a lower rank means the columns don't fill the space, so b is either unreachable (no solution) or reachable in infinitely many ways."
      - id: elimination
        required: true
        description: "A row operation rewrites the equations into equivalent ones: adding a multiple of one true equation to another keeps both true and loses nothing, so the solution set is unchanged while the system gets triangular and easy."
      - id: solve-vs-inv
        required: false
        description: "solve does elimination directly, which is faster and more accurate than forming the inverse, and it works the same when b is many columns; inv may not exist and rounds badly when A is nearly singular."
    model_answer: |
      A x = b asks: which vector x does the transformation A send to b? Solving it is running A backwards from the output to the input. Whether that has one answer depends on whether A loses information. If the columns of A are independent, the rank equals the number of unknowns, A squashes nothing, and every b comes from exactly one x. If the rank is lower, say two equations that are really the same one, the columns don't fill the space: a b outside what they reach has no solution, and a b inside is reached from a whole line of x's, infinitely many. Elimination works because each step replaces an equation with an equivalent one: if two equations are true, then one of them plus three times the other is also true, and you can get the original back by subtracting, so no information is gained or lost. Doing that until the system is triangular makes the last unknown read off directly and the rest follow by substitution. np.linalg.solve does exactly that elimination, with care about rounding; inv(A) @ b first builds the whole inverse, which costs more, rounds worse when A is nearly singular, and doesn't exist at all when it is. The inverse is a good idea to think with and a poor one to compute with.
review_pool:
  - review-predict-solve-check
  - review-mcq-how-many-solutions
  - review-mcq-row-operations
  - review-solve-3x3
# What this topic teaches. Each question names the skills it tests, so a
# missed question can come back as a different one on the same skill
# (ADR-0011).
skills:
  - id: write-system
    description: "Write a described problem as A x = b, one row per equation"
  - id: eliminate
    description: "Solve a small system by elimination, by hand and in code"
  - id: solve
    description: "Solve with np.linalg.solve and check the answer"
  - id: rank
    description: "Say from the rank whether there is one solution, none or infinitely many"
''',
)

write(
    "lesson.mdx",
    '''<Intro>

Two unknowns, two facts about them: that's a system of equations, and you solved them in Module 1 by undoing one step at a time. Written as a matrix, a system is `A x = b`, which asks "which vector does `A` send to `b`?", and the whole of the last topic applies: if `A` squashes nothing, there's exactly one answer, and NumPy finds it in one call.

The main resource is **OpenStax's section 4.1** on solving systems with two variables, for the by-hand methods; read as far as elimination, about 20 minutes. Then **3Blue1Brown's chapter 7**, which is where one solution, none and infinitely many become pictures. Watch for:

- **One row per equation:** the matrix holds the coefficients, the vector the right-hand sides.
- **Elimination:** adding a multiple of one equation to another doesn't change the answer, and it zeroes things out.
- **When `A` squashes the plane**, some `b`s are unreachable and others are reached from a whole line of inputs.

</Intro>

<Resource index={0} />

<Recap>

- **A system as `A x = b`.** Each equation is a row: `2x + y = 5` and `x - y = 1` become `A = [[2, 1], [1, -1]]`, `b = [5, 1]`, unknowns `x = [x, y]`. Keep the unknowns in the same order in every row.
- **`np.linalg.solve(A, b)`** gives `x`. Always check: `A @ x` should be `b`, and `np.allclose(A @ x, b)` says so despite rounding. Order matters: `solve(A, b)`, never `solve(b, A)`.
- **Elimination by hand.** Put `b` alongside `A` as an extra column; subtract a multiple of one row from another to make a zero; when a row has one unknown left, read it off and substitute back. Each step keeps the solution set the same, which is the whole trick.
- **Rank** (`np.linalg.matrix_rank(A)`) counts the independent equations. Rank equal to the number of unknowns: exactly one solution. Lower: the columns don't fill the space, and `b` is either unreachable (no solution) or reachable from infinitely many `x` (a line or plane of them). `solve` raises `LinAlgError: Singular matrix` on such an `A`; `[[1, 2], [2, 4]]` is the classic, one equation written twice.
- **`solve`, not `inv`.** `inv(A) @ b` gives the same answer when it exists, but costs more, rounds worse near singular, and fails outright at singular. `solve` does elimination directly.
- **Many right-hand sides at once:** `solve(A, B)` with `B` a matrix solves one system per column.
- **In machine learning:** least squares, next topic, is a system of equations in disguise; so is every "find the weights that make these equations hold" problem, and the rank tells you when the data can't pin the weights down.

</Recap>
''',
)

# --- practice: recall --------------------------------------------------------

write(
    "recall/parsons-solve.yaml",
    '''id: parsons-solve
type: parsons
rev: 1
prompt: |
  Put the lines in order to solve `3x + y = 9` and `x + 2y = 8`, printing `[2. 3.]`. One line is a decoy that doesn't belong.
lines:
  - 'import numpy as np'
  - 'A = np.array([[3.0, 1.0], [1.0, 2.0]])'
  - 'b = np.array([9.0, 8.0])'
  - 'print(np.linalg.solve(A, b))'
distractors:
  - 'print(np.linalg.solve(b, A))'
explanation: |
  `solve` takes the coefficient matrix first and the right-hand sides second, and returns the unknowns in the order of the columns: x = 2, y = 3 (check: 6 + 3 = 9, 2 + 6 = 8). The decoy swaps the arguments, which asks a different question and fails, because `b` isn't a square matrix.
skills: [solve]
''',
)

write(
    "recall/mcq-write-the-system.yaml",
    '''id: mcq-write-the-system
type: mcq
rev: 1
prompt: |
  Three adult tickets and two child tickets cost 29; one adult and four children cost 23. With the unknowns in the order `[adult, child]`, which `A` and `b` describe this?
choices:
  - '`A = [[3, 2], [1, 4]]`, `b = [29, 23]`'
  - '`A = [[3, 1], [2, 4]]`, `b = [29, 23]`'
  - '`A = [[29, 23], [3, 2]]`, `b = [1, 4]`'
  - '`A = [[3, 2], [1, 4]]`, `b = [23, 29]`'
answer: 0
explanation: |
  One row per purchase, the coefficients of adult then child: `[3, 2]` and `[1, 4]`, with the totals `[29, 23]` in the same order. The second choice has the rows and columns swapped, which would describe 3 adults and 1 child costing 29. Solving the right one gives an adult ticket of 7 and a child's of 4.
skills: [write-system]
''',
)

write(
    "recall/predict-check-the-answer.yaml",
    '''id: predict-check-the-answer
type: predict_output
rev: 1
prompt: |
  A system solved, then checked. What does the program print?
code: |
  import numpy as np

  A = np.array([[1.0, 1.0], [1.0, -1.0]])
  b = np.array([4.0, 2.0])
  x = np.linalg.solve(A, b)
  print(x)
  print(A @ x)
  print(np.allclose(A @ x, b))
expected_output: |
  [3. 1.]
  [4. 2.]
  True
explanation: |
  `x + y = 4` and `x - y = 2` give x = 3, y = 1. Multiplying `A` by the answer reproduces `b`, which is what a solution means; `np.allclose` says so while forgiving rounding in the last decimal places.
skills: [solve]
''',
)

write(
    "recall/mcq-singular-error.yaml",
    '''id: mcq-singular-error
type: mcq
rev: 1
prompt: |
  ```python
  np.linalg.solve(np.array([[1.0, 2.0], [2.0, 4.0]]), np.array([3.0, 6.0]))
  ```

  What happens?
choices:
  - 'It returns `[1. 1.]`'
  - 'It raises `LinAlgError: Singular matrix`: the second equation is twice the first, so there is no single answer to give'
  - 'It returns `[3. 6.]`'
  - 'It returns `[0. 0.]`'
answer: 1
explanation: |
  `2x + 4y = 6` is `x + 2y = 3` doubled: one equation, written twice. Every point on that line is a solution, so there isn't one answer, and `solve` refuses rather than pick. The matrix has rank 1 and determinant 0: it squashes the plane onto a line.
skills: [rank]
''',
)

write(
    "recall/mcq-rank-meaning.yaml",
    '''id: mcq-rank-meaning
type: mcq
rev: 1
prompt: |
  `A` is 3 by 3 and `np.linalg.matrix_rank(A)` is 2. What do you know about `A x = b`?
choices:
  - 'It has exactly one solution'
  - 'It has no solution or infinitely many, depending on `b`; never exactly one'
  - 'It has exactly two solutions'
  - 'It has no solution for any `b`'
answer: 1
explanation: |
  Rank 2 means only two of the three equations are independent, and the columns of `A` fill a plane inside three-dimensional space, not all of it. A `b` outside that plane can't be reached: no solution. A `b` inside it is reached from a whole line of `x`s: infinitely many. Exactly one would need rank 3.
skills: [rank]
''',
)

write(
    "recall/review-predict-solve-check.yaml",
    '''id: review-predict-solve-check
type: predict_output
rev: 1
prompt: |
  A diagonal system. What does the program print?
code: |
  import numpy as np

  A = np.array([[2.0, 0.0], [0.0, 4.0]])
  b = np.array([6.0, 8.0])
  x = np.linalg.solve(A, b)
  print(x)
  print(np.allclose(A @ x, b))
expected_output: |
  [3. 2.]
  True
explanation: |
  With zeros off the diagonal the equations don't interact: `2x = 6` and `4y = 8`, so x = 3 and y = 2. The check multiplies back and agrees.
skills: [solve]
''',
)

write(
    "recall/review-mcq-how-many-solutions.yaml",
    '''id: review-mcq-how-many-solutions
type: mcq
rev: 1
prompt: |
  `x + y = 2` and `2x + 2y = 5`. How many solutions?
choices:
  - 'Exactly one'
  - 'None: the second equation says `x + y = 2.5`, which contradicts the first'
  - 'Infinitely many'
  - 'Two'
answer: 1
explanation: |
  Divide the second equation by 2 and it says `x + y = 2.5`; no pair of numbers adds to both 2 and 2.5. As lines, they're parallel and never meet. The matrix `[[1, 1], [2, 2]]` has rank 1, so a system with it has either no solution (this `b`) or infinitely many (a `b` on the line, such as `[2, 4]`).
skills: [rank]
''',
)

write(
    "recall/review-mcq-row-operations.yaml",
    '''id: review-mcq-row-operations
type: mcq
rev: 1
prompt: |
  In elimination, three of these keep the system's solutions exactly the same. Which one does **not**?
choices:
  - 'Swapping two rows'
  - 'Multiplying every entry of a row by 3'
  - 'Adding twice row 1 to row 2'
  - 'Squaring every entry of a row'
answer: 3
explanation: |
  Swapping, scaling by a non-zero number and adding a multiple of one row to another each turn the equations into equivalent ones: anything that satisfied the old set satisfies the new one and back. Squaring the entries makes a different equation (`2x = 4` and `4x = 16` have different solutions), so the answer changes.
skills: [eliminate]
''',
)

# --- practice: exercises -------------------------------------------------------

write(
    "exercises/example-two-equations/exercise.yaml",
    '''id: example-two-equations
stage: worked_example
rev: 1
title: "Two equations, three ways"
prompt: |
  The same two equations solved with `np.linalg.solve`, checked, then solved by elimination by hand, and finally the rank of this system against a singular one. Press **Run**, then read how each part works.
steps:
  - label: "The system as A x = b"
    lines: "3-6"
    note: "`2x + y = 5` and `x - y = 1`: one row per equation, the coefficients in `A` (unknowns in the order x, y) and the right-hand sides in `b`."
  - label: "Solve, then check"
    lines: "7-10"
    note: "`solve` returns the unknowns in column order: x = 2, y = 1. Multiplying `A` by the answer gives `b` back; `np.allclose` says so while forgiving rounding."
  - label: "Elimination by hand"
    lines: "12-17"
    note: "Put `b` alongside `A`. Subtracting half of row 0 from row 1 makes its x-coefficient zero, leaving `-1.5y = -1.5`, so y = 1; substituting back into row 0 gives x = 2. Each step keeps the solutions the same."
  - label: "Rank: how many independent equations"
    lines: "19-20"
    note: "`A` has rank 2: two independent equations for two unknowns, one solution. `[[1, 2], [2, 4]]` has rank 1: its second row is the first doubled, so a system with it has no solution or infinitely many, and `solve` would refuse."
''',
)
write(
    "exercises/example-two-equations/solution.py",
    '''import numpy as np

# 2x + y = 5
# x - y = 1
A = np.array([[2.0, 1.0], [1.0, -1.0]])
b = np.array([5.0, 1.0])
x = np.linalg.solve(A, b)
print(x)
print(A @ x)
print(np.allclose(A @ x, b))

rows = np.array([[2.0, 1.0, 5.0], [1.0, -1.0, 1.0]])
rows[1] = rows[1] - 0.5 * rows[0]
print(rows)
y = rows[1, 2] / rows[1, 1]
x1 = (rows[0, 2] - rows[0, 1] * y) / rows[0, 0]
print(x1, y)

print(np.linalg.matrix_rank(A))
print(np.linalg.matrix_rank(np.array([[1.0, 2.0], [2.0, 4.0]])))
''',
)
write(
    "exercises/example-two-equations/test_exercise.py",
    '''from checks import run


def test_the_walkthrough():
    """Prints the solution, the check, the eliminated rows, the hand solution and two ranks."""
    assert run() == (
        "[2. 1.]\\n[5. 1.]\\nTrue\\n[[ 2.   1.   5. ]\\n [ 0.  -1.5 -1.5]]\\n2.0 1.0\\n2\\n1\\n"
    )
''',
)

write(
    "exercises/fill-elimination-step/exercise.yaml",
    '''id: fill-elimination-step
stage: fill_in
rev: 1
title: "Elimination, in code"
prompt: |
  `solve_2x2(rows)` takes a 2-by-3 array, each row an equation with its right-hand side as the third entry, and solves it by elimination: zero the first unknown out of row 1, read off `y`, substitute back for `x`. Replace each `...` so the program prints:

  ```
  2.0 1.0
  ```

  The program fails until every `...` is replaced.
hints:
  - "The factor that zeroes row 1's first entry is `rows[1, 0] / rows[0, 0]`: subtract that many copies of row 0."
  - "After the step, row 1 is `0, something, something`: `y` is its last entry divided by its middle one."
skills: [eliminate]
''',
)
FILL_TAIL = '''

x, y = solve_2x2(np.array([[2.0, 1.0, 5.0], [1.0, -1.0, 1.0]]))
print(x, y)
'''
write(
    "exercises/fill-elimination-step/starter.py",
    '''import numpy as np


def solve_2x2(rows):
    rows = rows.astype(float).copy()
    factor = rows[1, 0] / ...
    rows[1] = rows[1] - ... * rows[0]
    y = rows[1, 2] / ...
    x = (rows[0, 2] - rows[0, 1] * y) / rows[0, 0]
    return x, y
''' + FILL_TAIL,
)
write(
    "exercises/fill-elimination-step/solution.py",
    '''import numpy as np


def solve_2x2(rows):
    rows = rows.astype(float).copy()
    factor = rows[1, 0] / rows[0, 0]
    rows[1] = rows[1] - factor * rows[0]
    y = rows[1, 2] / rows[1, 1]
    x = (rows[0, 2] - rows[0, 1] * y) / rows[0, 0]
    return x, y
''' + FILL_TAIL,
)
write(
    "exercises/fill-elimination-step/test_exercise.py",
    '''import numpy as np

from checks import function, run


def test_this_system():
    """Prints 2.0 1.0."""
    printed = run()
    assert printed == "2.0 1.0\\n", f"Your program printed:\\n{printed}"


def test_another_system():
    """3x + y = 9 and x + 2y = 8 give x = 2, y = 3."""
    solve_2x2 = function("solve_2x2")
    x, y = solve_2x2(np.array([[3.0, 1.0, 9.0], [1.0, 2.0, 8.0]]))
    assert np.allclose([x, y], [2.0, 3.0])
''',
)
write(
    "exercises/fill-elimination-step/wrong/forgets-the-factor.py",
    '''import numpy as np


def solve_2x2(rows):
    rows = rows.astype(float).copy()
    factor = rows[1, 0] / rows[0, 0]
    rows[1] = rows[1] - 1 * rows[0]
    y = rows[1, 2] / rows[1, 1]
    x = (rows[0, 2] - rows[0, 1] * y) / rows[0, 0]
    return x, y
''' + FILL_TAIL,
)
write(
    "exercises/fill-elimination-step/wrong/typed-in.py",
    '''import numpy as np


def solve_2x2(rows):
    return 2.0, 1.0
''' + FILL_TAIL,
)

write(
    "exercises/write-mix/exercise.yaml",
    '''id: write-mix
stage: write
rev: 1
title: "Mix two solutions"
prompt: |
  A lab has a weak solution and a strong one (say 10% and 40%) and needs `total` litres at a `target` strength (say 30 litres at 20%). Two facts: the litres add up to the total, and the amount of the active ingredient adds up to `target * total`. Write `mix(total, target, low, high)` that builds this as `A x = b` and returns the litres of the weak and the strong solution, as an array, using `np.linalg.solve`. Then print `mix(30, 0.2, 0.1, 0.4)`:

  ```
  [20. 10.]
  ```
hints:
  - "The two equations, with unknowns `[weak, strong]`: `weak + strong = total` and `low * weak + high * strong = target * total`."
  - "So `A = [[1, 1], [low, high]]` and `b = [total, target * total]`."
skills: [write-system, solve]
''',
)
write("exercises/write-mix/starter.py", "")
write(
    "exercises/write-mix/solution.py",
    '''import numpy as np


def mix(total, target, low, high):
    A = np.array([[1.0, 1.0], [low, high]])
    b = np.array([total, target * total])
    return np.linalg.solve(A, b)


print(mix(30, 0.2, 0.1, 0.4))
''',
)
write(
    "exercises/write-mix/test_exercise.py",
    '''import numpy as np

from checks import function, run


def test_the_output():
    """Prints [20. 10.]."""
    printed = run()
    assert printed == "[20. 10.]\\n", f"Your program printed:\\n{printed}"


def test_other_mixes():
    """10 litres at 50% from 20% and 80% is 5 and 5; 100 at 30% from 10% and 50% is 50 and 50."""
    mix = function("mix")
    assert np.allclose(mix(10, 0.5, 0.2, 0.8), [5.0, 5.0])
    assert np.allclose(mix(100, 0.3, 0.1, 0.5), [50.0, 50.0])
''',
)
write(
    "exercises/write-mix/wrong/target-not-scaled.py",
    '''import numpy as np


def mix(total, target, low, high):
    A = np.array([[1.0, 1.0], [low, high]])
    b = np.array([total, target])
    return np.linalg.solve(A, b)


print(mix(30, 0.2, 0.1, 0.4))
''',
)
write(
    "exercises/write-mix/wrong/typed-in.py",
    '''import numpy as np


def mix(total, target, low, high):
    return np.array([20.0, 10.0])


print(mix(30, 0.2, 0.1, 0.4))
''',
)

# --- proof ------------------------------------------------------------------

write(
    "exercises/build-parabola-through/exercise.yaml",
    '''id: build-parabola-through
stage: build
rev: 1
title: "The parabola through three points"
prompt: |
  Three points with different x's fix exactly one parabola `y = a x² + b x + c`: each point gives one equation in the three unknowns `a`, `b`, `c`. Starting from a blank editor, write `parabola_through(points)`, which takes three `(x, y)` pairs, builds the 3-by-3 system (one row per point: `x², x, 1`), solves it with `np.linalg.solve`, and returns `[a, b, c]` as an array. When two points share an x the system is singular: return `None` instead (check `np.linalg.matrix_rank` before solving).

  Then print the result for the points `(0, 1)`, `(1, 3)`, `(2, 9)`:

  ```
  [2. 0. 1.]
  ```

  The checks use other points, confirm the parabola passes through them, and hand in a pair of points with the same x.
skills: [write-system, solve, rank]
''',
)
write("exercises/build-parabola-through/starter.py", "")
write(
    "exercises/build-parabola-through/solution.py",
    '''import numpy as np


def parabola_through(points):
    pts = np.array(points, dtype=float)
    xs = pts[:, 0]
    ys = pts[:, 1]
    A = np.column_stack([xs**2, xs, np.ones(3)])
    if np.linalg.matrix_rank(A) < 3:
        return None
    return np.linalg.solve(A, ys)


print(parabola_through([(0, 1), (1, 3), (2, 9)]))
''',
)
write(
    "exercises/build-parabola-through/test_exercise.py",
    '''import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints [2. 0. 1.]."""
    assert run() == "[2. 0. 1.]\\n"


def test_other_points():
    """The parabola through (-1, 4), (0, 1), (2, 1) is y = x² - 2x + 1, and it passes through all three."""
    parabola_through = function("parabola_through")
    a, b, c = parabola_through([(-1, 4), (0, 1), (2, 1)])
    assert np.allclose([a, b, c], [1.0, -2.0, 1.0])
    for x, y in [(-1, 4), (0, 1), (2, 1)]:
        assert abs(a * x * x + b * x + c - y) < 1e-9


def test_two_points_share_an_x():
    """Points with a repeated x give None, not an error."""
    parabola_through = function("parabola_through")
    assert parabola_through([(1, 2), (1, 5), (3, 0)]) is None
''',
)
write(
    "exercises/build-parabola-through/wrong/reversed-columns.py",
    '''import numpy as np


def parabola_through(points):
    pts = np.array(points, dtype=float)
    xs = pts[:, 0]
    ys = pts[:, 1]
    A = np.column_stack([np.ones(3), xs, xs**2])
    if np.linalg.matrix_rank(A) < 3:
        return None
    return np.linalg.solve(A, ys)


print(parabola_through([(0, 1), (1, 3), (2, 9)]))
''',
)
write(
    "exercises/build-parabola-through/wrong/no-singular-check.py",
    '''import numpy as np


def parabola_through(points):
    pts = np.array(points, dtype=float)
    xs = pts[:, 0]
    ys = pts[:, 1]
    A = np.column_stack([xs**2, xs, np.ones(3)])
    return np.linalg.solve(A, ys)


print(parabola_through([(0, 1), (1, 3), (2, 9)]))
''',
)
write(
    "exercises/build-parabola-through/wrong/typed-in.py",
    '''import numpy as np


def parabola_through(points):
    return np.array([2.0, 0.0, 1.0])


print("[2. 0. 1.]")
''',
)

write(
    "exercises/debug-gaussian-elimination/exercise.yaml",
    '''id: debug-gaussian-elimination
stage: debug
rev: 1
title: "Elimination for any size"
prompt: |
  `gaussian_solve(A, b)` is elimination for a system of any size: it puts `b` alongside `A` as an extra column, zeroes out everything below each pivot, then substitutes back from the last row up. For the system in the program it should print the same answer `np.linalg.solve` would:

  ```
  [ 2.  3. -1.]
  ```

  It has two bugs. Run it and compare with `np.linalg.solve(A, b)`. One bug is a slice that stops one column too early during elimination; the other is a loop that stops one row too early during back-substitution.
skills: [eliminate, solve]
''',
)
GAUSS_TAIL = '''

A = np.array([[2.0, 1.0, -1.0], [-3.0, -1.0, 2.0], [-2.0, 1.0, 2.0]])
b = np.array([8.0, -11.0, -3.0])
print(np.round(gaussian_solve(A, b), 6))
'''
write(
    "exercises/debug-gaussian-elimination/starter.py",
    '''import numpy as np


def gaussian_solve(A, b):
    rows = np.hstack([A, b.reshape(-1, 1)]).astype(float)
    n = len(b)
    for col in range(n):
        for r in range(col + 1, n):
            factor = rows[r, col] / rows[col, col]
            rows[r, col:n] = rows[r, col:n] - factor * rows[col, col:n]
    x = np.zeros(n)
    for r in range(n - 1, 0, -1):
        x[r] = (rows[r, n] - rows[r, r + 1 : n] @ x[r + 1 :]) / rows[r, r]
    return x
''' + GAUSS_TAIL,
)
write(
    "exercises/debug-gaussian-elimination/solution.py",
    '''import numpy as np


def gaussian_solve(A, b):
    rows = np.hstack([A, b.reshape(-1, 1)]).astype(float)
    n = len(b)
    for col in range(n):
        for r in range(col + 1, n):
            factor = rows[r, col] / rows[col, col]
            rows[r, col:] = rows[r, col:] - factor * rows[col, col:]
    x = np.zeros(n)
    for r in range(n - 1, -1, -1):
        x[r] = (rows[r, n] - rows[r, r + 1 : n] @ x[r + 1 :]) / rows[r, r]
    return x
''' + GAUSS_TAIL,
)
write(
    "exercises/debug-gaussian-elimination/test_exercise.py",
    '''import numpy as np

from checks import function, run

EXPECTED = "[ 2.  3. -1.]\\n"


def test_the_output():
    """Prints [ 2.  3. -1.]."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\\n{EXPECTED}\\nYour program printed:\\n{printed}"


def test_another_system():
    """Agrees with np.linalg.solve on another 3-by-3 system."""
    gaussian_solve = function("gaussian_solve")
    A = np.array([[1.0, 2.0, 0.0], [0.0, 1.0, 3.0], [4.0, 0.0, 1.0]])
    b = np.array([5.0, 10.0, 9.0])
    assert np.allclose(gaussian_solve(A, b), np.linalg.solve(A, b))
''',
)
write(
    "exercises/debug-gaussian-elimination/wrong/one-of-two.py",
    '''import numpy as np


def gaussian_solve(A, b):
    rows = np.hstack([A, b.reshape(-1, 1)]).astype(float)
    n = len(b)
    for col in range(n):
        for r in range(col + 1, n):
            factor = rows[r, col] / rows[col, col]
            rows[r, col:] = rows[r, col:] - factor * rows[col, col:]
    x = np.zeros(n)
    for r in range(n - 1, 0, -1):
        x[r] = (rows[r, n] - rows[r, r + 1 : n] @ x[r + 1 :]) / rows[r, r]
    return x
''' + GAUSS_TAIL,
)
write(
    "exercises/debug-gaussian-elimination/wrong/typed-in.py",
    '''import numpy as np


def gaussian_solve(A, b):
    return np.array([2.0, 3.0, -1.0])
''' + GAUSS_TAIL,
)

# --- review pool: a code exercise -------------------------------------------

write(
    "exercises/review-solve-3x3/exercise.yaml",
    '''id: review-solve-3x3
stage: review_code
rev: 1
title: "Three unknowns"
prompt: |
  Write `solve_system(A, b)`, which returns the solution of `A x = b` rounded to 6 places, and print it for the starter's `A` and `b`:

  ```
  [ 5.  3. -2.]
  ```
skills: [solve, write-system]
''',
)
STARTER_3X3 = '''import numpy as np

A = np.array([[1.0, 1.0, 1.0], [0.0, 2.0, 5.0], [2.0, 5.0, -1.0]])
b = np.array([6.0, -4.0, 27.0])
'''
write("exercises/review-solve-3x3/starter.py", STARTER_3X3)
write(
    "exercises/review-solve-3x3/solution.py",
    STARTER_3X3 + '''

def solve_system(A, b):
    return np.round(np.linalg.solve(A, b), 6)


print(solve_system(A, b))
''',
)
write(
    "exercises/review-solve-3x3/test_exercise.py",
    '''import numpy as np

from checks import function, run


def test_the_output():
    """Prints [ 5.  3. -2.]."""
    assert run() == "[ 5.  3. -2.]\\n"


def test_another_system():
    """Solves a 2-by-2 system too."""
    solve_system = function("solve_system")
    assert solve_system(np.array([[2.0, 1.0], [1.0, -1.0]]), np.array([5.0, 1.0])).tolist() == [2.0, 1.0]
''',
)
write(
    "exercises/review-solve-3x3/wrong/swapped-arguments.py",
    STARTER_3X3 + '''

def solve_system(A, b):
    return np.round(np.linalg.solve(A.T, b), 6)


print(solve_system(A, b))
''',
)
write(
    "exercises/review-solve-3x3/wrong/typed-in.py",
    STARTER_3X3 + '''

def solve_system(A, b):
    return np.array([5.0, 3.0, -2.0])


print("[ 5.  3. -2.]")
''',
)

print("ml.la.systems written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
