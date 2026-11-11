"""Writes the topic ml.math.algebra (the ML track's second topic). Run from
the repository root. Files are written as bytes with LF endings."""

import pathlib

ROOT = pathlib.Path("content/topics/ml.math.algebra")


def write(relative: str, text: str) -> None:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


write(
    "topic.yaml",
    '''id: ml.math.algebra
kind: topic
status: ready
title: "Algebra"
summary: "Solve equations by undoing, check by substituting, and rearrange formulas."
prerequisites: [ml.math.arithmetic]
estimated_minutes: 45
rev: 1
objectives:
  - "Solve a linear equation by undoing what was done to the unknown."
  - "Check an answer by substituting it back."
  - "Rearrange a formula to make another variable the subject."
  - "Apply the rules for multiplying powers."
resources:
  - title: "OpenStax Elementary Algebra 2e: chapter 2 (Solving Linear Equations and Inequalities) and section 6.2 (Use Multiplication Properties of Exponents)"
    url: https://openstax.org/details/books/elementary-algebra-2e
    type: reading
    use: link
    license: CC BY 4.0
  - title: "Khan Academy: Algebra 1"
    url: https://www.khanacademy.org/math/algebra
    type: interactive
    use: link
    license: CC BY-NC-SA 3.0 US (linked, not copied)
practice:
  - example-undo-the-equation
  - parsons-solve-for-x
  - mcq-undo-order
  - predict-rearranged-formula
  - mcq-exponent-rules
  - fill-fahrenheit-to-celsius
  - write-savings-goal
prove:
  build: build-interest-rearranged
  debug: debug-temperature-conversion
  explain:
    prompt: |
      A friend wants to solve `5x - 3 = 17` and types this:

      ```python
      x = 17 - 3 / 5
      print(x)
      ```

      It prints `16.4`, which can't be right. In your own words: what is the correct way to undo `5x - 3`, in what order and why, what line of Python does it, and how would you check the answer without trusting yourself?
    rubric:
      - id: reverse-order
        required: true
        description: "Undo in the reverse of the order the operations were done: the 3 was subtracted last, so add 3 first (giving 20), then divide by 5 (giving 4)."
      - id: parentheses
        required: true
        description: "In Python that needs parentheses, x = (17 + 3) / 5, because / happens before + otherwise."
      - id: friends-error
        required: true
        description: "The friend's line divides only the 3 by 5 (0.6) and subtracts that from 17, and subtracts instead of adding."
      - id: substitute
        required: true
        description: "Check by substituting: 5 * 4 - 3 should give 17, and Python can print that."
      - id: both-sides
        required: false
        description: "Says why undoing works: doing the same thing to both sides keeps the equation true."
    model_answer: |
      The equation says: take x, multiply by 5, then subtract 3, and you get 17. To find x, undo those in reverse order, doing the same to both sides so the equation stays true. The subtraction was done last, so undo it first: add 3 to both sides, giving 5x = 20. Then undo the multiplication: divide both sides by 5, giving x = 4. In Python that's x = (17 + 3) / 5; the parentheses matter because without them Python divides first. The friend's line does the division first, 3 / 5 = 0.6, and then subtracts it from 17, so it also has the sign wrong: 16.4. To check an answer, substitute it back: print(5 * x - 3) should show 17.0.
review_pool:
  - review-predict-powers
  - review-mcq-rearrange
  - review-solve-two-step
# What this topic teaches. Each question names the skills it tests, so a
# missed question can come back as a different one on the same skill
# (ADR-0011).
skills:
  - id: solve
    description: "Solve a linear equation by undoing what was done to the unknown, in reverse order"
  - id: substitute
    description: "Check an answer by substituting it back into the equation"
  - id: rearrange
    description: "Rearrange a formula to make another variable the subject"
  - id: powers
    description: "Apply the rules for multiplying powers of the same base"
''',
)

