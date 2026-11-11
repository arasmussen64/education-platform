"""Writes the topic ml.py.iterators-and-generators (Module 2's fourth topic).
Run from the repository root. Files are written as bytes with LF endings."""

import pathlib

ROOT = pathlib.Path("content/topics/ml.py.iterators-and-generators")


def write(relative: str, text: str) -> None:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


write(
    "topic.yaml",
    '''id: ml.py.iterators-and-generators
kind: topic
status: ready
title: "Iterators and generators"
summary: "What for really calls, and generators that produce values one at a time."
prerequisites: [ml.py.comprehensions]
estimated_minutes: 50
rev: 1
objectives:
  - "Explain what `for` really calls."
  - "Write a generator with `yield`, and read a stream lazily."
  - "Say why a generator can be used once."
resources:
  - title: "The Python Tutorial: Iterators, Generators and Generator Expressions (sections 9.8 to 9.10) (Python Software Foundation)"
    url: https://docs.python.org/3/tutorial/classes.html#iterators
    type: reading
    use: link
    license: PSF License Version 2
  - title: "Python for Everybody, chapter 7: Files (Dr. Chuck), for how a file is read line by line"
    url: https://www.py4e.com/html3/07-files
    type: reading
    use: link
    license: CC BY 4.0
practice:
  - example-what-for-really-calls
  - parsons-an-evens-generator
  - mcq-used-once
  - predict-lazy-order
  - mcq-yield-and-return
  - fill-clean-lines
  - write-running-total
prove:
  build: build-sliding-windows
  debug: debug-generator-mistakes
  explain:
    prompt: |
      A teammate's program reads a huge log file into a list, then loops over it twice: once to count errors, once to find the first warning. It runs out of memory. In your own words: what does a `for` loop actually call on the thing it loops over, and how is that different from a list? What would a generator change here, and why would it use almost no memory? And what would go wrong if they replaced the list with a generator and kept the two loops as they are?
    rubric:
      - id: protocol
        required: true
        description: "for calls iter() to get an iterator, then next() on it until it raises StopIteration; a list holds every item in memory, an iterator produces them one at a time."
      - id: generator
        required: true
        description: "A generator function yields one line at a time and pauses between yields, so only the current line is in memory, however big the file."
      - id: single-use
        required: true
        description: "A generator is used up by one pass: the second loop would see nothing, so either loop once doing both jobs, or make a fresh generator for the second pass."
      - id: laziness
        required: false
        description: "Mentions that nothing runs until the first next(), or that a generator expression (round brackets) is the one-line form."
    model_answer: |
      A for loop asks the thing it loops over for an iterator, with iter(), and then calls next() on that iterator again and again until it raises StopIteration. A list answers by handing out its items, but the whole list is already in memory before the loop starts; that's what ran out here. A generator is a function with yield instead of return: each next() runs it until the next yield, hands that value out, and pauses. For a log file that means reading and yielding one line at a time, so only the current line is in memory, whatever the file's size. The catch is that a generator can be walked through once. The first loop would consume every line, and the second loop would get StopIteration immediately and find nothing. So the teammate should either do both jobs in one pass over the lines, or call the generator function again to get a fresh generator for the second pass.
review_pool:
  - review-predict-generator-expression
  - review-mcq-what-for-calls
  - review-mcq-brackets
  - review-first-squares
# What this topic teaches. Each question names the skills it tests, so a
# missed question can come back as a different one on the same skill
# (ADR-0011).
skills:
  - id: protocol
    description: "Explain what for really calls: iter, next and StopIteration"
  - id: generators
    description: "Write a generator with yield, and know that it runs lazily"
  - id: single-use
    description: "Know that a generator is used up by one pass, and make a fresh one when needed"
  - id: genexpr
    description: "Read and write a generator expression, and know how it differs from a list comprehension"
''',
)

