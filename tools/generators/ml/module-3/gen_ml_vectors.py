"""Writes the topic ml.la.vectors (Module 3's second topic). Run from the
repository root. Files are written as bytes with LF endings."""

import pathlib

ROOT = pathlib.Path("content/topics/ml.la.vectors")


def write(relative: str, text: str) -> None:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


write(
    "topic.yaml",
    '''id: ml.la.vectors
kind: topic
status: ready
title: "Vectors: length, angle and dot product"
summary: "Norms and unit vectors, the dot product as similarity, the angle between vectors, and projecting one onto another."
prerequisites: [ml.la.numpy-arrays, ml.math.exponents-and-logs]
packages: [numpy]
estimated_minutes: 50
rev: 1
objectives:
  - "Compute a vector's length and make a unit vector."
  - "Compute a dot product and read it as a similarity."
  - "Find the angle between two vectors, and say what a dot product of zero means."
  - "Project one vector onto another."
# Linked, never copied or embedded: 3Blue1Brown's videos are under the
# standard YouTube licence; NumPy's documentation under the NumPy licence
# (BSD-3-Clause).
resources:
  - title: "Essence of linear algebra, chapter 1: Vectors, what even are they? (3Blue1Brown, Grant Sanderson)"
    url: https://www.youtube.com/watch?v=fNk_zzaMoSs
    type: video
    use: link
    license: Standard YouTube licence (linked, not embedded)
  - title: "Essence of linear algebra, chapter 9: Dot products and duality (3Blue1Brown, Grant Sanderson)"
    url: https://www.youtube.com/watch?v=LyGKycYT2v0
    type: video
    use: link
    license: Standard YouTube licence (linked, not embedded)
  - title: "numpy.linalg.norm (the NumPy developers)"
    url: https://numpy.org/doc/stable/reference/generated/numpy.linalg.norm.html
    type: reading
    use: link
    license: BSD-3-Clause (NumPy documentation)
practice:
  - example-length-and-dot
  - parsons-unit-vector
  - mcq-dot-sign
  - predict-dot-and-norm
  - mcq-cosine-similarity
  - fill-angle-between
  - mcq-projection
  - write-most-similar
prove:
  build: build-projection
  debug: debug-similarity-report
  explain:
    prompt: |
      Your recommender stores every product as a vector of numbers and finds "similar" ones with the dot product. A teammate asks: why divide the dot product by the two lengths before calling it a similarity? What does a dot product of exactly zero mean? Why should a product described with twice as many words still count as similar to its shorter description? And what does "projecting" a customer's taste vector onto a product's vector actually give you? In your own words.
    rubric:
      - id: dot-as-similarity
        required: true
        description: "The dot product adds up the products of matching entries; it's large when two vectors point the same way and have big entries in the same places."
      - id: cosine
        required: true
        description: "Dividing by both lengths leaves the cosine of the angle, which depends only on direction: twice the words means twice the length but the same direction, so the same similarity."
      - id: zero
        required: true
        description: "A dot product of zero means the vectors are perpendicular: nothing in common along any direction, the angle is 90 degrees."
      - id: projection
        required: false
        description: "The projection is the part of one vector that lies along the other, its shadow on that line, with length (v . w) / |w|; the rest is perpendicular to it."
    model_answer: |
      The dot product multiplies the two vectors entry by entry and adds the results, so it's large when both have big numbers in the same places and they point roughly the same way. But it also grows with the lengths: a product with twice as many words has a vector twice as long, and its dot product with anything doubles too. Dividing by both lengths removes that: what's left is the cosine of the angle between them, 1 for the same direction, 0 for perpendicular, -1 for opposite, and it doesn't change when a vector is scaled. That's why the longer description stays just as similar to the shorter one: same direction, different length. A dot product of exactly zero means the angle is 90 degrees: the vectors are perpendicular, with nothing in common along any direction. Projecting a taste vector onto a product's vector gives the part of the taste that lies along that product, its shadow on that line: a vector pointing the product's way, with length equal to the dot product divided by the product's length. What's left after subtracting it is perpendicular to the product, the part of the taste that product says nothing about.
review_pool:
  - review-predict-norm-3d
  - review-mcq-dot-formula
  - review-mcq-unit-vector
  - review-predict-projection
  - review-perpendicular
# What this topic teaches. Each question names the skills it tests, so a
# missed question can come back as a different one on the same skill
# (ADR-0011).
skills:
  - id: length
    description: "Compute a vector's length and make a unit vector"
  - id: dot
    description: "Compute a dot product, and read it as a similarity that length distorts and cosine fixes"
  - id: angle
    description: "Find the angle between two vectors, and know that a zero dot product means perpendicular"
  - id: projection
    description: "Project one vector onto another, and separate the perpendicular part"
''',
)

