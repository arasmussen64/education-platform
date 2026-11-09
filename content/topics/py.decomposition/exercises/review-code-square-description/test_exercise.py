from checks import function, printed

# Hidden tests: in a review, the learner sees each docstring and whether it
# passed, but not the failure messages.


def test_square_area():
    """square_area(3) returns 9, and square_area(5) returns 25."""
    square_area = function("square_area")
    assert square_area(3) == 9
    assert square_area(5) == 25


def test_describe_square():
    """describe_square(3) returns A square of side 3 has area 9, and works for 5 too."""
    describe_square = function("describe_square")
    assert describe_square(3) == "A square of side 3 has area 9"
    assert describe_square(5) == "A square of side 5 has area 25"


def test_docstrings_and_quiet():
    """Both functions have docstrings and print nothing."""
    for name in ("square_area", "describe_square"):
        f = function(name)
        assert (f.__doc__ or "").strip() != ""
        assert printed(f, 3) == ""