write(
    "lesson.mdx",
    '''<Intro>

Every `for` loop you've written has been asking a question you never saw: "give me the next one." Lists answer it from memory; a generator answers it by computing the next value on demand, and then forgetting it. That's how Python reads a file bigger than memory, and how data pipelines in machine learning feed a model one batch at a time.

The main resource is the official tutorial's **sections 9.8 to 9.10**: iterators, generators and generator expressions. About 15 minutes. Watch for:

- **`iter()` and `next()`:** what `for` calls behind the scenes, and `StopIteration`, how the end is signalled.
- **`yield`:** a function with `yield` doesn't run when you call it; it hands back a generator, which runs a step at a time, pausing at each `yield`.
- **Generator expressions:** a comprehension in round brackets, computing one value at a time instead of building a list.

The chapter from Python for Everybody is there for the file-reading picture: `for line in file` is a generator at work.

</Intro>

<Resource index={0} />

<Recap>

- **What `for` calls.** `for x in things:` first calls `iter(things)` to get an iterator, then calls `next()` on it for each loop, until `next()` raises `StopIteration`. You can do it by hand: `it = iter([10, 20])`, `next(it)` is 10, `next(it)` is 20, and the third `next(it)` raises.
- **A generator function** has `yield` where a function would have `return`. Calling it runs nothing; it returns a generator. Each `next()` runs the body until the next `yield`, hands out that value, and **pauses there**, keeping its local variables. When the body ends, `StopIteration`.
- **Lazy means on demand.** `squares = (n * n for n in range(1000000))` builds nothing until something asks; `sum(squares)` pulls the values through one at a time. Memory stays flat however long the stream.
- **A generator is used once.** After one pass it's exhausted: `list(g)` a second time gives `[]`. Need it twice? Call the generator function again, or keep a list if it fits.
- **Generator expressions** are comprehensions in round brackets: `(n * n for n in numbers)`. Pass one straight to `sum`, `max`, `any`, `all`; use square brackets when you need the list itself, more than once, or by index.
- **When to write one:** a sequence that's big, endless, or expensive to compute all at once; reading lines, batches, records from an API page by page.
- **In machine learning:** a data loader is a generator yielding one batch at a time, so training on a terabyte of data needs only one batch of memory; `for batch in loader:` is this protocol, exactly.

</Recap>
''',
)

# --- practice: recall --------------------------------------------------------

write(
    "recall/parsons-an-evens-generator.yaml",
    '''id: parsons-an-evens-generator
type: parsons
rev: 1
prompt: |
  Put the lines in order to define a generator of even numbers below a limit, and print `[0, 2, 4, 6]`. One line is a decoy that doesn't belong.
lines:
  - 'def evens(limit):'
  - '    n = 0'
  - '    while n < limit:'
  - '        yield n'
  - '        n = n + 2'
  - 'print(list(evens(7)))'
distractors:
  - '        return n'
explanation: |
  `yield` hands out one value and pauses, so the loop can continue to the next even number on the next `next()`. `return n` would end the function at 0 and the generator would produce nothing more. `list()` pulls every value through until the `while` ends.
skills: [generators]
''',
)

write(
    "recall/mcq-used-once.yaml",
    '''id: mcq-used-once
type: mcq
rev: 1
prompt: |
  ```python
  g = (n * 2 for n in [1, 2, 3])
  first = list(g)
  second = list(g)
  ```

  What are `first` and `second`?
choices:
  - 'Both are `[2, 4, 6]`'
  - '`first` is `[2, 4, 6]` and `second` is `[]`'
  - '`first` is `[]` and `second` is `[2, 4, 6]`'
  - 'The second `list(g)` raises an error'
answer: 1
explanation: |
  The first `list(g)` pulls every value through the generator, which is then exhausted. The second `list(g)` asks for `next()` and gets `StopIteration` at once, so it builds an empty list; no error, just nothing. To use the values twice, keep the first list, or build a fresh generator.
skills: [single-use]
''',
)

