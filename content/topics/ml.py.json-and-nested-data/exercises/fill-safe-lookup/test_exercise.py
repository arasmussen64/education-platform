from checks import function, run


def test_these_people():
    """Prints Oslo for Ada and unknown for the other three."""
    printed = run()
    assert printed == "Ada Oslo\nBo unknown\nCy unknown\nDi unknown\n", f"Your program printed:\n{printed}"


def test_other_records():
    """Works for a city, no address, an address that's a string, and an address with no city."""
    city_of = function("city_of")
    assert city_of({"address": {"city": "Rome"}}) == "Rome"
    assert city_of({}) == "unknown"
    assert city_of({"address": "Oslo"}) == "unknown"
    assert city_of({"address": {}}) == "unknown"
