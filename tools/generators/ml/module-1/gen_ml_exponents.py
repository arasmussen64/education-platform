"""Writes the topic ml.math.exponents-and-logs (the ML track's fourth topic).
Run from the repository root. Files are written as bytes with LF endings."""

import pathlib

ROOT = pathlib.Path("content/topics/ml.math.exponents-and-logs")


def write(relative: str, text: str) -> None:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


write(
    "topic.yaml",
    '''id: ml.math.exponents-and-logs
kind: topic
status: ready
title: "Exponents and logarithms"
summary: "Powers and their undoing: roots, logarithms, growth and decay, and why ML adds logs."
prerequisites: [ml.math.functions]
estimated_minutes: 45
rev: 1
objectives:
  - "Use powers, roots and negative exponents."
  - "Say what a logarithm is, and compute one."
  - "Turn products into sums with the log rules."
  - "Model growth and decay in code, and say why machine learning adds log-probabilities."
resources:
  - title: "OpenStax Intermediate Algebra 2e: chapter 10 (Exponential and Logarithmic Functions), sections 10.2 to 10.4"
    url: https://openstax.org/details/books/intermediate-algebra-2e
    type: reading
    use: link
    license: CC BY 4.0
  - title: "The Python Standard Library: math (Python Software Foundation)"
    url: https://docs.python.org/3/library/math.html
    type: reading
    use: link
    license: PSF License Version 2
  - title: "Khan Academy: Algebra 2"
    url: https://www.khanacademy.org/math/algebra2
    type: interactive
    use: link
    license: CC BY-NC-SA 3.0 US (linked, not copied)
practice:
  - example-powers-and-logs
  - parsons-doubling-days
  - mcq-what-a-log-asks
  - predict-log-of-a-product
  - mcq-negative-exponent
  - fill-compound-growth
  - write-half-life
prove:
  build: build-years-to-double
  debug: debug-decibels
  explain:
    prompt: |
      A friend says "the log of a product is the product of the logs". In your own words: what question does a logarithm answer, and what is `log10(1000)`? What is `log10(1000 * 100)`, and what does that show about the friend's claim? And why does machine learning add the logs of probabilities instead of multiplying the probabilities themselves?
    rubric:
      - id: meaning
        required: true
        description: "A logarithm answers 'the base to what power gives this number?': log10(1000) is 3 because 10 ** 3 is 1000."
      - id: product-to-sum
        required: true
        description: "log10(1000 * 100) is log10(100000), which is 5: the logs add (3 + 2), they don't multiply (3 * 2 would be 6). The friend is wrong."
      - id: why-ml
        required: true
        description: "Multiplying many probabilities between 0 and 1 gives a number so small the computer rounds it to 0; adding their logs keeps a usable number and gives the same ranking."
      - id: inverse
        required: false
        description: "Says that a log undoes a power (they're inverse functions), or mentions ln and e."
    model_answer: |
      A logarithm asks "the base to what power gives this number?" log10(1000) asks "10 to what power is 1000?", and the answer is 3, because 10 ** 3 is 1000. A log undoes a power the way a root undoes a square. For the product, 1000 * 100 is 100000, which is 10 ** 5, so log10(1000 * 100) is 5. The logs of the two numbers are 3 and 2, and 3 + 2 is 5: the log of a product is the SUM of the logs, not the product (3 * 2 would be 6). So the friend has the rule wrong. Machine learning uses this all the time: a model's confidence in a whole sentence or data set is many probabilities multiplied together, each between 0 and 1, and the product gets so small that a float rounds it to 0. Adding the logs instead gives an ordinary negative number, like -230, that the computer can hold, compare and take derivatives of, and because log is increasing, the biggest log-probability still belongs to the most likely answer.
review_pool:
  - review-predict-roots-and-powers
  - review-mcq-growth-formula
  - review-log2-table
# What this topic teaches. Each question names the skills it tests, so a
# missed question can come back as a different one on the same skill
# (ADR-0011).
skills:
  - id: powers
    description: "Use powers, roots and negative exponents"
  - id: log-meaning
    description: "Say what a logarithm is, and compute one"
  - id: log-rules
    description: "Turn products into sums with the log rules"
  - id: growth
    description: "Model growth and decay with a power in code"
''',
)