write(
    "recall/predict-lazy-order.yaml",
    '''id: predict-lazy-order
type: predict_output
rev: 1
prompt: |
  A generator with prints inside, to show when its body runs. What does the program print, in what order?
code: |
  def steps():
      print("start")
      yield 1
      print("middle")
      yield 2


  g = steps()
  print("made")
  print(next(g))
  print(next(g))
expected_output: |
  made
  start
  1
  middle
  2
explanation: |
  Calling `steps()` runs none of its body: it just makes the generator, so `made` prints first. The first `next(g)` runs the body up to the first `yield`: `start`, then hands out `1`. The second `next(g)` resumes right after that `yield`: `middle`, then `2`. The body runs only when asked, one step at a time.
skills: [generators]
''',
)

write(
    "recall/mcq-yield-and-return.yaml",
    '''id: mcq-yield-and-return
type: mcq
rev: 1
prompt: |
  Inside a generator function, what is the difference between `yield value` and `return`?
choices:
  - 'There is none: both hand out a value and end the function'
  - '`yield` hands out a value and pauses, keeping the local variables for the next `next()`; `return` ends the generator, which raises StopIteration to the caller'
  - '`yield` is faster but `return` is clearer'
  - '`return` hands out several values at once'
answer: 1
explanation: |
  `yield` is a pause with a value: the function's state is kept, and the next `next()` carries on from the line after. `return` (or reaching the end of the body) finishes the generator, and the caller's `next()` gets `StopIteration`, which a `for` loop treats as "done".
skills: [generators, protocol]
''',
)

write(
    "recall/review-predict-generator-expression.yaml",
    '''id: review-predict-generator-expression
type: predict_output
rev: 1
prompt: |
  A generator expression summed twice, then a fresh one for `max`. What does the program print?
code: |
  numbers = [3, 8, 5]
  doubled = (n * 2 for n in numbers)
  print(sum(doubled))
  print(sum(doubled))
  print(max(n * 2 for n in numbers))
expected_output: |
  32
  0
  16
explanation: |
  The first `sum` pulls 6, 16 and 10 through the generator: `32`. The generator is then exhausted, so the second `sum` adds up nothing: `0`. The last line makes a fresh generator expression inside the call, so `max` sees all three values: `16`.
skills: [genexpr, single-use]
''',
)

write(
    "recall/review-mcq-what-for-calls.yaml",
    '''id: review-mcq-what-for-calls
type: mcq
rev: 1
prompt: |
  What does `for item in things:` do behind the scenes?
choices:
  - 'It copies `things` into a list and walks the copy by index'
  - 'It calls `iter(things)` to get an iterator, then `next()` on it for each loop, until `next()` raises `StopIteration`'
  - 'It calls `things.next()` once per item, and stops at `None`'
  - 'It only works on lists, tuples and strings'
answer: 1
explanation: |
  That protocol is why `for` works on lists, files, dicts, ranges and generators alike: anything that can hand back an iterator. The end is signalled by `StopIteration`, not by a special value, so `None` can be an item like any other.
skills: [protocol]
''',
)

write(
    "recall/review-mcq-brackets.yaml",
    '''id: review-mcq-brackets
type: mcq
rev: 1
prompt: |
  What is the difference between `[n * n for n in range(1000000)]` and `(n * n for n in range(1000000))`?
choices:
  - 'None: round brackets are just another way to write a list'
  - 'The square brackets build the whole list in memory now; the round brackets make a generator that computes each square only when asked, and can be walked once'
  - 'The round brackets make a tuple of a million squares'
  - 'The round brackets are faster because they skip every other value'
answer: 1
explanation: |
  A list comprehension does all the work up front and keeps every value. A generator expression does the work on demand, one value per `next()`, holding only the current one; pass it to `sum` or a `for` loop and memory stays flat. The price is that it's used once.
skills: [genexpr]
''',
)

# --- practice: exercises -------------------------------------------------------

