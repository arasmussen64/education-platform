from checks import run


def test_five_minutes():
    """Typing 5 prints Seconds: 300."""
    printed = run("5\n")
    assert printed == "Seconds: 300\n", f"Your program printed:\n{printed}"


def test_ninety_minutes():
    """Typing 90 prints Seconds: 5400."""
    printed = run("90\n")
    assert printed == "Seconds: 5400\n", f"Your program printed:\n{printed}"
