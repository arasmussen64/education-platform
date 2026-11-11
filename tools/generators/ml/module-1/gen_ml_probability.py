"""Writes the topic ml.math.probability-and-statistics (the ML track's fifth
topic). Run from the repository root. Files are written as bytes with LF
endings."""

import pathlib

ROOT = pathlib.Path("content/topics/ml.math.probability-and-statistics")


def write(relative: str, text: str) -> None:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


write(
    "topic.yaml",
    '''id: ml.math.probability-and-statistics
kind: topic
status: ready
title: "Probability and statistics"
summary: "Mean, median and spread from a list; chance by counting; base rates with a table of 1,000 people."
prerequisites: [ml.math.arithmetic, py.list-algorithms]
estimated_minutes: 50
rev: 1
objectives:
  - "Compute mean, median and standard deviation from a list."
  - "Work out a probability by counting outcomes."
  - "Multiply probabilities for independent events."
  - "Reason about base rates with a table of 1,000 people."
resources:
  - title: "OpenStax Introductory Statistics 2e: chapter 2 (Descriptive Statistics, sections 2.5 to 2.7) and chapter 3 (Probability Topics, sections 3.1 to 3.3)"
    url: https://openstax.org/details/books/introductory-statistics-2e
    type: reading
    use: link
    license: CC BY 4.0
  - title: "Khan Academy: Statistics and probability"
    url: https://www.khanacademy.org/math/statistics-probability
    type: interactive
    use: link
    license: CC BY-NC-SA 3.0 US (linked, not copied)
practice:
  - example-mean-and-median
  - parsons-chance-by-counting
  - mcq-median-or-mean
  - predict-independent-events
  - mcq-thousand-people
  - fill-standard-deviation
  - write-base-rate-table
prove:
  build: build-grade-report
  debug: debug-dice-odds
  explain:
    prompt: |
      A condition affects 1 person in 100. A test catches it 90% of the time when someone has it, and wrongly says "positive" 10% of the time when they don't. A friend tests positive and says: "The test is 90% accurate, so I'm 90% likely to have it."

      In your own words, using a table of 1,000 people: how many of them have the condition and test positive, how many don't have it but test positive, and so what fraction of the people who test positive actually have it? Where did the friend's reasoning go wrong?
    rubric:
      - id: sick-positives
        required: true
        description: "Of 1,000 people, 10 have the condition, and 90% of them, 9, test positive."
      - id: healthy-positives
        required: true
        description: "990 don't have it, and 10% of them, 99, test positive anyway."
      - id: fraction
        required: true
        description: "So 9 of the 108 positives have it, about 8%; most positives are healthy people."
      - id: friends-error
        required: true
        description: "The 90% is the chance of a positive given the condition; the friend wants the chance of the condition given a positive, which depends on how rare the condition is (the base rate)."
      - id: rarer
        required: false
        description: "Notes that the rarer the condition, the more a positive is a false alarm, or names this as Bayes' rule."
    model_answer: |
      Picture 1,000 people. 1 in 100 has the condition, so 10 do and 990 don't. The test catches 90% of the 10: 9 people who have it test positive. It also wrongly flags 10% of the 990: 99 people who don't have it test positive. So 108 people test positive, and only 9 of them, about 8%, have the condition; the other 99 are healthy. The friend mixed up two different questions. "90% accurate" is the chance of a positive result given that you have the condition. What the friend wants is the chance of having the condition given a positive result, and that depends on how rare the condition is to begin with: when it's rare, the small slice of false positives from the large healthy group outnumbers the true positives from the small sick group. This is the base-rate effect, and working it out properly is Bayes' rule.
review_pool:
  - review-predict-mean-median
  - review-mcq-both-heads
  - review-mcq-spread
  - review-median-of-odd
# What this topic teaches. Each question names the skills it tests, so a
# missed question can come back as a different one on the same skill
# (ADR-0011).
skills:
  - id: center
    description: "Compute the mean and the median of a list, and say which to trust when"
  - id: spread
    description: "Compute the standard deviation of a list, and say what it measures"
  - id: probability
    description: "Work out a probability by counting outcomes, and multiply for independent events"
  - id: base-rate
    description: "Reason about base rates with a table of 1,000 people"
''',
)

