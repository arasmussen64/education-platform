"""Writes the topic ml.py.functions-as-values (Module 2's fifth topic). Run
from the repository root. Files are written as bytes with LF endings."""

import pathlib

ROOT = pathlib.Path("content/topics/ml.py.functions-as-values")


def write(relative: str, text: str) -> None:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


write(
    "topic.yaml",
    '''id: ml.py.functions-as-values
kind: topic
status: ready
title: "Functions as values"
summary: "Passing functions around: sort keys, lambda, and a decorator that counts calls."
prerequisites: [ml.py.comprehensions]
estimated_minutes: 50
rev: 1
objectives:
  - "Pass a function to another function, and sort with a key."
  - "Use `lambda` where it's clearer, and name the function where it isn't."
  - "Write a decorator that wraps a function."
resources:
  - title: "The Python Tutorial: Lambda Expressions (section 4.8.6) and Sorting HOW TO, Key Functions (Python Software Foundation)"
    url: https://docs.python.org/3/howto/sorting.html#key-functions
    type: reading
    use: link
    license: PSF License Version 2
  - title: "The Python Glossary: decorator (Python Software Foundation)"
    url: https://docs.python.org/3/glossary.html#term-decorator
    type: reading
    use: link
    license: PSF License Version 2
practice:
  - example-a-function-is-a-value
  - parsons-sort-by-length
  - mcq-what-key-does
  - predict-sort-with-lambda
  - mcq-lambda-or-def
  - fill-rank-the-scores
  - write-compose
prove:
  build: build-a-counting-decorator
  debug: debug-the-wrong-key
  explain:
    prompt: |
      A teammate sees `sorted(names, key=len)` and `@timed` above a function in your code and asks what's going on. In your own words: what does it mean to pass `len` without calling it, and what does `sorted` do with it? When is a `lambda` the right thing to pass, and when should the function get a name and a `def`? And what does a decorator like `@timed` actually do to the function below it?
    rubric:
      - id: value
        required: true
        description: "A function is a value: len without parentheses is the function itself, not its result, and sorted calls it on each item to get the thing to sort by."
      - id: lambda
        required: true
        description: "lambda is for a one-expression function used once, right where it's passed (key=lambda p: p[1]); anything longer, reused or needing a docstring gets a def and a name."
      - id: decorator
        required: true
        description: "A decorator is a function that takes the function below it and returns a replacement, usually a wrapper that does something extra (timing, counting, logging) and then calls the original; @timed means f = timed(f)."
      - id: closure
        required: false
        description: "Mentions that the wrapper remembers the original function (a closure), or that *args lets it wrap functions with any parameters."
    model_answer: |
      In Python a function is a value like a number or a list: len is the function, len("abc") is a call that gives 3. Passing key=len hands sorted the function itself, and sorted calls it on each item to get the value to order by, so names come out shortest first. A lambda is a function with no name and one expression, written where it's used: key=lambda p: p[1] says "sort by the second thing in each pair" without a separate def. That's right when the function is tiny and used once. As soon as it needs two lines, a reuse, or a docstring, it should get a def and a name, because a name says what it does. A decorator is a function that takes a function and returns a replacement for it. @timed above def f is the same as f = timed(f): timed builds a wrapper that notes the time, calls the original f, prints how long it took and returns f's result, and that wrapper is what the name f refers to from then on. The wrapper remembers the original because it was created inside timed, and *args lets it wrap a function with any parameters.
review_pool:
  - review-predict-filter-and-map
  - review-mcq-decorator-meaning
  - review-predict-decorator-order
  - review-sort-by-last-letter
# What this topic teaches. Each question names the skills it tests, so a
# missed question can come back as a different one on the same skill
# (ADR-0011).
skills:
  - id: pass-functions
    description: "Pass a function to another function, and know the difference between f and f()"
  - id: key
    description: "Sort, min and max with a key function"
  - id: lambda
    description: "Use lambda where it's clearer, and name the function where it isn't"
  - id: decorators
    description: "Write a decorator that wraps a function"
''',
)

