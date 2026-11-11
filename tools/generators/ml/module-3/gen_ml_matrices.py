"""Writes the topic ml.la.matrices-as-maps (Module 3's third topic). Run from
the repository root. Files are written as bytes with LF endings."""

import pathlib

ROOT = pathlib.Path("content/topics/ml.la.matrices-as-maps")


def write(relative: str, text: str) -> None:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


HELPERS = '''import numpy as np


def scaling(sx, sy):
    return np.array([[sx, 0.0], [0.0, sy]])


def rotation(degrees):
    t = np.radians(degrees)
    return np.array([[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]])
'''

write(
    "topic.yaml",
    '''id: ml.la.matrices-as-maps
kind: topic
status: ready
title: "Matrices as transformations"
summary: "A matrix as a function on vectors: rotations, scalings and shears as pictures, composition as multiplication, the inverse and the determinant."
prerequisites: [ml.la.vectors]
packages: [numpy]
estimated_minutes: 55
rev: 1
objectives:
  - "Apply a matrix to a vector, and say where the grid goes from the matrix's columns."
  - "Build rotation, scaling and shear matrices, and compose them by multiplying."
  - "Say what the identity and the inverse do, and when there is no inverse."
  - "Read the determinant as how much area is scaled."
# Linked, never copied or embedded: 3Blue1Brown's videos are under the
# standard YouTube licence; NumPy's documentation under the NumPy licence
# (BSD-3-Clause).
resources:
  - title: "Essence of linear algebra, chapter 3: Linear transformations and matrices (3Blue1Brown, Grant Sanderson)"
    url: https://www.youtube.com/watch?v=kYB8IZa5AuE
    type: video
    use: link
    license: Standard YouTube licence (linked, not embedded)
  - title: "Essence of linear algebra, chapter 4: Matrix multiplication as composition (3Blue1Brown, Grant Sanderson)"
    url: https://www.youtube.com/watch?v=XkY2DOUCWMU
    type: video
    use: link
    license: Standard YouTube licence (linked, not embedded)
  - title: "Essence of linear algebra, chapter 6: The determinant (3Blue1Brown, Grant Sanderson)"
    url: https://www.youtube.com/watch?v=Ip3X9LOh2dk
    type: video
    use: link
    license: Standard YouTube licence (linked, not embedded)
  - title: "numpy.linalg: inv and det (the NumPy developers)"
    url: https://numpy.org/doc/stable/reference/routines.linalg.html
    type: reading
    use: link
    license: BSD-3-Clause (NumPy documentation)
practice:
  - example-where-the-grid-goes
  - parsons-rotation-matrix
  - mcq-columns
  - predict-order-matters
  - mcq-determinant-zero
  - fill-scale-and-rotate
  - mcq-inverse
  - write-transform-points
prove:
  build: build-compose-and-undo
  debug: debug-transform-mistakes
  explain:
    prompt: |
      A teammate says a matrix is "a grid of numbers you multiply somehow". Set them straight, in your own words: what does a 2-by-2 matrix do to a vector, and why do its two columns tell you everything about it? What does multiplying two matrices mean, and why is `A @ B` usually not `B @ A`? What does the determinant measure, and what does a determinant of zero tell you about undoing the transformation?
    rubric:
      - id: columns
        required: true
        description: "A matrix is a function that moves every vector; its columns are where the basis vectors [1, 0] and [0, 1] land, and every other vector follows by stretching and adding those."
      - id: composition
        required: true
        description: "The product A @ B is the single matrix that does B first, then A; order matters because doing the transformations in the other order generally lands somewhere else (rotate then scale is not scale then rotate)."
      - id: determinant
        required: true
        description: "The determinant is the factor by which area is scaled (negative when orientation flips); zero means the plane is squashed onto a line or a point, information is lost, and there is no inverse."
      - id: identity-inverse
        required: false
        description: "The identity leaves every vector alone; the inverse undoes the matrix so inv(A) @ A is the identity."
    model_answer: |
      A matrix is a function: feed it a vector, get a vector back, and it moves the whole plane in a way that keeps grid lines straight and evenly spaced. You can read the function off the two columns: the first column is where [1, 0] lands and the second is where [0, 1] lands, and any vector [x, y] is x copies of the first column plus y copies of the second, so those two arrows determine everything. Multiplying two matrices builds the matrix that does one transformation after the other: A @ B does B first and then A. It isn't commutative because doing things in the other order usually ends somewhere else; rotating a square and then stretching it sideways gives a different shape from stretching it and then rotating. The determinant is the number the matrix multiplies every area by: a scaling of 2 by 3 has determinant 6, a rotation has 1, and a negative determinant means the plane was flipped over. A determinant of zero means areas become zero: the plane has been squashed onto a line or a point, different vectors now land in the same place, and there is nothing to undo it with, so the matrix has no inverse. Otherwise the inverse exists, and inv(A) @ A is the identity, the matrix that leaves every vector where it is.
review_pool:
  - review-predict-identity
  - review-mcq-order
  - review-predict-det-scale
  - review-apply-matrix
# What this topic teaches. Each question names the skills it tests, so a
# missed question can come back as a different one on the same skill
# (ADR-0011).
skills:
  - id: apply
    description: "Apply a matrix to a vector, and read where the grid goes from the columns"
  - id: build
    description: "Build rotation, scaling and shear matrices"
  - id: compose
    description: "Compose transformations by multiplying, in the right order"
  - id: inverse-det
    description: "Know what the identity, the inverse and the determinant mean, and when there is no inverse"
''',
)

