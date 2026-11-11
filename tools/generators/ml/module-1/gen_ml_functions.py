"""Writes the topic ml.math.functions (the ML track's third topic). Run from
the repository root. Files are written as bytes with LF endings."""

import pathlib

ROOT = pathlib.Path("content/topics/ml.math.functions")


def write(relative: str, text: str) -> None:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


write(
    "topic.yaml",
    '''id: ml.math.functions
kind: topic
status: ready
title: "Functions"
summary: "A function as a rule from input to output: lines, tables of values and composition."
prerequisites: [ml.math.algebra, py.return-values]
estimated_minutes: 45
rev: 1
objectives:
  - "Treat a function as a rule from input to output, and evaluate it."
  - "Read a line's slope and intercept, and say what each means."
  - "Put one function inside another."
  - "Make a table of values with a loop."
resources:
  - title: "OpenStax Intermediate Algebra 2e: chapter 3 (Graphs and Functions), sections 3.1 to 3.5"
    url: https://openstax.org/details/books/intermediate-algebra-2e
    type: reading
    use: link
    license: CC BY 4.0
  - title: "Khan Academy: College Algebra"
    url: https://www.khanacademy.org/math/college-algebra
    type: interactive
    use: link
    license: CC BY-NC-SA 3.0 US (linked, not copied)
practice:
  - example-function-as-a-rule
  - parsons-table-of-squares
  - mcq-slope-and-intercept
  - predict-compose
  - mcq-slope-from-two-points
  - fill-line-through-points
  - write-celsius-table
prove:
  build: build-delivery-cost
  debug: debug-half-then-ten
  explain:
    prompt: |
      In math class a function is written `f(x) = 2x + 1`, and in Python it's

      ```python
      def f(x):
          return 2 * x + 1
      ```

      In your own words: what does `f(3)` mean, and what is it? What do the math version and the Python version have in common? If `g(x) = x + 1`, what is `f(g(2))`, how did you work it out, and is it the same as `g(f(2))`?
    rubric:
      - id: rule
        required: true
        description: "A function is a rule that turns an input into one output; f(3) means put 3 in for x, giving 2 × 3 + 1 = 7."
      - id: same-thing
        required: true
        description: "The Python def is the same rule: it takes x in, returns 2 * x + 1, and the same input always gives the same output."
      - id: compose
        required: true
        description: "f(g(2)) is worked out from the inside: g(2) = 3, then f(3) = 7."
      - id: order
        required: true
        description: "g(f(2)) is different: f(2) = 5, then g(5) = 6; the order of composition matters."
      - id: table
        required: false
        description: "Mentions that evaluating a function for several inputs gives a table of values, or that a line's rule has a slope and a starting value."
    model_answer: |
      A function is a rule: put a number in, get exactly one number out. f(3) means "use 3 as x": 2 × 3 + 1, which is 7. The Python def is the same rule written for the computer: x comes in as the parameter, 2 * x + 1 goes out through return, and the same input always gives the same output, so f(3) is 7 every time. f(g(2)) is a function inside a function; work from the inside out: g(2) is 2 + 1 = 3, then f(3) is 7. The other order gives something else: f(2) is 5, then g(5) is 6, so g(f(2)) is 6. Which function you apply first matters. Evaluating f for 0, 1, 2, 3 in a loop gives a table of values, which is what a graph is made of.
review_pool:
  - review-predict-evaluate
  - review-mcq-intercept
  - review-line-table
# What this topic teaches. Each question names the skills it tests, so a
# missed question can come back as a different one on the same skill
# (ADR-0011).
skills:
  - id: evaluate
    description: "Treat a function as a rule from input to output, and evaluate it"
  - id: lines
    description: "Read a line's slope and intercept, from its rule or from two points, and say what each means"
  - id: compose
    description: "Put one function inside another, working from the inside out"
  - id: table
    description: "Make a table of a function's values with a loop"
''',
)

