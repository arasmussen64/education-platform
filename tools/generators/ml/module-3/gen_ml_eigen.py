"""Writes the topic ml.la.eigen (Module 3's sixth topic). Run from the
repository root. Files are written as bytes with LF endings.

Eigenvector signs and the order of eig()'s results differ between LAPACK
builds (the browser's and CPython's), so every printed result here is made
deterministic: eigh for symmetric matrices (ascending order), signs fixed
by hand, complex values sorted, and booleans where a vector would differ."""

import pathlib

ROOT = pathlib.Path("content/topics/ml.la.eigen")


def write(relative: str, text: str) -> None:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


write(
    "topic.yaml",
    '''id: ml.la.eigen
kind: topic
status: ready
title: "Eigenvalues and eigenvectors"
summary: "The directions a matrix only stretches, found with np.linalg.eig, and what they say about repeated transformations."
prerequisites: [ml.la.matrices-as-maps]
packages: [numpy]
estimated_minutes: 55
rev: 1
objectives:
  - "Say what an eigenvector and its eigenvalue are, and check a pair by multiplying."
  - "Find them with np.linalg.eig, and read complex ones as rotation."
  - "Predict what applying a matrix many times does from its eigenvalues."
  - "Diagonalize a matrix and say what that buys."
# Linked, never copied or embedded: 3Blue1Brown's videos are under the
# standard YouTube licence; NumPy's documentation under the NumPy licence
# (BSD-3-Clause).
resources:
  - title: "Essence of linear algebra, chapter 14: Eigenvectors and eigenvalues (3Blue1Brown, Grant Sanderson)"
    url: https://www.youtube.com/watch?v=PFDu9oVAE-g
    type: video
    use: link
    license: Standard YouTube licence (linked, not embedded)
  - title: "numpy.linalg.eig and eigh (the NumPy developers)"
    url: https://numpy.org/doc/stable/reference/generated/numpy.linalg.eig.html
    type: reading
    use: link
    license: BSD-3-Clause (NumPy documentation)
practice:
  - example-stretch-directions
  - parsons-check-an-eigenpair
  - mcq-what-an-eigenvector-is
  - predict-diagonal-eigen
  - mcq-powers
  - fill-power-iteration
  - mcq-complex-means-rotation
  - write-diagonalize
prove:
  build: build-steady-state
  debug: debug-eigen-check
  explain:
    prompt: |
      A colleague hears "eigen" and glazes over. In your own words, using the picture of a matrix moving the grid: what is an eigenvector, and what is its eigenvalue? What happens when you apply the same matrix over and over to a vector, and why does the largest eigenvalue end up in charge? What does it mean when a real 2-by-2 matrix has complex eigenvalues? And what does writing a matrix as `P D P⁻¹` buy you?
    rubric:
      - id: definition
        required: true
        description: "An eigenvector is a direction the matrix only stretches or flips, never turns; the eigenvalue is the stretch factor, negative for a flip, so A v = λ v."
      - id: powers
        required: true
        description: "Any vector is a mix of eigenvectors; each application multiplies each part by its eigenvalue, so after many steps the part with the largest |λ| dominates and the vector lines up with that eigenvector, growing or shrinking by that factor each step."
      - id: complex
        required: true
        description: "Complex eigenvalues of a real 2-by-2 matrix mean no real direction is kept: the matrix rotates (possibly while scaling), like the 90-degree rotation whose eigenvalues are i and -i."
      - id: diagonalize
        required: false
        description: "P holds the eigenvectors and D the eigenvalues; in the eigenvector basis the matrix is just stretching, so powers are P Dᵏ P⁻¹, cheap to compute and easy to reason about."
    model_answer: |
      When a matrix moves the grid, most vectors get turned as well as stretched. An eigenvector is one that doesn't turn: the matrix only stretches it, or flips it, so it ends up on the same line it started on. The eigenvalue is how much: A v = λ v, with λ = 2 meaning doubled and λ = -1 meaning flipped. Apply the matrix over and over and the eigenvectors explain what happens. Any starting vector is a mix of them, each application multiplies each part by its own eigenvalue, so after many steps the part with the biggest eigenvalue has grown the most and the vector points almost exactly along that eigenvector, growing or shrinking by that factor each time; that's why power iteration finds it. If a real 2-by-2 matrix has complex eigenvalues, no real direction is kept at all: the matrix turns everything, like the 90-degree rotation, whose eigenvalues are i and -i. Writing A as P D P⁻¹ means: change into the eigenvector basis (P⁻¹), where the matrix is just the stretches D, then change back (P). Powers become P Dᵏ P⁻¹, which is k-th powers of numbers instead of k matrix multiplications, and it makes the long-run behaviour readable straight off the diagonal.
review_pool:
  - review-predict-eigvalsh
  - review-mcq-identity-eigen
  - review-mcq-determinant-and-eigen
  - review-check-pair
# What this topic teaches. Each question names the skills it tests, so a
# missed question can come back as a different one on the same skill
# (ADR-0011).
skills:
  - id: define
    description: "Say what an eigenpair is, and check one by multiplying"
  - id: compute
    description: "Find eigenvalues and eigenvectors with eig and eigh, and read complex ones as rotation"
  - id: powers
    description: "Predict repeated application from the eigenvalues, and find the top eigenvector by power iteration"
  - id: diagonalize
    description: "Diagonalize a matrix as P D P⁻¹ and use it for powers and steady states"
''',
)

