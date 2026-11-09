from pathlib import Path

from checks import function, run


def count_asserts():
    source = Path("solution.py").read_text(encoding="utf-8")
    return sum(1 for line in source.splitlines() if line.strip().startswith("assert "))


def fails_when_is_even_is(broken):
    """Whether test_is_even fails once is_even is replaced by `broken`."""
    test = function("test_is_even")
    import solution

    original = solution.is_even
    solution.is_even = broken
    try:
        test()
    except AssertionError:
        return True
    finally:
        solution.is_even = original
    return False


def test_program():
    """Run directly, the file prints that all checks passed."""
    got = run()
    assert got == "is_even: all checks passed\n", f"Your program printed:\n{got}"


def test_three_asserts():
    """test_is_even has at least three asserts."""
    assert count_asserts() >= 3, f"Found {count_asserts()} assert lines; write at least 3"


def test_catches_always_true():
    """The tests fail for a broken is_even that says True for everything."""
    assert fails_when_is_even_is(lambda n: True), (
        "test_is_even passed for a function that calls every number even: test an odd number"
    )


def test_catches_reversed():
    """The tests fail for a broken is_even that has it backwards."""
    assert fails_when_is_even_is(lambda n: n % 2 == 1), (
        "test_is_even passed for a function that has even and odd swapped"
    )
