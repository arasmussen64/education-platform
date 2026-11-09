from checks import run, run_with


def test_as_in_the_table():
    """Prints 4 3, as the table's last row says."""
    printed = run()
    assert printed == "4 3\n", f"Your program printed:\n{printed}"


def test_with_a_small_n():
    """With n starting at 4, the if doesn't run: it prints 4 2."""
    printed = run_with({"n": 4})
    assert printed == "4 2\n", f"With n = 4, your program printed:\n{printed}"
