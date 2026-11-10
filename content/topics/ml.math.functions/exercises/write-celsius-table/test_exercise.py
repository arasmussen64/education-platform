from checks import function, run

TABLE = "0 C = 32.0 F\n25 C = 77.0 F\n50 C = 122.0 F\n75 C = 167.0 F\n100 C = 212.0 F\n"


def test_the_function():
    """to_fahrenheit(100) is 212.0, and to_fahrenheit(-40) is -40.0."""
    to_fahrenheit = function("to_fahrenheit")
    assert to_fahrenheit(100) == 212.0, f"to_fahrenheit(100) returned {to_fahrenheit(100)}"
    assert to_fahrenheit(-40) == -40.0, f"to_fahrenheit(-40) returned {to_fahrenheit(-40)}"


def test_the_table():
    """Prints the five rows from 0 C to 100 C."""
    printed = run()
    assert printed == TABLE, f"Expected this:\n{TABLE}\nYour program printed:\n{printed}"
