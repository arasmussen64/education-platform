import re

from checks import run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7). Each test checks one part of the
# program, so a failure points at the skill behind it (test_skills in
# exercise.yaml, ADR-0012).


def stats(text):
    """The three statistics the program printed, whatever the format:
    (4, 16, "quick"). Missing parts come back as None."""
    printed = run(text + "\n")
    words = re.search(r"Words:\s*(\d+)", printed)
    letters = re.search(r"Letters:\s*(\d+)", printed)
    longest = re.search(r"Longest word:\s*([A-Za-z]+)", printed)
    return (
        int(words.group(1)) if words else None,
        int(letters.group(1)) if letters else None,
        longest.group(1) if longest else None,
    )


def bars(text):
    """The lines of the chart: every printed line made only of #."""
    printed = run(text + "\n")
    return [line for line in printed.splitlines() if line and set(line) == {"#"}]


def test_words():
    """Counts the words: 4 in the quick brown fox, 1 in hello, 5 in a b c d e."""
    assert stats("the quick brown fox")[0] == 4
    assert stats("hello")[0] == 1
    assert stats("a b c d e")[0] == 5


def test_letters():
    """Counts the letters, not the spaces: 16 in the quick brown fox, 5 in a b c d e."""
    assert stats("the quick brown fox")[1] == 16
    assert stats("hello")[1] == 5
    assert stats("a b c d e")[1] == 5


def test_longest():
    """Finds the longest word, and the first of them when two tie: quick, not brown."""
    assert stats("the quick brown fox")[2] == "quick"
    assert stats("a journey begins")[2] == "journey"
    assert stats("hello")[2] == "hello"


def test_last_word():
    """The last word counts too, even though no space follows it: far, here."""
    assert stats("we go far")[2] == "far"
    assert stats("to be or not to be here")[2] == "here"
    assert stats("we go far")[0] == 3


def test_chart():
    """Draws one bar per word, one # per letter, in order."""
    assert bars("the quick brown fox") == ["###", "#####", "#####", "###"]
    assert bars("hello") == ["#####"]
    assert bars("a b c d e") == ["#", "#", "#", "#", "#"]


def test_layout():
    """Prints exactly the three statistics lines and then the bars, as in the example."""
    assert run("the quick brown fox\n") == (
        "Words: 4\nLetters: 16\nLongest word: quick\n###\n#####\n#####\n###\n"
    )
