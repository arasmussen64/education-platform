from checks import function, run


def test_the_output():
    """Prints the three merged lists."""
    printed = run()
    assert printed == '[1, 2, 3, 4, 9, 10, 11]\n[5, 6]\n[2, 2, 2]\n', f"Your program printed:\n{printed}"


def test_leftovers_on_either_side():
    """Whichever list runs out first, the rest of the other is kept, and two empty lists merge to nothing."""
    merge = function("merge")
    assert merge([1, 2, 3], [0]) == [0, 1, 2, 3]
    assert merge([5], [1, 2, 3]) == [1, 2, 3, 5]
    assert merge([], []) == []
