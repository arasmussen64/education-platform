"""Writes the topic ml.la.pca (Module 3's seventh and last topic before its
checkpoint). Run from the repository root. Files are written as bytes with
LF endings. Printed vectors have their signs fixed, because an eigenvector's
sign differs between LAPACK builds."""

import pathlib

ROOT = pathlib.Path("content/topics/ml.la.pca")


def write(relative: str, text: str) -> None:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


SIX_POINTS = "X = np.array([[2.0, 1.0], [3.0, 2.0], [4.0, 2.0], [5.0, 4.0], [6.0, 4.0], [7.0, 5.0]])\n"

write(
    "topic.yaml",
    '''id: ml.la.pca
kind: topic
status: ready
title: "PCA: what eigenvalues mean for data"
summary: "Center data, form the covariance matrix, take its eigenvectors as principal components, and project to fewer dimensions."
prerequisites: [ml.la.eigen, ml.la.least-squares, ml.math.probability-and-statistics]
packages: [numpy]
estimated_minutes: 60
rev: 1
objectives:
  - "Center a dataset and compute its covariance matrix."
  - "Find the principal components as the covariance matrix's eigenvectors."
  - "Project data onto the top components and read the variance explained."
  - "Say when PCA helps and what it throws away."
# Linked, never copied or embedded: StatQuest's videos are under the standard
# YouTube licence; NumPy's documentation under the NumPy licence
# (BSD-3-Clause).
resources:
  - title: "StatQuest: Principal Component Analysis (PCA), Step-by-Step (Josh Starmer)"
    url: https://www.youtube.com/watch?v=FgakZw6K1QQ
    type: video
    use: link
    license: Standard YouTube licence (linked, not embedded)
  - title: "numpy.cov (the NumPy developers)"
    url: https://numpy.org/doc/stable/reference/generated/numpy.cov.html
    type: reading
    use: link
    license: BSD-3-Clause (NumPy documentation)
practice:
  - example-the-direction-of-most-spread
  - parsons-covariance
  - mcq-what-pca-finds
  - predict-explained-share
  - mcq-why-center
  - fill-explained-variance
  - mcq-when-pca-helps
  - write-first-component
prove:
  build: build-pca
  debug: debug-pca-mistakes
  explain:
    prompt: |
      A teammate has fifty correlated sensor readings per sample and a model that overfits. They've heard PCA might help. In your own words: what does the covariance matrix hold, and why are its eigenvectors the directions the data spreads most along? What does projecting onto the top few components keep, and what does it throw away? How would you read "variance explained" to choose how many components to keep? And when is PCA the wrong tool?
    rubric:
      - id: covariance
        required: true
        description: "After centering, the covariance matrix holds each feature's variance on the diagonal and how pairs move together off it; its eigenvectors are the directions along which the centered data's spread is largest, at right angles to each other, with the eigenvalues as the variances along them."
      - id: projection
        required: true
        description: "Projecting onto the top k components keeps the coordinates along the k directions of most spread and discards the rest; the discarded part is the reconstruction error, small when the data nearly lies in a k-dimensional subspace."
      - id: explained
        required: true
        description: "Each eigenvalue over the total is that component's share of the variance; keep components until the running total is high enough (say 90 to 99 percent) or the shares drop to noise."
      - id: limits
        required: false
        description: "PCA is wrong when the useful signal has small variance, when the data isn't numeric and centred-scale meaningful, when features aren't on comparable scales (standardize first), or when the components must be interpretable."
    model_answer: |
      Center the readings first, so every feature has mean zero. The covariance matrix then holds, on its diagonal, how much each sensor varies, and off the diagonal, how much each pair moves together. It's symmetric, so its eigenvectors are at right angles and its eigenvalues are real, and along each eigenvector the data's variance is exactly that eigenvalue. The eigenvector with the largest eigenvalue is therefore the single direction the cloud spreads most along, the next one is the direction of most spread at right angles to it, and so on: the principal components. Projecting each sample onto the top k components keeps its coordinates along those k directions and throws away the coordinates along the rest. What's thrown away is the reconstruction error, and it's small when the fifty readings mostly move together, which correlated sensors do. Variance explained is each eigenvalue divided by their total: read the running sum and keep components until it reaches something like 95 percent, or until the remaining shares are the size of noise. PCA is the wrong tool when the signal you care about is a small-variance direction, when the features are on different scales and you haven't standardized them, when the data isn't numbers you can average, or when you need the components to mean something a person can name.
review_pool:
  - review-predict-centered-mean
  - review-mcq-explained-ratio
  - review-mcq-component-order
  - review-predict-reconstruct
  - review-top-share
# What this topic teaches. Each question names the skills it tests, so a
# missed question can come back as a different one on the same skill
# (ADR-0011).
skills:
  - id: covariance
    description: "Center data and compute its covariance matrix"
  - id: components
    description: "Take the principal components from the covariance matrix's eigenvectors, in order of eigenvalue"
  - id: project
    description: "Project data onto the top components and reconstruct it"
  - id: explained
    description: "Read the variance explained, choose how many components to keep, and say what PCA throws away"
''',
)

