from checks import run


def test_stops_at_exit():
    """Stops when the program calls sys.exit()."""
    assert run() == "start\n"
