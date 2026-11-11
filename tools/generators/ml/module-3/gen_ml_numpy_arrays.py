"""Writes the topic ml.la.numpy-arrays, the first of the ML track's Module 3
and the first topic to declare a package (ADR-0023). Run from the repository
root. Files are written as bytes with LF endings."""

import pathlib

ROOT = pathlib.Path("content/topics/ml.la.numpy-arrays")


def write(relative: str, text: str) -> None:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


write(
    "topic.yaml",
    '''id: ml.la.numpy-arrays
kind: topic
status: ready
title: "NumPy arrays"
summary: "Arrays with a shape and a dtype: indexing, slicing, elementwise arithmetic and broadcasting, and why vectorized code beats a loop."
prerequisites: [ml.py.comprehensions, ml.math.vectors-and-matrices]
# The first topic to need a package beyond the standard library (ADR-0023).
packages: [numpy]
estimated_minutes: 50
rev: 1
objectives:
  - "Make arrays from lists and ranges, and read their shape and dtype."
  - "Index and slice arrays, in one and two dimensions."
  - "Do arithmetic on whole arrays at once, and say what broadcasting does."
  - "Replace a loop over numbers with one array operation, and say why it's faster."
# Linked, never copied. NumPy's documentation is published under the NumPy
# licence (BSD-3-Clause).
resources:
  - title: "NumPy: the absolute basics for beginners (the NumPy developers)"
    url: https://numpy.org/doc/stable/user/absolute_beginners.html
    type: reading
    use: link
    license: BSD-3-Clause (NumPy documentation)
  - title: "NumPy user guide: Broadcasting (the NumPy developers)"
    url: https://numpy.org/doc/stable/user/basics.broadcasting.html
    type: reading
    use: link
    license: BSD-3-Clause (NumPy documentation)
practice:
  - example-arrays-and-shapes
  - parsons-column-means
  - mcq-shape
  - predict-slices
  - mcq-dtype-trap
  - mcq-broadcasting
  - fill-normalize
  - write-row-totals
prove:
  build: build-standardize
  debug: debug-axis-mistakes
  explain:
    prompt: |
      A teammate adds up the squares of a million numbers with `total = 0` and `for v in values: total = total + v * v`, sees your `np.sum(values * values)` run a hundred times faster, and asks what's going on, and "what does broadcasting even mean". In your own words: what is an array, compared with a list? Why is the array version so much faster? What does broadcasting do when two shapes don't match, and when does it refuse? And what goes wrong if you put `2.7` into an array that was made from whole numbers?
    rubric:
      - id: array-vs-list
        required: true
        description: "An array is one block of memory holding values of a single dtype, with a shape; a list is a sequence of separate Python objects of any type."
      - id: speed
        required: true
        description: "values * values and np.sum run as one compiled loop over the block, with no Python object made per number; the for loop interprets every step and boxes every value."
      - id: broadcasting
        required: true
        description: "Broadcasting lines shapes up from the right and stretches a dimension of size 1 (or a missing one) to match, so a row can be added to every row of a grid; it refuses when the trailing sizes differ and neither is 1."
      - id: dtype
        required: false
        description: "An array has one dtype for all its values, so 2.7 stored into an integer array is truncated to 2 without an error; make the array float first."
    model_answer: |
      A list is a row of pointers to separate Python objects, each with its own type and its own overhead. An array is one block of memory in which every value has the same dtype, say float64, laid out next to each other, plus a shape that says how to read the block as rows and columns. That layout is why the array version is fast: values * values is one loop written in C that runs over the block from start to end, and np.sum is another, with no Python object created or type checked per number. The for loop does all of that interpretation a million times. Broadcasting is how NumPy does arithmetic between arrays of different shapes: it lines the shapes up from the right, and where one array has size 1 or no dimension at all, it stretches that array along it without copying. So a grid of shape (3, 4) plus a row of shape (4,) adds the row to every row. If the trailing sizes differ and neither is 1, say (3, 4) against (3,), it refuses with a shape error, which is usually the moment you realise you needed a column, shape (3, 1). The dtype is also the trap: an array made from whole numbers is an integer array, and storing 2.7 into it keeps 2, with no error, because the block can only hold integers. Make it float at the start if it will ever hold a fraction.
review_pool:
  - review-predict-broadcast-row
  - review-mcq-axis
  - review-predict-arange-linspace
  - review-double-evens
# What this topic teaches. Each question names the skills it tests, so a
# missed question can come back as a different one on the same skill
# (ADR-0011).
skills:
  - id: make
    description: "Make arrays from lists and ranges, and read their shape and dtype"
  - id: index
    description: "Index and slice arrays in one and two dimensions, including with a mask"
  - id: elementwise
    description: "Do arithmetic on whole arrays, and say what broadcasting does"
  - id: vectorize
    description: "Replace a loop with an array operation, and reduce along an axis"
''',
)