write(
    "lesson.mdx",
    '''<Intro>

Eigenvectors were the directions a matrix only stretches. Point them at data and they become the directions the data spreads most along: center the points, build the covariance matrix, and its eigenvectors are the principal components, with the eigenvalues saying how much of the spread each one carries. Keep the first few and you've compressed the data to the directions that matter.

The main resource is **StatQuest's PCA step by step**, 20 minutes, which draws every step of this on two and three features. Then NumPy's `cov` page, mostly for the `rowvar=False` convention. Watch for:

- **Centering first:** without it, the first "component" points at the mean, not the spread.
- **The covariance matrix** of centered data: variances on the diagonal, how pairs move together off it.
- **Eigenvalues as variances** along each component, and their shares as "variance explained".

</Intro>

<Resource index={0} />

<Recap>

- **Center:** `centered = X - X.mean(axis=0)`, one feature per column, one sample per row.
- **Covariance matrix:** `C = centered.T @ centered / (n - 1)`, the same as `np.cov(X, rowvar=False)`. Symmetric; `C[i, j]` is how features `i` and `j` move together, `C[i, i]` feature `i`'s variance.
- **Components:** `values, vectors = np.linalg.eigh(C)`. The eigenvectors (columns of `vectors`) are the principal components, at right angles to each other; the eigenvalues are the variances along them. `eigh` lists them **ascending**, so the first component is the **last** column: `vectors[:, -1]`, or reverse the order with `[::-1]`.
- **Signs are arbitrary.** An eigenvector and its negative are the same direction; fix a sign convention (first entry positive) before comparing or printing.
- **Scores:** `centered @ components` gives each sample's coordinates along the kept directions. **Reconstruct** with `scores @ components.T + mean`; with all components it's exact, with fewer it's the best approximation of that rank.
- **Variance explained:** `values / values.sum()`, largest first; the running sum says how much of the spread `k` components keep. Choose `k` where it crosses a threshold you can defend (90, 95, 99 percent) or where the shares drop to noise.
- **Standardize first** when features have different units, or the one with the biggest numbers becomes the first component for no reason.
- **What it throws away:** the low-variance directions, which is fine for noise and wrong when the signal you need is small. Components are mixes of features and rarely mean anything by name.
- **In machine learning:** PCA is the standard first look at a high-dimensional dataset, a compression step before a model, and the picture behind "embeddings have a few directions that matter".

</Recap>
''',
)

# --- practice: recall --------------------------------------------------------

write(
    "recall/parsons-covariance.yaml",
    '''id: parsons-covariance
type: parsons
rev: 1
prompt: |
  Put the lines in order to compute the covariance matrix of four points (the corners of a 2-by-1 rectangle) and print:

  ```
  [[1.3333 0.    ]
   [0.     0.3333]]
  ```

  One line is a decoy that doesn't belong.
lines:
  - 'import numpy as np'
  - 'X = np.array([[0.0, 0.0], [2.0, 0.0], [0.0, 1.0], [2.0, 1.0]])'
  - 'centered = X - X.mean(axis=0)'
  - 'C = centered.T @ centered / (len(X) - 1)'
  - 'print(np.round(C, 4))'
distractors:
  - 'C = X.T @ X / (len(X) - 1)'
explanation: |
  Covariance is about spread around the mean, so the data is centered first; the decoy skips that and measures spread around the origin instead. The rectangle is twice as wide as it is tall, the features don't move together, so the matrix is diagonal with the x-variance four times the y-variance.
skills: [covariance]
''',
)