write(
    "lesson.mdx",
    '''<Intro>

In Python a function is a value: you can store it in a variable, put it in a list, and hand it to another function. That one idea is behind `sorted(..., key=...)`, behind every `@decorator` you'll see above a function, and behind how machine-learning libraries let you plug in a loss or an activation function by name.

The main resources are two short official pages: **Sorting HOW TO, Key Functions**, and the tutorial's section on **lambda expressions**; then the glossary's two paragraphs on **decorators**. About 15 minutes. Watch for:

- **`len` versus `len(x)`:** the function itself, versus a call that gives a result.
- **`key=`:** a function that `sorted`, `min` and `max` call on each item to get the thing to compare.
- **`lambda`:** a one-expression function with no name, for when a `def` would be heavier than the job.
- **A decorator** is a function that takes a function and returns a replacement.

Every piece of this is something you've already done with numbers and lists; the only new move is doing it with functions.

</Intro>

<Resource index={0} />

<Recap>

- **Functions are values.** `shout` is the function; `shout("hi")` is a call. You can pass the function: `apply(shout, "hi")` where `apply(func, text)` calls `func(text)`.
- **`key=`** gives `sorted`, `min` and `max` a function to call on each item; they compare the results. `sorted(words, key=len)` orders by length; `max(scores, key=lambda name: scores[name])` finds the name with the highest score. `reverse=True` flips the order.
- **`lambda arguments: expression`** is a nameless one-expression function, written where it's used: `key=lambda p: p[1]` sorts pairs by their second entry. If it needs two lines, a second use, or a name to be understood, write a `def`.
- **`map` and `filter`** take a function and a sequence: `map(len, words)` applies, `filter(is_even, numbers)` keeps. Both give lazy iterators; wrap in `list()` to see them. A comprehension usually reads better.
- **A decorator** is a function that takes a function and returns a wrapper. `@counted` above `def square(x):` means `square = counted(square)`: afterwards, `square` is the wrapper, which does its extra work and then calls the original. `*args` lets the wrapper accept whatever the original takes.
- **A closure** is why the wrapper remembers the original: it was created inside the decorator, and keeps the variables it saw there.
- **In machine learning:** `model.compile(loss="mse")` or `loss=my_loss` passes a function; training loops are decorated (`@torch.no_grad()`); `sorted(results, key=lambda r: r.accuracy, reverse=True)` picks the best run.

</Recap>
''',
)

# --- practice: recall --------------------------------------------------------

write(
    "recall/parsons-sort-by-length.yaml",
    '''id: parsons-sort-by-length
type: parsons
rev: 1
prompt: |
  Put the lines in order so the program sorts the words by length and prints `['ab', 'ccc', 'delta']`. One line is a decoy that doesn't belong.
lines:
  - 'words = ["delta", "ab", "ccc"]'
  - 'by_length = sorted(words, key=len)'
  - 'print(by_length)'
distractors:
  - 'by_length = sorted(words, key=len())'
explanation: |
  `key=len` passes the function `len` itself; `sorted` calls it on each word and orders by the results, 2, 3, 5. The decoy, `key=len()`, *calls* `len` with no argument, which is an error: `sorted` needs the function, not a result.
skills: [key, pass-functions]
''',
)

write(
    "recall/mcq-what-key-does.yaml",
    '''id: mcq-what-key-does
type: mcq
rev: 1
prompt: |
  What does `sorted(numbers, key=abs)` do with `numbers = [3, -7, 5]`?
choices:
  - 'Sorts the absolute values: `[3, 5, 7]`'
  - 'Sorts the numbers themselves by their absolute values: `[3, 5, -7]`'
  - 'Removes the negative numbers'
  - 'Raises an error, because `abs` was not called'
answer: 1
explanation: |
  `key` says what to **compare**, not what to return. `sorted` calls `abs` on each number to get 3, 7, 5, orders by those, and returns the original numbers in that order: `[3, 5, -7]`. Passing `abs` without parentheses is exactly right: `sorted` does the calling.
skills: [key]
''',
)

write(
    "recall/predict-sort-with-lambda.yaml",
    '''id: predict-sort-with-lambda
type: predict_output
rev: 1
prompt: |
  Pairs of name and age, sorted by age, and the youngest found. What does the program print?
code: |
  people = [("Ada", 36), ("Bob", 25), ("Cy", 31)]
  print(sorted(people, key=lambda p: p[1]))
  print(min(people, key=lambda p: p[1])[0])
expected_output: |
  [('Bob', 25), ('Cy', 31), ('Ada', 36)]
  Bob
explanation: |
  `lambda p: p[1]` is a nameless function that returns a pair's second entry, the age. `sorted` compares ages and returns the pairs youngest first; `min` returns the whole youngest pair, and `[0]` takes its name.
skills: [lambda, key]
''',
)