write(
    "lesson.mdx",
    '''<Intro>

A matrix moves the grid, and most arrows get turned as well as stretched. A few don't: they stay on their own line and are only stretched, and those special directions, with their stretch factors, tell you almost everything about what the matrix does when it's applied again and again. They're the eigenvectors and eigenvalues, and they're what PCA, Markov chains, Google's PageRank and the stability of every training loop are made of.

The main resource is **3Blue1Brown's chapter 14**, eigenvectors and eigenvalues: 17 minutes, and the picture you need. Watch for:

- **An eigenvector stays on its line;** the eigenvalue is how much it's stretched (negative means flipped).
- **Rotations have no real eigenvectors,** and the algebra says so with complex numbers.
- **In the eigenvector basis the matrix is diagonal:** just stretching.

Two notes about the code: `np.linalg.eigh` is for symmetric matrices and returns its eigenvalues in ascending order; `np.linalg.eig` works for any square matrix and returns them in no promised order, with eigenvectors scaled to length 1 whose signs can differ between machines. The exercises are written so that neither bites.

</Intro>

<Resource index={0} />

<Recap>

- **The definition.** `v` is an eigenvector of `A` with eigenvalue `λ` when `A @ v == λ * v` (allowing rounding: `np.allclose`): the matrix stretches `v` by `λ` and doesn't turn it. Any multiple of `v` is an eigenvector too; NumPy returns them with length 1.
- **Finding them.** `np.linalg.eig(A)` returns `(values, vectors)`, with the eigenvectors as the **columns** of `vectors`: `vectors[:, i]` goes with `values[i]`. For a symmetric matrix use `np.linalg.eigh`: real values in ascending order, eigenvectors at right angles to each other. `eigvals` and `eigvalsh` give the values alone.
- **Repeated application.** Write a vector as a mix of eigenvectors; each application multiplies each part by its eigenvalue. The part with the largest `|λ|` wins, so `A @ A @ ... @ x` lines up with that eigenvector and grows (or shrinks) by `λ` per step. **Power iteration** (apply, renormalize, repeat) finds the top eigenvector that way; `x @ A @ x` for a unit `x` is then the eigenvalue.
- **Complex eigenvalues** of a real matrix mean rotation: no real direction survives. The 90-degree rotation has eigenvalues `i` and `-i`.
- **Diagonalizing.** `A = P @ D @ inv(P)` with the eigenvectors in `P`'s columns and the eigenvalues on `D`'s diagonal. Powers become `P @ D**k @ inv(P)`; the determinant is the product of the eigenvalues; a zero eigenvalue means a squashed direction and no inverse.
- **Steady states.** A transition matrix (columns summing to 1) has eigenvalue 1; its eigenvector, scaled to sum to 1, is where the system settles whatever it started from.
- **In machine learning:** PCA, next topic, is the eigenvectors of a covariance matrix; the eigenvalues of a Hessian decide how fast gradient descent can step; PageRank is the top eigenvector of the web's link matrix.

</Recap>
''',
)

# --- practice: recall --------------------------------------------------------

