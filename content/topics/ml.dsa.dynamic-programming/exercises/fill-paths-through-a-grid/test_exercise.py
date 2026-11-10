from checks import function, run


def test_the_output():
    """Prints the three path counts."""
    printed = run()
    assert printed == '6 184756 601080390\n', f"Your program printed:\n{printed}"


def test_a_big_grid():
    """A 30 by 30 grid has 118264581564861424 paths, which only a memoized version can count in time."""
    paths = function("paths")
    assert paths(30, 30) == 118264581564861424
