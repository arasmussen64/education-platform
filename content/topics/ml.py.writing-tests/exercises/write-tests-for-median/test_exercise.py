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

from checks import run


def test_at_least_two_tests_pass():
    """Prints how many tests passed: at least 2, all of them passing against the real median."""
    printed = run().strip()
    assert printed.endswith("passed"), f"The program should end by printing how many tests passed. It printed:\n{printed}"
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