write(
    "exercises/example-what-for-really-calls/exercise.yaml",
    '''id: example-what-for-really-calls
stage: worked_example
rev: 1
title: "What for really calls"
prompt: |
  This program does by hand what `for` does for you, then writes a generator and a generator expression. Press **Run**, then read how each part works.
steps:
  - label: "iter and next"
    lines: "1-3"
    note: "`iter()` turns the list into an iterator, and each `next()` hands out one item. That's the whole of what `for` does, plus catching `StopIteration` at the end."
  - label: "A generator function"
    lines: "6-13"
    note: "`countdown` has `yield` instead of `return`. Calling it makes a generator; the `for` loop calls `next()` on it, and each `next()` runs the body to the next `yield`. The local `n` survives between pauses."
  - label: "A generator expression"
    lines: "16-17"
    note: "Round brackets: no list is built. `sum` asks for the squares one at a time: 0 + 1 + 4 + 9 is 14."
  - label: "Used once"
    lines: "18"
    note: "The same generator, asked again, has nothing left: `[]`. A generator is a stream, not a container."
''',
)
write(
    "exercises/example-what-for-really-calls/solution.py",
    '''it = iter([10, 20])
print(next(it))
print(next(it))


def countdown(n):
    while n > 0:
        yield n
        n = n - 1


for value in countdown(3):
    print(value)


squares = (n * n for n in range(4))
print(sum(squares))
print(list(squares))
''',
)
write(
    "exercises/example-what-for-really-calls/test_exercise.py",
    '''from checks import run


def test_the_walkthrough():
    """Prints 10, 20, the countdown 3 2 1, then 14 and an empty list."""
    assert run() == "10\\n20\\n3\\n2\\n1\\n14\\n[]\\n"
''',
)

write(
    "exercises/fill-clean-lines/exercise.yaml",
    '''id: fill-clean-lines
stage: fill_in
rev: 1
title: "Clean lines"
prompt: |
  A generator that yields the lines of some text, stripped of spaces, skipping blank ones. Replace each `...` so the program prints:

  ```
  ['alpha', 'beta', 'gamma']
  ```

  Until every `...` is replaced, Python can't run the program at all, and shows a syntax error.
hints:
  - "Strip each line first, then test it: an empty string is false, so `if stripped:` skips blanks."
  - "A generator hands a value out with `yield`, not `return`."
skills: [generators]
''',
)
write(
    "exercises/fill-clean-lines/starter.py",
    '''text = "alpha\\n\\n  beta  \\ngamma\\n"


def clean_lines(text):
    for line in text.split("\\n"):
        stripped = line.strip()
        if ...:
            ... stripped


print(list(clean_lines(text)))
''',
)
write(
    "exercises/fill-clean-lines/solution.py",
    '''text = "alpha\\n\\n  beta  \\ngamma\\n"


def clean_lines(text):
    for line in text.split("\\n"):
        stripped = line.strip()
        if stripped:
            yield stripped


print(list(clean_lines(text)))
''',
)
write(
    "exercises/fill-clean-lines/test_exercise.py",
    '''from checks import function, run


def test_this_text():
    """Prints ['alpha', 'beta', 'gamma']."""
    printed = run()
    assert printed == "['alpha', 'beta', 'gamma']\\n", f"Your program printed:\\n{printed}"


def test_it_is_a_generator():
    """clean_lines yields one line at a time and skips blank lines."""
    clean_lines = function("clean_lines")
    lines = clean_lines("x\\n\\n\\ny")
    assert next(lines) == "x"
    assert next(lines) == "y"
''',
)
write(
    "exercises/fill-clean-lines/wrong/keeps-blanks.py",
    '''text = "alpha\\n\\n  beta  \\ngamma\\n"


def clean_lines(text):
    for line in text.split("\\n"):
        stripped = line.strip()
        if True:
            yield stripped


print(list(clean_lines(text)))
''',
)
write(
    "exercises/fill-clean-lines/wrong/typed-in.py",
    '''text = "alpha\\n\\n  beta  \\ngamma\\n"


def clean_lines(text):
    return ["alpha", "beta", "gamma"]


print(list(clean_lines(text)))
''',
)

