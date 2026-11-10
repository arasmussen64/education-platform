from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints the three summaries."""
    assert run() == "[2, 4, 6]\n{'sun': 3, 'moon': 4}\n['A', 'B']\n"


def test_evens_and_lengths():
    """evens keeps order and skips odd numbers; lengths maps every word."""
    evens = function("evens")
    lengths = function("lengths")
    assert evens([7, 10, 3, 8]) == [10, 8]
    assert evens([1, 3]) == []
    assert lengths(["a", "bbb"]) == {"a": 1, "bbb": 3}


def test_initials():
    """initials gives each first letter once, sorted."""
    initials = function("initials")
    assert initials(["Zed", "Amy", "Zoe", "Al"]) == ["A", "Z"]
