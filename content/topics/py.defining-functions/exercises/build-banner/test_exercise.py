from checks import function, printed, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_banner_short():
    """banner("Hi") prints ==, Hi, == on three lines."""
    assert printed(function("banner"), "Hi") == "==\nHi\n==\n"


def test_banner_long():
    """banner("Prices") prints lines of six = signs."""
    assert printed(function("banner"), "Prices") == "======\nPrices\n======\n"


def test_program():
    """Running the program prints the Menu banner, then the Prices banner."""
    assert run() == "====\nMenu\n====\n======\nPrices\n======\n"