write(
    "exercises/write-running-total/exercise.yaml",
    '''id: write-running-total
stage: write
rev: 1
title: "A running total"
prompt: |
  Write a generator `running_total(numbers)` that yields the total so far after each number. Then print the list of running totals of `[1, 2, 3, 4]`:

  ```
  [1, 3, 6, 10]
  ```
hints:
  - "Keep a `total` that starts at 0; for each number, add it, then `yield total`."
  - "`list(running_total([1, 2, 3, 4]))` pulls the values through."
skills: [generators]
''',
)
write("exercises/write-running-total/starter.py", "")
write(
    "exercises/write-running-total/solution.py",
    '''def running_total(numbers):
    total = 0
    for n in numbers:
        total = total + n
        yield total


print(list(running_total([1, 2, 3, 4])))
''',
)
write(
    "exercises/write-running-total/test_exercise.py",
    '''from checks import function, run


def test_the_output():
    """Prints [1, 3, 6, 10]."""
    printed = run()
    assert printed == "[1, 3, 6, 10]\\n", f"Your program printed:\\n{printed}"


def test_other_numbers():
    """Works for other numbers, yields one at a time, and yields nothing for an empty list."""
    running_total = function("running_total")
    assert list(running_total([5, -5, 10])) == [5, 0, 10]
    assert list(running_total([])) == []
    first = running_total([2, 3])
    assert next(first) == 2
''',
)
write(
    "exercises/write-running-total/wrong/returns-a-list.py",
    '''def running_total(numbers):
    totals = []
    total = 0
    for n in numbers:
        total = total + n
        totals.append(total)
    return totals


print(list(running_total([1, 2, 3, 4])))
''',
)
write(
    "exercises/write-running-total/wrong/typed-in.py",
    '''def running_total(numbers):
    yield 1
    yield 3
    yield 6
    yield 10


print([1, 3, 6, 10])
''',
)

# --- proof ------------------------------------------------------------------

write(
    "exercises/build-sliding-windows/exercise.yaml",
    '''id: build-sliding-windows
stage: build
rev: 1
title: "Sliding windows"
prompt: |
  Starting from a blank editor, write a generator `windows(values, size)` that yields each run of `size` consecutive values from the list, as a list, moving one step at a time: for `[1, 2, 3, 4, 5]` and size 3, that's `[1, 2, 3]`, `[2, 3, 4]`, `[3, 4, 5]`. A list shorter than `size` yields nothing. Then print the list of windows for that example:

  ```
  [[1, 2, 3], [2, 3, 4], [3, 4, 5]]
  ```

  The checks call `windows` with other lists and sizes, and take values from it one at a time.
skills: [generators, protocol]
''',
)
write("exercises/build-sliding-windows/starter.py", "")
write(
    "exercises/build-sliding-windows/solution.py",
    '''def windows(values, size):
    for start in range(len(values) - size + 1):
        yield values[start:start + size]


print(list(windows([1, 2, 3, 4, 5], 3)))
''',
)
write(
    "exercises/build-sliding-windows/test_exercise.py",
    '''from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints the three windows of size 3."""
    assert run() == "[[1, 2, 3], [2, 3, 4], [3, 4, 5]]\\n"


def test_other_sizes():
    """Size 1 gives each value alone; a list shorter than the size gives nothing."""
    windows = function("windows")
    assert list(windows([7, 8, 9], 1)) == [[7], [8], [9]]
    assert list(windows([1, 2], 3)) == []


def test_one_at_a_time():
    """windows is a generator: next() gives the first window without building the rest."""
    windows = function("windows")
    first = windows([4, 5, 6], 2)
    assert next(first) == [4, 5]
    assert next(first) == [5, 6]
''',
)
write(
    "exercises/build-sliding-windows/wrong/off-by-one.py",
    '''def windows(values, size):
    for start in range(len(values) - size):
        yield values[start:start + size]


print(list(windows([1, 2, 3, 4, 5], 3)))
''',
)
write(
    "exercises/build-sliding-windows/wrong/returns-a-list.py",
    '''def windows(values, size):
    result = []
    for start in range(len(values) - size + 1):
        result.append(values[start:start + size])
    return result


print(list(windows([1, 2, 3, 4, 5], 3)))
''',
)
write(
    "exercises/build-sliding-windows/wrong/typed-in.py",
    '''def windows(values, size):
    yield [1, 2, 3]
    yield [2, 3, 4]
    yield [3, 4, 5]


print([[1, 2, 3], [2, 3, 4], [3, 4, 5]])
''',
)