write(
    "lesson.mdx",
    '''<Intro>

A vector is an arrow: it has a length and a direction. Module 1 built them as lists; now they're arrays, and the two questions this topic answers are the ones every model keeps asking: how long is it, and how much do two of them point the same way? The dot product answers the second, and almost everything called "similarity" in machine learning is a dot product with the lengths divided out.

The main resource is **3Blue1Brown's first chapter** of *Essence of linear algebra*, ten minutes of pictures: a vector as an arrow, as a list of numbers, and why both views are right. Then **chapter 9**, on dot products, which is the one idea here that deserves a picture. Watch for:

- **Length** is Pythagoras: the square root of the sum of the squares.
- **The dot product** adds up the products of matching entries, and comes out as a single number.
- **Why dividing by the lengths** turns a dot product into a cosine, which is the angle.
- **Projection** as a shadow: the part of one vector that lies along another.

</Intro>

<Resource index={0} />

<Recap>

- **Length** (the norm): `np.linalg.norm(v)`, which is `np.sqrt(np.sum(v * v))`. `[3, 4]` has length 5.
- **A unit vector** has length 1 and keeps the direction: `v / np.linalg.norm(v)`. Not `v / len(v)`: `len` counts the entries.
- **The dot product** `v @ w` (or `np.dot`) is the sum of the products of matching entries: `[3, 4] @ [4, 3]` is 12 + 12 = 24. `v @ v` is the length squared.
- **Reading it:** positive means the vectors point broadly the same way, negative opposite ways, and **zero means perpendicular**. With a unit axis vector it reads off a coordinate: `v @ [1, 0]` is v's first entry.
- **Cosine similarity** divides by both lengths: `(v @ w) / (norm(v) * norm(w))`. It's the cosine of the angle between them, from 1 (same direction) to -1 (opposite), and it doesn't change when either vector is scaled. The angle itself is `np.degrees(np.arccos(cos))`; clip `cos` to `[-1, 1]` first, because rounding can leave it at 1.0000000002 and `arccos` refuses that.
- **Projection** of `v` onto the line through `w`: `(v @ w) / (w @ w) * w`, the shadow of `v` on that line. Subtracting it from `v` leaves the part perpendicular to `w`. If `w` is a unit vector the divisor is 1, which is the only case where leaving it out works.
- **Rows at once:** for a 2-D array of vectors, `rows @ query` is every row's dot product with `query` in one go, and `np.linalg.norm(rows, axis=1)` every row's length. That's a recommender's inner loop, with no loop.
- **In machine learning:** word and image embeddings are vectors, and "nearest" means highest cosine; a linear model's prediction is a dot product of the features with the weights; projection is the first step of least squares, two topics from now.

</Recap>
''',
)

# --- practice: recall --------------------------------------------------------