write(
    "recall/mcq-lambda-or-def.yaml",
    '''id: mcq-lambda-or-def
type: mcq
rev: 1
prompt: |
  Which of these should be a `def` with a name, not a `lambda`?
choices:
  - 'The key for sorting pairs by their second entry'
  - 'A function that validates a record in six steps and is called from three places'
  - 'The key for finding the longest word'
  - 'A one-off `x + 1` passed to `map`'
answer: 1
explanation: |
  `lambda` is for one expression, used once, right where it's passed. Six steps need statements, which a `lambda` can't hold; three call sites need a name to be found; and a validation rule deserves a docstring. The other three are tiny and local, which is what `lambda` is for.
skills: [lambda]
''',
)

write(
    "recall/review-predict-filter-and-map.yaml",
    '''id: review-predict-filter-and-map
type: predict_output
rev: 1
prompt: |
  `filter` and `map` with lambdas. What does the program print?
code: |
  numbers = [1, 2, 3, 4]
  print(list(filter(lambda n: n % 2 == 0, numbers)))
  print(list(map(lambda n: n * 10, [1, 2])))
expected_output: |
  [2, 4]
  [10, 20]
explanation: |
  `filter` keeps the items for which the function returns true: the even ones. `map` applies the function to each item. Both give lazy iterators, hence the `list()`. The same results as `[n for n in numbers if n % 2 == 0]` and `[n * 10 for n in [1, 2]]`, which most people find easier to read.
skills: [pass-functions, lambda]
''',
)

write(
    "recall/review-mcq-decorator-meaning.yaml",
    '''id: review-mcq-decorator-meaning
type: mcq
rev: 1
prompt: |
  What does this mean?

  ```python
  @timed
  def train():
      ...
  ```
choices:
  - '`timed` runs once, before `train` is defined'
  - '`train = timed(train)`: `timed` is given the function and returns a replacement, which the name `train` then refers to'
  - '`train` is called with `timed` as its argument'
  - '`timed` is a type hint for `train`'
answer: 1
explanation: |
  A decorator is a function applied to the function below it. `@timed` is shorthand for defining `train` and then writing `train = timed(train)`. Whatever `timed` returns, usually a wrapper that does extra work and calls the original, is what `train` means from then on.
skills: [decorators]
''',
)

write(
    "recall/review-predict-decorator-order.yaml",
    '''id: review-predict-decorator-order
type: predict_output
rev: 1
prompt: |
  A decorator that prints around the call. What does the program print, in what order?
code: |
  def loud(func):
      def wrapper(*args):
          print("calling", func.__name__)
          result = func(*args)
          print("done")
          return result

      return wrapper


  @loud
  def add(a, b):
      return a + b


  print(add(2, 3))
expected_output: |
  calling add
  done
  5
explanation: |
  `@loud` makes `add` mean the wrapper. Calling `add(2, 3)` runs the wrapper: it prints `calling add`, calls the original (which returns 5 without printing), prints `done`, and returns the 5, which the outer `print` shows last. The decorator ran once, when `add` was defined; the wrapper runs on every call.
skills: [decorators]
''',
)

# --- practice: exercises -------------------------------------------------------