write(
    "lesson.mdx",
    '''<Intro>

A power is repeated multiplication, and a logarithm is the question "how many times?" asked backwards. Machine learning is full of both: data that doubles, errors that halve, and probabilities so small that only their logarithms fit in a computer.

The main resource is the free textbook *OpenStax Intermediate Algebra 2e*, **chapter 10, Exponential and Logarithmic Functions**: sections 10.2 (exponential functions), 10.3 (what a logarithm is) and 10.4 (the log rules). About 25 minutes; skim the graphs, read the definitions and the rules slowly. Watch for:

- **Negative and fractional exponents.** `10 ** -2` is 1/100, and `16 ** 0.5` is the square root, 4.
- **The definition of a logarithm:** log base b of y is the power you raise b to in order to get y. `log2(1024)` is 10 because `2 ** 10` is 1024.
- **The product rule:** the log of a product is the **sum** of the logs. That one rule is why machine learning adds logs instead of multiplying probabilities.
- **Growth and decay** are repeated multiplication: a balance that grows 5% a year is multiplied by 1.05 each year, and after `n` years it's been multiplied by `1.05 ** n`.

In Python the tools are `**`, and `math.log2`, `math.log10` and `math.log` (the natural log, base e) from the `math` module.

</Intro>

<Resource index={0} />

<Recap>

- **Powers:** `2 ** 10` is 1024. **Negative exponents** mean "one over": `2 ** -2` is `0.25`. **Fractional exponents** are roots: `16 ** 0.5` is `4.0`, the square root.
- **A logarithm undoes a power.** `math.log2(1024)` is `10.0`: "2 to what power is 1024?" `math.log10(100)` is `2.0`. `math.log(x)` with no base is the natural log, base `e` (about 2.718), which calculus and machine learning prefer.
- **The rules,** each one a fact about exponents in disguise:
  - product → sum: `log(a * b)` is `log(a) + log(b)`;
  - quotient → difference: `log(a / b)` is `log(a) - log(b)`;
  - power → multiple: `log(a ** n)` is `n * log(a)`.
- **Growth is a power.** Something that grows by `r` percent each step is multiplied by `(1 + r / 100)` each step: after `n` steps, `start * (1 + r / 100) ** n`. **Decay** is the same with a factor below 1: a dose that halves every 6 hours is `start * 0.5 ** (hours / 6)`.
- **How long until it doubles?** Either loop, multiplying until the amount passes double, or use a log: `math.log(2) / math.log(1 + r / 100)` years.
- **Why ML adds logs.** A model's confidence in a whole data set is many probabilities multiplied together, each between 0 and 1. The product is so small that a float rounds it to `0.0`. Add the logs instead: an ordinary negative number, with the same ranking, and the product rule says it's the same information. "Log-likelihood" and "cross-entropy" are this trick with names.

</Recap>
''',
)

# --- practice: recall --------------------------------------------------------

write(
    "recall/parsons-doubling-days.yaml",
    '''id: parsons-doubling-days
type: parsons
rev: 1
prompt: |
  A colony of bacteria doubles every day, starting from 1. Put the lines in order so the program counts the days until it passes 1000 and prints `10 1024`. One line is a decoy that doesn't belong.
lines:
  - 'amount = 1'
  - 'days = 0'
  - 'while amount < 1000:'
  - '    amount = amount * 2'
  - '    days = days + 1'
  - 'print(days, amount)'
distractors:
  - '    amount = amount + 2'
explanation: |
  Doubling is multiplying by 2, so the loop multiplies and counts a day each time until the amount reaches 1000: after 10 doublings it's `2 ** 10`, 1024. The decoy adds 2 instead, which is growth by the same amount each day, not by the same factor: that would take 500 days.
skills: [growth]
''',
)