write(
    "recall/parsons-unit-vector.yaml",
    '''id: parsons-unit-vector
type: parsons
rev: 1
prompt: |
  Put the lines in order so the program prints the unit vector in the direction of `[6, 8]`, which is `[0.6 0.8]`. One line is a decoy that doesn't belong.
lines:
  - 'import numpy as np'
  - 'v = np.array([6.0, 8.0])'
  - 'length = np.linalg.norm(v)'
  - 'print(v / length)'
distractors:
  - 'print(v / len(v))'
explanation: |
  The length of `[6, 8]` is 10, so dividing by it gives `[0.6 0.8]`, a vector of length 1 pointing the same way. The decoy divides by `len(v)`, which is 2, the number of entries, and gives `[3. 4.]`: a shorter vector, but not a unit one.
skills: [length]
''',
)

write(
    "recall/mcq-dot-sign.yaml",
    '''id: mcq-dot-sign
type: mcq
rev: 1
prompt: |
  Neither `u` nor `w` is the zero vector, and `u @ w` is exactly `0`. What do you know?
choices:
  - 'They point the same way'
  - 'They point opposite ways'
  - 'They are perpendicular: the angle between them is 90 degrees'
  - '`u` is longer than `w`'
answer: 2
explanation: |
  The dot product is the product of the lengths times the cosine of the angle. Neither length is zero, so the cosine is: the angle is 90 degrees. Same direction would give a positive product, opposite a negative one, and the dot product says nothing about which is longer.
skills: [angle]
''',
)

write(
    "recall/predict-dot-and-norm.yaml",
    '''id: predict-dot-and-norm
type: predict_output
rev: 1
prompt: |
  A length, a dot product, and a vector dotted with itself. What does the program print?
code: |
  import numpy as np

  a = np.array([1.0, 2.0, 2.0])
  b = np.array([2.0, 0.0, 0.0])
  print(np.linalg.norm(a))
  print(a @ b)
  print(a @ a)
  print(np.linalg.norm(a) ** 2)
expected_output: |
  3.0
  2.0
  9.0
  9.0
explanation: |
  The length of `a` is the square root of 1 + 4 + 4, which is 3. `a @ b` multiplies matching entries and adds: 2 + 0 + 0. `a @ a` is 1 + 4 + 4 = 9, and that's always the length squared, which the last line confirms.
skills: [dot, length]
''',
)

write(
    "recall/mcq-cosine-similarity.yaml",
    '''id: mcq-cosine-similarity
type: mcq
rev: 1
prompt: |
  Two documents as word counts over the same three words: `a = [3, 0, 3]` and `b = [1, 0, 1]`. What is their cosine similarity, `(a @ b) / (norm(a) * norm(b))`?
choices:
  - '`0`'
  - '`0.5`'
  - '`1.0`'
  - '`6`'
answer: 2
explanation: |
  `a @ b` is 3 + 0 + 3 = 6. The lengths are √18 and √2, whose product is √36 = 6. So the cosine is 1: the two vectors point in exactly the same direction, because `a` is three times `b`. The longer document uses the same words in the same proportions, and cosine similarity ignores the length. `6` is the raw dot product, before the lengths are divided out.
skills: [dot]
''',
)

write(
    "recall/mcq-projection.yaml",
    '''id: mcq-projection
type: mcq
rev: 1
prompt: |
  What is the projection of `v = [3, 4]` onto the direction `[1, 0]`?
choices:
  - '`[3, 0]`'
  - '`[0, 4]`'
  - '`[3, 4]`'
  - '`3`'
answer: 0
explanation: |
  The projection is the shadow of `v` on the line through `[1, 0]`, the x-axis: the part of `v` that lies along it, `[3, 0]`. The formula agrees: `(v @ w) / (w @ w) * w` is 3 / 1 times `[1, 0]`. What's left, `[0, 4]`, is the part perpendicular to that line. `3` is the projection's length, not the projection.
skills: [projection]
''',
)

write(
    "recall/review-predict-norm-3d.yaml",
    '''id: review-predict-norm-3d
type: predict_output
rev: 1
prompt: |
  A length in three dimensions, and the unit vector. What does the program print?
code: |
  import numpy as np

  r = np.array([0.0, 3.0, 4.0])
  print(np.linalg.norm(r))
  print(r / np.linalg.norm(r))
expected_output: |
  5.0
  [0.  0.6 0.8]
explanation: |
  Pythagoras works in any number of dimensions: the square root of 0 + 9 + 16 is 5. Dividing every entry by 5 gives a vector of length 1 in the same direction. NumPy prints `0.` for a float zero and pads the entries to line up.
skills: [length]
''',
)

