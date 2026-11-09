from pathlib import Path

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def count_asserts():
    source = Path("solution.py").read_text(encoding="utf-8")
    return sum(1 for line in source.splitlines() if line.strip().startswith("assert "))


def test_rules():
    """is_leap is True for 2024 and 2000, False for 2023 and 1900."""
    is_leap = function("is_leap")
    assert is_leap(2024) is True
    assert is_leap(2023) is False
    assert is_leap(1900) is False
    assert is_leap(2000) is True


def test_docstring():
    """is_leap has a docstring."""
    assert (function("is_leap").__doc__ or "").strip() != ""


def test_program():
    """Run directly, the file prints is_leap: all checks passed."""
    assert run() == "is_leap: all checks passed\n"


def test_enough_asserts():
    """test_is_leap has at least four asserts."""
    assert count_asserts() >= 4


def test_catches_century_bug():
    """test_is_leap fails for a version of is_leap that only checks divisibility by 4."""
    test = function("test_is_leap")
    import solution

    original = solution.is_leap
    solution.is_leap = lambda year: year % 4 == 0
    caught = False
    try:
        test()
    except AssertionError:
        caught = True
    finally:
        solution.is_leap = original
    assert caught
