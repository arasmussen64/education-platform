from checks import run


def test_pens():
    """Typing pens, 3 and 1.25 prints 3 pens: $3.75."""
    printed = run("pens\n3\n1.25\n")
    assert printed == "3 pens: $3.75\n", f"Your program printed:\n{printed}"


def test_cups():
    """Typing cups, 2 and 4 prints 2 cups: $8.00."""
    printed = run("cups\n2\n4\n")
    assert printed == "2 cups: $8.00\n", f"Your program printed:\n{printed}"
