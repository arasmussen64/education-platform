from checks import function

# Hidden tests: in a review, the learner sees each docstring and whether it
# passed, but not the failure messages.


def test_numbers():
    """to_int("42") is 42, and to_int("-3") is -3."""
    to_int = function("to_int")
    assert to_int("42") == 42
    assert to_int("-3") == -3


def test_not_numbers():
    """to_int gives None for "4.2", "forty" and ""."""
    to_int = function("to_int")
    assert to_int("4.2") is None
    assert to_int("forty") is None
    assert to_int("") is None