write(
    "exercises/example-a-function-is-a-value/exercise.yaml",
    '''id: example-a-function-is-a-value
stage: worked_example
rev: 1
title: "A function is a value"
prompt: |
  This program passes functions around: to a function of its own, then as sort keys, then to `map`. Press **Run**, then read how each part works.
steps:
  - label: "Two functions, and one that takes a function"
    lines: "1-10"
    note: "`apply(func, text)` calls whatever function it was given. `apply(shout, \\"hello\\")` passes `shout` itself, no parentheses; `apply` adds them when it calls `func(text)`."
  - label: "Sorting by a key"
    lines: "13-14"
    note: "`key=len` tells `sorted` to compare lengths, not words; `key=abs` compares sizes while returning the original numbers. The key function is called once per item."
  - label: "map"
    lines: "16"
    note: "`map(len, words)` applies `len` to each word and gives a lazy iterator; `list()` collects it. `[len(w) for w in words]` says the same thing and is usually clearer."
''',
)
write(
    "exercises/example-a-function-is-a-value/solution.py",
    '''def shout(text):
    return text.upper() + "!"


def whisper(text):
    return text.lower() + "..."


def apply(func, text):
    return func(text)


print(apply(shout, "hello"))
print(apply(whisper, "HELLO"))
print(sorted(["pear", "fig", "banana"], key=len))
print(sorted([3, -7, 5], key=abs))
print(list(map(len, ["a", "bbb"])))
''',
)
write(
    "exercises/example-a-function-is-a-value/test_exercise.py",
    '''from checks import run


def test_the_walkthrough():
    """Prints HELLO!, hello..., the words by length, the numbers by size, then [1, 3]."""
    assert run() == "HELLO!\\nhello...\\n['fig', 'pear', 'banana']\\n[3, 5, -7]\\n[1, 3]\\n"
''',
)

write(
    "exercises/fill-rank-the-scores/exercise.yaml",
    '''id: fill-rank-the-scores
stage: fill_in
rev: 1
title: "Rank the scores"
prompt: |
  Replace each `...` so the program lists the names from highest score to lowest, then prints the top scorer:

  ```
  ['Bob', 'Cy', 'Ada']
  Bob
  ```

  Until every `...` is replaced, Python can't run the program at all, and shows a syntax error.
hints:
  - "Sorting the dict gives its keys, the names; the key function should turn a name into its score: `scores[name]`."
  - "`reverse=True` puts the highest first; `max` with the same key finds the top scorer."
skills: [key, lambda]
''',
)
write(
    "exercises/fill-rank-the-scores/starter.py",
    '''scores = {"Ada": 72, "Bob": 91, "Cy": 85}
ranked = sorted(scores, key=lambda name: ..., reverse=...)
print(ranked)
print(max(scores, key=lambda name: ...))
''',
)
write(
    "exercises/fill-rank-the-scores/solution.py",
    '''scores = {"Ada": 72, "Bob": 91, "Cy": 85}
ranked = sorted(scores, key=lambda name: scores[name], reverse=True)
print(ranked)
print(max(scores, key=lambda name: scores[name]))
''',
)
write(
    "exercises/fill-rank-the-scores/test_exercise.py",
    '''from checks import run, run_with


def test_these_scores():
    """Prints ['Bob', 'Cy', 'Ada'], then Bob."""
    printed = run()
    assert printed == "['Bob', 'Cy', 'Ada']\\nBob\\n", f"Your program printed:\\n{printed}"


def test_other_scores():
    """Works for other scores."""
    printed = run_with({"scores": {"Dee": 50, "Eve": 99, "Fay": 75}})
    assert printed == "['Eve', 'Fay', 'Dee']\\nEve\\n", f"With Dee 50, Eve 99, Fay 75 it should rank Eve, Fay, Dee. It printed:\\n{printed}"
''',
)
write(
    "exercises/fill-rank-the-scores/wrong/lowest-first.py",
    '''scores = {"Ada": 72, "Bob": 91, "Cy": 85}
ranked = sorted(scores, key=lambda name: scores[name], reverse=False)
print(ranked)
print(max(scores, key=lambda name: scores[name]))
''',
)
write(
    "exercises/fill-rank-the-scores/wrong/typed-in.py",
    '''scores = {"Ada": 72, "Bob": 91, "Cy": 85}
ranked = ["Bob", "Cy", "Ada"]
print(ranked)
print("Bob")
''',
)

