"""Writes the topic ml.py.writing-tests (Module 2's sixth topic). The
exercises grade the learner's tests by running them against planted bugs:
a test that doesn't catch the bug doesn't count. Run from the repository
root. Files are written as bytes with LF endings."""

import pathlib

ROOT = pathlib.Path("content/topics/ml.py.writing-tests")


def write(relative: str, text: str) -> None:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


# Shared by the hidden tests: load the learner's module quietly, find their
# test functions, and see whether they catch a planted bug.
GRADER = '''import importlib
import io
import sys
from contextlib import redirect_stdout


def load_solution():
    """The learner's module, imported fresh, with its prints swallowed."""
    sys.modules.pop("solution", None)
    importlib.invalidate_caches()
    with redirect_stdout(io.StringIO()):
        return importlib.import_module("solution")


def learner_tests(module):
    return [getattr(module, name) for name in dir(module) if name.startswith("test_")]


def all_pass(module):
    for test in learner_tests(module):
        test()


def catches(module, name, bug):
    """Whether any of the learner's tests fails once `name` is replaced by `bug`."""
    if not callable(getattr(module, name, None)):
        raise AssertionError(f"Define a function called {name}.")
    original = getattr(module, name)
    setattr(module, name, bug)
    try:
        for test in learner_tests(module):
            try:
                test()
            except Exception:
                return True
        return False
    finally:
        setattr(module, name, original)
'''

RUNNER = '''
passed = 0
for name in sorted(dir()):
    if name.startswith("test_"):
        globals()[name]()
        passed = passed + 1
print(passed, "passed")
'''

write(
    "topic.yaml",
    '''id: ml.py.writing-tests
kind: topic
status: ready
title: "Writing tests"
summary: "Tests for a function, its edge cases, and what a test proves and can't."
prerequisites: [py.m6.checkpoint]
estimated_minutes: 50
rev: 1
objectives:
  - "Write pytest-style tests for a function, including its edge cases."
  - "Share set-up between tests with a helper, and say what a pytest fixture is for."
  - "Say what a test proves and what it can't."
resources:
  - title: "pytest documentation: Get Started (the pytest developers)"
    url: https://docs.pytest.org/en/stable/getting-started.html
    type: reading
    use: link
    license: MIT (linked, not copied)
  - title: "The Python Tutorial: the assert statement, in Simple statements (Python Software Foundation)"
    url: https://docs.python.org/3/reference/simple_stmts.html#the-assert-statement
    type: reading
    use: link
    license: PSF License Version 2
practice:
  - example-tests-for-a-leap-year
  - parsons-arrange-act-assert
  - mcq-what-a-test-proves
  - predict-assert-message
  - mcq-which-is-the-edge-case
  - fill-tests-for-clamp
  - write-tests-for-median
prove:
  build: build-word-count-with-tests
  debug: debug-tests-that-dont-test
  explain:
    prompt: |
      A teammate says: "All 40 tests pass, so the function has no bugs." Another says: "I don't write tests for the empty list; nobody passes an empty list." In your own words: what does a passing test prove, and what can't it prove? Why do the edge cases (empty, one item, the boundary values) deserve their own tests? And when three tests all start with the same five lines of set-up, what should you do about it, and what does pytest call its version of that?
    rubric:
      - id: proves
        required: true
        description: "A passing test proves the function behaved correctly for that one case; it can't prove there are no bugs, only that the tested cases work."
      - id: edges
        required: true
        description: "Edge cases are where bugs hide (off-by-one, empty input, a boundary included or not), and 'nobody passes that' is exactly how it reaches production untested."
      - id: setup
        required: true
        description: "Repeated set-up belongs in a helper function the tests call, or in a pytest fixture: a function that builds the thing and is handed to each test that names it as a parameter."
      - id: spec
        required: false
        description: "Mentions that a good test reads as a sentence about the behaviour, or that tests are a specification you can run."
    model_answer: |
      A passing test proves one thing: for the inputs that test used, the function gave the expected result. Forty passing tests prove forty cases; they say nothing about the cases nobody wrote down. So "no bugs" doesn't follow, only "none of these forty bugs". Edge cases are where the bugs actually live: an empty list that makes a division by zero, a single item that breaks a "middle two" median, a boundary value that the code excludes with < where it meant <=. "Nobody passes an empty list" is a prediction about users, and the day it's wrong the failure is in production instead of in the test run. When several tests share the same set-up, put it in a helper function the tests call, so a change to the set-up happens once; pytest's version is a fixture, a function marked @pytest.fixture that builds the thing, and any test that names it as a parameter gets a fresh one. Either way, each test still reads as one sentence about one behaviour.
review_pool:
  - review-predict-which-fails
  - review-mcq-test-names
  - review-tests-for-clamp-boundaries
# What this topic teaches. Each question names the skills it tests, so a
# missed question can come back as a different one on the same skill
# (ADR-0011).
skills:
  - id: write-tests
    description: "Write a test function: arrange, act, assert, with a name that says what it checks"
  - id: edge-cases
    description: "Test the edge cases: empty, one, the boundaries"
  - id: assert
    description: "Read and write assert, with a message that says what went wrong"
  - id: meaning
    description: "Say what a test proves and what it can't"
''',
)

