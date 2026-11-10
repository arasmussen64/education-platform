from checks import function, run


def test_the_output():
    """Prints 77.0, then Temperature(25)."""
    printed = run()
    assert printed == "77.0\nTemperature(25)\n", f"Your program printed:\n{printed}"


def test_other_temperatures():
    """Temperature(100) is 212.0 F, Temperature(-40) is -40.0 F, and each prints like the call that made it."""
    Temperature = function("Temperature")
    assert Temperature(100).fahrenheit() == 212.0
    assert Temperature(-40).fahrenheit() == -40.0
    assert repr(Temperature(100)) == "Temperature(100)"