write(
    "lesson.mdx",
    '''<Intro>

You already write functions in Python. The math word means the same thing: a rule that takes an input and gives back exactly one output. `f(x) = 2x + 1` and `def f(x): return 2 * x + 1` are one rule in two notations, and everything machine learning fits is a function: inputs in, a prediction out.

The main resource is the free textbook *OpenStax Intermediate Algebra 2e*, **chapter 3, Graphs and Functions**, sections 3.1 to 3.5. Read them lightly; the ideas matter more than the notation. About 25 minutes. Watch for:

- **A line's rule has two numbers.** In `y = mx + b`, `m` is the slope (how much y changes for each step of 1 in x) and `b` is where the line crosses the y-axis (the value when x is 0).
- **Slope from two points:** rise over run, the change in y divided by the change in x.
- **Function notation.** `f(3)` means "the output of f when the input is 3". A function inside a function, `f(g(x))`, is worked out from the inside.
- **A graph is a table of values,** one row per x, drawn.

Everything here runs in Python: you'll evaluate, compose and tabulate functions with code, and check the book's pictures with numbers.

</Intro>

<Resource index={0} />

<Recap>

- **A function is a rule: input in, one output out.** `f(x) = 2x + 1` in math is `def f(x): return 2 * x + 1` in Python. `f(3)` is 7 in both. The same input always gives the same output.
- **A table of values is a loop.** `for x in range(0, 4): print(x, f(x))` prints the rows a graph is drawn from. Change the range to zoom in or out.
- **Lines: `y = m * x + b`.** `m` is the **slope**: y changes by m for every 1 of x. `b` is the **intercept**: y when x is 0. In a taxi fare `2.5 * km + 4`, 2.5 is the price per kilometre and 4 is the flag fall.
- **Slope from two points** `(x1, y1)` and `(x2, y2)`: `(y2 - y1) / (x2 - x1)`, the rise over the run. Then the intercept is `y1 - slope * x1`.
- **Composition** `f(g(x))` works from the inside out: find `g(x)`, then put that into f. In Python it's just `f(g(2))`. Order matters: `g(f(2))` is usually different.
- **Later, in machine learning:** a model is a function with knobs (the slope and intercept of a line are the first two knobs you'll ever fit), and "training" means turning the knobs until the table of outputs matches the data.

</Recap>
''',
)

# --- practice: recall --------------------------------------------------------

write(
    "recall/parsons-table-of-squares.yaml",
    '''id: parsons-table-of-squares
type: parsons
rev: 1
prompt: |
  Put the lines in order so the program prints a table of squares: `1 1`, then `2 4`, then `3 9`. One line is a decoy that doesn't belong.
lines:
  - 'def square(x):'
  - '    return x * x'
  - 'for x in range(1, 4):'
  - '    print(x, square(x))'
distractors:
  - '    return x + x'
explanation: |
  The function is the rule, `x * x`, defined first so the loop can call it. The loop is the table: for each x from 1 to 3 it prints the input and the output. The decoy, `x + x`, is doubling, which would print `2 4 6` in the second column.
skills: [table, evaluate]
''',
)

write(
    "recall/mcq-slope-and-intercept.yaml",
    '''id: mcq-slope-and-intercept
type: mcq
rev: 1
prompt: |
  A taxi's fare is `fare = 2.5 * km + 4`. What do the two numbers mean?
choices:
  - '2.5 is the charge for getting in; 4 is the price per kilometre'
  - '2.5 is the price per kilometre; 4 is the charge for getting in'
  - '2.5 is the fare for a 4 km trip'
  - '4 is the most kilometres the fare covers'
answer: 1
explanation: |
  The number multiplying `km` is the slope: the fare goes up by 2.5 for every kilometre. The number on its own is the intercept: the fare when km is 0, the 4 you pay for getting in. Check with a 2 km trip: 2.5 × 2 + 4 is 9.
skills: [lines]
''',
)

