from checks import function, run


def test_the_output():
    """Prints the two pairs."""
    assert run() == '(3, 7)\n(3, 3)\n'


def test_other_curves():
    """A flat curve stops at 1 + patience; an improving one runs to the end."""
    early_stopping = function("early_stopping")
    assert early_stopping([0.5] * 10, patience=3) == (1, 4)
    assert early_stopping([0.9, 0.8, 0.7, 0.6], patience=2) == (4, 4)
