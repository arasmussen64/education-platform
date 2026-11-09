from checks import function, run


def test_program():
    """Prints the sentence for 5, then 5 itself, unchanged."""
    assert run() == "5 doubled is 10\n5\n"


def test_functions_alone():
    """double(7) returns 14, and describe(2) returns its sentence."""
    assert function("double")(7) == 14
    assert function("describe")(2) == "2 doubled is 4"