write(
    "recall/mcq-what-pca-finds.yaml",
    '''id: mcq-what-pca-finds
type: mcq
rev: 1
prompt: |
  What is the first principal component of a dataset?
choices:
  - 'The feature with the largest values'
  - 'The direction (a unit vector, usually a mix of features) along which the centered data has the largest variance'
  - 'The mean of the data'
  - 'The line of best fit through the data, as in least squares'
answer: 1
explanation: |
  PCA looks for directions, not features: the first component is the unit vector along which the centered points spread most, and it's usually a blend of several features. It's close to a line of best fit but not the same thing: least squares minimizes vertical gaps to predict `y`; PCA minimizes perpendicular gaps and treats all features alike.
skills: [components]
''',
)

write(
    "recall/predict-explained-share.yaml",
    '''id: predict-explained-share
type: predict_output
rev: 1
prompt: |
  The eigenvalues of the rectangle's covariance matrix, and the share of the spread the first component explains. What does the program print?
code: |
  import numpy as np

  X = np.array([[0.0, 0.0], [2.0, 0.0], [0.0, 1.0], [2.0, 1.0]])
  centered = X - X.mean(axis=0)
  C = centered.T @ centered / (len(X) - 1)
  values = np.linalg.eigvalsh(C)
  print(np.round(values, 4))
  print(round(float(values[-1] / values.sum()), 3))
expected_output: |
  [0.3333 1.3333]
  0.8
explanation: |
  The covariance matrix is diagonal, so its eigenvalues are the two variances, listed ascending by `eigvalsh`: a third along y, four thirds along x. The first component (the larger, `values[-1]`) carries 4/3 of a total 5/3: 80 percent of the spread.
skills: [explained]
''',
)

write(
    "recall/mcq-why-center.yaml",
    '''id: mcq-why-center
type: mcq
rev: 1
prompt: |
  What goes wrong if you skip centering and compute the "covariance" as `X.T @ X / (n - 1)` on raw data far from the origin?
choices:
  - 'Nothing: centering is only for neatness'
  - 'The first component points from the origin towards the data''s mean, which says nothing about how the points spread'
  - 'The eigenvalues become negative'
  - 'NumPy raises an error'
answer: 1
explanation: |
  Covariance measures spread *around the mean*. Without centering, the biggest "direction" is wherever the cloud sits relative to the origin, so the first component just points at the data, and the shares of variance come out wrong. The debug exercise has exactly this bug.
skills: [covariance]
''',
)

write(
    "recall/mcq-when-pca-helps.yaml",
    '''id: mcq-when-pca-helps
type: mcq
rev: 1
prompt: |
  In which situation is PCA most likely to **lose** what matters?
choices:
  - 'Fifty sensor readings that mostly rise and fall together'
  - 'A dataset where the signal you care about is a small, rare variation and the big variance is routine noise'
  - 'Pixels of images, where neighbouring pixels are strongly correlated'
  - 'Many redundant features that are near copies of each other'
answer: 1
explanation: |
  PCA keeps the directions of **largest** variance and discards the rest. When the important signal is a small variation (a faint fault pattern in a loud machine), it lives in a low-variance direction and is the first thing thrown away. The other three are the cases PCA was made for: correlated or redundant features that a few directions summarize.
skills: [explained]
''',
)

write(
    "recall/review-predict-centered-mean.yaml",
    '''id: review-predict-centered-mean
type: predict_output
rev: 1
prompt: |
  Data centered, and its mean afterwards. What does the program print?
code: |
  import numpy as np

  X = np.array([[1.0, 10.0], [3.0, 30.0], [5.0, 20.0]])
  centered = X - X.mean(axis=0)
  print(centered)
  print(centered.mean(axis=0))
expected_output: |
  [[ -2. -10.]
   [  0.  10.]
   [  2.   0.]]
  [0. 0.]
explanation: |
  The column means are 3 and 20; subtracting them from every row (broadcasting) leaves each column summing to zero, so the centered data's mean is `[0, 0]`. That's the starting point of every covariance matrix.
skills: [covariance]
''',
)

write(
    "recall/review-mcq-explained-ratio.yaml",
    '''id: review-mcq-explained-ratio
type: mcq
rev: 1
prompt: |
  A covariance matrix has eigenvalues 8 and 2. How much of the variance does the first component explain?
choices:
  - '8 percent'
  - '80 percent'
  - '50 percent'
  - '25 percent'
answer: 1
explanation: |
  The eigenvalues are the variances along the components, so the shares are each over the total: 8 of 10 is 80 percent for the first, 20 percent for the second. Keeping only the first component keeps four fifths of the spread.
skills: [explained]
''',
)

