from checks import run


def test_finds_the_mean():
    """Prints the error and slope at 0, then the best c, 7.0, and the error there, 8.0."""
    assert run() == "error at 0: 57.0\nslope at 0: -14.0\nbest c: 7.0\nerror there: 8.0\n"