write(
    "recall/predict-compose.yaml",
    '''id: predict-compose
type: predict_output
rev: 1
prompt: |
  One function inside another, both ways round. What does the program print?
code: |
  def square(x):
      return x * x


  def plus_one(x):
      return x + 1


  print(square(plus_one(2)))
  print(plus_one(square(2)))
expected_output: |
  9
  5
explanation: |
  Work from the inside out. `square(plus_one(2))`: first `plus_one(2)` is 3, then `square(3)` is `9`. The other way round, `square(2)` is 4 first, then `plus_one(4)` is `5`. Which function goes first changes the answer.
skills: [compose, evaluate]
''',
)

write(
    "recall/mcq-slope-from-two-points.yaml",
    '''id: mcq-slope-from-two-points
type: mcq
rev: 1
prompt: |
  A line goes through the points (0, 4) and (2, 10). What is its slope?
choices:
  - '6'
  - '2'
  - '3'
  - '0.5'
answer: 2
explanation: |
  Slope is rise over run: y goes from 4 to 10, a rise of 6, while x goes from 0 to 2, a run of 2. `(10 - 4) / (2 - 0)` is `3`: y goes up by 3 for every 1 of x. (And since the line passes through x = 0 at y = 4, its intercept is 4: the line is `y = 3x + 4`.)
skills: [lines]
''',
)

write(
    "recall/review-predict-evaluate.yaml",
    '''id: review-predict-evaluate
type: predict_output
rev: 1
prompt: |
  A function evaluated twice, the second time on its own output. What does the program print?
code: |
  def h(x):
      return 3 * x - 2


  print(h(4))
  print(h(h(1)))
expected_output: |
  10
  1
explanation: |
  `h(4)` is 3 × 4 − 2, which is `10`. For `h(h(1))`, work from the inside: `h(1)` is 3 × 1 − 2 = 1, and then `h(1)` again is `1`. A function applied to its own output is still just a function call, evaluated inside out.
skills: [evaluate, compose]
''',
)

write(
    "recall/review-mcq-intercept.yaml",
    '''id: review-mcq-intercept
type: mcq
rev: 1
prompt: |
  Where does the line `y = 0.5 * x + 7` cross the y-axis, and what is its slope?
choices:
  - 'It crosses at y = 0.5; the slope is 7'
  - 'It crosses at y = 7; the slope is 0.5'
  - 'It crosses at y = 7.5; the slope is 1'
  - 'It crosses at y = 0; the slope is 0.5'
answer: 1
explanation: |
  The y-axis is where x is 0, and `0.5 * 0 + 7` is 7: the intercept. The slope is the number multiplying x, `0.5`: y rises by half for each step of 1 in x.
skills: [lines]
''',
)

# --- practice: exercises -------------------------------------------------------

write(
    "exercises/example-function-as-a-rule/exercise.yaml",
    '''id: example-function-as-a-rule
stage: worked_example
rev: 1
title: "A function is a rule"
prompt: |
  This program defines the function `f(x) = 2x + 1`, evaluates it, and prints a table of its values. Press **Run**, then read how each part works.
steps:
  - label: "The rule"
    lines: "1-2"
    note: "`def f(x)` names the input and `return 2 * x + 1` gives the output. This is exactly the math notation `f(x) = 2x + 1`, with the multiplication written out."
  - label: "Evaluate it"
    lines: "5-7"
    note: "`f(3)` means put 3 in for x: 2 × 3 + 1 is 7. The same input always gives the same output: `f(0)` is 1, and `f(-2)` is -3."
  - label: "A table of values"
    lines: "9-10"
    note: "The loop evaluates f for x = 0, 1, 2, 3 and prints each pair. That table is what a graph of f is drawn from: each row is one point."
''',
)
write(
    "exercises/example-function-as-a-rule/solution.py",
    '''def f(x):
    return 2 * x + 1


print(f(3))
print(f(0))
print(f(-2))

for x in range(0, 4):
    print(x, f(x))
''',
)
write(
    "exercises/example-function-as-a-rule/test_exercise.py",
    '''from checks import run


def test_evaluates_and_tabulates():
    """Prints 7, 1 and -3, then the table from 0 to 3."""
    assert run() == "7\\n1\\n-3\\n0 1\\n1 3\\n2 5\\n3 7\\n"
''',
)

