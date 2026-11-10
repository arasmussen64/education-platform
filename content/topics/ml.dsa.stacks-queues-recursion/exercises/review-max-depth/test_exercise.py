from checks import function, run


def test_the_output():
    """Prints 0 1 3."""
    assert run() == '0 1 3\n'


def test_other_nests():
    """Four empty lists nested are depth 4; a flat list is depth 1."""
    max_depth = function("max_depth")
    assert (max_depth([[[[]]]]), max_depth([1, 2, 3])) == (4, 1)