write(
    "exercises/debug-generator-mistakes/exercise.yaml",
    '''id: debug-generator-mistakes
stage: debug
rev: 1
title: "Generator mistakes"
prompt: |
  This program should print the squares of 1 to 4, then their total and their largest:

  ```
  [1, 4, 9, 16]
  30
  16
  ```

  It has two bugs. Run it, fix what you find, and run it again. One is inside the generator; the other is in how it's used.
skills: [generators, single-use]
''',
)
write(
    "exercises/debug-generator-mistakes/starter.py",
    '''def squares(limit):
    n = 1
    while n <= limit:
        return n * n
        n = n + 1


values = squares(4)
print(list(values))
print(sum(values))
print(max(values))
''',
)
write(
    "exercises/debug-generator-mistakes/solution.py",
    '''def squares(limit):
    n = 1
    while n <= limit:
        yield n * n
        n = n + 1


values = list(squares(4))
print(values)
print(sum(values))
print(max(values))
''',
)
write(
    "exercises/debug-generator-mistakes/test_exercise.py",
    '''from checks import function, run

EXPECTED = "[1, 4, 9, 16]\\n30\\n16\\n"


def test_the_output():
    """Prints the squares, their total and their largest."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\\n{EXPECTED}\\nYour program printed:\\n{printed}"


def test_squares_is_a_generator():
    """squares yields one square at a time."""
    squares = function("squares")
    g = squares(3)
    assert next(g) == 1
    assert next(g) == 4
    assert list(g) == [9]
''',
)
write(
    "exercises/debug-generator-mistakes/wrong/only-yield-fixed.py",
    '''def squares(limit):
    n = 1
    while n <= limit:
        yield n * n
        n = n + 1


values = squares(4)
print(list(values))
print(sum(values))
print(max(values, default=0))
''',
)
write(
    "exercises/debug-generator-mistakes/wrong/typed-in.py",
    '''def squares(limit):
    return [1, 4, 9, 16]


print([1, 4, 9, 16])
print(30)
print(16)
''',
)

# --- review pool: a code exercise -------------------------------------------

write(
    "exercises/review-first-squares/exercise.yaml",
    '''id: review-first-squares
stage: review_code
rev: 1
title: "The first squares"
prompt: |
  Write a generator `first_squares(count)` that yields the squares of 1, 2, 3, ... up to `count` of them, then print the list of the first four:

  ```
  [1, 4, 9, 16]
  ```
skills: [generators]
''',
)
write("exercises/review-first-squares/starter.py", "")
write(
    "exercises/review-first-squares/solution.py",
    '''def first_squares(count):
    n = 1
    while n <= count:
        yield n * n
        n = n + 1


print(list(first_squares(4)))
''',
)
write(
    "exercises/review-first-squares/test_exercise.py",
    '''from checks import function, run


def test_the_output():
    """Prints [1, 4, 9, 16]."""
    assert run() == "[1, 4, 9, 16]\\n"


def test_other_counts():
    """first_squares(0) yields nothing, and next() on first_squares(2) gives 1."""
    first_squares = function("first_squares")
    assert list(first_squares(0)) == []
    assert next(first_squares(2)) == 1
''',
)
write(
    "exercises/review-first-squares/wrong/typed-in.py",
    '''def first_squares(count):
    yield 1
    yield 4
    yield 9
    yield 16


print([1, 4, 9, 16])
''',
)

print("ml.py.iterators-and-generators written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