write(
    "recall/parsons-check-an-eigenpair.yaml",
    '''id: parsons-check-an-eigenpair
type: parsons
rev: 1
prompt: |
  Put the lines in order to check that `[0, 1]` is an eigenvector of the diagonal matrix with eigenvalue 3, printing `True`. One line is a decoy that doesn't belong.
lines:
  - 'import numpy as np'
  - 'A = np.array([[2.0, 0.0], [0.0, 3.0]])'
  - 'v = np.array([0.0, 1.0])'
  - 'print(np.allclose(A @ v, 3 * v))'
distractors:
  - 'print(np.allclose(A * v, 3 * v))'
explanation: |
  An eigenpair satisfies `A @ v == λ * v`: the matrix applied to the vector equals the vector scaled. Here `A @ [0, 1]` is `[0, 3]`, three times `[0, 1]`. The decoy uses `*`, elementwise multiplication, which isn't applying the matrix at all.
skills: [define]
''',
)

write(
    "recall/mcq-what-an-eigenvector-is.yaml",
    '''id: mcq-what-an-eigenvector-is
type: mcq
rev: 1
prompt: |
  In the picture of a matrix moving the grid, an eigenvector is…
choices:
  - 'A vector the matrix doesn''t move at all'
  - 'A vector the matrix only stretches or flips, so it stays on its own line; the eigenvalue is the factor'
  - 'The longest vector the matrix produces'
  - 'A column of the matrix'
answer: 1
explanation: |
  Most vectors get turned as well as stretched. An eigenvector keeps its line: `A @ v` is `λ * v`, the same direction (or the opposite, if `λ` is negative), scaled by `λ`. A vector that isn't moved at all is the special case `λ = 1`. The columns of the matrix are where the basis vectors land, which is a different thing.
skills: [define]
''',
)

write(
    "recall/predict-diagonal-eigen.yaml",
    '''id: predict-diagonal-eigen
type: predict_output
rev: 1
prompt: |
  The eigenvalues of a diagonal matrix, and the matrix applied to an axis vector. What does the program print?
code: |
  import numpy as np

  D = np.array([[5.0, 0.0], [0.0, 2.0]])
  print(np.linalg.eigvalsh(D))
  print(D @ np.array([0.0, 1.0]))
expected_output: |
  [2. 5.]
  [0. 2.]
explanation: |
  A diagonal matrix stretches along the axes, so the axes are its eigenvectors and the diagonal entries its eigenvalues: 5 along x, 2 along y. `eigvalsh` (for symmetric matrices) returns them in ascending order, hence `[2. 5.]`. Applying `D` to `[0, 1]` gives `[0, 2]`: the vector doubled, not turned.
skills: [compute, define]
''',
)

write(
    "recall/mcq-powers.yaml",
    '''id: mcq-powers
type: mcq
rev: 1
prompt: |
  `A` has eigenvalues 0.5 and 2, with eigenvectors `u` and `w`. You apply `A` to some vector a hundred times. What do you end up with?
choices:
  - 'Roughly the vector you started with'
  - 'A vector pointing along `w`, about 2¹⁰⁰ times its starting share'
  - 'A vector pointing along `u`'
  - 'The zero vector'
answer: 1
explanation: |
  Split the start into a part along `u` and a part along `w`. Each application halves the first and doubles the second, so after a hundred rounds the `u` part is gone and the `w` part is enormous: the result points along `w`. That's why the largest eigenvalue decides long-run behaviour, and why repeatedly applying a matrix is how power iteration finds its top eigenvector.
skills: [powers]
''',
)

write(
    "recall/mcq-complex-means-rotation.yaml",
    '''id: mcq-complex-means-rotation
type: mcq
rev: 1
prompt: |
  `np.linalg.eigvals` of a real 2-by-2 matrix gives `[0.-1.j 0.+1.j]`. What does the matrix do to the plane?
choices:
  - 'It stretches along two directions'
  - 'It rotates: no real direction is kept, which is what complex eigenvalues of a real matrix mean'
  - 'It squashes the plane onto a line'
  - 'NumPy made a rounding error; eigenvalues are always real'
answer: 1
explanation: |
  A real eigenvector would be a direction the matrix doesn't turn. A rotation turns every direction, so there is none, and the algebra says so by producing complex eigenvalues. `i` and `-i` are exactly the 90-degree rotation's. Symmetric matrices, by contrast, always have real eigenvalues.
skills: [compute]
''',
)

