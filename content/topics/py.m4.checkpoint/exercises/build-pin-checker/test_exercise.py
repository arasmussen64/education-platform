from pathlib import Path

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7). Each test checks one part of the
# program, so a failure points at the skill behind it (test_skills in
# exercise.yaml, ADR-0012).


def count_asserts():
    source = Path("solution.py").read_text(encoding="utf-8")
    return sum(1 for line in source.splitlines() if line.strip().startswith("assert "))


def test_four_digits():
    """is_four_digits: True for 1357, False for 12345, 123, 12a4 and an empty PIN."""
    is_four_digits = function("is_four_digits")
    assert is_four_digits("1357") is True
    assert is_four_digits("12345") is False
    assert is_four_digits("123") is False
    assert is_four_digits("12a4") is False
    assert is_four_digits("") is False


def test_not_all_same():
    """not_all_same: False for 1111 and 0000, True for 1112."""
    not_all_same = function("not_all_same")
    assert not_all_same("1111") is False
    assert not_all_same("0000") is False
    assert not_all_same("1112") is True


def test_not_counting_up():
    """not_counting_up: False for 1234 and 6789, True for 4321, 1357 and 1235."""
    not_counting_up = function("not_counting_up")
    assert not_counting_up("1234") is False
    assert not_counting_up("6789") is False
    assert not_counting_up("4321") is True
    assert not_counting_up("1357") is True
    assert not_counting_up("1235") is True


def test_verdict():
    """check_pin: OK for 1357 and 4321; otherwise the first problem, in order."""
    check_pin = function("check_pin")
    assert check_pin("1357") == "OK"
    assert check_pin("4321") == "OK"
    assert check_pin("12345") == "must be 4 digits"
    assert check_pin("11111") == "must be 4 digits"
    assert check_pin("1111") == "digits must not all be the same"
    assert check_pin("1234") == "digits must not count up"


def test_docstrings():
    """Every function has a docstring."""
    for name in ("is_four_digits", "not_all_same", "not_counting_up", "check_pin", "main"):
        assert (function(name).__doc__ or "").strip() != "", name


def test_tests():
    """test_check_pin has 4 or more asserts, passes, and fails when check_pin always says OK."""
    assert count_asserts() >= 4
    test = function("test_check_pin")
    test()
    import solution

    original = solution.check_pin
    solution.check_pin = lambda pin: "OK"
    caught = False
    try:
        test()
    except AssertionError:
        caught = True
    finally:
        solution.check_pin = original
    assert caught


def test_program():
    """Run directly, the tests pass and then the typed PIN gets its verdict."""
    assert run("1357\n") == "check_pin: all checks passed\nOK\n"
    assert run("1234\n") == "check_pin: all checks passed\ndigits must not count up\n"
