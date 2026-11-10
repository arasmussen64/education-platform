from checks import run


def test_mean_and_median():
    """Prints mean 5.0, then median 4.0."""
    assert run() == "mean 5.0\nmedian 4.0\n"
