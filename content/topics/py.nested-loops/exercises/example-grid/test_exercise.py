from checks import run


def test_grid():
    """Prints three rows of four bricks, then done."""
    assert run() == "####\n####\n####\ndone\n"
