from pathlib import Path

from checks import function, run

# Hidden tests: in a review, the learner sees each docstring and whether it
# passed, but not the failure messages.


def count_asserts():
    source = Path("solution.py").read_text(encoding="utf-8")
    return sum(1 for line in source.splitlines() if line.strip().startswith("assert "))


def test_absolute_works():
    """absolute(-5) is 5, absolute(3) is 3, absolute(0) is 0."""
    absolute = function("absolute")
    assert absolute(-5) == 5
    assert absolute(3) == 3
    assert absolute(0) == 0


def test_program():
    """Run directly, the file prints absolute: all checks passed."""
    assert run() == "absolute: all checks passed\n"


def test_catches_unsigned_bug():
    """test_absolute has three or more asserts and fails for a version that returns n unchanged."""
    assert count_asserts() >= 3
    test = function("test_absolute")
    import solution

    original = solution.absolute
    solution.absolute = lambda n: n
    caught = False
    try:
        test()
    except AssertionError:
        caught = True
    finally:
        solution.absolute = original
    assert caught
