"""Writes ml.m3.checkpoint, "Checkpoint 3: fit and compress", which closes the
ML track's Module 3. Run from the repository root. Files are written as bytes
with LF endings."""

import pathlib

ROOT = pathlib.Path("content/topics/ml.m3.checkpoint")


def write(relative: str, text: str) -> None:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


MAIN = '''points = np.array([
    [0.0, 0.0, 3.1],
    [1.0, 0.0, 4.9],
    [0.0, 1.0, 2.05],
    [2.0, 3.0, 3.95],
    [3.0, 1.0, 8.1],
    [1.0, 2.0, 2.9],
])
'''
HEIGHTS = '''points = np.array([
    [160.0, 30.0, 26.2],
    [170.0, 40.0, 32.8],
    [180.0, 25.0, 35.1],
    [165.0, 50.0, 32.4],
    [175.0, 35.0, 34.6],
    [185.0, 45.0, 41.3],
])
'''
SENSORS = '''points = np.array([
    [1.0, 2.0, 4.6],
    [2.0, 1.0, 5.4],
    [3.0, 4.0, 8.4],
    [4.0, 2.0, 9.1],
    [5.0, 5.0, 11.9],
    [6.0, 3.0, 12.6],
])
'''
EXACT = "np.array([[0.0, 0.0, 3.0], [1.0, 0.0, 5.0], [0.0, 1.0, 2.0], [2.0, 3.0, 4.0], [3.0, 1.0, 8.0], [1.0, 2.0, 3.0]])"

FUNCTIONS = '''def fit_plane(points):
    A = np.column_stack([points[:, 0], points[:, 1], np.ones(len(points))])
    return np.linalg.solve(A.T @ A, A.T @ points[:, 2])


def compress(points, k):
    mean = points.mean(axis=0)
    centered = points - mean
    C = centered.T @ centered / (len(points) - 1)
    values, vectors = np.linalg.eigh(C)
    order = np.argsort(values)[::-1]
    values = values[order]
    components = vectors[:, order[:k]]
    rebuilt = (centered @ components) @ components.T + mean
    return values / values.sum(), rebuilt
'''

REPORT = '''

def report(points):
    coef = fit_plane(points)
    A = np.column_stack([points[:, 0], points[:, 1], np.ones(len(points))])
    print("plane", np.round(coef, 3))
    print("lstsq agrees", np.allclose(coef, np.linalg.lstsq(A, points[:, 2])[0]))
    shares, rebuilt = compress(points, 2)
    print("variance kept", round(float(shares[:2].sum()), 4))
    print("compression error", round(float(np.linalg.norm(points - rebuilt)), 3))
'''


def build_solution(data):
    return "import numpy as np\n\n\n" + FUNCTIONS + REPORT + "\n\n" + data + "report(points)\n"


def build_tests(expected):
    return f'''import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).

EXACT = {EXACT}


def test_the_output():
    """Prints the plane, the lstsq check, the variance kept and the compression error."""
    assert run() == {expected!r}


def test_fit_matches_lstsq():
    """fit_plane agrees with np.linalg.lstsq on other points, and finds an exact plane exactly."""
    fit_plane = function("fit_plane")
    other = np.array([[1.0, 1.0, 2.0], [2.0, 0.0, 7.0], [0.0, 3.0, -1.0], [4.0, 2.0, 9.5], [3.0, 3.0, 5.0]])
    A = np.column_stack([other[:, 0], other[:, 1], np.ones(5)])
    assert np.allclose(fit_plane(other), np.linalg.lstsq(A, other[:, 2])[0])
    assert np.allclose(fit_plane(EXACT), [2.0, -1.0, 3.0])


def test_compress():
    """compress returns shares that sum to 1 in descending order; three components rebuild exactly, two leave an error of sqrt((n - 1) times the smallest eigenvalue)."""
    compress = function("compress")
    other = np.array([[1.0, 1.0, 2.0], [2.0, 0.0, 7.0], [0.0, 3.0, -1.0], [4.0, 2.0, 9.5], [3.0, 3.0, 5.0]])
    shares, rebuilt = compress(other, 3)
    assert abs(shares.sum() - 1) < 1e-9
    assert (np.diff(shares) <= 1e-12).all()
    assert np.allclose(rebuilt, other)
    shares2, rebuilt2 = compress(other, 2)
    values = np.linalg.eigvalsh(np.cov(other, rowvar=False))
    assert abs(np.linalg.norm(other - rebuilt2) ** 2 - 4 * values[0]) < 1e-9


def test_exact_plane():
    """Points exactly on a plane: two components keep all the variance and rebuild them exactly."""
    compress = function("compress")
    shares, rebuilt = compress(EXACT, 2)
    assert abs(shares[:2].sum() - 1) < 1e-9
    assert np.allclose(rebuilt, EXACT)
'''


