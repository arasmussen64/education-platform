from checks import function, run


def test_program():
    """Running the program prints [91, 88, 72] and then 0."""
    got = run()
    assert got == "[91, 88, 72]\n0\n", f"Your program printed:\n{got}"


def test_top_three():
    """top_three gives three scores, highest first, and leaves the list unchanged."""
    top_three = function("top_three")
    scores = [72, 45, 88, 91, 60]
    assert top_three(scores) == [91, 88, 72], f"top_three returned {top_three(scores)!r}"
    assert scores == [72, 45, 88, 91, 60], f"the list was changed to {scores!r}"
    assert top_three([5]) == [5], f"top_three([5]) returned {top_three([5])!r}"


def test_first_position():
    """first_position returns the first match (0 for a in a, b, a) and -1 for no match."""
    first_position = function("first_position")
    assert first_position(["a", "b", "a"], "a") == 0, (
        f'first_position(["a", "b", "a"], "a") returned {first_position(["a", "b", "a"], "a")!r}'
    )
    assert first_position([1, 2], 9) == -1, (
        f"first_position([1, 2], 9) returned {first_position([1, 2], 9)!r}"
    )
