from checks import function, run


def test_verdicts():
    """check_password returns OK, or the first problem in order."""
    check_password = function("check_password")
    assert check_password("Secret99") == "OK", 'check_password("Secret99") should be OK'
    assert check_password("abc") == "too short", 'check_password("abc") should be too short'
    assert check_password("longenough") == "needs a digit", (
        'check_password("longenough") should be needs a digit'
    )
    assert check_password("longenough1") == "needs a capital letter", (
        'check_password("longenough1") should be needs a capital letter'
    )


def test_program():
    """Typing Secret99 prints the tests' message and OK."""
    got = run("Secret99\n")
    assert got == "check_password: all checks passed\nOK\n", f"Your program printed:\n{got}"
