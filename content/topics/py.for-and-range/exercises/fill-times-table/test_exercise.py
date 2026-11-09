from checks import run


def table(n):
    return "".join(f"{n} x {i} = {n * i}\n" for i in range(1, 11))


def test_three():
    """Typing 3 prints the 3 times table, from 3 x 1 = 3 to 3 x 10 = 30."""
    printed = run("3\n")
    assert printed == table(3), f"Your program printed:\n{printed}"


def test_seven():
    """Typing 7 prints the 7 times table: ten lines."""
    printed = run("7\n")
    assert printed == table(7), f"Your program printed:\n{printed}"