write(
    "lesson.mdx",
    '''<Intro>

Module 1 multiplied a matrix by a vector with loops and checked the shapes. This topic is about what that multiplication **means**: a matrix is a function that moves every vector in the plane at once, keeping the grid straight and evenly spaced. Rotations, stretches and shears are matrices, doing one after another is multiplying them, and the determinant is how much area they scale.

The main resource is **3Blue1Brown's chapter 3** of *Essence of linear algebra*, linear transformations and matrices: ten minutes of the grid moving. Then **chapter 4**, matrix multiplication as composition, and **chapter 6**, the determinant. About 35 minutes of video; worth every one. Watch for:

- **The columns** of a matrix are where `[1, 0]` and `[0, 1]` land. Everything else follows.
- **Multiplication is composition:** `A @ B` does `B` first, then `A`.
- **The determinant** is the area-scaling factor, and zero means squashed flat.

In the code, pictures are coordinates: the four corners of the unit square, before and after. Print them and sketch them on paper if the video's grid isn't in your head yet.

</Intro>

<Resource index={0} />

<Recap>

- **A matrix is a function on vectors:** `A @ v`. Its **columns** are where the basis vectors land: `A @ [1, 0]` is the first column, `A @ [0, 1]` the second, and `A @ [x, y]` is `x` times the first plus `y` times the second.
- **The standard ones.** Scaling: `[[sx, 0], [0, sy]]`. Rotation by θ, anticlockwise: `[[cos θ, -sin θ], [sin θ, cos θ]]` (with θ in radians: `np.radians(90)`). Shear: `[[1, k], [0, 1]]` slides each row sideways by `k` times its height. `np.eye(2)` is the identity, which moves nothing.
- **Composition is multiplication.** `(A @ B) @ v` equals `A @ (B @ v)`: `B` acts first. **Order matters:** rotate-then-scale and scale-then-rotate are different matrices, so `A @ B` is usually not `B @ A`.
- **Many points at once:** with points as rows of an `(n, 2)` array, `points @ M.T` transforms them all; no loop.
- **The inverse** `np.linalg.inv(A)` undoes `A`: `inv(A) @ A` is the identity. It exists only when the determinant isn't zero; otherwise `inv` raises `LinAlgError: Singular matrix`.
- **The determinant** `np.linalg.det(A)` is the factor by which `A` scales area: 6 for a scaling by 2 and 3, 1 for a rotation, 1 for a shear (it slants the square but keeps its area). Negative means the plane was flipped. **Zero means squashed** onto a line or a point: different vectors land in the same place, and nothing can undo that.
- **Rotations aren't exact.** `cos(90°)` comes out as `6e-17` rather than `0`, and a tiny negative rounds to `-0.`; the exercises print `np.round(v, 6) + 0.0`, which rounds the noise away and turns a `-0.` into a plain `0.`.
- **In machine learning:** a layer of a neural network is a matrix applied to a vector (then a bend); an image rotated or flipped for training is this topic's matrices applied to pixel coordinates; PCA, three topics from now, is a rotation chosen to line the data up with the axes.

</Recap>
''',
)

# --- practice: recall --------------------------------------------------------