BUILD_TEST_SKILLS = '''# Every test names the module skills it checks (ADR-0012), so a failed test
# says which topics to revisit.
test_skills:
  test_the_output: [ml.la.least-squares/normal, ml.la.pca/explained, ml.la.numpy-arrays/vectorize]
  test_fit_matches_lstsq: [ml.la.least-squares/lstsq, ml.la.least-squares/design, ml.la.systems/solve]
  test_compress: [ml.la.pca/components, ml.la.pca/project, ml.la.eigen/compute]
  test_exact_plane: [ml.la.least-squares/meaning, ml.la.pca/covariance]
'''


def write_build(folder, title, opening, data, expected, what_z):
    prompt = f'''  {opening}

  **The points.** Six samples with three measurements each, as rows:

  ```python
{"".join("  " + line + chr(10) for line in data.strip().splitlines())}  ```

  **Fit a plane.** `fit_plane(points)` treats the third column as the target, {what_z}: it builds the design matrix (the first two columns and a column of ones), solves the normal equations `AᵀA x = Aᵀz`, and returns `[a, b, c]` for `z ≈ a x + b y + c`.

  **Compress.** `compress(points, k)` runs PCA on all three columns: center, covariance with `n - 1`, `np.linalg.eigh`, components ordered by eigenvalue (largest first), scores along the top `k`, and the points rebuilt from those scores. It returns two things: every component's share of the variance (largest first), and the rebuilt points.

  **Report.** `report(points)` prints four lines: the plane's coefficients rounded to 3 places; whether `np.linalg.lstsq` agrees with them (`np.allclose`); the share of variance the top two components keep, rounded to 4; and the size of the compression error with two components, `np.linalg.norm(points - rebuilt)`, rounded to 3. Then call it on the points:

  ```
{"".join("  " + line + chr(10) for line in expected.strip().splitlines())}  ```

  The checks call your functions with other points, including points that lie exactly on a plane.
'''
    write(
        f"exercises/{folder}/exercise.yaml",
        f'''id: {folder}
stage: build
rev: 1
title: "{title}"
prompt: |
{prompt}{BUILD_TEST_SKILLS}''',
    )
    write(f"exercises/{folder}/starter.py", "")
    write(f"exercises/{folder}/solution.py", build_solution(data))
    write(f"exercises/{folder}/test_exercise.py", build_tests(expected))
    write(
        f"exercises/{folder}/wrong/no-intercept.py",
        build_solution(data).replace(
            "    A = np.column_stack([points[:, 0], points[:, 1], np.ones(len(points))])\n    return",
            "    A = np.column_stack([points[:, 0], points[:, 1]])\n    return",
        ),
    )
    write(
        f"exercises/{folder}/wrong/uncentered-pca.py",
        build_solution(data).replace(
            "    C = centered.T @ centered / (len(points) - 1)",
            "    C = points.T @ points / (len(points) - 1)",
        ),
    )
    write(
        f"exercises/{folder}/wrong/typed-in.py",
        "import numpy as np\n\n\n"
        + "def fit_plane(points):\n    return np.array([2.0, -1.0, 3.0])\n\n\n"
        + "def compress(points, k):\n    return np.array([1.0, 0.0, 0.0]), points\n\n\n"
        + "".join(f'print("{line}")\n' for line in expected.strip().splitlines()),
    )


MAIN_EXPECTED = "plane [ 2.015 -1.035  3.024]\nlstsq agrees True\nvariance kept 0.9998\ncompression error 0.079\n"

# --- topic ---------------------------------------------------------------------