write(
    "recall/review-mcq-dot-formula.yaml",
    '''id: review-mcq-dot-formula
type: mcq
rev: 1
prompt: |
  What is `np.array([1, 2]) @ np.array([4, 5])`?
choices:
  - '`9`'
  - '`14`'
  - '`[4, 10]`'
  - '`20`'
answer: 1
explanation: |
  The dot product multiplies matching entries and adds the results: 1 × 4 + 2 × 5 = 14, one number. `[4, 10]` is the elementwise product `a * b` before the adding; `9` is the sum of one vector's entries, `20` the product of both sums.
skills: [dot]
''',
)

write(
    "recall/review-mcq-unit-vector.yaml",
    '''id: review-mcq-unit-vector
type: mcq
rev: 1
prompt: |
  What does dividing a vector by its own length give?
choices:
  - 'A vector of length 1 pointing the same way'
  - 'The number 1'
  - 'A vector pointing the opposite way'
  - 'The vector with each entry divided by the number of entries'
answer: 0
explanation: |
  Scaling a vector by a positive number keeps its direction and multiplies its length, so dividing by the length leaves length 1: a unit vector, the direction on its own. The last choice is `v / len(v)`, which is the common mistake.
skills: [length]
''',
)

write(
    "recall/review-predict-projection.yaml",
    '''id: review-predict-projection
type: predict_output
rev: 1
prompt: |
  A projection onto the y-axis direction. What does the program print?
code: |
  import numpy as np


  def project(v, onto):
      return (v @ onto) / (onto @ onto) * onto


  print(project(np.array([3.0, 4.0]), np.array([0.0, 1.0])))
expected_output: |
  [0. 4.]
explanation: |
  `v @ onto` is 4, `onto @ onto` is 1, so the projection is 4 times `[0, 1]`: the shadow of `[3, 4]` on the y-axis, `[0. 4.]`. The 3 is the part perpendicular to that line, and it disappears.
skills: [projection]
''',
)

# --- practice: exercises -------------------------------------------------------

write(
    "exercises/example-length-and-dot/exercise.yaml",
    '''id: example-length-and-dot
stage: worked_example
rev: 1
title: "Length, unit vectors and the dot product"
prompt: |
  This program measures a vector, scales it to length 1, dots it with another, turns that into an angle, and dots it with the axes. Press **Run**, then read how each part works.
steps:
  - label: "Length, by hand and by name"
    lines: "3-5"
    note: "Pythagoras: square the entries, add, take the root. `[3, 4]` has length 5. `np.linalg.norm` is the same thing with a name."
  - label: "A unit vector"
    lines: "6-8"
    note: "Dividing by the length keeps the direction and makes the length 1: `[0.6 0.8]`. Every direction has exactly one unit vector."
  - label: "The dot product"
    lines: "10-11"
    note: "`v @ w` multiplies matching entries and adds: 3 × 4 + 4 × 3 = 24. One number from two vectors."
  - label: "From a dot product to an angle"
    lines: "12-14"
    note: "Divide by both lengths and the dot product becomes the cosine of the angle between the vectors: 24 / 25 = 0.96, an angle of about 16 degrees. Scaling either vector wouldn't change it."
  - label: "Dotting with the axes"
    lines: "16-19"
    note: "A dot product with a unit axis vector reads off that coordinate: 3 along x, 4 along y. The two axes dotted together give 0: perpendicular vectors have a dot product of zero."
''',
)
write(
    "exercises/example-length-and-dot/solution.py",
    '''import numpy as np

v = np.array([3.0, 4.0])
print(np.sqrt(np.sum(v * v)))
print(np.linalg.norm(v))
unit = v / np.linalg.norm(v)
print(unit)
print(np.linalg.norm(unit))

w = np.array([4.0, 3.0])
print(v @ w)
cos = (v @ w) / (np.linalg.norm(v) * np.linalg.norm(w))
print(cos)
print(round(float(np.degrees(np.arccos(cos))), 2))

right = np.array([1.0, 0.0])
up = np.array([0.0, 1.0])
print(v @ right, v @ up)
print(right @ up)
''',
)
write(
    "exercises/example-length-and-dot/test_exercise.py",
    '''from checks import run


def test_the_walkthrough():
    """Prints the length twice, the unit vector and its length, the dot product, the cosine, the angle, and the axis dots."""
    assert run() == "5.0\\n5.0\\n[0.6 0.8]\\n1.0\\n24.0\\n0.96\\n16.26\\n3.0 4.0\\n0.0\\n"
''',
)