write(
    "recall/parsons-rotation-matrix.yaml",
    '''id: parsons-rotation-matrix
type: parsons
rev: 1
prompt: |
  Put the lines in order to build the matrix that rotates by 90 degrees anticlockwise and apply it to `[1, 0]`, printing `[0. 1.]`. One line is a decoy that doesn't belong.
lines:
  - 'import numpy as np'
  - 'theta = np.radians(90)'
  - 'R = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])'
  - 'print(np.round(R @ np.array([1.0, 0.0]), 6))'
distractors:
  - 'R = np.array([[np.cos(theta), np.sin(theta)], [-np.sin(theta), np.cos(theta)]])'
explanation: |
  The rotation matrix has `-sin` in the top right: its first column, `[cos θ, sin θ]`, is where `[1, 0]` lands, which for 90 degrees is `[0, 1]`, straight up. The decoy has the minus sign on the other `sin`, which rotates **clockwise** and sends `[1, 0]` to `[0, -1]`. `np.round` hides the `6e-17` that `cos(90°)` comes out as.
skills: [build]
''',
)

write(
    "recall/mcq-columns.yaml",
    '''id: mcq-columns
type: mcq
rev: 1
prompt: |
  `A = np.array([[2, 1], [0, 3]])`. Without multiplying anything out, where does `[0, 1]` land under `A`?
choices:
  - '`[2, 0]`, the first column'
  - '`[1, 3]`, the second column'
  - '`[0, 3]`, the second row'
  - '`[0, 1]`: a matrix never moves the basis vectors'
answer: 1
explanation: |
  The columns of a matrix are where the basis vectors land: `A @ [1, 0]` is the first column and `A @ [0, 1]` the second. Check it: 2 × 0 + 1 × 1 = 1 and 0 × 0 + 3 × 1 = 3. Rows are the other direction, how each output coordinate is made.
skills: [apply]
''',
)

write(
    "recall/predict-order-matters.yaml",
    '''id: predict-order-matters
type: predict_output
rev: 1
prompt: |
  A rotation by 90 degrees and a shear, applied to the same vector in both orders. What does the program print?
code: |
  import numpy as np

  R = np.array([[0.0, -1.0], [1.0, 0.0]])
  S = np.array([[1.0, 1.0], [0.0, 1.0]])
  v = np.array([1.0, 1.0])
  print(S @ v)
  print(R @ (S @ v))
  print((R @ S) @ v)
  print((S @ R) @ v)
expected_output: |
  [2. 1.]
  [-1.  2.]
  [-1.  2.]
  [0. 1.]
explanation: |
  The shear slides `[1, 1]` to `[2, 1]`; rotating that by 90 degrees gives `[-1, 2]`. `(R @ S) @ v` is the same journey as one matrix: `S` first, then `R`. `S @ R` does the rotation first (`[1, 1]` goes to `[-1, 1]`) and then the shear (`[0, 1]`): a different place, because the order of transformations matters.
skills: [compose]
''',
)

write(
    "recall/mcq-determinant-zero.yaml",
    '''id: mcq-determinant-zero
type: mcq
rev: 1
prompt: |
  `np.linalg.det(M)` is `0.0`. What does that tell you about `M`?
choices:
  - '`M` is the identity'
  - '`M` squashes the plane onto a line or a point, so areas become zero and `M` has no inverse'
  - '`M` is a rotation'
  - '`M` doubles every area'
answer: 1
explanation: |
  The determinant is the factor by which `M` scales area. Zero area means the whole plane has been flattened onto a line (or a point): different vectors now land on top of each other, and no matrix can tell them apart again, so `np.linalg.inv(M)` raises `Singular matrix`. The identity and rotations have determinant 1.
skills: [inverse-det]
''',
)

write(
    "recall/mcq-inverse.yaml",
    '''id: mcq-inverse
type: mcq
rev: 1
prompt: |
  `A` stretches the plane by 2 along x. What is `np.linalg.inv(A) @ (A @ v)`?
choices:
  - '`v` itself: the inverse undoes `A`'
  - '`v` stretched by 4 along x'
  - 'The zero vector'
  - 'An error: a stretch has no inverse'
answer: 0
explanation: |
  The inverse of a transformation is the one that undoes it: here, squash by 2 along x. Doing `A` and then its inverse lands every vector back where it started, which is what `inv(A) @ A` being the identity means. A stretch has an inverse because its determinant (2) isn't zero.
skills: [inverse-det]
''',
)

