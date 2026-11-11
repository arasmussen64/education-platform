"""Writes the topic ml.py.comprehensions (the ML track's Module 2 opener).
Run from the repository root. Files are written as bytes with LF endings."""

import pathlib

ROOT = pathlib.Path("content/topics/ml.py.comprehensions")


def write(relative: str, text: str) -> None:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


write(
    "topic.yaml",
    '''id: ml.py.comprehensions
kind: topic
status: ready
title: "Comprehensions"
summary: "List, dict and set comprehensions, and when a loop is clearer."
prerequisites: [py.m5.checkpoint]
estimated_minutes: 45
rev: 1
objectives:
  - "Write list, dict and set comprehensions with conditions."
  - "Say when a plain loop is clearer."
  - "Avoid the nested-comprehension trap."
resources:
  - title: "The Python Tutorial: List Comprehensions, and Dictionaries (Python Software Foundation)"
    url: https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions
    type: reading
    use: link
    license: PSF License Version 2
  - title: "Python for Everybody, chapter 10: Tuples (Dr. Chuck): the section on comprehensions, as background"
    url: https://www.py4e.com/html3/10-tuples
    type: reading
    use: link
    license: CC BY 4.0
practice:
  - example-loop-to-comprehension
  - parsons-filter-and-square
  - mcq-read-a-comprehension
  - predict-dict-comprehension
  - mcq-when-a-loop-is-clearer
  - fill-keep-the-long-words
  - write-pass-or-fail
prove:
  build: build-three-summaries
  debug: debug-comprehension-mixups
  explain:
    prompt: |
      A teammate rewrites every loop in the code base as a comprehension, including this one:

      ```python
      results = []
      for row in rows:
          if row["status"] == "ok":
              value = parse(row["value"])
              if value is not None:
                  results.append(value)
      ```

      In your own words: what is a comprehension good at, and why is it often clearer than a loop? What can a loop do that a comprehension can't? Would you rewrite the loop above, and why or why not? And what goes wrong when people nest comprehensions?
    rubric:
      - id: good-at
        required: true
        description: "A comprehension builds a new list, dict or set from an existing sequence, mapping and filtering in one line that reads like a description of the result."
      - id: loop-only
        required: true
        description: "A loop can do several things per item, stop early (break), keep extra state, or have side effects like printing; a comprehension can only produce one value per item."
      - id: this-one
        required: true
        description: "This loop calls parse once and uses the result twice (to test it and to keep it), so a comprehension would call parse twice or need a trick; keep the loop, or at most comprehend over a helper."
      - id: nesting
        required: true
        description: "Nested comprehensions put the for clauses in an order that reads backwards from the result, and become hard to read; past one level, write loops."
      - id: naming
        required: false
        description: "Mentions giving the comprehension's result a good name, or that a comprehension shouldn't be used for its side effects."
    model_answer: |
      A comprehension makes a new list, dict or set out of an existing sequence: for each item, optionally keep it if a condition holds, and transform it. Written on one line it reads like a description of the result, "the squares of the even numbers", which is why it's often clearer than the four lines of loop that build the same thing. A loop can do more. It can do several things to each item, keep a running total or other state, stop early with break, and print or write files as it goes; a comprehension produces exactly one value per item and nothing else. The loop above is one I'd keep: it calls parse once and uses the result twice, to check it isn't None and to keep it, so a comprehension would have to call parse twice or hide the double use in a trick, and the two conditions are easier to read stacked. Nesting is where comprehensions go wrong: [x for row in grid for x in row] has its for clauses in the opposite order from how the result reads, and a second level of nesting, or a condition in the middle, becomes a puzzle. Past one level, write the loops.
review_pool:
  - review-predict-nested
  - review-mcq-set-comprehension
  - review-filter-a-dict
  - review-mcq-nested-order
# What this topic teaches. Each question names the skills it tests, so a
# missed question can come back as a different one on the same skill
# (ADR-0011).
skills:
  - id: list-comp
    description: "Write and read a list comprehension"
  - id: dict-set-comp
    description: "Write and read dict and set comprehensions"
  - id: conditions
    description: "Filter with an if clause inside a comprehension"
  - id: judgement
    description: "Say when a loop is clearer than a comprehension, and avoid the nested-comprehension trap"
''',
)

