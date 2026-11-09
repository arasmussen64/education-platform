from checks import run


def plans(day, temperature):
    return run(f"{day}\n{temperature}\n")


def test_hot_saturday():
    """Sat and 25 prints Weekend: True, Beach day: True, Stay in: False."""
    printed = plans("Sat", 25)
    assert printed == "Weekend: True\nBeach day: True\nStay in: False\n", (
        f"Your program printed:\n{printed}"
    )


def test_cold_monday():
    """Mon and 3 prints Weekend: False, Beach day: False, Stay in: True."""
    printed = plans("Mon", 3)
    assert printed == "Weekend: False\nBeach day: False\nStay in: True\n", (
        f"Your program printed:\n{printed}"
    )


def test_warm_monday():
    """Mon and 25 prints False, False, False: a warm weekday is neither."""
    printed = plans("Mon", 25)
    assert printed == "Weekend: False\nBeach day: False\nStay in: False\n", (
        f"Your program printed:\n{printed}"
    )


def test_sunday_at_twenty():
    """Sun and 20 prints Weekend: True, Beach day: False: 20 is not more than 20."""
    printed = plans("Sun", 20)
    assert printed == "Weekend: True\nBeach day: False\nStay in: False\n", (
        f"Your program printed:\n{printed}"
    )
