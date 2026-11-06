from checks import run


def test_apples():
    """Typing Apples and 1.5 prints Apples cost $1.50."""
    printed = run("Apples\n1.5\n")
    assert printed == "Apples cost $1.50\n", f"Your program printed:\n{printed}"


def test_other_items():
    """Works for other items and prices, always with two decimal places."""
    for typed, expected in [
        ("Tea\n2\n", "Tea cost $2.00\n"),
        ("Cake\n3.456\n", "Cake cost $3.46\n"),
    ]:
        printed = run(typed)
        assert printed == expected, (
            f"Typing {typed.split()} should print {expected.strip()}. "
            f"Your program printed:\n{printed}"
        )
