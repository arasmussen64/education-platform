"""Writes the topic ml.math.arithmetic (the ML track's first topic). Run from
the repository root. Files are written as bytes with LF endings."""

import pathlib

ROOT = pathlib.Path("content/topics/ml.math.arithmetic")


def write(relative: str, text: str) -> None:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


write(
    "topic.yaml",
    '''id: ml.math.arithmetic
kind: topic
status: ready
title: "Fractions, decimals and percentages"
summary: "Fractions, decimals and percentages, computed in Python, in the right order."
prerequisites: [py.arithmetic]
estimated_minutes: 45
rev: 1
objectives:
  - "Compute with fractions, decimals and percentages in Python."
  - "Apply the order of operations, and change it with parentheses."
  - "Work out a percentage of an amount and a percentage change, and round sensibly."
resources:
  - title: "OpenStax Prealgebra 2e: chapters 4 (Fractions), 5 (Decimals) and 6 (Percents)"
    url: https://openstax.org/details/books/prealgebra-2e
    type: reading
    use: link
    license: CC BY 4.0
  - title: "The Python Tutorial: Floating-Point Arithmetic, Issues and Limitations (Python Software Foundation)"
    url: https://docs.python.org/3/tutorial/floatingpoint.html
    type: reading
    use: link
    license: PSF License Version 2
  - title: "Khan Academy: Arithmetic"
    url: https://www.khanacademy.org/math/arithmetic
    type: interactive
    use: link
    license: CC BY-NC-SA 3.0 US (linked, not copied)
practice:
  - example-recipe-scaling
  - parsons-percent-off
  - mcq-order-of-operations
  - predict-fraction-to-decimal
  - mcq-percent-change
  - fill-tip-and-split
  - write-mix-ratio
prove:
  build: build-sale-receipt
  debug: debug-average-score
  explain:
    prompt: |
      A jacket costs `price = 80`. A friend writes two lines to work out the price after 25% off:

      ```python
      print(price * (1 - 25 / 100))
      print(price * 1 - 25 / 100)
      ```

      In your own words: what does the first line work out, step by step, and in what order does Python do the operations? Then: why does the second line give a different answer, and what is it?
    rubric:
      - id: inside-first
        required: true
        description: "In the first line Python does the parentheses first: 25 / 100 is 0.25, and 1 - 0.25 is 0.75."
      - id: multiply
        required: true
        description: "Then it multiplies: 80 * 0.75 is 60.0, the price with a quarter taken off."
      - id: percent
        required: true
        description: "25% means 25 out of 100, so 25 / 100 is the fraction taken off, and 1 - 0.25 is the fraction that's left."
      - id: without-parentheses
        required: true
        description: "In the second line * and / come before -, so Python works out 80 * 1 = 80 and 25 / 100 = 0.25, then 80 - 0.25 = 79.75."
      - id: check
        required: false
        description: "Checks the answer another way: 25% of 80 is 20, and 80 - 20 is 60."
    model_answer: |
      25% means 25 out of every 100, so 25 / 100 is 0.25, the fraction taken off, and 1 - 0.25 is 0.75, the fraction of the price that's left. In the first line Python does the parentheses first: 25 / 100 gives 0.25, then 1 - 0.25 gives 0.75. Then it multiplies: 80 * 0.75 is 60.0, so the jacket costs 60. (Check: 25% of 80 is 20, and 80 - 20 is 60.) In the second line there are no parentheses, and Python does * and / before -: 80 * 1 is 80, 25 / 100 is 0.25, and 80 - 0.25 is 79.75. So it takes a quarter of a dollar off instead of a quarter of the price.
review_pool:
  - review-predict-percent
  - review-mcq-fractions
  - review-unit-price
# What this topic teaches. Each question names the skills it tests, so a
# missed question can come back as a different one on the same skill
# (ADR-0011).
skills:
  - id: fractions
    description: "Compute with fractions and decimals in Python, and turn one into the other"
  - id: percent
    description: "Work out a percentage of an amount and a percentage change"
  - id: order
    description: "Apply the order of operations, and change it with parentheses"
''',
)