write(
    "recall/review-mcq-component-order.yaml",
    '''id: review-mcq-component-order
type: mcq
rev: 1
prompt: |
  `values, vectors = np.linalg.eigh(C)` for a covariance matrix `C`. Which column of `vectors` is the first principal component?
choices:
  - '`vectors[:, 0]`, the first column'
  - '`vectors[:, -1]`, the last column: `eigh` lists eigenvalues in ascending order, so the largest is last'
  - '`vectors[0]`, the first row'
  - 'Whichever has the largest entries'
answer: 1
explanation: |
  `eigh` returns the eigenvalues ascending and the matching eigenvectors as columns in the same order, so the direction of most variance is the last column. Rows aren't eigenvectors at all. Many programs reverse both with `[::-1]` so that index 0 is the first component.
skills: [components]
''',
)

write(
    "recall/review-predict-reconstruct.yaml",
    '''id: review-predict-reconstruct
type: predict_output
rev: 1
prompt: |
  Three points rebuilt from one score each along a component. What does the program print?
code: |
  import numpy as np

  mean = np.array([4.5, 3.0])
  component = np.array([0.6, 0.8])
  scores = np.array([-5.0, 0.0, 5.0])
  print(np.outer(scores, component) + mean)
expected_output: |
  [[ 1.5 -1. ]
   [ 4.5  3. ]
   [ 7.5  7. ]]
explanation: |
  A score is how far along the component a point sits from the mean. `np.outer` turns each score into that many copies of the component (a row per score), and adding the mean puts the points back where they came from: a score of 0 is the mean itself, and the other two are 5 units along the component either way. That's `reconstruct` with one component.
skills: [project]
''',
)

# --- practice: exercises -------------------------------------------------------

write(
    "exercises/example-the-direction-of-most-spread/exercise.yaml",
    '''id: example-the-direction-of-most-spread
stage: worked_example
rev: 1
title: "The direction of most spread"
prompt: |
  Six points that lie roughly along a slanted line. This program centers them, builds the covariance matrix, takes its eigenvectors, projects the points onto the first one, and rebuilds them from that single coordinate. Press **Run**, then read how each part works.
steps:
  - label: "Center the data"
    lines: "3-6"
    note: "Subtract each column's mean, so the cloud sits at the origin. The mean is `[4.5, 3]`; everything that follows is about spread around it."
  - label: "The covariance matrix"
    lines: "7-9"
    note: "`centered.T @ centered / (n - 1)`: variances on the diagonal (3.5 along x, 2.4 along y), and 2.8 off it, because the two features rise together. `np.cov` agrees."
  - label: "Its eigenvectors are the principal components"
    lines: "10-14"
    note: "`eigh` gives the eigenvalues ascending, `[0.096, 5.804]`, so the first component is the **last** column. Its sign is a free choice, fixed here so the first entry is positive: `[0.772, 0.635]`, the slant the points follow."
  - label: "Scores: the data along that direction"
    lines: "15-16"
    note: "Each point's coordinate along the component, from `-3.2` to `3.2`: six numbers instead of six pairs. That's the compression."
  - label: "How much is kept, and what comes back"
    lines: "17-19"
    note: "The first component carries 98.4 percent of the variance. Rebuilding each point from its single score lands within a few hundredths of the original: what's lost is the tiny spread across the line."
''',
)
write(
    "exercises/example-the-direction-of-most-spread/solution.py",
    "import numpy as np\n\n" + SIX_POINTS + '''mean = X.mean(axis=0)
centered = X - mean
print(mean)
C = centered.T @ centered / (len(X) - 1)
print(np.round(C, 3))
print(np.allclose(C, np.cov(X, rowvar=False)))
values, vectors = np.linalg.eigh(C)
print(np.round(values, 3))
top = vectors[:, -1]
top = top * np.sign(top[0])
print(np.round(top, 3))
scores = centered @ top
print(np.round(scores, 3))
print(np.round(values[-1] / values.sum(), 3))
back = np.outer(scores, top) + mean
print(np.round(back, 2))
''',
)
write(
    "exercises/example-the-direction-of-most-spread/test_exercise.py",
    '''from checks import run


def test_the_walkthrough():
    """Prints the mean, the covariance, the eigenvalues, the first component, the scores, the share kept and the rebuilt points."""
    assert run() == (
        "[4.5 3. ]\\n[[3.5 2.8]\\n [2.8 2.4]]\\nTrue\\n[0.096 5.804]\\n[0.772 0.635]\\n"
        "[-3.201 -1.794 -1.021  1.021  1.794  3.201]\\n0.984\\n"
        "[[2.03 0.97]\\n [3.11 1.86]\\n [3.71 2.35]\\n [5.29 3.65]\\n [5.89 4.14]\\n [6.97 5.03]]\\n"
    )
''',
)

