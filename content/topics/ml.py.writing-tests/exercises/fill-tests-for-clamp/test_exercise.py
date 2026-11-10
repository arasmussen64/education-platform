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


def test_all_three_pass():
    """Prints 3 passed."""
    printed = run()
    assert printed == "3 passed\n", f"Your program printed:\n{printed}"


def test_the_tests_catch_a_broken_clamp():
    """The tests fail for a clamp that ignores the low end."""
    module = load_solution()
    assert catches(module, "clamp", lambda value, low, high: min(value, high)), (
        "A clamp that never applies the low end should fail at least one test."
    )