write(
    "exercises/fill-angle-between/exercise.yaml",
    '''id: fill-angle-between
stage: fill_in
rev: 1
title: "The angle between"
prompt: |
  `angle_degrees(u, w)` should return the angle between two vectors, in degrees, rounded to 2 places. Replace each `...` so the program prints:

  ```
  45.0
  90.0
  ```

  The `np.clip` line is there on purpose: rounding can leave a cosine at 1.0000000002, which `arccos` refuses.
hints:
  - "The cosine of the angle is the dot product divided by **both** lengths: `(u @ w) / (norm(u) * norm(w))`."
  - "`np.arccos` turns a cosine back into an angle in radians; `np.degrees` converts it."
skills: [angle]
''',
)
write(
    "exercises/fill-angle-between/starter.py",
    '''import numpy as np


def angle_degrees(u, w):
    cos = (u @ w) / (np.linalg.norm(u) * ...)
    cos = np.clip(cos, -1.0, 1.0)
    return round(float(np.degrees(np.arccos(...))), 2)


print(angle_degrees(np.array([1.0, 0.0]), np.array([1.0, 1.0])))
print(angle_degrees(np.array([1.0, 0.0]), np.array([0.0, 1.0])))
''',
)
write(
    "exercises/fill-angle-between/solution.py",
    '''import numpy as np


def angle_degrees(u, w):
    cos = (u @ w) / (np.linalg.norm(u) * np.linalg.norm(w))
    cos = np.clip(cos, -1.0, 1.0)
    return round(float(np.degrees(np.arccos(cos))), 2)


print(angle_degrees(np.array([1.0, 0.0]), np.array([1.0, 1.0])))
print(angle_degrees(np.array([1.0, 0.0]), np.array([0.0, 1.0])))
''',
)
write(
    "exercises/fill-angle-between/test_exercise.py",
    '''import numpy as np

from checks import function, run


def test_these_pairs():
    """Prints 45.0, then 90.0."""
    printed = run()
    assert printed == "45.0\\n90.0\\n", f"Your program printed:\\n{printed}"


def test_other_pairs():
    """Opposite vectors give 180, and a vector with a scaled copy of itself gives 0."""
    angle_degrees = function("angle_degrees")
    assert angle_degrees(np.array([1.0, 0.0]), np.array([-2.0, 0.0])) == 180.0
    assert angle_degrees(np.array([1.0, 2.0]), np.array([2.0, 4.0])) == 0.0
''',
)
write(
    "exercises/fill-angle-between/wrong/forgets-the-lengths.py",
    '''import numpy as np


def angle_degrees(u, w):
    cos = (u @ w) / (np.linalg.norm(u) * 1)
    cos = np.clip(cos, -1.0, 1.0)
    return round(float(np.degrees(np.arccos(cos))), 2)


print(angle_degrees(np.array([1.0, 0.0]), np.array([1.0, 1.0])))
print(angle_degrees(np.array([1.0, 0.0]), np.array([0.0, 1.0])))
''',
)
write(
    "exercises/fill-angle-between/wrong/typed-in.py",
    '''import numpy as np


def angle_degrees(u, w):
    if w[1] == 1.0 and w[0] == 1.0:
        return 45.0
    return 90.0


print(angle_degrees(np.array([1.0, 0.0]), np.array([1.0, 1.0])))
print(angle_degrees(np.array([1.0, 0.0]), np.array([0.0, 1.0])))
''',
)