write(
    "recall/mcq-what-a-log-asks.yaml",
    '''id: mcq-what-a-log-asks
type: mcq
rev: 1
prompt: |
  `math.log2(32)` answers which question?
choices:
  - 'What is 32 divided by 2?'
  - 'What is 2 to what power is 32?'
  - 'What is 2 times 32?'
  - 'What is the square root of 32?'
answer: 1
explanation: |
  A logarithm is a power asked backwards: log base 2 of 32 is the exponent you raise 2 to in order to get 32. Since `2 ** 5` is 32, `math.log2(32)` is `5.0`. The other choices are 16, 64 and about 5.66.
skills: [log-meaning]
''',
)

write(
    "recall/predict-log-of-a-product.yaml",
    '''id: predict-log-of-a-product
type: predict_output
rev: 1
prompt: |
  The log of a product, two ways. What does the program print?
code: |
  import math

  a = math.log10(1000)
  b = math.log10(100)
  print(a + b)
  print(math.log10(1000 * 100))
expected_output: |
  5.0
  5.0
explanation: |
  `log10(1000)` is 3 and `log10(100)` is 2, so `a + b` is `5.0`. And `1000 * 100` is 100000, which is `10 ** 5`, so its log is `5.0` too: the log of a product is the sum of the logs. Multiplying numbers adds their exponents, and a log is just the exponent.
skills: [log-rules]
''',
)

write(
    "recall/mcq-negative-exponent.yaml",
    '''id: mcq-negative-exponent
type: mcq
rev: 1
prompt: |
  What does `print(10 ** -2)` show?
choices:
  - '`-100`'
  - '`0.1`'
  - '`-20`'
  - '`0.01`'
answer: 3
explanation: |
  A negative exponent means "one over": `10 ** -2` is `1 / 10 ** 2`, which is 1/100, `0.01`. It's small, not negative. (`10 ** -1` would be `0.1`.)
skills: [powers]
''',
)

write(
    "recall/review-predict-roots-and-powers.yaml",
    '''id: review-predict-roots-and-powers
type: predict_output
rev: 1
prompt: |
  A root, a zero power and a quotient of powers. What does the program print?
code: |
  print(81 ** 0.5)
  print(2 ** 0)
  print(10 ** 3 / 10 ** 2)
expected_output: |
  9.0
  1
  10.0
explanation: |
  An exponent of 0.5 is a square root: `81 ** 0.5` is `9.0` (a float, because the exponent is one). Anything to the power 0 is `1`. Dividing powers of the same base subtracts the exponents: `10 ** 3 / 10 ** 2` is `10 ** 1`, and `/` gives `10.0`.
skills: [powers]
''',
)

write(
    "recall/review-mcq-growth-formula.yaml",
    '''id: review-mcq-growth-formula
type: mcq
rev: 1
prompt: |
  A balance `p` grows by `r` percent every year. Which expression is the balance after `n` years?
choices:
  - '`p * (1 + r / 100) ** n`'
  - '`p + r / 100 * n`'
  - '`p * r / 100 ** n`'
  - '`(p + r / 100) ** n`'
answer: 0
explanation: |
  Growing by r percent means multiplying by `1 + r / 100`, and doing that n years running means multiplying by it n times: `(1 + r / 100) ** n`. The second choice adds the same amount each year (simple interest, a straight line, not growth); the others raise the wrong thing to the power.
skills: [growth]
''',
)

# --- practice: exercises -------------------------------------------------------

