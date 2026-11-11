from checks import function, run


def test_the_output():
    """Prints the three pairs."""
    printed = run()
    assert printed == '(6, 9)\n(4, 4)\n(1, 3)\n', f"Your program printed:\n{printed}"


def test_other_curves():
    """A late recovery after a wobble resets the patience; a single epoch stops at 1; patience 1 stops at the first non-improvement."""
    early_stopping = function("early_stopping")
    assert early_stopping([1.0, 0.9, 0.95, 0.85, 0.9, 0.9, 0.9, 0.9], patience=3) == (4, 7)
    assert early_stopping([0.3], patience=5) == (1, 1)
    assert early_stopping([0.5, 0.4, 0.45, 0.3], patience=1) == (2, 3)
