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

EXPECTED = "3 passed\n"


def test_three_pass():
    """Prints 3 passed."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_the_tests_still_test_something():
    """All three tests are kept, run, and fail for an add that subtracts."""
    module = load_solution()
    names = sorted(name for name in dir(module) if name.startswith("test_"))
    assert names == ["test_negative_numbers", "test_two_positive_numbers", "test_zero_changes_nothing"], (
        f"Keep all three tests and make all three run; don't delete any. Found: {names}"
    )
    assert catches(module, "add", lambda a, b: a - b)