write(
    "exercises/write-compose/exercise.yaml",
    '''id: write-compose
stage: write
rev: 1
title: "Compose two functions"
prompt: |
  Write a function `compose(f, g)` that returns a **new function** which, given `x`, returns `f(g(x))`. Then, with `increment` adding 1 and `double` multiplying by 2, print `compose(increment, double)(5)` and `compose(double, increment)(5)`:

  ```
  11
  12
  ```
hints:
  - "Define the new function inside `compose`: `def both(x): return f(g(x))`, then `return both` (no parentheses: return the function itself)."
  - "`increment` and `double` can be `def`s or lambdas: `increment = lambda x: x + 1`."
  - "`compose(increment, double)(5)` is double first (10), then increment (11)."
skills: [pass-functions, lambda]
''',
)
write("exercises/write-compose/starter.py", "")
write(
    "exercises/write-compose/solution.py",
    '''def compose(f, g):
    def both(x):
        return f(g(x))

    return both


def increment(x):
    return x + 1


def double(x):
    return x * 2


print(compose(increment, double)(5))
print(compose(double, increment)(5))
''',
)
write(
    "exercises/write-compose/test_exercise.py",
    '''from checks import function, run


def test_the_output():
    """Prints 11, then 12."""
    printed = run()
    assert printed == "11\\n12\\n", f"Your program printed:\\n{printed}"


def test_compose_returns_a_function():
    """compose(f, g) is a function that applies g first, then f, for any f and g."""
    compose = function("compose")
    square_then_negate = compose(lambda x: -x, lambda x: x * x)
    assert callable(square_then_negate)
    assert square_then_negate(3) == -9
    assert compose(str, abs)(-4) == "4"
''',
)
write(
    "exercises/write-compose/wrong/calls-instead-of-returning.py",
    '''def compose(f, g):
    def both(x):
        return f(g(x))

    return both(5)


def increment(x):
    return x + 1


def double(x):
    return x * 2


print(compose(increment, double))
print(compose(double, increment))
''',
)
write(
    "exercises/write-compose/wrong/typed-in.py",
    '''def compose(f, g):
    return f


print(11)
print(12)
''',
)

# --- proof ------------------------------------------------------------------

write(
    "exercises/build-a-counting-decorator/exercise.yaml",
    '''id: build-a-counting-decorator
stage: build
rev: 1
title: "A counting decorator"
prompt: |
  Starting from a blank editor, write a decorator `counted(func)` that returns a wrapper which counts how many times the function has been called. The wrapper takes any arguments (`*args`), adds one to a `count` attribute it keeps on itself (`wrapper.count`, starting at 0), calls the original with the same arguments, and returns its result.

  Then decorate a function `square(x)` with it, call `square(3)` and `square(4)`, and print both results and the count:

  ```
  9
  16
  2
  ```

  The checks decorate their own functions, with other numbers of arguments.
skills: [decorators, pass-functions]
''',
)
write("exercises/build-a-counting-decorator/starter.py", "")
write(
    "exercises/build-a-counting-decorator/solution.py",
    '''def counted(func):
    def wrapper(*args):
        wrapper.count = wrapper.count + 1
        return func(*args)

    wrapper.count = 0
    return wrapper


@counted
def square(x):
    return x * x


print(square(3))
print(square(4))
print(square.count)
''',
)
write(
    "exercises/build-a-counting-decorator/test_exercise.py",
    '''from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints 9, 16, then 2."""
    assert run() == "9\\n16\\n2\\n"


def test_counts_any_function():
    """counted wraps a two-argument function, returns its results, and counts from 0."""
    counted = function("counted")

    def add(a, b):
        return a + b

    add = counted(add)
    assert add.count == 0
    assert add(2, 3) == 5
    assert add(10, 5) == 15
    assert add.count == 2


def test_each_decorated_function_has_its_own_count():
    """Two decorated functions keep separate counts."""
    counted = function("counted")
    first = counted(lambda: "a")
    second = counted(lambda: "b")
    first()
    first()
    assert first.count == 2
    assert second.count == 0
''',
)
write(
    "exercises/build-a-counting-decorator/wrong/shared-count.py",
    '''calls = 0


def counted(func):
    def wrapper(*args):
        global calls
        calls = calls + 1
        wrapper.count = calls
        return func(*args)

    wrapper.count = 0
    return wrapper


@counted
def square(x):
    return x * x


print(square(3))
print(square(4))
print(square.count)
''',
)
write(
    "exercises/build-a-counting-decorator/wrong/forgets-to-return-result.py",
    '''def counted(func):
    def wrapper(*args):
        wrapper.count = wrapper.count + 1
        func(*args)

    wrapper.count = 0
    return wrapper


@counted
def square(x):
    return x * x


print(9)
print(16)
print(square.count + 2)
''',
)
write(
    "exercises/build-a-counting-decorator/wrong/typed-in.py",
    '''def counted(func):
    func.count = 2
    return func


@counted
def square(x):
    return x * x


print(9)
print(16)
print(2)
''',
)

