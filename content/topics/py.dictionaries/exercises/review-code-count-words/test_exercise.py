from checks import function

# Hidden tests: in a review, the learner sees each docstring and whether it
# passed, but not the failure messages.


def test_counts():
    """word_counts("a b a") is {"a": 2, "b": 1}."""
    assert function("word_counts")("a b a") == {"a": 2, "b": 1}


def test_edges():
    """word_counts("") is {}, and a word seen three times counts 3."""
    word_counts = function("word_counts")
    assert word_counts("") == {}
    assert word_counts("go go go stop") == {"go": 3, "stop": 1}
