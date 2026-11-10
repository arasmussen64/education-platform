import importlib
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

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_word_count():
    """word_count lowercases, splits on any whitespace, and counts repeats."""
    word_count = function("word_count")
    assert word_count("the cat and The dog") == {"the": 2, "cat": 1, "and": 1, "dog": 1}
    assert word_count("a  a\na") == {"a": 3}
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