write(
    "exercises/fill-explained-variance/exercise.yaml",
    '''id: fill-explained-variance
stage: fill_in
rev: 1
title: "Variance explained"
prompt: |
  `explained(X)` should return each component's share of the variance, largest first, rounded to 3 places. Replace each `...` so the program prints:

  ```
  [0.984 0.016]
  [1. 0.]
  ```

  (The second dataset lies exactly on a line, so one component carries everything.) The program fails until every `...` is replaced.
hints:
  - "Center along `axis=0`: one mean per column (per feature)."
  - "The covariance divides by `n - 1`; the shares divide each eigenvalue by `values.sum()`."
skills: [explained, covariance]
''',
)
EXPL_TAIL = "\n\n" + SIX_POINTS + '''print(explained(X))
print(explained(np.array([[1.0, 1.0], [2.0, 2.0], [3.0, 3.0], [4.0, 4.0]])))
'''
write(
    "exercises/fill-explained-variance/starter.py",
    '''import numpy as np


def explained(X):
    centered = X - X.mean(axis=...)
    C = centered.T @ centered / (len(X) - ...)
    values = np.linalg.eigvalsh(C)[::-1]
    return np.round(values / ..., 3)
''' + EXPL_TAIL,
)
write(
    "exercises/fill-explained-variance/solution.py",
    '''import numpy as np


def explained(X):
    centered = X - X.mean(axis=0)
    C = centered.T @ centered / (len(X) - 1)
    values = np.linalg.eigvalsh(C)[::-1]
    return np.round(values / values.sum(), 3)
''' + EXPL_TAIL,
)
write(
    "exercises/fill-explained-variance/test_exercise.py",
    '''import numpy as np

from checks import function, run


def test_the_output():
    """Prints [0.984 0.016], then [1. 0.]."""
    printed = run()
    assert printed == "[0.984 0.016]\\n[1. 0.]\\n", f"Your program printed:\\n{printed}"


def test_three_features():
    """Data that varies along one axis only puts all the variance in one component."""
    explained = function("explained")
    X = np.array([[1.0, 0.0, 0.0], [2.0, 0.0, 0.0], [3.0, 0.0, 0.0], [4.0, 0.0, 0.0]])
    assert explained(X).tolist() == [1.0, 0.0, 0.0]
''',
)
write(
    "exercises/fill-explained-variance/wrong/no-centering.py",
    '''import numpy as np


def explained(X):
    centered = X - X.mean(axis=0) * 0
    C = centered.T @ centered / (len(X) - 1)
    values = np.linalg.eigvalsh(C)[::-1]
    return np.round(values / values.sum(), 3)
''' + EXPL_TAIL,
)
write(
    "exercises/fill-explained-variance/wrong/typed-in.py",
    '''import numpy as np


def explained(X):
    if len(X) == 6:
        return np.array([0.984, 0.016])
    return np.array([1.0, 0.0])
''' + EXPL_TAIL,
)

