from checks import run


def test_eight():
    """Typing 8 prints three steps, 2, 4 and 8, then Reached 8 in 3 steps."""
    printed = run("8\n")
    expected = "Step 1: 2\nStep 2: 4\nStep 3: 8\nReached 8 in 3 steps\n"
    assert printed == expected, f"Your program printed:\n{printed}"


def test_five():
    """Typing 5 also takes three steps, ending at 8."""
    printed = run("5\n")
    expected = "Step 1: 2\nStep 2: 4\nStep 3: 8\nReached 5 in 3 steps\n"
    assert printed == expected, f"Your program printed:\n{printed}"


def test_one():
    """Typing 1 takes no steps at all."""
    printed = run("1\n")
    assert printed == "Reached 1 in 0 steps\n", f"Your program printed:\n{printed}"