write(
    "lesson.mdx",
    '''<Intro>

In Module 1 you built vectors as lists and multiplied matrices with loops, so you know what the work is. NumPy does the same work in compiled code over a single block of memory, and every machine-learning library is built on it. From here on the array **is** the lesson.

The main resource is NumPy's own **absolute basics for beginners**, as far as "Basic array operations" and "Broadcasting"; about 20 minutes. Then the short **Broadcasting** page from the user guide. Watch for:

- **`shape` and `dtype`:** an array has a shape (how many along each dimension) and one data type for every value.
- **Indexing with commas:** `grid[1, 2]` is row 1, column 2; `grid[:, 0]` is the whole first column.
- **Arithmetic on whole arrays:** `a * 2` and `a + b` work element by element, with no loop written by you.
- **Broadcasting:** how a row can be added to every row of a grid, and the rule for when shapes fit.

The first time you press Run on this topic, the browser downloads NumPy (around ten megabytes, once); after that it's instant.

</Intro>

<Resource index={0} />

<Recap>

- **Making arrays.** `np.array([1.5, 2.0, 3.5])` from a list, `np.array([[1, 2, 3], [4, 5, 6]])` from nested lists (a 2-D array), `np.arange(5)` for `[0 1 2 3 4]`, `np.linspace(0, 1, 5)` for five evenly spaced values, `np.zeros(3)` and `np.ones((2, 2))`.
- **Shape and dtype.** `a.shape` is a tuple, `(3,)` or `(2, 3)`; `a.dtype` is the one type every value has, `float64` for decimals. Whole numbers get an integer dtype whose width depends on the machine: the browser's NumPy is a 32-bit build and says `int32` where a laptop says `int64`, which is why this topic prints dtypes only for floats and for types it chose, like `np.int8`.
- **The dtype trap.** `a = np.array([1, 2, 3]); a[0] = 2.7` stores `2`: an integer array can't hold a fraction and doesn't complain. Make it float from the start: `np.array([1.0, 2, 3])`.
- **Indexing and slicing.** `grid[1, 2]` one value; `grid[0]` a row; `grid[:, 2]` a column; `grid[1:, :2]` a block; `grid[grid > 5]` the values where a condition holds (a boolean mask). Slices are views: changing one changes the original.
- **Elementwise arithmetic.** `a * 2`, `a + b`, `a ** 2`, `np.sqrt(a)` act on every element at once. No loop, and no Python object per number, which is where the speed comes from.
- **Broadcasting.** Shapes line up from the right. Where one array has size 1 or no dimension there, it's stretched to match, so `(2, 3) + (3,)` adds the row to each row. `(2, 3) + (2,)` fails: `operands could not be broadcast together`. A column is shape `(2, 1)`.
- **Reducing along an axis.** `grid.sum()` everything; `grid.sum(axis=0)` down the rows, one value per column; `grid.mean(axis=1)` across the columns, one value per row. `argmax` gives the position of the largest.
- **Vectorize.** When you catch yourself writing `for i in range(len(values))` over numbers, ask what array operation says the same thing. It's shorter, it's what everyone else will read, and it's often a hundred times faster.
- **In machine learning:** a dataset is a 2-D array (rows are examples, columns are features); standardizing its columns is `(x - x.mean(axis=0)) / x.std(axis=0)`, this topic's build; a batch of images is a 4-D array, and `shape` is the first thing you print when something's wrong.

</Recap>
''',
)

# --- practice: recall --------------------------------------------------------

write(
    "recall/parsons-column-means.yaml",
    '''id: parsons-column-means
type: parsons
rev: 1
prompt: |
  Two students, two tests: `[[90, 80], [70, 60]]`, one row per student. Put the lines in order so the program prints the **average of each test**, `[80. 70.]`. One line is a decoy that doesn't belong.
lines:
  - 'import numpy as np'
  - 'scores = np.array([[90, 80], [70, 60]])'
  - 'means = scores.mean(axis=0)'
  - 'print(means)'
distractors:
  - 'means = scores.mean(axis=1)'
explanation: |
  `axis=0` collapses the rows: the mean runs **down** each column, giving one value per test, `[80. 70.]`. The decoy's `axis=1` runs across each row, one value per student, `[85. 65.]`. The axis you name is the one that disappears.
skills: [vectorize]
''',
)