write(
    "topic.yaml",
    '''id: ml.m3.checkpoint
kind: checkpoint
status: ready
title: "Checkpoint 3: fit and compress"
summary: "Fit a plane to points with least squares, then find the directions the same points vary most along with PCA."
prerequisites: [ml.la.least-squares, ml.la.eigen, ml.la.pca]
estimated_minutes: 120
packages: [numpy]
rev: 1
objectives:
  - "Fit a plane to points with the normal equations, and check it against np.linalg.lstsq."
  - "Reduce the same points to their top principal components and report the variance kept."
  - "Find and fix three bugs in a matrix program: a shape mismatch, a transposed multiply and an uncentered covariance."
  - "Explain why the normal equations give the least-squares fit, and what the top eigenvector of a covariance matrix means."
prove:
  build: build-fit-and-compress
  debug: debug-matrix-report
  explain:
    prompt: |
      Your checkpoint program did Module 3 in one go: it fitted a plane to some points, and it compressed the same points with PCA. In your own words: why do the normal equations `AᵀA x = Aᵀz` give the least-squares plane, and what is perpendicular to what when they hold? What does the top eigenvector of the covariance matrix mean for the points, and why is the direction of most spread an eigenvector at all? The fitted plane and PCA's plane through the same points are not the same plane: what does each one make small? And what would change about both if the points lay exactly on a plane?
    rubric:
      - id: normal-equations
        required: true
        description: "The least-squares fit makes the residual z - A x perpendicular to every column of A (the fitted values are the projection of z onto the column space); writing Aᵀ(z - A x) = 0 gives AᵀA x = Aᵀz."
      - id: top-eigenvector
        required: true
        description: "The covariance matrix's top eigenvector is the direction along which the centered points' variance is largest; the variance along a unit direction u is uᵀCu, which is maximized by the eigenvector with the largest eigenvalue, and that eigenvalue is the variance along it."
      - id: two-planes
        required: true
        description: "Least squares minimizes the squared vertical gaps in z (z is special, the target); PCA's plane minimizes the squared perpendicular distances, treating all three coordinates alike, so the two planes differ unless the points are exactly planar."
      - id: exact
        required: false
        description: "On exactly planar points both agree: the residual is zero, lstsq and the normal equations give the exact coefficients, the smallest eigenvalue is zero, two components keep all the variance and rebuild the points exactly."
    model_answer: |
      The fitted plane's predictions A x are a combination of the columns of A, so they live in the plane those columns span inside the six-dimensional space of all possible z vectors. The closest point in that plane to the real z is its projection, and what's left over, the residual z - A x, sticks straight out: it is perpendicular to every column of A. Saying that in symbols is Aᵀ(z - A x) = 0, which rearranges to AᵀA x = Aᵀz, a square system you can solve; that's why solving it gives the least-squares fit. For PCA, the covariance matrix C holds how the centered points spread; the variance along any unit direction u is uᵀCu, and the direction that makes that largest turns out to be the eigenvector of C with the largest eigenvalue, with the variance along it equal to that eigenvalue. So the top eigenvector is the line the cloud is longest along, and the top two span the plane it's flattest around. That plane is not the regression plane. Least squares treats z as the target and minimizes the squared vertical gaps in z only; PCA treats all three coordinates alike and minimizes the squared perpendicular distances to the plane. If the points lay exactly on a plane, the two would agree: the residual would be zero, lstsq and the normal equations would give the exact coefficients, the smallest eigenvalue would be zero, and two components would keep all the variance and rebuild every point exactly.
# For a learner who's stuck on the build (ADR-0012): a solved sibling, the
# build in steps with hints, then fresh versions.
unstuck:
  example: example-fit-and-compress-in-2d
  steps: [step-design-matrix, step-normal-equations, step-covariance, step-components]
  versions: [build-fit-and-compress-heights, build-fit-and-compress-sensors]
''',
)

# --- the build and its fresh versions ----------------------------------------------

write_build(
    "build-fit-and-compress",
    "Fit and compress",
    "Starting from a blank editor, do Module 3 in one program: fit a plane to six points with the normal equations, check it against `lstsq`, then compress the same points with PCA and say how much was kept.",
    MAIN,
    MAIN_EXPECTED,
    "roughly `z = 2x - y + 3` with a little noise",
)
write_build(
    "build-fit-and-compress-heights",
    "Fit and compress: heights, ages and weights",
    "Starting from a blank editor, fit a plane to six people's measurements (height in cm, age in years, weight in kg) with the normal equations, check it against `lstsq`, then compress the same rows with PCA and say how much was kept.",
    HEIGHTS,
    "plane [  0.493   0.186 -58.318]\nlstsq agrees True\nvariance kept 1.0\ncompression error 0.176\n",
    "the weight, which rises with height and age",
)
write_build(
    "build-fit-and-compress-sensors",
    "Fit and compress: three sensors",
    "Starting from a blank editor, fit a plane to six readings from three sensors with the normal equations, check it against `lstsq`, then compress the same readings with PCA and say how much was kept.",
    SENSORS,
    "plane [1.525 0.455 2.04 ]\nlstsq agrees True\nvariance kept 0.9998\ncompression error 0.112\n",
    "the third sensor, which tracks the other two (roughly `z = 1.5x + 0.5y + 2`)",
)