write(
    "recall/review-predict-eigvalsh.yaml",
    '''id: review-predict-eigvalsh
type: predict_output
rev: 1
prompt: |
  The eigenvalues of a symmetric matrix, and their product against the determinant. What does the program print?
code: |
  import numpy as np

  A = np.array([[4.0, 1.0], [1.0, 4.0]])
  values = np.linalg.eigvalsh(A)
  print(values)
  print(round(float(np.prod(values)), 6), round(float(np.linalg.det(A)), 6))
expected_output: |
  [3. 5.]
  15.0 15.0
explanation: |
  `[[4, 1], [1, 4]]` stretches `[1, 1]` by 5 and `[1, -1]` by 3; `eigvalsh` lists them ascending. The determinant is the product of the eigenvalues, 15, because both measure how much area is scaled.
skills: [compute, diagonalize]
''',
)

write(
    "recall/review-mcq-identity-eigen.yaml",
    '''id: review-mcq-identity-eigen
type: mcq
rev: 1
prompt: |
  What are the eigenvectors and eigenvalues of the identity matrix `np.eye(2)`?
choices:
  - 'Only `[1, 0]` and `[0, 1]`, each with eigenvalue 1'
  - 'Every non-zero vector, each with eigenvalue 1'
  - 'None: the identity has no eigenvectors'
  - 'Every non-zero vector, each with eigenvalue 0'
answer: 1
explanation: |
  The identity leaves every vector where it is, so every direction is kept and every stretch factor is 1: `I @ v == 1 * v` for all `v`. `eig` will return two of them (the axes), but any pair of independent directions would do.
skills: [define]
''',
)

write(
    "recall/review-mcq-determinant-and-eigen.yaml",
    '''id: review-mcq-determinant-and-eigen
type: mcq
rev: 1
prompt: |
  One of a matrix's eigenvalues is 0. What follows?
choices:
  - 'The matrix is the zero matrix'
  - 'The determinant is 0: some direction is squashed to nothing, and the matrix has no inverse'
  - 'The matrix is a rotation'
  - 'All its other eigenvalues are 0 too'
answer: 1
explanation: |
  An eigenvalue of 0 means a direction `v` with `A @ v = 0`: the matrix flattens it completely. The determinant is the product of the eigenvalues, so it's 0, which is the same fact said as area, and a matrix that flattens a direction can't be undone. The other eigenvalues can be anything.
skills: [diagonalize]
''',
)

# --- practice: exercises -------------------------------------------------------

write(
    "exercises/example-stretch-directions/exercise.yaml",
    '''id: example-stretch-directions
stage: worked_example
rev: 1
title: "The directions that only stretch"
prompt: |
  This program finds the eigenvectors of a symmetric matrix, checks one, watches repeated application line up with it, and meets a matrix with no real eigenvectors. Press **Run**, then read how each part works.
steps:
  - label: "eigh: values and vectors"
    lines: "3-6"
    note: "`eigh` is for symmetric matrices: eigenvalues in ascending order, `[1, 3]`, and the eigenvectors as the **columns** of the second result. Line 6 fixes each column's sign (first entry positive), because the sign is a free choice that differs between machines."
  - label: "Check a pair"
    lines: "7-9"
    note: "`v` is the second column, for eigenvalue 3. `A @ v` and `3 * v` are the same vector: `A` stretched `v` by 3 without turning it. The axis vector `[1, 0]`, by contrast, is turned to `[2, 1]`."
  - label: "Apply it again and again"
    lines: "11-15"
    note: "Five applications to `[1, 0]` give `[122, 121]`: huge, and almost exactly along `[1, 1]`, the eigenvector with the larger eigenvalue. Each round triples that part and leaves the other alone, so the big one wins."
  - label: "No real eigenvectors"
    lines: "17-18"
    note: "The 90-degree rotation turns every direction, so none is kept, and its eigenvalues come out complex: `i` and `-i`. `sort_complex` puts them in a fixed order; `eig` promises none."
''',
)
write(
    "exercises/example-stretch-directions/solution.py",
    '''import numpy as np

A = np.array([[2.0, 1.0], [1.0, 2.0]])
values, vectors = np.linalg.eigh(A)
print(values)
vectors = vectors * np.sign(vectors[0])
v = vectors[:, 1]
print(np.round(A @ v, 3), np.round(values[1] * v, 3))
print(A @ np.array([1.0, 0.0]))

x = np.array([1.0, 0.0])
for _ in range(5):
    x = A @ x
print(x)
print(np.round(x / np.linalg.norm(x), 3))

R = np.array([[0.0, -1.0], [1.0, 0.0]])
print(np.round(np.sort_complex(np.linalg.eigvals(R)), 6))
''',
)
write(
    "exercises/example-stretch-directions/test_exercise.py",
    '''from checks import run


def test_the_walkthrough():
    """Prints the eigenvalues, a checked pair, a turned vector, five applications, and complex eigenvalues."""
    assert run() == (
        "[1. 3.]\\n[2.121 2.121] [2.121 2.121]\\n[2. 1.]\\n[122. 121.]\\n[0.71  0.704]\\n[0.-1.j 0.+1.j]\\n"
    )
''',
)