write(
    "recall/mcq-shape.yaml",
    '''id: mcq-shape
type: mcq
rev: 1
prompt: |
  What is `np.array([[1, 2, 3], [4, 5, 6]]).shape`?
choices:
  - '`(3, 2)`'
  - '`(2, 3)`'
  - '`6`'
  - '`(2,)`'
answer: 1
explanation: |
  Two inner lists, so two rows; three numbers in each, so three columns: `(2, 3)`, rows first. `6` is the `size`, the total count. `(2,)` would be a one-dimensional array of two values.
skills: [make]
''',
)

write(
    "recall/predict-slices.yaml",
    '''id: predict-slices
type: predict_output
rev: 1
prompt: |
  A 3-by-3 grid, sliced four ways. What does the program print?
code: |
  import numpy as np

  grid = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
  print(grid[0])
  print(grid[:, 2])
  print(grid[1:, :2])
  print(grid[grid > 5])
expected_output: |
  [1 2 3]
  [3 6 9]
  [[4 5]
   [7 8]]
  [6 7 8 9]
explanation: |
  `grid[0]` is the first row. `grid[:, 2]` is every row's third value: the last column, as a one-dimensional array. `grid[1:, :2]` keeps rows from 1 on and columns before 2, a 2-by-2 block. `grid[grid > 5]` is a boolean mask: the values where the test holds, flattened into one dimension.
skills: [index]
''',
)

write(
    "recall/mcq-dtype-trap.yaml",
    '''id: mcq-dtype-trap
type: mcq
rev: 1
prompt: |
  ```python
  a = np.array([1, 2, 3])
  a[0] = 2.7
  print(a[0])
  ```

  What is printed?
choices:
  - '`2.7`'
  - '`2`'
  - '`3`'
  - 'An error: a float can''t go into an integer array'
answer: 1
explanation: |
  The array was made from whole numbers, so its dtype is an integer type, and every value must be one. Storing `2.7` keeps the whole part, `2`, with no error. If an array will ever hold a fraction, make it float from the start: `np.array([1.0, 2, 3])` or `dtype=float`.
skills: [make]
''',
)

write(
    "recall/mcq-broadcasting.yaml",
    '''id: mcq-broadcasting
type: mcq
rev: 1
prompt: |
  `grid` has shape `(3, 4)`: three rows, four columns. Which of these can be added to it with `grid + other`?
choices:
  - 'An array of shape `(3,)`'
  - 'An array of shape `(4,)`'
  - 'An array of shape `(2, 4)`'
  - 'An array of shape `(3, 3)`'
answer: 1
explanation: |
  Broadcasting lines the shapes up from the right: `(4,)` matches the last dimension, 4, and is stretched across the three rows, so the row is added to every row. `(3,)` against 4 doesn't match and isn't 1, so NumPy refuses; to add one value per row you'd need a column, shape `(3, 1)`. The other two have the wrong sizes outright.
skills: [elementwise]
''',
)

write(
    "recall/review-predict-broadcast-row.yaml",
    '''id: review-predict-broadcast-row
type: predict_output
rev: 1
prompt: |
  A 2-by-2 grid plus a row of two values. What does the program print?
code: |
  import numpy as np

  grid = np.array([[1, 2], [3, 4]])
  print(grid + np.array([10, 20]))
expected_output: |
  [[11 22]
   [13 24]]
explanation: |
  Shape `(2, 2)` plus shape `(2,)`: the row lines up with the last dimension and is stretched over both rows, so 10 is added down the first column and 20 down the second. That's broadcasting; no loop and no copy of the row.
skills: [elementwise]
''',
)

write(
    "recall/review-mcq-axis.yaml",
    '''id: review-mcq-axis
type: mcq
rev: 1
prompt: |
  `grid` has shape `(2, 3)`. What does `grid.mean(axis=0)` give?
choices:
  - 'One number: the mean of all six values'
  - 'Three numbers: the mean of each column'
  - 'Two numbers: the mean of each row'
  - 'A `(2, 3)` array of the same values'
answer: 1
explanation: |
  The axis you name is the one that collapses. `axis=0` is the rows, so the mean runs down each column and one value per column is left: three. `axis=1` would collapse the columns, leaving one mean per row: two. No axis at all gives a single number.
skills: [vectorize]
''',
)

