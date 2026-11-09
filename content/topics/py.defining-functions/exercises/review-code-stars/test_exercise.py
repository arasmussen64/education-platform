from checks import function, printed, run

# Hidden tests: in a review, the learner sees each docstring and whether it
# passed, but not the failure messages.


def test_stars():
    """stars(4) prints four stars on one line."""
    assert printed(function("stars"), 4) == "****\n"


def test_one_star():
    """stars(1) prints a single star."""
    assert printed(function("stars"), 1) == "*\n"


def test_program():
    """Running the program prints lines of 3, 1 and 5 stars."""
    assert run() == "***\n*\n*****\n"