write(
    "recall/review-predict-identity.yaml",
    '''id: review-predict-identity
type: predict_output
rev: 1
prompt: |
  The identity matrix, printed and applied. What does the program print?
code: |
  import numpy as np

  I = np.eye(2)
  print(I)
  print(I @ np.array([5.0, -2.0]))
expected_output: |
  [[1. 0.]
   [0. 1.]]
  [ 5. -2.]
explanation: |
  `np.eye(2)` is the 2-by-2 identity: ones on the diagonal, zeros elsewhere. Its columns are `[1, 0]` and `[0, 1]`, so the basis vectors land on themselves, and so does every other vector. NumPy pads `5.` to line up with `-2.`.
skills: [inverse-det, apply]
''',
)

write(
    "recall/review-mcq-order.yaml",
    '''id: review-mcq-order
type: mcq
rev: 1
prompt: |
  `A @ B` is the matrix that…
choices:
  - 'does `A` first, then `B`'
  - 'does `B` first, then `A`'
  - 'does `A` and `B` at the same time, so the order never matters'
  - 'adds the two transformations together'
answer: 1
explanation: |
  `(A @ B) @ v` is `A @ (B @ v)`: the matrix nearest the vector acts first. Read it right to left, like function composition `f(g(x))`. Because doing the two transformations in the other order usually ends somewhere else, `A @ B` and `B @ A` are usually different matrices.
skills: [compose]
''',
)

write(
    "recall/review-predict-det-scale.yaml",
    '''id: review-predict-det-scale
type: predict_output
rev: 1
prompt: |
  The determinant of a scaling. What does the program print?
code: |
  import numpy as np

  M = np.array([[2.0, 0.0], [0.0, 3.0]])
  print(round(float(np.linalg.det(M)), 6))
  square = np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]])
  print(square @ M.T)
expected_output: |
  6.0
  [[0. 0.]
   [2. 0.]
   [2. 3.]
   [0. 3.]]
explanation: |
  Stretching by 2 along x and 3 along y turns the unit square into a 2-by-3 rectangle: six times the area, which is exactly what the determinant says. `square @ M.T` applies the matrix to every corner at once, one row each.
skills: [inverse-det, apply]
''',
)

# --- practice: exercises -------------------------------------------------------

write(
    "exercises/example-where-the-grid-goes/exercise.yaml",
    '''id: example-where-the-grid-goes
stage: worked_example
rev: 1
title: "Where the grid goes"
prompt: |
  This program applies a stretch, a rotation and a shear to vectors, composes them in both orders, and ends with the identity, the inverse and the determinant. Press **Run**, then read how each part works, sketching the vectors if it helps.
steps:
  - label: "A matrix moves a vector, and its columns say how"
    lines: "3-6"
    note: "`A` doubles the x-coordinate: `[1, 1]` goes to `[2, 1]`. Its columns are where the basis vectors land: `[1, 0]` goes to `[2, 0]`, `[0, 1]` stays `[0, 1]`."
  - label: "A rotation"
    lines: "7-9"
    note: "`R` is the 90-degree rotation. It sends `[1, 0]` straight up to `[0, 1]`; applied twice, `[1, 0]` lands at `[-1, 0]`: 180 degrees."
  - label: "A shear"
    lines: "10-11"
    note: "`S` slides the top of the square sideways: `[0, 1]` goes to `[1, 1]` while the bottom edge stays put. The square becomes a slanted parallelogram of the same area."
  - label: "Composition, and why order matters"
    lines: "12"
    note: "`R @ S` means shear first, then rotate: `[1, 1]` lands at `[-1, 2]`. `S @ R` rotates first, then shears: `[0, 1]`. Different matrices, different places."
  - label: "Identity, inverse, determinant"
    lines: "14-20"
    note: "`np.eye(2)` moves nothing. `inv(A)` halves x, undoing `A`: applying both lands back on `[1, 1]`. The determinant is the area factor: 2 for the stretch, 1 for the rotation, 1 for the shear."
''',
)
write(
    "exercises/example-where-the-grid-goes/solution.py",
    '''import numpy as np

A = np.array([[2.0, 0.0], [0.0, 1.0]])
v = np.array([1.0, 1.0])
print(A @ v)
print(A @ np.array([1.0, 0.0]), A @ np.array([0.0, 1.0]))
R = np.array([[0.0, -1.0], [1.0, 0.0]])
print(R @ np.array([1.0, 0.0]))
print(R @ R @ np.array([1.0, 0.0]))
S = np.array([[1.0, 1.0], [0.0, 1.0]])
print(S @ np.array([0.0, 1.0]))
print((R @ S) @ v, (S @ R) @ v)

I = np.eye(2)
print(I @ v)
print(np.linalg.inv(A))
print(np.linalg.inv(A) @ (A @ v))
print(round(np.linalg.det(A)))
print(round(np.linalg.det(R)))
print(round(np.linalg.det(S)))
''',
)
write(
    "exercises/example-where-the-grid-goes/test_exercise.py",
    '''from checks import run


def test_the_walkthrough():
    """Prints the stretched, rotated and sheared vectors, both compositions, the identity's work, the inverse and three determinants."""
    assert run() == (
        "[2. 1.]\\n[2. 0.] [0. 1.]\\n[0. 1.]\\n[-1.  0.]\\n[1. 1.]\\n[-1.  2.] [0. 1.]\\n"
        "[1. 1.]\\n[[0.5 0. ]\\n [0.  1. ]]\\n[1. 1.]\\n2\\n1\\n1\\n"
    )
''',
)