write(
    "recall/review-predict-arange-linspace.yaml",
    '''id: review-predict-arange-linspace
type: predict_output
rev: 1
prompt: |
  Two ways to make a run of numbers. What does the program print?
code: |
  import numpy as np

  print(np.arange(0, 10, 2))
  print(np.linspace(0, 1, 3))
expected_output: |
  [0 2 4 6 8]
  [0.  0.5 1. ]
explanation: |
  `arange(start, stop, step)` works like `range`: from 0, below 10, in steps of 2, whole numbers. `linspace(start, stop, count)` gives exactly `count` evenly spaced values **including** the stop, as floats: 0, 0.5 and 1. NumPy prints floats with the decimal point and pads them to line up.
skills: [make]
''',
)

# --- practice: exercises -------------------------------------------------------

write(
    "exercises/example-arrays-and-shapes/exercise.yaml",
    '''id: example-arrays-and-shapes
stage: worked_example
rev: 1
title: "Arrays and shapes"
prompt: |
  This program makes arrays, reads their shapes, slices a grid, does arithmetic on whole arrays and reduces along an axis. Press **Run**, then read how each part works. (The first Run on this topic downloads NumPy, once.)
steps:
  - label: "An array has a shape and one dtype"
    lines: "3-5"
    note: "`np.array` turns a list into an array. Its `shape` is `(3,)`, three values along one dimension, and its `dtype` is `float64`: every value in an array has the same type."
  - label: "Two dimensions"
    lines: "7-10"
    note: "Nested lists make a 2-D array of shape `(2, 3)`: two rows, three columns. `grid[1, 2]` is one value, row 1 column 2; `grid[:, 0]` is the whole first column."
  - label: "Arithmetic on the whole array, and broadcasting"
    lines: "12-13"
    note: "`a * 2` doubles every value without a loop. Adding a row of three values to a grid of shape `(2, 3)` adds it to **each** row: that's broadcasting."
  - label: "Reducing along an axis"
    lines: "14-15"
    note: "`sum(axis=0)` runs down the rows and leaves one total per column; `mean(axis=1)` runs across the columns and leaves one mean per row. The axis you name is the one that disappears."
  - label: "Making arrays"
    lines: "17-18"
    note: "`arange` counts like `range`; `linspace` gives evenly spaced values including the end. Both are the usual way to make an x-axis."
''',
)
write(
    "exercises/example-arrays-and-shapes/solution.py",
    '''import numpy as np

a = np.array([1.5, 2.0, 3.5])
print(a)
print(a.shape, a.dtype)

grid = np.array([[1, 2, 3], [4, 5, 6]])
print(grid.shape)
print(grid[1, 2])
print(grid[:, 0])

print(a * 2)
print(grid + np.array([10, 20, 30]))
print(grid.sum(axis=0))
print(grid.mean(axis=1))

print(np.arange(5))
print(np.linspace(0, 1, 5))
''',
)
write(
    "exercises/example-arrays-and-shapes/test_exercise.py",
    '''from checks import run


def test_the_walkthrough():
    """Prints the arrays, shapes, slices, sums and ranges shown in the steps."""
    assert run() == (
        "[1.5 2.  3.5]\\n(3,) float64\\n(2, 3)\\n6\\n[1 4]\\n[3. 4. 7.]\\n"
        "[[11 22 33]\\n [14 25 36]]\\n[5 7 9]\\n[2. 5.]\\n"
        "[0 1 2 3 4]\\n[0.   0.25 0.5  0.75 1.  ]\\n"
    )
''',
)