write(
    "exercises/write-first-component/exercise.yaml",
    '''id: write-first-component
stage: write
rev: 1
title: "The first component, and the scores"
prompt: |
  Write `first_component(X)`, which returns the first principal component of `X` as a unit vector with its **first entry positive** (multiply by `np.sign` of the first entry), and `scores(X)`, each point's coordinate along it. Print both for the starter's six points, rounded to 3 places:

  ```
  [0.772 0.635]
  [-3.201 -1.794 -1.021  1.021  1.794  3.201]
  ```
hints:
  - "Center, build the covariance matrix, `eigh` it: the first component is the last column, `vectors[:, -1]`."
  - "Fix the sign with `top * np.sign(top[0])`, then the scores are `centered @ top`."
skills: [components, project]
''',
)
write("exercises/write-first-component/starter.py", "import numpy as np\n\n" + SIX_POINTS)
write(
    "exercises/write-first-component/solution.py",
    "import numpy as np\n\n" + SIX_POINTS + '''

def first_component(X):
    centered = X - X.mean(axis=0)
    C = centered.T @ centered / (len(X) - 1)
    values, vectors = np.linalg.eigh(C)
    top = vectors[:, -1]
    return top * np.sign(top[0])


def scores(X):
    return (X - X.mean(axis=0)) @ first_component(X)


print(np.round(first_component(X), 3))
print(np.round(scores(X), 3))
''',
)
write(
    "exercises/write-first-component/test_exercise.py",
    '''import numpy as np

from checks import function, run


def test_the_output():
    """Prints the component, then the scores."""
    printed = run()
    assert printed == "[0.772 0.635]\\n[-3.201 -1.794 -1.021  1.021  1.794  3.201]\\n", f"Your program printed:\\n{printed}"


def test_collinear_points():
    """Points on the line y = x give the component [0.707, 0.707] and scores spaced by the square root of 2."""
    first_component = function("first_component")
    scores = function("scores")
    X = np.array([[1.0, 1.0], [2.0, 2.0], [3.0, 3.0], [4.0, 4.0]])
    assert np.allclose(first_component(X), [2**-0.5, 2**-0.5])
    assert np.allclose(scores(X), np.array([-1.5, -0.5, 0.5, 1.5]) * 2**0.5)
''',
)
write(
    "exercises/write-first-component/wrong/smallest-component.py",
    "import numpy as np\n\n" + SIX_POINTS + '''

def first_component(X):
    centered = X - X.mean(axis=0)
    C = centered.T @ centered / (len(X) - 1)
    values, vectors = np.linalg.eigh(C)
    top = vectors[:, 0]
    return top * np.sign(top[0])


def scores(X):
    return (X - X.mean(axis=0)) @ first_component(X)


print(np.round(first_component(X), 3))
print(np.round(scores(X), 3))
''',
)
write(
    "exercises/write-first-component/wrong/typed-in.py",
    "import numpy as np\n\n" + SIX_POINTS + '''

def first_component(X):
    return np.array([0.772, 0.635])


def scores(X):
    return np.array([-3.201, -1.794, -1.021, 1.021, 1.794, 3.201])


print("[0.772 0.635]")
print("[-3.201 -1.794 -1.021  1.021  1.794  3.201]")
''',
)

# --- proof ------------------------------------------------------------------

