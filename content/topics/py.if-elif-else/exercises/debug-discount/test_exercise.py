from checks import run


def test_big_order():
    """Typing 120 prints Discount: 20%, then Thank you!"""
    printed = run("120\n")
    assert printed == "Discount: 20%\nThank you!\n", f"Your program printed:\n{printed}"


def test_medium_order():
    """Typing 60 prints Discount: 10%, then Thank you!"""
    printed = run("60\n")
    assert printed == "Discount: 10%\nThank you!\n", f"Your program printed:\n{printed}"


def test_small_order():
    """Typing 20 prints Discount: 0%, then Thank you!"""
    printed = run("20\n")
    assert printed == "Discount: 0%\nThank you!\n", f"Your program printed:\n{printed}"


def test_boundaries():
    """Exactly 100 gets 20% and exactly 50 gets 10%."""
    for total, percent in [(100, 20), (50, 10)]:
        printed = run(f"{total}\n")
        assert printed == f"Discount: {percent}%\nThank you!\n", (
            f"Typing {total} should print Discount: {percent}%. Your program printed:\n{printed}"
        )