write(
    "lesson.mdx",
    '''<Intro>

Statistics is what you do to a list of numbers to say something true about it; probability is counting what could happen. Both are the ground machine learning stands on: a model is judged by statistics of its errors, and most models output probabilities.

The main resource is the free textbook *OpenStax Introductory Statistics 2e*: **chapter 2, sections 2.5 to 2.7** (measures of the center and of the spread of data) and **chapter 3, sections 3.1 to 3.3** (probability, independent events and the rules). About 30 minutes; the examples are long, so read the definitions and skim the rest. Watch for:

- **Mean and median** answer "what's typical?" differently, and one big value changes the mean but not the median.
- **Standard deviation** measures how spread out the numbers are: the typical distance from the mean.
- **Probability as counting:** favourable outcomes divided by all equally likely outcomes.
- **Independent events multiply:** the chance of both is the product of the chances.

The book works examples by hand. Here every one of them is a few lines of Python over a list, and the code is the definition.

</Intro>

<Resource index={0} />

<Recap>

- **Mean:** `sum(values) / len(values)`. **Median:** sort, take the middle (for an even count, the mean of the two middle values). For `[2, 4, 4, 10]` the mean is `5.0` and the median `4.0`: the 10 pulls the mean up and leaves the median alone. Use the median when a few huge values would mislead (salaries, house prices).
- **Standard deviation** is the typical distance from the mean: subtract the mean from each value, square, average the squares, take the square root. For `[2, 4, 4, 4, 5, 5, 7, 9]` it's `2.0`. A small spread means the values huddle near the mean; a large one means they don't.
- **Probability by counting:** for equally likely outcomes, favourable ÷ total. Two dice have 36 outcomes; 6 of them sum to 7, so the chance is `6 / 36`, about 0.167. Nested loops count outcomes without missing any.
- **Independent events multiply:** heads **and** a six is `0.5 * 1 / 6`. **Not** something is `1 - p`: not a six is `5 / 6`.
- **Base rates:** before trusting a test result, ask how common the thing is. Put 1,000 people in a table: how many have it and test positive, how many don't have it and test positive anyway. When the thing is rare, the false positives from the big healthy group outnumber the true positives, so most positives are false alarms. That's Bayes' rule in a table.
- **In machine learning:** the mean of the squared errors is the loss a regression minimizes; standard deviation is how data gets scaled before training; the base-rate table is why a 99%-accurate classifier can be useless for a rare class.

</Recap>
''',
)

# --- practice: recall --------------------------------------------------------

write(
    "recall/parsons-chance-by-counting.yaml",
    '''id: parsons-chance-by-counting
type: parsons
rev: 1
prompt: |
  Two dice are rolled. Put the lines in order so the program counts the outcomes that sum to 7 and prints the chance, `0.16666666666666666`. One line is a decoy that doesn't belong.
lines:
  - 'favourable = 0'
  - 'for first in range(1, 7):'
  - '    for second in range(1, 7):'
  - '        if first + second == 7:'
  - '            favourable = favourable + 1'
  - 'print(favourable / 36)'
distractors:
  - 'print(favourable / 12)'
explanation: |
  Two loops visit every one of the 6 × 6 = 36 equally likely outcomes; the `if` counts the 6 that sum to 7 (1+6, 2+5, 3+4, 4+3, 5+2, 6+1). Favourable over total is `6 / 36`. The decoy divides by 12, as if the two dice only had 12 outcomes between them.
skills: [probability]
''',
)

write(
    "recall/mcq-median-or-mean.yaml",
    '''id: mcq-median-or-mean
type: mcq
rev: 1
prompt: |
  Five salaries, in thousands: `[30, 32, 35, 40, 200]`. Which number better describes what a typical person here earns, and why?
choices:
  - 'The mean, 67.4: it uses every value'
  - 'The median, 35: one very large salary pulls the mean far above what most people earn'
  - 'The mean, 67.4: the median ignores the highest salary'
  - 'Neither: five numbers are too few to say anything'
answer: 1
explanation: |
  The mean is `337 / 5`, 67.4, higher than four of the five salaries, because the 200 drags it up. The median is the middle value once sorted, 35, and the 200 could be 2,000 without changing it. When a few huge values are around, the median is the honest "typical".
skills: [center]
''',
)

write(
    "recall/predict-independent-events.yaml",
    '''id: predict-independent-events
type: predict_output
rev: 1
prompt: |
  A coin flip and a die roll don't affect each other. What does the program print?
code: |
  p_heads = 0.5
  p_six = 1 / 6
  print(p_heads * p_six)
  print(1 - p_six)
expected_output: |
  0.08333333333333333
  0.8333333333333334
explanation: |
  Independent events multiply: heads **and** a six is `0.5 * 1 / 6`, one chance in twelve, `0.08333333333333333`. **Not** a six is everything else: `1 - 1 / 6`, five in six, `0.8333333333333334`. The long decimals are floats being honest about sixths.
skills: [probability]
''',
)