write(
    "exercises/fill-scale-and-rotate/exercise.yaml",
    '''id: fill-scale-and-rotate
stage: fill_in
rev: 1
title: "Scaling and rotation matrices"
prompt: |
  Two functions that build matrices: `scaling(sx, sy)` stretches by `sx` along x and `sy` along y, and `rotation(degrees)` rotates anticlockwise. Replace each `...` so the program prints:

  ```
  [-1.  0.]
  [3.  0.5]
  [-2.  0.]
  ```

  The program fails until every `...` is replaced.
hints:
  - "A scaling matrix has the two factors on the diagonal and zeros elsewhere: `[[sx, 0], [0, sy]]`."
  - "`np.cos` and `np.sin` want radians: `np.radians(degrees)` converts. The rotation matrix is `[[cos, -sin], [sin, cos]]`."
skills: [build]
''',
)
write(
    "exercises/fill-scale-and-rotate/starter.py",
    '''import numpy as np


def scaling(sx, sy):
    return np.array([[sx, 0.0], [0.0, ...]])


def rotation(degrees):
    t = np.radians(...)
    return np.array([[np.cos(t), -np.sin(t)], [np.sin(t), ...]])


print(np.round(rotation(180) @ np.array([1.0, 0.0]), 6))
print(scaling(3, 0.5) @ np.array([1.0, 1.0]))
print(np.round(rotation(90) @ np.array([0.0, 2.0]), 6))
''',
)
write(
    "exercises/fill-scale-and-rotate/solution.py",
    HELPERS + '''

print(np.round(rotation(180) @ np.array([1.0, 0.0]), 6))
print(scaling(3, 0.5) @ np.array([1.0, 1.0]))
print(np.round(rotation(90) @ np.array([0.0, 2.0]), 6))
''',
)
write(
    "exercises/fill-scale-and-rotate/test_exercise.py",
    '''import numpy as np

from checks import function, run


def test_the_output():
    """Prints the three transformed vectors."""
    printed = run()
    assert printed == "[-1.  0.]\\n[3.  0.5]\\n[-2.  0.]\\n", f"Your program printed:\\n{printed}"


def test_the_matrices():
    """rotation(45) sends [1, 0] to [0.7071, 0.7071]; scaling(2, 3) has determinant 6."""
    rotation = function("rotation")
    scaling = function("scaling")
    assert np.round(rotation(45) @ np.array([1.0, 0.0]), 4).tolist() == [0.7071, 0.7071]
    assert round(float(np.linalg.det(scaling(2, 3))), 6) == 6.0
''',
)
write(
    "exercises/fill-scale-and-rotate/wrong/degrees-not-radians.py",
    '''import numpy as np


def scaling(sx, sy):
    return np.array([[sx, 0.0], [0.0, sy]])


def rotation(degrees):
    t = np.radians(1) * 0 + degrees
    return np.array([[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]])


print(np.round(rotation(180) @ np.array([1.0, 0.0]), 6))
print(scaling(3, 0.5) @ np.array([1.0, 1.0]))
print(np.round(rotation(90) @ np.array([0.0, 2.0]), 6))
''',
)
write(
    "exercises/fill-scale-and-rotate/wrong/typed-in.py",
    '''import numpy as np


def scaling(sx, sy):
    return np.array([[3.0, 0.0], [0.0, 0.5]])


def rotation(degrees):
    return np.array([[-1.0, 0.0], [0.0, -1.0]])


print("[-1.  0.]")
print("[3.  0.5]")
print("[-2.  0.]")
''',
)