write(
    "exercises/example-powers-and-logs/exercise.yaml",
    '''id: example-powers-and-logs
stage: worked_example
rev: 1
title: "Powers, and powers undone"
prompt: |
  This program takes powers, roots and logarithms. Press **Run**, then read how each part works.
steps:
  - label: "A power"
    lines: "3"
    note: "`2 ** 10` is ten 2s multiplied together: 1024. Computer sizes come in these: a kilobyte is 2 ** 10 bytes."
  - label: "A negative exponent is one over"
    lines: "4"
    note: "`2 ** -2` is `1 / (2 ** 2)`, which is 0.25. Negative exponents make things small, not negative."
  - label: "A fractional exponent is a root"
    lines: "5"
    note: "`16 ** 0.5` is the square root of 16, 4.0. Raising to a half undoes squaring."
  - label: "A logarithm undoes a power"
    lines: "6-7"
    note: "`math.log2(1024)` asks '2 to what power is 1024?': 10.0. `math.log10(100)` asks the same of 10: 2.0. The `math` module is imported on line 1."
''',
)
write(
    "exercises/example-powers-and-logs/solution.py",
    '''import math

print(2 ** 10)
print(2 ** -2)
print(16 ** 0.5)
print(math.log2(1024))
print(math.log10(100))
''',
)
write(
    "exercises/example-powers-and-logs/test_exercise.py",
    '''from checks import run


def test_powers_and_logs():
    """Prints 1024, 0.25, 4.0, 10.0 and 2.0."""
    assert run() == "1024\\n0.25\\n4.0\\n10.0\\n2.0\\n"
''',
)

write(
    "exercises/fill-compound-growth/exercise.yaml",
    '''id: fill-compound-growth
stage: fill_in
rev: 1
title: "Compound growth"
prompt: |
  A balance of 1000 grows by 5% a year for 10 years. Replace each `...` so the program prints the final balance with two decimal places:

  ```
  After 10 years: 1628.89
  ```

  Until every `...` is replaced, Python can't run the program at all, and shows a syntax error.
hints:
  - "Growing by 5% means multiplying by 1 plus 5 hundredths. Which operator turns `rate` into hundredths?"
  - "Ten years of growth is that factor multiplied ten times: a power, `** years`."
skills: [growth]
''',
)
write(
    "exercises/fill-compound-growth/starter.py",
    '''start = 1000
rate = 5
years = 10
balance = start * (1 + rate ... 100) ... years
print(f"After {years} years: {balance:.2f}")
''',
)
write(
    "exercises/fill-compound-growth/solution.py",
    '''start = 1000
rate = 5
years = 10
balance = start * (1 + rate / 100) ** years
print(f"After {years} years: {balance:.2f}")
''',
)
write(
    "exercises/fill-compound-growth/test_exercise.py",
    '''from checks import run, run_with


def test_ten_years():
    """Prints After 10 years: 1628.89."""
    printed = run()
    assert printed == "After 10 years: 1628.89\\n", f"Your program printed:\\n{printed}"


def test_any_growth():
    """Works for any start, rate and years: 500 at 10% for 3 years is 665.50."""
    printed = run_with({"start": 500, "rate": 10, "years": 3})
    assert printed == "After 3 years: 665.50\\n", (
        f"With 500, 10% and 3 years it should print After 3 years: 665.50. It printed:\\n{printed}"
    )
''',
)
write(
    "exercises/fill-compound-growth/wrong/multiplies-instead-of-power.py",
    '''start = 1000
rate = 5
years = 10
balance = start * (1 + rate / 100) * years
print(f"After {years} years: {balance:.2f}")
''',
)
write(
    "exercises/fill-compound-growth/wrong/typed-in.py",
    '''start = 1000
rate = 5
years = 10
balance = 1628.89
print(f"After {years} years: {balance:.2f}")
''',
)

