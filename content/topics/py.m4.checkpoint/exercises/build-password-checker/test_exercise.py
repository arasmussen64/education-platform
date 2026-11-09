from pathlib import Path

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7). Each test checks one part of the
# program, so a failure points at the skill behind it (test_skills in
# exercise.yaml, ADR-0012).


def count_asserts():
    source = Path("solution.py").read_text(encoding="utf-8")
    return sum(1 for line in source.splitlines() if line.strip().startswith("assert "))


def test_min_length():
    """has_min_length: True for 8 characters, False for 7 and for an empty password."""
    has_min_length = function("has_min_length")
    assert has_min_length("abcdefgh") is True
    assert has_min_length("abcdefg") is False
    assert has_min_length("") is False


def test_has_digit():
    """has_digit: True for abc1 and for 9, False for abc."""
    has_digit = function("has_digit")
    assert has_digit("abc1") is True
    assert has_digit("9") is True
    assert has_digit("abc") is False


def test_has_upper():
    """has_upper: True for abC and ABC, False for abc and for 123."""
    has_upper = function("has_upper")
    assert has_upper("abC") is True
    assert has_upper("ABC") is True
    assert has_upper("abc") is False
    assert has_upper("123") is False


def test_verdict():
    """check_password: OK for Secret99; otherwise the first problem, in order."""
    check_password = function("check_password")
    assert check_password("Secret99") == "OK"
    assert check_password("Abcdefg1") == "OK"
    assert check_password("Abcdef1") == "too short"
    assert check_password("abc") == "too short"
    assert check_password("longenough") == "needs a digit"
    assert check_password("longenough1") == "needs a capital letter"
    assert check_password("LONGENOUGH") == "needs a digit"


def test_docstrings():
    """Every function has a docstring."""
    for name in ("has_min_length", "has_digit", "has_upper", "check_password", "main"):
        assert (function(name).__doc__ or "").strip() != "", name


def test_tests():
    """test_check_password has 4 or more asserts, passes, and fails when check_password always says OK."""
    assert count_asserts() >= 4
    test = function("test_check_password")
    test()
    import solution

    original = solution.check_password
    solution.check_password = lambda password: "OK"
    caught = False
    try:
        test()
    except AssertionError:
        caught = True
    finally:
        solution.check_password = original
    assert caught


def test_program():
    """Run directly, the tests pass and then the typed password gets its verdict."""
    assert run("Secret99\n") == "check_password: all checks passed\nOK\n"
    assert run("abc\n") == "check_password: all checks passed\ntoo short\n"
