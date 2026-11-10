from checks import function, run


def test_the_output():
    """Prints 6, 2 and -1."""
    printed = run()
    assert printed == '6\n2\n-1\n', f"Your program printed:\n{printed}"


def test_more_amounts():
    """Zero needs no coins; 3, 7 and 405 make 13 with three coins; 2 can't be made from 3s."""
    min_coins = function("min_coins")
    assert min_coins([1, 2], 0) == 0
    assert min_coins([3, 7, 405], 13) == 3
    assert min_coins([3], 2) == -1
    assert min_coins([9, 6, 5, 1], 11) == 2