write(
    "exercises/write-half-life/exercise.yaml",
    '''id: write-half-life
stage: write
rev: 1
title: "Half-life"
prompt: |
  A dose of 200 mg of a medicine halves in the body every 6 hours. Write a function `remaining(hours)` that returns how much is left after `hours` hours, `200 * 0.5 ** (hours / 6)`, then print a table for 0, 6, 12, 18 and 24 hours, one decimal place:

  ```
  0 h: 200.0 mg
  6 h: 100.0 mg
  12 h: 50.0 mg
  18 h: 25.0 mg
  24 h: 12.5 mg
  ```
hints:
  - "Halving is multiplying by 0.5; `hours / 6` is how many halvings have happened, so the factor is `0.5 ** (hours / 6)`."
  - "`range(0, 25, 6)` counts 0, 6, 12, 18, 24."
  - "In the loop: `print(f\\"{h} h: {remaining(h):.1f} mg\\")`."
skills: [growth, powers]
''',
)
write("exercises/write-half-life/starter.py", "")
write(
    "exercises/write-half-life/solution.py",
    '''def remaining(hours):
    return 200 * 0.5 ** (hours / 6)


for h in range(0, 25, 6):
    print(f"{h} h: {remaining(h):.1f} mg")
''',
)
write(
    "exercises/write-half-life/test_exercise.py",
    '''from checks import function, run

TABLE = "0 h: 200.0 mg\\n6 h: 100.0 mg\\n12 h: 50.0 mg\\n18 h: 25.0 mg\\n24 h: 12.5 mg\\n"


def test_the_function():
    """remaining(6) is 100.0, and remaining(3) is about 141.4."""
    remaining = function("remaining")
    assert remaining(6) == 100.0, f"remaining(6) returned {remaining(6)}"
    assert round(remaining(3), 1) == 141.4, f"remaining(3) returned {remaining(3)}"


def test_the_table():
    """Prints the five rows from 0 h to 24 h."""
    printed = run()
    assert printed == TABLE, f"Expected this:\\n{TABLE}\\nYour program printed:\\n{printed}"
''',
)
write(
    "exercises/write-half-life/wrong/linear-decay.py",
    '''def remaining(hours):
    return 200 - 100 * (hours / 6)


for h in range(0, 25, 6):
    print(f"{h} h: {remaining(h):.1f} mg")
''',
)
write(
    "exercises/write-half-life/wrong/typed-in.py",
    '''def remaining(hours):
    return 200


print("0 h: 200.0 mg")
print("6 h: 100.0 mg")
print("12 h: 50.0 mg")
print("18 h: 25.0 mg")
print("24 h: 12.5 mg")
''',
)

# --- proof ------------------------------------------------------------------

write(
    "exercises/build-years-to-double/exercise.yaml",
    '''id: build-years-to-double
stage: build
rev: 1
title: "Years to double"
prompt: |
  Starting from a blank editor, write a function `years_to_double(rate)` that returns how many whole years it takes money to at least double when it grows by `rate` percent a year. Count years, multiplying by `1 + rate / 100` each year, until the amount is at least twice what it started as. Then print a table for rates 2, 5 and 10:

  ```
  2%: 36 years
  5%: 15 years
  10%: 8 years
  ```

  The checks call your function with other rates too.
skills: [growth, log-rules]
''',
)
write("exercises/build-years-to-double/starter.py", "")
write(
    "exercises/build-years-to-double/solution.py",
    '''def years_to_double(rate):
    amount = 1.0
    years = 0
    while amount < 2.0:
        amount = amount * (1 + rate / 100)
        years = years + 1
    return years


for rate in (2, 5, 10):
    print(f"{rate}%: {years_to_double(rate)} years")
''',
)
write(
    "exercises/build-years-to-double/test_exercise.py",
    '''from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_table():
    """Prints the years to double at 2%, 5% and 10%."""
    assert run() == "2%: 36 years\\n5%: 15 years\\n10%: 8 years\\n"


def test_the_function():
    """years_to_double(100) is 1, and years_to_double(7) is 11."""
    years_to_double = function("years_to_double")
    assert years_to_double(100) == 1
    assert years_to_double(7) == 11
''',
)
write(
    "exercises/build-years-to-double/wrong/simple-interest.py",
    '''def years_to_double(rate):
    amount = 1.0
    years = 0
    while amount < 2.0:
        amount = amount + rate / 100
        years = years + 1
    return years


for rate in (2, 5, 10):
    print(f"{rate}%: {years_to_double(rate)} years")
''',
)
write(
    "exercises/build-years-to-double/wrong/typed-in.py",
    '''def years_to_double(rate):
    return 36


print("2%: 36 years")
print("5%: 15 years")
print("10%: 8 years")
''',
)

