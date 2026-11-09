from checks import run


def test_right_name_and_pin():
    """Typing ada and 1234 prints Welcome."""
    printed = run("ada\n1234\n")
    assert printed == "Welcome\n", f"Your program printed:\n{printed}"


def test_wrong_pin():
    """Typing ada and 0000 prints Access denied."""
    printed = run("ada\n0000\n")
    assert printed == "Access denied\n", f"Your program printed:\n{printed}"


def test_wrong_name():
    """Typing bob and 1234 prints Access denied: both have to be right."""
    printed = run("bob\n1234\n")
    assert printed == "Access denied\n", f"Your program printed:\n{printed}"
