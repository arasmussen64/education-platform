from checks import run, run_with


def test_this_product():
    """Prints [17, 39]."""
    printed = run()
    assert printed == "[17, 39]\n", f"Your program printed:\n{printed}"


def test_another_product():
    """Works for other matrices and vectors: [[2, 0], [1, 3]] times [4, 5] is [8, 19]."""
    printed = run_with({"m": [[2, 0], [1, 3]], "v": [4, 5]})
    assert printed == "[8, 19]\n", (
        f"With [[2, 0], [1, 3]] and [4, 5] it should print [8, 19]. It printed:\n{printed}"
    )
