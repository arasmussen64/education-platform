from checks import run


def rows(stdin):
    """The printed lines, without any space at the end of a line."""
    return [line.rstrip() for line in run(stdin).splitlines()]


def test_three():
    """Typing 3 prints 1 2 3, then 2 4 6, then 3 6 9."""
    printed = rows("3\n")
    assert printed == ["1 2 3", "2 4 6", "3 6 9"], f"Your program printed:\n{printed}"


def test_two():
    """Typing 2 prints 1 2, then 2 4."""
    printed = rows("2\n")
    assert printed == ["1 2", "2 4"], f"Your program printed:\n{printed}"


def test_one():
    """Typing 1 prints just 1."""
    printed = rows("1\n")
    assert printed == ["1"], f"Your program printed:\n{printed}"