write(
    "recall/mcq-thousand-people.yaml",
    '''id: mcq-thousand-people
type: mcq
rev: 1
prompt: |
  A condition affects 2 people in 100. A test catches every case, and wrongly says "positive" for 5% of healthy people. Of 1,000 people tested, how many test positive **without** having the condition?
choices:
  - '5'
  - '20'
  - '49'
  - '50'
answer: 2
explanation: |
  Of 1,000 people, 20 have the condition and 980 don't. 5% of the 980 healthy people test positive anyway: `980 * 0.05` is `49`. Alongside the 20 true positives, that's 49 of 69 positives who are healthy. (50 would be 5% of all 1,000, forgetting that the 20 sick people aren't false positives.)
skills: [base-rate]
''',
)

write(
    "recall/review-predict-mean-median.yaml",
    '''id: review-predict-mean-median
type: predict_output
rev: 1
prompt: |
  A list with one huge value. What does the program print?
code: |
  values = [1, 2, 3, 100]
  mean = sum(values) / len(values)
  ordered = sorted(values)
  median = (ordered[1] + ordered[2]) / 2
  print(mean)
  print(median)
expected_output: |
  26.5
  2.5
explanation: |
  The mean is `106 / 4`, `26.5`, bigger than three of the four values because the 100 drags it. The median of four values is the mean of the middle two once sorted, `(2 + 3) / 2`, `2.5`, and the 100 doesn't touch it.
skills: [center]
''',
)

write(
    "recall/review-mcq-both-heads.yaml",
    '''id: review-mcq-both-heads
type: mcq
rev: 1
prompt: |
  You flip two fair coins. What is the chance that both land heads?
choices:
  - '`0.5`'
  - '`1.0`'
  - '`0.25`'
  - '`0.75`'
answer: 2
explanation: |
  The flips are independent, so the chances multiply: `0.5 * 0.5` is `0.25`. Counting agrees: of the four equally likely outcomes (HH, HT, TH, TT), one is both heads. Adding the chances (1.0) would mean certainty, which it plainly isn't.
skills: [probability]
''',
)

write(
    "recall/review-mcq-spread.yaml",
    '''id: review-mcq-spread
type: mcq
rev: 1
prompt: |
  Two classes both have a mean test score of 70. Class A's scores have a standard deviation of 2; class B's have a standard deviation of 15. Which statement is true?
choices:
  - 'Class B did better overall'
  - "Class A's scores are nearly all close to 70; class B's are spread far above and below it"
  - 'Class A has more students'
  - "Class B's median must be higher than class A's"
answer: 1
explanation: |
  The mean says where the middle is; the standard deviation says how far scores typically sit from it. A spread of 2 means almost everyone in A scored within a few points of 70; a spread of 15 means B has students in the 50s and the 80s. Neither number says anything about class size or who did "better".
skills: [spread]
''',
)

# --- practice: exercises -------------------------------------------------------

write(
    "exercises/example-mean-and-median/exercise.yaml",
    '''id: example-mean-and-median
stage: worked_example
rev: 1
title: "Mean and median"
prompt: |
  This program finds the mean and the median of four scores. Press **Run**, then read how each part works.
steps:
  - label: "The mean"
    lines: "1-2"
    note: "Add them all up and divide by how many: `20 / 4` is 5.0. `sum()` and `len()` do the two halves."
  - label: "Sort first"
    lines: "3"
    note: "The median needs the values in order. `sorted()` gives a new, sorted list and leaves the original alone."
  - label: "The middle of an even count"
    lines: "4-5"
    note: "With four values there's no single middle one, so the median is the mean of the two middle values, at positions 1 and 2: `(4 + 4) / 2` is 4.0."
  - label: "Compare them"
    lines: "6-7"
    note: "The 10 pulls the mean up to 5.0 but leaves the median at 4.0. That's the whole reason both exist."
''',
)
write(
    "exercises/example-mean-and-median/solution.py",
    '''scores = [2, 4, 4, 10]
mean = sum(scores) / len(scores)
ordered = sorted(scores)
middle = len(ordered) // 2
median = (ordered[middle - 1] + ordered[middle]) / 2
print("mean", mean)
print("median", median)
''',
)
write(
    "exercises/example-mean-and-median/test_exercise.py",
    '''from checks import run


def test_mean_and_median():
    """Prints mean 5.0, then median 4.0."""
    assert run() == "mean 5.0\\nmedian 4.0\\n"
''',
)