write(
    "exercises/fill-line-through-points/exercise.yaml",
    '''id: fill-line-through-points
stage: fill_in
rev: 1
title: "The line through two points"
prompt: |
  A line goes through (1, 7) and (3, 13). Replace each `...` so the program works out its slope and intercept and prints the line's rule:

  ```
  y = 3.0x + 4.0
  ```

  Until every `...` is replaced, Python can't run the program at all, and shows a syntax error.
hints:
  - "The slope is rise over run: the change in y divided by the change in x."
  - "Once you have the slope, the intercept is `y1 - slope * x1`: start from a point you know and undo the slope's share."
skills: [lines]
''',
)
write(
    "exercises/fill-line-through-points/starter.py",
    '''x1 = 1
y1 = 7
x2 = 3
y2 = 13
slope = (y2 ... y1) / (x2 ... x1)
intercept = y1 ... slope * x1
print(f"y = {slope}x + {intercept}")
''',
)
write(
    "exercises/fill-line-through-points/solution.py",
    '''x1 = 1
y1 = 7
x2 = 3
y2 = 13
slope = (y2 - y1) / (x2 - x1)
intercept = y1 - slope * x1
print(f"y = {slope}x + {intercept}")
''',
)
write(
    "exercises/fill-line-through-points/test_exercise.py",
    '''from checks import run, run_with


def test_these_points():
    """Prints y = 3.0x + 4.0."""
    printed = run()
    assert printed == "y = 3.0x + 4.0\\n", f"Your program printed:\\n{printed}"


def test_any_points():
    """Works for any two points: (0, 2) and (4, 10) give y = 2.0x + 2.0."""
    printed = run_with({"x1": 0, "y1": 2, "x2": 4, "y2": 10})
    assert printed == "y = 2.0x + 2.0\\n", (
        f"Through (0, 2) and (4, 10) it should print y = 2.0x + 2.0. It printed:\\n{printed}"
    )
''',
)
write(
    "exercises/fill-line-through-points/wrong/run-over-rise.py",
    '''x1 = 1
y1 = 7
x2 = 3
y2 = 13
slope = (x2 - x1) / (y2 - y1)
intercept = y1 - slope * x1
print(f"y = {slope}x + {intercept}")
''',
)
write(
    "exercises/fill-line-through-points/wrong/typed-in.py",
    '''x1 = 1
y1 = 7
x2 = 3
y2 = 13
slope = 3.0
intercept = 4.0
print(f"y = {slope}x + {intercept}")
''',
)