write(
    "lesson.mdx",
    '''<Intro>

Algebra is arithmetic with a blank in it. `3x - 7 = 11` says: take a number, triple it, take 7 away, and you get 11. Finding the number means undoing those steps, and Python is a fine place to do that, because it can also check the answer for you.

The main resource is the free textbook *OpenStax Elementary Algebra 2e*: **chapter 2, Solving Linear Equations and Inequalities** (the first three sections are enough), and **section 6.2, Use Multiplication Properties of Exponents**. About 25 minutes. Watch for:

- **Undoing in reverse order.** Whatever was done to x last gets undone first. If x was multiplied and then had something subtracted, add first, then divide.
- **Both sides.** Every step is done to both sides of the equation, so it stays true.
- **Checking by substituting.** Put your answer back in and see if the two sides agree. In Python that's one `print`.
- **Powers of the same base multiply by adding exponents:** x² · x³ is x⁵.

The book writes answers by hand. Here you'll write them as Python expressions, which forces you to be exact about the order of operations, the thing most algebra mistakes are really about.

</Intro>

<Resource index={0} />

<Recap>

- **To solve, undo in reverse order.** `3x - 7 = 11`: the 7 was subtracted last, so add 7 to both sides (`3x = 18`), then divide by 3 (`x = 6`). In Python: `x = (11 + 7) / 3`. The parentheses are the "first add, then divide".
- **Check by substituting.** `print(3 * x - 7)` should show `11.0`. If it doesn't, the undoing was wrong, and no amount of confidence changes that.
- **Rearranging a formula is the same move.** `speed = distance / time` solved for `time` is `time = distance / speed`; `F = C * 9 / 5 + 32` solved for `C` is `C = (F - 32) * 5 / 9`. Undo the `+ 32` first, then the `* 9 / 5`.
- **Powers:** `x ** 2 * x ** 3` is `x ** 5`: multiplying powers of the same base adds the exponents. `(x ** 2) ** 3` is `x ** 6`: a power of a power multiplies them. `x ** -1` is `1 / x`, and `x ** 0` is `1`.
- **A mistake to expect:** `17 - 3 / 5` is not "17 minus 3, then divided by 5". Python divides first. When you mean "then", write parentheses.
- **Answers are often floats.** `(11 + 7) / 3` is `6.0`, not `6`, because `/` always gives a float. That's fine; show it with `:.1f` or `round()` when it matters.

</Recap>
''',
)

# --- practice: recall --------------------------------------------------------

write(
    "recall/parsons-solve-for-x.yaml",
    '''id: parsons-solve-for-x
type: parsons
rev: 1
prompt: |
  Put the lines in order so the program solves `3x + 5 = 20` and prints `x = 5.0`, then `check: 20.0`. One line is a decoy that doesn't belong.
lines:
  - 'right = 20'
  - 'x = (right - 5) / 3'
  - 'print("x =", x)'
  - 'print("check:", 3 * x + 5)'
distractors:
  - 'x = right - 5 / 3'
explanation: |
  Undo in reverse order: the 5 was added last, so take it away first (`right - 5`), then divide by 3. The parentheses make Python subtract before it divides; the decoy divides first and gives 18.33. The last line substitutes the answer back: 3 × 5 + 5 is 20, so the solution checks.
skills: [solve, substitute]
''',
)

write(
    "recall/mcq-undo-order.yaml",
    '''id: mcq-undo-order
type: mcq
rev: 1
prompt: |
  To solve `2x + 6 = 14`, what should you do to both sides **first**?
choices:
  - 'Divide by 2'
  - 'Add 6'
  - 'Multiply by 2'
  - 'Subtract 6'
answer: 3
explanation: |
  The left side was built by multiplying x by 2 and **then** adding 6. Undo in reverse: take the 6 away first (`2x = 8`), then divide by 2 (`x = 4`). Dividing first would also have to divide the 6, which is where mistakes creep in; adding 6 or multiplying by 2 moves away from x.
skills: [solve]
''',
)

