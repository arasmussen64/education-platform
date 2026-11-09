from checks import run


def fee(hours, day):
    return run(f"{hours}\n{day}\n")


def test_short_stay():
    """Up to 1 hour on a Monday costs $2.00."""
    for hours in (0.5, 1):
        printed = fee(hours, "Mon")
        assert printed == "Fee: $2.00\n", (
            f"{hours} hours on Mon should cost $2.00. Your program printed:\n{printed}"
        )


def test_longer_stays():
    """Up to 3 hours costs $5.00, and longer costs the $12.00 day rate."""
    for hours, expected in [(2, "5.00"), (3, "5.00"), (5, "12.00"), (3.5, "12.00")]:
        printed = fee(hours, "Mon")
        assert printed == f"Fee: ${expected}\n", (
            f"{hours} hours on Mon should cost ${expected}. Your program printed:\n{printed}"
        )


def test_sunday_free():
    """Sun and sun are free; Mon is not."""
    assert fee(5, "Sun") == "Fee: $0.00\n", "Sun should be free"
    assert fee(5, "sun") == "Fee: $0.00\n", "sun should be free too"
    assert fee(5, "Mon") == "Fee: $12.00\n", "Mon should not be free"


def test_always_prints():
    """Prints exactly one Fee line, whatever the hours and day."""
    for hours, day in [(0.5, "Mon"), (2, "Tue"), (5, "Wed"), (5, "Sun")]:
        printed = fee(hours, day)
        assert printed.count("Fee:") == 1, (
            f"For {hours} hours on {day}, your program printed:\n{printed}"
        )
