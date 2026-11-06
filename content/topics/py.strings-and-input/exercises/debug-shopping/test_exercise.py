from checks import run


def test_pens():
    """Typing pens, 3 and 1.25 prints 3 pens cost $3.75."""
    printed = run("pens\n3\n1.25\n")
    assert printed == "3 pens cost $3.75\n", f"Your program printed:\n{printed}"


def test_apples():
    """Typing apples, 4 and 0.5 prints 4 apples cost $2.00."""
    printed = run("apples\n4\n0.5\n")
    assert printed == "4 apples cost $2.00\n", f"Your program printed:\n{printed}"