write(
    "lesson.mdx",
    '''<Intro>

You've written a hundred loops that build a list: start empty, go through something, append. Python has a shorter way to say exactly that, called a comprehension, and most Python you'll read from now on uses it. This topic opens Module 2, the intermediate Python the rest of the track is written in.

The main resource is the official Python tutorial's section on **list comprehensions** (and the short note on dict comprehensions just below it). About 15 minutes. Watch for:

- **The shape:** `[expression for item in sequence]`, optionally `if condition` at the end.
- **The three kinds:** square brackets make a list, curly braces with `key: value` make a dict, curly braces without make a set.
- **It's the same loop,** just written as a description of the result. Everything a comprehension does, a loop can do; not the other way round.

The second resource is older and uses some syntax you haven't met yet; skim it only if you want a second explanation.

</Intro>

<Resource index={0} />

<Recap>

- **A list comprehension** is a loop that builds a list, on one line: `[n * n for n in numbers]` is the squares. Read it as "n squared, for each n in numbers".
- **A condition filters:** `[n * n for n in numbers if n % 2 == 0]` keeps only the even ones. The `if` goes at the end, after the `for`.
- **Dict comprehensions** make a dict: `{w: len(w) for w in words}` maps each word to its length. **Set comprehensions** make a set: `{w[0] for w in words}` is the set of first letters, each once. (Print a set through `sorted()` when the order matters, because a set has none.)
- **When to use a loop instead:** when you'd do more than one thing per item, keep a running total, stop early, print as you go, or use a computed value twice. A comprehension produces one value per item and nothing else; if yours needs a trick, it's a loop.
- **The nested trap:** `[x for row in grid for x in row]` flattens a grid, with the `for` clauses in the order you'd write the loops, outer first, which is the opposite of how the result reads. Past one level, write the loops; nobody will thank you for the one-liner.
- **Name the result well.** `squares = [...]` tells the reader what it is; the comprehension tells them how.
- **In machine learning:** comprehensions are everywhere in data preparation: `[len(text) for text in texts]`, `{word: i for i, word in enumerate(vocabulary)}`. Reading them fast matters more than writing clever ones.

</Recap>
''',
)

# --- practice: recall --------------------------------------------------------

write(
    "recall/parsons-filter-and-square.yaml",
    '''id: parsons-filter-and-square
type: parsons
rev: 1
prompt: |
  Put the lines in order so the program prints the squares of the numbers greater than 4: `[64, 25, 144]`. One line is a decoy that doesn't belong.
lines:
  - 'numbers = [3, 8, 5, 12]'
  - 'big = [n * n for n in numbers if n > 4]'
  - 'print(big)'
distractors:
  - 'big = [n * n if n > 4 for n in numbers]'
explanation: |
  The condition goes at the **end** of a comprehension, after the `for`: "n squared, for each n in numbers, if n is greater than 4". The decoy puts the `if` before the `for`, which isn't valid Python (an `if` before the `for` would need an `else`, and means something different).
skills: [list-comp, conditions]
''',
)

write(
    "recall/mcq-read-a-comprehension.yaml",
    '''id: mcq-read-a-comprehension
type: mcq
rev: 1
prompt: |
  What does this expression give?

  ```python
  [len(w) for w in ["hi", "hello"]]
  ```
choices:
  - '`[2, 5]`'
  - '`7`'
  - '`["hi", "hello"]`'
  - '`["h", "h"]`'
answer: 0
explanation: |
  Read it as "the length of w, for each w in the list": a new list with one number per word, `[2, 5]`. It doesn't add them up (that would be `sum(...)` around it), and it keeps the lengths, not the words.
skills: [list-comp]
''',
)

write(
    "recall/predict-dict-comprehension.yaml",
    '''id: predict-dict-comprehension
type: predict_output
rev: 1
prompt: |
  A dict comprehension over another dict's items. What does the program print?
code: |
  prices = {"tea": 2.5, "cake": 4.0}
  doubled = {name: price * 2 for name, price in prices.items()}
  print(doubled)
expected_output: |
  {'tea': 5.0, 'cake': 8.0}
explanation: |
  `.items()` gives each `(name, price)` pair, and the comprehension builds a new dict with the same keys and doubled values. Dicts keep their insertion order, so `tea` comes first, as in the original. The original `prices` is unchanged.
skills: [dict-set-comp]
''',
)

write(
    "recall/mcq-when-a-loop-is-clearer.yaml",
    '''id: mcq-when-a-loop-is-clearer
type: mcq
rev: 1
prompt: |
  Which of these is a job for a plain loop, not a comprehension?
choices:
  - 'The lengths of every word in a list'
  - 'The even numbers in a list, squared'
  - 'Printing each name in a list on its own line'
  - 'A dict from each word to its first letter'
answer: 2
explanation: |
  Printing is a side effect: nothing is being built. A comprehension that's written for its side effects (`[print(n) for n in names]`) builds a list of `None`s nobody wants, and misleads the reader, who expects a comprehension to produce a value. The other three build a new list or dict from a sequence, which is exactly what comprehensions are for.
skills: [judgement]
''',
)

