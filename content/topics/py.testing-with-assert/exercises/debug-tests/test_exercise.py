from checks import function, run


def test_program():
    """Run directly, the file prints average: all checks passed."""
    got = run()
    assert got == "average: all checks passed\n", f"Your program printed:\n{got}"


def test_tests_pass():
    """test_average() runs without a failure against the real average."""
    function("test_average")()


def test_catches_a_bug():
    """test_average fails when average is replaced by a + b."""
    test = function("test_average")
    import solution

    original = solution.average
    solution.average = lambda a, b: a + b
    caught = False
    try:
        test()
    except AssertionError:
        caught = True
    finally:
        solution.average = original
    assert caught, "test_average should fail when average is wrong"
