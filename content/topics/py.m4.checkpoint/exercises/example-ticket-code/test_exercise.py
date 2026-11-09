from checks import function, run


def test_program():
    """Run directly with AB1234, the tests pass and the code is OK."""
    assert run("AB1234\n") == "check_code: all checks passed\nOK\n"


def test_verdicts():
    """check_code gives the first problem in order: length, then first character, then last."""
    check_code = function("check_code")
    assert check_code("12345A") == "must start with a letter"
    assert check_code("ABCDEF") == "must end with a digit"
    assert check_code("AB12") == "wrong length"
    assert check_code("1234567") == "wrong length"