write(
    "exercises/write-most-similar/exercise.yaml",
    '''id: write-most-similar
stage: write
rev: 1
title: "The most similar row"
prompt: |
  `rows` is a 2-D array with one vector per row, and `query` a vector of the same width. Write `most_similar(query, rows)`, which returns the position (0, 1, 2, ...) of the row with the highest **cosine similarity** to the query, without a loop: every dot product at once with `rows @ query`, every length at once with `np.linalg.norm(rows, axis=1)`. Then print it for the starter's rows and query:

  ```
  0
  ```
hints:
  - "`rows @ query` gives one dot product per row; divide that array by `np.linalg.norm(rows, axis=1) * np.linalg.norm(query)`."
  - "`.argmax()` gives the position of the largest value; wrap it in `int()`."
skills: [dot, length]
''',
)
STARTER_ROWS = '''import numpy as np

rows = np.array([[2.0, 2.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 5.0]])
query = np.array([1.0, 1.0, 0.0])
'''
write("exercises/write-most-similar/starter.py", STARTER_ROWS)
write(
    "exercises/write-most-similar/solution.py",
    STARTER_ROWS + '''

def most_similar(query, rows):
    sims = rows @ query / (np.linalg.norm(rows, axis=1) * np.linalg.norm(query))
    return int(sims.argmax())


print(most_similar(query, rows))
''',
)
write(
    "exercises/write-most-similar/test_exercise.py",
    '''import numpy as np

from checks import function, run


def test_the_output():
    """Prints 0."""
    printed = run()
    assert printed == "0\\n", f"Your program printed:\\n{printed}"


def test_length_is_ignored():
    """A short row pointing the query's way beats a long row pointing elsewhere."""
    most_similar = function("most_similar")
    rows = np.array([[5.0, 0.0], [1.0, 3.0], [0.0, 0.5]])
    assert most_similar(np.array([0.0, 1.0]), rows) == 2
''',
)
write(
    "exercises/write-most-similar/wrong/dot-only.py",
    STARTER_ROWS + '''

def most_similar(query, rows):
    return int((rows @ query).argmax())


print(most_similar(query, rows))
''',
)
write(
    "exercises/write-most-similar/wrong/typed-in.py",
    STARTER_ROWS + '''

def most_similar(query, rows):
    return 0


print(0)
''',
)

# --- proof ------------------------------------------------------------------