write(
    "exercises/fill-standard-deviation/exercise.yaml",
    '''id: fill-standard-deviation
stage: fill_in
rev: 1
title: "Standard deviation"
prompt: |
  The standard deviation is the typical distance from the mean: for each value, square its distance from the mean; average those squares; take the square root. Replace each `...` so the program prints:

  ```
  mean 5.0
  spread 2.0
  ```

  Until every `...` is replaced, Python can't run the program at all, and shows a syntax error.
hints:
  - "The distance from the mean is `value - mean`; squaring it is `** 2`."
  - "Averaging the squares means dividing their total by how many values there are."
  - "A square root is a power of one half: `** 0.5`."
skills: [spread]
''',
)
write(
    "exercises/fill-standard-deviation/starter.py",
    '''values = [2, 4, 4, 4, 5, 5, 7, 9]
mean = sum(values) / len(values)
total = 0
for value in values:
    total = total + (value - mean) ...
variance = total ... len(values)
spread = variance ... 0.5
print("mean", mean)
print("spread", spread)
''',
)
write(
    "exercises/fill-standard-deviation/solution.py",
    '''values = [2, 4, 4, 4, 5, 5, 7, 9]
mean = sum(values) / len(values)
total = 0
for value in values:
    total = total + (value - mean) ** 2
variance = total / len(values)
spread = variance ** 0.5
print("mean", mean)
print("spread", spread)
''',
)
write(
    "exercises/fill-standard-deviation/test_exercise.py",
    '''from checks import run, run_with


def test_these_values():
    """Prints mean 5.0, then spread 2.0."""
    printed = run()
    assert printed == "mean 5.0\\nspread 2.0\\n", f"Your program printed:\\n{printed}"


def test_other_values():
    """Works for any list: [1, 3, 5] has mean 3.0 and spread about 1.63."""
    printed = run_with({"values": [1, 3, 5]})
    assert printed.startswith("mean 3.0\\nspread 1.63"), (
        f"With [1, 3, 5] it should print mean 3.0, then spread 1.63.... It printed:\\n{printed}"
    )
''',
)
write(
    "exercises/fill-standard-deviation/wrong/no-square-root.py",
    '''values = [2, 4, 4, 4, 5, 5, 7, 9]
mean = sum(values) / len(values)
total = 0
for value in values:
    total = total + (value - mean) ** 2
variance = total / len(values)
spread = variance ** 1
print("mean", mean)
print("spread", spread)
''',
)
write(
    "exercises/fill-standard-deviation/wrong/typed-in.py",
    '''values = [2, 4, 4, 4, 5, 5, 7, 9]
mean = sum(values) / len(values)
spread = 2.0
print("mean", mean)
print("spread", spread)
''',
)

write(
    "exercises/write-base-rate-table/exercise.yaml",
    '''id: write-base-rate-table
stage: write
rev: 1
title: "A table of 1,000 people"
prompt: |
  A condition affects a fraction `rate = 0.01` of people. A test catches a fraction `sensitivity = 0.9` of those who have it, and wrongly says "positive" for a fraction `false_positive = 0.1` of those who don't. For `population = 1000` people, print how many test positive and have the condition, and how many test positive without it, as whole numbers:

  ```
  Positive and sick: 9
  Positive and healthy: 99
  ```

  Keep the four starting lines: the checks run your program with other numbers too.
hints:
  - "The sick are `population * rate`; the sick positives are that times `sensitivity`."
  - "The healthy are everyone else; the healthy positives are that times `false_positive`."
  - "Print a float as a whole number with `:.0f`."
skills: [base-rate]
''',
)
write(
    "exercises/write-base-rate-table/starter.py",
    "population = 1000\nrate = 0.01\nsensitivity = 0.9\nfalse_positive = 0.1\n",
)
write(
    "exercises/write-base-rate-table/solution.py",
    '''population = 1000
rate = 0.01
sensitivity = 0.9
false_positive = 0.1
sick = population * rate
healthy = population - sick
print(f"Positive and sick: {sick * sensitivity:.0f}")
print(f"Positive and healthy: {healthy * false_positive:.0f}")
''',
)
write(
    "exercises/write-base-rate-table/test_exercise.py",
    '''from checks import run, run_with


def test_this_test():
    """Prints Positive and sick: 9, then Positive and healthy: 99."""
    printed = run()
    assert printed == "Positive and sick: 9\\nPositive and healthy: 99\\n", (
        f"Your program printed:\\n{printed}"
    )


def test_another_test():
    """Works for other numbers: 2% with a perfect catch rate and 5% false positives gives 20 and 49."""
    printed = run_with({"rate": 0.02, "sensitivity": 1.0, "false_positive": 0.05})
    assert printed == "Positive and sick: 20\\nPositive and healthy: 49\\n", (
        f"With rate 0.02, sensitivity 1.0 and false_positive 0.05 it should print 20, then 49. It printed:\\n{printed}"
    )
''',
)
write(
    "exercises/write-base-rate-table/wrong/false-positives-of-everyone.py",
    '''population = 1000
rate = 0.01
sensitivity = 0.9
false_positive = 0.1
sick = population * rate
print(f"Positive and sick: {sick * sensitivity:.0f}")
print(f"Positive and healthy: {population * false_positive:.0f}")
''',
)
write(
    "exercises/write-base-rate-table/wrong/typed-in.py",
    '''population = 1000
rate = 0.01
sensitivity = 0.9
false_positive = 0.1
print("Positive and sick: 9")
print("Positive and healthy: 99")
''',
)