write(
    "exercises/write-transform-points/exercise.yaml",
    '''id: write-transform-points
stage: write
rev: 1
title: "Transform every point at once"
prompt: |
  `square` holds the four corners of the unit square, one point per row. Write `transform(M, points)`, which applies the matrix `M` to every row at once and returns the new points in the same shape, with no loop: `points @ M.T` does it (each row times the transposed matrix is `M @ row`). Then print the square under the shear `S` in the starter:

  ```
  [[0. 0.]
   [1. 0.]
   [2. 1.]
   [1. 1.]]
  ```
hints:
  - "For one point, `M @ p`. For a whole array of points as rows, `points @ M.T` gives `M @ p` for every row, as rows."
  - "The result has the same shape as `points`: one transformed point per row."
skills: [apply, compose]
''',
)
STARTER_POINTS = '''import numpy as np

square = np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]])
S = np.array([[1.0, 1.0], [0.0, 1.0]])
'''
write("exercises/write-transform-points/starter.py", STARTER_POINTS)
write(
    "exercises/write-transform-points/solution.py",
    STARTER_POINTS + '''

def transform(M, points):
    return points @ M.T


print(transform(S, square))
''',
)
write(
    "exercises/write-transform-points/test_exercise.py",
    '''import numpy as np

from checks import function, run


def test_the_output():
    """Prints the sheared square's corners."""
    printed = run()
    assert printed == "[[0. 0.]\\n [1. 0.]\\n [2. 1.]\\n [1. 1.]]\\n", f"Your program printed:\\n{printed}"


def test_other_matrix_and_points():
    """A scaling by 2 and 3 of two points gives each point scaled, as rows."""
    transform = function("transform")
    M = np.array([[2.0, 0.0], [0.0, 3.0]])
    points = np.array([[1.0, 1.0], [-1.0, 0.5]])
    assert transform(M, points).tolist() == [[2.0, 3.0], [-2.0, 1.5]]
''',
)
write(
    "exercises/write-transform-points/wrong/no-transpose.py",
    STARTER_POINTS + '''

def transform(M, points):
    return points @ M


print(transform(S, square))
''',
)
write(
    "exercises/write-transform-points/wrong/typed-in.py",
    STARTER_POINTS + '''

def transform(M, points):
    return np.array([[0.0, 0.0], [1.0, 0.0], [2.0, 1.0], [1.0, 1.0]])


print(transform(S, square))
''',
)

# --- proof ------------------------------------------------------------------

