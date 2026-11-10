from checks import function, run

EXPECTED = "'kitten' -> 'sitting' 3\n'' -> 'abc' 3\n'flaw' -> 'lawn' 2\n'same' -> 'same' 0\n"


def test_the_output():
    """Prints the four distances."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_more_pairs():
    """abc to nothing is 3, sunday to saturday is 3, and a one-letter substitution is 1."""
    edit_distance = function("edit_distance")
    assert edit_distance("abc", "") == 3 and edit_distance("sunday", "saturday") == 3 and edit_distance("cat", "cut") == 1