write(
    "lesson.mdx",
    '''<Intro>

The machine-learning track starts with the math it leans on, done in Python, where a wrong idea shows up as a wrong number. This first topic is the arithmetic you already use: fractions, decimals and percentages, and the order Python does things in.

The main resource is three chapters of the free textbook *OpenStax Prealgebra 2e*: **Fractions** (chapter 4), **Decimals** (chapter 5) and **Percents** (chapter 6). Don't read them cover to cover: skim each chapter's opening section and its summary, and slow down wherever something looks unfamiliar. About 20 minutes. Watch for:

- **A fraction is a division waiting to happen.** Three quarters is 3 ÷ 4, which is 0.75. In Python that's `3 / 4`.
- **A percentage is a fraction of 100.** 25% is 25 out of 100, so 25% of something is that something times `25 / 100`.
- **The order of operations.** Multiplication and division happen before addition and subtraction unless parentheses say otherwise, in the book and in Python.

You've met Python's operators already (`+ - * / // % **`). Here they get a workout on the kind of numbers that appear in every data set.

</Intro>

<Resource index={0} />

<Recap>

- **Fractions are divisions.** `3 / 4` is `0.75`, `1 / 8` is `0.125`, `2 / 3` is `0.6666666666666666`. To add fractions, add their decimals: `3 / 8 + 1 / 8` is `0.5`. (`7 // 8` is `0`: floor division throws the fraction away.)
- **Decimals are floats, and floats are approximate.** `0.1 + 0.2` prints `0.30000000000000004`. That's not a bug in your program: a computer stores numbers in binary, and most decimals don't fit exactly, so the last digit can be off. Show results with `round(x, 2)` or an f-string, `f"{x:.2f}"`, and never test two floats with `==`.
- **Percent means per hundred.** `x% of y` is `y * x / 100`: 18% of 84.5 is `84.5 * 18 / 100`, which is `15.21`. Adding a percentage: `y * (1 + x / 100)`. Taking one off: `y * (1 - x / 100)`.
- **Percentage change** is `(new - old) / old * 100`: from 40 to 50 is `(50 - 40) / 40 * 100`, which is `25.0`. Divide by the **old** value, the one you started from.
- **Ratios split a whole.** Two parts juice to three parts water is five parts in all, so the juice is `2 / 5` of the whole and the water `3 / 5`.
- **Order of operations:** parentheses first, then `**`, then `* / // %`, then `+ -`, left to right within a level. So `2 + 3 * 4 ** 2` is `2 + 3 * 16`, which is `50`. When a line mixes operations, add parentheses: they cost nothing and say what you mean.
- **Round at the end,** when a number is shown to a person, not in the middle of a calculation: rounding early loses precision that later steps needed.

</Recap>
''',
)

# --- practice: recall --------------------------------------------------------

write(
    "recall/parsons-percent-off.yaml",
    '''id: parsons-percent-off
type: parsons
rev: 1
prompt: |
  Put the lines in order so the program prints `You pay 60.0` for a price of 80 with 25% off. One line is a decoy that doesn't belong.
lines:
  - 'price = 80'
  - 'discount = price * 25 / 100'
  - 'final = price - discount'
  - 'print("You pay", final)'
distractors:
  - 'final = price - 25'
explanation: |
  25% off means a quarter of the **price** comes off, so the discount is `price * 25 / 100`, which is 20.0, and the final price is 60.0. `price - 25` would take 25 dollars off instead of 25 percent.
skills: [percent]
''',
)

write(
    "recall/mcq-order-of-operations.yaml",
    '''id: mcq-order-of-operations
type: mcq
rev: 1
prompt: |
  What does this line show?

  ```python
  print(2 + 3 * 4 ** 2)
  ```
choices:
  - '`400`'
  - '`80`'
  - '`50`'
  - '`196`'
answer: 2
explanation: |
  Powers first: `4 ** 2` is 16. Then multiplication: `3 * 16` is 48. Then addition: `2 + 48` is `50`. The other answers come from doing the operations left to right, or adding before multiplying: `(2 + 3) * 16` is 80, `(2 + 3 * 4) ** 2` is 196, and `((2 + 3) * 4) ** 2` is 400.
skills: [order]
''',
)