write(
    "exercises/fill-power-iteration/exercise.yaml",
    '''id: fill-power-iteration
stage: fill_in
rev: 1
title: "Power iteration"
prompt: |
  Power iteration finds the eigenvector with the largest eigenvalue by applying the matrix again and again and renormalizing each time, so the vector can't blow up. Replace each `...` so the program prints the top eigenvector of `A` and its eigenvalue (the Rayleigh quotient `x @ A @ x` for a unit vector `x`):

  ```
  [0.707 0.707] 3.0
  ```

  The program fails until every `...` is replaced.
hints:
  - "Each round applies the matrix: `x = A @ x`."
  - "Then scales the result back to length 1: `x = x / np.linalg.norm(x)`."
skills: [powers]
''',
)
POWER_TAIL = '''

A = np.array([[2.0, 1.0], [1.0, 2.0]])
x = top_eigenvector(A)
print(np.round(x, 3), round(float(x @ A @ x), 3))
'''
write(
    "exercises/fill-power-iteration/starter.py",
    '''import numpy as np


def top_eigenvector(A, rounds=50):
    x = np.ones(len(A))
    for _ in range(rounds):
        x = A @ ...
        x = x / np.linalg.norm(...)
    return x
''' + POWER_TAIL,
)
write(
    "exercises/fill-power-iteration/solution.py",
    '''import numpy as np


def top_eigenvector(A, rounds=50):
    x = np.ones(len(A))
    for _ in range(rounds):
        x = A @ x
        x = x / np.linalg.norm(x)
    return x
''' + POWER_TAIL,
)
write(
    "exercises/fill-power-iteration/test_exercise.py",
    '''import numpy as np

from checks import function, run


def test_the_output():
    """Prints [0.707 0.707] 3.0."""
    printed = run()
    assert printed == "[0.707 0.707] 3.0\\n", f"Your program printed:\\n{printed}"


def test_another_matrix():
    """Finds the eigenvector for eigenvalue 3 of [[3, 1], [0, 2]], with length 1."""
    top_eigenvector = function("top_eigenvector")
    B = np.array([[3.0, 1.0], [0.0, 2.0]])
    x = top_eigenvector(B)
    assert abs(np.linalg.norm(x) - 1) < 1e-9
    assert np.allclose(B @ x, 3 * x, atol=1e-6)
''',
)
write(
    "exercises/fill-power-iteration/wrong/never-normalizes.py",
    '''import numpy as np


def top_eigenvector(A, rounds=50):
    x = np.ones(len(A))
    for _ in range(rounds):
        x = A @ x
        x = x / np.linalg.norm(np.ones(len(A)))
    return x
''' + POWER_TAIL,
)
write(
    "exercises/fill-power-iteration/wrong/typed-in.py",
    '''import numpy as np


def top_eigenvector(A, rounds=50):
    return np.array([0.7071067811865476, 0.7071067811865476])
''' + POWER_TAIL,
)

