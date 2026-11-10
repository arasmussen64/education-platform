from checks import function, run


def test_the_output():
    """Prints True False True."""
    printed = run()
    assert printed == 'True False True\n', f"Your program printed:\n{printed}"


def test_every_value_and_some_gaps():
    """Every inserted value is found, values between them are not, and an empty tree holds nothing."""
    insert = function("insert")
    contains = function("contains")
    root = None
    for value in (8, 3, 10, 1, 6, 14, 4, 7, 13):
        root = insert(root, value)
    assert all(contains(root, value) for value in (8, 3, 10, 1, 6, 14, 4, 7, 13))
    assert not any(contains(root, value) for value in (0, 2, 5, 9, 11, 12, 15))
    assert not contains(None, 1)
