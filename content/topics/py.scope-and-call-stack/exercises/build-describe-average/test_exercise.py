from checks import function, printed, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_average():
    """average(4, 8) returns 6.0, and average(3, 4) returns 3.5."""
    average = function("average")
    assert average(4, 8) == 6.0
    assert average(3, 4) == 3.5


def test_describe():
    """describe(4, 8) returns The average of 4 and 8 is 6.0."""
    assert function("describe")(4, 8) == "The average of 4 and 8 is 6.0"


def test_describe_any_numbers():
    """describe(1, 1) returns The average of 1 and 1 is 1.0: it uses only its parameters."""
    assert function("describe")(1, 1) == "The average of 1 and 1 is 1.0"


def test_returns_quietly():
    """Neither function prints anything."""
    assert printed(function("average"), 4, 8) == ""
    assert printed(function("describe"), 4, 8) == ""


def test_program():
    """Running the program prints the sentences for 4 and 8, then 3 and 4."""
    assert run() == "The average of 4 and 8 is 6.0\nThe average of 3 and 4 is 3.5\n"
