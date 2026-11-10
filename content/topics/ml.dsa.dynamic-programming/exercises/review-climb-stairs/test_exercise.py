from checks import function, run


def test_the_output():
    """Prints 1 2 8 1346269."""
    assert run() == '1 2 8 1346269\n'


def test_more_stairs():
    """ways(0) is 1, ways(3) is 3, and ways(80) is 37889062373143906, which only a non-exponential version reaches."""
    ways = function("ways")
    assert ways(0) == 1 and ways(3) == 3 and ways(80) == 37889062373143906