write(
    "exercises/build-projection/exercise.yaml",
    '''id: build-projection
stage: build
rev: 1
title: "Projection and what's left"
prompt: |
  Starting from a blank editor, write `project(v, onto)`, the projection of `v` onto the line through `onto`: `(v @ onto) / (onto @ onto) * onto`, the shadow of `v` on that line. Then `rejection(v, onto)`, what's left of `v` after the projection is subtracted: the part perpendicular to `onto`. Both must work whatever the length of `onto`, and in any number of dimensions.

  Then print the projection and rejection of `[3, 4]` onto `[1, 0]`, and onto `[1, 1]`:

  ```
  [3. 0.]
  [0. 4.]
  [3.5 3.5]
  [-0.5  0.5]
  ```

  The checks use other vectors, in three dimensions too, and confirm that the projection lies along `onto`, the rejection is perpendicular to it, and the two add back up to `v`.
skills: [projection, dot]
''',
)
write("exercises/build-projection/starter.py", "")
write(
    "exercises/build-projection/solution.py",
    '''import numpy as np


def project(v, onto):
    return (v @ onto) / (onto @ onto) * onto


def rejection(v, onto):
    return v - project(v, onto)


v = np.array([3.0, 4.0])
print(project(v, np.array([1.0, 0.0])))
print(rejection(v, np.array([1.0, 0.0])))
print(project(v, np.array([1.0, 1.0])))
print(rejection(v, np.array([1.0, 1.0])))
''',
)
write(
    "exercises/build-projection/test_exercise.py",
    '''import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints the four vectors."""
    assert run() == "[3. 0.]\\n[0. 4.]\\n[3.5 3.5]\\n[-0.5  0.5]\\n"


def test_three_dimensions():
    """Projecting [1, 2, 3] onto [0, 0, 2] gives [0, 0, 3]; the rejection is [1, 2, 0]."""
    project = function("project")
    rejection = function("rejection")
    v = np.array([1.0, 2.0, 3.0])
    onto = np.array([0.0, 0.0, 2.0])
    assert project(v, onto).tolist() == [0.0, 0.0, 3.0]
    assert rejection(v, onto).tolist() == [1.0, 2.0, 0.0]


def test_the_geometry():
    """For another pair: the projection lies along onto, the rejection is perpendicular to it, and they add up to v."""
    project = function("project")
    rejection = function("rejection")
    v = np.array([2.0, -1.0, 4.0])
    onto = np.array([3.0, 1.0, -2.0])
    p = project(v, onto)
    r = rejection(v, onto)
    assert np.allclose(p, (p @ onto) / (onto @ onto) * onto)
    assert abs(r @ onto) < 1e-9
    assert np.allclose(p + r, v)
''',
)
write(
    "exercises/build-projection/wrong/unit-only.py",
    '''import numpy as np


def project(v, onto):
    return (v @ onto) * onto


def rejection(v, onto):
    return v - project(v, onto)


v = np.array([3.0, 4.0])
print(project(v, np.array([1.0, 0.0])))
print(rejection(v, np.array([1.0, 0.0])))
print(project(v, np.array([1.0, 1.0])))
print(rejection(v, np.array([1.0, 1.0])))
''',
)
write(
    "exercises/build-projection/wrong/swapped.py",
    '''import numpy as np


def project(v, onto):
    return (v @ onto) / (v @ v) * v


def rejection(v, onto):
    return v - project(v, onto)


v = np.array([3.0, 4.0])
print(project(v, np.array([1.0, 0.0])))
print(rejection(v, np.array([1.0, 0.0])))
print(project(v, np.array([1.0, 1.0])))
print(rejection(v, np.array([1.0, 1.0])))
''',
)
write(
    "exercises/build-projection/wrong/typed-in.py",
    '''import numpy as np


def project(v, onto):
    return np.array([3.0, 0.0])


def rejection(v, onto):
    return np.array([0.0, 4.0])


print("[3. 0.]")
print("[0. 4.]")
print("[3.5 3.5]")
print("[-0.5  0.5]")
''',
)

