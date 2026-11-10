from checks import function, run


def test_the_output():
    """Prints the three flattened lists."""
    printed = run()
    assert printed == "[1, 2, 3, 4, 5, 6]\n[]\n['a']\n", f"Your program printed:\n{printed}"


def test_a_hundred_levels():
    """A nest 100 levels deep flattens to the 100 numbers in order."""
    flatten = function("flatten")
    nested = [99]
    for i in range(98, -1, -1):
        nested = [i, nested]
    assert flatten(nested) == list(range(100))
