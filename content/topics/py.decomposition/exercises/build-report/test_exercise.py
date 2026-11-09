from checks import function, printed, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_count_words():
    """count_words returns 4 for the quick brown fox and 1 for hello."""
    count_words = function("count_words")
    assert count_words("the quick brown fox") == 4
    assert count_words("hello") == 1


def test_longest_word():
    """longest_word returns quick for the quick brown fox, far for we go far, and big for big cat."""
    longest_word = function("longest_word")
    assert longest_word("the quick brown fox") == "quick"
    assert longest_word("we go far") == "far"
    assert longest_word("big cat") == "big"


def test_summary():
    """summary returns 4 words, longest: quick, and works for other texts."""
    summary = function("summary")
    assert summary("the quick brown fox") == "4 words, longest: quick"
    assert summary("big cat") == "2 words, longest: big"


def test_docstrings():
    """Each of the three functions has a docstring."""
    for name in ("count_words", "longest_word", "summary"):
        assert (function(name).__doc__ or "").strip() != ""


def test_quiet_workers():
    """The three functions return their results and print nothing."""
    assert printed(function("count_words"), "a b") == ""
    assert printed(function("longest_word"), "a b") == ""
    assert printed(function("summary"), "a b") == ""


def test_program():
    """Running the program prints the summary of the quick brown fox, then of hello."""
    assert run() == "4 words, longest: quick\n1 words, longest: hello\n"