write(
    "exercises/write-diagonalize/exercise.yaml",
    '''id: write-diagonalize
stage: write
rev: 1
title: "Diagonalize, then take powers"
prompt: |
  Write `diagonalize(A)`, which returns `(P, D)` with the eigenvectors of `A` as the columns of `P` (straight from `np.linalg.eig`) and the eigenvalues on the diagonal of `D` (`np.diag`), so that `A` equals `P @ D @ inv(P)`. Then write `power(A, k)`, which computes `A` to the power `k` as `P @ D**k @ inv(P)` (raise the diagonal matrix to the power with `np.linalg.matrix_power`). Print two checks for the starter's matrix:

  ```
  True
  True
  ```

  (The first: `P @ D @ inv(P)` rebuilds `A`. The second: `power(A, 4)` matches `np.linalg.matrix_power(A, 4)`.)
hints:
  - "`values, vectors = np.linalg.eig(A)`; `P` is `vectors` and `D` is `np.diag(values)`."
  - "Compare matrices with `np.allclose`, never `==`: the rebuilt `A` is off in the last decimal places."
skills: [diagonalize, compute]
''',
)
STARTER_DIAG = '''import numpy as np

A = np.array([[4.0, 1.0], [2.0, 3.0]])
'''
write("exercises/write-diagonalize/starter.py", STARTER_DIAG)
write(
    "exercises/write-diagonalize/solution.py",
    STARTER_DIAG + '''

def diagonalize(A):
    values, vectors = np.linalg.eig(A)
    return vectors, np.diag(values)


def power(A, k):
    P, D = diagonalize(A)
    return P @ np.linalg.matrix_power(D, k) @ np.linalg.inv(P)


P, D = diagonalize(A)
print(np.allclose(P @ D @ np.linalg.inv(P), A))
print(np.allclose(power(A, 4), np.linalg.matrix_power(A, 4)))
''',
)
write(
    "exercises/write-diagonalize/test_exercise.py",
    '''import numpy as np

from checks import function, run


def test_the_output():
    """Prints True twice."""
    printed = run()
    assert printed == "True\\nTrue\\n", f"Your program printed:\\n{printed}"


def test_another_matrix():
    """D is diagonal, P D inv(P) rebuilds the matrix, and power(A, 3) is right, for a 3-by-3."""
    diagonalize = function("diagonalize")
    power = function("power")
    A = np.array([[2.0, 0.0, 1.0], [0.0, 3.0, 0.0], [1.0, 0.0, 2.0]])
    P, D = diagonalize(A)
    assert np.allclose(D, np.diag(np.diag(D)))
    assert np.allclose(P @ D @ np.linalg.inv(P), A)
    assert np.allclose(power(A, 3), np.linalg.matrix_power(A, 3))
''',
)
write(
    "exercises/write-diagonalize/wrong/rows-not-columns.py",
    STARTER_DIAG + '''

def diagonalize(A):
    values, vectors = np.linalg.eig(A)
    return vectors.T, np.diag(values)


def power(A, k):
    P, D = diagonalize(A)
    return P @ np.linalg.matrix_power(D, k) @ np.linalg.inv(P)


P, D = diagonalize(A)
print(np.allclose(P @ D @ np.linalg.inv(P), A))
print(np.allclose(power(A, 4), np.linalg.matrix_power(A, 4)))
''',
)
write(
    "exercises/write-diagonalize/wrong/typed-in.py",
    STARTER_DIAG + '''

def diagonalize(A):
    return np.eye(2), A


def power(A, k):
    return A


print(True)
print(True)
''',
)

# --- proof ------------------------------------------------------------------