write(
    "lesson.mdx",
    '''<Intro>

Every Check you've passed on this platform was a test someone wrote: a function named `test_…` with an `assert` inside, run by pytest-style tooling. Now you write them. A test is a sentence about a behaviour that a computer can check for you, every time, forever, and the moment you have a few you can change code without fear.

The main resource is pytest's **Get Started** page, as far as the first example and its output. About 10 minutes. Then the two paragraphs on `assert` in the language reference. Watch for:

- **A test is a function named `test_…`** containing `assert`s. Any `assert` that fails makes the test fail; a test that runs to the end passes.
- **Arrange, act, assert:** set things up, do the thing, check the result.
- **The assert message** (`assert x == 3, "why"`) is what you read when it fails.

The platform runs your tests with its own small runner rather than pytest itself, so in this topic the programs end with a loop that calls every `test_…` function and prints how many passed. The tests themselves are exactly what pytest would run.

</Intro>

<Resource index={0} />

<Recap>

- **A test** is a function named `test_something` with `assert`s inside. pytest finds every such function in files named `test_*.py` and runs them; here a small loop at the bottom of the program does the same.
- **Arrange, act, assert.** Set up the inputs, call the function once, check the result. One behaviour per test, named so the test's name is a sentence: `test_centuries_are_not_leap`.
- **`assert condition, message`.** When the condition is false, the test fails with the message. Write the message for the person who'll read the failure: what was expected, and from what.
- **Edge cases are the point.** The empty list, a single item, the boundary values (is 10 inside `0..10`?), negative numbers, repeated items. Bugs live there; the happy path is where the author already looked.
- **What a passing test proves:** that the function worked for that case. **What it can't:** that there are no bugs. More cases, better cases, more confidence; never certainty.
- **Shared set-up** goes in a helper the tests call. pytest's version is a **fixture**: a function decorated with `@pytest.fixture` that builds the thing; a test that names it as a parameter gets a fresh one each time.
- **Tests as a specification.** A good test file reads like a list of promises the function keeps. When a bug is found, the first thing to write is the test that would have caught it.
- **In machine learning:** tests for data cleaning, for feature code and for the shapes that flow through a model catch the mistakes that otherwise show up as a slightly worse accuracy nobody can explain.

</Recap>
''',
)

# --- practice: recall --------------------------------------------------------

write(
    "recall/parsons-arrange-act-assert.yaml",
    '''id: parsons-arrange-act-assert
type: parsons
rev: 1
prompt: |
  Put the lines in order to write one test (arrange, act, assert), run it, and print `passed`. One line is a decoy that doesn't belong.
lines:
  - 'def test_total_of_two_items():'
  - '    cart = [2.5, 4.0]'
  - '    total = sum(cart)'
  - '    assert total == 6.5'
  - 'test_total_of_two_items()'
  - 'print("passed")'
distractors:
  - '    assert total = 6.5'
explanation: |
  Arrange (`cart`), act (`sum`), assert (`== 6.5`): three lines, one behaviour. The decoy uses a single `=`, which is an assignment and isn't valid inside `assert`; a comparison needs `==`. The test is a function, so it runs only when called.
skills: [write-tests, assert]
''',
)

