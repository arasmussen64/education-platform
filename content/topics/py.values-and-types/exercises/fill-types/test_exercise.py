from checks import run


def test_an_int_first():
    """The first line shows an int."""
    lines = run().splitlines()
    assert lines[:1] == ["<class 'int'>"], (
        "The first value should be a whole number, with no quotes."
    )


def test_then_a_float():
    """The second line shows a float."""
    lines = run().splitlines()
    assert lines[1:2] == ["<class 'float'>"], (
        "The second value should be a number with a decimal point."
    )


def test_then_a_str():
    """The third line shows a str, and nothing comes after it."""
    lines = run().splitlines()
    assert lines[2:] == ["<class 'str'>"], (
        "The third value should be text, in quotes, and it should be the last."
    )
