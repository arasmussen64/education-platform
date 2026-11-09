from checks import run


def test_forty_and_sixty():
    """Typing 40 and 60 prints Same: False, First is bigger: False, Add up to 100: True."""
    printed = run("40\n60\n")
    expected = "Same: False\nFirst is bigger: False\nAdd up to 100: True\n"
    assert printed == expected, f"Your program printed:\n{printed}"


def test_seven_and_seven():
    """Typing 7 and 7 prints Same: True, First is bigger: False, Add up to 100: False."""
    printed = run("7\n7\n")
    expected = "Same: True\nFirst is bigger: False\nAdd up to 100: False\n"
    assert printed == expected, f"Your program printed:\n{printed}"


def test_ninety_and_five():
    """Typing 90 and 5 prints Same: False, First is bigger: True, Add up to 100: False."""
    printed = run("90\n5\n")
    expected = "Same: False\nFirst is bigger: True\nAdd up to 100: False\n"
    assert printed == expected, f"Your program printed:\n{printed}"