write(
    "recall/mcq-what-a-test-proves.yaml",
    '''id: mcq-what-a-test-proves
type: mcq
rev: 1
prompt: |
  All of a function's tests pass. What do you know?
choices:
  - 'The function has no bugs'
  - 'The function behaves as the tests expect for the cases they cover, and nothing about the cases they don’t'
  - 'The function is fast enough'
  - 'The tests are well written'
answer: 1
explanation: |
  A test checks one case. Passing tests prove those cases work; they can't speak for the inputs nobody tested, which is where bugs usually are. That's why the edge cases get their own tests, and why "all tests pass" is a good sign, not a guarantee.
skills: [meaning]
''',
)

write(
    "recall/predict-assert-message.yaml",
    '''id: predict-assert-message
type: predict_output
rev: 1
prompt: |
  Two asserts, one of them wrong about what `clamp` should do. What does the program print?
code: |
  def clamp(value, low, high):
      return max(low, min(value, high))


  try:
      assert clamp(15, 0, 10) == 10
      assert clamp(-3, 0, 10) == 1, "below the range should give the low end"
      print("all passed")
  except AssertionError as error:
      print("failed:", error)
expected_output: |
  failed: below the range should give the low end
explanation: |
  The first assert holds: 15 clamped to 0..10 is 10. The second expects 1, but clamping -3 gives the low end, 0, so the assert fails and raises `AssertionError` carrying its message. The `except` prints it. (The test was wrong, not the function: that happens, and the message is what tells you which.)
skills: [assert]
''',
)

write(
    "recall/mcq-which-is-the-edge-case.yaml",
    '''id: mcq-which-is-the-edge-case
type: mcq
rev: 1
prompt: |
  You're testing `median(values)`. Which input is the one most likely to find a bug that the others wouldn't?
choices:
  - '`[3, 1, 2]`'
  - '`[10, 20, 30, 40, 50]`'
  - '`[4, 1, 3, 2]`, an even count'
  - '`[1, 2, 3]`'
answer: 2
explanation: |
  Three of these are odd-length lists with a clear middle; a correct-looking `median` that only handles the odd case passes all of them. The even count has no single middle, so it needs "the mean of the middle two", which is the branch most often missing or wrong. (`[3, 1, 2]` is a good test too: it catches a median that forgets to sort.)
skills: [edge-cases]
''',
)

write(
    "recall/review-predict-which-fails.yaml",
    '''id: review-predict-which-fails
type: predict_output
rev: 1
prompt: |
  Three tests of a `word_count` function, run by a loop that reports each one. Which fail, and what does the program print?
code: |
  def word_count(text):
      return len(text.split())


  def test_three_words():
      assert word_count("a b c") == 3


  def test_empty_text():
      assert word_count("") == 0


  def test_extra_spaces():
      assert word_count("a  b") == 3


  for name in ["test_three_words", "test_empty_text", "test_extra_spaces"]:
      try:
          globals()[name]()
          print(name, "passed")
      except AssertionError:
          print(name, "failed")
expected_output: |
  test_three_words passed
  test_empty_text passed
  test_extra_spaces failed
explanation: |
  `split()` with no argument splits on any run of whitespace, so `"a  b"` is two words, not three: the third test's expectation is wrong, and it fails. The empty string splits into no words, so `0` is right. A failing test means either the function or the test is wrong; here it's the test, and the fix is to expect 2.
skills: [assert, meaning]
''',
)

write(
    "recall/review-mcq-test-names.yaml",
    '''id: review-mcq-test-names
type: mcq
rev: 1
prompt: |
  Which of these functions would pytest (and this topic's runner) actually run as a test?
choices:
  - '`def check_empty_list():`'
  - '`def test_empty_list():`'
  - '`def empty_list_test():`'
  - '`def TestEmptyList():`'
answer: 1
explanation: |
  Tests are found by name: a function whose name **starts with** `test_` (in a file named `test_*.py`, for pytest). A function called `check_…` or `…_test` is never collected, so it passes by never running, which is the quietest way a test can be broken.
skills: [write-tests]
''',
)

# --- practice: exercises -------------------------------------------------------

