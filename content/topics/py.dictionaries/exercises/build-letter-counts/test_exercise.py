from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_count_letters():
    """count_letters counts each character, in order of first appearance, and skips spaces."""
    count_letters = function("count_letters")
    assert count_letters("banana") == {"b": 1, "a": 3, "n": 2}
    assert count_letters("a b") == {"a": 1, "b": 1}
    assert count_letters("") == {}


def test_most_common():
    """most_common picks the key with the highest count, the first one on a tie."""
    most_common = function("most_common")
    assert most_common({"x": 2, "y": 5}) == "y"
    assert most_common({"x": 2, "y": 2}) == "x"
    assert most_common({"only": 1}) == "only"


def test_program():
    """Running the program prints the counts for banana bread and the most common letter."""
    assert run() == (
        "Counts: {'b': 2, 'a': 4, 'n': 2, 'r': 1, 'e': 1, 'd': 1}\nMost common: a\n"
    )