write(
    "recall/predict-rearranged-formula.yaml",
    '''id: predict-rearranged-formula
type: predict_output
rev: 1
prompt: |
  Speed is distance divided by time. This program rearranges that to find the time, then checks. What does it print?
code: |
  distance = 150
  speed = 60
  time = distance / speed
  print(time)
  print(speed * time)
expected_output: |
  2.5
  150.0
explanation: |
  `speed = distance / time` rearranged for time is `time = distance / speed`: 150 / 60 is `2.5` hours. The check multiplies back: 60 × 2.5 is `150.0`, the distance we started with (a float, because `time` is one).
skills: [rearrange, substitute]
''',
)

write(
    "recall/mcq-exponent-rules.yaml",
    '''id: mcq-exponent-rules
type: mcq
rev: 1
prompt: |
  Which expression is equal to `2 ** 3 * 2 ** 4`?
choices:
  - '`2 ** 12`'
  - '`4 ** 7`'
  - '`2 ** 7`'
  - '`2 ** 1`'
answer: 2
explanation: |
  `2 ** 3` is three 2s multiplied together and `2 ** 4` is four more, so the product is seven 2s: `2 ** 7`, which is 128. Multiplying powers of the same base **adds** the exponents. `2 ** 12` multiplies them (that's `(2 ** 3) ** 4`), and `4 ** 7` changes the base.
skills: [powers]
''',
)

write(
    "recall/review-predict-powers.yaml",
    '''id: review-predict-powers
type: predict_output
rev: 1
prompt: |
  Three power rules in a row. What does the program print?
code: |
  print(2 ** 3 * 2 ** 2)
  print((2 ** 3) ** 2)
  print(10 ** -1)
expected_output: |
  32
  64
  0.1
explanation: |
  Multiplying powers of the same base adds the exponents: `2 ** 3 * 2 ** 2` is `2 ** 5`, 32. A power of a power multiplies them: `(2 ** 3) ** 2` is `2 ** 6`, 64. A negative exponent means one over: `10 ** -1` is 1/10, `0.1`.
skills: [powers]
''',
)

write(
    "recall/review-mcq-rearrange.yaml",
    '''id: review-mcq-rearrange
type: mcq
rev: 1
prompt: |
  The area of a rectangle is `area = length * width`. You know the area and the length. Which line gives the width?
choices:
  - '`width = area * length`'
  - '`width = area / length`'
  - '`width = length / area`'
  - '`width = area - length`'
answer: 1
explanation: |
  The width was multiplied by the length to make the area, so undo the multiplication: divide both sides by the length, `width = area / length`. Check with numbers: a 3 by 4 rectangle has area 12, and 12 / 3 is 4.
skills: [rearrange]
''',
)

# --- practice: exercises -------------------------------------------------------

write(
    "exercises/example-undo-the-equation/exercise.yaml",
    '''id: example-undo-the-equation
stage: worked_example
rev: 1
title: "Undo the equation"
prompt: |
  This program solves `3x - 7 = 11` and checks its own answer. Press **Run**, then read how each part works.
steps:
  - label: "Name what you know"
    lines: "1"
    note: "The right-hand side is a number; give it a name so the next line reads like the algebra."
  - label: "Undo in reverse order"
    lines: "2"
    note: "x was multiplied by 3 and **then** had 7 subtracted. Undo the subtraction first (add 7), then the multiplication (divide by 3). The parentheses make Python add before it divides."
  - label: "Show the answer"
    lines: "3"
    note: "`6.0`, a float, because `/` always gives one. That's the right answer; the `.0` is Python being precise about the type."
  - label: "Check by substituting"
    lines: "4"
    note: "Put x back into the left-hand side. If it prints `11.0`, the solution is right. Make a habit of this line: it catches every undoing mistake."
''',
)
write(
    "exercises/example-undo-the-equation/solution.py",
    '''right_side = 11
x = (right_side + 7) / 3
print("x =", x)
print("check:", 3 * x - 7)
''',
)
write(
    "exercises/example-undo-the-equation/test_exercise.py",
    '''from checks import run


def test_solves_and_checks():
    """Prints x = 6.0, then check: 11.0."""
    assert run() == "x = 6.0\\ncheck: 11.0\\n"
''',
)