write(
    "exercises/example-tests-for-a-leap-year/exercise.yaml",
    '''id: example-tests-for-a-leap-year
stage: worked_example
rev: 1
title: "Tests for a leap year"
prompt: |
  This program defines `is_leap` and three tests for it, then runs the tests. Press **Run**, then read how each part works.
steps:
  - label: "The function under test"
    lines: "1-2"
    note: "A year is a leap year if it's divisible by 4, except centuries, except every fourth century. Three rules, so at least three tests."
  - label: "One behaviour per test"
    lines: "5-15"
    note: "Each test is a function named `test_…` whose name is a sentence about one rule. Inside, `assert` checks a concrete case: 2024 is, 2023 isn't; 1900 isn't; 2000 is. An `assert` that fails raises `AssertionError`, which fails the test."
  - label: "A small runner"
    lines: "18-23"
    note: "pytest would find and run these for you. Here a loop finds every name starting with `test_`, calls it, and counts. Running `test_…` functions by name is exactly what pytest does."
''',
)
write(
    "exercises/example-tests-for-a-leap-year/solution.py",
    '''def is_leap(year):
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def test_every_fourth_year_is_leap():
    assert is_leap(2024)
    assert not is_leap(2023)


def test_centuries_are_not_leap():
    assert not is_leap(1900)


def test_every_fourth_century_is_leap():
    assert is_leap(2000)


passed = 0
for name in sorted(dir()):
    if name.startswith("test_"):
        globals()[name]()
        passed = passed + 1
        print(name, "passed")
print(passed, "passed")
''',
)
write(
    "exercises/example-tests-for-a-leap-year/test_exercise.py",
    '''from checks import run


def test_three_tests_pass():
    """Prints each test's name as it passes, then 3 passed."""
    assert run() == (
        "test_centuries_are_not_leap passed\\n"
        "test_every_fourth_century_is_leap passed\\n"
        "test_every_fourth_year_is_leap passed\\n3 passed\\n"
    )
''',
)

write(
    "exercises/fill-tests-for-clamp/exercise.yaml",
    '''id: fill-tests-for-clamp
stage: fill_in
rev: 1
title: "Tests for clamp"
prompt: |
  `clamp(value, low, high)` keeps a value inside a range. Replace each `...` with the value each test should expect, so that all three tests pass and the program prints:

  ```
  3 passed
  ```

  Until every `...` is replaced, Python can't run the program at all, and shows a syntax error.
hints:
  - "A value already inside the range comes back unchanged."
  - "A value above the range becomes the high end; below it, the low end."
skills: [write-tests, edge-cases]
''',
)
write(
    "exercises/fill-tests-for-clamp/starter.py",
    '''def clamp(value, low, high):
    return max(low, min(value, high))


def test_inside_the_range_is_unchanged():
    assert clamp(5, 0, 10) == ...


def test_above_the_range_becomes_the_high_end():
    assert clamp(15, 0, 10) == ...


def test_below_the_range_becomes_the_low_end():
    assert clamp(-3, 0, 10) == ...
''' + RUNNER,
)
write(
    "exercises/fill-tests-for-clamp/solution.py",
    '''def clamp(value, low, high):
    return max(low, min(value, high))


def test_inside_the_range_is_unchanged():
    assert clamp(5, 0, 10) == 5


def test_above_the_range_becomes_the_high_end():
    assert clamp(15, 0, 10) == 10


def test_below_the_range_becomes_the_low_end():
    assert clamp(-3, 0, 10) == 0
''' + RUNNER,
)
write(
    "exercises/fill-tests-for-clamp/test_exercise.py",
    GRADER + '''
from checks import run


def test_all_three_pass():
    """Prints 3 passed."""
    printed = run()
    assert printed == "3 passed\\n", f"Your program printed:\\n{printed}"


def test_the_tests_catch_a_broken_clamp():
    """The tests fail for a clamp that ignores the low end."""
    module = load_solution()
    assert catches(module, "clamp", lambda value, low, high: min(value, high)), (
        "A clamp that never applies the low end should fail at least one test."
    )
''',
)
write(
    "exercises/fill-tests-for-clamp/wrong/expects-the-input-back.py",
    '''def clamp(value, low, high):
    return max(low, min(value, high))


def test_inside_the_range_is_unchanged():
    assert clamp(5, 0, 10) == 5


def test_above_the_range_becomes_the_high_end():
    assert clamp(15, 0, 10) == 10


def test_below_the_range_becomes_the_low_end():
    assert clamp(-3, 0, 10) == -3
''' + RUNNER,
)
write(
    "exercises/fill-tests-for-clamp/wrong/typed-in.py",
    '''def clamp(value, low, high):
    return max(low, min(value, high))


def test_inside_the_range_is_unchanged():
    assert True


def test_above_the_range_becomes_the_high_end():
    assert True


def test_below_the_range_becomes_the_low_end():
    assert True
''' + RUNNER,
)