write(
    "exercises/debug-the-wrong-key/exercise.yaml",
    '''id: debug-the-wrong-key
stage: debug
rev: 1
title: "The wrong key"
prompt: |
  This program should list some products cheapest first, then name the most expensive:

  ```
  [('tea', 2.5), ('cake', 4.0), ('jam', 6.5)]
  jam
  ```

  It has two bugs. Run it, fix what you find, and run it again. Both are in what the key functions return.
skills: [key, lambda]
''',
)
write(
    "exercises/debug-the-wrong-key/starter.py",
    '''products = [("cake", 4.0), ("jam", 6.5), ("tea", 2.5)]
cheapest_first = sorted(products, key=lambda p: p[0])
print(cheapest_first)
priciest = max(products, key=lambda p: p)
print(priciest[0])
''',
)
write(
    "exercises/debug-the-wrong-key/solution.py",
    '''products = [("cake", 4.0), ("jam", 6.5), ("tea", 2.5)]
cheapest_first = sorted(products, key=lambda p: p[1])
print(cheapest_first)
priciest = max(products, key=lambda p: p[1])
print(priciest[0])
''',
)
write(
    "exercises/debug-the-wrong-key/test_exercise.py",
    '''from checks import run, run_with

EXPECTED = "[('tea', 2.5), ('cake', 4.0), ('jam', 6.5)]\\njam\\n"


def test_the_output():
    """Prints the products cheapest first, then jam."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\\n{EXPECTED}\\nYour program printed:\\n{printed}"


def test_other_products():
    """Works when the alphabetical order and the price order disagree."""
    printed = run_with({"products": [("zebra", 1.0), ("apple", 9.0), ("mango", 3.0)]})
    assert printed == "[('zebra', 1.0), ('mango', 3.0), ('apple', 9.0)]\\napple\\n", (
        f"It should sort by price, not by name. It printed:\\n{printed}"
    )
''',
)
write(
    "exercises/debug-the-wrong-key/wrong/only-sort-fixed.py",
    '''products = [("cake", 4.0), ("jam", 6.5), ("tea", 2.5)]
cheapest_first = sorted(products, key=lambda p: p[1])
print(cheapest_first)
priciest = max(products, key=lambda p: p)
print(priciest[0])
''',
)
write(
    "exercises/debug-the-wrong-key/wrong/typed-in.py",
    '''products = [("cake", 4.0), ("jam", 6.5), ("tea", 2.5)]
print([('tea', 2.5), ('cake', 4.0), ('jam', 6.5)])
print("jam")
''',
)

# --- review pool: a code exercise -------------------------------------------

write(
    "exercises/review-sort-by-last-letter/exercise.yaml",
    '''id: review-sort-by-last-letter
stage: review_code
rev: 1
title: "Sort by the last letter"
prompt: |
  Starting from `words = ["banana", "cherry", "fig"]`, print the words sorted by their **last** letter, using a key function:

  ```
  ['banana', 'fig', 'cherry']
  ```

  Keep the starting line: the checks run your program with other words too.
skills: [key, lambda]
''',
)
write("exercises/review-sort-by-last-letter/starter.py", 'words = ["banana", "cherry", "fig"]\n')
write(
    "exercises/review-sort-by-last-letter/solution.py",
    '''words = ["banana", "cherry", "fig"]
print(sorted(words, key=lambda word: word[-1]))
''',
)
write(
    "exercises/review-sort-by-last-letter/test_exercise.py",
    '''from checks import run, run_with


def test_these_words():
    """Prints ['banana', 'fig', 'cherry']: a, g, y."""
    assert run() == "['banana', 'fig', 'cherry']\\n"


def test_other_words():
    """Sorts by last letter, not first: ['axe', 'bob', 'cat'] gives bob, axe, cat."""
    assert run_with({"words": ["axe", "bob", "cat"]}) == "['bob', 'axe', 'cat']\\n"
''',
)
write(
    "exercises/review-sort-by-last-letter/wrong/first-letter.py",
    '''words = ["banana", "cherry", "fig"]
print(sorted(words, key=lambda word: word[0]))
''',
)
write(
    "exercises/review-sort-by-last-letter/wrong/typed-in.py",
    '''words = ["banana", "cherry", "fig"]
print(['banana', 'fig', 'cherry'])
''',
)

print("ml.py.functions-as-values written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
