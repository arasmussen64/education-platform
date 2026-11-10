from checks import run, run_with


def test_seventy_seven():
    """Prints 77 degrees F is 25.0 degrees C."""
    printed = run()
    assert printed == "77 degrees F is 25.0 degrees C\n", (
        f"Your program printed:\n{printed}"
    )


def test_boiling_point():
    """Works for any temperature: 212 F is 100.0 C."""
    printed = run_with({"fahrenheit": 212})
    assert printed == "212 degrees F is 100.0 degrees C\n", (
        f"With fahrenheit = 212 it should print 212 degrees F is 100.0 degrees C. It printed:\n{printed}"
    )