write(
    "recall/predict-fraction-to-decimal.yaml",
    '''id: predict-fraction-to-decimal
type: predict_output
rev: 1
prompt: |
  Each line turns fractions into numbers. What does the program print?
code: |
  print(1 / 8)
  print(3 / 8 + 1 / 8)
  print(7 // 8)
expected_output: |
  0.125
  0.5
  0
explanation: |
  A fraction is a division: one eighth is `1 / 8`, which is `0.125`. Fractions with the same bottom add up: three eighths plus one eighth is four eighths, `0.5`. The last line uses `//`, floor division, which keeps only the whole number of times 8 fits into 7: `0`.
skills: [fractions]
''',
)

write(
    "recall/mcq-percent-change.yaml",
    '''id: mcq-percent-change
type: mcq
rev: 1
prompt: |
  A plant grew from 40 cm to 50 cm. Which expression gives the percentage change in its height?
choices:
  - '`(50 - 40) / 50 * 100`'
  - '`50 / 40`'
  - '`(50 - 40) / 40 * 100`'
  - '`50 - 40`'
answer: 2
explanation: |
  Percentage change compares the change with what you **started** from: `(50 - 40) / 40 * 100` is 10 / 40 × 100, which is `25.0`, a 25% increase. Dividing by 50 compares with the new height instead and gives 20%; `50 / 40` is the ratio 1.25, not a percentage; and `50 - 40` is the change in centimetres.
skills: [percent]
''',
)

write(
    "recall/review-predict-percent.yaml",
    '''id: review-predict-percent
type: predict_output
rev: 1
prompt: |
  Three ways of working with 20% of a price of 50. What does the program print?
code: |
  price = 50
  print(price * 20 / 100)
  print(price * 0.2)
  print(price - price * 20 / 100)
expected_output: |
  10.0
  10.0
  40.0
explanation: |
  20% of 50 is `50 * 20 / 100`, which is `10.0` (a float, because `/` always gives one). `0.2` is 20 / 100 already, so `50 * 0.2` is the same `10.0`. The last line takes the 20% off: `50 - 10.0` is `40.0`.
skills: [percent]
''',
)

write(
    "recall/review-mcq-fractions.yaml",
    '''id: review-mcq-fractions
type: mcq
rev: 1
prompt: |
  Which expression gives three quarters as a decimal, `0.75`?
choices:
  - '`3 // 4`'
  - '`3 / 4`'
  - '`3 % 4`'
  - '`4 / 3`'
answer: 1
explanation: |
  A fraction is its top divided by its bottom: `3 / 4` is `0.75`. `3 // 4` is `0` (floor division keeps only whole times), `3 % 4` is `3` (the remainder), and `4 / 3` is the fraction upside down, about `1.33`.
skills: [fractions]
''',
)

# --- practice: exercises -------------------------------------------------------

write(
    "exercises/example-recipe-scaling/exercise.yaml",
    '''id: example-recipe-scaling
stage: worked_example
rev: 1
title: "Scaling a recipe"
prompt: |
  A recipe for two people needs two thirds of a cup of sugar. This program works out the sugar for five people. Press **Run**, then read how each part works.
steps:
  - label: "A fraction is a division"
    lines: "1"
    note: "Two thirds is 2 ÷ 3, so `2 / 3` gives the decimal `0.6666666666666666`. Floats are approximate: the real value goes on forever."
  - label: "Scale it"
    lines: "2-3"
    note: "Divide by 2 for one person, then multiply by 5 for five. Python does the division first, then the multiplication, left to right: `0.333… * 5`."
  - label: "Show the raw number"
    lines: "4"
    note: "`1.6666666666666665`: the full float, with a last digit that's off because of how floats are stored. Right, but not what a recipe says."
  - label: "Round for people"
    lines: "5-6"
    note: "`round(sugar, 2)` gives `1.67`, and the f-string `:.2f` shows two decimal places inside text. Round at the end, when the number is shown, not in the middle."
''',
)
write(
    "exercises/example-recipe-scaling/solution.py",
    '''sugar_for_two = 2 / 3
people = 5
sugar = sugar_for_two / 2 * people
print(sugar)
print(round(sugar, 2))
print(f"{sugar:.2f} cups of sugar")
''',
)
write(
    "exercises/example-recipe-scaling/test_exercise.py",
    '''from checks import run


def test_scales_the_recipe():
    """Prints the raw amount, then 1.67, then 1.67 cups of sugar."""
    assert run() == "1.6666666666666665\\n1.67\\n1.67 cups of sugar\\n"
''',
)