write(
    "exercises/build-steady-state/exercise.yaml",
    '''id: build-steady-state
stage: build
rev: 1
title: "Where it settles"
prompt: |
  Each year 10% of a city's people move to the suburbs and 20% of the suburbs' people move to the city. As a matrix acting on `[city, suburbs]`, that's `T = [[0.9, 0.2], [0.1, 0.8]]`: each column sums to 1, and next year's populations are `T @ this_year`. Starting from a blank editor, write:

  - `after_years(T, start, years)`: the populations after that many years (`np.linalg.matrix_power` helps).
  - `steady_state(T)`: the split the populations settle into whatever they started from. It's the eigenvector of `T` with eigenvalue 1, scaled so its entries sum to 1. Find that eigenvector by looking for the eigenvalue **closest to 1** among `np.linalg.eig`'s results (never assume it comes first), take the real part, and scale.

  Then print, for `T` and a start of 1000 people in the city and none in the suburbs:

  ```
  [900. 100.]
  [676.1 323.9]
  [0.667 0.333]
  ```

  (After one year, rounded to 1 place; after ten; and the steady state, rounded to 3.) The checks use other transition matrices, including a 3-by-3, and confirm `T @ steady == steady`.
skills: [diagonalize, powers, compute]
''',
)
write("exercises/build-steady-state/starter.py", "")
write(
    "exercises/build-steady-state/solution.py",
    '''import numpy as np


def after_years(T, start, years):
    return np.linalg.matrix_power(T, years) @ start


def steady_state(T):
    values, vectors = np.linalg.eig(T)
    i = int(np.argmin(np.abs(values - 1)))
    s = np.real(vectors[:, i])
    return s / s.sum()


T = np.array([[0.9, 0.2], [0.1, 0.8]])
start = np.array([1000.0, 0.0])
print(np.round(after_years(T, start, 1), 1))
print(np.round(after_years(T, start, 10), 1))
print(np.round(steady_state(T), 3))
''',
)
write(
    "exercises/build-steady-state/test_exercise.py",
    '''import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints the populations after one and ten years, then the steady state."""
    assert run() == "[900. 100.]\\n[676.1 323.9]\\n[0.667 0.333]\\n"


def test_after_years():
    """after_years agrees with applying T repeatedly."""
    after_years = function("after_years")
    T = np.array([[0.7, 0.4], [0.3, 0.6]])
    start = np.array([10.0, 20.0])
    by_hand = start.copy()
    for _ in range(7):
        by_hand = T @ by_hand
    assert np.allclose(after_years(T, start, 7), by_hand)


def test_steady_state():
    """The steady state is kept by T, sums to 1, and is right for a 2-by-2 and a 3-by-3."""
    steady_state = function("steady_state")
    T = np.array([[0.7, 0.4], [0.3, 0.6]])
    s = steady_state(T)
    assert np.allclose(T @ s, s)
    assert abs(s.sum() - 1) < 1e-9
    assert np.allclose(s, [4 / 7, 3 / 7])
    T3 = np.array([[0.5, 0.3, 0.2], [0.3, 0.4, 0.3], [0.2, 0.3, 0.5]])
    s3 = steady_state(T3)
    assert np.allclose(T3 @ s3, s3)
    assert abs(s3.sum() - 1) < 1e-9
''',
)
write(
    "exercises/build-steady-state/wrong/uses-rows.py",
    '''import numpy as np


def after_years(T, start, years):
    return np.linalg.matrix_power(T, years) @ start


def steady_state(T):
    values, vectors = np.linalg.eig(T.T)
    i = int(np.argmin(np.abs(values - 1)))
    s = np.real(vectors[:, i])
    return s / s.sum()


T = np.array([[0.9, 0.2], [0.1, 0.8]])
start = np.array([1000.0, 0.0])
print(np.round(after_years(T, start, 1), 1))
print(np.round(after_years(T, start, 10), 1))
print(np.round(steady_state(T), 3))
''',
)
write(
    "exercises/build-steady-state/wrong/no-scaling.py",
    '''import numpy as np


def after_years(T, start, years):
    return np.linalg.matrix_power(T, years) @ start


def steady_state(T):
    values, vectors = np.linalg.eig(T)
    i = int(np.argmin(np.abs(values - 1)))
    return np.abs(np.real(vectors[:, i]))


T = np.array([[0.9, 0.2], [0.1, 0.8]])
start = np.array([1000.0, 0.0])
print(np.round(after_years(T, start, 1), 1))
print(np.round(after_years(T, start, 10), 1))
print(np.round(steady_state(T), 3))
''',
)
write(
    "exercises/build-steady-state/wrong/typed-in.py",
    '''import numpy as np


def after_years(T, start, years):
    return np.array([900.0, 100.0])


def steady_state(T):
    return np.array([2 / 3, 1 / 3])


print("[900. 100.]")
print("[676.1 323.9]")
print("[0.667 0.333]")
''',
)

