from checks import function, run


def test_program():
    """The three printed checks come out the same every run."""
    assert run() == (
        "5 rolls, all between 1 and 6: True\n"
        "Mean of 2, 4, 9: 5\n"
        "A random pick is one of the options: True\n"
    )


def test_roll():
    """roll(6) is always between 1 and 6, and roll(1) is always 1."""
    roll = function("roll")
    for _ in range(50):
        assert 1 <= roll(6) <= 6
    assert roll(1) == 1