write(
    "exercises/write-celsius-table/exercise.yaml",
    '''id: write-celsius-table
stage: write
rev: 1
title: "A conversion table"
prompt: |
  Write a function `to_fahrenheit(celsius)` that returns the Fahrenheit value, `celsius * 9 / 5 + 32`. Then print a table for 0, 25, 50, 75 and 100 degrees Celsius, one line each, with one decimal place:

  ```
  0 C = 32.0 F
  25 C = 77.0 F
  50 C = 122.0 F
  75 C = 167.0 F
  100 C = 212.0 F
  ```
hints:
  - "`def to_fahrenheit(celsius):` then `return celsius * 9 / 5 + 32`."
  - "`range(0, 101, 25)` counts 0, 25, 50, 75, 100: the third number is the step."
  - "In the loop, print an f-string that uses the function: `f\\"{c} C = {to_fahrenheit(c):.1f} F\\"`."
skills: [table, evaluate]
''',
)
write("exercises/write-celsius-table/starter.py", "")
write(
    "exercises/write-celsius-table/solution.py",
    '''def to_fahrenheit(celsius):
    return celsius * 9 / 5 + 32


for c in range(0, 101, 25):
    print(f"{c} C = {to_fahrenheit(c):.1f} F")
''',
)
write(
    "exercises/write-celsius-table/test_exercise.py",
    '''from checks import function, run

TABLE = "0 C = 32.0 F\\n25 C = 77.0 F\\n50 C = 122.0 F\\n75 C = 167.0 F\\n100 C = 212.0 F\\n"


def test_the_function():
    """to_fahrenheit(100) is 212.0, and to_fahrenheit(-40) is -40.0."""
    to_fahrenheit = function("to_fahrenheit")
    assert to_fahrenheit(100) == 212.0, f"to_fahrenheit(100) returned {to_fahrenheit(100)}"
    assert to_fahrenheit(-40) == -40.0, f"to_fahrenheit(-40) returned {to_fahrenheit(-40)}"


def test_the_table():
    """Prints the five rows from 0 C to 100 C."""
    printed = run()
    assert printed == TABLE, f"Expected this:\\n{TABLE}\\nYour program printed:\\n{printed}"
''',
)
write(
    "exercises/write-celsius-table/wrong/wrong-step.py",
    '''def to_fahrenheit(celsius):
    return celsius * 9 / 5 + 32


for c in range(0, 100, 25):
    print(f"{c} C = {to_fahrenheit(c):.1f} F")
''',
)
write(
    "exercises/write-celsius-table/wrong/typed-in.py",
    '''def to_fahrenheit(celsius):
    return celsius * 9 / 5 + 32


print("0 C = 32.0 F")
print("25 C = 77.0 F")
print("50 C = 122.0 F")
print("75 C = 167.0 F")
print("100 C = 212.0 F")
''',
)

# --- proof ------------------------------------------------------------------

write(
    "exercises/build-delivery-cost/exercise.yaml",
    '''id: build-delivery-cost
stage: build
rev: 1
title: "Delivery cost"
prompt: |
  A courier charges 3.00 to pick a parcel up, plus 1.20 per kilometre. Starting from a blank editor, write a function `cost(km)` that returns the charge for a trip of `km` kilometres, then print a table for 1, 5 and 10 kilometres, each with two decimal places:

  ```
  1 km: 4.20
  5 km: 9.00
  10 km: 15.00
  ```

  The checks call your function with other distances too.
skills: [lines, evaluate, table]
''',
)
write("exercises/build-delivery-cost/starter.py", "")
write(
    "exercises/build-delivery-cost/solution.py",
    '''def cost(km):
    return 3.0 + 1.2 * km


for km in (1, 5, 10):
    print(f"{km} km: {cost(km):.2f}")
''',
)
write(
    "exercises/build-delivery-cost/test_exercise.py",
    '''from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_table():
    """Prints the charge for 1, 5 and 10 km."""
    assert run() == "1 km: 4.20\\n5 km: 9.00\\n10 km: 15.00\\n"


def test_the_function():
    """cost(0) is the pick-up charge, and cost(2.5) is 6.0."""
    cost = function("cost")
    assert cost(0) == 3.0
    assert cost(2.5) == 6.0
''',
)
write(
    "exercises/build-delivery-cost/wrong/no-pickup-charge.py",
    '''def cost(km):
    return 1.2 * km


for km in (1, 5, 10):
    print(f"{km} km: {cost(km):.2f}")
''',
)
write(
    "exercises/build-delivery-cost/wrong/slope-and-intercept-swapped.py",
    '''def cost(km):
    return 1.2 + 3.0 * km


for km in (1, 5, 10):
    print(f"{km} km: {cost(km):.2f}")
''',
)
write(
    "exercises/build-delivery-cost/wrong/typed-in.py",
    '''def cost(km):
    return 4.2


print("1 km: 4.20")
print("5 km: 9.00")
print("10 km: 15.00")
''',
)

