from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints [19, 22], then [43, 50]."""
    assert run() == "[19, 22]\n[43, 50]\n"


def test_other_shapes():
    """multiply works for a 1x3 times a 3x1, and a 2x3 times a 3x2."""
    multiply = function("multiply")
    assert multiply([[1, 2, 3]], [[1], [2], [3]]) == [[14]]
    assert multiply([[1, 2, 3], [4, 5, 6]], [[1, 2], [3, 4], [5, 6]]) == [
        [22, 28],
        [49, 64],
    ]


def test_identity():
    """Multiplying by the identity matrix changes nothing."""
    multiply = function("multiply")
    assert multiply([[1, 2], [3, 4], [5, 6]], [[1, 0], [0, 1]]) == [[1, 2], [3, 4], [5, 6]]