write(
    "exercises/build-pca/exercise.yaml",
    '''id: build-pca
stage: build
rev: 1
title: "PCA from scratch"
prompt: |
  Starting from a blank editor, write PCA as two functions.

  - `pca(X, k)` returns three things: the **scores** (each sample's coordinates along the top `k` components, shape `(n, k)`), the **components** as columns (shape `(features, k)`, largest variance first, each with its first entry positive), and **explained**, every component's share of the variance, largest first (all of them, not just `k`).
  - `reconstruct(scores, components, mean)` rebuilds the samples: `scores @ components.T + mean`.

  Center the data, build the covariance matrix with `n - 1`, use `np.linalg.eigh`, and remember it lists eigenvalues ascending. Then, for the six points below with `k = 1`, print the explained shares rounded to 3 places and the size of the reconstruction error, `np.linalg.norm(X - rebuilt)`, rounded to 3:

  ```python
  X = np.array([[2.0, 1.0], [3.0, 2.0], [4.0, 2.0], [5.0, 4.0], [6.0, 4.0], [7.0, 5.0]])
  ```

  ```
  [0.984 0.016]
  0.695
  ```

  The checks run `pca` on three-feature data that lies in a plane (two components rebuild it exactly), check the components are unit vectors at right angles, and check that all the components of 2-D data rebuild it exactly.
skills: [components, project, explained, covariance]
''',
)
write("exercises/build-pca/starter.py", "")
write(
    "exercises/build-pca/solution.py",
    '''import numpy as np


def pca(X, k):
    mean = X.mean(axis=0)
    centered = X - mean
    C = centered.T @ centered / (len(X) - 1)
    values, vectors = np.linalg.eigh(C)
    order = np.argsort(values)[::-1]
    values = values[order]
    components = vectors[:, order[:k]]
    components = components * np.sign(components[0])
    return centered @ components, components, values / values.sum()


def reconstruct(scores, components, mean):
    return scores @ components.T + mean


X = np.array([[2.0, 1.0], [3.0, 2.0], [4.0, 2.0], [5.0, 4.0], [6.0, 4.0], [7.0, 5.0]])
scores, components, explained = pca(X, 1)
print(np.round(explained, 3))
rebuilt = reconstruct(scores, components, X.mean(axis=0))
print(round(float(np.linalg.norm(X - rebuilt)), 3))
''',
)
write(
    "exercises/build-pca/test_exercise.py",
    '''import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).

PLANE = np.array(
    [[1.0, 2.0, 3.0], [2.0, 1.0, 3.0], [3.0, 5.0, 8.0], [4.0, 3.0, 7.0], [5.0, 6.0, 11.0], [6.0, 4.0, 10.0]]
)
SIX = np.array([[2.0, 1.0], [3.0, 2.0], [4.0, 2.0], [5.0, 4.0], [6.0, 4.0], [7.0, 5.0]])


def test_the_output():
    """Prints the explained shares and the reconstruction error."""
    assert run() == "[0.984 0.016]\\n0.695\\n"


def test_data_in_a_plane():
    """Three features that lie in a plane: two components rebuild them exactly, and the third share is zero."""
    pca = function("pca")
    reconstruct = function("reconstruct")
    scores, components, explained = pca(PLANE, 2)
    assert scores.shape == (6, 2) and components.shape == (3, 2)
    assert np.allclose(reconstruct(scores, components, PLANE.mean(axis=0)), PLANE)
    assert np.allclose(np.round(explained, 4), [0.9355, 0.0645, 0.0])
    assert np.allclose(components.T @ components, np.eye(2))


def test_all_components_rebuild_exactly():
    """With every component kept, 2-D data comes back exactly, and the components have positive first entries."""
    pca = function("pca")
    reconstruct = function("reconstruct")
    scores, components, explained = pca(SIX, 2)
    assert np.allclose(reconstruct(scores, components, SIX.mean(axis=0)), SIX)
    assert (components[0] > 0).all()
    assert np.allclose(components[:, 0], [0.772, 0.635], atol=1e-3)
''',
)
write(
    "exercises/build-pca/wrong/no-centering.py",
    '''import numpy as np


def pca(X, k):
    mean = X.mean(axis=0)
    C = X.T @ X / (len(X) - 1)
    values, vectors = np.linalg.eigh(C)
    order = np.argsort(values)[::-1]
    values = values[order]
    components = vectors[:, order[:k]]
    components = components * np.sign(components[0])
    return (X - mean) @ components, components, values / values.sum()


def reconstruct(scores, components, mean):
    return scores @ components.T + mean


X = np.array([[2.0, 1.0], [3.0, 2.0], [4.0, 2.0], [5.0, 4.0], [6.0, 4.0], [7.0, 5.0]])
scores, components, explained = pca(X, 1)
print(np.round(explained, 3))
rebuilt = reconstruct(scores, components, X.mean(axis=0))
print(round(float(np.linalg.norm(X - rebuilt)), 3))
''',
)
write(
    "exercises/build-pca/wrong/ascending-order.py",
    '''import numpy as np


def pca(X, k):
    mean = X.mean(axis=0)
    centered = X - mean
    C = centered.T @ centered / (len(X) - 1)
    values, vectors = np.linalg.eigh(C)
    components = vectors[:, :k]
    components = components * np.sign(components[0])
    return centered @ components, components, values / values.sum()


def reconstruct(scores, components, mean):
    return scores @ components.T + mean


X = np.array([[2.0, 1.0], [3.0, 2.0], [4.0, 2.0], [5.0, 4.0], [6.0, 4.0], [7.0, 5.0]])
scores, components, explained = pca(X, 1)
print(np.round(explained, 3))
rebuilt = reconstruct(scores, components, X.mean(axis=0))
print(round(float(np.linalg.norm(X - rebuilt)), 3))
''',
)
write(
    "exercises/build-pca/wrong/typed-in.py",
    '''import numpy as np


def pca(X, k):
    return np.zeros((len(X), k)), np.zeros((X.shape[1], k)), np.array([0.984, 0.016])


def reconstruct(scores, components, mean):
    return scores @ components.T + mean


print("[0.984 0.016]")
print(0.695)
''',
)

