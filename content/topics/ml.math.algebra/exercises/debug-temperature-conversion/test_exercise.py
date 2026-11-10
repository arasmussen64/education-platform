from checks import run, run_with

EXPECTED = "37.0 C\n310.15 K\n"


def test_body_temperature():
    """Prints 37.0 C, then 310.15 K."""
    printed = run()
    assert printed == EXPECTED, (
        f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"
    )


def test_freezing_point():
    """Works for any temperature: 32 F is 0.0 C and 273.15 K."""
    printed = run_with({"fahrenheit": 32})
    assert printed == "0.0 C\n273.15 K\n", (
        f"With fahrenheit = 32 it should print 0.0 C, then 273.15 K. It printed:\n{printed}"
    )
