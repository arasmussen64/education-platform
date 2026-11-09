from checks import function, run


def test_rules():
    """Each rule function answers its question: 8 is long enough, 7 is not; digits and capitals are found."""
    has_min_length = function("has_min_length")
    has_digit = function("has_digit")
    has_upper = function("has_upper")
    assert has_min_length("abcdefgh") is True, "8 characters is long enough"
    assert has_min_length("abcdefg") is False, "7 characters is too short"
    assert has_digit("abc9") is True and has_digit("abc") is False, "has_digit"
    assert has_upper("abZ") is True and has_upper("abz") is False, "has_upper"


def test_program():
    """Typing Secret99 prints the tests' message and OK."""
    got = run("Secret99\n")
    assert got == "check_password: all checks passed\nOK\n", f"Your program printed:\n{got}"
