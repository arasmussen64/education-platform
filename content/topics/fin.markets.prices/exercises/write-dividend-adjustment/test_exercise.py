from checks import function, run

EXPECTED = (
    "day 0: 39.02\n"
    "day 1: 39.80\n"
    "day 2: 40.00\n"
    "day 3: 40.20\n"
    "day 4: 40.60\n"
    "return from the raw closes: 1.50%\n"
    "return with the dividend: 4.04%\n"
)


def test_the_report():
    """Prints the five adjusted closes, the raw return and the return with the dividend."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_another_dividend():
    """A 0.50 dividend with the ex-date at day 2, after a 24.00 close: the factor is 1 - 0.50 / 24.00."""
    adjust_for_dividend = function("adjust_for_dividend")
    got = adjust_for_dividend([25.0, 24.0, 23.5, 23.8], 2, 0.5)
    expected = [24.4792, 23.5, 23.5, 23.8]
    assert [round(value, 4) for value in got] == expected, (
        f"adjust_for_dividend([25.0, 24.0, 23.5, 23.8], 2, 0.5) should be about {expected}. It returned {got}"
    )


def test_leaves_the_closes_alone():
    """adjust_for_dividend returns a new list and leaves the raw closes as they were."""
    adjust_for_dividend = function("adjust_for_dividend")
    raw = [25.0, 24.0, 23.5, 23.8]
    adjust_for_dividend(raw, 2, 0.5)
    assert raw == [25.0, 24.0, 23.5, 23.8], f"The list passed in was changed to {raw}"
