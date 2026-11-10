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