write(
    "exercises/fill-fahrenheit-to-celsius/exercise.yaml",
    '''id: fill-fahrenheit-to-celsius
stage: fill_in
rev: 1
title: "Fahrenheit to Celsius"
prompt: |
  The formula from Celsius to Fahrenheit is `F = C * 9 / 5 + 32`. This program needs it the other way round. Replace each `...` so it prints:

  ```
  77 degrees F is 25.0 degrees C
  ```

  Until every `...` is replaced, Python can't run the program at all, and shows a syntax error.
hints:
  - "Undo in reverse order: the 32 was added last, so take it away first."
  - "Then undo the `* 9 / 5`: multiply by 5 and divide by 9."
  - "The whole subtraction has to happen before the multiplying: `(fahrenheit - 32) * 5 / 9`."
skills: [rearrange]
''',
)
write(
    "exercises/fill-fahrenheit-to-celsius/starter.py",
    '''fahrenheit = 77
celsius = (fahrenheit ... 32) ... 5 / 9
print(f"{fahrenheit} degrees F is {celsius:.1f} degrees C")
''',
)
write(
    "exercises/fill-fahrenheit-to-celsius/solution.py",
    '''fahrenheit = 77
celsius = (fahrenheit - 32) * 5 / 9
print(f"{fahrenheit} degrees F is {celsius:.1f} degrees C")
''',
)
write(
    "exercises/fill-fahrenheit-to-celsius/test_exercise.py",
    '''from checks import run, run_with


def test_seventy_seven():
    """Prints 77 degrees F is 25.0 degrees C."""
    printed = run()
    assert printed == "77 degrees F is 25.0 degrees C\\n", (
        f"Your program printed:\\n{printed}"
    )


def test_boiling_point():
    """Works for any temperature: 212 F is 100.0 C."""
    printed = run_with({"fahrenheit": 212})
    assert printed == "212 degrees F is 100.0 degrees C\\n", (
        f"With fahrenheit = 212 it should print 212 degrees F is 100.0 degrees C. It printed:\\n{printed}"
    )
''',
)
write(
    "exercises/fill-fahrenheit-to-celsius/wrong/adds-instead.py",
    '''fahrenheit = 77
celsius = (fahrenheit + 32) * 5 / 9
print(f"{fahrenheit} degrees F is {celsius:.1f} degrees C")
''',
)
write(
    "exercises/fill-fahrenheit-to-celsius/wrong/typed-in.py",
    '''fahrenheit = 77
celsius = 25.0
print(f"{fahrenheit} degrees F is {celsius:.1f} degrees C")
''',
)

write(
    "exercises/write-savings-goal/exercise.yaml",
    '''id: write-savings-goal
stage: write
rev: 1
title: "Savings goal"
prompt: |
  You've saved `saved = 300` toward a `goal = 1200`, and you put away `monthly = 150` each month. The equation is `saved + monthly * months = goal`. Solve it for `months` and print, with one decimal place:

  ```
  Months: 6.0
  ```

  Keep the three starting lines: the checks run your program with other numbers too.
hints:
  - "Undo in reverse order: the `saved` was added last, so take it away from the goal first."
  - "What's left is `monthly * months`; undo the multiplication by dividing by `monthly`."
  - "Show one decimal place with `f\\"{months:.1f}\\"`."
skills: [solve]
''',
)
write("exercises/write-savings-goal/starter.py", "saved = 300\ngoal = 1200\nmonthly = 150\n")
write(
    "exercises/write-savings-goal/solution.py",
    '''saved = 300
goal = 1200
monthly = 150
months = (goal - saved) / monthly
print(f"Months: {months:.1f}")
''',
)
write(
    "exercises/write-savings-goal/test_exercise.py",
    '''from checks import run, run_with


def test_this_goal():
    """Prints Months: 6.0."""
    printed = run()
    assert printed == "Months: 6.0\\n", f"Your program printed:\\n{printed}"


def test_any_goal():
    """Works for any numbers: 100 saved, a goal of 1000 and 80 a month is 11.2 months."""
    printed = run_with({"saved": 100, "goal": 1000, "monthly": 80})
    assert printed == "Months: 11.2\\n", (
        f"With saved 100, goal 1000 and monthly 80 it should print Months: 11.2. It printed:\\n{printed}"
    )
''',
)
write(
    "exercises/write-savings-goal/wrong/forgets-saved.py",
    '''saved = 300
goal = 1200
monthly = 150
months = goal / monthly
print(f"Months: {months:.1f}")
''',
)
write(
    "exercises/write-savings-goal/wrong/typed-in.py",
    '''saved = 300
goal = 1200
monthly = 150
print("Months: 6.0")
''',
)

