from checks import run


def at(hour):
    return run(f"{hour}\n")


def test_mid_morning():
    """Typing 10 prints Open, then Lunch break: False."""
    printed = at(10)
    assert printed == "Open\nLunch break: False\n", f"Your program printed:\n{printed}"


def test_lunch():
    """Typing 12 or 13 prints Open, then Lunch break: True."""
    for hour in (12, 13):
        printed = at(hour)
        assert printed == "Open\nLunch break: True\n", (
            f"Typing {hour} should print Open and Lunch break: True. Your program printed:\n{printed}"
        )


def test_closed():
    """Typing 17, 8 or 20 prints Closed, then Lunch break: False."""
    for hour in (17, 8, 20):
        printed = at(hour)
        assert printed == "Closed\nLunch break: False\n", (
            f"Typing {hour} should print Closed and Lunch break: False. Your program printed:\n{printed}"
        )


def test_opening_time():
    """Typing 9 prints Open: the shop opens at 9."""
    printed = at(9)
    assert printed == "Open\nLunch break: False\n", f"Your program printed:\n{printed}"