write(
    "recall/review-predict-nested.yaml",
    '''id: review-predict-nested
type: predict_output
rev: 1
prompt: |
  A comprehension inside a comprehension builds a small multiplication table. What does the program print?
code: |
  table = [[i * j for j in range(1, 3)] for i in range(1, 3)]
  print(table)
expected_output: |
  [[1, 2], [2, 4]]
explanation: |
  The outer comprehension makes one row per `i` (1 and 2); each row is the inner comprehension, `i * j` for `j` in 1 and 2. So row 1 is `[1, 2]` and row 2 is `[2, 4]`. A comprehension **inside** another, like this, reads fine; it's the flattened form with two `for`s in one comprehension that gets hard to read.
skills: [list-comp]
''',
)

write(
    "recall/review-mcq-set-comprehension.yaml",
    '''id: review-mcq-set-comprehension
type: mcq
rev: 1
prompt: |
  How many values does this set contain?

  ```python
  {n % 3 for n in range(10)}
  ```
choices:
  - '10'
  - '3'
  - '9'
  - '1'
answer: 1
explanation: |
  `n % 3` can only be 0, 1 or 2, and a set keeps each value once, so the set is `{0, 1, 2}`: three values. A list comprehension with the same body would have ten entries, with repeats.
skills: [dict-set-comp]
''',
)

write(
    "recall/review-mcq-nested-order.yaml",
    '''id: review-mcq-nested-order
type: mcq
rev: 1
prompt: |
  `grid = [[1, 2], [3, 4]]`. Which comprehension flattens it to `[1, 2, 3, 4]`, and what's the catch?
choices:
  - '`[x for x in row for row in grid]`; no catch'
  - '`[x for row in grid for x in row]`; the for clauses go outer first, the opposite of how the result reads, so past one level a loop is clearer'
  - '`[row for row in grid]`; it already is flat'
  - '`[grid[x] for x in range(4)]`; a grid is just a list'
answer: 1
explanation: |
  With two `for` clauses in one comprehension, they come in the order you'd write the loops: `for row in grid` first, then `for x in row`. That's valid and common for one level of flattening, but it reads backwards from the result, and one more level or a condition in the middle turns it into a puzzle. The first choice uses `row` before it exists and fails.
skills: [list-comp, judgement]
''',
)

# --- practice: exercises -------------------------------------------------------

write(
    "exercises/example-loop-to-comprehension/exercise.yaml",
    '''id: example-loop-to-comprehension
stage: worked_example
rev: 1
title: "From a loop to a comprehension"
prompt: |
  This program builds the same list twice, once with a loop and once with a comprehension, then shows a condition, a dict comprehension and a set comprehension. Press **Run**, then read how each part works.
steps:
  - label: "The loop you know"
    lines: "1-5"
    note: "Start empty, go through the numbers, append each square. Four lines to say 'the squares of the numbers'."
  - label: "The same thing as a comprehension"
    lines: "7-8"
    note: "`[n * n for n in numbers]`: the expression to keep, then the loop it comes from. Same list, one line, and it reads like the description."
  - label: "A condition"
    lines: "10-11"
    note: "`if n % 2 == 0` at the end keeps only the even numbers before squaring them: `[4, 16]`."
  - label: "A dict and a set"
    lines: "13-16"
    note: "Curly braces with `key: value` make a dict (each word to its length); without, a set (each first letter once). A set has no order, so it's printed through `sorted()`."
''',
)
write(
    "exercises/example-loop-to-comprehension/solution.py",
    '''numbers = [1, 2, 3, 4, 5]
squares = []
for n in numbers:
    squares.append(n * n)
print(squares)

squares = [n * n for n in numbers]
print(squares)

even_squares = [n * n for n in numbers if n % 2 == 0]
print(even_squares)

words = ["apple", "fig", "avocado"]
lengths = {w: len(w) for w in words}
print(lengths)
print(sorted({w[0] for w in words}))
''',
)
write(
    "exercises/example-loop-to-comprehension/test_exercise.py",
    '''from checks import run


def test_the_four_results():
    """Prints the squares twice, the even squares, the lengths and the first letters."""
    assert run() == (
        "[1, 4, 9, 16, 25]\\n[1, 4, 9, 16, 25]\\n[4, 16]\\n"
        "{'apple': 5, 'fig': 3, 'avocado': 7}\\n['a', 'f']\\n"
    )
''',
)