write(
    "exercises/debug-eigen-check/exercise.yaml",
    '''id: debug-eigen-check
stage: debug
rev: 1
title: "A check that checks the wrong thing"
prompt: |
  `report(A, values, vectors)` is given a matrix and its eigenvalues and eigenvectors (the eigenvectors as the columns of `vectors`, the way `np.linalg.eig` returns them), and should check each pair and print:

  ```
  eigenvalue 2.0 check True
  eigenvalue 3.0 check True
  ```

  It has two bugs. Run it: both checks print `False`. One bug reads the eigenvectors the wrong way round (rows, not columns); the other prints and checks the same eigenvalue twice.
skills: [define, compute]
''',
)
CHECK_TAIL = '''

A = np.array([[2.0, 1.0], [0.0, 3.0]])
values = np.array([2.0, 3.0])
vectors = np.array([[1.0, 1.0], [0.0, 1.0]])
report(A, values, vectors)
'''
write(
    "exercises/debug-eigen-check/starter.py",
    '''import numpy as np


def report(A, values, vectors):
    for i in range(len(values)):
        v = vectors[i]
        ok = bool(np.allclose(A @ v, values[0] * v))
        print("eigenvalue", round(float(values[0]), 6), "check", ok)
''' + CHECK_TAIL,
)
write(
    "exercises/debug-eigen-check/solution.py",
    '''import numpy as np


def report(A, values, vectors):
    for i in range(len(values)):
        v = vectors[:, i]
        ok = bool(np.allclose(A @ v, values[i] * v))
        print("eigenvalue", round(float(values[i]), 6), "check", ok)
''' + CHECK_TAIL,
)
write(
    "exercises/debug-eigen-check/test_exercise.py",
    '''import numpy as np

from checks import function, printed, run

EXPECTED = "eigenvalue 2.0 check True\\neigenvalue 3.0 check True\\n"


def test_the_output():
    """Prints both eigenvalues with a passing check."""
    out = run()
    assert out == EXPECTED, f"Expected this:\\n{EXPECTED}\\nYour program printed:\\n{out}"


def test_a_wrong_pair_is_caught():
    """A wrong eigenvalue is reported as False, and a right one as True, in order."""
    report = function("report")
    A = np.array([[5.0, 0.0], [0.0, 1.0]])
    out = printed(report, A, np.array([5.0, 2.0]), np.eye(2))
    assert out == "eigenvalue 5.0 check True\\neigenvalue 2.0 check False\\n", f"It printed:\\n{out}"
''',
)
write(
    "exercises/debug-eigen-check/wrong/columns-only.py",
    '''import numpy as np


def report(A, values, vectors):
    for i in range(len(values)):
        v = vectors[:, i]
        ok = bool(np.allclose(A @ v, values[0] * v))
        print("eigenvalue", round(float(values[0]), 6), "check", ok)
''' + CHECK_TAIL,
)
write(
    "exercises/debug-eigen-check/wrong/typed-in.py",
    '''import numpy as np


def report(A, values, vectors):
    print("eigenvalue 2.0 check True")
    print("eigenvalue 3.0 check True")
''' + CHECK_TAIL,
)

# --- review pool: a code exercise -------------------------------------------

write(
    "exercises/review-check-pair/exercise.yaml",
    '''id: review-check-pair
stage: review_code
rev: 1
title: "Is it an eigenpair?"
prompt: |
  Write `is_eigenpair(A, v, lam)`, which returns `True` when `A @ v` equals `lam * v` (allowing rounding), and print it for the three pairs in the starter:

  ```
  True
  True
  False
  ```
skills: [define]
''',
)
STARTER_PAIR = '''import numpy as np

A = np.array([[2.0, 1.0], [1.0, 2.0]])
'''
write("exercises/review-check-pair/starter.py", STARTER_PAIR)
write(
    "exercises/review-check-pair/solution.py",
    STARTER_PAIR + '''

def is_eigenpair(A, v, lam):
    return bool(np.allclose(A @ v, lam * v))


print(is_eigenpair(A, np.array([1.0, 1.0]), 3.0))
print(is_eigenpair(A, np.array([1.0, -1.0]), 1.0))
print(is_eigenpair(A, np.array([1.0, 0.0]), 2.0))
''',
)
write(
    "exercises/review-check-pair/test_exercise.py",
    '''import numpy as np

from checks import function, run


def test_the_output():
    """Prints True, True, False."""
    assert run() == "True\\nTrue\\nFalse\\n"


def test_other_pairs():
    """Works for a diagonal matrix: [0, 1] with 3 is a pair, [1, 1] with 3 is not."""
    is_eigenpair = function("is_eigenpair")
    D = np.array([[2.0, 0.0], [0.0, 3.0]])
    assert is_eigenpair(D, np.array([0.0, 1.0]), 3.0) is True
    assert is_eigenpair(D, np.array([1.0, 1.0]), 3.0) is False
''',
)
write(
    "exercises/review-check-pair/wrong/ignores-lambda.py",
    STARTER_PAIR + '''

def is_eigenpair(A, v, lam):
    return bool(np.allclose(A @ v, v))


print(is_eigenpair(A, np.array([1.0, 1.0]), 3.0))
print(is_eigenpair(A, np.array([1.0, -1.0]), 1.0))
print(is_eigenpair(A, np.array([1.0, 0.0]), 2.0))
''',
)
write(
    "exercises/review-check-pair/wrong/typed-in.py",
    STARTER_PAIR + '''

def is_eigenpair(A, v, lam):
    return True


print(True)
print(True)
print(False)
''',
)

print("ml.la.eigen written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
