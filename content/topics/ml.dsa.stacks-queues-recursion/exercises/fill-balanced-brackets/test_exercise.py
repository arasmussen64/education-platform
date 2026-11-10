from checks import function, run


def test_the_output():
    """Prints the four verdicts."""
    printed = run()
    assert printed == "'([]{})' True\n'([)]' False\n'((' False\n'f(x[0]) + g({})' True\n", f"Your program printed:\n{printed}"


def test_more_texts():
    """An empty text is balanced; a lone closer, a lone opener and a crossed pair are not; letters are ignored."""
    balanced = function("balanced")
    assert balanced("") and balanced("a(b)c") and balanced("{[()]}")
    assert not balanced(")") and not balanced("(") and not balanced("{(})")