write(
    "exercises/write-tests-for-median/exercise.yaml",
    '''id: write-tests-for-median
stage: write
rev: 1
title: "Tests for median"
prompt: |
  The starter has a correct `median`. Write at least two tests for it: one with an **odd** count of values given out of order (so a median that forgets to sort would fail), and one with an **even** count (so a median that only handles the odd case would fail). Keep the runner at the bottom; the program should print how many tests passed:

  ```
  2 passed
  ```

  The checks run your tests against the real `median`, and then against two broken ones, to see that they catch them.
hints:
  - "A test is a function named `test_…` with an `assert` inside: `assert median([3, 1, 2]) == 2`."
  - "For an even count the median is the mean of the two middle values: `median([4, 1, 3, 2])` is 2.5."
  - "Give each test a name that says what it checks."
skills: [write-tests, edge-cases]
''',
)
MEDIAN = '''def median(values):
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2 == 1:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2
'''
write("exercises/write-tests-for-median/starter.py", MEDIAN + "\n\n# Your tests go here.\n" + RUNNER)
write(
    "exercises/write-tests-for-median/solution.py",
    MEDIAN + '''

def test_odd_count_out_of_order():
    assert median([3, 1, 2]) == 2


def test_even_count_takes_the_middle_two():
    assert median([4, 1, 3, 2]) == 2.5
''' + RUNNER,
)
write(
    "exercises/write-tests-for-median/test_exercise.py",
    GRADER + '''
from checks import run


def test_at_least_two_tests_pass():
    """Prints how many tests passed: at least 2, all of them passing against the real median."""
    printed = run().strip()
    assert printed.endswith("passed"), f"The program should end by printing how many tests passed. It printed:\\n{printed}"
    count = int(printed.split()[-2])
    assert count >= 2, f"Write at least two tests; {count} ran."
    all_pass(load_solution())


def test_catches_a_median_that_forgets_to_sort():
    """At least one test fails for a median that doesn't sort first."""
    module = load_solution()

    def unsorted_median(values):
        middle = len(values) // 2
        if len(values) % 2 == 1:
            return values[middle]
        return (values[middle - 1] + values[middle]) / 2

    assert catches(module, "median", unsorted_median), (
        "Use an odd count of values given out of order, like [3, 1, 2]."
    )


def test_catches_a_median_that_only_handles_odd_counts():
    """At least one test fails for a median that ignores even counts."""
    module = load_solution()

    def odd_only_median(values):
        return sorted(values)[len(values) // 2]

    assert catches(module, "median", odd_only_median), (
        "Use an even count of values, like [4, 1, 3, 2], whose median is 2.5."
    )
''',
)
write(
    "exercises/write-tests-for-median/wrong/only-sorted-odd-inputs.py",
    MEDIAN + '''

def test_three_values():
    assert median([1, 2, 3]) == 2


def test_five_values():
    assert median([1, 2, 3, 4, 5]) == 3
''' + RUNNER,
)
write(
    "exercises/write-tests-for-median/wrong/typed-in.py",
    MEDIAN + '''

def test_one():
    assert True


def test_two():
    assert True
''' + RUNNER,
)

# --- proof ------------------------------------------------------------------