write(
    "exercises/fill-keep-the-long-words/exercise.yaml",
    '''id: fill-keep-the-long-words
stage: fill_in
rev: 1
title: "Keep the long words"
prompt: |
  Replace each `...` so the comprehension keeps the words longer than 3 letters, in upper case, and the program prints:

  ```
  ['MOON', 'STAR', 'PLANET']
  ```

  Until every `...` is replaced, Python can't run the program at all, and shows a syntax error.
hints:
  - "The expression at the front is what each kept word becomes: `w.upper()`."
  - "The condition at the end decides which words are kept: `if len(w) > 3`."
skills: [conditions, list-comp]
''',
)
write(
    "exercises/fill-keep-the-long-words/starter.py",
    '''words = ["sun", "moon", "star", "planet"]
long_words = [... for w in words if ...]
print(long_words)
''',
)
write(
    "exercises/fill-keep-the-long-words/solution.py",
    '''words = ["sun", "moon", "star", "planet"]
long_words = [w.upper() for w in words if len(w) > 3]
print(long_words)
''',
)
write(
    "exercises/fill-keep-the-long-words/test_exercise.py",
    '''from checks import run, run_with


def test_these_words():
    """Prints ['MOON', 'STAR', 'PLANET']."""
    printed = run()
    assert printed == "['MOON', 'STAR', 'PLANET']\\n", f"Your program printed:\\n{printed}"


def test_other_words():
    """Works for other words: only 'bbbb' survives from ['a', 'bbbb', 'cc']."""
    printed = run_with({"words": ["a", "bbbb", "cc"]})
    assert printed == "['BBBB']\\n", f"With ['a', 'bbbb', 'cc'] it should print ['BBBB']. It printed:\\n{printed}"
''',
)
write(
    "exercises/fill-keep-the-long-words/wrong/keeps-short-ones.py",
    '''words = ["sun", "moon", "star", "planet"]
long_words = [w.upper() for w in words if len(w) >= 3]
print(long_words)
''',
)
write(
    "exercises/fill-keep-the-long-words/wrong/typed-in.py",
    '''words = ["sun", "moon", "star", "planet"]
long_words = ["MOON", "STAR", "PLANET"]
print(long_words)
''',
)

write(
    "exercises/write-pass-or-fail/exercise.yaml",
    '''id: write-pass-or-fail
stage: write
rev: 1
title: "Pass or fail"
prompt: |
  Starting from `scores = {"Ada": 72, "Bob": 45, "Cy": 50}`, build a dict `results` with a **dict comprehension** that maps each name to `"pass"` if the score is 50 or more and `"fail"` otherwise, then print it:

  ```
  {'Ada': 'pass', 'Bob': 'fail', 'Cy': 'pass'}
  ```

  Keep the starting line: the checks run your program with other scores too.
hints:
  - "Loop over `scores.items()` to get each name and score together."
  - "A value that depends on a condition is written `\\"pass\\" if score >= 50 else \\"fail\\"`: that's an expression, so it can go at the front of a comprehension."
  - "`{name: ... for name, score in scores.items()}`."
skills: [dict-set-comp, conditions]
''',
)
write("exercises/write-pass-or-fail/starter.py", 'scores = {"Ada": 72, "Bob": 45, "Cy": 50}\n')
write(
    "exercises/write-pass-or-fail/solution.py",
    '''scores = {"Ada": 72, "Bob": 45, "Cy": 50}
results = {name: "pass" if score >= 50 else "fail" for name, score in scores.items()}
print(results)
''',
)
write(
    "exercises/write-pass-or-fail/test_exercise.py",
    '''from checks import run, run_with


def test_these_scores():
    """Prints {'Ada': 'pass', 'Bob': 'fail', 'Cy': 'pass'}."""
    printed = run()
    assert printed == "{'Ada': 'pass', 'Bob': 'fail', 'Cy': 'pass'}\\n", f"Your program printed:\\n{printed}"


def test_other_scores():
    """Works for other scores: 49 fails and 50 passes."""
    printed = run_with({"scores": {"Dee": 49, "Eve": 50}})
    assert printed == "{'Dee': 'fail', 'Eve': 'pass'}\\n", (
        f"With Dee 49 and Eve 50 it should print {{'Dee': 'fail', 'Eve': 'pass'}}. It printed:\\n{printed}"
    )
''',
)
write(
    "exercises/write-pass-or-fail/wrong/strictly-above-fifty.py",
    '''scores = {"Ada": 72, "Bob": 45, "Cy": 50}
results = {name: "pass" if score > 50 else "fail" for name, score in scores.items()}
print(results)
''',
)
write(
    "exercises/write-pass-or-fail/wrong/typed-in.py",
    '''scores = {"Ada": 72, "Bob": 45, "Cy": 50}
print({'Ada': 'pass', 'Bob': 'fail', 'Cy': 'pass'})
''',
)