write(
    "exercises/fill-tip-and-split/exercise.yaml",
    '''id: fill-tip-and-split
stage: fill_in
rev: 1
title: "Tip and split"
prompt: |
  A bill of 84.5 gets an 18% tip and is split between 3 people. Replace each `...` so the program prints:

  ```
  Total with tip: 99.71
  Each pays: 33.24
  ```

  Until every `...` is replaced, Python can't run the program at all, and shows a syntax error.
hints:
  - "18% of the bill is the bill times 18, divided by 100."
  - "Each person pays the total **with the tip** divided by the number of people."
skills: [percent]
''',
)
write(
    "exercises/fill-tip-and-split/starter.py",
    '''bill = 84.5
tip_percent = 18
people = 3
tip = bill * tip_percent ...
total = bill + tip
each = total ...
print(f"Total with tip: {total:.2f}")
print(f"Each pays: {each:.2f}")
''',
)
write(
    "exercises/fill-tip-and-split/solution.py",
    '''bill = 84.5
tip_percent = 18
people = 3
tip = bill * tip_percent / 100
total = bill + tip
each = total / people
print(f"Total with tip: {total:.2f}")
print(f"Each pays: {each:.2f}")
''',
)
write(
    "exercises/fill-tip-and-split/test_exercise.py",
    '''from checks import run, run_with


def test_this_bill():
    """Prints Total with tip: 99.71, then Each pays: 33.24."""
    printed = run()
    assert printed == "Total with tip: 99.71\\nEach pays: 33.24\\n", (
        f"Your program printed:\\n{printed}"
    )


def test_any_bill():
    """Works for any bill, tip and number of people."""
    printed = run_with({"bill": 60, "tip_percent": 20, "people": 4})
    assert printed == "Total with tip: 72.00\\nEach pays: 18.00\\n", (
        "With a bill of 60, a 20% tip and 4 people it should print "
        f"Total with tip: 72.00, then Each pays: 18.00. It printed:\\n{printed}"
    )
''',
)
write(
    "exercises/fill-tip-and-split/wrong/tip-not-a-percent.py",
    '''bill = 84.5
tip_percent = 18
people = 3
tip = bill * tip_percent
total = bill + tip
each = total / people
print(f"Total with tip: {total:.2f}")
print(f"Each pays: {each:.2f}")
''',
)
write(
    "exercises/fill-tip-and-split/wrong/typed-in.py",
    '''bill = 84.5
tip_percent = 18
people = 3
tip = 15.21
total = 99.71
each = 33.24
print(f"Total with tip: {total:.2f}")
print(f"Each pays: {each:.2f}")
''',
)

write(
    "exercises/write-mix-ratio/exercise.yaml",
    '''id: write-mix-ratio
stage: write
rev: 1
title: "Fruit punch"
prompt: |
  Fruit punch is 2 parts juice to 3 parts water. Starting from `total = 1.5` litres, print how much juice and how much water to use, each with two decimal places:

  ```
  Juice: 0.60 litres
  Water: 0.90 litres
  ```

  Keep the line `total = 1.5`: the checks run your program with other totals too.
hints:
  - "2 parts and 3 parts make 5 parts in all. What fraction of the whole is juice?"
  - "The juice is `total * 2 / 5`. Write the water the same way."
  - "Show two decimal places with an f-string: `f\\"{juice:.2f}\\"`."
skills: [fractions, order]
''',
)
write("exercises/write-mix-ratio/starter.py", "total = 1.5\n")
write(
    "exercises/write-mix-ratio/solution.py",
    '''total = 1.5
juice = total * 2 / 5
water = total * 3 / 5
print(f"Juice: {juice:.2f} litres")
print(f"Water: {water:.2f} litres")
''',
)
write(
    "exercises/write-mix-ratio/test_exercise.py",
    '''from checks import run, run_with


def test_one_and_a_half_litres():
    """Prints Juice: 0.60 litres, then Water: 0.90 litres."""
    printed = run()
    assert printed == "Juice: 0.60 litres\\nWater: 0.90 litres\\n", (
        f"Your program printed:\\n{printed}"
    )


def test_any_total():
    """Works for any total: 2.0 litres gives 0.80 and 1.20."""
    printed = run_with({"total": 2.0})
    assert printed == "Juice: 0.80 litres\\nWater: 1.20 litres\\n", (
        f"With total = 2.0 it should print Juice: 0.80 litres, then Water: 1.20 litres. It printed:\\n{printed}"
    )
''',
)
write(
    "exercises/write-mix-ratio/wrong/parts-not-fractions.py",
    '''total = 1.5
juice = total * 2 / 3
water = total - juice
print(f"Juice: {juice:.2f} litres")
print(f"Water: {water:.2f} litres")
''',
)
write(
    "exercises/write-mix-ratio/wrong/typed-in.py",
    '''total = 1.5
print("Juice: 0.60 litres")
print("Water: 0.90 litres")
''',
)