write(
    "exercises/fill-normalize/exercise.yaml",
    '''id: fill-normalize
stage: fill_in
rev: 1
title: "Scale to 0..1"
prompt: |
  `normalize(values)` should scale an array so its smallest value becomes 0 and its largest 1, with everything else in proportion: subtract the minimum, then divide by the range. Replace each `...` so the program prints:

  ```
  [0.   0.25 0.5  1.  ]
  ```

  Until every `...` is replaced, Python can't run the program at all, and shows a syntax error.
hints:
  - "Subtract `low` from every value: `values - low` does that to the whole array at once."
  - "The range is `high - low`; dividing the whole array by it is one operation too."
skills: [elementwise]
''',
)
write(
    "exercises/fill-normalize/starter.py",
    '''import numpy as np


def normalize(values):
    low = values.min()
    high = values.max()
    return (values - ...) / (... - ...)


print(normalize(np.array([2.0, 4.0, 6.0, 10.0])))
''',
)
write(
    "exercises/fill-normalize/solution.py",
    '''import numpy as np


def normalize(values):
    low = values.min()
    high = values.max()
    return (values - low) / (high - low)


print(normalize(np.array([2.0, 4.0, 6.0, 10.0])))
''',
)
write(
    "exercises/fill-normalize/test_exercise.py",
    '''import numpy as np

from checks import function, run


def test_this_array():
    """Prints [0.   0.25 0.5  1.  ]."""
    printed = run()
    assert printed == "[0.   0.25 0.5  1.  ]\\n", f"Your program printed:\\n{printed}"


def test_other_arrays():
    """The smallest value becomes 0 and the largest 1, for other arrays too."""
    normalize = function("normalize")
    assert normalize(np.array([5.0, 10.0])).tolist() == [0.0, 1.0]
    assert normalize(np.array([3, 3, 9])).tolist() == [0.0, 0.0, 1.0]
''',
)
write(
    "exercises/fill-normalize/wrong/divides-by-the-max.py",
    '''import numpy as np


def normalize(values):
    low = values.min()
    high = values.max()
    return (values - low) / (high - 0)


print(normalize(np.array([2.0, 4.0, 6.0, 10.0])))
''',
)
write(
    "exercises/fill-normalize/wrong/typed-in.py",
    '''import numpy as np


def normalize(values):
    return np.array([0.0, 0.25, 0.5, 1.0])


print(normalize(np.array([2.0, 4.0, 6.0, 10.0])))
''',
)

write(
    "exercises/write-row-totals/exercise.yaml",
    '''id: write-row-totals
stage: write
rev: 1
title: "Totals by shop, and the best day"
prompt: |
  `sales` is a 2-D array with one row per shop and one column per day: `np.array([[10, 20, 30], [40, 50, 60]])`. Write `shop_totals(sales)`, which returns each shop's total as an array, and `best_day(sales)`, which returns the position (0, 1, 2, ...) of the day with the highest total across all shops. No loops: use `sum` with an axis and `argmax`. Then print both for that array:

  ```
  [ 60 150]
  2
  ```
hints:
  - "A shop is a row, so its total runs **across** the columns: `sales.sum(axis=1)`."
  - "A day is a column: `sales.sum(axis=0)` gives one total per day, and `.argmax()` the position of the largest."
skills: [vectorize]
''',
)
write("exercises/write-row-totals/starter.py", "import numpy as np\n\nsales = np.array([[10, 20, 30], [40, 50, 60]])\n")
write(
    "exercises/write-row-totals/solution.py",
    '''import numpy as np

sales = np.array([[10, 20, 30], [40, 50, 60]])


def shop_totals(sales):
    return sales.sum(axis=1)


def best_day(sales):
    return int(sales.sum(axis=0).argmax())


print(shop_totals(sales))
print(best_day(sales))
''',
)
write(
    "exercises/write-row-totals/test_exercise.py",
    '''import numpy as np

from checks import function, run


def test_the_output():
    """Prints [ 60 150], then 2."""
    printed = run()
    assert printed == "[ 60 150]\\n2\\n", f"Your program printed:\\n{printed}"


def test_other_sales():
    """Works for three shops and two days: totals per shop, and the best day's position."""
    shop_totals = function("shop_totals")
    best_day = function("best_day")
    sales = np.array([[5, 1], [1, 1], [0, 9]])
    assert shop_totals(sales).tolist() == [6, 2, 9]
    assert best_day(sales) == 1
''',
)
write(
    "exercises/write-row-totals/wrong/axis-swapped.py",
    '''import numpy as np

sales = np.array([[10, 20, 30], [40, 50, 60]])


def shop_totals(sales):
    return sales.sum(axis=0)


def best_day(sales):
    return int(sales.sum(axis=1).argmax())


print(shop_totals(sales))
print(best_day(sales))
''',
)
write(
    "exercises/write-row-totals/wrong/typed-in.py",
    '''import numpy as np

sales = np.array([[10, 20, 30], [40, 50, 60]])


def shop_totals(sales):
    return np.array([60, 150])


def best_day(sales):
    return 2


print("[ 60 150]")
print(2)
''',
)