write(
    "exercises/debug-similarity-report/exercise.yaml",
    '''id: debug-similarity-report
stage: debug
rev: 1
title: "A similarity report"
prompt: |
  `report(query, rows)` should print each row's cosine similarity to the query, rounded to 3 places, and the position of the most similar row:

  ```
  similarities: [1.    0.707 0.   ]
  most similar: row 0
  ```

  It has two bugs. Run it and check the numbers: with these rows the program runs, but the similarities are wrong, and the checks' rows will make the first bug a shape error. One bug is in the order of a matrix product; the other is a length taken over the wrong thing.
skills: [dot, length]
''',
)
REPORT_CALL = '''

report(np.array([1.0, 1.0, 0.0]), np.array([[2.0, 2.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 5.0]]))
'''
write(
    "exercises/debug-similarity-report/starter.py",
    '''import numpy as np


def report(query, rows):
    sims = query @ rows / (np.linalg.norm(rows) * np.linalg.norm(query))
    print("similarities:", np.round(sims, 3))
    print("most similar: row", int(sims.argmax()))
''' + REPORT_CALL,
)
write(
    "exercises/debug-similarity-report/solution.py",
    '''import numpy as np


def report(query, rows):
    sims = rows @ query / (np.linalg.norm(rows, axis=1) * np.linalg.norm(query))
    print("similarities:", np.round(sims, 3))
    print("most similar: row", int(sims.argmax()))
''' + REPORT_CALL,
)
write(
    "exercises/debug-similarity-report/test_exercise.py",
    '''import numpy as np

from checks import function, printed, run

EXPECTED = "similarities: [1.    0.707 0.   ]\\nmost similar: row 0\\n"


def test_the_output():
    """Prints the three similarities and the most similar row."""
    out = run()
    assert out == EXPECTED, f"Expected this:\\n{EXPECTED}\\nYour program printed:\\n{out}"


def test_two_rows():
    """Works for two rows of three: one along the query, one perpendicular to it."""
    out = printed(function("report"), np.array([0.0, 1.0, 0.0]), np.array([[0.0, 2.0, 0.0], [3.0, 0.0, 4.0]]))
    assert out == "similarities: [1. 0.]\\nmost similar: row 0\\n", f"For those rows it printed:\\n{out}"
''',
)
write(
    "exercises/debug-similarity-report/wrong/one-of-two.py",
    '''import numpy as np


def report(query, rows):
    sims = rows @ query / (np.linalg.norm(rows) * np.linalg.norm(query))
    print("similarities:", np.round(sims, 3))
    print("most similar: row", int(sims.argmax()))
''' + REPORT_CALL,
)
write(
    "exercises/debug-similarity-report/wrong/typed-in.py",
    '''import numpy as np


def report(query, rows):
    print("similarities: [1.    0.707 0.   ]")
    print("most similar: row 0")
''' + REPORT_CALL,
)

# --- review pool: a code exercise -------------------------------------------

write(
    "exercises/review-perpendicular/exercise.yaml",
    '''id: review-perpendicular
stage: review_code
rev: 1
title: "Perpendicular?"
prompt: |
  Write `is_perpendicular(u, w)`, which returns `True` when two vectors are perpendicular: their dot product is zero, allowing for rounding (`abs(u @ w) < 1e-9`). Then print it for `[1, 2]` against `[2, -1]`, and for `[1, 1]` against `[1, 2]`:

  ```
  True
  False
  ```
skills: [angle, dot]
''',
)
write("exercises/review-perpendicular/starter.py", "import numpy as np\n")
write(
    "exercises/review-perpendicular/solution.py",
    '''import numpy as np


def is_perpendicular(u, w):
    return bool(abs(u @ w) < 1e-9)


print(is_perpendicular(np.array([1.0, 2.0]), np.array([2.0, -1.0])))
print(is_perpendicular(np.array([1.0, 1.0]), np.array([1.0, 2.0])))
''',
)
write(
    "exercises/review-perpendicular/test_exercise.py",
    '''import numpy as np

from checks import function, run


def test_the_output():
    """Prints True, then False."""
    assert run() == "True\\nFalse\\n"


def test_three_dimensions():
    """Two axes are perpendicular; a vector and a scaled copy of itself aren't."""
    is_perpendicular = function("is_perpendicular")
    assert is_perpendicular(np.array([1.0, 0.0, 0.0]), np.array([0.0, 5.0, 0.0])) is True
    assert is_perpendicular(np.array([1.0, 2.0, 3.0]), np.array([2.0, 4.0, 6.0])) is False
''',
)
write(
    "exercises/review-perpendicular/wrong/compares-lengths.py",
    '''import numpy as np


def is_perpendicular(u, w):
    return bool(np.linalg.norm(u) == np.linalg.norm(w))


print(is_perpendicular(np.array([1.0, 2.0]), np.array([2.0, -1.0])))
print(is_perpendicular(np.array([1.0, 1.0]), np.array([1.0, 2.0])))
''',
)
write(
    "exercises/review-perpendicular/wrong/typed-in.py",
    '''import numpy as np


def is_perpendicular(u, w):
    return True


print(True)
print(False)
''',
)

print("ml.la.vectors written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