# --- the debug -----------------------------------------------------------------------

write(
    "exercises/debug-matrix-report/exercise.yaml",
    f'''id: debug-matrix-report
stage: debug
rev: 1
title: "Three bugs in a matrix program"
prompt: |
  This is the checkpoint's program, and it should print:

  ```
{"".join("  " + line + chr(10) for line in MAIN_EXPECTED.strip().splitlines())}  ```

  It has three bugs, in three different places, and each hides the next. Run it and read each error: the first is a **shape mismatch** when the design matrix is built (how many ones?); the second is a **transposed multiply** in the normal equations (which product is square?); and once both are fixed the program runs but the variance kept is wrong, because the covariance is computed on **uncentered** data.
test_skills:
  test_the_output: [ml.la.numpy-arrays/elementwise, ml.la.least-squares/design, ml.la.pca/covariance]
  test_exact_plane: [ml.la.systems/solve, ml.la.pca/explained]
''',
)
DEBUG_SOLUTION = build_solution(MAIN)
write(
    "exercises/debug-matrix-report/starter.py",
    DEBUG_SOLUTION.replace(
        "    A = np.column_stack([points[:, 0], points[:, 1], np.ones(len(points))])\n    return np.linalg.solve(A.T @ A, A.T @ points[:, 2])",
        "    A = np.column_stack([points[:, 0], points[:, 1], np.ones(2)])\n    return np.linalg.solve(A @ A.T, A.T @ points[:, 2])",
    ).replace(
        "    C = centered.T @ centered / (len(points) - 1)",
        "    C = points.T @ points / (len(points) - 1)",
    ),
)
write("exercises/debug-matrix-report/solution.py", DEBUG_SOLUTION)
write(
    "exercises/debug-matrix-report/test_exercise.py",
    f'''import numpy as np

from checks import function, printed, run

EXPECTED = {MAIN_EXPECTED!r}


def test_the_output():
    """Prints the plane, the lstsq check, the variance kept and the compression error."""
    out = run()
    assert out == EXPECTED, f"Expected this:\\n{{EXPECTED}}\\nYour program printed:\\n{{out}}"


def test_exact_plane():
    """On points exactly on a plane: the exact coefficients, all the variance kept, no error."""
    out = printed(function("report"), {EXACT})
    assert out == "plane [ 2. -1.  3.]\\nlstsq agrees True\\nvariance kept 1.0\\ncompression error 0.0\\n", (
        f"For points on the plane z = 2x - y + 3 it printed:\\n{{out}}"
    )
''',
)
write(
    "exercises/debug-matrix-report/wrong/two-of-three.py",
    DEBUG_SOLUTION.replace(
        "    C = centered.T @ centered / (len(points) - 1)",
        "    C = points.T @ points / (len(points) - 1)",
    ),
)
write(
    "exercises/debug-matrix-report/wrong/typed-in.py",
    "import numpy as np\n\n\n"
    + "def report(points):\n"
    + "".join(f'    print("{line}")\n' for line in MAIN_EXPECTED.strip().splitlines())
    + "\n\n"
    + MAIN
    + "report(points)\n",
)

# --- the way through: a solved sibling -------------------------------------------------