write(
    "exercises/debug-half-then-ten/exercise.yaml",
    '''id: debug-half-then-ten
stage: debug
rev: 1
title: "Half, then ten"
prompt: |
  This program should halve a number and add ten, first for 8, then in a table for 1, 2 and 3:

  ```
  14.0
  1 10.5
  2 11.0
  3 11.5
  ```

  It has two bugs. Run it, fix what you find, and run it again. Compare every row with what the functions should give.
skills: [compose, table]
''',
)
write(
    "exercises/debug-half-then-ten/starter.py",
    '''def half(x):
    return x // 2


def plus_ten(x):
    return x + 10


print(plus_ten(half(8)))

for x in range(1, 3):
    print(x, plus_ten(half(x)))
''',
)
write(
    "exercises/debug-half-then-ten/solution.py",
    '''def half(x):
    return x / 2


def plus_ten(x):
    return x + 10


print(plus_ten(half(8)))

for x in range(1, 4):
    print(x, plus_ten(half(x)))
''',
)
write(
    "exercises/debug-half-then-ten/test_exercise.py",
    '''from checks import function, run

EXPECTED = "14.0\\n1 10.5\\n2 11.0\\n3 11.5\\n"


def test_the_output():
    """Prints 14.0, then the three rows of the table."""
    printed = run()
    assert printed == EXPECTED, (
        f"Expected this:\\n{EXPECTED}\\nYour program printed:\\n{printed}"
    )


def test_half_of_an_odd_number():
    """half(5) is 2.5, not 2."""
    half = function("half")
    assert half(5) == 2.5, f"half(5) returned {half(5)}"
''',
)
write(
    "exercises/debug-half-then-ten/wrong/only-range-fixed.py",
    '''def half(x):
    return x // 2


def plus_ten(x):
    return x + 10


print(plus_ten(half(8)))

for x in range(1, 4):
    print(x, plus_ten(half(x)))
''',
)
write(
    "exercises/debug-half-then-ten/wrong/only-half-fixed.py",
    '''def half(x):
    return x / 2


def plus_ten(x):
    return x + 10


print(plus_ten(half(8)))

for x in range(1, 3):
    print(x, plus_ten(half(x)))
''',
)
write(
    "exercises/debug-half-then-ten/wrong/typed-in.py",
    '''def half(x):
    return x // 2


def plus_ten(x):
    return x + 10


print("14.0")
print("1 10.5")
print("2 11.0")
print("3 11.5")
''',
)

# --- review pool: a code exercise -------------------------------------------

write(
    "exercises/review-line-table/exercise.yaml",
    '''id: review-line-table
stage: review_code
rev: 1
title: "A line, tabulated"
prompt: |
  Starting from `m = 2` and `b = -3`, print the table of `y = m * x + b` for x from 0 to 3, one row per line, the x then the y:

  ```
  0 -3
  1 -1
  2 1
  3 3
  ```

  Keep the two starting lines: the checks run your program with other lines too.
skills: [table, lines]
''',
)
write("exercises/review-line-table/starter.py", "m = 2\nb = -3\n")
write(
    "exercises/review-line-table/solution.py",
    '''m = 2
b = -3
for x in range(0, 4):
    print(x, m * x + b)
''',
)
write(
    "exercises/review-line-table/test_exercise.py",
    '''from checks import run, run_with


def test_this_line():
    """Prints the four rows for y = 2x - 3."""
    assert run() == "0 -3\\n1 -1\\n2 1\\n3 3\\n"


def test_any_line():
    """Works for any m and b: y = x gives 0 0, 1 1, 2 2, 3 3."""
    assert run_with({"m": 1, "b": 0}) == "0 0\\n1 1\\n2 2\\n3 3\\n"
''',
)
write(
    "exercises/review-line-table/wrong/stops-early.py",
    '''m = 2
b = -3
for x in range(0, 3):
    print(x, m * x + b)
''',
)
write(
    "exercises/review-line-table/wrong/typed-in.py",
    '''m = 2
b = -3
print("0 -3")
print("1 -1")
print("2 1")
print("3 3")
''',
)

print("ml.math.functions written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