# --- proof ------------------------------------------------------------------

write(
    "exercises/build-three-summaries/exercise.yaml",
    '''id: build-three-summaries
stage: build
rev: 1
title: "Three summaries"
prompt: |
  Starting from a blank editor, write three functions, each a single comprehension inside a `return`:

  - `evens(numbers)` returns a list of the even numbers, in order;
  - `lengths(words)` returns a dict from each word to its length;
  - `initials(names)` returns a **sorted list** of the distinct first letters of the names (build a set, then sort it).

  Then print `evens([1, 2, 3, 4, 5, 6])`, `lengths(["sun", "moon"])` and `initials(["Ada", "Bob", "Alan"])`, one per line:

  ```
  [2, 4, 6]
  {'sun': 3, 'moon': 4}
  ['A', 'B']
  ```

  The checks call your functions with other arguments too.
skills: [list-comp, dict-set-comp, conditions]
''',
)
write("exercises/build-three-summaries/starter.py", "")
write(
    "exercises/build-three-summaries/solution.py",
    '''def evens(numbers):
    return [n for n in numbers if n % 2 == 0]


def lengths(words):
    return {w: len(w) for w in words}


def initials(names):
    return sorted({name[0] for name in names})


print(evens([1, 2, 3, 4, 5, 6]))
print(lengths(["sun", "moon"]))
print(initials(["Ada", "Bob", "Alan"]))
''',
)
write(
    "exercises/build-three-summaries/test_exercise.py",
    '''from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints the three summaries."""
    assert run() == "[2, 4, 6]\\n{'sun': 3, 'moon': 4}\\n['A', 'B']\\n"


def test_evens_and_lengths():
    """evens keeps order and skips odd numbers; lengths maps every word."""
    evens = function("evens")
    lengths = function("lengths")
    assert evens([7, 10, 3, 8]) == [10, 8]
    assert evens([1, 3]) == []
    assert lengths(["a", "bbb"]) == {"a": 1, "bbb": 3}


def test_initials():
    """initials gives each first letter once, sorted."""
    initials = function("initials")
    assert initials(["Zed", "Amy", "Zoe", "Al"]) == ["A", "Z"]
''',
)
write(
    "exercises/build-three-summaries/wrong/initials-repeat.py",
    '''def evens(numbers):
    return [n for n in numbers if n % 2 == 0]


def lengths(words):
    return {w: len(w) for w in words}


def initials(names):
    return sorted([name[0] for name in names])


print(evens([1, 2, 3, 4, 5, 6]))
print(lengths(["sun", "moon"]))
print(initials(["Ada", "Bob", "Alan"]))
''',
)
write(
    "exercises/build-three-summaries/wrong/odds-instead.py",
    '''def evens(numbers):
    return [n for n in numbers if n % 2 == 1]


def lengths(words):
    return {w: len(w) for w in words}


def initials(names):
    return sorted({name[0] for name in names})


print(evens([1, 2, 3, 4, 5, 6]))
print(lengths(["sun", "moon"]))
print(initials(["Ada", "Bob", "Alan"]))
''',
)
write(
    "exercises/build-three-summaries/wrong/typed-in.py",
    '''def evens(numbers):
    return [2, 4, 6]


def lengths(words):
    return {"sun": 3, "moon": 4}


def initials(names):
    return ["A", "B"]


print([2, 4, 6])
print({'sun': 3, 'moon': 4})
print(['A', 'B'])
''',
)