# --- proof ------------------------------------------------------------------

write(
    "exercises/build-interest-rearranged/exercise.yaml",
    '''id: build-interest-rearranged
stage: build
rev: 1
title: "How much was invested?"
prompt: |
  Simple interest is `interest = principal * rate / 100 * years`: the amount invested, times the yearly rate as a percentage, times the years. Starting from a blank editor, start with `interest = 180`, `rate = 4` and `years = 3`, one line each. Rearrange the formula to find the principal, then print it and a check that puts it back into the original formula, each with two decimal places:

  ```
  Principal: 1500.00
  Check: 180.00
  ```
skills: [rearrange, substitute]
''',
)
write("exercises/build-interest-rearranged/starter.py", "")
write(
    "exercises/build-interest-rearranged/solution.py",
    '''interest = 180
rate = 4
years = 3
principal = interest / (rate / 100 * years)
check = principal * rate / 100 * years
print(f"Principal: {principal:.2f}")
print(f"Check: {check:.2f}")
''',
)
write(
    "exercises/build-interest-rearranged/test_exercise.py",
    '''from checks import run, run_with

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_this_investment():
    """Prints Principal: 1500.00, then Check: 180.00 for 180, 4% and 3 years."""
    assert run() == "Principal: 1500.00\\nCheck: 180.00\\n"


def test_any_investment():
    """Works for any interest, rate and years: the check gives the interest back."""
    printed = run_with({"interest": 50, "rate": 2, "years": 5})
    assert printed == "Principal: 500.00\\nCheck: 50.00\\n"
''',
)
write(
    "exercises/build-interest-rearranged/wrong/rate-not-a-percent.py",
    '''interest = 180
rate = 4
years = 3
principal = interest / (rate * years)
check = principal * rate / 100 * years
print(f"Principal: {principal:.2f}")
print(f"Check: {check:.2f}")
''',
)
write(
    "exercises/build-interest-rearranged/wrong/divides-in-the-wrong-order.py",
    '''interest = 180
rate = 4
years = 3
principal = interest / rate / 100 * years
check = principal * rate / 100 * years
print(f"Principal: {principal:.2f}")
print(f"Check: {check:.2f}")
''',
)
write(
    "exercises/build-interest-rearranged/wrong/typed-in.py",
    '''interest = 180
rate = 4
years = 3
print("Principal: 1500.00")
print("Check: 180.00")
''',
)

