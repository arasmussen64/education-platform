from checks import function, run

EXPECTED = '[95, 95, 88]\n[95] [95, 95, 88, 66, 50, 41, 23, 12, 7, 3]\n'


def test_the_output():
    """Prints the top three, the top one and all ten in order."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_other_streams():
    """The two largest of a longer stream come out largest first, and k above the length returns everything sorted."""
    top_k = function("top_k")
    assert top_k([4, 9, 1, 7, 9, 3, 8, 2, 6, 5, 0], 2) == [9, 9]
    assert top_k([3, 1, 2], 5) == [3, 2, 1]