write(
    "exercises/debug-comprehension-mixups/exercise.yaml",
    '''id: debug-comprehension-mixups
stage: debug
rev: 1
title: "Comprehension mix-ups"
prompt: |
  This program should print the even numbers from a list and a dict from each word to its length:

  ```
  [2, 8, 4]
  {'tea': 3, 'bread': 5}
  ```

  It has two bugs. Run it, fix what you find, and run it again. Read each comprehension aloud as a sentence and compare it with what the comment says it should do.
skills: [conditions, dict-set-comp]
''',
)
write(
    "exercises/debug-comprehension-mixups/starter.py",
    '''numbers = [2, 7, 8, 4, 5]
words = ["tea", "bread"]

# The even numbers, in order.
evens = [n for n in numbers if n % 2 == 1]
print(evens)

# Each word mapped to its length.
lengths = {len(w): w for w in words}
print(lengths)
''',
)
write(
    "exercises/debug-comprehension-mixups/solution.py",
    '''numbers = [2, 7, 8, 4, 5]
words = ["tea", "bread"]

# The even numbers, in order.
evens = [n for n in numbers if n % 2 == 0]
print(evens)

# Each word mapped to its length.
lengths = {w: len(w) for w in words}
print(lengths)
''',
)
write(
    "exercises/debug-comprehension-mixups/test_exercise.py",
    '''from checks import run, run_with

EXPECTED = "[2, 8, 4]\\n{'tea': 3, 'bread': 5}\\n"


def test_the_output():
    """Prints [2, 8, 4], then {'tea': 3, 'bread': 5}."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\\n{EXPECTED}\\nYour program printed:\\n{printed}"


def test_other_data():
    """Works for other numbers and words."""
    printed = run_with({"numbers": [1, 6], "words": ["x"]})
    assert printed == "[6]\\n{'x': 1}\\n", f"With [1, 6] and ['x'] it should print [6], then {{'x': 1}}. It printed:\\n{printed}"
''',
)
write(
    "exercises/debug-comprehension-mixups/wrong/only-evens-fixed.py",
    '''numbers = [2, 7, 8, 4, 5]
words = ["tea", "bread"]

# The even numbers, in order.
evens = [n for n in numbers if n % 2 == 0]
print(evens)

# Each word mapped to its length.
lengths = {len(w): w for w in words}
print(lengths)
''',
)
write(
    "exercises/debug-comprehension-mixups/wrong/only-dict-fixed.py",
    '''numbers = [2, 7, 8, 4, 5]
words = ["tea", "bread"]

# The even numbers, in order.
evens = [n for n in numbers if n % 2 == 1]
print(evens)

# Each word mapped to its length.
lengths = {w: len(w) for w in words}
print(lengths)
''',
)
write(
    "exercises/debug-comprehension-mixups/wrong/typed-in.py",
    '''numbers = [2, 7, 8, 4, 5]
words = ["tea", "bread"]
print([2, 8, 4])
print({'tea': 3, 'bread': 5})
''',
)

# --- review pool: a code exercise -------------------------------------------

write(
    "exercises/review-filter-a-dict/exercise.yaml",
    '''id: review-filter-a-dict
stage: review_code
rev: 1
title: "Filter a dict"
prompt: |
  Starting from `stock = {"pens": 12, "ink": 2, "paper": 40, "clips": 3}`, build a dict of the items with more than 3 in stock, with a dict comprehension, and print it:

  ```
  {'pens': 12, 'paper': 40}
  ```

  Keep the starting line: the checks run your program with other stock too.
skills: [dict-set-comp, conditions]
''',
)
write("exercises/review-filter-a-dict/starter.py", 'stock = {"pens": 12, "ink": 2, "paper": 40, "clips": 3}\n')
write(
    "exercises/review-filter-a-dict/solution.py",
    '''stock = {"pens": 12, "ink": 2, "paper": 40, "clips": 3}
plenty = {item: count for item, count in stock.items() if count > 3}
print(plenty)
''',
)
write(
    "exercises/review-filter-a-dict/test_exercise.py",
    '''from checks import run, run_with


def test_this_stock():
    """Prints {'pens': 12, 'paper': 40}."""
    assert run() == "{'pens': 12, 'paper': 40}\\n"


def test_other_stock():
    """Exactly 3 is not more than 3."""
    assert run_with({"stock": {"a": 3, "b": 4}}) == "{'b': 4}\\n"
''',
)
write(
    "exercises/review-filter-a-dict/wrong/three-or-more.py",
    '''stock = {"pens": 12, "ink": 2, "paper": 40, "clips": 3}
plenty = {item: count for item, count in stock.items() if count >= 3}
print(plenty)
''',
)
write(
    "exercises/review-filter-a-dict/wrong/typed-in.py",
    '''stock = {"pens": 12, "ink": 2, "paper": 40, "clips": 3}
print({'pens': 12, 'paper': 40})
''',
)

print("ml.py.comprehensions written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