# --- proof ------------------------------------------------------------------

write(
    "exercises/build-sale-receipt/exercise.yaml",
    '''id: build-sale-receipt
stage: build
rev: 1
title: "Sale receipt"
prompt: |
  Starting from a blank editor, write a program that prints a receipt for a sale. Start with `price = 120`, `discount_percent = 15` and `tax_percent = 8`, one line each. The discount comes off the price first; then the tax is added to the discounted price. Print, each amount with two decimal places:

  ```
  Discount: 18.00
  Price after discount: 102.00
  Tax: 8.16
  Total: 110.16
  ```
skills: [percent, order]
''',
)
write("exercises/build-sale-receipt/starter.py", "")
write(
    "exercises/build-sale-receipt/solution.py",
    '''price = 120
discount_percent = 15
tax_percent = 8
discount = price * discount_percent / 100
after_discount = price - discount
tax = after_discount * tax_percent / 100
total = after_discount + tax
print(f"Discount: {discount:.2f}")
print(f"Price after discount: {after_discount:.2f}")
print(f"Tax: {tax:.2f}")
print(f"Total: {total:.2f}")
''',
)
write(
    "exercises/build-sale-receipt/test_exercise.py",
    '''from checks import run, run_with

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_this_sale():
    """Prints the discount, the price after it, the tax and the total for 120, 15% and 8%."""
    assert run() == (
        "Discount: 18.00\\nPrice after discount: 102.00\\nTax: 8.16\\nTotal: 110.16\\n"
    )


def test_any_sale():
    """Works for any price, discount and tax: the tax is charged on the discounted price."""
    printed = run_with({"price": 50, "discount_percent": 10, "tax_percent": 20})
    assert printed == (
        "Discount: 5.00\\nPrice after discount: 45.00\\nTax: 9.00\\nTotal: 54.00\\n"
    )
''',
)
write(
    "exercises/build-sale-receipt/wrong/tax-on-full-price.py",
    '''price = 120
discount_percent = 15
tax_percent = 8
discount = price * discount_percent / 100
after_discount = price - discount
tax = price * tax_percent / 100
total = after_discount + tax
print(f"Discount: {discount:.2f}")
print(f"Price after discount: {after_discount:.2f}")
print(f"Tax: {tax:.2f}")
print(f"Total: {total:.2f}")
''',
)
write(
    "exercises/build-sale-receipt/wrong/discount-as-amount.py",
    '''price = 120
discount_percent = 15
tax_percent = 8
discount = discount_percent
after_discount = price - discount
tax = after_discount * tax_percent / 100
total = after_discount + tax
print(f"Discount: {discount:.2f}")
print(f"Price after discount: {after_discount:.2f}")
print(f"Tax: {tax:.2f}")
print(f"Total: {total:.2f}")
''',
)
write(
    "exercises/build-sale-receipt/wrong/typed-in.py",
    '''price = 120
discount_percent = 15
tax_percent = 8
print("Discount: 18.00")
print("Price after discount: 102.00")
print("Tax: 8.16")
print("Total: 110.16")
''',
)

