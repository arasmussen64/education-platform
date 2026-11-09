from checks import function, run


def test_program():
    """Typing Secret99 prints the tests' message and OK: every assert expects the right verdict."""
    got = run("Secret99\n")
    assert got == "check_password: all checks passed\nOK\n", f"Your program printed:\n{got}"


def test_catches_a_bug():
    """test_check_password fails when check_password always says OK."""
    test = function("test_check_password")
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
    assert caught, "the tests should fail for a checker that calls every password OK"