write(
    "exercises/example-fit-and-compress-in-2d/exercise.yaml",
    '''id: example-fit-and-compress-in-2d
stage: worked_example
rev: 1
title: "Fit and compress, in two dimensions"
prompt: |
  The checkpoint's two jobs on the six two-dimensional points from the PCA topic: a line fitted with the normal equations, then the same points compressed to one component. Press **Run**, then read how each part works; the checkpoint is this with one more column.
steps:
  - label: "The design matrix and the normal equations"
    lines: "5-8"
    note: "One row per point: its `x` and a 1 for the intercept; the target is the `y` column. `AᵀA x = Aᵀy` is 2 by 2, and `solve` gives the slope and intercept, `[0.8, -0.6]`. With a third column the matrix is 3 by 3 and nothing else changes."
  - label: "How wrong the line is"
    lines: "9"
    note: "The residual, `y - A @ coef`, measures the vertical gaps; its length is 0.894. That's the number least squares made as small as possible."
  - label: "Center, covariance, eigenvectors"
    lines: "11-16"
    note: "PCA treats both columns alike: center, covariance with `n - 1`, `eigh`. The last column is the first component (sign fixed), `[0.772, 0.635]`, and its eigenvalue's share of the total is the variance kept, 98.4 percent."
  - label: "Compress to one number per point, and rebuild"
    lines: "17-19"
    note: "The scores are each point's coordinate along the component; `np.outer` rebuilds the points from them. The rebuild misses by 0.695 in total: the perpendicular spread PCA threw away, smaller than the line's 0.894 because PCA minimizes perpendicular gaps, not vertical ones."
''',
)
write(
    "exercises/example-fit-and-compress-in-2d/solution.py",
    '''import numpy as np

X = np.array([[2.0, 1.0], [3.0, 2.0], [4.0, 2.0], [5.0, 4.0], [6.0, 4.0], [7.0, 5.0]])

A = np.column_stack([X[:, 0], np.ones(6)])
coef = np.linalg.solve(A.T @ A, A.T @ X[:, 1])
print("line", np.round(coef, 3))
print("line residual", round(float(np.linalg.norm(X[:, 1] - A @ coef)), 3))

mean = X.mean(axis=0)
centered = X - mean
C = centered.T @ centered / (len(X) - 1)
values, vectors = np.linalg.eigh(C)
top = vectors[:, -1] * np.sign(vectors[0, -1])
print("top component", np.round(top, 3), "kept", round(float(values[-1] / values.sum()), 4))
scores = centered @ top
rebuilt = np.outer(scores, top) + mean
print("compression error", round(float(np.linalg.norm(X - rebuilt)), 3))
''',
)
write(
    "exercises/example-fit-and-compress-in-2d/test_exercise.py",
    '''from checks import run


def test_the_walkthrough():
    """Prints the line, its residual, the top component with the share kept, and the compression error."""
    assert run() == (
        "line [ 0.8 -0.6]\\nline residual 0.894\\ntop component [0.772 0.635] kept 0.9836\\ncompression error 0.695\\n"
    )
''',
)

# --- the way through: the build in steps ------------------------------------------------

PRELUDE = "import numpy as np\n\n" + MAIN + "\n\n"

write(
    "exercises/step-design-matrix/exercise.yaml",
    '''id: step-design-matrix
stage: fill_in
rev: 1
title: "Step 1: the design matrix"
prompt: |
  The first part of fitting the plane is the design matrix: one row per point, holding its `x`, its `y`, and a 1 for the intercept. Replace the `...` so the program prints the matrix's shape and its first two rows:

  ```
  (6, 3)
  [[0. 0. 1.]
   [1. 0. 1.]]
  ```
hints:
  - "The column of ones needs one entry per point: `np.ones(len(points))`."
''',
)
write(
    "exercises/step-design-matrix/starter.py",
    PRELUDE + '''def design(points):
    return np.column_stack([points[:, 0], points[:, 1], np.ones(...)])


A = design(points)
print(A.shape)
print(A[:2])
''',
)
write(
    "exercises/step-design-matrix/solution.py",
    PRELUDE + '''def design(points):
    return np.column_stack([points[:, 0], points[:, 1], np.ones(len(points))])


A = design(points)
print(A.shape)
print(A[:2])
''',
)
write(
    "exercises/step-design-matrix/test_exercise.py",
    '''import numpy as np

from checks import function, run


def test_the_output():
    """Prints (6, 3) and the first two rows."""
    printed = run()
    assert printed == "(6, 3)\\n[[0. 0. 1.]\\n [1. 0. 1.]]\\n", f"Your program printed:\\n{printed}"


def test_other_points():
    """Four points give a 4-by-3 matrix whose last column is ones."""
    design = function("design")
    A = design(np.array([[1.0, 2.0, 9.0], [3.0, 4.0, 9.0], [5.0, 6.0, 9.0], [7.0, 8.0, 9.0]]))
    assert A.shape == (4, 3)
    assert A[:, 2].tolist() == [1.0, 1.0, 1.0, 1.0]
    assert A[:, 0].tolist() == [1.0, 3.0, 5.0, 7.0]
''',
)
write(
    "exercises/step-design-matrix/wrong/wrong-count.py",
    PRELUDE + '''def design(points):
    return np.column_stack([points[:, 0], points[:, 1], np.ones(len(points) - 0) * 1 + points[:, 2] * 0])


A = design(points)
print(A.shape)
print(A[:1])
''',
)
write(
    "exercises/step-design-matrix/wrong/typed-in.py",
    PRELUDE + '''def design(points):
    return np.array([[0.0, 0.0, 1.0], [1.0, 0.0, 1.0]])


print((6, 3))
print(np.array([[0.0, 0.0, 1.0], [1.0, 0.0, 1.0]]))
''',
)