write(
    "exercises/build-word-count-with-tests/exercise.yaml",
    '''id: build-word-count-with-tests
stage: build
rev: 1
title: "Word count, with tests"
prompt: |
  Starting from a blank editor, write `word_count(text)`, which returns a dict from each word to how many times it appears: split on whitespace, and treat words as the same regardless of case (`"The"` and `"the"` are one word, counted under `"the"`). Then write **at least three tests** for it, covering mixed case, a repeated word, and the empty string (which gives an empty dict). End the program with a runner that calls every function whose name starts with `test_` and prints how many passed, like `3 passed`.

  The checks call `word_count` with their own texts, run your tests, and then run them again against broken versions of `word_count` to see that your tests catch them.
skills: [write-tests, edge-cases, assert]
''',
)
write("exercises/build-word-count-with-tests/starter.py", "")
WORD_COUNT = '''def word_count(text):
    counts = {}
    for word in text.lower().split():
        counts[word] = counts.get(word, 0) + 1
    return counts
'''
write(
    "exercises/build-word-count-with-tests/solution.py",
    WORD_COUNT + '''

def test_mixed_case_counts_as_one_word():
    assert word_count("the cat and The dog") == {"the": 2, "cat": 1, "and": 1, "dog": 1}


def test_a_repeated_word_is_counted():
    assert word_count("a a a") == {"a": 3}


def test_empty_text_gives_an_empty_dict():
    assert word_count("") == {}
''' + RUNNER,
)
write(
    "exercises/build-word-count-with-tests/test_exercise.py",
    GRADER + '''
from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_word_count():
    """word_count lowercases, splits on any whitespace, and counts repeats."""
    word_count = function("word_count")
    assert word_count("the cat and The dog") == {"the": 2, "cat": 1, "and": 1, "dog": 1}
    assert word_count("a  a\\na") == {"a": 3}
    assert word_count("") == {}


def test_three_tests_pass():
    """The program ends with at least three passing tests."""
    printed = run().strip()
    assert printed.endswith("passed")
    assert int(printed.split()[-2]) >= 3
    all_pass(load_solution())


def test_the_tests_catch_broken_versions():
    """The tests fail for a word_count that keeps case, and for one that counts each word once."""
    module = load_solution()

    def keeps_case(text):
        counts = {}
        for word in text.split():
            counts[word] = counts.get(word, 0) + 1
        return counts

    def counts_once(text):
        return {word: 1 for word in text.lower().split()}

    assert catches(module, "word_count", keeps_case)
    assert catches(module, "word_count", counts_once)
''',
)
write(
    "exercises/build-word-count-with-tests/wrong/tests-miss-the-case-rule.py",
    WORD_COUNT + '''

def test_counts_words():
    assert word_count("a b a") == {"a": 2, "b": 1}


def test_a_repeated_word_is_counted():
    assert word_count("a a a") == {"a": 3}


def test_empty_text_gives_an_empty_dict():
    assert word_count("") == {}
''' + RUNNER,
)
write(
    "exercises/build-word-count-with-tests/wrong/keeps-case.py",
    '''def word_count(text):
    counts = {}
    for word in text.split():
        counts[word] = counts.get(word, 0) + 1
    return counts


def test_counts_words():
    assert word_count("a b a") == {"a": 2, "b": 1}


def test_a_repeated_word_is_counted():
    assert word_count("a a a") == {"a": 3}


def test_empty_text_gives_an_empty_dict():
    assert word_count("") == {}
''' + RUNNER,
)
write(
    "exercises/build-word-count-with-tests/wrong/typed-in.py",
    WORD_COUNT + '''

def test_one():
    assert True


def test_two():
    assert True


def test_three():
    assert True


print("3 passed")
''',
)