# --- proof ------------------------------------------------------------------

write(
    "exercises/build-standardize/exercise.yaml",
    '''id: build-standardize
stage: build
rev: 1
title: "Standardize the columns"
prompt: |
  Machine-learning models like every feature on the same scale. Starting from a blank editor, write `standardize(grid)`: for a 2-D array with one column per feature, return a new array in which each column has had its own mean subtracted and been divided by its own standard deviation (`std()`), so every column ends with mean 0 and standard deviation 1. No loops: one expression with `mean`, `std`, an axis and broadcasting.

  Then print the result for `np.array([[1.0, 10.0], [2.0, 20.0], [3.0, 30.0]])`, rounded to 2 decimal places with `np.round`:

  ```
  [[-1.22 -1.22]
   [ 0.    0.  ]
   [ 1.22  1.22]]
  ```

  The checks call `standardize` with other grids, including one with a single column, and check every column's mean and spread.
skills: [elementwise, vectorize]
''',
)
write("exercises/build-standardize/starter.py", "")
write(
    "exercises/build-standardize/solution.py",
    '''import numpy as np


def standardize(grid):
    return (grid - grid.mean(axis=0)) / grid.std(axis=0)


grid = np.array([[1.0, 10.0], [2.0, 20.0], [3.0, 30.0]])
print(np.round(standardize(grid), 2))
''',
)
write(
    "exercises/build-standardize/test_exercise.py",
    '''import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints the standardized grid, rounded."""
    assert run() == "[[-1.22 -1.22]\\n [ 0.    0.  ]\\n [ 1.22  1.22]]\\n"


def test_columns_end_with_mean_0_and_std_1():
    """Every column of a 4-by-3 grid ends with mean 0 and standard deviation 1, and the shape is kept."""
    standardize = function("standardize")
    grid = np.array([[2.0, 100.0, -1.0], [4.0, 150.0, 0.0], [6.0, 50.0, 3.0], [8.0, 200.0, 2.0]])
    result = standardize(grid)
    assert result.shape == (4, 3)
    assert np.allclose(result.mean(axis=0), 0)
    assert np.allclose(result.std(axis=0), 1)


def test_one_column():
    """A single column works, and the original grid is left unchanged."""
    standardize = function("standardize")
    grid = np.array([[1.0], [3.0], [5.0]])
    result = standardize(grid)
    assert np.allclose(result[:, 0], [-1.2247, 0.0, 1.2247], atol=1e-3)
    assert grid.tolist() == [[1.0], [3.0], [5.0]]
''',
)
write(
    "exercises/build-standardize/wrong/by-rows.py",
    '''import numpy as np


def standardize(grid):
    return (grid - grid.mean(axis=1, keepdims=True)) / grid.std(axis=1, keepdims=True)


grid = np.array([[1.0, 10.0], [2.0, 20.0], [3.0, 30.0]])
print(np.round(standardize(grid), 2))
''',
)
write(
    "exercises/build-standardize/wrong/no-std.py",
    '''import numpy as np


def standardize(grid):
    return grid - grid.mean(axis=0)


grid = np.array([[1.0, 10.0], [2.0, 20.0], [3.0, 30.0]])
print(np.round(standardize(grid), 2))
''',
)
write(
    "exercises/build-standardize/wrong/typed-in.py",
    '''import numpy as np


def standardize(grid):
    return np.array([[-1.22, -1.22], [0.0, 0.0], [1.22, 1.22]])


print("[[-1.22 -1.22]")
print(" [ 0.    0.  ]")
print(" [ 1.22  1.22]]")
''',
)

