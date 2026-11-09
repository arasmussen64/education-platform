from checks import function, run


def test_program():
    """Running the program prints the sentence for the quick brown fox."""
    got = run()
    assert got == "'the quick brown fox' has 4 words\n", f"Your program printed:\n{got}"


def test_docstring():
    """words_in has a docstring."""
    doc = function("words_in").__doc__
    assert doc is not None and doc.strip() != "", (
        "Put a sentence in triple quotes on the first line of words_in"
    )


def test_describe_uses_words_in():
    """describe("hi there") says 2 words: it uses words_in rather than a fixed number."""
    describe = function("describe")
    assert describe("hi there") == "'hi there' has 2 words", (
        f'describe("hi there") returned {describe("hi there")!r}'
    )