write(
    "exercises/build-compose-and-undo/exercise.yaml",
    '''id: build-compose-and-undo
stage: build
rev: 1
title: "Compose, and undo"
prompt: |
  Starting from a blank editor, write `scaling(sx, sy)` and `rotation(degrees)` as in the fill-in, then two more functions:

  - `compose(*matrices)` returns the **single** matrix that applies the given matrices **in the order given**, first argument first. So `compose(A, B) @ v` must equal `B @ (A @ v)`. Any number of matrices, at least one.
  - `undo(M)` returns the inverse of `M`, or `None` when `M` has no inverse (its determinant is zero, allowing for rounding: `abs(det) < 1e-12`).

  Then print, rounded to 6 places: `compose(rotation(90), scaling(2, 3)) @ [1, 0]`, the same with the two swapped, and `undo` of the matrix `[[1, 2], [2, 4]]`:

  ```
  [0. 3.]
  [0. 2.]
  None
  ```

  The checks compose other matrices, apply `undo` to a matrix that does have an inverse, and check `undo(M) @ M` is the identity.
skills: [compose, inverse-det, build]
''',
)
write("exercises/build-compose-and-undo/starter.py", "")
write(
    "exercises/build-compose-and-undo/solution.py",
    HELPERS + '''

def compose(*matrices):
    result = np.eye(len(matrices[0]))
    for M in matrices:
        result = M @ result
    return result


def undo(M):
    if abs(np.linalg.det(M)) < 1e-12:
        return None
    return np.linalg.inv(M)


print(np.round(compose(rotation(90), scaling(2, 3)) @ np.array([1.0, 0.0]), 6))
print(np.round(compose(scaling(2, 3), rotation(90)) @ np.array([1.0, 0.0]), 6))
print(undo(np.array([[1.0, 2.0], [2.0, 4.0]])))
''',
)
write(
    "exercises/build-compose-and-undo/test_exercise.py",
    '''import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints [0. 3.], [0. 2.] and None."""
    assert run() == "[0. 3.]\\n[0. 2.]\\nNone\\n"


def test_compose_applies_in_order():
    """compose(A, B, C) @ v is C @ (B @ (A @ v)), and compose(A) is A."""
    compose = function("compose")
    A = np.array([[1.0, 2.0], [0.0, 1.0]])
    B = np.array([[0.0, -1.0], [1.0, 0.0]])
    C = np.array([[3.0, 0.0], [0.0, 0.5]])
    v = np.array([1.0, -2.0])
    assert np.allclose(compose(A, B, C) @ v, C @ (B @ (A @ v)))
    assert np.allclose(compose(A), A)


def test_undo():
    """undo(M) @ M is the identity when M has an inverse, and undo is None when it hasn't."""
    undo = function("undo")
    M = np.array([[2.0, 1.0], [1.0, 3.0]])
    assert np.allclose(undo(M) @ M, np.eye(2))
    assert undo(np.array([[1.0, 1.0], [1.0, 1.0]])) is None
    assert undo(np.array([[0.0, 0.0], [0.0, 0.0]])) is None
''',
)
write(
    "exercises/build-compose-and-undo/wrong/wrong-order.py",
    HELPERS + '''

def compose(*matrices):
    result = np.eye(len(matrices[0]))
    for M in matrices:
        result = result @ M
    return result


def undo(M):
    if abs(np.linalg.det(M)) < 1e-12:
        return None
    return np.linalg.inv(M)


print(np.round(compose(rotation(90), scaling(2, 3)) @ np.array([1.0, 0.0]), 6))
print(np.round(compose(scaling(2, 3), rotation(90)) @ np.array([1.0, 0.0]), 6))
print(undo(np.array([[1.0, 2.0], [2.0, 4.0]])))
''',
)
write(
    "exercises/build-compose-and-undo/wrong/no-singular-check.py",
    HELPERS + '''

def compose(*matrices):
    result = np.eye(len(matrices[0]))
    for M in matrices:
        result = M @ result
    return result


def undo(M):
    return np.linalg.inv(M)


print(np.round(compose(rotation(90), scaling(2, 3)) @ np.array([1.0, 0.0]), 6))
print(np.round(compose(scaling(2, 3), rotation(90)) @ np.array([1.0, 0.0]), 6))
print(undo(np.array([[1.0, 2.0], [2.0, 4.0]])))
''',
)
write(
    "exercises/build-compose-and-undo/wrong/typed-in.py",
    HELPERS + '''

def compose(*matrices):
    return matrices[0]


def undo(M):
    return None


print("[0. 3.]")
print("[0. 2.]")
print(None)
''',
)