write(
    "exercises/step-normal-equations/exercise.yaml",
    '''id: step-normal-equations
stage: fill_in
rev: 1
title: "Step 2: the normal equations"
prompt: |
  With the design matrix built, the plane is one `solve` away. Replace each `...` so `fit_plane` solves the normal equations and the program prints:

  ```
  plane [ 2.015 -1.035  3.024]
  ```
hints:
  - "The left side is `A.T @ A`, a 3-by-3 matrix; the right side is `A.T @ z`, three numbers."
  - "`np.linalg.solve(left, right)` returns `[a, b, c]`."
''',
)
write(
    "exercises/step-normal-equations/starter.py",
    PRELUDE + '''def fit_plane(points):
    A = np.column_stack([points[:, 0], points[:, 1], np.ones(len(points))])
    z = points[:, 2]
    return np.linalg.solve(... @ A, A.T @ ...)


print("plane", np.round(fit_plane(points), 3))
''',
)
write(
    "exercises/step-normal-equations/solution.py",
    PRELUDE + '''def fit_plane(points):
    A = np.column_stack([points[:, 0], points[:, 1], np.ones(len(points))])
    z = points[:, 2]
    return np.linalg.solve(A.T @ A, A.T @ z)


print("plane", np.round(fit_plane(points), 3))
''',
)
write(
    "exercises/step-normal-equations/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints the plane's coefficients."""
    printed = run()
    assert printed == "plane [ 2.015 -1.035  3.024]\\n", f"Your program printed:\\n{{printed}}"


def test_exact_plane():
    """Points exactly on z = 2x - y + 3 give [2, -1, 3]."""
    fit_plane = function("fit_plane")
    assert np.allclose(fit_plane({EXACT}), [2.0, -1.0, 3.0])
''',
)
write(
    "exercises/step-normal-equations/wrong/no-transpose.py",
    PRELUDE + '''def fit_plane(points):
    A = np.column_stack([points[:, 0], points[:, 1], np.ones(len(points))])
    z = points[:, 2]
    return np.linalg.lstsq(A, z + 0.5)[0]


print("plane", np.round(fit_plane(points), 3))
''',
)
write(
    "exercises/step-normal-equations/wrong/typed-in.py",
    PRELUDE + '''def fit_plane(points):
    return np.array([2.015, -1.035, 3.024])


print("plane [ 2.015 -1.035  3.024]")
''',
)

write(
    "exercises/step-covariance/exercise.yaml",
    '''id: step-covariance
stage: fill_in
rev: 1
title: "Step 3: the covariance matrix"
prompt: |
  Now the PCA half. Replace each `...` so `covariance` centers the points and builds their covariance matrix, and the program prints it rounded to 3 places:

  ```
  [[ 1.367  0.567  2.167]
   [ 0.567  1.367 -0.273]
   [ 2.167 -0.273  4.656]]
  ```
hints:
  - "Center along `axis=0`: subtract each column's mean from that column."
  - "Divide `centered.T @ centered` by `n - 1`, where `n` is the number of points."
''',
)
write(
    "exercises/step-covariance/starter.py",
    PRELUDE + '''def covariance(points):
    centered = points - points.mean(axis=...)
    return centered.T @ centered / (len(points) - ...)


print(np.round(covariance(points), 3))
''',
)
write(
    "exercises/step-covariance/solution.py",
    PRELUDE + '''def covariance(points):
    centered = points - points.mean(axis=0)
    return centered.T @ centered / (len(points) - 1)


print(np.round(covariance(points), 3))
''',
)
write(
    "exercises/step-covariance/test_exercise.py",
    '''import numpy as np

from checks import function, run


def test_the_output():
    """Prints the 3-by-3 covariance matrix."""
    printed = run()
    assert printed == "[[ 1.367  0.567  2.167]\\n [ 0.567  1.367 -0.273]\\n [ 2.167 -0.273  4.656]]\\n", (
        f"Your program printed:\\n{printed}"
    )


def test_matches_np_cov():
    """Agrees with np.cov on other points."""
    covariance = function("covariance")
    other = np.array([[1.0, 2.0, 0.0], [3.0, 1.0, 4.0], [2.0, 5.0, 1.0], [0.0, 2.0, 2.0]])
    assert np.allclose(covariance(other), np.cov(other, rowvar=False))
''',
)
write(
    "exercises/step-covariance/wrong/divides-by-n.py",
    PRELUDE + '''def covariance(points):
    centered = points - points.mean(axis=0)
    return centered.T @ centered / (len(points) - 0)


print(np.round(covariance(points), 3))
''',
)
write(
    "exercises/step-covariance/wrong/typed-in.py",
    PRELUDE + '''def covariance(points):
    return np.array([[1.367, 0.567, 2.167], [0.567, 1.367, -0.273], [2.167, -0.273, 4.656]])


print("[[ 1.367  0.567  2.167]")
print(" [ 0.567  1.367 -0.273]")
print(" [ 2.167 -0.273  4.656]]")
''',
)

write(
    "exercises/step-components/exercise.yaml",
    '''id: step-components
stage: fill_in
rev: 1
title: "Step 4: the components' shares"
prompt: |
  The last piece before the full build: the share of variance each component carries, largest first. Replace each `...` so the program prints:

  ```
  [0.776 0.224 0.   ]
  ```

  (The third share is 0.0002 before rounding: the points nearly lie in a plane.)
hints:
  - "`eigvalsh` returns the eigenvalues ascending; `[::-1]` reverses them."
  - "Each share is an eigenvalue over `values.sum()`."
''',
)
write(
    "exercises/step-components/starter.py",
    PRELUDE + '''def shares(points):
    centered = points - points.mean(axis=0)
    C = centered.T @ centered / (len(points) - 1)
    values = np.linalg.eigvalsh(C)[...]
    return values / ...


print(np.round(shares(points), 3))
''',
)
write(
    "exercises/step-components/solution.py",
    PRELUDE + '''def shares(points):
    centered = points - points.mean(axis=0)
    C = centered.T @ centered / (len(points) - 1)
    values = np.linalg.eigvalsh(C)[::-1]
    return values / values.sum()


print(np.round(shares(points), 3))
''',
)
write(
    "exercises/step-components/test_exercise.py",
    '''import numpy as np

from checks import function, run


def test_the_output():
    """Prints [0.776 0.224 0.   ]."""
    printed = run()
    assert printed == "[0.776 0.224 0.   ]\\n", f"Your program printed:\\n{printed}"


def test_shares_sum_to_one_descending():
    """For other points the shares are the covariance's eigenvalues over their total, largest first."""
    shares = function("shares")
    other = np.array([[1.0, 2.0, 0.0], [3.0, 1.0, 4.0], [2.0, 5.0, 1.0], [0.0, 2.0, 2.0]])
    s = shares(other)
    values = np.linalg.eigvalsh(np.cov(other, rowvar=False))[::-1]
    assert np.allclose(s, values / values.sum())
    assert abs(s.sum() - 1) < 1e-9
''',
)
write(
    "exercises/step-components/wrong/ascending.py",
    PRELUDE + '''def shares(points):
    centered = points - points.mean(axis=0)
    C = centered.T @ centered / (len(points) - 1)
    values = np.linalg.eigvalsh(C)[::1]
    return values / values.sum()


print(np.round(shares(points), 3))
''',
)
write(
    "exercises/step-components/wrong/typed-in.py",
    PRELUDE + '''def shares(points):
    return np.array([0.776, 0.224, 0.0])


print("[0.776 0.224 0.   ]")
''',
)

print("ml.m3.checkpoint written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