write(
    "exercises/debug-axis-mistakes/exercise.yaml",
    '''id: debug-axis-mistakes
stage: debug
rev: 1
title: "The axis mistakes"
prompt: |
  `report(grid)` takes sales with one row per shop and one column per day, and should print the average of each day, how far each sale was above its day's average, and which day (counting from 1) sold the most in total:

  ```
  daily averages: [20. 30. 50.]
  above average:
  [[-5. -5.  5.]
   [ 5.  5. -5.]]
  best day: 3
  ```

  It has two bugs, both about which axis a calculation runs along. Run it, read the shape error, fix it, run again, and check the last line against the numbers by hand.
skills: [vectorize, elementwise]
''',
)
REPORT_TAIL = '''

report(np.array([[15, 25, 55], [25, 35, 45]]))
'''
write(
    "exercises/debug-axis-mistakes/starter.py",
    '''import numpy as np


def report(grid):
    daily = grid.mean(axis=1)
    print("daily averages:", daily)
    print("above average:")
    print(grid - daily)
    best = grid.sum(axis=1).argmax() + 1
    print("best day:", best)
''' + REPORT_TAIL,
)
write(
    "exercises/debug-axis-mistakes/solution.py",
    '''import numpy as np


def report(grid):
    daily = grid.mean(axis=0)
    print("daily averages:", daily)
    print("above average:")
    print(grid - daily)
    best = grid.sum(axis=0).argmax() + 1
    print("best day:", best)
''' + REPORT_TAIL,
)
write(
    "exercises/debug-axis-mistakes/test_exercise.py",
    '''import numpy as np

from checks import function, printed, run

EXPECTED = "daily averages: [20. 30. 50.]\\nabove average:\\n[[-5. -5.  5.]\\n [ 5.  5. -5.]]\\nbest day: 3\\n"


def test_the_output():
    """Prints the daily averages, the differences and the best day."""
    out = run()
    assert out == EXPECTED, f"Expected this:\\n{EXPECTED}\\nYour program printed:\\n{out}"


def test_other_grid():
    """Works for two shops and two days."""
    out = printed(function("report"), np.array([[1, 2], [3, 8]]))
    assert out == "daily averages: [2. 5.]\\nabove average:\\n[[-1. -3.]\\n [ 1.  3.]]\\nbest day: 2\\n", (
        f"For [[1, 2], [3, 8]] it printed:\\n{out}"
    )
''',
)
write(
    "exercises/debug-axis-mistakes/wrong/one-of-two.py",
    '''import numpy as np


def report(grid):
    daily = grid.mean(axis=0)
    print("daily averages:", daily)
    print("above average:")
    print(grid - daily)
    best = grid.sum(axis=1).argmax() + 1
    print("best day:", best)
''' + REPORT_TAIL,
)
write(
    "exercises/debug-axis-mistakes/wrong/typed-in.py",
    '''import numpy as np


def report(grid):
    print("daily averages: [20. 30. 50.]")
    print("above average:")
    print("[[-5. -5.  5.]")
    print(" [ 5.  5. -5.]]")
    print("best day: 3")
''' + REPORT_TAIL,
)

# --- review pool: a code exercise -------------------------------------------

write(
    "exercises/review-double-evens/exercise.yaml",
    '''id: review-double-evens
stage: review_code
rev: 1
title: "Double the evens"
prompt: |
  Write `double_evens(values)`, which returns the even values of an array, doubled, using a boolean mask (no loop). Then print it for the array in the starter:

  ```
  [ 4  8 12]
  ```
skills: [index, elementwise]
''',
)
write("exercises/review-double-evens/starter.py", "import numpy as np\n\nvalues = np.array([1, 2, 3, 4, 5, 6])\n")
write(
    "exercises/review-double-evens/solution.py",
    '''import numpy as np

values = np.array([1, 2, 3, 4, 5, 6])


def double_evens(values):
    return values[values % 2 == 0] * 2


print(double_evens(values))
''',
)
write(
    "exercises/review-double-evens/test_exercise.py",
    '''import numpy as np

from checks import function, run


def test_the_output():
    """Prints [ 4  8 12]."""
    assert run() == "[ 4  8 12]\\n"


def test_other_values():
    """Keeps only the evens, doubled; an array with no evens gives an empty array."""
    double_evens = function("double_evens")
    assert double_evens(np.array([7, 10])).tolist() == [20]
    assert double_evens(np.array([1, 3])).tolist() == []
''',
)
write(
    "exercises/review-double-evens/wrong/doubles-everything.py",
    '''import numpy as np

values = np.array([1, 2, 3, 4, 5, 6])


def double_evens(values):
    return values * 2


print(double_evens(values))
''',
)
write(
    "exercises/review-double-evens/wrong/typed-in.py",
    '''import numpy as np

values = np.array([1, 2, 3, 4, 5, 6])


def double_evens(values):
    return np.array([4, 8, 12])


print("[ 4  8 12]")
''',
)

print("ml.la.numpy-arrays written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
