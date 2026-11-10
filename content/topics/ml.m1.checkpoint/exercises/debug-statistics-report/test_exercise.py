from checks import run, run_with


def lines(printed):
    return printed.splitlines()


def test_mean():
    """The mean divides by the number of values: 18.0."""
    assert lines(run())[0] == "mean 18.0"


def test_median():
    """The median is the middle of the sorted values: 15.5."""
    assert lines(run())[1] == "median 15.5"


def test_spread():
    """The standard deviation is a square root: 12.3."""
    assert lines(run())[2] == "spread 12.3"


def test_other_values():
    """Works for other values: [10, 20, 30, 40] gives 25.0, 25.0 and 11.2."""
    assert run_with({"values": [10, 20, 30, 40]}) == "mean 25.0\nmedian 25.0\nspread 11.2\n"
