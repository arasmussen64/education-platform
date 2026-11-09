from pathlib import Path

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7). Each test checks one part of the
# program, so a failure points at the skill behind it (test_skills in
# exercise.yaml, ADR-0012).


def count_asserts():
    source = Path("solution.py").read_text(encoding="utf-8")
    return sum(1 for line in source.splitlines() if line.strip().startswith("assert "))


def test_right_length():
    """is_right_length: True for 3 and 12 characters, False for 2 and 13."""
    is_right_length = function("is_right_length")
    assert is_right_length("abc") is True
    assert is_right_length("abcdefghijkl") is True
    assert is_right_length("ab") is False
    assert is_right_length("abcdefghijklm") is False


def test_starts_with_letter():
    """starts_with_letter: True for ada and Ada, False for 9lives and _ada."""
    starts_with_letter = function("starts_with_letter")
    assert starts_with_letter("ada") is True
    assert starts_with_letter("Ada") is True
    assert starts_with_letter("9lives") is False
    assert starts_with_letter("_ada") is False


def test_is_simple():
    """is_simple: True for ada_42 and ADA, False for ada-42 and ada 42."""
    is_simple = function("is_simple")
    assert is_simple("ada_42") is True
    assert is_simple("ADA") is True
    assert is_simple("ada-42") is False
    assert is_simple("ada 42") is False


def test_verdict():
    """check_username: OK for ada_42; otherwise the first problem, in order."""
    check_username = function("check_username")
    assert check_username("ada_42") == "OK"
    assert check_username("Ada") == "OK"
    assert check_username("ab") == "must be 3 to 12 characters"
    assert check_username("9-") == "must be 3 to 12 characters"
    assert check_username("9lives") == "must start with a letter"
    assert check_username("ada-42") == "only letters, digits and underscores"


def test_docstrings():
    """Every function has a docstring."""
    for name in ("is_right_length", "starts_with_letter", "is_simple", "check_username", "main"):
        assert (function(name).__doc__ or "").strip() != "", name


def test_tests():
    """test_check_username has 4 or more asserts, passes, and fails when check_username always says OK."""
    assert count_asserts() >= 4
    test = function("test_check_username")
    test()
    import solution

    original = solution.check_username
    solution.check_username = lambda name: "OK"
    caught = False
    try:
        test()
    except AssertionError:
        caught = True
    finally:
        solution.check_username = original
    assert caught


def test_program():
    """Run directly, the tests pass and then the typed name gets its verdict."""
    assert run("ada_42\n") == "check_username: all checks passed\nOK\n"
    assert run("9lives\n") == "check_username: all checks passed\nmust start with a letter\n"