write(
    "exercises/debug-tests-that-dont-test/exercise.yaml",
    '''id: debug-tests-that-dont-test
stage: debug
rev: 1
title: "Tests that don't test"
prompt: |
  This program has a correct `add` and three tests for it, and should print:

  ```
  3 passed
  ```

  It has two bugs, both in the tests. Run it, read what happens, fix it, and run again. One test is wrong about the answer; one test is never run at all. Fix the tests; don't delete them.
skills: [write-tests, assert]
''',
)
write(
    "exercises/debug-tests-that-dont-test/starter.py",
    '''def add(a, b):
    return a + b


def test_two_positive_numbers():
    assert add(2, 3) == 6


def test_zero_changes_nothing():
    assert add(7, 0) == 7


def check_negative_numbers():
    assert add(-2, -3) == -5
''' + RUNNER,
)
write(
    "exercises/debug-tests-that-dont-test/solution.py",
    '''def add(a, b):
    return a + b


def test_two_positive_numbers():
    assert add(2, 3) == 5


def test_zero_changes_nothing():
    assert add(7, 0) == 7


def test_negative_numbers():
    assert add(-2, -3) == -5
''' + RUNNER,
)
write(
    "exercises/debug-tests-that-dont-test/test_exercise.py",
    GRADER + '''
from checks import run

EXPECTED = "3 passed\\n"


def test_three_pass():
    """Prints 3 passed."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\\n{EXPECTED}\\nYour program printed:\\n{printed}"


def test_the_tests_still_test_something():
    """All three tests are kept, run, and fail for an add that subtracts."""
    module = load_solution()
    names = sorted(name for name in dir(module) if name.startswith("test_"))
    assert names == ["test_negative_numbers", "test_two_positive_numbers", "test_zero_changes_nothing"], (
        f"Keep the three tests and fix them, don't delete or rename them. Found: {names}"
    )
    assert catches(module, "add", lambda a, b: a - b)
''',
)
write(
    "exercises/debug-tests-that-dont-test/wrong/only-answer-fixed.py",
    '''def add(a, b):
    return a + b


def test_two_positive_numbers():
    assert add(2, 3) == 5


def test_zero_changes_nothing():
    assert add(7, 0) == 7


def check_negative_numbers():
    assert add(-2, -3) == -5
''' + RUNNER,
)
write(
    "exercises/debug-tests-that-dont-test/wrong/deleted-the-failing-test.py",
    '''def add(a, b):
    return a + b


def test_zero_changes_nothing():
    assert add(7, 0) == 7


def test_negative_numbers():
    assert add(-2, -3) == -5


def test_nothing():
    pass
''' + RUNNER,
)
write(
    "exercises/debug-tests-that-dont-test/wrong/typed-in.py",
    '''def add(a, b):
    return a + b


print("3 passed")
''',
)

# --- review pool: a code exercise -------------------------------------------

write(
    "exercises/review-tests-for-clamp-boundaries/exercise.yaml",
    '''id: review-tests-for-clamp-boundaries
stage: review_code
rev: 1
title: "Tests at the boundaries"
prompt: |
  The starter has a correct `clamp`. Write two tests for the **boundaries**: a value exactly equal to the high end comes back unchanged, and a value exactly equal to the low end comes back unchanged. Keep the runner; the program should print `2 passed`.

  The checks run your tests against a clamp that excludes its boundaries, which should make at least one of them fail.
skills: [edge-cases, write-tests]
''',
)
CLAMP = '''def clamp(value, low, high):
    return max(low, min(value, high))
'''
write("exercises/review-tests-for-clamp-boundaries/starter.py", CLAMP + "\n\n# Your tests go here.\n" + RUNNER)
write(
    "exercises/review-tests-for-clamp-boundaries/solution.py",
    CLAMP + '''

def test_the_high_end_is_inside():
    assert clamp(10, 0, 10) == 10


def test_the_low_end_is_inside():
    assert clamp(0, 0, 10) == 0
''' + RUNNER,
)
write(
    "exercises/review-tests-for-clamp-boundaries/test_exercise.py",
    GRADER + '''
from checks import run


def test_two_tests_pass():
    """Prints 2 passed (or more), all passing against the real clamp."""
    printed = run().strip()
    assert printed.endswith("passed")
    assert int(printed.split()[-2]) >= 2
    all_pass(load_solution())


def test_catches_excluded_boundaries():
    """At least one test fails for a clamp that pushes boundary values inward."""
    module = load_solution()

    def exclusive_clamp(value, low, high):
        if value >= high:
            return high - 1
        if value <= low:
            return low + 1
        return value

    assert catches(module, "clamp", exclusive_clamp)
''',
)
write(
    "exercises/review-tests-for-clamp-boundaries/wrong/tests-the-middle.py",
    CLAMP + '''

def test_inside():
    assert clamp(5, 0, 10) == 5


def test_also_inside():
    assert clamp(7, 0, 10) == 7
''' + RUNNER,
)
write(
    "exercises/review-tests-for-clamp-boundaries/wrong/typed-in.py",
    CLAMP + '''

def test_one():
    assert True


def test_two():
    assert True
''' + RUNNER,
)

print("ml.py.writing-tests written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