# --- proof ------------------------------------------------------------------

write(
    "exercises/build-grade-report/exercise.yaml",
    '''id: build-grade-report
stage: build
rev: 1
title: "Grade report"
prompt: |
  Starting from a blank editor, write three functions that each take a list of numbers: `mean(values)`, `median(values)` (sort first; for an even count, the mean of the two middle values) and `spread(values)` (the standard deviation: the square root of the mean of the squared distances from the mean). Then, for `scores = [68, 74, 74, 80, 90, 94]`, print, each with one decimal place:

  ```
  Mean: 80.0
  Median: 77.0
  Spread: 9.2
  ```

  The checks call your functions with other lists too.
skills: [center, spread]
''',
)
write("exercises/build-grade-report/starter.py", "")
write(
    "exercises/build-grade-report/solution.py",
    '''def mean(values):
    return sum(values) / len(values)


def median(values):
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2 == 1:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2


def spread(values):
    average = mean(values)
    total = 0
    for value in values:
        total = total + (value - average) ** 2
    return (total / len(values)) ** 0.5


scores = [68, 74, 74, 80, 90, 94]
print(f"Mean: {mean(scores):.1f}")
print(f"Median: {median(scores):.1f}")
print(f"Spread: {spread(scores):.1f}")
''',
)
write(
    "exercises/build-grade-report/test_exercise.py",
    '''from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_report():
    """Prints the mean, median and spread of the six scores."""
    assert run() == "Mean: 80.0\\nMedian: 77.0\\nSpread: 9.2\\n"


def test_mean_and_median():
    """mean and median work for other lists, odd counts and unsorted ones included."""
    mean = function("mean")
    median = function("median")
    assert mean([10, 20, 30]) == 20.0
    assert median([9, 1, 5]) == 5
    assert median([1, 2, 3, 100]) == 2.5


def test_spread():
    """spread divides by the number of values, and is 0 when they're all the same."""
    spread = function("spread")
    assert round(spread([10, 20, 30]), 2) == 8.16
    assert spread([4, 4, 4]) == 0
''',
)
write(
    "exercises/build-grade-report/wrong/median-without-sorting.py",
    '''def mean(values):
    return sum(values) / len(values)


def median(values):
    middle = len(values) // 2
    if len(values) % 2 == 1:
        return values[middle]
    return (values[middle - 1] + values[middle]) / 2


def spread(values):
    average = mean(values)
    total = 0
    for value in values:
        total = total + (value - average) ** 2
    return (total / len(values)) ** 0.5


scores = [68, 74, 74, 80, 90, 94]
print(f"Mean: {mean(scores):.1f}")
print(f"Median: {median(scores):.1f}")
print(f"Spread: {spread(scores):.1f}")
''',
)
write(
    "exercises/build-grade-report/wrong/sample-spread.py",
    '''def mean(values):
    return sum(values) / len(values)


def median(values):
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2 == 1:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2


def spread(values):
    average = mean(values)
    total = 0
    for value in values:
        total = total + (value - average) ** 2
    return (total / (len(values) - 1)) ** 0.5


scores = [68, 74, 74, 80, 90, 94]
print(f"Mean: {mean(scores):.1f}")
print(f"Median: {median(scores):.1f}")
print(f"Spread: {spread(scores):.1f}")
''',
)
write(
    "exercises/build-grade-report/wrong/typed-in.py",
    '''def mean(values):
    return 80.0


def median(values):
    return 77.0


def spread(values):
    return 9.2


print("Mean: 80.0")
print("Median: 77.0")
print("Spread: 9.2")
''',
)