write(
    "exercises/debug-average-score/exercise.yaml",
    '''id: debug-average-score
stage: debug
rev: 1
title: "Average score"
prompt: |
  Three quizzes were marked out of 30. This program should print the average mark and what percentage that is:

  ```
  Average: 19.0 out of 30
  Percent: 63.3%
  ```

  It has two bugs. Run it, fix what you find, and run it again. Check each number, not just whether it runs.
skills: [order, percent]
''',
)
write(
    "exercises/debug-average-score/starter.py",
    '''quiz1 = 18
quiz2 = 24
quiz3 = 15
out_of = 30
average = quiz1 + quiz2 + quiz3 / 3
percent = average / out_of
print(f"Average: {average:.1f} out of {out_of}")
print(f"Percent: {percent:.1f}%")
''',
)
write(
    "exercises/debug-average-score/solution.py",
    '''quiz1 = 18
quiz2 = 24
quiz3 = 15
out_of = 30
average = (quiz1 + quiz2 + quiz3) / 3
percent = average / out_of * 100
print(f"Average: {average:.1f} out of {out_of}")
print(f"Percent: {percent:.1f}%")
''',
)
write(
    "exercises/debug-average-score/test_exercise.py",
    '''from checks import run, run_with

EXPECTED = "Average: 19.0 out of 30\\nPercent: 63.3%\\n"


def test_these_quizzes():
    """Prints Average: 19.0 out of 30, then Percent: 63.3%."""
    printed = run()
    assert printed == EXPECTED, (
        f"Expected this:\\n{EXPECTED}\\nYour program printed:\\n{printed}"
    )


def test_any_quizzes():
    """Works for any marks: 10, 20 and 30 out of 40 give 20.0 and 50.0%."""
    printed = run_with({"quiz1": 10, "quiz2": 20, "quiz3": 30, "out_of": 40})
    assert printed == "Average: 20.0 out of 40\\nPercent: 50.0%\\n", (
        f"With marks 10, 20 and 30 out of 40 it should print Average: 20.0 out of 40, then Percent: 50.0%. It printed:\\n{printed}"
    )
''',
)
write(
    "exercises/debug-average-score/wrong/only-average-fixed.py",
    '''quiz1 = 18
quiz2 = 24
quiz3 = 15
out_of = 30
average = (quiz1 + quiz2 + quiz3) / 3
percent = average / out_of
print(f"Average: {average:.1f} out of {out_of}")
print(f"Percent: {percent:.1f}%")
''',
)
write(
    "exercises/debug-average-score/wrong/only-percent-fixed.py",
    '''quiz1 = 18
quiz2 = 24
quiz3 = 15
out_of = 30
average = quiz1 + quiz2 + quiz3 / 3
percent = average / out_of * 100
print(f"Average: {average:.1f} out of {out_of}")
print(f"Percent: {percent:.1f}%")
''',
)
write(
    "exercises/debug-average-score/wrong/typed-in.py",
    '''quiz1 = 18
quiz2 = 24
quiz3 = 15
out_of = 30
average = 19.0
percent = 63.3
print(f"Average: {average:.1f} out of {out_of}")
print(f"Percent: {percent:.1f}%")
''',
)

# --- review pool: a code exercise -------------------------------------------

write(
    "exercises/review-unit-price/exercise.yaml",
    '''id: review-unit-price
stage: review_code
rev: 1
title: "Price per kilogram"
prompt: |
  A pack of coffee costs `pack_price = 4.5` and weighs `grams = 750`. Print the price per kilogram with two decimal places:

  ```
  Per kg: 6.00
  ```

  Keep the two starting lines: the checks run your program with other packs too.
skills: [fractions, order]
''',
)
write("exercises/review-unit-price/starter.py", "pack_price = 4.5\ngrams = 750\n")
write(
    "exercises/review-unit-price/solution.py",
    '''pack_price = 4.5
grams = 750
per_kg = pack_price / grams * 1000
print(f"Per kg: {per_kg:.2f}")
''',
)
write(
    "exercises/review-unit-price/test_exercise.py",
    '''from checks import run, run_with


def test_this_pack():
    """Prints Per kg: 6.00 for 4.5 and 750 grams."""
    assert run() == "Per kg: 6.00\\n"


def test_any_pack():
    """Works for any pack: 3.6 for 450 grams is 8.00 per kg."""
    assert run_with({"pack_price": 3.6, "grams": 450}) == "Per kg: 8.00\\n"
''',
)
write(
    "exercises/review-unit-price/wrong/per-gram.py",
    '''pack_price = 4.5
grams = 750
per_kg = pack_price / grams
print(f"Per kg: {per_kg:.2f}")
''',
)
write(
    "exercises/review-unit-price/wrong/typed-in.py",
    '''pack_price = 4.5
grams = 750
print("Per kg: 6.00")
''',
)

print("ml.math.arithmetic written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