write(
    "exercises/debug-transform-mistakes/exercise.yaml",
    '''id: debug-transform-mistakes
stage: debug
rev: 1
title: "The square that went wrong"
prompt: |
  `corners_after(M, corners)` should print each corner of the unit square after a 90-degree anticlockwise rotation:

  ```
  [0. 0.]
  [0. 1.]
  [-1.  1.]
  [-1.  0.]
  ```

  It has two bugs. Run it: the first output is the wrong **shape** entirely, which points at the operator; once that's fixed, the corners come out rotated the wrong way, which points at the matrix.
skills: [apply, build]
''',
)
DEBUG_TAIL = '''

corners = np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]])
corners_after(rotation(90), corners)
'''
write(
    "exercises/debug-transform-mistakes/starter.py",
    '''import numpy as np


def rotation(degrees):
    t = np.radians(degrees)
    return np.array([[np.cos(t), np.sin(t)], [-np.sin(t), np.cos(t)]])


def corners_after(M, corners):
    for corner in corners:
        # Rounded, and + 0.0 turns a -0. into a plain 0.
        print(np.round(M * corner, 6) + 0.0)
''' + DEBUG_TAIL,
)
write(
    "exercises/debug-transform-mistakes/solution.py",
    '''import numpy as np


def rotation(degrees):
    t = np.radians(degrees)
    return np.array([[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]])


def corners_after(M, corners):
    for corner in corners:
        # Rounded, and + 0.0 turns a -0. into a plain 0.
        print(np.round(M @ corner, 6) + 0.0)
''' + DEBUG_TAIL,
)
write(
    "exercises/debug-transform-mistakes/test_exercise.py",
    '''import numpy as np

from checks import function, printed, run

EXPECTED = "[0. 0.]\\n[0. 1.]\\n[-1.  1.]\\n[-1.  0.]\\n"


def test_the_output():
    """Prints the four rotated corners."""
    out = run()
    assert out == EXPECTED, f"Expected this:\\n{EXPECTED}\\nYour program printed:\\n{out}"


def test_other_angle_and_points():
    """rotation(180) sends [1, 2] to [-1, -2] and [3, -1] to [-3, 1]."""
    rotation = function("rotation")
    corners_after = function("corners_after")
    out = printed(corners_after, rotation(180), np.array([[1.0, 2.0], [3.0, -1.0]]))
    assert out == "[-1. -2.]\\n[-3.  1.]\\n", f"For a half turn it printed:\\n{out}"
''',
)
write(
    "exercises/debug-transform-mistakes/wrong/operator-only.py",
    '''import numpy as np


def rotation(degrees):
    t = np.radians(degrees)
    return np.array([[np.cos(t), np.sin(t)], [-np.sin(t), np.cos(t)]])


def corners_after(M, corners):
    for corner in corners:
        # Rounded, and + 0.0 turns a -0. into a plain 0.
        print(np.round(M @ corner, 6) + 0.0)
''' + DEBUG_TAIL,
)
write(
    "exercises/debug-transform-mistakes/wrong/typed-in.py",
    '''import numpy as np


def rotation(degrees):
    return np.eye(2)


def corners_after(M, corners):
    print("[0. 0.]")
    print("[0. 1.]")
    print("[-1.  1.]")
    print("[-1.  0.]")
''' + DEBUG_TAIL,
)

# --- review pool: a code exercise -------------------------------------------

write(
    "exercises/review-apply-matrix/exercise.yaml",
    '''id: review-apply-matrix
stage: review_code
rev: 1
title: "Apply the swap"
prompt: |
  `M` swaps the two coordinates of any vector. Write `apply(M, v)` that returns `M @ v`, and print it for `[3, 4]`:

  ```
  [4. 3.]
  ```

  Keep the starter's `M`: the checks use other vectors and another matrix.
skills: [apply]
''',
)
write("exercises/review-apply-matrix/starter.py", "import numpy as np\n\nM = np.array([[0.0, 1.0], [1.0, 0.0]])\n")
write(
    "exercises/review-apply-matrix/solution.py",
    '''import numpy as np

M = np.array([[0.0, 1.0], [1.0, 0.0]])


def apply(M, v):
    return M @ v


print(apply(M, np.array([3.0, 4.0])))
''',
)
write(
    "exercises/review-apply-matrix/test_exercise.py",
    '''import numpy as np

from checks import function, run


def test_the_output():
    """Prints [4. 3.]."""
    assert run() == "[4. 3.]\\n"


def test_other_matrix():
    """A stretch by 2 along x sends [1, 1] to [2, 1]."""
    apply = function("apply")
    assert apply(np.array([[2.0, 0.0], [0.0, 1.0]]), np.array([1.0, 1.0])).tolist() == [2.0, 1.0]
''',
)
write(
    "exercises/review-apply-matrix/wrong/elementwise.py",
    '''import numpy as np

M = np.array([[0.0, 1.0], [1.0, 0.0]])


def apply(M, v):
    return (M * v).sum(axis=0)


print(apply(M, np.array([3.0, 4.0])))
''',
)
write(
    "exercises/review-apply-matrix/wrong/typed-in.py",
    '''import numpy as np

M = np.array([[0.0, 1.0], [1.0, 0.0]])


def apply(M, v):
    return np.array([4.0, 3.0])


print("[4. 3.]")
''',
)

print("ml.la.matrices-as-maps written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