write(
    "exercises/debug-decibels/exercise.yaml",
    '''id: debug-decibels
stage: debug
rev: 1
title: "Decibels"
prompt: |
  Loudness in decibels is `10 * log10(power / reference)`, where the reference is the quietest sound a person can hear, 0.000000000001 watts (`1e-12`). This program should print the loudness of a 0.5 W sound:

  ```
  117.0 dB
  ```

  It has two bugs. Run it, fix what you find, and run it again. If the number is wildly off, suspect the log; if it has the wrong sign, suspect the fraction.
skills: [log-meaning, log-rules]
''',
)
write(
    "exercises/debug-decibels/starter.py",
    '''import math

power = 0.5
reference = 1e-12
ratio = reference / power
decibels = 10 * math.log(ratio)
print(f"{decibels:.1f} dB")
''',
)
write(
    "exercises/debug-decibels/solution.py",
    '''import math

power = 0.5
reference = 1e-12
ratio = power / reference
decibels = 10 * math.log10(ratio)
print(f"{decibels:.1f} dB")
''',
)
write(
    "exercises/debug-decibels/test_exercise.py",
    '''from checks import run, run_with

EXPECTED = "117.0 dB\\n"


def test_half_a_watt():
    """Prints 117.0 dB."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\\n{EXPECTED}\\nYour program printed:\\n{printed}"


def test_any_power():
    """Works for any power: a millionth of a watt is 60.0 dB."""
    printed = run_with({"power": 1e-6})
    assert printed == "60.0 dB\\n", (
        f"With power = 1e-6 it should print 60.0 dB. It printed:\\n{printed}"
    )
''',
)
write(
    "exercises/debug-decibels/wrong/only-ratio-fixed.py",
    '''import math

power = 0.5
reference = 1e-12
ratio = power / reference
decibels = 10 * math.log(ratio)
print(f"{decibels:.1f} dB")
''',
)
write(
    "exercises/debug-decibels/wrong/only-log-fixed.py",
    '''import math

power = 0.5
reference = 1e-12
ratio = reference / power
decibels = 10 * math.log10(ratio)
print(f"{decibels:.1f} dB")
''',
)
write(
    "exercises/debug-decibels/wrong/typed-in.py",
    '''import math

power = 0.5
reference = 1e-12
decibels = 117.0
print(f"{decibels:.1f} dB")
''',
)

# --- review pool: a code exercise -------------------------------------------

write(
    "exercises/review-log2-table/exercise.yaml",
    '''id: review-log2-table
stage: review_code
rev: 1
title: "A table of logs"
prompt: |
  Print `math.log2` of 1, 2, 4, 8 and 16, one row per line, the number then its log:

  ```
  1 0.0
  2 1.0
  4 2.0
  8 3.0
  16 4.0
  ```

  Notice what happens to the log each time the number doubles.
skills: [log-meaning, log-rules]
''',
)
write("exercises/review-log2-table/starter.py", "import math\n")
write(
    "exercises/review-log2-table/solution.py",
    '''import math

for n in (1, 2, 4, 8, 16):
    print(n, math.log2(n))
''',
)
write(
    "exercises/review-log2-table/test_exercise.py",
    '''from checks import run


def test_the_table():
    """Prints the five rows, the log going up by 1 each time the number doubles."""
    assert run() == "1 0.0\\n2 1.0\\n4 2.0\\n8 3.0\\n16 4.0\\n"
''',
)
write(
    "exercises/review-log2-table/wrong/natural-log.py",
    '''import math

for n in (1, 2, 4, 8, 16):
    print(n, math.log(n))
''',
)
write(
    "exercises/review-log2-table/wrong/typed-in.py",
    '''import math

print("1 0.0")
print("2 1.0")
print("4 2.0")
print("8 3.0")
print("16 4.0")
''',
)

print("ml.math.exponents-and-logs written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
