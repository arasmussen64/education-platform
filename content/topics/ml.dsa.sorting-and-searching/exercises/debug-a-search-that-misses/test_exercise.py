from checks import function, run

EXPECTED = '[2, 7, 11, 19, 30, 41, 56, 64, 73, 88]\n2 at index 0\n30 at index 4\n88 at index 9\n50 at index -1\n'


def test_the_output():
    """Prints the sorted readings and the four searches."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_the_edges():
    """The last element and a single-element list are found; the first element of two is found."""
    binary_search = function("binary_search")
    assert binary_search(list(range(0, 1000, 2)), 998) == 499
    assert binary_search([5], 5) == 0 and binary_search([5, 6], 5) == 0
