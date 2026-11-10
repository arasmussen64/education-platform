from checks import function, run


def test_the_output():
    """Prints the two counts."""
    assert run() == '235146 23\n'


def test_more_networks():
    """A single layer from 5 to 1 is 6 parameters; a list with one size is 0."""
    parameter_count = function("parameter_count")
    assert parameter_count([5, 1]) == 6 and parameter_count([9]) == 0
