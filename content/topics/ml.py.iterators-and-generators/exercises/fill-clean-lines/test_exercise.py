from checks import function, run


def test_this_text():
    """Prints ['alpha', 'beta', 'gamma']."""
    printed = run()
    assert printed == "['alpha', 'beta', 'gamma']\n", f"Your program printed:\n{printed}"


def test_it_is_a_generator():
    """clean_lines yields one line at a time and skips blank lines."""
    clean_lines = function("clean_lines")
    lines = clean_lines("x\n\n\ny")
    assert next(lines) == "x"
    assert next(lines) == "y"
