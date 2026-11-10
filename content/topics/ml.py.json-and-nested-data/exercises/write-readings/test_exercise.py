import json

from checks import function, run


def test_the_output():
    """Prints the two readings, then the JSON made from them."""
    printed = run()
    assert printed == (
        "[Reading(sensor='a', value=1.5), Reading(sensor='b', value=2.0)]\n"
        '[{"sensor": "a", "value": 1.5}, {"sensor": "b", "value": 2.0}]\n'
    ), f"Your program printed:\n{printed}"


def test_parse_converts_values():
    """parse_readings turns values into floats, and an empty array into an empty list."""
    parse_readings = function("parse_readings")
    readings = parse_readings('[{"sensor": "z", "value": "3.5"}]')
    assert readings[0].sensor == "z"
    assert readings[0].value == 3.5
    assert isinstance(readings[0].value, float)
    assert parse_readings("[]") == []


def test_round_trip():
    """to_json of parsed readings reads back as the same records."""
    parse_readings = function("parse_readings")
    to_json = function("to_json")
    text = '[{"sensor": "q", "value": 1.0}, {"sensor": "r", "value": 0.5}]'
    assert json.loads(to_json(parse_readings(text))) == json.loads(text)