write(
    "exercises/debug-pca-mistakes/exercise.yaml",
    '''id: debug-pca-mistakes
stage: debug
rev: 1
title: "A PCA that points the wrong way"
prompt: |
  `report(X)` should print the share of variance the first component explains and the component itself (first entry positive):

  ```
  first component explains 0.984
  direction [0.772 0.635]
  ```

  It has two bugs. Run it: the share is too high and the direction is wrong. One bug is in how the covariance is built (what should happen to the data first?); the other is in which column of the eigenvectors is taken (remember `eigh`'s order).
skills: [covariance, components]
''',
)
REPORT_TAIL = "\n\n" + SIX_POINTS + "report(X)\n"
write(
    "exercises/debug-pca-mistakes/starter.py",
    '''import numpy as np


def report(X):
    C = X.T @ X / (len(X) - 1)
    values, vectors = np.linalg.eigh(C)
    top = vectors[:, 0]
    top = top * np.sign(top[0])
    print("first component explains", round(float(values[-1] / values.sum()), 3))
    print("direction", np.round(top, 3))
''' + REPORT_TAIL,
)
write(
    "exercises/debug-pca-mistakes/solution.py",
    '''import numpy as np


def report(X):
    centered = X - X.mean(axis=0)
    C = centered.T @ centered / (len(X) - 1)
    values, vectors = np.linalg.eigh(C)
    top = vectors[:, -1]
    top = top * np.sign(top[0])
    print("first component explains", round(float(values[-1] / values.sum()), 3))
    print("direction", np.round(top, 3))
''' + REPORT_TAIL,
)
write(
    "exercises/debug-pca-mistakes/test_exercise.py",
    '''import numpy as np

from checks import function, printed, run

EXPECTED = "first component explains 0.984\\ndirection [0.772 0.635]\\n"


def test_the_output():
    """Prints the share and the direction."""
    out = run()
    assert out == EXPECTED, f"Expected this:\\n{EXPECTED}\\nYour program printed:\\n{out}"


def test_rectangle():
    """For the corners of a 2-by-1 rectangle: 0.8 along the x direction."""
    out = printed(function("report"), np.array([[0.0, 0.0], [2.0, 0.0], [0.0, 1.0], [2.0, 1.0]]))
    assert out == "first component explains 0.8\\ndirection [1. 0.]\\n", f"For the rectangle it printed:\\n{out}"
''',
)
write(
    "exercises/debug-pca-mistakes/wrong/centering-only.py",
    '''import numpy as np


def report(X):
    centered = X - X.mean(axis=0)
    C = centered.T @ centered / (len(X) - 1)
    values, vectors = np.linalg.eigh(C)
    top = vectors[:, 0]
    top = top * np.sign(top[0])
    print("first component explains", round(float(values[-1] / values.sum()), 3))
    print("direction", np.round(top, 3))
''' + REPORT_TAIL,
)
write(
    "exercises/debug-pca-mistakes/wrong/typed-in.py",
    '''import numpy as np


def report(X):
    print("first component explains 0.984")
    print("direction [0.772 0.635]")
''' + REPORT_TAIL,
)

# --- review pool: a code exercise -------------------------------------------

write(
    "exercises/review-top-share/exercise.yaml",
    '''id: review-top-share
stage: review_code
rev: 1
title: "The share the first component keeps"
prompt: |
  Write `top_share(X)`, which returns the share of the variance the first principal component explains, rounded to 3 places, and print it for the starter's points:

  ```
  0.984
  ```
skills: [explained, covariance]
''',
)
write("exercises/review-top-share/starter.py", "import numpy as np\n\n" + SIX_POINTS)
write(
    "exercises/review-top-share/solution.py",
    "import numpy as np\n\n" + SIX_POINTS + '''

def top_share(X):
    centered = X - X.mean(axis=0)
    values = np.linalg.eigvalsh(centered.T @ centered / (len(X) - 1))
    return round(float(values[-1] / values.sum()), 3)


print(top_share(X))
''',
)
write(
    "exercises/review-top-share/test_exercise.py",
    '''import numpy as np

from checks import function, run


def test_the_output():
    """Prints 0.984."""
    assert run() == "0.984\\n"


def test_rectangle():
    """The 2-by-1 rectangle's corners give 0.8."""
    top_share = function("top_share")
    assert top_share(np.array([[0.0, 0.0], [2.0, 0.0], [0.0, 1.0], [2.0, 1.0]])) == 0.8
''',
)
write(
    "exercises/review-top-share/wrong/smallest.py",
    "import numpy as np\n\n" + SIX_POINTS + '''

def top_share(X):
    centered = X - X.mean(axis=0)
    values = np.linalg.eigvalsh(centered.T @ centered / (len(X) - 1))
    return round(float(values[0] / values.sum()), 3)


print(top_share(X))
''',
)
write(
    "exercises/review-top-share/wrong/typed-in.py",
    "import numpy as np\n\n" + SIX_POINTS + '''

def top_share(X):
    return 0.984


print(0.984)
''',
)

print("ml.la.pca written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
