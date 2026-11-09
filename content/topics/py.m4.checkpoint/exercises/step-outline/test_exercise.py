from checks import function, run


def test_program():
    """Typing Secret99 prints the tests' message and OK; typing abc gets too short."""
    got = run("Secret99\n")
    assert got == "check_password: all checks passed\nOK\n", f"Your program printed:\n{got}"
    got = run("abc\n")
    assert got == "check_password: all checks passed\ntoo short\n", (
        f"Your program printed:\n{got}"
    )


def test_verdicts():
    """check_password gives each password its first problem, in order."""
    check_password = function("check_password")
    for password, expected in [
        ("Abcdefg1", "OK"),
        ("Abcdef1", "too short"),
        ("longenough", "needs a digit"),
        ("longenough1", "needs a capital letter"),
    ]:
        got = check_password(password)
        assert got == expected, f"check_password({password!r}) returned {got!r}, not {expected!r}"


def test_docstrings():
    """Every function has a docstring."""
    for name in ("has_min_length", "has_digit", "has_upper", "check_password", "main"):
        assert (function(name).__doc__ or "").strip() != "", f"{name} needs a docstring"