write(
    "exercises/debug-dice-odds/exercise.yaml",
    '''id: debug-dice-odds
stage: debug
rev: 1
title: "Dice odds"
prompt: |
  This program should count the ways two dice can sum to at least `target = 10`, and print the chance as a percentage:

  ```
  Ways: 6
  Chance: 16.7%
  ```

  It has two bugs. Run it, fix what you find, and run it again. List the six ways on paper first, then check which ones the program is missing.
skills: [probability]
''',
)
write(
    "exercises/debug-dice-odds/starter.py",
    '''target = 10
ways = 0
for first in range(1, 6):
    for second in range(1, 7):
        if first + second >= target:
            ways = ways + 1
chance = ways / 36
print(f"Ways: {ways}")
print(f"Chance: {chance:.1f}%")
''',
)
write(
    "exercises/debug-dice-odds/solution.py",
    '''target = 10
ways = 0
for first in range(1, 7):
    for second in range(1, 7):
        if first + second >= target:
            ways = ways + 1
chance = ways / 36 * 100
print(f"Ways: {ways}")
print(f"Chance: {chance:.1f}%")
''',
)
write(
    "exercises/debug-dice-odds/test_exercise.py",
    '''from checks import run, run_with

EXPECTED = "Ways: 6\\nChance: 16.7%\\n"


def test_at_least_ten():
    """Prints Ways: 6, then Chance: 16.7%."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\\n{EXPECTED}\\nYour program printed:\\n{printed}"


def test_any_target():
    """Works for any target: at least 11 is 3 ways, 8.3%."""
    printed = run_with({"target": 11})
    assert printed == "Ways: 3\\nChance: 8.3%\\n", (
        f"With target = 11 it should print Ways: 3, then Chance: 8.3%. It printed:\\n{printed}"
    )
''',
)
write(
    "exercises/debug-dice-odds/wrong/only-range-fixed.py",
    '''target = 10
ways = 0
for first in range(1, 7):
    for second in range(1, 7):
        if first + second >= target:
            ways = ways + 1
chance = ways / 36
print(f"Ways: {ways}")
print(f"Chance: {chance:.1f}%")
''',
)
write(
    "exercises/debug-dice-odds/wrong/only-percent-fixed.py",
    '''target = 10
ways = 0
for first in range(1, 6):
    for second in range(1, 7):
        if first + second >= target:
            ways = ways + 1
chance = ways / 36 * 100
print(f"Ways: {ways}")
print(f"Chance: {chance:.1f}%")
''',
)
write(
    "exercises/debug-dice-odds/wrong/typed-in.py",
    '''target = 10
ways = 6
chance = 16.7
print(f"Ways: {ways}")
print(f"Chance: {chance:.1f}%")
''',
)

# --- review pool: a code exercise -------------------------------------------

write(
    "exercises/review-median-of-odd/exercise.yaml",
    '''id: review-median-of-odd
stage: review_code
rev: 1
title: "The middle value"
prompt: |
  Starting from `values = [7, 1, 5]`, print the median: the middle value once the list is sorted. The list always has an odd number of values.

  ```
  5
  ```

  Keep the starting line: the checks run your program with other lists too.
skills: [center]
''',
)
write("exercises/review-median-of-odd/starter.py", "values = [7, 1, 5]\n")
write(
    "exercises/review-median-of-odd/solution.py",
    '''values = [7, 1, 5]
ordered = sorted(values)
print(ordered[len(ordered) // 2])
''',
)
write(
    "exercises/review-median-of-odd/test_exercise.py",
    '''from checks import run, run_with


def test_three_values():
    """Prints 5 for [7, 1, 5]."""
    assert run() == "5\\n"


def test_five_values():
    """Prints 5 for [3, 9, 1, 7, 5], the middle once sorted."""
    assert run_with({"values": [3, 9, 1, 7, 5]}) == "5\\n"
''',
)
write(
    "exercises/review-median-of-odd/wrong/forgets-to-sort.py",
    '''values = [7, 1, 5]
print(values[len(values) // 2])
''',
)
write(
    "exercises/review-median-of-odd/wrong/typed-in.py",
    '''values = [7, 1, 5]
print(5)
''',
)

print("ml.math.probability-and-statistics written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
