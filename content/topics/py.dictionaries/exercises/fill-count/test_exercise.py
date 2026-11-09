from checks import run, run_with


def test_banana():
    """Running the program prints the counts for banana."""
    got = run()
    assert got == "{'b': 1, 'a': 3, 'n': 2}\n", f"Your program printed:\n{got}"


def test_other_word():
    """For the word aab it prints {'a': 2, 'b': 1}."""
    got = run_with({"word": "aab"})
    assert got == "{'a': 2, 'b': 1}\n", f"With the word aab, your program printed:\n{got}"
