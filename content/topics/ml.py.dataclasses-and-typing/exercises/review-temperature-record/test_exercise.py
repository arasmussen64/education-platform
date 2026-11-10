from checks import function, run


def test_the_output():
    """Prints Temperature(celsius=25), then 77.0."""
    assert run() == "Temperature(celsius=25)\n77.0\n"


def test_the_record():
    """Temperature is a dataclass, and 100 C is 212.0 F."""
    Temperature = function("Temperature")
    assert Temperature.__dataclass_fields__.keys() == {"celsius"}
    assert Temperature(100).fahrenheit() == 212.0