write(
    "exercises/debug-temperature-conversion/exercise.yaml",
    '''id: debug-temperature-conversion
stage: debug
rev: 1
title: "Body temperature"
prompt: |
  This program should convert a temperature from Fahrenheit to Celsius and to kelvin, which is Celsius plus 273.15:

  ```
  37.0 C
  310.15 K
  ```

  It has two bugs. Run it, fix what you find, and run it again. Check each number against the formulas, not just whether it runs.
skills: [rearrange, solve]
''',
)
write(
    "exercises/debug-temperature-conversion/starter.py",
    '''fahrenheit = 98.6
celsius = fahrenheit - 32 * 5 / 9
kelvin = celsius + 273
print(f"{celsius:.1f} C")
print(f"{kelvin:.2f} K")
''',
)
write(
    "exercises/debug-temperature-conversion/solution.py",
    '''fahrenheit = 98.6
celsius = (fahrenheit - 32) * 5 / 9
kelvin = celsius + 273.15
print(f"{celsius:.1f} C")
print(f"{kelvin:.2f} K")
''',
)
write(
    "exercises/debug-temperature-conversion/test_exercise.py",
    '''from checks import run, run_with

EXPECTED = "37.0 C\\n310.15 K\\n"


def test_body_temperature():
    """Prints 37.0 C, then 310.15 K."""
    printed = run()
    assert printed == EXPECTED, (
        f"Expected this:\\n{EXPECTED}\\nYour program printed:\\n{printed}"
    )


def test_freezing_point():
    """Works for any temperature: 32 F is 0.0 C and 273.15 K."""
    printed = run_with({"fahrenheit": 32})
    assert printed == "0.0 C\\n273.15 K\\n", (
        f"With fahrenheit = 32 it should print 0.0 C, then 273.15 K. It printed:\\n{printed}"
    )
''',
)
write(
    "exercises/debug-temperature-conversion/wrong/only-parentheses-fixed.py",
    '''fahrenheit = 98.6
celsius = (fahrenheit - 32) * 5 / 9
kelvin = celsius + 273
print(f"{celsius:.1f} C")
print(f"{kelvin:.2f} K")
''',
)
write(
    "exercises/debug-temperature-conversion/wrong/only-kelvin-fixed.py",
    '''fahrenheit = 98.6
celsius = fahrenheit - 32 * 5 / 9
kelvin = celsius + 273.15
print(f"{celsius:.1f} C")
print(f"{kelvin:.2f} K")
''',
)
write(
    "exercises/debug-temperature-conversion/wrong/typed-in.py",
    '''fahrenheit = 98.6
celsius = 37.0
kelvin = 310.15
print(f"{celsius:.1f} C")
print(f"{kelvin:.2f} K")
''',
)

# --- review pool: a code exercise -------------------------------------------

write(
    "exercises/review-solve-two-step/exercise.yaml",
    '''id: review-solve-two-step
stage: review_code
rev: 1
title: "Solve a two-step equation"
prompt: |
  The equation is `a * x + b = c`, with `a = 4`, `b = 9` and `c = 29`. Solve it for `x` and print the answer with one decimal place, then a check that substitutes it back:

  ```
  x = 5.0
  check: 29.0
  ```

  Keep the three starting lines: the checks run your program with other values too.
skills: [solve, substitute]
''',
)
write("exercises/review-solve-two-step/starter.py", "a = 4\nb = 9\nc = 29\n")
write(
    "exercises/review-solve-two-step/solution.py",
    '''a = 4
b = 9
c = 29
x = (c - b) / a
print(f"x = {x:.1f}")
print(f"check: {a * x + b:.1f}")
''',
)
write(
    "exercises/review-solve-two-step/test_exercise.py",
    '''from checks import run, run_with


def test_this_equation():
    """Prints x = 5.0, then check: 29.0."""
    assert run() == "x = 5.0\\ncheck: 29.0\\n"


def test_any_equation():
    """Works for any a, b and c: 3x + 2 = 14 gives 4.0."""
    assert run_with({"a": 3, "b": 2, "c": 14}) == "x = 4.0\\ncheck: 14.0\\n"
''',
)
write(
    "exercises/review-solve-two-step/wrong/divides-first.py",
    '''a = 4
b = 9
c = 29
x = c - b / a
print(f"x = {x:.1f}")
print(f"check: {a * x + b:.1f}")
''',
)
write(
    "exercises/review-solve-two-step/wrong/typed-in.py",
    '''a = 4
b = 9
c = 29
print("x = 5.0")
print("check: 29.0")
''',
)

print("ml.math.algebra written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
